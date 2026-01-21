# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: gemini-2.5-flash | Strategy: V44.2 Standard-Template
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 14.56s | Tokens: In=1466, Out=657
# Created At: 2026-01-21 23:56:36
# Fix Status: [Repaired] | Fixes: Regex=2, AST=0
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

def generate(level=1, **kwargs):
    # Helper function for LaTeX number formatting
    # This function is crucial for ensuring negative numbers are correctly parenthesized
    def fmt_num(n):
        if n < 0:
            return f"({n})"
        return str(n)

    # 1. Variable Definition from MASTER_SPEC
    MAGNITUDE_MIN = 1
    MAGNITUDE_MAX = 150

    # 2. Operation Logic - Step 1: Generate values
    # Randomly select absolute values for n1 and n2
    n1_abs = random.randint(MAGNITUDE_MIN, MAGNITUDE_MAX)
    n2_abs = random.randint(MAGNITUDE_MIN, MAGNITUDE_MAX)

    # Randomly determine if n1 and n2 are negative
    n1_is_negative = random.choice([True, False])
    n2_is_negative = random.choice([True, False])

    # Calculate the actual integer values for n1 and n2
    n1 = -n1_abs if n1_is_negative else n1_abs
    n2 = -n2_abs if n2_is_negative else n2_abs

    # Constraint: n1 and n2 will never be 0 due to MAGNITUDE_MIN = 1.

    # 2. Operation Logic - Step 2: Construct question (q)
    # Use the mandatory fmt_num to format numbers for LaTeX,
    # ensuring negative numbers are enclosed in parentheses.
    q_str_n1 = fmt_num(n1)
    q_str_n2 = fmt_num(n2)

    # Construct the final question in LaTeX format
    q = f"${q_str_n1} - {q_str_n2}$"

    # 2. Operation Logic - Step 3: Calculate answer (a)
    # Perform the subtraction operation
    a_val = n1 - n2
    # Convert the answer to a string as required
    a = str(a_val)

    # 4. 格式潔癖 (Sanitization) - MUST BE INCLUDED
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a: a = a.split("=")[-1].strip()

    # Return format (Research Standard) - MUST BE INCLUDED
    return {
        'question_text': q,
        'correct_answer': a,
        'answer': a,      # 必須包含此欄位
        'mode': 1         # 必須包含此欄位
    }