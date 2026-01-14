# ==============================================================================
# ID: jh_數學1上_PowerOfNumbers
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 54.69s | RAG: 8 examples
# Created At: 2026-01-09 16:08:28
# Fix Status: [Clean Pass]
# ==============================================================================


import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses."""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result





# ==============================================================================
# GOLD STANDARD TEMPLATE v8.7 (Universal)
# ==============================================================================
# Rules for AI Coder:
# 1. LATEX: Use f-string with DOUBLE BRACES for LaTeX commands. 
#    Ex: f"\\frac{{{a}}}{{{b}}}" -> \frac{a}{b}
#    Ex: f"\\begin{{bmatrix}} {a} & {b} \\\\ {c} & {d} \\end{{bmatrix}}"
# 2. NEGATIVES: Use fmt_num(val) to handle negative numbers like (-5).
# 3. LEVEL: Level 1 = Basic Concept/Direct Calc. Level 2 = Application/Mixed.
# 4. RETURN: Must return dict with 'question_text', 'answer', 'correct_answer', 'difficulty'.
# ==============================================================================


# Level 1 Problem Types
# ------------------------------------------------------------------------------

def generate_type_1_problem():
    """
    Level 1, Type 1: Applying the power rule (a/b)^n = a^n / b^n for positive fractions.
    Question: Fill in the box.
    """
    numerator = random.randint(2, 9)
    denominator = random.randint(numerator + 1, 10) # ensure fraction < 1
    exponent = random.randint(2, 5)
    frac_latex = f"\\frac{{{numerator}}}{{{denominator}}}"
    
    question_text = (
        f"在下列□中填入適當的數，使等號成立。\n"
        f"${frac_latex}^{{{exponent}}} = {numerator}^\\Box / {denominator}^\\Box$"
    )
    answer = f"□皆為{exponent}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1, Type 2: Applying the power rule (a/b)^n = a^n / b^n where a can be negative.
    Question: Fill in the box.
    """
    numerator = random.randint(-9, -2)
    denominator = random.randint(2, 9)
    exponent = random.randint(2, 5)
    frac_latex = f"\\frac{{{fmt_num(numerator)}}}{{{denominator}}}"
    
    question_text = (
        f"在下列□中填入適當的數，使等號成立。\n"
        f"${fmt_num(numerator)}^\\Box / {denominator}^\\Box$" # Corrected according to spec, should be `fmt_num(numerator)`
    )
    # The question in spec was "${frac_latex}^{{{exponent}}} = {fmt_num(numerator)}^\\Box / {denominator}^\\Box$"
    # The provided example for type 2 is ( -5/3 )^3=(-5 )^□ / 3^□.
    # The spec's `frac_latex` already handles `fmt_num(numerator)`, so the second part of the equation should use it as well.
    question_text = (
        f"在下列□中填入適當的數，使等號成立。\n"
        f"${frac_latex}^{{{exponent}}} = {fmt_num(numerator)}^\\Box / {denominator}^\\Box$"
    )
    answer = f"□皆為{exponent}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 1, Type 3: Comparing powers of the same base x^a and x^b where a != b.
    Handles 0 < x < 1 and x > 1 cases.
    """
    base_type = random.choice(['fraction_lt_1', 'fraction_gt_1', 'decimal_lt_1', 'decimal_gt_1'])
    
    exp1 = random.randint(2, 10)
    exp2 = exp1 + random.randint(1, 3) # Ensure exp2 > exp1 for consistent comparison logic
    
    base_val = None
    base_latex = ""
    
    if base_type == 'fraction_lt_1':
        num = random.randint(1, 5)
        den = random.randint(num + 1, 10)
        base_val = Fraction(num, den)
        base_latex = f"\\frac{{{num}}}{{{den}}}"
    elif base_type == 'fraction_gt_1':
        num = random.randint(6, 10)
        den = random.randint(2, num - 1)
        base_val = Fraction(num, den)
        base_latex = f"\\frac{{{num}}}{{{den}}}"
    elif base_type == 'decimal_lt_1':
        base_val = round(random.uniform(0.1, 0.9), 1)
        base_latex = str(base_val)
    elif base_type == 'decimal_gt_1':
        base_val = round(random.uniform(1.1, 2.5), 1)
        base_latex = str(base_val)

    comparison_symbol = ""
    if base_val < 1:
        # For 0 < x < 1, x^a > x^b if a < b
        comparison_symbol = '>' # Because exp1 < exp2, so base_val^exp1 > base_val^exp2
    else: # base_val > 1
        # For x > 1, x^a < x^b if a < b
        comparison_symbol = '<' # Because exp1 < exp2, so base_val^exp1 < base_val^exp2
    
    question_text = (
        f"比較下列各組數的大小。\n"
        f"${base_latex}^{{{exp1}}} \\text{{、}} {base_latex}^{{{exp2}}}$"
    )
    answer = f"${base_latex}^{{{exp1}}} {comparison_symbol} {base_latex}^{{{exp2}}}$"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 1
    }

# ------------------------------------------------------------------------------
# Level 2 Problem Types
# ------------------------------------------------------------------------------

def generate_type_4_problem():
    """
    Level 2, Type 4: Comparing powers with different bases or larger exponents.
    """
    scenario = random.choice(['base_gt_1_exponents', 'base_lt_1_exponents', 'mixed_bases'])
    
    base1, exp1, base2, exp2 = None, None, None, None
    latex1, latex2, comparison_symbol = "", "", ""
    
    if scenario == 'base_gt_1_exponents':
        base = round(random.uniform(1.01, 1.5), 2)
        exp1 = random.randint(5, 15)
        exp2 = exp1 + random.randint(5, 15)
        latex1 = f"{base}^{{{exp1}}}"
        latex2 = f"{base}^{{{exp2}}}"
        comparison_symbol = '<' # since base > 1, higher exponent means larger value
    elif scenario == 'base_lt_1_exponents':
        base = round(random.uniform(0.5, 0.99), 2)
        exp1 = random.randint(10, 20)
        exp2 = exp1 + random.randint(10, 20)
        latex1 = f"{base}^{{{exp1}}}"
        latex2 = f"{base}^{{{exp2}}}"
        comparison_symbol = '>' # since 0 < base < 1, higher exponent means smaller value
    elif scenario == 'mixed_bases':
        base1 = round(random.uniform(1.01, 1.2), 2)
        exp1 = random.randint(8, 15)
        base2 = round(random.uniform(0.8, 0.99), 2)
        exp2 = random.randint(15, 25)
        
        latex1 = f"{base1}^{{{exp1}}}"
        latex2 = f"{base2}^{{{exp2}}}"
        
        # Calculate actual values to determine comparison symbol
        val1 = base1**exp1
        val2 = base2**exp2
        
        if val1 > val2:
            comparison_symbol = '>'
        elif val1 < val2:
            comparison_symbol = '<'
        else:
            comparison_symbol = '=' # Highly unlikely for random floats, but good practice
            
    question_text = (
        f"比較下列各組數的大小。\n"
        f"${latex1} \\text{{、}} {latex2}$"
    )
    answer = f"${latex1} {comparison_symbol} {latex2}$"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 2
    }


def generate_type_5_problem():
    """
    Level 2, Type 5: Multi-step calculation involving multiplication/division of powers of fractions.
    """
    num1 = random.randint(1, 5) * random.choice([-1, 1])
    den1 = random.randint(2, 6)
    exp1 = random.randint(2, 4)
    
    num2 = random.randint(1, 5) * random.choice([-1, 1])
    den2 = random.randint(2, 6)
    exp2 = random.randint(2, 4)
    
    op_choice = random.choice(['multiply', 'divide'])
    
    frac1_latex = f"\\left({fmt_num(num1)}/{den1}\\right)^{{{exp1}}}"
    frac2_latex = f"\\left({fmt_num(num2)}/{den2}\\right)^{{{exp2}}}"
    
    val1 = Fraction(num1, den1)**exp1
    val2 = Fraction(num2, den2)**exp2
    
    result = Fraction(0) # Initialize
    op_latex = ''
    
    if op_choice == 'multiply':
        result = val1 * val2
        op_latex = '\\times'
    else: # 'divide'
        # num2 is always 1-5, so Fraction(num2, den2) is never 0, thus val2 will never be 0.
        result = val1 / val2
        op_latex = '\\div'
        
    question_text = (
        f"計算下列各式的值。\n"
        f"${frac1_latex} {op_latex} {frac2_latex}$"
    )
    
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Level 2, Type 6: More complex multi-step calculation involving addition, multiplication, division, and powers of fractions.
    Question: Calculate (frac1^exp1 * int_val) + (frac2^exp2 / frac3^exp3)
    """
    num1 = random.randint(1, 3) * random.choice([-1, 1])
    den1 = random.randint(2, 5)
    exp1 = random.randint(2, 3)
    
    num2 = random.randint(1, 3) * random.choice([-1, 1])
    den2 = random.randint(2, 5)
    exp2 = random.randint(2, 3)
    
    num3 = random.randint(1, 3) * random.choice([-1, 1])
    den3 = random.randint(2, 5)
    exp3 = random.randint(2, 3)
    
    int_val = random.randint(2, 10)
    
    frac1_latex = f"\\left({fmt_num(num1)}/{den1}\\right)^{{{exp1}}}"
    frac2_latex = f"\\left({fmt_num(num2)}/{den2}\\right)^{{{exp2}}}"
    frac3_latex = f"\\left({fmt_num(num3)}/{den3}\\right)^{{{exp3}}}"
    
    # Calculate values using Fraction objects
    val1_term = Fraction(num1, den1)**exp1 * int_val
    
    val2_base = Fraction(num2, den2)**exp2
    val3_base = Fraction(num3, den3)**exp3
    
    # num3 is always 1-3, so Fraction(num3, den3) is never 0, thus val3_base will never be 0.
    val2_term = val2_base / val3_base
    
    result = val1_term + val2_term
    
    question_text = (
        f"計算 ${frac1_latex} \\times {int_val} + {frac2_latex} \\div {frac3_latex}$ 的值。"
    )
    
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 2
    }

