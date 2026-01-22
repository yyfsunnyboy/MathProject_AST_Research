# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: qwen2.5-coder:14b | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 36.45s | Tokens: In=3939, Out=1034
# Created At: 2026-01-22 22:46:59
# Fix Status: [Repaired] | Fixes: Regex=12, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================


# [INJECTED UTILS]

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


# [AI GENERATED CODE]
# ---------------------------------------------------------


def generate(level=1, **kwargs):

    def fmt_num(num, signed=False, op=False):
        if isinstance(num, Fraction):
            if num < 0:
                return f"(-{to_latex(Fraction(-num.numerator, num.denominator))})"
            else:
                return to_latex(num)
        elif num < 0:
            return f"({num})"
        else:
            return str(num)

    def to_latex(frac):
        if frac < 0:
            return f"(-\\frac{{{{{abs(frac.numerator)}}}}}{{{{{{frac.denominator}}}}}})"
        else:
            return f"\\frac{{{{{{frac.numerator}}}}}}{{{{{{frac.denominator}}}}}}"

    base_int = random.choice([-15, -13, -11, -9, -7, -5, -3, -2, 2, 3, 5, 7, 9, 11, 13, 15])
    denominator = random.randint(2, 10)
    while denominator == 0:
        denominator = random.randint(2, 10)

    fraction_val = Fraction(base_int, denominator).limit_denominator()
    mixed_number_val = base_int + Fraction(random.randint(1, denominator - 1), denominator).limit_denominator()

    def is_decimal(frac):
        while frac.denominator % 2 == 0:
            frac.numerator //= 2
            frac.denominator //= 2
        while frac.denominator % 5 == 0:
            frac.numerator //= 5
            frac.denominator //= 5
        return frac.denominator == 1

    decimal_fraction_val = fraction_val if is_decimal(fraction_val) else None
    if decimal_fraction_val and random.choice([True, False]):
        decimal_fraction_val = float(decimal_fraction_val)

    N_term_types = [base_int, fraction_val, mixed_number_val, decimal_fraction_val]
    N_term = random.choice(N_term_types)

    operators_basic = ['+', '-']
    operators_multi_div = ['\\times', '\\div']
    operators_all = operators_basic + operators_multi_div

    def generate_chained_operations():
        target_final_result = Fraction(random.randint(-10, 10), random.randint(2, 10)).limit_denominator()
        terms = [target_final_result]
        ops = []

        for _ in range(2):
            op = random.choice(operators_all)
            if op == '\\times':
                next_val = Fraction(target_final_result.numerator // target_final_result.denominator, random.randint(2, 10)).limit_denominator()
                terms.append(next_val)
                target_final_result *= next_val
            elif op == '\\div':
                next_val = Fraction(random.randint(2, 10), target_final_result.denominator).limit_denominator()
                terms.append(next_val)
                target_final_result /= next_val
            else:
                next_val = Fraction(random.randint(-10, 10), random.randint(2, 10)).limit_denominator()
                terms.append(next_val)
                if op == '+':
                    target_final_result += next_val
                else:
                    target_final_result -= next_val
            ops.append(op)

        q = fmt_num(terms[0])
        for i in range(len(ops)):
            q += f" {ops[i]} {fmt_num(terms[i + 1])}"

        return q, str(target_final_result)

    def generate_distributive_property():
        common_factor = random.choice([base_int, fraction_val, decimal_fraction_val])
        inner_result_term = Fraction(random.randint(-10, 10), random.randint(2, 10)).limit_denominator()
        op_inner = random.choice(['+', '-'])
        B = N_term
        A = inner_result_term + B if op_inner == '+' else inner_result_term - B

        q = f"{fmt_num(A)} {op_inner} {fmt_num(B)} \\times {fmt_num(common_factor)}"
        a = str((A + B) * common_factor)

        return q, a

    question_type = random.choice(['Chained Operations', 'Distributive Property'])
    if question_type == 'Chained Operations':
        q, a = generate_chained_operations()
    else:
        q, a = generate_distributive_property()

    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a:
            a = a.split("=")[-1].strip()

    return {
        'question_text': f"${q}$",
        'correct_answer': a,
        'answer': a,
        'mode': 1
    }