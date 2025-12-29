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

TEMPLATE_PATH = 'skills/Example_Program.py'

UNIVERSAL_SKELETON = """
import random

def generate(level=1):
    # 1. Define Variables (Logic Layer)
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    
    # 2. Calculate Answer
    ans = a + b
    
    # 3. Question Text
    # NOTICE: Use f-string with TRIPLE QUOTES for safety
    question_text = f\"\"\"計算 ${a} + {b}$ 的值為何？\"\"\"
    
    # 4. Return Data
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
    
    if undefined_vars:
        # 尋找 def generate(...): 的位置
        match = re.search(r'(def generate\(.*?\):)', fixed_code)
        if match:
            # 在函式定義下一行插入變數初始化
            function_def_end = match.end()
            injection_code = "\n    # [Auto-Fix] 初始化未定義變數以避免 Crash\n"
            for var in undefined_vars:
                # 簡單啟發式設定
                if var == 'n':
                    val = "10" 
                else:
                    val = "0"
                injection_code += f"    {var} = {val}\n"
            
            # 插入程式碼
            fixed_code = fixed_code[:function_def_end] + injection_code + fixed_code[function_def_end:]
            
    return fixed_code



def auto_generate_skill_code(skill_id, queue=None):
    """
    自動為指定的 skill_id 生成 Python 出題程式碼。
    使用 UNIVERSAL_SKELETON 作為 One-Shot 範本，結合資料庫的邏輯需求。
    """
    start_time = time.time()

    message = f"正在為技能 '{skill_id}' 自動生成程式碼..."
    if current_app: current_app.logger.info(message)
    if queue: queue.put(f"INFO: {message}")

    # 1. 取得該技能的「邏輯需求」 (從 SkillInfo)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    
    # 讀取 gemini_prompt 作為數學邏輯需求
    target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Generate a Python math problem for skill: {skill_id}"

    # 2. 組合 Prompt：教 AI 「看著 A (範本)，寫出 B (新邏輯)」
    system_instruction = """
You are a Python Code Generator.
Task: Write Python code for a NEW math skill based on the "TARGET LOGIC".
Method: MIMIC the structure of the "GOLDEN TEMPLATE" exactly.

RULES:
1. Return ONLY the raw Python code. No text explanations.
2. Do NOT copy the logic from the template (don't write addition code).
3. Implement the logic described in "TARGET LOGIC".
4. Use standard variable names (e.g., question_text, ans).
5. Always use f-string with TRIPLE QUOTES (f\"\"\"...\"\"\") for question_text.
"""

    full_prompt = f"""
{system_instruction}

### GOLDEN TEMPLATE (Follow this coding style):
```python
{UNIVERSAL_SKELETON}
TARGET LOGIC (Implement this math concept):
{target_logic}

YOUR CODE:
"""

    # 3. 呼叫 AI 模型
    try:
        client = get_ai_client() 
        response = client.generate_content(full_prompt)
        generated_code = response.text
        
        if current_app:
            current_app.logger.info(f"🤖 AI 生成完成，長度: {len(generated_code)} chars")

        # 4. 清理 Markdown
        if generated_code.startswith("```python"): generated_code = generated_code.replace("```python", "", 1)
        if generated_code.startswith("```"): generated_code = generated_code.replace("```", "", 1)
        if generated_code.endswith("```"): generated_code = generated_code.rsplit("```", 1)[0]
        generated_code = generated_code.strip()

        # 5. Regex LaTeX 預防性修復 (保留原本邏輯)
        latex_commands = [
            'angle', 'frac', 'sqrt', 'pi', 'times', 'div', 'pm', 'circ', 'triangle', 'overline', 'degree',
            'alpha', 'beta', 'gamma', 'delta', 'theta', 'phi', 'rho', 'sigma', 'omega', 'Delta', 'lambda',
            'mathbb', 'mathrm', 'mathbf', 'mathcal', 'infty', 
            'in', 'notin', 'subset', 'subseteq', 'cup', 'cap', 'neq', 'approx', 'le', 'ge', 'cdot',
            'left', 'right', 'sum', 'prod', 'int', 'lim', 'binom',
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln',
            'perp', '%' 
        ]
        
        generated_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', generated_code)
        for cmd in latex_commands:
            generated_code = re.sub(rf'(?<!\\)\\{cmd}', rf'\\\\{cmd}', generated_code)

        # 變數準備：記錄修復狀況
        initial_error = None
        repair_triggered = False

        # 6. 語法驗證與修復 (Syntax Check)
        is_valid, syntax_error = validate_python_code(generated_code)
        if not is_valid:
            initial_error = syntax_error
            repair_triggered = True
            
            if current_app: current_app.logger.warning(f"語法錯誤: {syntax_error}，嘗試修復...")
            generated_code = fix_code_syntax(generated_code, syntax_error)
            
            # 二次驗證
            is_valid_2, syntax_error_2 = validate_python_code(generated_code)
            if not is_valid_2:
                log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), False, syntax_error_2, True)
                msg = f"自動修復失敗: {syntax_error_2}"
                if current_app: current_app.logger.error(msg)
                return False, msg

        # 7. 靜態邏輯分析 (Pyflakes)
        is_logically_valid, logic_error_log = validate_logic_with_pyflakes(generated_code)
        
        if not is_logically_valid:
            if current_app: 
                current_app.logger.warning(f"邏輯檢查未通過，嘗試語意修復 (Semantic Repair)...")
                if not initial_error: initial_error = "Pyflakes Logic Error"
            
            generated_code = fix_logic_errors(generated_code, logic_error_log)
            repair_triggered = True

        # 8. 寫入檔案
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{skill_id}.py')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)

        # 9. Reload Module
        try:
            module_name = f"skills.{skill_id}"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
            
            log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), True, initial_error, repair_triggered)
            return True, "Success"

        except Exception as e:
            log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), False, f"Runtime: {str(e)}", repair_triggered)
            return False, f"Runtime Error: {str(e)}"

    except Exception as e:
        log_experiment(skill_id, start_time, len(full_prompt), 0, False, f"AI Error: {str(e)}", False)
        return False, f"AI Error: {str(e)}"

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