# ------------------------------------------------------------------------------
# Main Dispatcher and Checker
# ------------------------------------------------------------------------------

def generate(level=1):
    """
    Generates a math problem based on the specified difficulty level.
    """
    if level == 1:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
        ]
        return random.choice(problem_types)()
    elif level == 2:
        problem_types = [
            generate_type_4_problem,
            generate_type_5_problem,
            generate_type_6_problem,
        ]
        return random.choice(problem_types)()
    else:
        raise ValueError("Invalid level. Choose 1 for Basic or 2 for Advanced.")

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization, including LaTeX fractions.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    # Try direct comparison first for exact matches, especially for comparison problems (A > B)
    if user == correct:
        return {"correct": True, "result": "正確！"}
        
    # Attempt numerical comparison for calculation problems
    try:
        # Helper to convert a string (number, fraction, or LaTeX fraction) to a float
        def to_float_from_str(s):
            # Handle LaTeX fraction format: \frac{num}{den}
            if s.startswith('-\\frac{'):
                parts = s[len('-\\frac{'):-1].split('}{')
                return float(-Fraction(int(parts[0]), int(parts[1])))
            elif s.startswith('\\frac{'):
                parts = s[len('\\frac{'):-1].split('}{')
                return float(Fraction(int(parts[0]), int(parts[1])))
            # Handle standard fraction format: num/den (e.g., "1/2", "-3/4")
            elif '/' in s and s.count('/') == 1 and all(p.isdigit() or (p.startswith('-') and p[1:].isdigit()) for p in s.split('/')):
                return float(Fraction(s))
            # Handle integers and decimals (e.g., "5", "0.5", "-2.3")
            else:
                return float(s)

        user_float = to_float_from_str(user)
        correct_float = to_float_from_str(correct)
        
        if abs(user_float - correct_float) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except (ValueError, TypeError, ZeroDivisionError):
        # If conversion to float fails for either user or correct answer,
        # or if it's not a numerical answer (e.g., "□皆為5", "A < B"),
        # then it's not a numerical comparison case.
        pass
        
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
