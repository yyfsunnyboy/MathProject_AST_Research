import os
import re
import sys
import importlib
import json
import ast  # 用於語法檢查
from flask import current_app
from core.ai_analyzer import get_model
from models import db, SkillInfo, TextbookExample

TEMPLATE_PATH = 'skills/Example_Program.py'

def fix_code_syntax(code_str, error_msg=""):
    """
    [保留 GitHub 版本功能 + 針對數列組合擴充] 自動修復常見的 AI 生成語法錯誤
    """
    fixed_code = code_str

    # --- [新增 0] 優先修復致命的 Escape Sequence 錯誤 ---
    # 修復 \ (空白) -> \\ (空白)，解決 SyntaxWarning: invalid escape sequence '\ '
    # 這必須在其他處理之前做，避免破壞結構
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    
    # 修復 \u 開頭但非 Unicode 的情況 (如向量 u)，解決 SyntaxError: truncated \uXXXX escape
    # 如果 \u 後面接的不是 4 個 16 進位數字，就把它變成 \\u
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # =========================================================================
    # [新增修復] 針對本次 Log 回報的特定錯誤進行修補
    # =========================================================================
    
    # 1. 修復 SyntaxWarning: invalid escape sequence '\e' (常見於 \eta, \epsilon)
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)

    # 2. 修復 SyntaxWarning: invalid escape sequence '\q' (常見於 \quad, \qrt)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # 3. 修復 f-string: single '}' is not allowed (常見於 LaTeX \right})
    #    AI 常在 f-string 中生成如 f"...\right}..."，導致 Python 誤判 } 為 f-string 結尾
    #    此正則表達式會抓取 f"..." 或 f'...' 結構中，緊接在 \right 後面的單獨 }，並將其轉義為 }}
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    # --- [補強] 針對 f-string 中的 cases 環境進行雙括號轉義 ---
    # 這是解決 "Unknown environment" 與 f-string 崩潰的關鍵
    # 將 f"...\begin{cases}..." 轉換為 f"...\begin{{cases}}..."
    fixed_code = re.sub(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    
    # 同理處理 \end{cases}
    fixed_code = re.sub(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    # 4. [新增] 修復 "Unknown environment '{cases}'" 錯誤
    #    原因：AI 有時會漏掉 \begin 或 \end，只寫 {cases}，或者在 f-string 中 \b 被轉義
    #    修復動作：
    #    (A) 補全漏掉的 \begin
    #        將 " {cases}" (前面有空白或特定符號) 替換為 " \\begin{cases}"
    #        注意：這裡使用 \\\\begin 是為了在 Python 字串中輸出 \begin
    fixed_code = re.sub(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', fixed_code)
    
    #    (B) 確保 cases 環境有正確的結尾 (簡易檢查)
    #        如果字串中有 \begin{cases} 但沒有 \end{cases}，嘗試在該字串結尾前補上
    #        (這部分比較複雜，先做最常見的替換：將未閉合的 cases 區塊修復)
    #        這裡主要處理 AI 寫成 Unknown environment '{cases}' 的狀況，通常是因為 \begin 不見了。
    
    #    (C) 修復三元一次聯立方程式中常見的換行錯誤
    #        在 cases 環境中，換行應為 \\，但在 Python f-string 中需要寫成 \\\\
    #        此規則尋找 cases 環境中的單一 \，並嘗試修正為雙反斜線 (視情況而定，保守起見先不強制全改，僅針對明顯錯誤)

    # =========================================================================
    # --- [第三道防線] 補全遺漏的 LaTeX 語法 ---
    
    # 5. 修復漏寫 \begin 的 {cases}
    #    注意：只在「非 f-string」的情況下補全，以免造成 f-string 再次報錯
    #    (簡單判斷：如果該行沒有 f" 或 f' 開頭，才執行此替換)
    lines = fixed_code.split('\n')
    new_lines = []
    for line in lines:
        if not re.search(r'f["\']', line): # 只有在不是 f-string 的行才補全 \begin
            line = re.sub(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
        new_lines.append(line)
    fixed_code = '\n'.join(new_lines)
    # 1. 修復 f-string 中的 LaTeX 單獨大括號 (f-string: single '}' is not allowed)
    # [擴充] 加入 sum (級數), prod (乘積), binom (組合), sigma (統計), lim (極限)
    latex_patterns = [
        r'sqrt', r'frac', r'text', r'angle', r'overline', r'degree', 
        r'mathbf', r'mathrm', r'mathbb', r'mathcal', 
        r'hat', r'vec', r'bar', r'dot', 
        r'times', r'div', r'pm', r'mp',
        r'sin', r'cos', r'tan', r'cot', r'sec', r'csc',
        r'log', r'ln', r'lim', 
        r'sum', r'prod', r'binom', r'sigma', # 新增針對 \s 錯誤的修復
        r'perp', r'phi', r'pi', r'theta', # [新增] 解決 \p 相關錯誤
        r'%' 
    ]
    
    for pat in latex_patterns:
        # 將 \pat{ 替換為 \pat{{
        if pat == r'%':
             fixed_code = re.sub(r'\\%\{', r'\\%{{', fixed_code)
        else:
             fixed_code = re.sub(rf'\\{pat}\{{', rf'\\{pat}{{{{', fixed_code)

    # 簡單暴力修法：針對特定錯誤直接全域替換常見 LaTeX 結構
    # [調整] 這裡的觸發條件放寬，因為有時候 ast 不一定會精準報出 single '}'
    if "single '}'" in error_msg or "single '{'" in error_msg or "invalid escape sequence" in error_msg:
        # 修復分數
        fixed_code = re.sub(r'\\frac\{', r'\\frac{{', fixed_code)
        fixed_code = re.sub(r'\}\{', r'}}{{', fixed_code)
        
        # [新增] 修復下標 (遞迴數列常用 a_{n}) 和 上標 (次方)
        # 把 _{n} 變成 _{{n}}, ^{n} 變成 ^{{n}}, 支援負號 (e.g. 10^{-2})
        fixed_code = re.sub(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code)
        fixed_code = re.sub(r'\^\{(-?\w+)\}', r'^{{\1}}', fixed_code)
        
        # 修復三角函數/加總/組合
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\_\{', r'\\\1_{{', fixed_code)
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\^\{', r'\\\1^{{', fixed_code)

        # [加強版] 修復一般結尾括號
        # 原始邏輯: 只修復接引號的: fixed_code = re.sub(r'(\d|\w)\}(?=\"|\')', r'\1}}', fixed_code)
        # 新增邏輯 1: 修復接 $ 符號的 (例如 $x^{2}$)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\$)', r'\1}}', fixed_code)
        # 新增邏輯 2: 修復接空格或逗號的 (例如 sin(x), )
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\s|\,|\.)', r'\1}}', fixed_code)
        # 保留原有邏輯 (接引號)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\"|\')', r'\1}}', fixed_code)
        
        # [新增] 針對括號結尾的特別修復 (如 \sin(x) -> \sin(x}) -> \sin(x}}) )
        fixed_code = re.sub(r'\\(sin|cos|tan|cot|sec|csc)\((.*?)\)', r'\\\1(\2)', fixed_code) 

    # 2. 修復缺漏的括號 (Python 2 style print)
    if "expected '('" in error_msg:
        fixed_code = re.sub(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        fixed_code = re.sub(r'print\s+(.*)', r'print(\1)', fixed_code)

    return fixed_code

def validate_python_code(code_str):
    """
    [保留 GitHub 版本功能] 驗證 Python 程式碼語法是否正確
    """
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, f"{e.msg} (Line {e.lineno})"

# --- 定義 Prompt 骨架 (完整 13 點規則版，使用 replace 避免括號衝突) ---
PROMPT_SKELETON = """
You are a Python expert specializing in educational software for math learning.
Your task is to write a Python script for a specific math skill.

Target Skill ID: <<SKILL_ID>>
Topic Description: <<TOPIC_DESCRIPTION>>
Input Type: <<INPUT_TYPE>> (If 'graph', use matplotlib to generate an image)

--- REFERENCE EXAMPLES (How this skill is taught) ---
<<EXAMPLES_TEXT>>

--- CODE TEMPLATE (You MUST follow this structure) ---
<<TEMPLATE_CODE>>

--- REQUIREMENTS ---
1. **Functionality**:
   - Implement `def generate(level=1):` returning a dict with `question_text`, `answer`, `correct_answer`.
   - Implement `check(user_answer, correct_answer)`: Return dict with `correct` (bool) and `result` (feedback string).
   - The code must be robust, handling random number generation to create unique problems each time.

2. **Input Types**:
   - If Input Type is 'text': The question is text-only.
   - If Input Type is 'graph': The `generate` function MUST create a matplotlib figure, save it to `static/generated_plots/<<SKILL_ID>>_<uuid>.png`, and include `<img src="...">` in `question_text`.

3. **Output Format**:
   - Return ONLY the raw Python code.
   - Do NOT wrap in markdown code blocks (```python ... ```).
   - Do NOT include explanations outside the code.

【CRITICAL PYTHON SYNTAX RULES (Strict Enforcement)】
1. **Function Signature - MANDATORY**: 
   - The main entry function MUST be defined EXACTLY as: 
     `def generate(level=1):`
   - ❌ WRONG: `def generate():` (Will cause TypeError)
   - ✅ CORRECT: `def generate(level=1):`

2. **f-string Escaping - MANDATORY DOUBLE BRACES**: 
   - When using f-strings (f"..."), you MUST use **DOUBLE CURLY BRACES** `{{ }}` for any LaTeX syntax or literal braces.
   - ❌ WRONG: f"Ans: $x^{2}$" (Python thinks '2' is a variable -> SyntaxError)
   - ✅ CORRECT: f"Ans: $x^{{2}}$" (Python renders this as: Ans: $x^2$)

3. **Raw Strings for LaTeX**:
   - For LaTeX commands, ALWAYS use raw strings (r"...") or double backslashes (\\\\).
   - ✅ CORRECT: r"\\angle A", r"\\frac{{1}}{{2}}", r"\\sum", r"\\%"
   - ❌ WRONG: "\\angle A", "\\sum", "\\%" (SyntaxWarning: invalid escape sequence)

4. **Clean Output**: 
   - Output ONLY valid Python code starting with `import ...`. 

5. **LaTeX in f-strings - DETAILED EXAMPLES**: 
   - Exponents: f"$x^{{2}}$" (NOT f"$x^{2}$")
   - Subscripts (Recursion): f"$a_{{n}}$" (NOT f"$a_{n}$")
   - Fractions: f"$\\frac{{a}}{{b}}$" (NOT f"$\\frac{a}{b}$")
   - Sets: f"$x \\in \\mathbb{{R}}$"
   - Summation: f"$\\sum_{{i=1}}^{{n}}$" (Double braces for limits)
   - **Common Pitfall**: If using variables inside LaTeX, do NOT double brace the variable itself, only the LaTeX braces.
     - Correct: f"$\\frac{{{numerator}}}{{{denominator}}}$" (Outer {} for Python variable, Inner {} for LaTeX syntax)

6. **Escape Sequences & Percent Signs**:
   - For LaTeX backslashes (e.g., \\frac, \\circ, \\triangle, \\sum) and PERCENT SIGNS (%), you MUST use **Python Raw Strings (r"...")** OR **Double Backslashes (\\\\)**.
   - ❌ WRONG: "\\sum", "\\%" (Python raises SyntaxWarning because of \\s and \\%)
   - ✅ CORRECT: r"\\sum", r"\\%"

7. **No Full-width Characters**:
   - Do NOT use full-width symbols (？, ：, ，, ＋) in variable names or logic flow. They are ONLY allowed inside display strings (question_text).

8. **Template Markers**:
   - NEVER include template markers like `${{` or `}}` inside the final Python code.

9. **CRITICAL LATEX COMMAND ESCAPING**:
   - All LaTeX commands (e.g., \\angle, \\begin, \\frac, \\overline, \\circ, \\sum) MUST be written with a double backslash (\\\\) if inside normal strings, or standard backslash if inside raw strings (r"...").

10. **F-STRING & LATEX INTERACTION (THE "NO DOUBLE $" RULE)**:
    - **CRITICAL**: DO NOT put `$` signs directly inside the curly braces `{{ }}` or immediately next to them if the variable is already within a `$...$` block.
    - **CORRECT (Grouped)**: f"${{a}}：{{b}} = {{c}}：x$"
    - **WRONG (Isolated)**:   f"${{a}}：${{b}} = ${{c}}：x$"

11. **NO NEWLINES INSIDE LATEX (The "Red \\n" Rule)**:
    - **NEVER** put a newline character `\\n` inside the LaTeX delimiters `$...$`.
    - If you need a line break, use `<br>` and place it **OUTSIDE** the math block.
    - ❌ WRONG: f"Solve: $\\n x^2 = 1$"
    - ✅ CORRECT: f"Solve:<br>$x^2 = 1$"

12. **RANDOM RANGE SAFETY (CRITICAL for Stability)**:
    - Check `start <= stop` before calling `random.randint(start, stop)`.
    - Avoid `ValueError: empty range for randrange()`.

13. **NO EXTERNAL LIBRARIES (Standard Library Only)**:
    - **DO NOT** import `sympy`, `numpy`, `pandas`, or `scipy`.
    - Use ONLY Python standard libraries: `random`, `math`, `fractions`, `re`, `collections`.

Now, generate the Python code for '<<SKILL_ID>>'.
"""

def auto_generate_skill_code(skill_id, queue=None):
    """
    自動為指定的 skill_id 生成 Python 出題程式碼。
    [完整版] 結合 13 點規則 + Replace 策略 + 數列/級數/組合專項修復。
    """
    message = f"正在為技能 '{skill_id}' 自動生成程式碼..."
    if current_app: current_app.logger.info(message)
    if queue: queue.put(f"INFO: {message}")

    # 1. 讀取範本
    template_path = os.path.join(current_app.root_path, TEMPLATE_PATH)
    template_code = ""
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_code = f.read()

    # 2. 讀取例題
    examples = TextbookExample.query.filter_by(skill_id=skill_id).all()
    examples_text = "\n".join([
        f"--- 例題 ---\n題目: {ex.problem_text}\n答案: {ex.correct_answer}\n詳解: {ex.detailed_solution}\n" 
        for ex in examples
    ])

    skill = SkillInfo.query.get(skill_id)
    topic_description = skill.description if skill else skill_id
    input_type = skill.input_type if skill else "text"

    # 3. 構建 Prompt (使用 replace 策略)
    prompt = PROMPT_SKELETON.replace("<<SKILL_ID>>", skill_id) \
                            .replace("<<TOPIC_DESCRIPTION>>", str(topic_description)) \
                            .replace("<<INPUT_TYPE>>", input_type) \
                            .replace("<<EXAMPLES_TEXT>>", examples_text) \
                            .replace("<<TEMPLATE_CODE>>", template_code)

    # 4. 呼叫 AI 模型
    try:
        model = get_model()
        response = model.generate_content(prompt)
        generated_code = response.text

        # 5. 清理 Markdown
        if generated_code.startswith("```python"): generated_code = generated_code.replace("```python", "", 1)
        if generated_code.startswith("```"): generated_code = generated_code.replace("```", "", 1)
        if generated_code.endswith("```"): generated_code = generated_code.rsplit("```", 1)[0]
        generated_code = generated_code.strip()

        # 6. Regex LaTeX 預防性修復
        # [擴充] 針對您遇到的 \s, \m 錯誤，加入 sum, sigma, mathbb 等指令
        # [重要] 新增 'u' 和 'v' 以避免向量運算 (u+v) 時出現 \u+v (unicode error)
        latex_commands = [
            'angle', 'frac', 'sqrt', 'pi', 'times', 'div', 'pm', 'circ', 'triangle', 'overline', 'degree',
            'alpha', 'beta', 'gamma', 'delta', 'theta', 'phi', 'rho', 'sigma', 'omega', 'Delta', 'lambda',
            'mathbb', 'mathrm', 'mathbf', 'mathcal', 'infty', 
            'in', 'notin', 'subset', 'subseteq', 'cup', 'cap', 'neq', 'approx', 'le', 'ge', 'cdot',
            'left', 'right', 'sum', 'prod', 'int', 'lim', 'binom',
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln',
            'perp', # 解決 \p 錯誤
            '%' # 特殊符號
        ]
        
        # [新增] 全域修復：針對 "\ " (反斜線空格) 的問題
        # 這是造成 invalid escape sequence '\ ' 的主因
        generated_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', generated_code)

        for cmd in latex_commands:
            # 確保反斜線 (raw string 修正)
            generated_code = re.sub(rf'(?<!\\)\\{cmd}', rf'\\\\{cmd}', generated_code)

        # 7. 語法驗證與修復
        is_valid, syntax_error = validate_python_code(generated_code)
        if not is_valid:
            if current_app: current_app.logger.warning(f"語法錯誤: {syntax_error}，嘗試修復...")
            generated_code = fix_code_syntax(generated_code, syntax_error)
            
            # 二次驗證
            is_valid_2, syntax_error_2 = validate_python_code(generated_code)
            if not is_valid_2:
                msg = f"自動修復失敗: {syntax_error_2}"
                if current_app: current_app.logger.error(msg)
                return False, msg

        # 8. 寫入檔案
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{skill_id}.py')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)

        # 9. 更新資料庫
        if skill:
            skill.input_type = input_type
            db.session.commit()

        # 10. Reload Module
        try:
            module_name = f"skills.{skill_id}"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
            return True, "Success"

        except Exception as e:
            return False, f"Runtime Error: {str(e)}"

    except Exception as e:
        return False, f"AI Error: {str(e)}"