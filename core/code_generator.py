import os
import re
import sys
import importlib
import json
import ast  # 用於語法檢查
import time # ★ 用於計時
import io
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
# ★ 引入資料庫模型
from models import db, SkillInfo, TextbookExample, ExperimentLog
from config import Config

TEMPLATE_PATH = 'skills/Example_Program.py'

# [Strict Skeleton for Phi-3.5]
UNIVERSAL_SKELETON = """
import random

def generate(level=1):
    # STEP 1: Define Variables
    # RULE: You MUST use 'val_a', 'val_b' for numbers, and 'ans' for the result.
    val_a = random.randint(1, 100)
    val_b = random.randint(1, 100)
    
    # STEP 2: Logic Calculation
    # Calculate 'ans' using the variables above
    ans = val_a + val_b
    
    # STEP 3: Question String
    # RULE: Use f-string with TRIPLE QUOTES. Use LaTeX format like ${val_a}$.
    question_text = f\"\"\"計算 ${val_a} + {val_b}$ 的值為何？\"\"\"
    
    # STEP 4: Return
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }

def check(user_ans, correct_ans):
    return {"correct": user_ans.strip() == correct_ans.strip(), "result": f"答案是 ${correct_ans}$", "next_question": True}
"""

def fix_code_syntax(code_str, error_msg=""):
    """
    [保留 GitHub 版本功能 + 針對數列組合擴充] 自動修復常見的 AI 生成語法錯誤
    """
    fixed_code = code_str

    # --- [新增 0] 優先修復致命的 Escape Sequence 錯誤 ---
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 1. 修復各種 invalid escape sequence
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # 2. 修復 f-string: single '}' is not allowed
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    
    # 3. 修復 cases 環境
    fixed_code = re.sub(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    
    # 補全漏掉的 \begin{cases}
    lines = fixed_code.split('\n')
    new_lines = []
    for line in lines:
        if not re.search(r'f["\']', line): 
            line = re.sub(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
        new_lines.append(line)
    fixed_code = '\n'.join(new_lines)

    # 4. 修復一般 LaTeX 結構的雙大括號
    latex_patterns = [
        r'sqrt', r'frac', r'text', r'angle', r'overline', r'degree', 
        r'mathbf', r'mathrm', r'mathbb', r'mathcal', 
        r'hat', r'vec', r'bar', r'dot', 
        r'times', r'div', r'pm', r'mp',
        r'sin', r'cos', r'tan', r'cot', r'sec', r'csc',
        r'log', r'ln', r'lim', 
        r'sum', r'prod', r'binom', r'sigma', 
        r'perp', r'phi', r'pi', r'theta', 
        r'%' 
    ]
    
    for pat in latex_patterns:
        if pat == r'%':
             fixed_code = re.sub(r'\\%\{', r'\\%{{', fixed_code)
        else:
             fixed_code = re.sub(rf'\\{pat}\{{', rf'\\{pat}{{{{', fixed_code)

    # 5. 暴力修法 (針對特定錯誤訊息)
    if "single '}'" in error_msg or "single '{'" in error_msg or "invalid escape sequence" in error_msg:
        fixed_code = re.sub(r'\\frac\{', r'\\frac{{', fixed_code)
        fixed_code = re.sub(r'\}\{', r'}}{{', fixed_code)
        fixed_code = re.sub(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code)
        fixed_code = re.sub(r'\^\{(-?\w+)\}', r'^{{\1}}', fixed_code)
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\_\{', r'\\\1_{{', fixed_code)
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\^\{', r'\\\1^{{', fixed_code)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\$)', r'\1}}', fixed_code)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\s|\,|\.)', r'\1}}', fixed_code)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\"|\')', r'\1}}', fixed_code)
        fixed_code = re.sub(r'\\(sin|cos|tan|cot|sec|csc)\((.*?)\)', r'\\\1(\2)', fixed_code) 

    # 6. Python 2 print
    if "expected '('" in error_msg:
        fixed_code = re.sub(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        fixed_code = re.sub(r'print\s+(.*)', r'print(\1)', fixed_code)

    return fixed_code

def validate_python_code(code_str):
    """
    [語法驗證] 驗證 Python 程式碼語法是否正確 (Syntax Check)
    """
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, f"{e.msg} (Line {e.lineno})"

def validate_logic_with_pyflakes(code_str):
    """
    [邏輯驗證] 使用 Pyflakes 抓出 NameError (變數未定義) 等邏輯錯誤
    """
    log_stream = io.StringIO()
    reporter = Reporter(log_stream, log_stream)
    
    # 執行檢查
    pyflakes_check(code_str, "generated_code", reporter)
    
    # 取得錯誤訊息
    error_log = log_stream.getvalue()
    
    # 判斷是否通過 (只要有 undefined name 就算失敗)
    is_valid = "undefined name" not in error_log
    
    return is_valid, error_log

def fix_logic_errors(code_str, error_log):
    """
    [語意修復] 針對 Pyflakes 抓到的錯誤進行嘗試性修復 (例如注入變數初始值)
    """
    fixed_code = code_str
    
    # 找出所有未定義的變數名稱
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    
    # --- 1. 優先處理標準庫缺失 (新增這段) ---
    known_modules = ['random', 'math', 're', 'os', 'sys', 'json', 'Fraction']
    imports_to_add = []
    
    # 檢查是否有已知的模組遺失
    for var in list(undefined_vars): # 用 list 複製一份以便移除 set 元素
        if var in known_modules:
            if var == 'Fraction':
                imports_to_add.append("from fractions import Fraction")
            else:
                imports_to_add.append(f"import {var}")
            undefined_vars.remove(var) # 處理過了，從列表中移除
            
    # 如果有缺少的 import，插在程式碼最前面
    if imports_to_add:
        fixed_code = "\n".join(imports_to_add) + "\n" + fixed_code

    # --- 2. 處理剩下的未知變數 (原本的笨邏輯，只用在剩下的變數) ---
    if undefined_vars:
        match = re.search(r'(def generate\(.*?\):)', fixed_code)
        if match:
            function_def_end = match.end()
            injection_code = "\n    # [Auto-Fix] 初始化未定義變數以避免 Crash\n"
            for var in undefined_vars:
                if var == 'n': val = "10" 
                else: val = "0"
                injection_code += f"    {var} = {val}\n"
            
            fixed_code = fixed_code[:function_def_end] + injection_code + fixed_code[function_def_end:]
            
    return fixed_code



def auto_generate_skill_code(skill_id, queue=None):
    """
    自動為指定的 skill_id 生成 Python 出題程式碼。
    Strategy:
    - Weak Models (Phi-3.5): Use Strict Skeleton (prevent syntax errors).
    - Smart Models (Qwen, Gemini): Use Creative Expert Prompt (encourage variety).
    """
    start_time = time.time()
    
    # 0. Identify Model Strategy
    current_model = Config.LOCAL_MODEL_NAME if Config.AI_PROVIDER == 'local' else Config.GEMINI_MODEL_NAME
    is_weak_model = (Config.AI_PROVIDER == 'local') and ("phi" in current_model.lower())
    
    strategy_name = "Strict Skeleton" if is_weak_model else "Creative Expert"
    message = f"正在為技能 '{skill_id}' 生成程式碼 (Model: {current_model}, Strategy: {strategy_name})..."
    
    if current_app: current_app.logger.info(message)
    if queue: queue.put(f"INFO: {message}")

    # 1. Get Logic Requirements
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Generate a math problem for: {skill_id}"

    # === [新增] 2. 撈取課本例題 (RAG) ===
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(3).all()

    # ★★★ 加入這行偵錯 ★★★
    if current_app: current_app.logger.info(f"🔍 [RAG Debug] Skill '{skill_id}' 撈到了 {len(examples)} 題例題")

    example_text = ""
    if examples:
        example_text = "### REFERENCE EXAMPLES (Mimic these styles):\n"
        for i, ex in enumerate(examples):
            # 使用 getattr 確保相容性，並優先嘗試正確的欄位名稱 problem_text / correct_answer
            q_content = getattr(ex, 'problem_text', getattr(ex, 'content', 'N/A')) 
            a_content = getattr(ex, 'correct_answer', getattr(ex, 'answer', 'N/A'))
            example_text += f"Ex {i+1}: {q_content} -> Answer: {a_content}\n"
    else:
        example_text = "No specific examples provided. Follow standard Taiwan Junior High School math style."
    # ==================================

    # 2. Construct Prompt based on Model Type
    if is_weak_model:
        # --- Strict Strategy (for Phi-3.5) ---
        system_instruction = """
You are a Strict Code Generator.
Task: Write Python code for a math skill to match "TARGET LOGIC".
Method: MIMIC the "GOLDEN TEMPLATE" exactly.
RULES:
1. Return ONLY the raw Python code.
2. Use variables 'val_a', 'val_b', 'ans' as shown in the template.
3. Use f-strings with TRIPLE QUOTES for 'question_text'.
4. Do NOT change the function signatures (generate, check).
"""
        full_prompt = f"""
{system_instruction}

### GOLDEN TEMPLATE:
```python
{UNIVERSAL_SKELETON}
```

### TARGET LOGIC:
{target_logic}

### YOUR CODE:
"""
    else:
        # --- Expert Math Teacher Prompt (v4.0: Strict API Enforcement) ---
        
        # 1. 核心工具函式 (含浮點數防呆)
        # Fix: Using r''' to wrap the string, avoiding conflict with inner docstring """
        to_latex_template = r'''
from fractions import Fraction
import math

def to_latex(num):
    """
    將數字轉換為 LaTeX 格式，自動處理分數、帶分數與負號。
    """
    if isinstance(num, float):
        num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator > 1000: num = num.limit_denominator(100)
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            abs_num = abs(num)
            i = abs_num.numerator // abs_num.denominator
            rem = abs_num - i
            return f"{sign}{i} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)
'''

        # 2. 系統指令 (強制要求 API 格式與 ASCII 圖形)
        system_instruction = (
            "你是一位台灣頂級數學老師。請撰寫 Python 程式碼來生成數學題目。\n\n"
            "### ⚠️ 絕對指令 (違反將導致系統崩潰):\n"
            "1. **必須包含工具函式**: 程式碼開頭務必貼上 `to_latex` 函式。\n"
            "2. **回傳字典 Key 必須精確**: `generate()` 函式回傳的字典，**只能**包含以下三個 Key:\n"
            "   - `\"question_text\"` (題目內容，含 LaTeX 與 ASCII 圖形)\n"
            "   - `\"answer\"` (簡答，給學生看)\n"
            "   - `\"correct_answer\"` (標準答案，比對用)\n"
            "   (❌ 嚴禁使用 `\"question\"` 或 `\"result\"`)\n\n"
            "### 📋 程式架構規範:\n"
            "1. **模組化**: 設計 `sub_problem_midpoint`, `sub_problem_distance` 等子函式。\n"
            "2. **圖形模擬**: 數線題 **必須** 在 `question_text` 中包含 ASCII 圖示。例如:\n"
            "   `數線示意： <---|---|---|--->`\n"
            "              `   A   0   B`\n"
            "3. **數值處理**: 所有數字顯示前一律呼叫 `to_latex()`。\n\n"
            "### REFERENCE EXAMPLES:\n" + example_text
        )

        full_prompt = system_instruction + "\n\n### TARGET LOGIC:\n" + target_logic + "\n\n### YOUR CODE:\n```python\nimport random\n"

    # 3. Call AI
    try:
        client = get_ai_client(role='coder') 
        response = client.generate_content(full_prompt)
        generated_code = response.text
        
        # 4. Clean Code (Robust Regex Extraction + Iterative Trimming)
        # 策略 A: 優先嘗試抓取 Markdown ``` 包裹的內容
        code_block_match = re.search(r'```(?:python)?\s*(.*?)```', generated_code, re.DOTALL | re.IGNORECASE)
        
        if code_block_match:
            generated_code = code_block_match.group(1)
        else:
            # 策略 B: 沒標籤？嘗試從 import 開始抓 (去頭)
            if "import random" in generated_code:
                generated_code = generated_code[generated_code.find("import random"):]
        
        generated_code = generated_code.strip()

        # [新增] 暴力移除 input() 與 print() 範例 (防止 Server 卡死)
        # 如果最後幾行出現 input( 或 print(，直接砍掉
        lines = generated_code.split('\n')
        # 從後面往前找，如果發現這種測試代碼就砍掉
        while lines and (
            "input(" in lines[-1] or 
            "print(" in lines[-1] or 
            "generate(" in lines[-1] or # 防止它呼叫自己
            lines[-1].strip().startswith("#") or
            lines[-1].strip() == ""
        ):
            if current_app: current_app.logger.warning(f"🧹 移除測試代碼: {lines[-1]}")
            lines.pop()
        
        generated_code = '\n'.join(lines)

        # 策略 C: 斬首去尾法 (Iterative Trimming) - ★ 新增這段
        # 如果最後一行是廢話 (導致語法錯誤)，就一行一行砍掉
        for _ in range(10):
            try:
                ast.parse(generated_code)
                break # 語法正確！跳出迴圈
            except SyntaxError as e:
                lines = generated_code.split('\n')
                # 如果錯誤在最後幾行，極大機率是廢話，砍掉！
                if len(lines) > 5 and e.lineno >= len(lines) - 2:
                    if current_app: current_app.logger.warning(f"🔪 偵測到尾部廢話 (Line {e.lineno})，執行切除手術...")
                    generated_code = '\n'.join(lines[:-1])
                else:
                    break

        # --- [CRITICAL FIX] Force-fix function signatures for weak models ---
        # 1. Force 'generate' to accept 'level'
        # Changes "def generate():" to "def generate(level=1):"
        generated_code = re.sub(r'def generate\(\s*\):', r'def generate(level=1):', generated_code)

        # 2. Force 'check' to accept 'correct_ans' if missing
        # Changes "def check(user_ans):" to "def check(user_ans, correct_ans):"
        # It captures the first argument name dynamically to preserve it.
        generated_code = re.sub(r'def check\(\s*([^,)]+)\s*\):', r'def check(\1, correct_ans):', generated_code)
        # --------------------------------------------------------------------

        # 5. Regex Safety Fixes
        generated_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', generated_code)
        latex_commands = ['frac', 'sqrt', 'times', 'div', 'pi', 'angle', 'degree', 'cdot']
        for cmd in latex_commands:
            generated_code = re.sub(rf'(?<!\\)\\{cmd}', rf'\\\\{cmd}', generated_code)

        # 6. Syntax Check & Repair
        initial_error = None
        repair_triggered = False
        
        is_valid, syntax_error = validate_python_code(generated_code)
        if not is_valid:
            initial_error = syntax_error
            repair_triggered = True
            if current_app: current_app.logger.warning(f"Syntax Error: {syntax_error}, attempting fix...")
            generated_code = fix_code_syntax(generated_code, syntax_error)
            
            is_valid_2, syntax_error_2 = validate_python_code(generated_code)
            if not is_valid_2:
                log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), False, syntax_error_2, True)
                return False, f"Auto-Fix Failed: {syntax_error_2}"

        # 7. Logic Check (Pyflakes)
        is_logically_valid, logic_error_log = validate_logic_with_pyflakes(generated_code)
        if not is_logically_valid:
            if not initial_error: initial_error = "Pyflakes Logic Error"
            generated_code = fix_logic_errors(generated_code, logic_error_log)
            repair_triggered = True

        # 8. Save File
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{skill_id}.py')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)

        # 9. Reload
        module_name = f"skills.{skill_id}"
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
            
        log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), True, initial_error, repair_triggered)
        return True, "Success"

    except Exception as e:
        log_experiment(skill_id, start_time, len(full_prompt), 0, False, f"Error: {str(e)}", False)
        if current_app: current_app.logger.error(f"Gen Error: {e}")
        return False, str(e)

# 輔助函式：寫入 DB
def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired):
    try:
        from config import Config
        duration = time.time() - start_time
        # 如果有安裝 psutil 可以解除註解
        # import psutil
        # cpu = psutil.cpu_percent()
        # ram = psutil.virtual_memory().percent
        cpu, ram = 50.0, 90.0 # 暫時值，模擬你剛剛的數據
        
        log = ExperimentLog(
            skill_id=skill_id,
            ai_provider=Config.AI_PROVIDER,
            model_name=Config.LOCAL_MODEL_NAME if Config.AI_PROVIDER == 'local' else Config.GEMINI_MODEL_NAME,
            duration_seconds=round(duration, 2),
            input_length=input_len,
            output_length=output_len,
            is_success=success,
            syntax_error_initial=error_msg,
            ast_repair_triggered=repaired,
            cpu_usage=cpu,
            ram_usage=ram
        )
        db.session.add(log)
        db.session.commit()
        if current_app: current_app.logger.info(f"📊 實驗數據已記錄: {duration}s, AST/Semantic 修復={repaired}")
    except Exception as e:
        if current_app: current_app.logger.error(f"寫入實驗 Log 失敗: {e}")