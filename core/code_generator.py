# -*- coding: utf-8 -*-
# ==============================================================================
# ID: code_generator.py
# Version: v8.0 (Golden Stable - Rollback & Stabilize)
# Description: 
#   回到 v7.9.3 的穩定基礎，僅保留最安全的修復機制。
#   1. Utils Injection: 強制注入工具函式。
#   2. Return Fixer: 修復回傳格式。
#   3. Global Cleaner: 移除外層測試碼 (解決 unpack error)。
#   4. Auto-Dispatcher: 自動修復入口函式。
# ==============================================================================

import os
import re
import sys
import importlib
import json
import ast
import time
import io
import random
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
from models import db, SkillInfo, TextbookExample, ExperimentLog
from config import Config

# ==============================================================================
# 1. 完美的工具函式 (PERFECT_UTILS)
# ==============================================================================
PERFECT_UTILS = r'''
def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")
'''

def inject_perfect_utils(code_str):
    clean_code = code_str
    clean_code = re.sub(r'def to_latex\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)
    clean_code = re.sub(r'def fmt_num\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)
    clean_code = re.sub(r'def draw_number_line\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)

    match = re.search(r'^(import .*|from .*)$', clean_code, re.MULTILINE)
    if match:
        last_import_pos = 0
        for m in re.finditer(r'^(import .*|from .*)$', clean_code, re.MULTILINE):
            last_import_pos = m.end()
        final_code = clean_code[:last_import_pos] + "\n" + PERFECT_UTILS + "\n" + clean_code[last_import_pos:]
    else:
        final_code = PERFECT_UTILS + "\n" + clean_code
    return final_code

def inject_robust_dispatcher(code_str):
    candidates = re.findall(r'def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str)
    valid_funcs = []
    for func in candidates:
        if func not in ['generate', 'generate_design_prompt', 'auto_generate_skill_code', 'check', '_generate_scientific_coeff_str']:
            valid_funcs.append(func)
    
    valid_funcs = sorted(list(set(valid_funcs)))
    if not valid_funcs:
        if "def generate_problem(" in code_str: valid_funcs = ["generate_problem"]
        else: return code_str

    dispatcher_code = "\n\n# [Auto-Injected Robust Dispatcher by v8.0]\n"
    dispatcher_code += "def generate(level=1):\n"
    dispatcher_code += f"    available_types = {str(valid_funcs)}\n"
    dispatcher_code += "    selected_type = random.choice(available_types)\n"
    dispatcher_code += "    try:\n"
    for i, func in enumerate(valid_funcs):
        if i == 0: dispatcher_code += f"        if selected_type == '{func}': return {func}()\n"
        else: dispatcher_code += f"        elif selected_type == '{func}': return {func}()\n"
    dispatcher_code += f"        else: return {valid_funcs[0]}()\n"
    dispatcher_code += "    except TypeError:\n"
    dispatcher_code += f"        return {valid_funcs[0]}()\n"

    final_code = code_str + dispatcher_code
    return final_code

def fix_return_format(code_str):
    fixed_code = code_str
    
    # ==============================================================================
    # [Priority 1] DeepSeek Multi-Return Truncator (必須最先執行！)
    # 專門對付：return f"...", [ans1], f"...", [ans2]
    # 策略：抓取第一個 "f-string" 和緊接著的 "List"，並丟棄後面所有東西
    # ==============================================================================
    # 解說：
    # 1. (^\s*)return\s+ : 抓 return 開頭
    # 2. (f["\'].*?["\']) : 抓第一個 f-string (問題)
    # 3. \s*,\s* : 中間的逗號
    # 4. (\[.*?\]) : 抓第一個 List (答案)
    # 5. \s*,.*$ : 抓後面跟著的逗號和任何東西 (這就是我們要切掉的部分)
    pattern_truncator = r'(^\s*)return\s+(f["\'].*?["\'])\s*,\s*(\[.*?\])\s*,\s*.*$'
    
    def repl_truncator(m):
        # 強制只保留第一組，並轉為 Dict
        # 注意：我們加上 str() 包裹 list[0]
        return f"{m.group(1)}return {{'question_text': {m.group(2)}, 'answer': str({m.group(3)}[0]), 'correct_answer': str({m.group(3)}[0])}}"
    
    fixed_code = re.sub(pattern_truncator, repl_truncator, fixed_code, flags=re.MULTILINE)

    # ==============================================================================
    # [Priority 2] DeepSeek Standard List Return
    # 專門對付：return f"...", [ans]  (沒有後續，只有一組)
    # ==============================================================================
    pattern_list = r'(^\s*)return\s+(f["\'].*?["\'])\s*,\s*(\[.*?\])\s*$'
    
    def repl_list(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2)}, 'answer': str({m.group(3)}[0]), 'correct_answer': str({m.group(3)}[0])}}"
    
    fixed_code = re.sub(pattern_list, repl_list, fixed_code, flags=re.MULTILINE)

    # ==============================================================================
    # [Priority 3] Standard Tuple (Legacy Qwen Support)
    # 對付：return q, a (最普通的 Tuple)
    # ==============================================================================
    # 注意：這裡排除掉以 [ 開頭的答案，避免誤傷上面的規則
    pattern_2 = r'(^\s*)return\s+(?:\(?)\s*([^,\{\}\n#\)]+?)\s*,\s*([^,\{\}\n#\)\[]+?)\s*(?:\)?)\s*$'
    
    def repl_2(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2).strip()}, 'answer': {m.group(3).strip()}, 'correct_answer': {m.group(3).strip()}}}"
    
    fixed_code = re.sub(pattern_2, repl_2, fixed_code, flags=re.MULTILINE)

    # [Priority 4] Tuple with 3 elements (q, a, ca)
    pattern_3 = r'(^\s*)return\s+(?:\(?)\s*([^,\{\}\n#\)]+?)\s*,\s*([^,\{\}\n#\)]+?)\s*,\s*([^,\{\}\n#\)]+?)\s*(?:\)?)\s*$'
    def repl_3(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2).strip()}, 'answer': {m.group(3).strip()}, 'correct_answer': {m.group(4).strip()}}}"
    fixed_code = re.sub(pattern_3, repl_3, fixed_code, flags=re.MULTILINE)
    
    return fixed_code

