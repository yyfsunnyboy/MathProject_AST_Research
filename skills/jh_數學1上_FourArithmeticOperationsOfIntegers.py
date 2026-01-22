# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: qwen2.5-coder:14b | Strategy: V44.2 Standard-Template
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 43.18s | Tokens: In=6366, Out=1342
# Created At: 2026-01-22 15:37:03
# Fix Status: [Repaired] | Fixes: Regex=14, AST=0
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
    VAR_SMALL_INT_RANGE = list(range(-12, -1)) + list(range(1, 13))
    VAR_MEDIUM_INT_RANGE = list(range(-30, -1)) + list(range(1, 31))
    VAR_LARGE_INT_RANGE = list(range(-100, -1)) + list(range(1, 101))
    VAR_FINAL_RESULT_RANGE = range(-150, 151)
    OPERATORS_MD = ['*', '/']
    OPERATORS_AS = ['+', '-']
    ALL_OPERATORS = ['+', '-', '*', '/']

    def generate_integer_division_pair(max_abs_dividend_target, max_abs_divisor_range, max_abs_quotient_range):
        while True:
            divisor = random.choice(list(range(-max_abs_divisor_range, -1)) + list(range(1, max_abs_divisor_range + 1)))
            quotient = random.choice(list(range(-max_abs_quotient_range, -1)) + list(range(1, max_abs_quotient_range + 1)))
            dividend = divisor * quotient
            if abs(dividend) <= max_abs_dividend_target:
                return (dividend, divisor, quotient)

    while True:
        mode = random.choice(['A.1', 'A.2', 'B.1'])

        if mode == 'A.1':
            k_final = random.choice(VAR_SMALL_INT_RANGE)
            op2_char = random.choice(OPERATORS_MD)
            n3_raw = random.choice(VAR_SMALL_INT_RANGE)

            if op2_char == '/':
                n3 = n3_raw
                intermediate_val_target = k_final * n3
            elif op2_char == '*':
                while k_final % n3_raw != 0:
                    n3_raw = random.choice(VAR_SMALL_INT_RANGE)
                n3 = n3_raw
                intermediate_val_target = k_final // n3

            if abs(intermediate_val_target) > VAR_LARGE_INT_RANGE[-1]:
                continue

            op1_char = random.choice(OPERATORS_MD)
            n2_raw = random.choice(VAR_SMALL_INT_RANGE)

            if op1_char == '/':
                n2 = n2_raw
                n1 = intermediate_val_target * n2
            elif op1_char == '*':
                while intermediate_val_target % n2_raw != 0:
                    n2_raw = random.choice(VAR_SMALL_INT_RANGE)
                n2 = n2_raw
                n1 = intermediate_val_target // n2

            if abs(n1) > VAR_LARGE_INT_RANGE[-1] or abs(n2) > VAR_LARGE_INT_RANGE[-1] or abs(n3) > VAR_LARGE_INT_RANGE[-1]:
                continue

            final_answer = eval(f"{n1} {op1_char} {n2} {op2_char} {n3}")

        elif mode == 'A.2':
            n1 = random.choice(VAR_MEDIUM_INT_RANGE)
            op1_char = random.choice(OPERATORS_AS)
            op2_char = random.choice(OPERATORS_MD)

            if op2_char == '*':
                n2 = random.choice(VAR_SMALL_INT_RANGE)
                n3 = random.choice(VAR_SMALL_INT_RANGE)
            elif op2_char == '/':
                n2_dividend, n3_divisor, _ = generate_integer_division_pair(VAR_LARGE_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1])
                n2 = n2_dividend
                n3 = n3_divisor

            if abs(n2 * n3) > VAR_LARGE_INT_RANGE[-1] and op2_char == '*':
                continue
            elif abs(n2 / n3) > VAR_LARGE_INT_RANGE[-1] and op2_char == '/':
                continue

            final_answer = eval(f"{n1} {op1_char} ({n2} {op2_char} {n3})")

        elif mode == 'B.1':
            op1_char = random.choice(OPERATORS_MD)
            if op1_char == '*':
                n1 = random.choice(VAR_SMALL_INT_RANGE)
                n2 = random.choice(VAR_SMALL_INT_RANGE)
                term1_val = n1 * n2
            elif op1_char == '/':
                n1_dividend, n2_divisor, _ = generate_integer_division_pair(VAR_LARGE_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1])
                n1 = n1_dividend
                n2 = n2_divisor
                term1_val = n1 // n2

            if abs(term1_val) > VAR_LARGE_INT_RANGE[-1]:
                continue

            op3_char = random.choice(OPERATORS_MD)
            if op3_char == '*':
                n3 = random.choice(VAR_SMALL_INT_RANGE)
                n4 = random.choice(VAR_SMALL_INT_RANGE)
                term2_val = n3 * n4
            elif op3_char == '/':
                n3_dividend, n4_divisor, _ = generate_integer_division_pair(VAR_LARGE_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1], VAR_SMALL_INT_RANGE[-1])
                n3 = n3_dividend
                n4 = n4_divisor
                term2_val = n3 // n4

            if abs(term2_val) > VAR_LARGE_INT_RANGE[-1]:
                continue

            op2_char = random.choice(OPERATORS_AS)
            final_answer = eval(f"{term1_val} {op2_char} {term2_val}")

        if abs(final_answer) > VAR_FINAL_RESULT_RANGE[-1]:
            continue

        q = f"${fmt_num(n1)} \\times {fmt_num(n2)} \\div {fmt_num(n3)}$"
        a = str(final_answer)

        # Sanitization
        if isinstance(q, str):
            q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        if isinstance(a, str) and "=" in a:
            a = a.split("=")[-1].strip()

        return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}