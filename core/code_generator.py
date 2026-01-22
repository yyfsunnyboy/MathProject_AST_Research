# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 
    V44.9 Code Generator (Hybrid-Healing Edition)
    1. [Hybrid Healing]: 加強對小模型 (Qwen/14B) 的自動修復策略與警告機制。
    2. [LaTeX Safety]: 修復 LaTeX 運算符誤用（例如 `\*`、`\/`）並新增 f-string 檢測警示。
    3. [Prompt Upgrade]: 更新 `UNIVERSAL_GEN_CODE_PROMPT` 以明確禁止自創格式化函式與使用 eval() 處理 LaTeX。

版本資訊 (Version): V44.9 (Hybrid-Healing Edition)
更新日期 (Date): 2026-01-22
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
    """
    將數字轉換為 LaTeX 格式 (支援分數、整數、小數)
    [V44.9 Fix]: 強制將負號提取至分數外層，避免 \frac{-1}{7} 這種寫法。
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        
        # 統一處理正負號
        is_neg = num < 0
        sign_str = "-" if is_neg else ""
        abs_num = abs(num)
        
        # 帶分數處理 (Mixed Number)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: 
                return f"{sign_str}{whole}"
            # 輸出格式: -1 \frac{3}{7}
            return f"{sign_str}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
            
        # 真分數處理 (Proper Fraction)
        # [Fix]: 使用 abs_num.numerator 確保分子永遠是正的，負號由 sign_str 控制
        return f"{sign_str}\\frac{{{abs_num.numerator}}}{{{abs_num.denominator}}}"
        
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    格式化數字 (標準樣板要求)：
    - 自動括號：負數會自動被包在括號內 (-5) 或 (-\frac{1}{2})
    - signed=True: 強制顯示正負號 (+3, -5)
    """
    # 1. 取得基礎 LaTeX 字串 (這時負號已經在最前面了，例如 -\frac{1}{7})
    latex_val = to_latex(num)
    
    # 2. 判斷是否為 0
    if num == 0 and not signed and not op: return "0"
    
    # 3. 判斷正負 (依賴數值本身，而非字串)
    is_neg = (num < 0)
    
    # 為了處理 op=True 或 signed=True，我們需要絕對值的字串
    # 但這裡為了效率，我們直接操作 latex_val
    if is_neg:
        # 移除開頭的負號以取得絕對值內容
        abs_latex_val = latex_val[1:] 
    else:
        abs_latex_val = latex_val

    # 4. 組裝回傳值
    if op: 
        # op=True: 用於運算子連接 " + 3", " - 5"
        return f" - {abs_latex_val}" if is_neg else f" + {abs_latex_val}"
    
    if signed: 
        # signed=True: 強制帶號 "-5", "+3"
        return f"-{abs_latex_val}" if is_neg else f"+{abs_latex_val}"
    
    if is_neg: 
        # 預設模式: 負數加括號 (-\frac{1}{7})
        return f"({latex_val})"
        
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

【環境說明 (Tool Definition)】
系統已預先載入以下工具，**請勿重複 Import，否則會導致變數遮蔽 (Shadowing) 錯誤**：
- `import random`
- `import math`
- `import re`
- `from fractions import Fraction`

### 核心工具說明 (Crucial Utils Usage):
1. **`def fmt_num(num, signed=False, op=False)`**: 
   - **功能**: 將數字轉為 LaTeX 格式字符串 (整數、分數、小數皆可)。
   - **預設用法 `fmt_num(n)` (推薦)**: 
     - 正數回傳 `"5"`，負數回傳 `"(-5)"`。
     - 分數 `Fraction(1, 2)` 回傳 `\frac{1}{2}`，負分數回傳 `(-\frac{1}{2})`。
   - **禁忌用法**: 嚴禁對表達式首項使用 `op=True`。

2. **`def to_latex(num)`**: 自動將分數物件轉為 `\frac{a}{b}` 格式 (自動約分、處理負號)。

【任務目標】
撰寫一個完整的 `generate(level=1, **kwargs)` 函式。

【安全層架構 (Four Safety Pillars)】

◆ **第一層：零值防護 (Zero Safety)**
   - **科學上的原因**：分母為 0 或除數為 0 會引發 ZeroDivisionError，導致程序中止。
   - **強制標準**：所有隨機生成的分母、除數必須透過 while 迴圈確保非零。
   - **標準範例**：
     ```python
     denom = random.randint(2, 10)
     while denom == 0:
         denom = random.randint(2, 10)
     ```
   - **或**：
     ```python
     divisor = random.randint(1, 10)
     while divisor == 0:
         divisor = random.randint(1, 10)
     ```