def clean_global_scope_execution(code_str):
    """
    [v8.0] 移除全域範圍的執行碼 (解決 unpack error)
    只移除 print 或 明顯的賦值測試，避免誤刪 import
    """
    lines = code_str.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # 移除 Qwen 雞婆寫的測試碼
        if stripped.startswith("question, answer =") or \
           stripped.startswith("q, a =") or \
           (stripped.startswith("print(") and "def " not in code_str) or \
           (stripped.startswith("generate(") and "def " not in stripped):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def sanitize_code(code_str):
    """
    [v8.0] 針對已知的 LLM 幻覺進行無條件的字串清理
    """
    fixed_code = code_str
    
    # 1. 修正 'from math import abs' 錯誤 (abs 是 built-in，無需 import)
    # 將其替換為 'import math' 以防萬一它還需要 math 裡的其他東西
    fixed_code = re.sub(r'^\s*from\s+math\s+import\s+abs\s*$', 'import math', fixed_code, flags=re.MULTILINE)
    
    # 2. 如果是混在其他 import 裡 (e.g., from math import sqrt, abs) -> 移除 abs
    fixed_code = re.sub(r'(from\s+math\s+import\s+.*),\s*abs', r'\1', fixed_code)
    fixed_code = re.sub(r'(from\s+math\s+import\s+.*)abs,\s*', r'\1', fixed_code)
    
    return fixed_code

