# -*- coding: utf-8 -*-
r"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 
    V45.0 Code Generator (op_latex Enhanced Edition)
    1. [op_latex Global]: 在 PERFECT_UTILS 中預設全域 op_latex 映射表，讓所有技能都能直接使用。
    2. [Auto-Inject Healer]: 偵測 op_latex[...] 用法但無定義時，自動在 generate() 開頭注入映射表。
    3. [Regex Detection]: 改良 op_latex 未定義警告，使用正則偵測 op_latex[...] 形式（通殺）。
    4. [Hybrid Healing]: 保留對小模型 (Qwen/14B) 的自動修復策略與警告機制。

版本資訊 (Version): V45.0 (op_latex Enhanced Edition)
更新日期 (Date): 2026-01-26
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
import math
import operator
from fractions import Fraction
import datetime as _pydt
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

# --- Path helpers (robust base root resolver) ---
def _get_base_root():
    """
    優先用 Flask current_app.root_path；若不可用，回退到 core/ 的上一層（專案根）
    """
    try:
        from flask import has_app_context
        if has_app_context():
            return current_app.root_path
    except Exception:
        pass
    # fallback: project root = parent of core/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def _path_in_root(*parts):
    return os.path.join(_get_base_root(), *parts)

def _ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p

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
import ast
import operator

# [Research Standard Utils]

def to_latex(num):
    """
    將數字轉換為 LaTeX 格式 (支援分數、整數、小數)
    [V46.2 Fix]: 強制限制分數的複雜度 (分母 <= 100)，避免出現百萬級大數。
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    
    if isinstance(num, Fraction):
        # [Critical Fix] 強制整形：如果分母太大，強制找最接近的簡單分數
        # 這能把 1060591/273522 自動變成合理的 K12 數字 (如 3 7/8)
        if num.denominator > 100:
            num = num.limit_denominator(100)

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
            # ✅ 修正: 整數部分不加大括號 (V46.5)
            return f"{sign_str}{whole}\\frac{{{rem_num}}}{{{abs_num.denominator}}}"
            
        # 真分數處理 (Proper Fraction)
        return f"{sign_str}\\frac{{{abs_num.numerator}}}{{{abs_num.denominator}}}"
        
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    格式化數字 (標準樣板要求)：
    - 自動括號：負數會自動被包在括號內 (-5) 或 (-\frac{1}{2})
    - signed=True: 強制顯示正負號 (+3, -5)
    """
    # 1. 取得基礎 LaTeX 字串
    latex_val = to_latex(num)
    
    # 2. 判斷是否為 0
    if num == 0 and not signed and not op: return "0"
    
    # 3. 判斷正負 (依賴數值本身)
    is_neg = (num < 0)
    
    # 為了處理 op=True 或 signed=True，我們需要絕對值的字串
    if is_neg:
        # 移除開頭的負號以取得絕對值內容
        # 注意: to_latex 可能回傳 "-{1}\frac..." 或 "-\frac..."
        if latex_val.startswith("-"):
            abs_latex_val = latex_val[1:] 
        else:
            abs_latex_val = latex_val # Should not happen but safe fallback
    else:
        abs_latex_val = latex_val

    # 4. 組裝回傳值
    if op: 
        return f" - {abs_latex_val}" if is_neg else f" + {abs_latex_val}"
    
    if signed: 
        return f"-{abs_latex_val}" if is_neg else f"+{abs_latex_val}"
    
    if is_neg: 
        return f"({latex_val})"
        
    return latex_val

# [AST Healer Inject] 安全運算核心
def safe_eval(expr_str):
    """
    [AST Healer 專用] 安全的數學表達式解析器
    [V46.4 Fix]: Python 3.12+ 兼容性修復，移除 ast.Num 依賴。
    """
    # 允許的運算子白名單
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv, 
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval(node):
        # [Python 3.12+ Fix] ast.Num 已被移除，使用 ast.Constant
        if isinstance(node, ast.Constant):
            return node.value
        # [Legacy] 保留 ast.Num 以支持舊版 Python (< 3.8)
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            # 關鍵：遇到除法，自動轉 Fraction
            if isinstance(node.op, ast.Div):
                return Fraction(left, right)
            return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'Fraction':
                args = [_eval(a) for a in node.args]
                return Fraction(*args)
        raise TypeError(f"Unsupported type: {node}")

    try:
        # 預處理：將 LaTeX 運算符轉回 Python
        clean_expr = str(expr_str).replace('\\times', '*').replace('\\div', '/')
        # 解析並計算
        result = _eval(ast.parse(clean_expr, mode='eval').body)
        
        # [Clamp] 強制整形：運算結果如果是複雜分數，直接化簡
        if isinstance(result, Fraction):
            if result.denominator > 100 or abs(result.numerator) > 10000:
                result = result.limit_denominator(100)
                
        return result
    except Exception as e:
        return 0

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

def clean_latex_output(q_str):
    """
    [V46.6 Fix] LaTeX 格式清洗器 (移除帶分數大括號邏輯)
    修復常見的 LaTeX 運算符錯誤與格式問題
    """
    if not isinstance(q_str, str): return str(q_str)
    clean_q = q_str.replace('$', '').strip()
    import re
    
    # 1. 修復運算符：* -> \times, / -> \div
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*\*\s*', r' \\times ', clean_q)
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*/\s*(?![{}])', r' \\div ', clean_q)
    
    # 2. 修復雙重括號 ((...)) -> (...)
    clean_q = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', clean_q)
    
    # 3. [REMOVED V46.6] 不再自動添加帶分數大括號
    # 原邏輯: clean_q = re.sub(r'(\d+)\s*(\\frac)', r'{\1}\2', clean_q)
    # 原因: to_latex() 已經正確處理格式，此步驟會誤傷
    
    # 4. 移除多餘空白
    clean_q = re.sub(r'\s+', ' ', clean_q).strip()
    
    return f"${clean_q}$"

def check(user_answer, correct_answer):
    """
    [V45.7 Smart Validator]
    """
    if not user_answer: return {"correct": False, "result": "未作答"}
    
    def parse_value(val_str):
        s = str(val_str).strip().replace(" ", "").replace("$", "").replace("\\", "")
        s = s.replace("times", "*").replace("div", "/")
        try:
            s = re.sub(r'frac\{(\d+)\}\{(\d+)\}', r'(\1/\2)', s)
            s = re.sub(r'(?<=\d)\(', r'*(', s)  # NEW [V47.3]: 將 "3(1/2)" 轉為 "3*(1/2)" 避免 eval 視為函式呼叫
            return float(eval(s))
        except:
            return None

    val_u = parse_value(user_answer)
    val_c = parse_value(correct_answer)

    if val_u is not None and val_c is not None:
        if math.isclose(val_u, val_c, rel_tol=1e-7):
            return {"correct": True, "result": "正確"}
    
    u_clean = str(user_answer).strip().replace(" ", "")
    c_clean = str(correct_answer).strip().replace(" ", "")
    if u_clean == c_clean:
        return {"correct": True, "result": "正確"}

    return {"correct": False, "result": f"正確答案: {correct_answer}"}

# [V47.4 跨領域工具組]

def clamp_fraction(fr, max_den=1000, max_num=100000):
    """防止分數爆炸：限制分子分母"""
    if not isinstance(fr, Fraction):
        fr = Fraction(fr)
    if abs(fr.numerator) > max_num or fr.denominator > max_den:
        fr = fr.limit_denominator(max_den)
    return fr