◆ **第二層：反浮點數禁止 (Anti-Float Mandate)**
   - **嚴禁**使用 `float`, `/` (Python 3 float division)。
   - **必須**使用 `Fraction(numerator, denominator)` 進行所有除法運算。

◆ **第三層：反 eval() 防火牆 (Anti-Eval)**
   - **嚴禁**使用 `eval()`、`exec()`。
   - 所有數學運算必須用 Python 原生操作符或 `Fraction` 完成。

◆ **第四層：格式嚴格令 (Format-Strict)**
   - LaTeX 運算符必須用 `\times`, `\div`，不可用 `*`, `/`。
   - 分數必須用 `\frac{a}{b}` 格式，不可手動拼接。

【嚴格代碼規範】
1. **結構要求**：
   - 輸出完整的函式定義：`def generate(level=1, **kwargs):`
   - 務必自行處理函式內部的縮進 (4 spaces)。
   
2. **回傳格式 (Research Standard)**：
   - 必須回傳如下的字典格式：
     ```python
     return {
         'question_text': q, 
         'correct_answer': a, 
         'answer': a,      # 用於自動批改
         'mode': 1         # 題型編號
     }
     ```

3. **LaTeX 格式與運算鐵律 (Crucial)**：
   - **單一環境原則**：`question_text` 必須**只在最外層**包裹一對 `$`。
   - **連鎖運算標準模式**：
     - `q += f" {op} {fmt_num(next_val)}"` (利用 fmt_num 自動處理負號括號)。
     - **禁止**將 `operators` 列表與 `fmt_num(..., signed=True)` 同時使用。

   - **分數與工具強制令 (Fraction Strict Rules)**：
     - **運算邏輯**：凡涉及分數計算，**必須**使用 Python `Fraction(num, den)` 物件，**嚴禁**手動進行 GCD 約分或整數除法模擬。
     - **顯示邏輯**：
       - **嚴禁**手動拼接 LaTeX 字串 (如 `f"\\frac{{{n}}}{{{d}}}"` 或 `\\left(-\\frac...\\right)` )。
       - **必須**將 `Fraction` 物件傳入 `fmt_num()` 或 `to_latex()` 來取得 LaTeX 字串。
       - 範例:
         - ❌ 錯誤: `term = f"\\frac{{{n}}}{{{d}}}"`
         - ✅ 正確: `term = to_latex(Fraction(n, d))` (系統會自動處理負號與括號)

   - **運算符映射**：
     - **禁止**將 LaTeX 符號 (`\times`, `\div`) 放入 `eval()`。
     - **禁止**使用 f-string 直接插入反斜線運算符 (如 `f"\\{op}"`)，必須使用顯式轉換。

4. **格式潔癖 (Sanitization)**：
   - 在 return 前，**必須**包含以下清洗代碼：
     ```python
     if isinstance(q, str):
         q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
         q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
     if isinstance(a, str):
         if "=" in a: a = a.split("=")[-1].strip()
     ```

