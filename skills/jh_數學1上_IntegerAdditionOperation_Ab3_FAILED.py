# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: gemini-2.5-flash | Strategy: V44.2 Standard-Template
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 21.67s | Tokens: In=1824, Out=696
# Created At: 2026-01-21 23:46:59
# Fix Status: [Repaired] | Fixes: Regex=3, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================

import random
import math
import re
from fractions import Fraction

# [INJECTED UTILS]

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


# [AI GENERATED CODE]
# ---------------------------------------------------------

import random
import re

# Helper function to format numbers for LaTeX, ensuring negative numbers are in parentheses
def fmt_num(n):
    if n < 0:
        return f"({n})"
    return str(n)

def generate(level=1, **kwargs):
    # 1. 變數定義 (Variable Definition)
    # 隨機生成 abs_val1 (範圍 [1, 15])
    abs_val1 = random.randint(1, 15)
    # 隨機生成 abs_val2 (範圍 [1, 15])
    abs_val2 = random.randint(1, 15)
    
    # 隨機決定 sign_n1 (True 為正數, False 為負數)
    sign_n1 = random.choice([True, False])
    # 隨機決定 sign_n2 (True 為正數, False 為負數)
    sign_n2 = random.choice([True, False])

    # 2. 運算邏輯 (Operation Logic)
    # 根據 sign_n1 決定 n1 的實際值
    n1 = abs_val1 if sign_n1 else -abs_val1
    # 根據 sign_n2 決定 n2 的實際值
    n2 = abs_val2 if sign_n2 else -abs_val2

    # 計算最終答案
    result_answer = n1 + n2

    # 3. 格式要求 (Format Requirements)
    # 題目 q (LaTeX 格式)
    # 構建 n1 的 LaTeX 字串表示 (使用 fmt_num 處理負數括號)
    n1_latex_str = fmt_num(n1)

    # 構建 n2 的 LaTeX 字串表示, 並包含加號, 確保格式如 "$A + B$"
    # 根據 MASTER_SPEC 範例, 加號前後有空格
    n2_latex_str_with_op = f"+ {fmt_num(n2)}"
    
    # 組合最終題目字串
    q = f"${n1_latex_str} {n2_latex_str_with_op}$"
    
    # 答案 a (僅輸出最終計算結果的數值字串)
    a = str(result_answer)

    # 格式潔癖 (Sanitization)
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a: a = a.split("=")[-1].strip()

    # 回傳格式 (Research Standard)
    return {
        'question_text': q, 
        'correct_answer': a, 
        'answer': a,      # 必須包含此欄位
        'mode': 1         # 必須包含此欄位
    }