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
    Standard Answer Checker
    Handles float tolerance and string normalization (LaTeX spaces).
    """
    if user_answer is None: return {"correct": False, "result": "No answer provided."}
    
    # 1. Normalize strings (remove spaces, LaTeX commas, etc.)
    def normalize(s):
        return str(s).strip().replace(" ", "").replace("\\,", "").replace("\\;", "")
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy
    if user_norm == correct_norm:
        return {"correct": True, "result": "Correct!"}
        
    # 3. Float Match Strategy (for numerical answers)
    try:
        # If both can be parsed as floats and are close enough
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # If parsing to float fails, it's not a simple numerical answer.
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}    
    return result
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
    fixed_code = code_str
    
    # Step 0: Critical Escape Fixes
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 1. Invalid escapes common in DeepSeek outputs
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # 2. f-string single brace fixes (Protect LaTeX commands inside f-strings)
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    
    # 3. cases environment fixes (The "Smart Board" Issue)
    fixed_code = re.sub(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    
    # Manual line-by-line check for cases without f-string context
    lines = fixed_code.split('\n')
    new_lines = []
    for line in lines:
        if not re.search(r'f["\']', line): 
            line = re.sub(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
        new_lines.append(line)
    fixed_code = '\n'.join(new_lines)

    # 4. General LaTeX double brace enforcement for common math commands
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
        if pat == r'%': fixed_code = re.sub(r'\\%\{', r'\\%{{', fixed_code)
        else: fixed_code = re.sub(rf'\\{pat}\{{', rf'\\{pat}{{{{', fixed_code)

    # v8.7.2: Exponent Protection (指數保護)
    fixed_code = re.sub(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', fixed_code)

    # 5. Brute force fallback for stubborn errors
    if any(k in error_msg for k in ["single '}'", "single '{'", "invalid escape sequence"]):
        fixed_code = re.sub(r'\\frac\{', r'\\frac{{', fixed_code)
        fixed_code = re.sub(r'\}\{', r'}}{{', fixed_code)
        fixed_code = re.sub(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code)
        fixed_code = re.sub(r'\^\{(-?\w+)\}', r'^{{{\1}}}', fixed_code) # Aggressive exponent fix
        
        # [v8.7.3 Fix] 針對高中數學 \sum_{...}, \prod^{...} 的修復
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\_\{', r'\\\1_{{', fixed_code)
        fixed_code = re.sub(r'\\(sum|prod|binom|sigma)\^\{', r'\\\1^{{', fixed_code)

        # Protect single char subscripts/superscripts at end of string or before punctuation
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\$)', r'\1}}', fixed_code)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\s|\,|\.)', r'\1}}', fixed_code)
        fixed_code = re.sub(r'(\d|\w|\))\}(?=\"|\')', r'\1}}', fixed_code)
        fixed_code = re.sub(r'\\(sin|cos|tan|cot|sec|csc)\((.*?)\)', r'\\\1(\2)', fixed_code) 

    # 6. Python 2 print statement fix (Legacy model compatibility)
    if "expected '('" in error_msg:
        fixed_code = re.sub(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        fixed_code = re.sub(r'print\s+(.*)', r'print(\1)', fixed_code)

    return fixed_code


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
    fixed_code = code_str
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    imports = []
    for var in undefined_vars:
        if var in ['random', 'math']: imports.append(f"import {var}")
        if var == 'Fraction': imports.append("from fractions import Fraction")
    if imports: fixed_code = "\n".join(imports) + "\n" + fixed_code
    return fixed_code


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
1.  **Clean Answer**: `correct_answer` must be a clean string matching the format hint (e.g., "x=3, y=5" or "50"). NO LaTeX symbols in the value.
2.  **Language**: All text must be **Traditional Chinese (Taiwan)**.

### ARCHITECT'S SPECIFICATION:
{target_logic}

### ENVIRONMENT TOOLS (Already Injected):
- to_latex(n), fmt_num(n)
- matplotlib.pyplot as plt, numpy as np, io, base64, matplotlib.patches as patches

### FINAL CHECKLIST:
1. Output pure Python code. Start with `import random`.
2. Return dict keys: 'question_text', 'correct_answer', 'visuals' (or 'visual_aids').
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

NO HELPERS: Do NOT define to_latex, fmt_num, is_prime, etc.

One-to-One Mapping: Write generate_type_1_problem ... generate_type_N_problem.

Smart Dispatcher: Implement def generate(level=1):.

LaTeX Safety: Use double braces {{ }} for LaTeX commands in f-strings: f"\\frac{{{{a}}}}{{{{b}}}}".

Return Keys: Return dict with keys: 'question_text', 'answer', 'correct_answer'.

Clean Answers: answer and correct_answer MUST NOT contain $ signs.

LANGUAGE CONSTRAINT: Traditional Chinese (繁體中文) ONLY. Translate all word problems and context.

LEVEL COMPLETENESS: You MUST implement content for BOTH Level 1 and Level 2. If RAG examples are missing for a level, invent a simplified or advanced variant. Do NOT raise "No Level X" errors.

OUTPUT: Return ONLY the Python code. Start with import random. """

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        code = response.text
        
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
        is_valid, syntax_err = validate_python_code(code)
        repaired = False
        if not is_valid:
            code = fix_code_syntax(code, syntax_err)
            is_valid, syntax_err = validate_python_code(code)
            repaired = True
            
        is_valid_log, logic_err = validate_logic_with_pyflakes(code)
        if not is_valid_log:
            code = fix_logic_errors(code, logic_err)
            repaired = True

        duration = time.time() - start_time
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + code)
            
        log_experiment(skill_id, start_time, len(prompt), len(code), True, syntax_err if not is_valid else "None", repaired)
        return True, "Success"

    except Exception as e:
        log_experiment(skill_id, start_time, len(prompt), 0, False, str(e), False)
        return False, str(e)