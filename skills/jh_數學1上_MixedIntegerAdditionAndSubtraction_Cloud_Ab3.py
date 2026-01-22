# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 9.71s | Tokens: In=4879, Out=664
# Created At: 2026-01-22 20:04:38
# Fix Status: [Repaired] | Fixes: Regex=4, AST=0
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
    """
    生成整數的加減運算題目。
    根據 MASTER_SPEC:
    - 項數 N 在 3 到 5 之間。
    - 數值項 n_i 範圍在 [-100, 100]。
    - 運算子為 '+' 或 '-'。
    - 題目使用 LaTeX 格式, 負數項會自動加括號。
    - 答案為計算結果的整數。
    """

    # I. 變數定義 (Variable Definition)
    # 1. 項數 (Number of Terms) N
    N = random.randint(3, 5)

    # 2. 數值項 (Numerical Terms) n_i
    terms = [random.randint(-100, 100) for _ in range(N)]

    # II. 運算邏輯 (Operation Logic)
    # 1. 運算子序列 (Operator Sequence) op_i
    operators = [random.choice(['+', '-']) for _ in range(N - 1)]

    # 2. 算式結構 (Expression Structure) 與 3. 計算 (Calculation)
    # 構建題目字符串和同時計算答案
    q_parts = []
    current_answer = terms[0]

    # 將第一個數字加入題目字符串
    q_parts.append(fmt_num(terms[0]))

    # 遍歷運算子和後續數字
    for i in range(N - 1):
        op = operators[i]
        next_term = terms[i+1]

        # 將運算子加入題目字符串
        q_parts.append(op)

        # 將下一個數字加入題目字符串 (fmt_num 自動處理負數括號)
        q_parts.append(fmt_num(next_term))

        # 執行計算
        if op == '+':
            current_answer += next_term
        elif op == '-':
            current_answer -= next_term

    # III. 格式要求 (Format Requirements)
    # 1. 題目 q (LaTeX 數學模式格式)
    q = f"${' '.join(q_parts)}$"

    # 2. 答案 a
    a = current_answer

    # Sanitization
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a:
            a = a.split("=")[-1].strip()

    return {
        'question_text': q,
        'correct_answer': a,
        'answer': a,
        'mode': 1
    }