def safe_pow(base, exp, max_abs_exp=10):
    """安全指數運算，避免溢出"""
    if abs(exp) > max_abs_exp:
        return Fraction(0)  # 或其他安全默認
    try:
        if isinstance(base, Fraction) and exp >= 0:
            return Fraction(base.numerator ** exp, base.denominator ** exp)
        elif isinstance(base, Fraction) and exp < 0:
            return Fraction(base.denominator ** (-exp), base.numerator ** (-exp))
        else:
            return Fraction(int(base ** exp), 1)
    except:
        return Fraction(0)

def factorial_bounded(n, max_n=1000):
    """有界階乘"""
    if not (0 <= n <= max_n):
        return None
    result = 1
    for i in range(2, int(n) + 1):
        result *= i
    return result

def nCr(n, r, max_n=5000):
    """組合數 C(n,r)"""
    n, r = int(n), int(r)
    if not (0 <= r <= n <= max_n):
        return None
    if r > n - r:
        r = n - r
    result = 1
    for i in range(r):
        result = result * (n - i) // (i + 1)
    return result

def nPr(n, r, max_n=5000):
    """排列數 P(n,r)"""
    n, r = int(n), int(r)
    if not (0 <= r <= n <= max_n):
        return None
    result = 1
    for i in range(n, n - r, -1):
        result *= i
    return result

def rational_gauss_solve(a, b, p, c, d, q):
    """2x2 線性系統求解器 (用 Fraction)
    a*x + b*y = p
    c*x + d*y = q
    返回 {'x': Fraction, 'y': Fraction} 或 None
    """
    a, b, p, c, d, q = [Fraction(x) for x in [a, b, p, c, d, q]]
    det = a * d - b * c
    if det == 0:
        return None  # 無解或無窮解
    x = (p * d - b * q) / det
    y = (a * q - p * c) / det
    return {'x': x, 'y': y}

def normalize_angle(theta, unit='deg'):
    """角度正規化到 [0, 360) 或 [0, 2π)"""
    theta = float(theta)
    if unit == 'deg':
        theta = theta % 360
        if theta < 0:
            theta += 360
        return theta
    else:  # rad
        theta = theta % (2 * math.pi)
        if theta < 0:
            theta += 2 * math.pi
        return theta

def fmt_set(iterable, braces='{}'):
    """集合顯示：元素使用 fmt_num（不含外層 $）"""
    items = [fmt_num(x) for x in iterable]
    inner = ", ".join(items)
    return ("\\{" + inner + "\\}") if braces == '\\{\\}' else ("{" + inner + "}")

def fmt_interval(a, b, left_open=False, right_open=False):
    """區間顯示：(a,b)、[a,b)、(a,b]、[a,b]；端點使用 fmt_num"""
    l = "(" if left_open else "["
    r = ")" if right_open else "]"
    return f"{l}{fmt_num(a)}, {fmt_num(b)}{r}"

def fmt_vec(*coords):
    """向量顯示：分量使用 fmt_num（不含外層 $）"""
    inner = ", ".join(fmt_num(x) for x in coords)
    return "\\langle " + inner + " \\rangle"

# ✅ 預設的 LaTeX 運算子映射（四則）- 全域可用
op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
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
你是資深 K12 數學演算法工程師。你只負責「產出可直接執行的 Python 代碼」：
定義一個 `generate(level=1, **kwargs)` 函式，遵循統一的「跨領域生成管線」。
無論題型是四則運算、方程式、幾何、三角、機率統計或排列組合，都走相同流程。
不得輸出任何文字敘述或 Markdown，僅輸出 Python 代碼。

【已預載工具（直接使用，禁止重新定義/重新 import）】
- 基礎模組：`random`, `math`, `re`, `ast`, `operator`, `Fraction` (from fractions)
- 格式化工具：`fmt_num(num, signed=False, op=False)`, `to_latex(num)`, `clean_latex_output(q_str)`
- 驗證工具：`check(user_answer, correct_answer)`
- 數論工具：`gcd`, `lcm`, `is_prime`, `get_factors`
- **運算子映射**：`op_latex` = `{'+': '+', '-': '-', '*': '\\times', '/': '\\div'}` 
  - ✅ 直接使用: `f"{fmt_num(n1)} {op_latex[op]} {fmt_num(n2)}"`
  - ❌ **嚴禁重新定義**: 不要在 generate() 內部再寫 `op_latex = {...}`
- 新增跨領域工具 (V47.4+)：
  - `clamp_fraction(fr, max_den=1000, max_num=100000)` - 防止分數爆炸
  - `safe_pow(base, exp, max_abs_exp=10)` - 安全指數
  - `factorial_bounded(n, max_n=1000)` - 有界階乘
  - `nCr(n, r, max_n=5000)`, `nPr(n, r, max_n=5000)` - 組合與排列
  - `rational_gauss_solve(a,b,p,c,d,q)` - 2×2 線性系統求解器
  - `normalize_angle(theta, unit='deg')` - 角度正規化
  - `fmt_set(iterable, braces='{}')` - 集合顯示
  - `fmt_interval(a, b, left_open, right_open)` - 區間顯示
  - `fmt_vec(*coords)` - 向量顯示

【通用生成管線 (V47.4 - 8 步驟)】

1) **模板與變異選擇**：
   依 MASTER_SPEC 中的 templates 列表，隨機選一個模板與其變異點。
   (例：chain_of_operations vs distributive_property)

2) **變數生成與邊界檢查**：
   按模板的 variables 規則，生成每個變數 (int/Fraction)。
   - **零值保護**：任何分母或除數都不得為 0；用 while 重抽或從候選集篩選。
   - **互斥檢查**：若規則列出互斥關係 (mutually_exclusive_with)，確保不同時出現。
   - **有界檢查**：數值範圍合理 (K12 級，分數分母預設 ≤ 20，避免計算過於繁瑣)。

3) **運算與計算**：
   按 construction 敘述的「自然語序」，依次計算中間值與最終答案。
   - **嚴禁 eval/exec/safe_eval**：所有數學結果必須用 Python 直接計算 (`+`, `-`, `*`, `Fraction`)。
   - **防浮點誤差**：生成小數時用 `Fraction(str(value))`；涉及除法務必用 Fraction。
   - **選擇適當工具**：若題型涉及階乘、組合、指數等，使用 factorial_bounded、nCr、safe_pow 等。

4) **題幹組合 (Question String)**：
   用 `fmt_num(...)` 與 `fmt_interval()`, `fmt_set()`, `fmt_vec()` 等領域工具組合題幹字串 `q`。
   - 乘除使用全域已定義的 `op_latex` 映射（❌ 不要在 generate() 內重新定義）。
   - **嚴禁用 to_latex() 組題幹**：改用 fmt_num()（能自動為負數加括號）。
   - **f-string 嚴格規則**：
     ✅ `f"{fmt_num(n1)} {op_latex[op]} {fmt_num(n2)}"` (單層 `{}` + `f` 前綴)
     ❌ `f"{{op_latex[op]}}"` (雙括號會字面量出現)
     ❌ `"{fmt_num(n)}"` (無 `f` 前綴無法插值)

5) **LaTeX 清洗 (Question Output)**：
   - 先用 fmt_num / fmt_interval / fmt_set / fmt_vec 組好題幹字串 `q`（不含 `$`）。
   - 緊接著：`q = clean_latex_output(q)` （**只呼叫一次**；自動加外層 `$...$`）。
   - **禁止多重包裹**：`fmt_num(clean_latex_output)(X)` 是錯誤的。

