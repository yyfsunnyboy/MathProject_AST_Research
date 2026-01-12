# -*- coding: utf-8 -*-
# ==============================================================================
# ID: code_generator.py
# Version: v8.8 (The "Omni-Fix" Edition)
# Last Updated: 2026-01-09
# Author: Math-Master AI Dev Team
# 
# Description: 
#   The core engine responsible for generating, validating, and repairing
#   Python math problem generation scripts.
#
#   [v8.8 Fixes]:
#   1. fmt_num Upgrade: Added support for 'signed' and 'op' arguments to fix crashes.
#   2. Language Enforcement: Strict Prompt to force Traditional Chinese output.
#   3. Level Guarantee: Strict Prompt to forbid "No Level X problems" errors.
#   4. Syntax & Indentation: Includes all previous Regex Armor and syntax fixes.
# ==============================================================================

import os
import re
import sys
import io
import time
import ast
import random
import importlib
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
from models import db, SkillInfo, TextbookExample, ExperimentLog, SkillGenCodePrompt
from config import Config

# ==============================================================================
# --- Perfect Utils (Standard Math Tools v3.1) ---
# Description: The "Standard Library" injected into every generated skill.
# ==============================================================================
PERFECT_UTILS = r'''
import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
# --- 4. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案 (No answer)"}
    
    # 1. Normalize strings (字串正規化)
    def normalize(s):
        s = str(s).strip()
        # 移除空格、LaTeX間距
        s = s.replace(" ", "").replace("\\,", "").replace("\\;", "")
        # [Fix] 支援中文全形逗號，轉為半形，避免判錯
        s = s.replace("，", ",") 
        return s
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy (精確比對)
    if user_norm == correct_norm:
        return {"correct": True, "result": "Correct!"}
        
    # 3. Float Match Strategy (數值容錯比對)
    try:
        # 嘗試將兩者都轉為浮點數，如果誤差極小則算對
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # 無法轉為數字，可能是代數式或座標，維持字串比對結果
        
    # [Fix] 錯誤訊息優化：中文、換行顯示，去除不必要的符號
    # 這裡回傳的 result 會直接顯示在前端 Result 區域
    return {"correct": False, "result": f"答案錯誤。正確答案為：\n{correct_answer}"}
'''

def inject_perfect_utils(code_str):
    """
    Injects PERFECT_UTILS at the top.
    CRITICAL: Strips AI-generated duplicates to prevent redefinition errors.
    """
    # 1. Strip known helper functions if AI wrote them despite instructions
    pattern = r'def (to_latex|fmt_num|get_positive_factors|is_prime|get_prime_factorization|gcd|lcm|get_random_fraction|draw_number_line)\(.*?(\n\s+.*)+'
    clean = re.sub(pattern, '', code_str, flags=re.MULTILINE)
    
    # 2. Strip standard imports to avoid duplication
    clean = clean.replace("import random", "").replace("import math", "").replace("from fractions import Fraction", "").replace("from functools import reduce", "")
    
    return PERFECT_UTILS + "\n" + clean


# ==============================================================================
# UNIVERSAL SYSTEM PROMPT (v9.2 Optimized - Lean & Powerful)
# 結合了「規則防護」與「範例引導」，用最少的 Token 達到最強的約束力
# ==============================================================================

UNIVERSAL_GEN_CODE_PROMPT = """
You are a Senior Python Developer for a Math Web App.
Your task is to generate a Python module based on a math skill.

### ⛔ CRITICAL PROHIBITIONS (Instant Server Crash if violated):
1. **NO `import matplotlib.pyplot as plt`**.
2. **NO `plt.subplots()`, `plt.show()`, or `plt.close()`**.
3. **NO Single Braces `{}` in f-strings for LaTeX**.

### ✅ GOLDEN CODE TEMPLATE (Follow this Pattern EXACTLY):

```python
import random
import io
import base64
from matplotlib.figure import Figure  # [Safety] Use Object-Oriented Interface

def get_base64_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate(level=1):
    # 1. Logic & Calculation
    a = random.randint(1, 10)
    ans = a + 5

    # 2. Thread-Safe Plotting (No pyplot)
    fig = Figure(figsize=(8, 2))
    ax = fig.subplots()
    ax.plot([0, a], [0, 0], 'b-')
    ax.text(a/2, -0.1, f"{{a}}") # [LaTeX] Use double braces if needed
    ax.axis('off')
    
    img_str = get_base64_image(fig)

    # 3. Output Format
    # [LaTeX] f-string MUST use double braces {{ }} for LaTeX commands
    question = f"What is the result of $\\frac{{{a}}}{{2}}$?" 

    return {
        "question_text": question,
        "answer": str(ans),
        "correct_answer": str(ans),
        "image_base64": img_str,
        "difficulty": level
    }

def check(user, correct):
    # 4. Robust Checking (String first, then Float)
    u = user.strip().replace(" ", "")
    c = correct.strip().replace(" ", "")
    if u == c: return {"correct": True, "result": "Correct!"}
    try:
        if abs(float(u) - float(c)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except:
        pass
    return {"correct": False, "result": f"Incorrect. Answer: {correct}"}
"""


