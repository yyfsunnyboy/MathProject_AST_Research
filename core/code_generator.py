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

可用的工具函式包括：
- `fmt_num(num, signed=False, op=False)`: 格式化數字為 LaTeX
- `to_latex(num)`: 將分數轉為 LaTeX 格式
- `is_prime(n)`, `gcd(a, b)`, `lcm(a, b)`, `get_factors(n)`: 數論工具
- `check(user_answer, correct_answer)`: 標準批改函式（已預先定義）

### ⚠️ 核心開發原則 (Universal Rules):

**1. 環境約束 (Environment Constraints)**
   - ✅ 僅使用預載工具 (`random`, `math`, `re`, `Fraction`)
   - ❌ 禁止 Import 任何模組（包括重複 import 預載工具）
   - ❌ 禁止使用 `numpy`, `matplotlib`, `sympy` 等外部套件
   - ❌ 禁止使用 `eval()` 或 `exec()`
   - ✅ Python 3 語法：`list(range())` 而非 `range() + range()`

**2. 數值計算原則 (Numerical Computing)**
   - ✅ 整數運算使用 `//` (整除) 和 `%` (取餘)
   - ✅ 分數運算使用 `Fraction(a, b)`
   - ✅ 三角函數使用 `math.sin()`, `math.cos()` 等
   - ✅ 浮點數比較使用 `math.isclose(a, b, rel_tol=1e-9)`
   - ❌ 避免直接使用 `/` 導致意外的浮點數

**3. LaTeX 渲染規範 (LaTeX Rendering)**
   - ✅ 整個題目用一對 `$...$` 包裹（外層單一環境）
   - ✅ 數字使用 `fmt_num(n)` 自動處理括號
   - ✅ 運算符轉換：
```python
     # 四則運算
     '*' → '\\times'
     '/' → '\\div'
     '+' → '+'
     '-' → '-'
     
     # 進階運算
     '**' → '^{...}'        # 次方
     'sqrt' → '\\sqrt{...}' # 根號
     'frac' → '\\frac{...}{...}' # 分數
```
   - ❌ 禁止碎片化：`f"${a}$ + ${b}$"` ❌

**4. 程式結構規範 (Code Structure)**
   - ✅ 必須定義 `def generate(level=1, **kwargs):`
   - ✅ 必須回傳：
```python
     return {
         'question_text': q,      # 題目文字 (LaTeX 格式)
         'correct_answer': a,     # 正確答案
         'answer': a,             # 用於批改
         'mode': 1                # 題型編號
     }
```
   - ✅ 在 return 前必須執行 Sanitization：
```python
     if isinstance(q, str):
         q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
         q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
     if isinstance(a, str):
         if "=" in a: a = a.split("=")[-1].strip()
```

### 🚨 常見錯誤與修正 (Common Pitfalls):

| 錯誤類型 | 錯誤寫法 | 正確寫法 | 適用領域 |
|---------|---------|---------|---------|
| **Range 串接** | `range(-5,0) + range(1,6)` | `list(range(-5,0)) + list(range(1,6))` | 所有領域 |
| **自創工具** | `def format_num(n): ...` | 直接使用 `fmt_num(n)` | 所有領域 |
| **運算符未轉換** | `f"${a} * {b}$"` | `f"${fmt_num(a)} \\times {fmt_num(b)}$"` | 四則運算 |
| **浮點數除法** | `a = n1 / n2` | `a = n1 // n2` 或 `Fraction(n1, n2)` | 整數/分數 |
| **使用 eval** | `eval(f"{a}+{b}")` | `a + b` | 所有領域 |
| **分數格式** | `f"{a}/{b}"` | `to_latex(Fraction(a, b))` | 分數運算 |
| **三角函數** | `sin(x)` | `math.sin(math.radians(x))` | 三角函數 |
| **次方運算** | `f"${a}^{b}$"` | `f"${a}^{{{b}}}$"` (三層大括號) | 多項式 |

### 📚 領域專用範例 (Domain-Specific Examples):