6) **答案組合 (Answer Output)**：
   `a = fmt_num(result)` 或其他領域工具（不含 `$`）。
   答案格式依題型決定：分數、度數、集合、區間等。

7) **清洗段 (Standardization)**：
   固定變數名 `q` 與 `a`，移除 `q` 中的冗餘前綴（如「計算下列」、題號等）。
   ```python
   if isinstance(q, str):
       q = re.sub(r'^計算下列.*[：:]?', '', q).strip()
       q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
   if isinstance(a, str):
       if "=" in a:
           a = a.split("=")[-1].strip()
   ```

8) **回傳結構 (固定鍵名，不可增刪)**：
   ```python
   return {
       'question_text': q,            # q 已是 clean_latex_output 後的 "$...$" 完成品
       'correct_answer': a,           # a 是 fmt_num(...) 結果，不含 "$"
       'answer': a,                   # 與 correct_answer 同
       'mode': 1
   }
   ```

【一次過防呆總則 (必讀必遵守)】

- **只寫 def generate(level=1, **kwargs)：** 可在內部定義 _ 開頭的輔助函式，但嚴禁重新定義 fmt_num, to_latex, clean_latex_output, check, 及新工具。
- **嚴禁 import 任何模組：** 已預載所有依賴。
- **嚴禁 eval/exec/字串算式：** 所有運算用 Python 直接計算。
- **嚴禁浮點數直接運算：** 涉及除法務必轉 Fraction。
- **嚴禁自創工具函數：** 不要發明不存在的函數！常見錯誤：
  ❌ `random_fraction(...)` - 應直接用 `Fraction(random.randint(...), random.randint(...))`
  ❌ `random_mixed_number(...)` - 應自己用 Fraction 計算帶分數
  ❌ `fmt_neg_paren(...)` - 應直接用 `fmt_num(...)` (已自動為負數加括號)
  ❌ `fmt_num(..., type='...')` - fmt_num 只有 signed 和 op 參數
- **變數名固定：** 題幹用 `q`，答案用 `a`；勿自創 `q_latex`, `answer_str` 等。
- **列表收集：** 循環生成變數時，務必 `append` 到列表（如 `terms.append(term)`），避免空列表導致 IndexError。
- **LaTeX 規則：** 題幹內用 fmt_num (或 fmt_interval 等)，最後才 clean_latex_output；答案用 fmt_num (無外層 `$`)。
- **f-string 單層括號：** `f"{fmt_num(...)}"` 而非 `f"{{...}}"`。

【輸出限制】
只輸出 Python 代碼；不含任何說明、Markdown、註解。
不可出現 print、測試碼、Jupyter cell。return 後無任何代碼。

【參考片段 (僅風格示意，勿逐字抄)】
```python
def generate(level=1, **kwargs):
    # [Step 1] 模板選擇
    template = random.choice(['chain_of_operations', 'distributive_property'])
    
    # [Step 2] 變數生成
    def _rand_num():
        # 隨機生成 int / Fraction...
        pass
    
    n1 = _rand_num()
    while n1 == 0: n1 = _rand_num()
    
    # [Step 3] 運算
    result = n1 + n2  # 直接計算，Fraction 會自動化簡
    
    # [Step 4] 題幹
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    q = f"{fmt_num(n1)} {op_latex['+']} {fmt_num(n2)}"
    
    # [Step 5] 清洗
    q = clean_latex_output(q)
    
    # [Step 6] 答案
    a = fmt_num(result)
    
    # [Step 7] 清洗變數名
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    # [Step 8] 回傳
    return {
        'question_text': q,
        'correct_answer': a,
        'answer': a,
        'mode': 1
    }
```

