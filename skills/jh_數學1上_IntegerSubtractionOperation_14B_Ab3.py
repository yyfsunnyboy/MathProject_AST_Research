# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: qwen2.5-coder:14b | Strategy: V44.2 Standard-Template
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 69.01s | Tokens: In=4602, Out=312
# Created At: 2026-01-22 19:29:46
# Fix Status: [Repaired] | Fixes: Regex=6, AST=0
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
    # 生成基礎數值
    abs_val1 = random.randint(1, 200)
    abs_val2 = random.randint(1, 200)
    
    # 確定運算數的正負號
    sign_for_op1 = random.choice([1, -1])
    sign_for_op2 = random.choice([1, -1])
    
    operand1 = abs_val1 * sign_for_op1
    operand2 = abs_val2 * sign_for_op2
    
    # 構建算式
    if operand1 < 0:
        operand1_str = f"({operand1})"
    else:
        operand1_str = str(operand1)
    
    if operand2 < 0:
        operand2_str = f"({operand2})"
    else:
        operand2_str = str(operand2)
    
    q = f"${operand1_str} - {operand2_str}$"
    
    # 計算答案
    a = operand1 - operand2
    
    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}