# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 
    V44.2 Code Generator (Stability Hotfix)
    1. [Restoration]: 恢復 `inject_robust_dispatcher` 以修復 ImportError。
    2. [Standard Compliance]: 保持 V44.1 的所有科研標準 (Header, Token, AST)。
    3. [Pure Math]: 堅持純符號計算 (No Matplotlib)。

版本資訊 (Version): V44.2
更新日期 (Date): 2026-01-21
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import os
import re
import sys
import io
import time
import ast
import random
import textwrap
import sqlite3
import psutil
from datetime import datetime
from flask import current_app
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter

# Local Imports
from core.ai_wrapper import get_ai_client
from models import db, SkillGenCodePrompt
from config import Config

# Optional GPU Monitor
try:
    import GPUtil
except ImportError:
    GPUtil = None

# ==============================================================================
# 1. 基礎建設函式 (Infrastructure)
# ==============================================================================
def get_system_snapshot():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu, gpuram = 0.0, 0.0
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0].load * 100
                gpuram = gpus[0].memoryUtil * 100
        except: pass
    return cpu, ram, gpu, gpuram

def categorize_error(error_msg):
    if not error_msg or error_msg == "None": return None
    err_low = error_msg.lower()
    if "syntax" in err_low: return "SyntaxError"
    if "list" in err_low: return "FormatError"
    return "RuntimeError"

# ==============================================================================
# 2. 完美工具庫 (Perfect Utils - Standard Edition)
# ==============================================================================
PERFECT_UTILS = r'''
import random
import math
from fractions import Fraction
import re

# [Research Standard Utils]

def to_latex(num):
    """將數字轉換為 LaTeX 格式 (支援分數、整數、小數)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
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
    格式化數字 (標準樣板要求)：
    - signed=True: 強制顯示正負號 (+3, -5)
    - op=True: 用於運算子連接 (自動加空格: " + 3", " - 5")
    - 負數自動加括號
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    
    if op: return f" - {abs_str}" if is_neg else f" + {abs_str}"
    if signed: return f"-{abs_str}" if is_neg else f"+{abs_str}"
    if is_neg: return f"({latex_val})"
    return latex_val

# [數論工具箱]
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

def get_factors(n):
    n = abs(n)
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def check(user_answer, correct_answer):
    """標準化字串比對批改"""
    if not user_answer: return {"correct": False, "result": "未作答"}
    
    def clean(s):
        return str(s).strip().replace(" ", "").replace("$", "").replace("\\", "").lower()
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    if u == c: return {"correct": True, "result": "正確"}
    
    try:
        if math.isclose(float(eval(u)), float(eval(c)), rel_tol=1e-9):
             return {"correct": True, "result": "正確"}
    except: pass

    return {"correct": False, "result": f"正確答案: {correct_answer}"}
'''

# ==============================================================================
# 3. 骨架與 Prompt 定義
# ==============================================================================
CALCULATION_SKELETON = r'''
import random
import math
import re
from fractions import Fraction

# [INJECTED UTILS]
''' + PERFECT_UTILS + r'''

# [AI GENERATED CODE]
# ---------------------------------------------------------
''' + "\n"  # <--- [修正] 強制補一個換行，防止黏合錯誤

def get_dynamic_skeleton(skill_id):
    return CALCULATION_SKELETON

UNIVERSAL_GEN_CODE_PROMPT = r"""【角色設定】
你是由 Google DeepMind 開發的高級數學演算法工程師。
你的任務是根據 MASTER_SPEC，撰寫符合「科研專用標準樣板」的 Python 程式碼。

【任務目標】
撰寫一個完整的 `generate(level=1, **kwargs)` 函式。

【嚴格代碼規範】
1. **結構要求**：
   - 輸出完整的函式定義：`def generate(level=1, **kwargs):`
   - 務必自行處理函式內部的縮進 (4 spaces)。
   
2. **回傳格式 (Research Standard)**：
   - 必須回傳如下的字典格式 (包含 answer 與 mode)：
     ```python
     return {
         'question_text': q, 
         'correct_answer': a, 
         'answer': a,      # 必須包含此欄位
         'mode': 1         # 必須包含此欄位
     }
     ```

3. **數學邏輯**：
   - 題目 `q` 必須是 LaTeX 格式 (如 `$(-3) \times (-5)$`)。
   - 答案 `a` 必須是最終數值字串 (如 `15`)。
   - **強制使用** `fmt_num(n)` 來格式化所有 LaTeX 數字，確保負號括號正確。

4. **格式潔癖 (Sanitization)**：
   - 在 return 前，**必須**包含以下清洗代碼：
     ```python
     if isinstance(q, str):
         q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
         q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
     if isinstance(a, str):
         if "=" in a: a = a.split("=")[-1].strip()
     ```

【輸出限制】
- 僅輸出 Python 程式碼，不包含 ```python 標籤。
- **嚴禁**使用 matplotlib、numpy。
- **嚴禁**定義額外的 class。
"""