【最終任務】
依上述「通用生成管線」與「防呆總則」，產出唯一的 `def generate(level=1, **kwargs):` 實作。
遵守 8 步驟、預載工具、禁 eval、格式化規則。
不得有任何多餘內容。
"""

# ==============================================================================
# 4. 修復與驗證工具
# ==============================================================================

class ASTHealer(ast.NodeTransformer):
    """
    [V45.0 AST Logic Surgeon]
    深入語法樹層級，修復 Regex 無法觸及的邏輯錯誤。
    """
    def __init__(self):
        self.fixes = 0

    def visit_BinOp(self, node):
        self.generic_visit(node)
        # 1. 修復次方符號：將 XOR (^) 轉為 Pow (**)
        if isinstance(node.op, ast.BitXor):
            self.fixes += 1
            node.op = ast.Pow()
            return node
        # [V47.4 REMOVED] 不再攔截 ast.Div：
        # Python Fraction 物件本來就支援 / 運算回傳 Fraction
        # 攔截會導致 Fraction(Fraction(...), Fraction(...)) TypeError
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        
        # 1. 攔截 eval/exec/safe_eval (轉接或標準化為 safe_eval)
        # 或者直接攔截 safe_eval (如果 AI 已經學會用 safe_eval 但用錯了參數)
        target_funcs = ['eval', 'exec', 'safe_eval']
        
        if isinstance(node.func, ast.Name) and node.func.id in target_funcs:
            self.fixes += 1
            node.func.id = 'safe_eval'
            
            # [V46.0 Fix] 強制清洗 safe_eval 的參數
            # 我們的 safe_eval 只接受一個參數 (expr_str)
            # 如果 AI 傳了 globals/locals 字典 (例如 eval(s, {...}))，全部丟掉
            if len(node.args) > 1:
                print(f"🧹 [AST Healer] 清除 safe_eval 的多餘參數 (只保留運算式)")
                node.args = [node.args[0]] # 只保留第一個
                
            return node
        
        # 2. 處理 fmt_num
        if isinstance(node.func, ast.Name) and node.func.id == 'fmt_num':
            # [Fix A] 移除幻想參數
            if node.keywords:
                original_len = len(node.keywords)
                node.keywords = [k for k in node.keywords if k.arg in ['signed', 'op']]
                if len(node.keywords) != original_len:
                    self.fixes += 1
            # [Fix B] 補救空參數
            if not node.args:
                self.fixes += 1
                node.args = [
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='random', ctx=ast.Load()),
                            attr='randint',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=10)),
                            ast.Constant(value=10)
                        ],
                        keywords=[]
                    )
                ]
            return node
        
        # 3. [V47.0] 格式化函式重定向（加白名單保護系統工具）
        if isinstance(node.func, ast.Name):
            # 白名單：保護系統合法工具，不要動手腳
            protected = {
                'fmt_num', 'to_latex', 'clean_latex_output', 'check', 'safe_eval',
                'gcd', 'lcm', 'is_prime', 'get_factors',
                'clamp_fraction', 'safe_pow', 'factorial_bounded', 'nCr', 'nPr',
                'rational_gauss_solve', 'normalize_angle',
                'fmt_set', 'fmt_interval', 'fmt_vec'
            }
            
            # 只對非白名單且可疑名稱的函數進行重定向
            if node.func.id not in protected and re.search(r'(format|latex|display)', node.func.id, re.IGNORECASE):
                self.fixes += 1
                node.func.id = 'fmt_num'
                node.keywords = [k for k in node.keywords if k.arg in ['signed', 'op']]
                return node
        return node
    
    def visit_Import(self, node):
        self.fixes += 1
        return None
    
    def visit_ImportFrom(self, node):
        self.fixes += 1
        return None
    
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if re.search(r'(Format|LaTeX|Display)', node.name, re.IGNORECASE) and node.name != 'generate':
            self.fixes += 1
            return None 
        return node
    
    def visit_While(self, node):
        """
        [Circuit Breaker]
        將潛在的無窮迴圈 while True 轉換為有限的 for _ in range(1000)
        [V45.9 Fix]: 增加次數至 1000，避免隨機生成演算法過早失敗導致變數未定義。
        """
        self.generic_visit(node)
        
        is_infinite = False
        
        # 檢查是否為 while True
        # 1. 現代 Python (3.8+)
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            is_infinite = True
        # 2. 舊版 Python (<3.8) - 必須檢查 hasattr 避免 3.12+ 崩潰
        elif hasattr(ast, 'NameConstant') and isinstance(node.test, ast.NameConstant) and node.test.value is True:
            is_infinite = True
            
        if is_infinite:
            self.fixes += 1
            print(f"🛑 [AST Healer] 熔斷機制啟動: while True -> for loop (1000 runs)")
            
            # 轉換為 for _ in range(1000):
            return ast.For(
                target=ast.Name(id='_safety_loop_var', ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Name(id='range', ctx=ast.Load()),
                    args=[ast.Constant(value=1000)], # [Fix] 給予更多嘗試機會
                    keywords=[]
                ),
                body=node.body,
                orelse=node.orelse,
                type_comment=None
            )
            
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple):
            target_tuple = node.targets[0]
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'fmt_num':
                self.fixes += 1
                val_var = target_tuple.elts[0]
                latex_var = target_tuple.elts[1]
                if node.value.args:
                    num_source = node.value.args[0]
                else:
                    num_source = ast.Call(
                        func=ast.Attribute(value=ast.Name(id='random', ctx=ast.Load()), attr='randint', ctx=ast.Load()),
                        args=[ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=10)), ast.Constant(value=10)],
                        keywords=[]
                    )
                assign_val = ast.Assign(targets=[val_var], value=num_source)
                assign_latex = ast.Assign(
                    targets=[latex_var],
                    value=ast.Call(
                        func=ast.Name(id='fmt_num', ctx=ast.Load()),
                        args=[val_var],
                        keywords=node.value.keywords
                    )
                )
                return [assign_val, assign_latex]
        
        return node

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

    # [V47.4 REMOVED] 不再轉換 / → //：
    # 分數四則運算需要有理數除法，不能變成整數除法
    # Fraction(a) / Fraction(b) 正確回傳 Fraction 結果

    # [DISABLED V46.6] 帶分數格式修復已移除
    # 原因: to_latex() 本身不會生成 {整數}\frac 格式
    # 只有舊版 clean_latex_output() 的 regex 會誤加，已在源頭移除
    # 保留此註釋以追蹤修復歷史
    # 
    # refined_code, n4 = re.subn(
    #     r'\{(\d+)\}(\\frac)',
    #     r'\1\2',
    #     refined_code
    # )
    # fixes += n4

    return refined_code, fixes

def fix_code_syntax(code_str, error_msg=""):
    """
    [V45.6 Syntax Emergency Room + Orthopedic Surgeon]
    1. Regex 修復語法錯誤 (Latex, Break, Op-var)。
    2. [NEW] Auto-Indenter: 自動矯正 IndentationError。
    """
    # --- Part 1: Regex Healers ---
    fixed_code = code_str.replace("，", ", ").replace("：", ": ")
    fixed_code = re.sub(r'###.*?\n', '', fixed_code) 
    
    total_fixes = 0
    def apply_fix(pattern, replacement, code):
        new_code, count = re.subn(pattern, replacement, code, flags=re.MULTILINE)
        return new_code, count

    # 1. Latex Fixes
    fixed_code, c = apply_fix(r'(?<!\\)\\ ', r'\\\\ ', fixed_code); total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code); total_fixes += c

    # 2. Tuple Unpacking Fix (Missing Comma)
    # [V45.3 Fix] 排除 Python 關鍵字，避免誤將 `continue\nvar =` 轉成 `continue, var =`
    # 原 pattern 會把跨行的 continue/expression = 誤判為 tuple unpacking
    unpacking_pattern = r'^(\s*(?!break|continue|return|pass|raise|yield)[a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\s*=(?!=)'
    fixed_code, c = re.subn(unpacking_pattern, r'\1, \2 =', fixed_code, flags=re.MULTILINE)
    total_fixes += c

    # 3. [Fix] "break, var = val" Hallucination
    # 改良策略：不嘗試猜縮排，直接用 ; 接在同一行 (Python 允許)
    # var = val; break
    # [V45.1 Fix] 使用 [ \t]* 取代 \s*，確保 pattern 必須在同一行匹配（\s 會跨越換行符）
    break_pattern = r'^[ \t]*break[ \t]*,[ \t]*([a-zA-Z_]\w*)[ \t]*=[ \t]*(.+)$'
    fixed_code, c = re.subn(break_pattern, r'\1 = \2; break', fixed_code, flags=re.MULTILINE)
    if c > 0: print(f"🚑 [Syntax Healer] 修復了 {c} 處 break 賦值幻覺 (使用分號策略)")
    total_fixes += c

    # 4. [Fix] "Variable as Operator" (a op b)
    op_vars = r'(?:op\d+|current_op|Op_\w+)'
    
    # Pattern A: 括號內的運算
    pattern_inner = rf'\(([\w\.]+)\s+({op_vars})\s+([\w\.]+)\)'
    for _ in range(3): 
        fixed_code, c = re.subn(pattern_inner, r'safe_eval(f"{ \1 } { \2 } { \3 }")', fixed_code)
        total_fixes += c

    # Pattern B: 賦值語句
    pattern_assign = rf'=\s*(.+?)\s+({op_vars})\s+([\w\.]+)\s*$'
    def assign_replacer(match):
        left = match.group(1)
        op = match.group(2)
        right = match.group(3)
        return f'= safe_eval(f"""{{ {left} }} {{ {op} }} {{ {right} }}""")'

    fixed_code, c = re.subn(pattern_assign, assign_replacer, fixed_code, flags=re.MULTILINE)
    if c > 0: print(f"🚑 [Syntax Healer] 修復了 {c} 處運算符變數語法")
    total_fixes += c
    
    # 5. f-string braces
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

    # --- Part 2: Auto-Indenter (The Orthopedic Surgeon) ---
    # 這是專門用來修復 IndentationError 的邏輯
    lines = fixed_code.split('\n')
    indented_lines = []
    prev_line_ends_colon = False
    prev_indent = 0
    
    for line in lines:
        stripped = line.strip()
        # 忽略空行
        if not stripped:
            indented_lines.append(line)
            continue
            
        current_indent = len(line) - len(line.lstrip())
        
        # 如果上一行是冒號結尾 (if/for/while/def)，這一行必須縮排
        if prev_line_ends_colon:
            if current_indent <= prev_indent:
                # 偵測到縮排錯誤！強制縮排
                new_indent = prev_indent + 4 # 補 4 個空白
                fixed_line = " " * new_indent + line.lstrip()
                indented_lines.append(fixed_line)
                
                # 更新狀態 (假設修好了，這行就不是冒號結尾了，除非它自己也是)
                # 但要注意這行可能也是冒號結尾 (巢狀結構)
                # 這裡簡單處理：既然我們強制縮排了，我們信任這個新縮排
                prev_indent = new_indent 
            else:
                indented_lines.append(line)
                prev_indent = current_indent
        else:
            indented_lines.append(line)
            prev_indent = current_indent
            
        # 檢查這一行是否以冒號結尾 (忽略註解)
        # 用 split('#')[0] 去掉註解
        code_part = stripped.split('#')[0].rstrip()
        if code_part.endswith(':'):
            prev_line_ends_colon = True
        else:
            prev_line_ends_colon = False
            
    fixed_code = '\n'.join(indented_lines)

    return fixed_code, total_fixes

def fix_code_via_ast(code_str):
    """
    使用 AST Transformer 進行邏輯手術
    """
    try:
        tree = ast.parse(code_str)
        healer = ASTHealer()
        new_tree = healer.visit(tree)
        ast.fix_missing_locations(new_tree)  # 修正行號
        
        # 轉回程式碼
        new_code = ast.unparse(new_tree)
        return new_code, healer.fixes
    except Exception as e:
        # 如果 AST 解析本身就失敗（代表語法爛到無法解析），則放棄治療，交給原流程
        print(f"AST Healing Failed: {e}")
        return code_str, 0

def validate_python_code(code_str):
    try:
        # [V46.1 Fix] 修正 Host 端 NameError
        # 我們不需要手動傳入 safe_eval，因為 code_str (生成的代碼)
        # 裡面已經透過 PERFECT_UTILS 注入了 safe_eval 的定義。
        # exec 執行時會自然地先定義函式，再執行後面的邏輯。
        
        exec(code_str, {
            'Fraction': Fraction, 
            'random': random, 
            'math': math, 
            're': re,
            'ast': ast,
            'operator': operator
        })
        return True, "Success"
    except Exception as e:
        # [Debug] 詳細錯誤輸出
        error_msg = f"{type(e).__name__}: {str(e)}"
        
        # 過濾掉一些非代碼邏輯的干擾訊息
        if "break outside loop" in error_msg:
             return False, error_msg

        print(f"❌ [Validation Failed] 執行時錯誤: {error_msg}")
        
        if "local variable" in error_msg and "referenced before assignment" in error_msg:
            print(f"   💡 提示: 這可能是因為 while True 熔斷後，迴圈內變數未初始化導致。")
        elif "safe_eval" in error_msg:
             print(f"   💡 提示: 請檢查生成的代碼開頭是否包含 PERFECT_UTILS 定義。")
             
        return False, error_msg

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

        # ========================================
        # Step E.5: [FIXED V46.8] 工具函式重定義偵測器
        # ========================================
        shadowing_fixes = 0
        PROTECTED_TOOLS = [
            'fmt_num', 'to_latex', 'is_prime', 'gcd', 'lcm', 'get_factors', 'check',
            'clamp_fraction', 'safe_pow', 'factorial_bounded', 'nCr', 'nPr',
            'rational_gauss_solve', 'normalize_angle',
            'fmt_set', 'fmt_interval', 'fmt_vec'
        ]

        if 'def generate' in clean_code:
            gen_start = clean_code.find('def generate')
            gen_content = clean_code[gen_start:]
            
            for tool_name in PROTECTED_TOOLS:
                # ✅ 修正 V46.8: 必須匹配「行首 + def + 函式名 + (」
                # 避免誤判 to_latex(value) 這種調用
                pattern = rf'^\s*def\s+{tool_name}\s*\('
                if re.search(pattern, gen_content, re.MULTILINE):
                    print(f"🔴 [{skill_id}] CRITICAL: 重新定義了 {tool_name}")
                    
                    lines = gen_content.split('\n')
                    cleaned_gen_lines = []
                    skip_mode = False
                    target_indent = -1
                    
                    for line in lines:
                        # ✅ 同樣修正：嚴格匹配定義行
                        if re.match(rf'^\s*def\s+{tool_name}\s*\(', line):
                            skip_mode = True
                            target_indent = len(line) - len(line.lstrip())
                            shadowing_fixes += 1
                            continue
                        
                        if skip_mode:
                            current_indent = len(line) - len(line.lstrip())
                            if not line.strip() or line.strip().startswith('#'):
                                continue
                            if current_indent <= target_indent and line.strip():
                                skip_mode = False
                            else:
                                continue
                        
                        cleaned_gen_lines.append(line)
                    
                    gen_content = '\n'.join(cleaned_gen_lines)
            
            clean_code = clean_code[:gen_start] + gen_content

        regex_fixes += shadowing_fixes

        # ========================================
        # Step E.6: [NEW] 混合數字串修復
        # ========================================
        mixed_num_fixes = 0

        # Pattern 1: 偵測並修復 f"{A}{fmt_num(frac)}" 模式
        pattern1 = r'return\s+f"(\{[^}]+\})\{fmt_num\(([^)]+)\)\}"'
        if re.search(pattern1, clean_code):
            print(f"🔴 [{skill_id}] CRITICAL: 偵測到混合數字串拼接")
            # 修復：改為回傳 Fraction 相加
            clean_code = re.sub(
                pattern1,
                r'return Fraction(\1) + \2',
                clean_code
            )
            mixed_num_fixes += 1

        # Pattern 2: 偵測 eval(字串) 用於混合數
        if re.search(r'elif isinstance\([^,]+, str\):\s+return eval\(', clean_code):
            print(f"⚠️ [{skill_id}] 偵測到 eval(字串)，可能導致混合數錯誤")

        # Pattern 3: 修復 _generate_mixed_number 的實作
        mixed_num_pattern = r'(def _generate_mixed_number\(\):.*?)(return f".*?fmt_num.*?")'
        if re.search(mixed_num_pattern, clean_code, re.DOTALL):
            print(f"🔧 [{skill_id}] 修復 _generate_mixed_number")
            clean_code = re.sub(
                r'(def _generate_mixed_number\(\):.*?frac = [^\n]+\n\s+)return f".*?fmt_num.*?"',
                r'\1return Fraction(A) + frac',
                clean_code,
                flags=re.DOTALL
            )
            mixed_num_fixes += 1

        regex_fixes += mixed_num_fixes

        # ========================================
        # Step E.7: LaTeX 格式修復（混合數專用）
        # ========================================
        latex_fixes = 0

        # 修復 1：過多的大括號 {{{{num}}}}
        clean_code, n = re.subn(r'\{{4,}([^}]+)\}{4,}', r'{\1}', clean_code)
        latex_fixes += n

        # 修復 2：TO_LATEX 內部包含 $ 符號
        if 'return f"$' in clean_code and 'def TO_LATEX' in clean_code:
            print(f"⚠️ [{skill_id}] TO_LATEX 內部不應包含 $ 符號")
            clean_code = re.sub(r'return f"\$([^"]+)\$"', r'return f"\1"', clean_code)
            latex_fixes += 1

        # 修復 3：整數除法應改為普通除法
        clean_code, n = re.subn(
            r'(\w+)\s*=\s*(\w+)\s*//\s*(\w+)(?=.*# Division)',
            r'\1 = \2 / \3',
            clean_code
        )
        latex_fixes += n

        # [V47.4 REMOVED] 修復 4：移除自動注入 $ 的規則：
        # 正確做法是 q = clean_latex_output(q)（會自動包 $...$）
        # 此規則會造成雙重 $，與正確流程打架

        regex_fixes += latex_fixes

        # ========================================
        # Step E.9: [V47.0] Return 語句修正
        # ========================================
        return_fixes = 0

        # Fix 1: 修正 fmt_num(字串變數) 的錯誤用法
        if "'question_text': fmt_num(" in clean_code:
            pattern = r"'question_text':\s*fmt_num\(([a-zA-Z_]\w*)\)"
            matches = list(re.finditer(pattern, clean_code))
            
            for match in reversed(matches):
                var_name = match.group(1)
                # 判斷是否為字串變數
                if any(kw in var_name.lower() for kw in ['latex', 'question', 'q', 'text', 'str']):
                    new_str = f"'question_text': clean_latex_output({var_name})"
                    clean_code = clean_code[:match.start()] + new_str + clean_code[match.end():]
                    return_fixes += 1
                    print(f"🔧 [{skill_id}] 修正: fmt_num({var_name}) → clean_latex_output({var_name})")

        regex_fixes += return_fixes

        # ========================================
        # Step E.8: [NEW] 變數名稱對齊與雙重 $ 修復
        # ========================================
        var_fixes = 0
        
        # Fix 1: 如果 AI 用了 'a' 但實際變數叫 'answer'
        # 檢查：有 'answer =' 但沒有 'a =' 定義
        has_answer_def = re.search(r'\banswer\s*=', clean_code)
        has_a_def = re.search(r'\ba\s*=\s*(?!answer)', clean_code)  # a = 但不是 a = answer
        has_a_usage = 'isinstance(a, str)' in clean_code or "'a'" in clean_code
        
        if has_answer_def and not has_a_def and has_a_usage:
            # 替換所有 'a' 引用為 'answer'
            clean_code = clean_code.replace('isinstance(a, str)', 'isinstance(answer, str)')
            clean_code = re.sub(r"'='\s+in\s+a\b", "'=' in answer", clean_code)
            clean_code = re.sub(r'"="\s+in\s+a\b', '"=" in answer', clean_code)
            clean_code = re.sub(r'\ba\.split\(', 'answer.split(', clean_code)
            # 同時處理 return 中的 'answer': a
            clean_code = re.sub(r"'answer':\s*a\b", "'answer': answer", clean_code)
            clean_code = re.sub(r"'correct_answer':\s*a\b", "'correct_answer': answer", clean_code)
            var_fixes += 1
            print(f"🔧 [{skill_id}] 修復變數名稱: a -> answer")
        
        # Fix 2: 防止 return 中雙重 $ 包裹 (終極版 V46.8)
        # 當 clean_latex_output() 已經處理過 q，return 中不需要再包 $
        if "clean_latex_output" in clean_code:
            old_len = len(clean_code)
            
            # Pattern 1: 直接在 return 中用 f'${q}$' 的各種形式
            clean_code = re.sub(
                r"'question_text':\s*f?['\"]?\$\{q\}\$['\"]?",
                r"'question_text': q",
                clean_code
            )
            
            # Pattern 2: 在 clean_latex_output 之前就加了 $ 的情況
            clean_code = re.sub(
                r'q\s*=\s*f?["\']?\$\{[^}]+\}\$["\']?\s*\n\s*q\s*=\s*clean_latex_output\(q\)',
                r'q = clean_latex_output(q)',
                clean_code
            )
            
            # Pattern 3: 已經有 clean_latex_output 但 return 仍包 $
            clean_code = re.sub(
                r"'question_text':\s*f\['\"]\$\{q\}\$['\"]\b",
                r"'question_text': q",
                clean_code
            )
            
            # Pattern 4: [V46.8 NEW] 通用 f-string 形式 f'${q}$' → q
            clean_code = re.sub(
                r"f['\"]?\$\{q\}\$['\"]?",
                r"q",
                clean_code
            )
            
            if len(clean_code) != old_len:
                var_fixes += 1
                print(f"🔧 [{skill_id}] 移除雙重 $ 包裹 (終極版)")
        
        regex_fixes += var_fixes

        # ========================================
        # Step E.9: [V47.4 優化] Return 語句自動 LaTeX 清洗（僅對 q）
        # ========================================
        # 問題修復：廣義 regex 容易誤包其他變數（如 f, q_latex 等）
        # 解決方案：改為只處理 q，且加前置檢查是否已清洗過
        return_fixes = 0
        
        if "'question_text':" in clean_code:
            # 檢查前面是否已經有 q = clean_latex_output(q)
            already_clean_q = re.search(r'\bq\s*=\s*clean_latex_output\s*\(\s*q\s*\)', clean_code)
            
            # 僅對 'q' 自動包裝；若前面已清洗過則維持 'q'
            if already_clean_q:
                # 已清洗過，不需要再包裝
                pass
            else:
                # 未清洗，在 return 時包裝
                old_pattern = r"'question_text':\s*q\b"
                new_str = "'question_text': clean_latex_output(q)"
                clean_code, n = re.subn(old_pattern, new_str, clean_code)
                return_fixes = n
                if return_fixes > 0:
                    print(f"🔧 [{skill_id}] 在 return 中包裹 clean_latex_output(q) ({return_fixes} 處)")
        
        
        regex_fixes += return_fixes

        # ========================================
        # Step F.5: [NEW V46.8] Pre-AST 語法清洗
        # ========================================
        pre_ast_fixes = 0

        # Fix 1: 修復 eval(calc_string) → safe_eval(calc_string)
        clean_code, n = re.subn(
            r'\beval\s*\(',
            r'safe_eval(',
            clean_code
        )
        pre_ast_fixes += n
        if n > 0:
            print(f"🔧 [{skill_id}] 轉換 eval() → safe_eval() ({n} 處)")

        # Fix 2: 修復可能的語法錯誤（多餘的括號、引號）
        # 檢查是否有未閉合的字串
        open_quotes = clean_code.count('"') % 2
        if open_quotes != 0:
            print(f"⚠️ [{skill_id}] 偵測到未閉合的引號")
            # 嘗試自動閉合（在最後一個 return 之前）
            lines = clean_code.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                if 'return' in lines[i]:
                    if not lines[i].rstrip().endswith('"'):
                        lines[i] = lines[i].rstrip() + '"'
                        pre_ast_fixes += 1
                    break
            clean_code = '\n'.join(lines)

        regex_fixes += pre_ast_fixes

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

        # [V47.4 REMOVED] D. 修復整數除法已移除：
        # 分數四則運算需要有理數除法 (/)，不能變成整數除法 (//)
        # Fraction(a) / Fraction(b) 正確回傳 Fraction 結果

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
        
        # [方案 B] 偵測 op_latex[...] 用法但無定義，自動注入
        needs_op_map = re.search(r'\bop_latex\s*\[', clean_code) and 'op_latex =' not in clean_code
        if needs_op_map:
            clean_code = re.sub(
                r'(def\s+generate\s*\([^)]*\):\n)',
                r"\1    op_latex = {'+': '+', '-': '-', '*': '\\\\times', '/': '\\\\div'}\n",
                clean_code,
                count=1
            )
            qwen_fixes += 1
            print(f"🔧 [{skill_id}] 自動注入 op_latex 映射表")
        
        # [V45.2 Fix] 移除函數內部的重複 op_latex 定義
        # 問題：AI 有時會在 if/for 內部定義 op_latex，這會遮蔽全域定義
        # 導致其他分支引用時出現 UnboundLocalError
        # 解決：因為全域 PERFECT_UTILS 已有 op_latex，直接刪除內部定義
        local_op_latex_pattern = r'^([ \t]+)op_latex\s*=\s*\{[^}]+\}\s*\n'
        local_op_matches = list(re.finditer(local_op_latex_pattern, clean_code, re.MULTILINE))
        if local_op_matches:
            # 只刪除縮排 >= 8 空格的定義（在循環或條件內部）
            for match in reversed(local_op_matches):
                indent = len(match.group(1))
                if indent >= 8:  # 在條件/循環內部（def generate 內的 if/for）
                    clean_code = clean_code[:match.start()] + clean_code[match.end():]
                    qwen_fixes += 1
                    print(f"🔧 [{skill_id}] 移除內部重複 op_latex 定義 (縮排 {indent})")
        
        # [改良版] 使用正則偵測 op_latex 未定義 (適用 op_latex[...] 形式)
        if re.search(r'\bop_latex\s*\[', clean_code) and 'op_latex =' not in clean_code:
            warnings.append("op_latex 未定義")
        # 檢查早前偵測到的 f-string 反斜線插入問題，並轉入 warnings
        try:
            if fstring_problem_detected:
                warnings.append('偵測到 f-string 直接插入反斜線運算符 (如 f"\\{op}")，請改用 op_latex 或 "\\times"/"\\div" 方法')
        except NameError:
            pass

        if warnings:
            print(f"⚠️ [{skill_id}] 偵測到問題: {', '.join(warnings)}")

        # ========================================
        # F-Zero. [V45.4 Fix] 幻覺函數修復 (Hallucination Healer)
        # ========================================
        
        # 1. fmt_neg_paren -> fmt_num
        clean_code, n = re.subn(r'\bfmt_neg_paren\s*\(', 'fmt_num(', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 幻覺修復: fmt_neg_paren -> fmt_num ({n} 處)")

        # 2. fmt_num(..., type='...') -> fmt_num(...) 移除 type 參數
        # 簡單處理: 移除 , type='...' 或 , type="..."
        clean_code, n = re.subn(r',\s*type\s*=\s*[\'"][^\'"]*[\'"]', '', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 幻覺修復: 移除 fmt_num 的 type 參數 ({n} 處)")

        # 3. 注入缺失的 random 工具 (若 AI 堅持使用)
        hallucination_utils = ""
        
        if 'random_fraction(' in clean_code and 'def random_fraction' not in clean_code:
            hallucination_utils += """
    def random_fraction(min_v, max_v, min_den=2, max_den=10, *args):
        # [Auto-Injected Helper]
        num = random.randint(min_v, max_v) # 簡化實作
        den = random.randint(min_den, max_den)
        return Fraction(num, den) if den != 0 else Fraction(num, 1)