def infer_model_tag(model_name):
    """
    根據模型名稱自動判斷 V9 架構師的分級 (Model Tag)。
    支援 Qwen, DeepSeek, Phi, Llama 等常見模型。
    """
    name = model_name.lower()
    
    # 1. Cloud Models
    if any(x in name for x in ['gemini', 'gpt', 'claude']): return 'cloud_pro'
    
    # 2. Local Large/Medium (>= 10B)
    # DeepSeek 默認視為強邏輯模型，歸類在 local_14b (除非顯式標註 7b/8b)
    if '70b' in name or '32b' in name or '14b' in name: return 'local_14b'
    if 'deepseek' in name and not any(x in name for x in ['1.5b', '7b', '8b']): return 'local_14b'
    if 'qwen' in name and not any(x in name for x in ['0.5b', '1.5b', '3b', '7b']): return 'local_14b'
    
    # 3. Local Small/Edge (< 10B)
    if 'phi' in name or '7b' in name or '8b' in name: return 'edge_7b'
    
    # Default Fallback
    return 'local_14b'


# ==============================================================================
# --- Dispatcher Injection (v8.7 Level-Aware) ---
# ==============================================================================
def inject_robust_dispatcher(code_str):
    if re.search(r'^def generate\s*\(', code_str, re.MULTILINE):
        return code_str 
    
    # Find all generated problem type functions
    candidates = re.findall(r'^def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str, re.MULTILINE)
    valid_funcs = [f for f in candidates if f not in ['generate', 'check', 'solve', 'to_latex', 'fmt_num']]
    
    if not valid_funcs: return code_str
    
    # Heuristic Split: First half -> Level 1, Second half -> Level 2
    mid_point = (len(valid_funcs) + 1) // 2
    level_1_funcs = valid_funcs[:mid_point]
    level_2_funcs = valid_funcs[mid_point:] if len(valid_funcs) > 1 else valid_funcs

    dispatcher_code = "\n\n# [Auto-Injected Smart Dispatcher v8.7]\n"
    dispatcher_code += "def generate(level=1):\n"
    dispatcher_code += f"    if level == 1:\n"
    dispatcher_code += f"        types = {str(level_1_funcs)}\n"
    dispatcher_code += f"        selected = random.choice(types)\n"
    dispatcher_code += f"    else:\n"
    
    if level_2_funcs:
        dispatcher_code += f"        types = {str(level_2_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"
    else:
        dispatcher_code += f"        types = {str(level_1_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"

    for func in valid_funcs:
        dispatcher_code += f"    if selected == '{func}': return {func}()\n"
    
    dispatcher_code += f"    return {valid_funcs[0]}()\n"
    return code_str + dispatcher_code


def fix_return_format(code_str):
    pattern = r'(^\s*)return\s+(f["\'].*?["\'])\s*,\s*(\[.*?\])\s*$'
    def repl(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2)}, 'answer': str({m.group(3)}[0]), 'correct_answer': str({m.group(3)}[0])}}"
    return re.sub(pattern, repl, code_str, flags=re.MULTILINE)


def clean_global_scope_execution(code_str):
    lines = code_str.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if (s.startswith("print(") or s.startswith("generate(")) and "def " not in code_str: 
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def load_gold_standard_example():
    try:
        path = os.path.join(current_app.root_path, 'skills', 'Example_Program.py')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        print(f"⚠️ Warning: Could not load Example_Program.py: {e}")
    return "def generate_type_1_problem(): return {}"


