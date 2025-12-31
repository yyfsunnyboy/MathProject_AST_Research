import os
import re
import sys
import importlib
import json
import ast
import time
import io
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
from models import db, SkillInfo, TextbookExample, ExperimentLog
from config import Config

# [v7.7.1] Universal Skeleton + Utils Injection + Full Syntax Repair
UNIVERSAL_SKELETON = """
import random
import math
from fractions import Fraction

def generate(level=1):
    # Dispatcher
    problem_type = random.choice(['calc', 'app'])
    if problem_type == 'calc': return generate_calc_problem()
    else: return generate_app_problem()

def generate_calc_problem():
    return {"question_text": "...", "answer": "...", "correct_answer": "..."}

def generate_app_problem():
    return {"question_text": "...", "answer": "...", "correct_answer": "..."}

def check(user_ans, correct_ans):
    return {"correct": user_ans.strip() == correct_ans.strip(), "result": f"Ans: {correct_ans}", "next_question": True}
"""

# ★★★ 完美的工具函式 (將強制注入) ★★★
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
    """
    [v7.7] 強制替換 AI 生成的工具函式，避免語法錯誤。
    """
    clean_code = code_str
    # 清除 to_latex
    clean_code = re.sub(r'def to_latex\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)
    # 清除 fmt_num
    clean_code = re.sub(r'def fmt_num\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)
    # 清除 draw_number_line
    clean_code = re.sub(r'def draw_number_line\(.*?\):(\n\s+.*)+', '', clean_code, flags=re.MULTILINE)

    # 找到 import 區塊的結尾，插入完美工具
    match = re.search(r'^(import .*|from .*)$', clean_code, re.MULTILINE)
    if match:
        last_import_pos = 0
        for m in re.finditer(r'^(import .*|from .*)$', clean_code, re.MULTILINE):
            last_import_pos = m.end()
        
        final_code = clean_code[:last_import_pos] + "\n" + PERFECT_UTILS + "\n" + clean_code[last_import_pos:]
    else:
        final_code = PERFECT_UTILS + "\n" + clean_code
        
    return final_code

def fix_code_syntax(code_str, error_msg=""):
    """
    [v7.6 完整復原版] 自動修復常見的 AI 生成語法錯誤 (含 LaTeX 衝突處理)
    """
    fixed_code = code_str

    # --- [Step 0] 優先修復致命的 Escape Sequence 錯誤 ---
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 1. 修復各種 invalid escape sequence
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # 2. 修復 f-string: single '}' is not allowed
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    
    # 3. 修復 cases 環境 (LaTeX 的一大地雷)
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

    # 4. 修復一般 LaTeX 結構的雙大括號 (防止 f-string 解析錯誤)
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
    return fixed_code

def auto_generate_skill_code(skill_id, queue=None):
    start_time = time.time()
    
    # 1. Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    
    strategy_name = "General Math Pedagogy v7.7.1 (Full Fix + Utils Inject)"
    
    if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}...")

    # 2. RAG
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Generate math: {skill_id}"
    
    # 這裡稍微放寬 RAG 數量，讓 30B 讀多一點資料
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(10).all()
    rag_count = len(examples)
    
    example_text = ""
    if examples:
        example_text = "### REFERENCE EXAMPLES:\n"
        for i, ex in enumerate(examples):
            q = getattr(ex, 'problem_text', 'N/A')
            a = getattr(ex, 'correct_answer', 'N/A')
            example_text += f"Ex {i+1}: {q} -> Ans: {a}\n"

    # 3. Prompt
    system_instruction = (
        "You are an expert Python Math Problem Generator for **Taiwan Junior High School** students.\n"
        "### CRITICAL RULES:\n"
        "1. **Traditional Chinese**: Output in 繁體中文.\n"
        "2. **Context Adaptation**: Adapt logic to `TARGET SKILL`.\n"
        "3. **No Ghost Options**: List options explicitly if asking 'Which one...'.\n"
        "4. **Tools**: usage of `to_latex`, `fmt_num` is expected.\n"
        "5. **Return Keys**: `{'question_text', 'answer', 'correct_answer'}`.\n\n"
        
        "### MANDATORY STRUCTURE:\n"
        "```python\n"
        "import random\n"
        "import math\n"
        "from fractions import Fraction\n\n"
        "# ... (Utils will be injected automatically, but you can define them if you want)\n\n"
        "def generate_calc_problem():\n"
        "   # Logic here\n"
        "   return {...}\n\n"
        "def generate(level=1):\n"
        "   return generate_calc_problem()\n"
        "```\n\n"
        f"### REQUIRED UTILS (For Reference):\n```python\n{PERFECT_UTILS}\n```\n\n"
        "### REFERENCE EXAMPLES:\n" + example_text
    )
    full_prompt = system_instruction + "\n\n### TARGET SKILL LOGIC:\n" + target_logic + "\n\n### YOUR PYTHON CODE:\n```python\nimport random\n"

    # 4. Call AI
    try:
        client = get_ai_client(role='coder') 
        response = client.generate_content(full_prompt)
        generated_code = response.text
        
        match = re.search(r'```(?:python)?\s*(.*?)```', generated_code, re.DOTALL | re.IGNORECASE)
        if match: generated_code = match.group(1)
        elif "import random" in generated_code: generated_code = generated_code[generated_code.find("import random"):]
        
        generated_code = generated_code.strip()
        lines = generated_code.split('\n')
        while lines and ("input(" in lines[-1] or "print(" in lines[-1] or "generate(" in lines[-1] or lines[-1].strip() == ""):
            lines.pop()
        generated_code = '\n'.join(lines)
        
        # [v7.7] 注入工具 (先做，保證工具是好的)
        generated_code = inject_perfect_utils(generated_code)
        
        generated_code = re.sub(r'def generate\(\s*\):', r'def generate(level=1):', generated_code)
        generated_code = re.sub(r'def check\(\s*([^,)]+)\s*\):', r'def check(\1, correct_ans):', generated_code)
        
        # [v7.6] 完整語法修復 (後做，修復 AI 生成的 latex 字串問題)
        is_valid, syntax_error = validate_python_code(generated_code)
        repair_triggered = False
        if not is_valid:
            generated_code = fix_code_syntax(generated_code, syntax_error)
            # 再驗證一次
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
        
        log_experiment(skill_id, start_time, len(full_prompt), len(generated_code), True, syntax_error if not is_valid else "None", repair_triggered)
        return True, "Success"

    except Exception as e:
        log_experiment(skill_id, start_time, len(full_prompt), 0, False, str(e), False)
        if current_app: current_app.logger.error(f"Gen Error: {e}")
        return False, str(e)

def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired):
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
            syntax_error_initial=error_msg,
            ast_repair_triggered=repaired,
            cpu_usage=50.0, ram_usage=90.0
        )
        db.session.add(log)
        db.session.commit()
    except Exception: pass