"""
            qwen_fixes += 1
            print(f"🔧 [{skill_id}] 自動注入 random_fraction 輔助函式")

        if 'random_mixed_number(' in clean_code and 'def random_mixed_number' not in clean_code:
            hallucination_utils += """
    def random_mixed_number(min_whole, max_whole, min_num, max_num, min_den, max_den):
        # [Auto-Injected Helper]
        w = random.randint(min_whole, max_whole)
        n = random.randint(min_num, max_num)
        d = random.randint(min_den, max_den)
        if d == 0: d = 1
        return Fraction(w * d + n, d)
"""
            qwen_fixes += 1
            print(f"🔧 [{skill_id}] 自動注入 random_mixed_number 輔助函式")

        # 將輔助函式注入到 generate 函式開頭
        if hallucination_utils:
            clean_code = re.sub(
                r'(def\s+generate\s*\([^)]*\):\n)',
                r'\1' + hallucination_utils,
                clean_code,
                count=1
            )

        # F. [V47.3 新增] Healer 熱修補：題幹強制使用 fmt_num，修復雙括號與缺 f-string
        # ========================================
        # F.1 強制題幹使用 fmt_num：將所有 to_latex(...) 改為 fmt_num(...)
        clean_code, n = re.subn(r'\bto_latex\s*\(', 'fmt_num(', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 題幹格式修復: to_latex(...) → fmt_num(...) ({n} 處)")
        
        # F.2 修復 f-string 內雙大括號包 op_latex 的情況
        # 例：f"{{{op_latex[op]}}}" → f"{op_latex[op]}"
        clean_code, n = re.subn(r'\{\{op_latex\[(.+?)\]\}\}', r'{op_latex[\1]}', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] f-string 修復: {{{{op_latex[...]}}}} → {{op_latex[...]}} ({n} 處)")
        
        # F.3 若 q 行包含 {...} 但不是 f-string，補上 f 前綴
        # 匹配 "q = '...{...}...'" 或 "q += '...{...}...'"
        clean_code, n = re.subn(
            r"(q\s*[\+\-]?=\s*)'([^'\n]*\{[^'\n]*\}[^'\n]*)',",
            r"\1f'\2',",
            clean_code
        )
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] f-string 前綴修復: q = '{{...}}' → q = f'{{...}}' ({n} 處)")
        
        # F.4 [V47.0 後處理] 修復 fmt_num(clean_latex_output)(X) 這種錯誤串接
        # 防止替換順序導致的雙重包裹
        clean_code, n = re.subn(
            r'fmt_num\s*\(\s*clean_latex_output\s*\)\s*\(\s*([a-zA-Z_]\w*)\s*\)',
            r'clean_latex_output(\1)',
            clean_code
        )
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 修復函式串接錯誤: fmt_num(clean_latex_output)(X) → clean_latex_output(X) ({n} 處)")

        # [V47.4 新增通用 Regex 修補]
        # G.1 修復 to_latex(...) 在全域：轉為 fmt_num(...)
        clean_code, n = re.subn(r'\bto_latex\s*\(', 'fmt_num(', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 全域修復: to_latex(...) → fmt_num(...) ({n} 處)")
        
        # G.2 修復雙括號 {{}} 包 op_latex
        clean_code, n = re.subn(r'\{\{op_latex\[(.+?)\]\}\}', r'{op_latex[\1]}', clean_code)
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 雙括號修復: {{{{op_latex[...]}}}} → {{op_latex[...]}} ({n} 處)")
        
        # G.3 修復 Fraction 除法：Fraction(a, b) / Fraction(c, d) → (a/b) / (c/d) 或用乘法倒數
        clean_code, n = re.subn(
            r'Fraction\s*\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)\s*/\s*Fraction\s*\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)',
            r'(\1 / \2) / (\3 / \4)',
            clean_code
        )
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] Fraction 除法修復: Fraction(a,b)/Fraction(c,d) → 更清晰形式 ({n} 處)")
        
        # G.4 修復括號模式：若存在 bracket_structure = random.choice(...) 的候選集中有 None 或空值，篩選掉
        clean_code, n = re.subn(
            r'(bracket_structure\s*=\s*random\.choice\(\[)([^\]]*None[^\]]*)\](\))',
            r'\1\2\3',
            clean_code
        )
        if n > 0:
            qwen_fixes += n
            print(f"🔧 [{skill_id}] 括號候選篩選: 移除 None 或無效值 ({n} 處)")
        
        regex_fixes += qwen_fixes
        healing_duration = time.time() - healing_start

        # ========================================
        # Step G: [NEW] AST 深度邏輯手術
        # ========================================
        # 只有當程式碼至少是語法正確(Syntax Valid)時，AST 才能運作
        # 所以先做一次快速檢查，或直接 try-catch
        
        ast_start = time.time()
        clean_code, ast_fixes_count = fix_code_via_ast(clean_code)
        ast_fixes += ast_fixes_count
        # ========================================

        # ========================================
        # Step H: [DISABLED V46.9] 強制 LaTeX 清洗
        # ========================================
        # ❌ 已禁用原因：
        #    - 舊邏輯假設變數名稱為 q，但 AI 可能使用 q_latex、question 等
        #    - 導致 LaTeX 清洗邏輯無法應用（問題代碼中 return 用 q_latex 但檢查 q）
        # ✅ 新解決方案：使用 Step E.9 Return 語句自動清洗
        #    - 自動偵測 return 中的實際變數名稱
        #    - 對所有變數名稱都能正確應用 clean_latex_output()
        # ========================================

        # 組合
        final_code = CALCULATION_SKELETON + "\n" + clean_code

        # 7. 驗證
        is_valid, error_msg = validate_python_code(final_code)
        
        # 8. 生成完整標頭 (Header)
        duration = time.time() - start_time
        created_at = _pydt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        output_dir = _ensure_dir(_path_in_root('skills'))  # ← 用穩定解析
        # Dynamic Sampling: 执行 10 次生成验证 + Gating
        dyn_ok = True  # [V47.4] 動態採樣 Gating 標誌
        if is_valid:
            import importlib.util
            try:
                spec = importlib.util.spec_from_loader("temp_skill", loader=None)
                temp_module = importlib.util.module_from_spec(spec)
                exec(final_code, temp_module.__dict__)
                
                # 采样测试
                for sample_idx in range(10):
                    try:
                        item = temp_module.generate()
                        # 验证返回结构
                        assert isinstance(item, dict), f"generate() must return dict, got {type(item)}"
                        assert 'question_text' in item, "Missing 'question_text' key"
                        assert 'answer' in item, "Missing 'answer' key"
                        # 验证没有函数对象或类型错误
                        question_str = str(item.get('question_text', ''))
                        if 'function' in str(type(item.get('question_text', ''))).lower():
                            raise TypeError(f"question_text is function object, not string: {type(item['question_text'])}")
                    except Exception as e:
                        error_msg = f"Dynamic sampling failed at iteration {sample_idx+1}: {str(e)}"
                        dyn_ok = False  # [V47.4] Gating: 採樣失敗，標記不能寫檔
                        print(f"[WARN] {error_msg}")
                        break
                else:
                    # 10 次都成功
                    print(f"✅ [{skill_id}] Dynamic sampling passed all 10 iterations")
            except Exception as e:
                dyn_ok = False  # [V47.4] Gating: 採樣框架出錯，標記不能寫檔
                print(f"[WARN] Dynamic sampling error (gating activated): {str(e)}")
        
        # [V47.4] Gating 控制：只有當 is_valid AND dyn_ok 時，才寫檔
        success_final = bool(is_valid and dyn_ok)
        if success_final:
            out_path = os.path.join(output_dir, f'{skill_id}.py')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(header + final_code)
            print(f"✅ [{skill_id}] File written: {os.path.abspath(out_path)}")
        else:
            if not is_valid:
                print(f"❌ [{skill_id}] Syntax validation failed - file NOT written")
            if not dyn_ok:
                print(f"❌ [{skill_id}] Dynamic sampling gating failed - file NOT written")
            
            # [V47.4] 影子寫檔：失敗樣本保留以便 debug（不影響正式）
            try:
                shadow_dir = _ensure_dir(_path_in_root('skills_shadow'))
                iso_dir    = _ensure_dir(_path_in_root('reports', 'isolated'))
                ts = _pydt.datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # 1) final_code（含 skeleton 的完整檔）
                shadow_path = os.path.join(shadow_dir, f"{skill_id}_FAILED_{ts}.py")
                with open(shadow_path, 'w', encoding='utf-8') as f:
                    f.write(header + final_code)
                
                # 2) clean_code（Healer 後、未包 skeleton）
                clean_only_path = os.path.join(shadow_dir, f"{skill_id}_FAILED_{ts}.clean.py")
                try:
                    with open(clean_only_path, 'w', encoding='utf-8') as f:
                        f.write(clean_code)
                except:
                    pass
                
                # 替代：直接再寫一份 final_code 到 iso_dir 當第二個落點（保險）
                iso_copy_path = os.path.join(iso_dir, f"{skill_id}_FAILED_{ts}.py")
                with open(iso_copy_path, 'w', encoding='utf-8') as f:
                    f.write(header + final_code)
                
                # 3) raw_output（模型原始文字）
                raw_path = os.path.join(shadow_dir, f"{skill_id}_FAILED_{ts}.raw.txt")
                with open(raw_path, 'w', encoding='utf-8') as f:
                    f.write(raw_output or "")
                
                print("📦 Isolated Save:")
                print("   • Final (skeleton+code):", os.path.abspath(shadow_path))
                print("   • Raw LLM output      :", os.path.abspath(raw_path))
                print("   • Extra copy (reports):", os.path.abspath(iso_copy_path))
            except Exception as e:
                print(f"[WARN] Shadow save failed: {e}")

        # [V47.4] Feature Flags 快照：把旗標串成文字，便於離線分析
        flags = {
            'capsule': 0,      # 是否啟用 Architect Domain Capsule（目前 0/1）
            'coderV': 'V47.4', # Coder prompt 流水線版本字串
            'regexV47': 1,     # 是否啟用通用 Regex 修補
            'dynStrict': 1,    # 嚴格動態採樣 gating
            'shadow': 0,       # 是否影子寫檔（skills_shadow）
        }
        prompt_level_with_flags = (kwargs.get('prompt_level', 'Full-Healing')
                                   + " | "
                                   + ";".join(f"{k}={v}" for k, v in flags.items()))

        # 9. Log
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=len(prompt),
            code_len=len(final_code),
            is_valid=success_final,
            error_msg=error_msg,
            repaired=(regex_fixes > 0 or ast_fixes > 0),
            model_name=current_model,
            final_code=final_code,
            raw_response=raw_output,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            score_syntax=100.0 if success_final else 0.0,
            ablation_id=ablation_id,
            model_size_class=kwargs.get('model_size_class', 'cloud'),
            prompt_level=prompt_level_with_flags,
            healing_duration=healing_duration,
            is_executable=1 if success_final else 0,
            missing_imports_fixed=', '.join(removed_list) if removed_list else '',
            score_math=0.0,
            score_visual=0.0,
            resource_cleanup_flag=False
        )

        return success_final, "V47.4 Generated", {
            'tokens': prompt_tokens + completion_tokens,
            'score_syntax': 100.0 if success_final else 0.0,
            'fixes': regex_fixes + ast_fixes,
            'is_valid': success_final
        }

    except Exception as e:
        print(f"Generate Error: {e}")
        # 保底落盤：把能拿到的 final_code 或 raw_output 寫到 reports/isolated/
        try:
            iso_dir = _ensure_dir(_path_in_root('reports', 'isolated'))
            ts = _pydt.datetime.now().strftime('%Y%m%d_%H%M%S')
            if 'final_code' in locals():
                p = os.path.join(iso_dir, f"{skill_id}_EXCEPTION_{ts}.py")
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(locals().get('header', '') + final_code)
                print("🧯 Saved final_code on exception:", os.path.abspath(p))
            if 'raw_output' in locals() and raw_output:
                p = os.path.join(iso_dir, f"{skill_id}_EXCEPTION_{ts}.raw.txt")
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(raw_output)
                print("🧯 Saved raw_output on exception:", os.path.abspath(p))
        except Exception as ee:
            print("[WARN] Exception fallback save failed:", ee)
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