【輸出限制 (最重要的防火牆)】
- 僅輸出 Python 程式碼，不包含 Markdown 標籤。
- **嚴禁**使用 matplotlib, numpy。
- **嚴禁**寫入任何 `import` 語句。
- **嚴禁**重新定義 `fmt_num` 或 `to_latex`。
"""

# ==============================================================================
# 4. 修復與驗證工具
# ==============================================================================
# [NEW] 新增這個函式來過濾 import
def clean_redundant_imports(code_str):
    """
    移除 AI 生成程式碼中重複的 Import 語句。
    這能防止變數遮蔽 (Shadowing) 並確保 AST 解析乾淨。
    """
    lines = code_str.split('\n')
    cleaned_lines = []
    removed_count = 0  # ✅ 新增計數器
    removed_list = []
    
    # 定義要過濾的關鍵字 (只要以此開頭就殺掉)
    FORBIDDEN_PREFIXES = (
        'import random', 
        'import math', 
        'import re', 
        'from fractions', 
        'import fractions',
        'from math' 
    )
    
    for line in lines:
        stripped = line.strip()
        # 如果這一行是 forbidden import，直接跳過 (刪除)
        if stripped.startswith(FORBIDDEN_PREFIXES):
            removed_count += 1  # ✅ 計數
            removed_list.append(stripped)
            continue
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines), removed_count, removed_list  # ✅ 回傳三個值

def refine_ai_code(code_str):
    """
    [Active Healer] 主動修復小模型 (如 Qwen) 常犯的錯誤
    """
    fixes = 0
    refined_code = code_str

    # 1. 移除自創的格式化函式 (Force removal of custom formatters)
    forbidden_funcs = ['format_number_for_latex', 'format_num_latex', 'latex_format', '_format_term_with_parentheses']
    
    for func_name in forbidden_funcs:
        if f'def {func_name}' in refined_code:
            lines = refined_code.split('\n')
            cleaned_lines = []
            skip_mode = False
            target_indent = -1
            
            for line in lines:
                # 偵測函式定義開頭
                if f'def {func_name}' in line:
                    skip_mode = True
                    target_indent = len(line) - len(line.lstrip())
                    fixes += 1
                    continue
                
                if skip_mode:
                    current_indent = len(line) - len(line.lstrip())
                    if not line.strip(): 
                        continue
                    if current_indent > target_indent:
                        continue
                    else:
                        skip_mode = False  # 縮排回來了，結束跳過
                
                cleaned_lines.append(line)
            
            refined_code = '\n'.join(cleaned_lines)
            
            # 2. 將該函式的呼叫替換為 fmt_num
            refined_code, n = re.subn(f'{func_name}\\(', 'fmt_num(', refined_code)
            fixes += n

    # 3. 修復錯誤的 LaTeX 運算符 (Qwen 特有錯誤: \* \/)
    refined_code, n1 = re.subn(r'(?<=f")([^{"]*?)\\\*([^{"]*?)(?=")', r'\1\\times\2', refined_code)
    refined_code, n2 = re.subn(r'(?<=f")([^{"]*?)\\\/([^{"]*?)(?=")', r'\1\\div\2', refined_code)
    fixes += (n1 + n2)

    # 4. 修復整數除法 (將 / 轉為 //) - 僅在非字串區域
    refined_code, n3 = re.subn(r'(\w+)\s*=\s*(\w+)\s*/\s*(\w+)(?=\s*(?:#|$))', r'\1 = \2 // \3', refined_code)
    fixes += n3

    return refined_code, fixes

def fix_code_syntax(code_str, error_msg=""):
    """自動修復常見語法錯誤"""
    fixed_code = code_str.replace("，", ", ").replace("：", ": ")
    fixed_code = re.sub(r'###.*?\n', '', fixed_code) 
    
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
# 5. 核心生成函式 (V44.9 Main Engine - Hybrid-Healing)
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

        # 5. 清洗與組裝 (Strict Pipeline Order)
        regex_fixes = 0
        ast_fixes = 0
        
        # Step A: 移除 Markdown
        clean_code, n = re.subn(r'```python|```', '', raw_output, flags=re.DOTALL)
        regex_fixes += n

        # Step B: 清洗特殊空格 (MUST DO BEFORE IMPORT CLEANING)
        original_len = len(clean_code)
        clean_code = clean_code.replace('\xa0', ' ').replace('　', ' ').strip()
        if len(clean_code) != original_len:
            regex_fixes += 1

        # Step C: 移除重複 Import
        clean_code, import_removed, removed_list = clean_redundant_imports(clean_code)
        regex_fixes += import_removed
        
        # Step D: 包裹函式與縮排修復
        if "def generate" not in clean_code:
            indent_str = '    '  # Standard 4 spaces
            clean_code = "def generate(level=1, **kwargs):\n" + textwrap.indent(clean_code, indent_str)
            
            if "return" not in clean_code:
                clean_code += "\n    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}"
            regex_fixes += 1

        # Step E: [NEW] 主動邏輯修復 (Healer)
        # 這是新增的關鍵步驟
        clean_code, healer_fixes = refine_ai_code(clean_code)
        regex_fixes += healer_fixes

        # Step F: 基礎語法修復
        healing_start = time.time()
        clean_code, r_fixes = fix_code_syntax(clean_code)
        regex_fixes += r_fixes

        # ========================================
        # 6.5. 通用語法修復（適用所有領域）
        # ========================================
        qwen_fixes = 0

        # A. 移除自創工具函式（通用 pattern）
        forbidden_funcs = ['format_number_for_latex', 'format_num', 'latex_format']
        for func_name in forbidden_funcs:
            if f'def {func_name}' in clean_code:
                lines = clean_code.split('\n')
                cleaned_lines = []
                skip_mode = False
                indent_level = 0
                
                for line in lines:
                    if f'def {func_name}' in line:
                        skip_mode = True
                        indent_level = len(line) - len(line.lstrip())
                        continue
                    
                    if skip_mode:
                        current_indent = len(line) - len(line.lstrip())
                        if not line.strip() or line.strip().startswith('#'):
                            continue
                        if current_indent <= indent_level and line.strip():
                            skip_mode = False
                        else:
                            continue
                    
                    cleaned_lines.append(line)
                
                clean_code = '\n'.join(cleaned_lines)
                qwen_fixes += 1

        # B. 替換自創函式為標準工具（通用替換）
        for old_func in forbidden_funcs:
            clean_code, n = re.subn(f'{old_func}\\(', 'fmt_num(', clean_code)
            qwen_fixes += n

        # B.1 修復 LaTeX 運算符錯誤 (ex: "\\*" -> "\\times", "\\/" -> "\\div")
        clean_code, n = re.subn(r'\\\*', r'\\times', clean_code)  # 匹配字串中的 \* 並替換為 \times
        qwen_fixes += n
        clean_code, n = re.subn(r'\\/', r'\\div', clean_code)      # 匹配字串中的 \/ 並替換為 \div
        qwen_fixes += n

        # B.2 偵測危險的 f-string 反斜線插入樣式 (如 f"\\{op}")，無法安全自動修復，但稍後發出警告
        # (警告會在 warnings 清單建立後加入)
        b_fstring_issue = re.search(r'f["\'].*\\\{', clean_code)
        if b_fstring_issue:
            # 記錄至本地變數，稍後會轉成正式 warnings
            fstring_problem_detected = True
        else:
            fstring_problem_detected = False

        # C. 修復 Python 3 語法錯誤
        clean_code, n = re.subn(
            r'range\(([^)]+)\)\s*\+\s*range\(([^)]+)\)',
            r'list(range(\1)) + list(range(\2))',
            clean_code
        )
        qwen_fixes += n

        # D. 修復整數除法（適用於整數運算領域）
        clean_code, n = re.subn(
            r'(\w+)\s*=\s*(\w+)\s*/\s*(\w+)(?=\s*(?:#|$))',
            r'\1 = \2 // \3',
            clean_code,
            flags=re.MULTILINE
        )
        qwen_fixes += n

        # E. 通用警告（無法自動修復）
        warnings = []
        if 'eval(' in clean_code:
            warnings.append("使用了 eval()")
            if ('\\times' in clean_code) or ('\\div' in clean_code):
                warnings.append("eval() 與 LaTeX 運算符共同出現，請移除 LaTeX 字符或避免使用 eval()")
        if 'def generate' in clean_code:
             if 'import ' in clean_code.split('def generate')[0]:
                warnings.append("重複 import")
        elif 'import ' in clean_code:
             warnings.append("重複 import")
        if '{op_latex}' in clean_code and 'op_latex =' not in clean_code:
            warnings.append("op_latex 未定義")
        # 檢查早前偵測到的 f-string 反斜線插入問題，並轉入 warnings
        try:
            if fstring_problem_detected:
                warnings.append('偵測到 f-string 直接插入反斜線運算符 (如 f"\\{op}")，請改用 op_latex 或 "\\times"/"\\div" 方法')
        except NameError:
            pass

        if warnings:
            print(f"⚠️ [{skill_id}] 偵測到問題: {', '.join(warnings)}")

        regex_fixes += qwen_fixes
        healing_duration = time.time() - healing_start

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
# Model: {current_model} | Strategy: V44.9 Hybrid-Healing
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
            repaired=(regex_fixes > 0 or ast_fixes > 0),
            model_name=current_model,
            final_code=final_code,
            raw_response=raw_output,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            score_syntax=100.0 if is_valid else 0.0,
            ablation_id=ablation_id,
            model_size_class=kwargs.get('model_size_class', 'cloud'),
            prompt_level=kwargs.get('prompt_level', 'Full-Healing'),
            healing_duration=healing_duration,
            is_executable=1 if is_valid else 0,
            missing_imports_fixed=', '.join(removed_list) if removed_list else '',
            score_math=0.0,
            score_visual=0.0,
            resource_cleanup_flag=False
        )

        return True, "V44.9 Generated", {
            'tokens': prompt_tokens + completion_tokens,
            'score_syntax': 100.0 if is_valid else 0.0,
            'fixes': regex_fixes + ast_fixes,
            'is_valid': is_valid
        }

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
    在 V44.9 架構下，AI 已生成單一完整邏輯，不需要分流注入。
    直接回傳原代碼即可維持相容性。
    """
    return code_str

def validate_and_fix_code(c): return c, 0
def fix_logic_errors(c, e): return c, 0