def fix_code_syntax(code_str, error_msg=""):
    """
    [Syntax Repair v8.0] 回歸穩定的 Regex，移除危險的實驗性規則
    """
    fixed_code = code_str

    # --- Escape Sequence ---
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # --- F-String Braces (Safe Mode) ---
    # 只修復 \right}，不亂動其他的 }
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    
    # Scientific Notation / Superscripts (針對 {數字} 修復)
    fixed_code = re.sub(r'\\(\^|_)\{', r'\\\1{{', fixed_code)
    fixed_code = re.sub(r'\\(\^|_)\{(\d+)\}', r'\\\1{{\2}}', fixed_code)

    # Cases Environment
    fixed_code = re.sub(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    
    lines = fixed_code.split('\n')
    new_lines = []
    for line in lines:
        if not re.search(r'f["\']', line): 
            line = re.sub(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
        new_lines.append(line)
    fixed_code = '\n'.join(new_lines)

    # 一般 LaTeX 雙括號
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

    # 暴力修復 (僅針對錯誤訊息)
    if "single '}'" in error_msg or "single '{'" in error_msg:
        # [NEW] 新增這兩行：針對 LaTeX 的集合符號 \{ \} 在 f-string 中被誤判
        fixed_code = fixed_code.replace(r"\}", r"\}}") 
        fixed_code = fixed_code.replace(r"\{", r"\{{")
        fixed_code = re.sub(r'\\frac\{', r'\\frac{{', fixed_code)        
        fixed_code = re.sub(r'\}\{', r'}}{{', fixed_code)                
        fixed_code = re.sub(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code)
        fixed_code = re.sub(r'\^\{(-?\w+)\}', r'^{{\1}}', fixed_code)

    # Python 2 print 修復
    if "expected '('" in error_msg:
        fixed_code = re.sub(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        fixed_code = re.sub(r'print\s+(.*)', r'print(\1)', fixed_code)

    return fixed_code

def validate_python_code(code_str):
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, f"{e.msg} (Line {e.lineno})"

def validate_logic_with_pyflakes(code_str):
    log_stream = io.StringIO()
    reporter = Reporter(log_stream, log_stream)
    pyflakes_check(code_str, "generated_code", reporter)
    error_log = log_stream.getvalue()
    is_valid = "undefined name" not in error_log
    return is_valid, error_log

def fix_logic_errors(code_str, error_log):
    fixed_code = code_str
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    known_modules = ['random', 'math', 're', 'os', 'sys', 'json', 'Fraction']
    imports_to_add = []
    for var in list(undefined_vars):
        if var in known_modules:
            if var == 'Fraction': imports_to_add.append("from fractions import Fraction")
            else: imports_to_add.append(f"import {var}")
            undefined_vars.remove(var)
    if imports_to_add:
        fixed_code = "\n".join(imports_to_add) + "\n" + fixed_code
    
    if "ValueError" in error_log or "empty range" in error_log:
         wrapper = "\ndef safe_randint(a, b):\n    return random.randint(min(a, b), max(a, b))\n"
         fixed_code = wrapper + fixed_code.replace("random.randint", "safe_randint")

    return fixed_code

# ==============================================================================
# Main Generation Logic (v8.0)
# ==============================================================================
def auto_generate_skill_code(skill_id, queue=None):
    start_time = time.time()
    
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    has_architect_plan = (skill and skill.gemini_prompt and len(skill.gemini_prompt) > 50)
    
    if has_architect_plan:
        strategy_name = "Architect-Engineer Pipeline (v8.0)"
        target_logic = skill.gemini_prompt 
        task_instruction = (
            "1. **IMPLEMENT the Logic Plan**: The `TARGET SKILL LOGIC` section contains a detailed design plan.\n"
            "2. **Dynamic Implementation**: Implement **ALL** types defined in the plan.\n"
            "3. **Focus on Function Logic**: Ensure each `generate_type_X` function returns a valid dictionary.\n"
        )
    else:
        strategy_name = "Standard Mode"
        target_logic = f"Generate math: {skill_id}"
        task_instruction = (
            "1. **Define 3 distinct problem types** based on the `REFERENCE EXAMPLES`.\n"
        )

    if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model} | Mode: {strategy_name}")

    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(10).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        example_text = "### REFERENCE EXAMPLES:\n"
        for i, ex in enumerate(examples):
            q = getattr(ex, 'problem_text', 'N/A')
            a = getattr(ex, 'correct_answer', 'N/A')
            example_text += f"Ex {i+1}: {q} -> Ans: {a}\n"

    system_instruction = (
        "You are an expert Python Math Problem Generator.\n"
        "### CRITICAL RULES:\n"
        "1. **Traditional Chinese**: Output in 繁體中文.\n"
        "2. **Tools**: usage of `to_latex`, `fmt_num` is expected.\n"
        "3. **Return Keys**: `{'question_text', 'answer', 'correct_answer'}`.\n"
        "4. **Double Braces**: In f-strings, use `{{ }}` for LaTeX.\n\n"
        
        "### MANDATORY STRUCTURE:\n"
        f"{task_instruction}"
        "```python\n"
        "import random\n"
        "import math\n"
        "from fractions import Fraction\n\n"
        "# ... (Utils injected automatically)\n\n"
        "def generate_type_1_problem(): ...\n"
        "# ... Implement all types from the Architect Plan\n"
        "```\n\n"
        f"### REQUIRED UTILS (For Reference):\n```python\n{PERFECT_UTILS}\n```\n\n"
        f"{example_text}"
    )
    
    full_prompt = system_instruction + "\n\n### TARGET SKILL LOGIC (ARCHITECT PLAN):\n" + target_logic + "\n\n### YOUR PYTHON CODE:\n```python\nimport random\n"

    try:
        client = get_ai_client(role='coder') 
        response = client.generate_content(full_prompt)
        generated_code = response.text

        # [Token Tracking] Extract or Estimate Token Usage
        prompt_tokens = 0
        completion_tokens = 0
        try:
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            else:
                # Fallback estimate for Local LLM (approx 4 chars per token)
                prompt_tokens = len(full_prompt) // 4
                completion_tokens = len(generated_code) // 4
        except Exception:
            pass # Keep defaults (0) if extraction fails
        
        match = re.search(r'```(?:python)?\s*(.*?)```', generated_code, re.DOTALL | re.IGNORECASE)
        if match: generated_code = match.group(1)
        elif "import random" in generated_code: generated_code = generated_code[generated_code.find("import random"):]
        
        generated_code = generated_code.strip()
        lines = generated_code.split('\n')
        while lines and ("input(" in lines[-1] or "print(" in lines[-1] or "generate(" in lines[-1] or lines[-1].strip() == ""):
            lines.pop()
        generated_code = '\n'.join(lines)
        
        # [Pipeline 1] 注入工具
        generated_code = inject_perfect_utils(generated_code)

        # [Pipeline 2] 修復回傳格式
        generated_code = fix_return_format(generated_code)

        # [Pipeline 3] 清理雞婆的測試碼 (重要!)
        generated_code = clean_global_scope_execution(generated_code)
       
        # [NEW] [Pipeline 3.5] 強制消毒 (修復 abs import 等幻覺)
        generated_code = sanitize_code(generated_code)

        # [Pipeline 4] 自動分派
        generated_code = inject_robust_dispatcher(generated_code)
        
        generated_code = re.sub(r'def check\(\s*([^,)]+)\s*\):', r'def check(\1, correct_ans):', generated_code)
        
        # [Pipeline 5] 語法與邏輯修復
        is_valid, syntax_error = validate_python_code(generated_code)
        repair_triggered = False
        if not is_valid:
            generated_code = fix_code_syntax(generated_code, syntax_error)
            is_valid, syntax_error = validate_python_code(generated_code)
            repair_triggered = True
            
        is_valid, logic_error = validate_logic_with_pyflakes(generated_code)
        if not is_valid:
            generated_code = fix_logic_errors(generated_code, logic_error)
            repair_triggered = True

        duration = time.time() - start_time
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Fix Status: {'[Repaired]' if repair_triggered else '[Clean Pass]'}
# ==============================================================================\n\n'''
        
        output_path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header + generated_code)

        module_name = f"skills.{skill_id}"
        if module_name in sys.modules: importlib.reload(sys.modules[module_name])
        else: importlib.import_module(module_name)
        
        log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), True, syntax_error if not is_valid else "None", repair_triggered, prompt_tokens, completion_tokens)
        return True, "Success"

    except Exception as e:
        log_experiment(skill_id, start_time, len(full_prompt), 0, False, str(e), False)
        if current_app: current_app.logger.error(f"Gen Error: {e}")
        return False, str(e)

def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired, prompt_tokens=0, completion_tokens=0):
    try:
        duration = time.time() - start_time
        log = ExperimentLog(
            skill_id=skill_id,
            ai_provider=Config.AI_PROVIDER,
            model_name=Config.LOCAL_MODEL_NAME if Config.AI_PROVIDER == 'local' else Config.GEMINI_MODEL_NAME,
            duration_seconds=round(duration, 2),
            input_length=input_len,
            output_length=output_len,
            is_success=success,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            syntax_error_initial=error_msg,
            ast_repair_triggered=repaired,
            cpu_usage=50.0, ram_usage=90.0
        )
        db.session.add(log)
        db.session.commit()
    except Exception: pass