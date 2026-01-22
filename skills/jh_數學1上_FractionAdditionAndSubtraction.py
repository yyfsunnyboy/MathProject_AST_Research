# ==============================================================================
# ID: jh_數學1上_FractionAdditionAndSubtraction
# Model: qwen2.5-coder:14b | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 16.28s | Tokens: In=2699, Out=439
# Created At: 2026-01-22 21:10:36
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
    # Step 1: Variable Generation
    numerator1 = random.randint(-20, 20)
    while numerator1 == 0:
        numerator1 = random.randint(-20, 20)
    
    numerator2 = random.randint(-20, 20)
    while numerator2 == 0:
        numerator2 = random.randint(-20, 20)
    
    denominator = random.randint(2, 15)
    
    operator = random.choice(['+', '-'])
    
    # Step 2: Question Generation
    term1_str = fmt_num(Fraction(numerator1, denominator))
    term2_str = fmt_num(Fraction(numerator2, denominator))
    
    q = f"${term1_str} {operator} {term2_str}$"
    
    # Step 3: Answer Calculation and Formatting
    if operator == '+':
        result_numerator = numerator1 + numerator2
    elif operator == '-':
        result_numerator = numerator1 - numerator2
    
    result_denominator = denominator
    
    gcd = math.gcd(abs(result_numerator), abs(result_denominator))
    
    simplified_numerator = result_numerator // gcd
    simplified_denominator = result_denominator // gcd
    
    if simplified_denominator == 1:
        a = str(simplified_numerator)
    else:
        a = f"{simplified_numerator}/{simplified_denominator}"
    
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
        'answer': a,      # 用於自動批改
        'mode': 1         # 題型編號
    }