**範例 1: 整數四則運算**
```python
def generate(level=1, **kwargs):
    n1 = random.randint(-12, 12)
    n2 = random.randint(2, 12)
    
    op_char = random.choice(['*', '/'])
    op_latex = '\\times' if op_char == '*' else '\\div'
    
    a = n1 * n2 if op_char == '*' else n1 // n2
    q = f"${fmt_num(n1)} {op_latex} {fmt_num(n2)}$"
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

**範例 2: 分數運算**
```python
def generate(level=1, **kwargs):
    # 生成兩個真分數
    num1, den1 = random.randint(1, 9), random.randint(2, 12)
    num2, den2 = random.randint(1, 9), random.randint(2, 12)
    
    frac1 = Fraction(num1, den1)
    frac2 = Fraction(num2, den2)
    
    # 加法運算
    result = frac1 + frac2
    
    # LaTeX 格式化
    q = f"${to_latex(frac1)} + {to_latex(frac2)}$"
    a = to_latex(result)
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

**範例 3: 一元二次方程式**
```python
def generate(level=1, **kwargs):
    # 生成標準式 ax² + bx + c = 0
    a_coef = random.choice([1, 2, 3])
    b_coef = random.randint(-10, 10)
    c_coef = random.randint(-10, 10)
    
    # 判別式
    discriminant = b_coef**2 - 4*a_coef*c_coef
    
    # 確保有實數解
    if discriminant < 0:
        c_coef = -abs(c_coef)  # 強制有解
    
    # 生成題目
    if a_coef == 1:
        a_str = "x^{2}"
    else:
        a_str = f"{a_coef}x^{{{2}}}"
    
    b_str = fmt_num(b_coef, op=True) + "x"
    c_str = fmt_num(c_coef, op=True)
    
    q = f"${a_str}{b_str}{c_str} = 0$"
    
    # 計算解（使用公式解）
    sqrt_disc = math.sqrt(discriminant)
    x1 = (-b_coef + sqrt_disc) / (2 * a_coef)
    x2 = (-b_coef - sqrt_disc) / (2 * a_coef)
    
    if math.isclose(x1, x2):
        a = f"{x1:.2f}"
    else:
        a = f"{x1:.2f}, {x2:.2f}"
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

**範例 4: 三角函數**
```python
def generate(level=1, **kwargs):
    # 生成特殊角
    angle = random.choice([0, 30, 45, 60, 90])
    func = random.choice(['sin', 'cos', 'tan'])
    
    # 計算答案
    rad = math.radians(angle)
    if func == 'sin':
        a = math.sin(rad)
        func_latex = '\\sin'
    elif func == 'cos':
        a = math.cos(rad)
        func_latex = '\\cos'
    else:
        a = math.tan(rad) if angle != 90 else 'undefined'
        func_latex = '\\tan'
    
    # 格式化答案（保留常見值）
    if isinstance(a, float):
        if math.isclose(a, 0): a = "0"
        elif math.isclose(a, 1): a = "1"
        elif math.isclose(a, 0.5): a = "\\frac{1}{2}"
        elif math.isclose(a, math.sqrt(3)/2): a = "\\frac{\\sqrt{3}}{2}"
        else: a = f"{a:.4f}"
    
    q = f"${func_latex}({angle}^\\circ)$"
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

**範例 5: 微積分（導數）**
```python
def generate(level=1, **kwargs):
    # 生成簡單多項式 ax^n
    coef = random.randint(1, 10)
    power = random.randint(2, 5)
    
    # 原函式
    if coef == 1:
        q = f"$x^{{{power}}}$"
    else:
        q = f"${coef}x^{{{power}}}$"
    
    # 計算導數
    deriv_coef = coef * power
    deriv_power = power - 1
    
    if deriv_power == 0:
        a = str(deriv_coef)
    elif deriv_power == 1:
        a = f"{deriv_coef}x" if deriv_coef != 1 else "x"
    else:
        a = f"{deriv_coef}x^{{{deriv_power}}}"
    
    q = f"對 {q} 求導"
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

### 🎯 開發流程建議 (Development Workflow):

**第 1 步：理解 MASTER_SPEC**
- 識別數學領域（整數、分數、代數、幾何、微積分等）
- 確認輸入輸出格式（數值、表達式、方程式等）

**第 2 步：選擇合適工具**
- 整數運算 → `random.randint()`, `//`, `%`
- 分數運算 → `Fraction(a, b)`
- 三角函數 → `math.sin/cos/tan()`, `math.radians()`
- 複雜表達式 → 先計算數值，再轉為 LaTeX

