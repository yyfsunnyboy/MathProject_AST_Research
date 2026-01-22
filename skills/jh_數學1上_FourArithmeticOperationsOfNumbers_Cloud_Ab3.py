# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: gemini-2.5-flash | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 75.53s | Tokens: In=3517, Out=3650
# Created At: 2026-01-22 21:16:55
# Fix Status: [Repaired] | Fixes: Regex=8, AST=0
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
    q = ""
    a = None
    mode = 1

    # --- Helper functions based on MASTER_SPEC ---
    # These helpers are defined within the generate function's scope
    # to ensure they use the pre-loaded `Fraction` and other modules.

    def _get_base_int():
        """Generates an integer in [-15, -1] U [1, 15]."""
        return random.choice(list(range(-15, 0)) + list(range(1, 16)))

    def _get_denominator():
        """Generates a denominator in [2, 10]."""
        return random.randint(2, 10)

    def _generate_fraction_obj(allow_improper=True):
        """Generates a Fraction object, ensuring simplest form."""
        while True:
            num = _get_base_int()
            den = _get_denominator()
            frac = Fraction(num, den)
            # Fraction constructor automatically simplifies.
            # The constraint "gcd(abs(numerator), denominator) = 1" refers to the simplified form.
            if allow_improper or abs(frac) < 1:
                return frac
            # If not allowing improper and it's improper, regenerate
            if not allow_improper and abs(frac) >= 1:
                continue

    def _generate_mixed_number_obj():
        """Generates a mixed number as a Fraction object, correctly handling signs."""
        integer_part = _get_base_int()
        proper_frac_part = _generate_fraction_obj(allow_improper=False) # Ensure proper fraction
        
        # Mixed number representation: integer_part (absolute value) + proper_frac_part, then apply original sign
        # e.g., -2 1/2 is -(2 + 1/2) = -5/2
        absolute_value = abs(integer_part) + proper_frac_part
        
        if integer_part < 0:
            return -absolute_value
        else:
            return absolute_value

    def _is_finite_decimal_with_max_2_places(frac_obj):
        """Checks if a Fraction can be represented as a finite decimal with at most 2 decimal places."""
        if not isinstance(frac_obj, Fraction):
            return False
        
        # Check if it's a finite decimal
        den = frac_obj.denominator
        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        if den != 1:
            return False # Not a finite decimal
        
        # Check if it has at most 2 decimal places after conversion to float
        float_val = float(frac_obj)
        s = str(float_val)
        if '.' in s:
            decimal_part = s.split('.')[-1]
            return len(decimal_part) <= 2
        return True # It's an integer, so 0 decimal places

    def _generate_N_term():
        """Generates a numerical term (int, Fraction, or float for finite decimals)."""
        choice = random.choice(['int', 'fraction', 'mixed'])
        num_obj = None

        if choice == 'int':
            num_obj = _get_base_int()
        elif choice == 'fraction':
            num_obj = _generate_fraction_obj(allow_improper=True)
        elif choice == 'mixed':
            num_obj = _generate_mixed_number_obj()
        
        # Randomly convert to float if it's a convertible fraction and meets criteria
        if isinstance(num_obj, Fraction) and _is_finite_decimal_with_max_2_places(num_obj) and random.random() < 0.5:
            return float(num_obj)
        
        return num_obj

    # Operator mappings for LaTeX display and internal calculation
    op_map_latex = {
        '+': '+',
        '-': '-',
        '*': r'\times',
        '/': r'\div'
    }

    op_map_calc = {
        r'\times': '*',
        r'\div': '/'
    }

    problem_type = random.choice(['chained', 'distributive'])

    if problem_type == 'chained':
        # Type A: Chained Operations
        num_terms = random.randint(3, 4) # For level 1, stick to 3 or 4 terms
        
        q_parts = [] # For LaTeX question string
        calc_parts = [] # For `eval()` string
        
        # Generate first term
        term1 = _generate_N_term()
        q_parts.append(fmt_num(term1))
        # Convert to Fraction for consistent calculation with eval
        calc_parts.append(f"Fraction({Fraction(term1).numerator}, {Fraction(term1).denominator})")

        for i in range(num_terms - 1):
            op_calc_str = random.choice(['+', '-', '*', '/'])
            op_latex_str = op_map_latex[op_calc_str]
            
            next_term = _generate_N_term()

            # Ensure division by zero is avoided
            while op_calc_str == '/' and (next_term == 0 or (isinstance(next_term, Fraction) and next_term.numerator == 0)):
                next_term = _generate_N_term()
            
            q_parts.append(op_latex_str)
            q_parts.append(fmt_num(next_term))
            calc_parts.append(op_calc_str)
            calc_parts.append(f"Fraction({Fraction(next_term).numerator}, {Fraction(next_term).denominator})")
        
        # Randomly add parentheses for 3-term expressions for `level=1` (simple cases)
        if num_terms == 3 and random.random() < 0.5: # 50% chance for parentheses
            paren_choice = random.choice([1, 2]) # (N1 op1 N2) op2 N3 or N1 op1 (N2 op2 N3)
            if paren_choice == 1:
                # (N1 op1 N2) op2 N3
                q_parts.insert(0, '(')
                q_parts.insert(4, ')')
                calc_parts.insert(0, '(')
                calc_parts.insert(4, ')')
            else:
                # N1 op1 (N2 op2 N3)
                q_parts.insert(2, '(')
                q_parts.insert(6, ')')
                calc_parts.insert(2, '(')
                calc_parts.insert(6, ')')

        q = '$' + ' '.join(q_parts) + '$'
        
        # Calculate the answer
        calc_expr = ' '.join(calc_parts)
        try:
            raw_result = eval(calc_expr)
        except ZeroDivisionError:
            # If a division by zero somehow slipped through, regenerate.
            return generate(level, **kwargs) # Recursively call to regenerate
        
        # Post-process the result to match desired output format
        if isinstance(raw_result, float):
            a = round(raw_result, 2) # Limit float precision for answer
        else:
            final_frac = Fraction(raw_result)
            if final_frac.denominator == 1:
                a = int(final_frac)
            elif _is_finite_decimal_with_max_2_places(final_frac) and random.random() < 0.7: # Higher chance to convert to decimal if possible
                a = float(final_frac)
            else:
                a = final_frac

    else: # problem_type == 'distributive'
        # Type B: Distributive Property
        
        # Choose a structure template
        # Use placeholders for A, B, C, op_inner_latex, op_outer_latex
        templates = [
            # A * C + B * C
            {'q': '{A_str} {op_outer_latex} {C_str} + {B_str} {op_outer_latex} {C_str}',
             'calc': '({A_calc} {op_outer_calc} {C_calc}) + ({B_calc} {op_outer_calc} {C_calc})',
             'op_outer_options': ['*', '/'], 'op_inner_options': ['+', '-']},
            # A * C - B * C
            {'q': '{A_str} {op_outer_latex} {C_str} - {B_str} {op_outer_latex} {C_str}',
             'calc': '({A_calc} {op_outer_calc} {C_calc}) - ({B_calc} {op_outer_calc} {C_calc})',
             'op_outer_options': ['*', '/'], 'op_inner_options': ['+', '-']},
            # C * A + C * B
            {'q': '{C_str} {op_outer_latex} {A_str} + {C_str} {op_outer_latex} {B_str}',
             'calc': '({C_calc} {op_outer_calc} {A_calc}) + ({C_calc} {op_outer_calc} {B_calc})',
             'op_outer_options': ['*'], 'op_inner_options': ['+', '-']}, # Division C / A is not distributive over C / (A+B)
            # C * A - C * B
            {'q': '{C_str} {op_outer_latex} {A_str} - {C_str} {op_outer_latex} {B_str}',
             'calc': '({C_calc} {op_outer_calc} {A_calc}) - ({C_calc} {op_outer_calc} {B_calc})',
             'op_outer_options': ['*'], 'op_inner_options': ['+', '-']},
            # A ÷ C + B ÷ C
            {'q': '{A_str} {op_outer_latex} {C_str} + {B_str} {op_outer_latex} {C_str}',
             'calc': '({A_calc} {op_outer_calc} {C_calc}) + ({B_calc} {op_outer_calc} {C_calc})',
             'op_outer_options': ['/'], 'op_inner_options': ['+', '-']},
            # A ÷ C - B ÷ C
            {'q': '{A_str} {op_outer_latex} {C_str} - {B_str} {op_outer_latex} {C_str}',
             'calc': '({A_calc} {op_outer_calc} {C_calc}) - ({B_calc} {op_outer_calc} {C_calc})',
             'op_outer_options': ['/'], 'op_inner_options': ['+', '-']},
        ]
        
        template = random.choice(templates)
        op_outer_calc = random.choice(template['op_outer_options'])
        op_outer_latex = op_map_latex[op_outer_calc]
        op_inner_calc = random.choice(template['op_inner_options'])

        # Generate common_factor C
        common_factor = _generate_N_term()
        # Ensure common_factor is not zero, especially if it's a divisor
        while common_factor == 0 or \
              (isinstance(common_factor, Fraction) and common_factor.numerator == 0) or \
              (op_outer_calc == '/' and (common_factor == 0 or (isinstance(common_factor, Fraction) and common_factor.numerator == 0))):
            common_factor = _generate_N_term()
        
        # Generate inner_result_term (small range for easier A, B generation)
        inner_result_term = _generate_N_term()
        while inner_result_term == 0: # Ensure inner result is not trivial 0
             inner_result_term = _generate_N_term()

        # Generate B
        B = _generate_N_term()
        
        # Calculate A such that (A op_inner B) = inner_result_term
        A_frac = Fraction(inner_result_term)
        B_frac = Fraction(B)
        
        if op_inner_calc == '+':
            A_frac = A_frac - B_frac
        else: # op_inner_calc == '-'
            A_frac = A_frac + B_frac
        
        # Convert A_frac back to int/float if it was originally, for consistency in display
        A_val = A_frac
        if A_frac.denominator == 1:
            A_val = int(A_frac)
        elif _is_finite_decimal_with_max_2_places(A_frac) and random.random() < 0.5:
            A_val = float(A_frac)
        
        # Prepare strings for question and calculation
        A_str = fmt_num(A_val)
        B_str = fmt_num(B)
        C_str = fmt_num(common_factor)
        
        A_calc = f"Fraction({Fraction(A_val).numerator}, {Fraction(A_val).denominator})"
        B_calc = f"Fraction({Fraction(B).numerator}, {Fraction(B).denominator})"
        C_calc = f"Fraction({Fraction(common_factor).numerator}, {Fraction(common_factor).denominator})"

        q_formatted = template['q'].format(
            A_str=A_str, B_str=B_str, C_str=C_str,
            op_outer_latex=op_outer_latex
        )
        q = '$' + q_formatted + '$'

        calc_expr = template['calc'].format(
            A_calc=A_calc, B_calc=B_calc, C_calc=C_calc,
            op_outer_calc=op_outer_calc
        )
        
        try:
            raw_result = eval(calc_expr)
        except ZeroDivisionError:
            return generate(level, **kwargs) # Recursively call to regenerate

        # Post-process the result
        if isinstance(raw_result, float):
            a = round(raw_result, 2)
        else:
            final_frac = Fraction(raw_result)
            if final_frac.denominator == 1:
                a = int(final_frac)
            elif _is_finite_decimal_with_max_2_places(final_frac) and random.random() < 0.7:
                a = float(final_frac)
            else:
                a = final_frac
    
    # Sanitize outputs as per strict code guidelines
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