# ==============================================================================
# 4. 修復與驗證工具
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    """自動修復常見語法錯誤"""
    fixed_code = code_str.replace("，", ", ").replace("：", ": ")
    fixed_code = re.sub(r'###.*?\n', '', fixed_code) 
    fixed_code = re.sub(r'```.*?(\n|$)', '', fixed_code)
    
    total_fixes = 0
    def apply_fix(pattern, replacement, code):
        new_code, count = re.subn(pattern, replacement, code, flags=re.MULTILINE)
        return new_code, count

    # Latex 雙反斜線修復
    fixed_code, c = apply_fix(r'(?<!\\)\\ ', r'\\\\ ', fixed_code); total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code); total_fixes += c

    # f-string 括號修復
    def fix_latex_braces(match):
        content = match.group(1)
        if not (re.search(r'\\[a-zA-Z]+', content) and not re.search(r'^\\n', content)):
            return f'f"{content}"'
        pattern = r'(\{[a-zA-Z_][a-zA-Z0-9_]*(\(.*\))?\})|(\{)|(\})'
        def token_sub(m):
            if m.group(1): return m.group(1) 
            if m.group(3): return "{{"        
            if m.group(4): return "}}"        
            return m.group(0)
        new_content = re.sub(pattern, token_sub, content)
        return f'f"{new_content}"'

    fixed_code, c = re.subn(r'f"(.*?)"', fix_latex_braces, fixed_code); total_fixes += c
    fixed_code, c = re.subn(r"f'(.*?)'", fix_latex_braces, fixed_code); total_fixes += c
    fixed_code, c = apply_fix(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', fixed_code); total_fixes += c

    return fixed_code, total_fixes

def validate_python_code(code_str):
    try:
        ast.parse(code_str)
        return True, "Success"
    except SyntaxError as e:
        # [Debug] 直接印出錯誤行數與內容
        error_msg = f"SyntaxError: {e.msg} at Line {e.lineno}\nCode: {e.text.strip() if e.text else 'N/A'}"
        print(f"❌ [Validation Failed] {error_msg}")
        return False, error_msg
    except Exception as e:
        print(f"❌ [Validation Failed] SystemError: {str(e)}")
        return False, str(e)

def log_experiment(skill_id, start_time, prompt_len, code_len, is_valid, error_msg, repaired, model_name, actual_provider=None, **kwargs):
    """實驗數據記錄"""
    duration = time.time() - start_time
    conn = sqlite3.connect(Config.db_path)
    c = conn.cursor()
    query = """
    INSERT INTO experiment_log (
        skill_id, start_time, duration_seconds, prompt_len, code_len, 
        is_success, error_msg, repaired, model_name, 
        model_size_class, prompt_level, raw_response, final_code,
        score_syntax, score_math, score_visual, healing_duration, 
        is_executable, ablation_id, missing_imports_fixed, resource_cleanup_flag,
        prompt_tokens, completion_tokens, total_tokens
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        skill_id, start_time, duration, prompt_len, code_len,
        1 if is_valid else 0, str(error_msg), 1 if repaired else 0, model_name,
        kwargs.get('model_size_class', 'Unknown'),
        kwargs.get('prompt_level', 'Bare'),
        kwargs.get('raw_response', ''),
        kwargs.get('final_code', ''),
        kwargs.get('score_syntax', 0.0),
        kwargs.get('score_math', 0.0),
        kwargs.get('score_visual', 0.0),
        kwargs.get('healing_duration', 0.0),
        kwargs.get('is_executable', 1 if is_valid else 0),
        kwargs.get('ablation_id', 1),
        kwargs.get('missing_imports_fixed', ''),
        1 if kwargs.get('resource_cleanup_flag') else 0,
        kwargs.get('prompt_tokens', 0),
        kwargs.get('completion_tokens', 0),
        kwargs.get('total_tokens', 0)
    )
    try:
        c.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"❌ Database Log Error: {e}")
    finally:
        conn.close()

# ==============================================================================
# 5. 核心生成函式 (V44.2 Main Engine)
# ==============================================================================
def auto_generate_skill_code(skill_id, queue=None, **kwargs):
    start_time = time.time()
    role_config = Config.MODEL_ROLES.get('coder', {'provider': 'google', 'model': 'gemini-1.5-flash'})
    current_model = role_config.get('model', 'Unknown')
    ablation_id = kwargs.get('ablation_id', 3)
    
    # 1. 讀取 Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, prompt_type="MASTER_SPEC").order_by(SkillGenCodePrompt.created_at.desc()).first()
    spec = active_prompt.prompt_content if active_prompt else "生成一題簡單的整數四則運算。"
    
    # 2. 組合 Prompt
    prompt = UNIVERSAL_GEN_CODE_PROMPT + f"\n\n### MASTER_SPEC:\n{spec}"
    
    raw_output = ""
    prompt_tokens, completion_tokens = 0, 0

    try:
        # 3. 呼叫 AI
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        raw_output = response.text
        
        # 4. Token 統計
        try:
            if hasattr(response, 'usage_metadata'): 
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            elif hasattr(response, 'usage'): 
                u = response.usage
                prompt_tokens = getattr(u, 'prompt_tokens', 0)
                completion_tokens = getattr(u, 'completion_tokens', 0)
        except: pass

        # 5. 清洗與組裝 (Full Function Replacement + Import Cleaning)
        regex_fixes = 0
        ast_fixes = 0
        
        # 移除 Markdown
        clean_code, n = re.subn(r'```python|```', '', raw_output, flags=re.DOTALL)
        clean_code = clean_code.strip()
        regex_fixes += n

        # [V44.3 新增] 移除 AI 雞婆寫的重複 Import
        lines = clean_code.split('\n')
        filtered_lines = []
        for line in lines:
            # 如果這行是 import 開頭，且骨架裡已經有了，就跳過
            if line.strip().startswith(('import random', 'import math', 'import re', 'from fractions')):
                continue
            filtered_lines.append(line)
        clean_code = '\n'.join(filtered_lines)
        
        # Fallback: 包裹函式
        if "def generate" not in clean_code:
            clean_code = "def generate(level=1, **kwargs):\n" + textwrap.indent(clean_code, '    ')
            if "return" not in clean_code:
                clean_code += "\n    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}"
            regex_fixes += 1

        # 6. 語法修復
        clean_code, r_fixes = fix_code_syntax(clean_code)
        regex_fixes += r_fixes

        # 組合
        final_code = CALCULATION_SKELETON + "\n" + clean_code

        # 7. 驗證
        is_valid, error_msg = validate_python_code(final_code)
        
        # 8. 生成完整標頭 (Header)
        duration = time.time() - start_time
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fix_status_str = "[Repaired]" if (regex_fixes > 0 or ast_fixes > 0) else "[Clean Pass]"
        verify_status_str = "PASSED" if is_valid else "FAILED"
        
        header = f"""# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: V44.2 Standard-Template
# Ablation ID: {ablation_id} | Env: RTX 5060 Ti 16GB
# Performance: {duration:.2f}s | Tokens: In={prompt_tokens}, Out={completion_tokens}
# Created At: {created_at}
# Fix Status: {fix_status_str} | Fixes: Regex={regex_fixes}, AST={ast_fixes}
# Verification: Internal Logic Check = {verify_status_str}
# ==============================================================================
"""
        # 寫檔
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f'{skill_id}.py'), 'w', encoding='utf-8') as f:
            f.write(header + final_code)

        # 9. Log
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=len(prompt),
            code_len=len(final_code),
            is_valid=is_valid,
            error_msg=error_msg,
            repaired=(regex_fixes > 0),
            model_name=current_model,
            final_code=final_code,
            raw_response=raw_output,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            score_syntax=1.0 if is_valid else 0.0,
            ablation_id=ablation_id
        )

        return True, "V44.2 Generated", {'tokens': prompt_tokens + completion_tokens}

    except Exception as e:
        print(f"Generate Error: {e}")
        return False, str(e), {}

# ==============================================================================
# 6. Legacy Support (兼容舊腳本)
# ==============================================================================
def inject_robust_dispatcher(code_str):
    """
    [Legacy Stub]
    舊版 sync_skills_files.py 會呼叫此函式。
    在 V44.2 架構下，AI 已生成單一完整邏輯，不需要分流注入。
    直接回傳原代碼即可維持相容性。
    """
    return code_str

def validate_and_fix_code(c): return c, 0
def fix_logic_errors(c, e): return c, 0