**第 3 步：構建題目邏輯**
- 生成數值 → 計算答案 → 格式化為 LaTeX
- 確保每個運算符都正確轉換

**第 4 步：執行 Sanitization**
- 使用標準清洗代碼（見上方）

**第 5 步：自我檢查**
- [ ] 沒有重複 import
- [ ] 沒有使用 eval()
- [ ] LaTeX 格式正確（單一 $ 環境）
- [ ] Python 3 語法（list(range())）
- [ ] 回傳格式完整

### 📖 LaTeX 速查表 (Quick Reference):

| 數學符號 | LaTeX 語法 | 使用場景 |
|---------|-----------|---------|
| 乘法 | `\\times` | 整數、分數 |
| 除法 | `\\div` | 整數 |
| 分數 | `\\frac{a}{b}` | 分數運算 |
| 次方 | `x^{n}` | 多項式、指數 |
| 根號 | `\\sqrt{x}` | 根式運算 |
| 絕對值 | `|x|` | 數值分析 |
| 三角函數 | `\\sin, \\cos, \\tan` | 三角函數 |
| 微分 | `\\frac{d}{dx}` | 微積分 |
| 積分 | `\\int` | 微積分 |
| 極限 | `\\lim_{x \\to a}` | 極限 |
| 總和 | `\\sum_{i=1}^{n}` | 級數 |
| 矩陣 | `\\begin{pmatrix}...\\end{pmatrix}` | 線性代數 |

【任務目標】
撰寫一個完整的 `generate(level=1, **kwargs)` 函式。

【嚴格代碼規範】
（保持原有內容...）

【輸出限制 (最重要的防火牆)】
- 僅輸出 Python 程式碼，不包含 Markdown 標籤。
- **嚴禁**使用 matplotlib, numpy。
- **嚴禁**使用 `eval()` 函式。
- **嚴禁**寫入任何 `import` 語句 (random, math, re, fractions 皆已預載，重複寫入會導致系統崩潰)。
- **嚴禁**重新定義 `fmt_num` 或 `to_latex`。
- **嚴禁**自創任何格式化函式（如 `format_number_for_latex`）。
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
        
        # Step 1: 移除 Markdown
        clean_code, n = re.subn(r'```python|```', '', raw_output, flags=re.DOTALL)
        regex_fixes += n

        # Step 2: 清洗特殊空格
        original_len = len(clean_code)
        clean_code = clean_code.replace('\xa0', ' ').replace('　', ' ').strip()
        if len(clean_code) != original_len:
            regex_fixes += 1  # ✅ 新增計數

        # Step 3: 移除重複 Import
        clean_code, import_removed, removed_list = clean_redundant_imports(clean_code)  # ✅ 接收三個值
        regex_fixes += import_removed  # ✅ 累加
        
        # Step 4: 包裹函式
        if "def generate" not in clean_code:
            # [FIX] 這裡手動輸入標準的 4 個 ASCII 空格 ( )，不要用 Tab 或 NBSP
            indent_str = '    ' 
            clean_code = "def generate(level=1, **kwargs):\n" + textwrap.indent(clean_code, indent_str)
            
            if "return" not in clean_code:
                # 這裡的換行後縮排也確保是標準空格
                clean_code += "\n    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}"
            regex_fixes += 1

        # 6. 語法修復
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
        if 'def generate' in clean_code:
             if 'import ' in clean_code.split('def generate')[0]:
                warnings.append("重複 import")
        elif 'import ' in clean_code:
             warnings.append("重複 import")
        if '{op_latex}' in clean_code and 'op_latex =' not in clean_code:
            warnings.append("op_latex 未定義")

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

        return True, "V44.2 Generated", {
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
    在 V44.2 架構下，AI 已生成單一完整邏輯，不需要分流注入。
    直接回傳原代碼即可維持相容性。
    """
    return code_str

def validate_and_fix_code(c): return c, 0
def fix_logic_errors(c, e): return c, 0