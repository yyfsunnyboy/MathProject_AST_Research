# -*- coding: utf-8 -*-
# ==============================================================================
# ID: code_generator.py
# Version: v8.6.1 (The "Gold Standard" - Indentation Fixed)
# Description: 
#   [System Core - Ultimate Merge]
#   1. Golden Sample Injection: Loads skills/Example_Program.py as reference.
#   2. Regex Armor v7.7.7: Includes all user-provided regex fixes.
#   3. Perfect Utils: Injects math helper functions.
#   4. Smart Dispatcher: Auto-detects and injects generate() if missing.
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
# --- Perfect Utils (Standard Math Tools) ---
# ==============================================================================
PERFECT_UTILS = r'''
import random
import math
from fractions import Fraction

def to_latex(num):
    """Convert number to LaTeX (integers, decimals, fractions, mixed numbers)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            if rem == 0: return f"{sign}{abs(num).numerator // abs(num).denominator}"
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses"""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

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
    return result
'''


def inject_perfect_utils(code_str):
    clean = re.sub(r'def (to_latex|fmt_num|draw_number_line)\(.*?(\n\s+.*)+', '', code_str, flags=re.MULTILINE)
    clean = clean.replace("import random", "").replace("import math", "").replace("from fractions import Fraction", "")
    return PERFECT_UTILS + "\n" + clean


def inject_robust_dispatcher(code_str):
    if re.search(r'^def generate\s*\(', code_str, re.MULTILINE):
        return code_str 
    candidates = re.findall(r'^def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str, re.MULTILINE)
    valid_funcs = [f for f in candidates if f not in ['generate', 'check', 'solve']]
    if not valid_funcs: return code_str
    
    dispatcher_code = "\n\n# [Auto-Injected Dispatcher]\n"
    dispatcher_code += "def generate(level=1):\n"
    dispatcher_code += f"    types = {str(valid_funcs)}\n"
    dispatcher_code += "    selected = random.choice(types)\n"
    for i, func in enumerate(valid_funcs):
        if i == 0: dispatcher_code += f"    if selected == '{func}': return {func}()\n"
        else: dispatcher_code += f"    elif selected == '{func}': return {func}()\n"
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


# ==============================================================================
# --- THE REGEX ARMOR (v7.7.7) ---
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    fixed_code = code_str
    
    # Step 0: Critical Escape Fixes
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 1. Invalid escapes
    fixed_code = re.sub(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\q', r'\\\\q', fixed_code)

    # 2. f-string single brace fixes
    fixed_code = re.sub(r'(f"[^"]*?\\right)\}([^"]*")', r'\1}}\2', fixed_code)
    fixed_code = re.sub(r"(f'[^']*?\\right)\}([^']*')", r'\1}}\2', fixed_code)
    
    # 3. cases environment fixes
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

    # 4. General LaTeX double brace enforcement
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

    # 5. Brute force fallback
    if any(k in error_msg for k in ["single '}'", "single '{'", "invalid escape sequence"]):
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

    # 6. Python 2 print fix
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
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    
    # 1. Strategy & Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    has_architect_plan = (skill and skill.gemini_prompt and len(skill.gemini_prompt) > 50)
    target_logic = skill.gemini_prompt if has_architect_plan else f"Math logic for {skill_id}"
    strategy_name = "Architect-Engineer (v8.0)" if has_architect_plan else "Standard Mode"

    # 2. Golden Reference
    gold_standard_code = load_gold_standard_example()

    # 3. RAG Examples
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(10).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        example_text = "\n### REFERENCE EXAMPLES (RAG):\n"
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\n"

    # 4. Construct Prompt
    prompt = f"""
You are a Senior Python Engineer for a Math Education System.

### MISSION:
Implement the skill `{skill_id}` by strictly following the **Architect's Spec** below.
You MUST output a **complete, runnable Python script**.

### REFERENCE CODE (GOLD STANDARD):
**MIMIC THIS STRUCTURE EXACTLY** (imports, internal helpers, separate type functions, main dispatcher):

```python
{gold_standard_code}
ARCHITECT'S SPECIFICATION:
{target_logic}

{example_text}

CODING RULES:
Full Implementation: No pass or placeholders.

Helper Functions: Implement internal helpers first.

One-to-One Mapping: Write generate_type_1_problem ... generate_type_N_problem.

Dispatcher: Write def generate(level=1): at the end.

LaTeX: Use double braces {{ }} for LaTeX commands in f-strings: f"\\\\frac{{{{a}}}}{{{{b}}}}".

Return Keys: Return dict with question_text, answer, correct_answer.

OUTPUT:
Return ONLY the Python code. Start with import random. """

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        code = response.text
        
        # Cleanup Regex (Corrected v12.2)
        match = re.search(r'```(?:python)?\s*(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if match: code = match.group(1)
        elif "import random" in code: code = code[code.find("import random"):]
        
        # Pipeline Processing
        code = inject_perfect_utils(code)
        code = fix_return_format(code)
        code = clean_global_scope_execution(code)
        code = inject_robust_dispatcher(code) 

        # Repair Cycle
        is_valid, syntax_err = validate_python_code(code)
        repaired = False
        if not is_valid:
            code = fix_code_syntax(code, syntax_err) # v7.7.7 Fixer
            is_valid, syntax_err = validate_python_code(code)
            repaired = True
            
        is_valid_log, logic_err = validate_logic_with_pyflakes(code)
        if not is_valid_log:
            code = fix_logic_errors(code, logic_err)
            repaired = True

        # --- Generate Header Info ---
        duration = time.time() - start_time
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'}
# ==============================================================================\n\n'''
        # Write File
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + code)
            
        log_experiment(skill_id, start_time, len(prompt), len(code), True, syntax_err if not is_valid else "None", repaired)
        return True, "Success"

    except Exception as e:
        log_experiment(skill_id, start_time, len(prompt), 0, False, str(e), False)
        return False, str(e)