def fix_missing_answer_key(code_str):
    """
    Auto-patch the generated code to ensure 'answer' key exists in the return dict.
    It injects a decorator that copies 'correct_answer' to 'answer' at runtime.
    [V9.2 Update]: Now patches ALL functions starting with 'generate'.
    """
    patch_code = """
# [Auto-Injected Patch v9.2] Universal Return Fixer
# 1. Ensures 'answer' key exists (copies from 'correct_answer')
# 2. Ensures 'image_base64' key exists (extracts from 'visuals')
def _patch_return_dict(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            # Fix 1: Answer Key
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            
            # Fix 2: Image Key (Flatten visuals for legacy frontend)
            if 'image_base64' not in res and 'visuals' in res:
                try:
                    # Extract first image value from visuals list
                    for item in res['visuals']:
                        if item.get('type') == 'image/png':
                            res['image_base64'] = item.get('value')
                            break
                except: pass
        return res
    return wrapper

# Apply patch to ALL generator functions in scope
import sys
# Iterate over a copy of globals keys to avoid modification issues
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'generate'):
        globals()[_name] = _patch_return_dict(_func)
"""
    return code_str + patch_code

# ==============================================================================
# --- THE REGEX ARMOR (v8.7.3 - Full Math Protection) ---
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    """
    [V9.8 Upgrade] Returns (fixed_code, fix_count)
    保留 v8.8 Omni-Fix 的所有邏輯，並加入修復次數統計。
    """
    fixed_code = code_str
    total_fixes = 0
    
    # 輔助函式：執行置換並回傳次數
    def apply_fix(pattern, replacement, code):
        new_code, count = re.subn(pattern, replacement, code, flags=re.MULTILINE)
        return new_code, count

    # Step 0: Critical Escape Fixes (反斜線修復)
    fixed_code, c = apply_fix(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)
    total_fixes += c

    # 1. Invalid escapes (常見錯誤)
    fixed_code, c = apply_fix(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\q', r'\\\\q', fixed_code)
    total_fixes += c

    # 2. f-string single brace fixes (保護 LaTeX 指令不被 f-string 吃掉)
    fixed_code, c = apply_fix(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    total_fixes += c
    
    # 3. cases environment fixes (The "Smart Board" Issue)
    # 3.1 針對 f-string 內的 cases 修復
    fixed_code, c = apply_fix(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    
    # 3.2 [關鍵恢復] 手動逐行檢查 (Manual line-by-line check)
    # 這是為了修復不在 f-string 內，但被寫成 {cases} 的情況，且避免誤傷 f-string
    lines = fixed_code.split('\n')
    new_lines = []
    cases_manual_fixes = 0
    
    for line in lines:
        # 如果這一行沒有 f-string 的特徵 (f" 或 f')，才進行暴力修復
        if not re.search(r'f["\']', line): 
            new_line, c = re.subn(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
            if c > 0:
                cases_manual_fixes += c
                line = new_line
        new_lines.append(line)
    
    if cases_manual_fixes > 0:
        fixed_code = '\n'.join(new_lines)
        total_fixes += cases_manual_fixes

    # 4. General LaTeX double brace enforcement (通用數學指令保護)
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
            fixed_code, c = apply_fix(r'\\%\{', r'\\%{{', fixed_code)
            total_fixes += c
        else: 
            fixed_code, c = apply_fix(rf'\\{pat}\{{', rf'\\{pat}{{{{', fixed_code)
            total_fixes += c

    # v8.7.2: Exponent Protection (指數保護)
    fixed_code, c = apply_fix(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', fixed_code)
    total_fixes += c

    # 5. Brute force fallback (暴力救援模式 - 僅在錯誤訊息吻合時觸發)
    if any(k in error_msg for k in ["single '}'", "single '{'", "invalid escape sequence"]):
        fallback_fixes = 0
        fixed_code, c = apply_fix(r'\\frac\{', r'\\frac{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\}\{', r'}}{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\^\{(-?\w+)\}', r'^{{{\1}}}', fixed_code); fallback_fixes += c # Aggressive exponent fix
        
        # [v8.7.3 Fix] 高中數學符號修復
        fixed_code, c = apply_fix(r'\\(sum|prod|binom|sigma)\_\{', r'\\\1_{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\\(sum|prod|binom|sigma)\^\{', r'\\\1^{{', fixed_code); fallback_fixes += c

        # Protect single char subscripts
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\$)', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\s|\,|\.)', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\"|\')', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\\(sin|cos|tan|cot|sec|csc)\((.*?)\)', r'\\\1(\2)', fixed_code); fallback_fixes += c
        
        total_fixes += fallback_fixes

    # 6. Python 2 print statement fix (Legacy model compatibility)
    if "expected '('" in error_msg:
        fixed_code, c = apply_fix(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        total_fixes += c
        fixed_code, c = apply_fix(r'print\s+(.*)', r'print(\1)', fixed_code)
        total_fixes += c

    return fixed_code, total_fixes


# ==============================================================================
# --- Generator Pipeline ---
# ==============================================================================
def validate_python_code(code_str):
    try: ast.parse(code_str); return True, None
    except SyntaxError as e: return False, f"{e.msg} (Line {e.lineno})"
    except Exception as e: return False, str(e)


def validate_logic_with_pyflakes(code_str):
    log_stream = io.StringIO(); reporter = Reporter(log_stream, log_stream)
    pyflakes_check(code_str, "generated_code", reporter)
    error_log = log_stream.getvalue()
    return "undefined name" not in error_log.lower(), error_log


def fix_logic_errors(code_str, error_log):
    """
    [V9.8 Upgrade] Returns (fixed_code, fix_count)
    """
    fixed_code = code_str
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    
    imports = []
    fix_count = 0
    
    for var in undefined_vars:
        if var in ['random', 'math']: 
            imports.append(f"import {var}")
            fix_count += 1
        if var == 'Fraction': 
            imports.append("from fractions import Fraction")
            fix_count += 1
            
    if imports: 
        fixed_code = "\n".join(imports) + "\n" + fixed_code
        
    return fixed_code, fix_count


def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired, actual_model_name="Unknown", regex_fixes=0, logic_fixes=0, prompt_tokens=0, completion_tokens=0):
    """
    [V9.8 Data Upgrade] 紀錄詳細的修復次數與 Token 用量
    """
    try:
        duration = time.time() - start_time
        safe_error_msg = str(error_msg)[:500] if error_msg else "None"
        
        # 建立 Log 物件 (加入新欄位)
        log = ExperimentLog(
            skill_id=skill_id,
            ai_provider=Config.AI_PROVIDER,
            model_name=actual_model_name,
            duration_seconds=round(duration, 2),
            input_length=input_len,
            output_length=output_len,
            is_success=success,
            syntax_error_initial=safe_error_msg,
            ast_repair_triggered=repaired,
            
            # [New Data Points]
            regex_fix_count=regex_fixes,
            logic_fix_count=logic_fixes,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            
            cpu_usage=50.0, 
            ram_usage=90.0
        )
        
        db.session.add(log)
        db.session.commit()
        
        status = "✅ Success" if success else "❌ Failed"
        # 顯示更詳細的 Log
        repair_info = f" | Fixes: {regex_fixes+logic_fixes} (R:{regex_fixes}/L:{logic_fixes})" if repaired else ""
        token_info = f" | Tokens: {prompt_tokens}+{completion_tokens}" if prompt_tokens else ""
        
        print(f"📊 [DB Log] {status}: {skill_id} | Time: {duration:.2f}s{repair_info}{token_info}")
        
    except Exception as e:
        db.session.rollback() # [Critical] 失敗時必須回滾，不然下一次寫入也會死
        # 6. [關鍵] 印出失敗原因 (紅色火焰)
        print(f"\\n🔥🔥🔥 [DB Error] 資料庫寫入炸裂！🔥🔥🔥")
        print(f"錯誤原因: {e}")
        print(f"嘗試寫入的資料: Skill={skill_id}, Model={actual_model_name}, ErrMsg={safe_error_msg}\\n")


def auto_generate_skill_code(skill_id, queue=None):
    start_time = time.time()
    
    # 1. Determine Target Tag based on Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    target_tag = infer_model_tag(current_model)

    # 2. [Strict Mode] Fetch ONLY the matching Architect Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=target_tag, is_active=True).first()
    
    # 3. Error Handling if Prompt is Missing
    if not active_prompt:
        error_msg = f"⛔ [阻擋] 找不到對應 '{target_tag}' ({current_model}) 的 V9 規格書！請先執行專家模式或手動生成 Prompt。"
        if current_app: current_app.logger.error(f"{skill_id}: {error_msg}")
        return False, error_msg

    # Pre-fetch skill info (needed for fallback or logging)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()


    gold_standard_code = load_gold_standard_example()
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(5).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        example_text = "\n### REFERENCE EXAMPLES (RAG):\n"
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\n"

    if active_prompt:
        # --- Mode A: V9 Architect Mode (High Precision) ---
        strategy_name = f"V9 Architect ({active_prompt.model_tag})"
        target_logic = active_prompt.user_prompt_template
        
        # V9 Specialized Prompt: Hybrid Logic (Algebra + Geometry)
        prompt = f"""
You are a Senior Python Engineer for a K-12 Math System.
### MISSION
Execute the Architect's Implementation Plan with **ADAPTIVE LOGIC**.

### 🧠 1. DOMAIN ADAPTATION (CRITICAL)
Analyze the Architect's Spec and Reference Examples to determine the domain:

#### 👉 IF ALGEBRA (Equations, Functions, Calculus):
1.  **Structural Diversity**: You MUST implement `random.choice` to select between at least **3 different Equation Structures** (e.g., Standard Form `ax+by=c`, Slope Form `y=mx+b`, Rearranged `ax=by+c`). **DO NOT** hardcode a single template.
2.  **Visualization**: Use `ax.plot` for lines/curves. Show intersections if they exist.
3.  **Format Hint**: Append `\\n(答案格式：x=_, y=_)` (or specific vars) to `question_text`.

#### 👉 IF GEOMETRY (Shapes, Angles, Symmetry):
1.  **Visual Accuracy**: Use `matplotlib.patches` (Polygon, Circle). Ensure `ax.set_aspect('equal')` so shapes aren't distorted.
2.  **Scenario**: Vary the orientation (rotation), size, or missing parameters.
3.  **Format Hint**: Append `\\n(答案格式：長度=_)` or `\\n(答案格式：角度=_)` or `\\n(答案格式：選A/B/C)`.

### 📝 2. GENERAL RULES
{UNIVERSAL_GEN_CODE_PROMPT}

### ARCHITECT'S SPECIFICATION:
{target_logic}

### ENVIRONMENT TOOLS (Already Injected):
- to_latex(n), fmt_num(n)
- from matplotlib.figure import Figure
- io, base64

### FINAL CHECKLIST:
1. Output pure Python code. Start with `import random`.
2. Ensure you followed the Return Structure in the Core Rules.
"""
    else:
        # --- Mode B: Legacy V8 Mode (Fallback) ---
        strategy_name = "Standard Mode"
        target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Math logic for {skill_id}"
        
        # [v8.7.3 Upgrade]: Prompt Optimization - No Helpers Output
        prompt = f"""
You are a Senior Python Engineer for a Math Education System.

### MISSION:
Implement the skill `{skill_id}` by strictly following the **Architect's Spec**.

### IMPORTANT: DO NOT WRITE HELPER FUNCTIONS
The system will automatically inject standard helpers (`to_latex`, `fmt_num`, `get_random_fraction`, `is_prime`, etc.) at runtime.
**YOU MUST NOT DEFINE THEM.** Just use them directly.

### REFERENCE STRUCTURE (GOLD STANDARD v3.0):
```python
import random
import math
from fractions import Fraction

# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    val = get_random_fraction()
    # Question needs LaTeX wrapping:
    q = f"What is ${{to_latex(val)}}?"
    # Answer MUST be clean (NO $ signs):
    a = to_latex(val) 
    return {{'question_text': q, 'answer': a, 'correct_answer': a}}

def generate(level=1):
    # Dispatcher logic
    ...
ARCHITECT'S SPECIFICATION: {target_logic}

{example_text}

CODING RULES:

CODING RULES:

1. **NO HELPERS**: Do NOT define `to_latex`, `fmt_num`, `check`, etc. They are auto-injected. Use them directly.

2. **Smart Dispatcher**: Implement `def generate(level=1):` to handle difficulty levels.
   - **[重要：函式命名規範]** 不論題目類型為何，主生成函式必須統一命名為 `generate()`。
   - 禁止使用 `generate_number_line()` 或 `generate_logic()` 等自定義名稱。
   - 如果有繪圖輔助函式（如 `draw_graph`），請在 `generate()` 函式內部呼叫它。
   - 必須確保檔案中存在 `def generate():` 和 `def check(user_answer, correct_answer):`。

3. **LaTeX Formatting (CRITICAL)**: 
   - All mathematical expressions (integers, fractions, equations) in `question_text` MUST be wrapped in single dollar signs `$`.
   - Example: `f"計算 ${fmt_num(a)} + {fmt_num(b)}$ 的值"` -> "計算 $3 + 5$ 的值".
   - **NO BACKTICKS**: Never use backticks (`) to wrap numbers or lists. BAD: `[1, 2]`. GOOD: $1, 2$.

4. **Answer Format Hint (CRITICAL)**:
   - You **MUST** append a clear format hint at the very end of `question_text`.
   - Format: `\\n(答案格式：...)`.
   - Example 1 (Values): `... \\n(答案格式：請填寫整數)` or `... \\n(答案格式：最簡分數)`.
   - Example 2 (Variables): `... \\n(答案格式：x=_, y=_)` (This ensures specific ordering).
   - Example 3 (Coordinates): `... \\n(答案格式：(x,y))`.

5. **Return Keys**: Return dict with keys: `'question_text'`, `'answer'`, `'correct_answer'`.
   - `correct_answer`: Must be a clean string for checking (e.g., "-5", "3/4", "x=2, y=3"). 
   - Do NOT use LaTeX (`$`) in `correct_answer` or `answer` keys, as this makes user input matching difficult. Keep it raw text.

6. **Language**: Traditional Chinese (Taiwan) ONLY (繁體中文). Use local terminology (e.g., 座標, 聯立方程式).

7. **Level Completeness**: Implement both Level 1 (Basic) and Level 2 (Advanced/Applied).

OUTPUT: Return ONLY the Python code. Start with `import random`.

[防呆輸出要求] 在 Python 檔案的最末尾，請務必包含以下代碼，確保進入點相容性：
```python
# 確保主進入點存在 (別名掛載)
if 'generate' not in globals() and any(k.startswith('generate_') for k in globals()):
    generate = next(v for k, v in globals().items() if k.startswith('generate_'))
``` """

    # 初始化計數器
    regex_fixes = 0
    logic_fixes = 0
    prompt_tokens = 0
    completion_tokens = 0

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        code = response.text
        
        # [V9.8] 嘗試獲取 Token 用量 (視 API 而定)
        try:
            # 適用於 Google Gemini / Vertex AI
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            # 如果是其他 API，可能需要調整這裡
        except:
            pass # 取不到就算了，保持 0
        
        match = re.search(r'```(?:python)?\s*(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if match: code = match.group(1)
        elif "import random" in code: code = code[code.find("import random"):]
        
        # [V9.5 Check] Integrity Validation
        if "def generate" not in code:
            # If critical function is missing, it implies truncation.
            # We attempt a naive fix by appending a default dispatcher if at least generate_problem exists.
            if "def generate_problem" in code:
                code += "\n\n# [Auto-Recovered Dispatcher]\ndef generate(level=1):\n    return generate_problem()"
            else:
                return False, "Critical Error: Generated code is incomplete (missing 'generate' function)."
        
        code = inject_perfect_utils(code)
        code = fix_return_format(code)
        code = clean_global_scope_execution(code)
        code = inject_robust_dispatcher(code) 
        code = fix_missing_answer_key(code)
        
        # [V9.8] 驗證與修復 (使用新版函式)
        is_valid, syntax_err = validate_python_code(code)
        repaired = False
        
        if not is_valid:
            # 呼叫新版 fix_code_syntax，接收次數
            code, r_count = fix_code_syntax(code, syntax_err)
            regex_fixes += r_count # 累加
            
            is_valid, syntax_err = validate_python_code(code)
            repaired = True
            
        is_valid_log, logic_err = validate_logic_with_pyflakes(code)
        if not is_valid_log:
            # 呼叫新版 fix_logic_errors，接收次數
            code, l_count = fix_logic_errors(code, logic_err)
            logic_fixes += l_count # 累加
            repaired = True

        duration = time.time() - start_time
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'}
# Fixes: Regex={regex_fixes}, Logic={logic_fixes}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + code)
            
        # [V9.8] 呼叫 Log，傳入完整數據
        log_experiment(
            skill_id, start_time, len(prompt), len(code), True, 
            syntax_err if not is_valid else "None", repaired,
            current_model,
            regex_fixes=regex_fixes,      # New
            logic_fixes=logic_fixes,      # New
            prompt_tokens=prompt_tokens,  # New
            completion_tokens=completion_tokens # New
        )
        return True, "Success"

    except Exception as e:
        log_experiment(
            skill_id, start_time, len(prompt) if 'prompt' in locals() else 0, 0, False, 
            str(e), False,
            current_model if 'current_model' in locals() else "Unknown",
            regex_fixes=regex_fixes, logic_fixes=logic_fixes # 即使失敗也記錄已嘗試的修復
        )
        return False, str(e)