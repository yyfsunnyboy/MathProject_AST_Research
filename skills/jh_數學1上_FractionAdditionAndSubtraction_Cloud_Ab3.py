# ==============================================================================
# ID: jh_數學1上_FractionAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 11.78s | Tokens: In=2630, Out=633
# Created At: 2026-01-22 21:01:50
# Fix Status: [Repaired] | Fixes: Regex=5, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================


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


def generate(level=1, **kwargs):
    # 1. 變數定義 (Variable Definitions)
    # numerator1 (n1): [-20, 20], n1 ≠ 0
    n1 = random.randint(-20, 20)
    while n1 == 0:
        n1 = random.randint(-20, 20)

    # numerator2 (n2): [-20, 20], n2 ≠ 0
    n2 = random.randint(-20, 20)
    while n2 == 0:
        n2 = random.randint(-20, 20)

    # denominator (d): [2, 15]
    d = random.randint(2, 15)

    # operator (op): ['+', '-']
    op = random.choice(['+', '-'])

    # 2. 題目生成 (q)
    # 嚴格遵循 LaTeX 格式與運算鐵律: 必須將 Fraction 物件傳入 fmt_num()
    # fmt_num 會自動處理負號、括號和 \frac 格式。
    frac1 = Fraction(n1, d)
    frac2 = Fraction(n2, d)

    term1_latex = fmt_num(frac1)
    term2_latex = fmt_num(frac2)

    # 單一環境原則: question_text 必須只在最外層包裹一對 $
    q = f"${term1_latex} {op} {term2_latex}$"

    # 3. 答案計算與格式化 (a)
    result_frac = None
    if op == '+':
        result_frac = frac1 + frac2
    elif op == '-':
        result_frac = frac1 - frac2

    # 將 Fraction 物件格式化為 MASTER_SPEC 指定的字串形式 (例如 "0", "15/4", "-1/2")
    if result_frac.denominator == 1:
        a = str(result_frac.numerator)
    else:
        a = f"{result_frac.numerator}/{result_frac.denominator}"

    # 格式潔癖 (Sanitization)
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a: a = a.split("=")[-1].strip()

    return {
        'question_text': q,
        'correct_answer': a,
        'answer': a,
        'mode': 1
    }