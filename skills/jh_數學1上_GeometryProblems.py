# ==============================================================================
# ID: jh_數學1上_GeometryProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 32.95s | RAG: 2 examples
# Created At: 2026-01-09 22:56:24
# Fix Status: [Clean Pass]
#==============================================================================


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

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

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





# (Helpers are auto-injected here, do not write them)

def generate_type_1_basic_problem():
    """
    Generates a basic Level 1 geometry problem: area of a rectangle.
    This type is invented to satisfy the Level 1 completeness requirement.
    """
    length = random.randint(5, 15)
    width = random.randint(3, 10)
    area = length * width

    question_text = f"已知長方形的長為 ${length}$ 公分，寬為 ${width}$ 公分，請問此長方形的面積為多少平方公分？"
    correct_answer = str(area)
    return {'question_text': question_text, 'answer': correct_answer, 'correct_answer': correct_answer}

def generate_type_1_problem():
    """
    Generates a Type 1 problem (Area of an embedded triangle in a rectangle) for Level 2,
    based on Example 1 from the Architect's Spec.
    """
    # Variables as per spec
    bc_len_ans = random.randint(2, 8)  # The unknown length, BC
    ab_len = random.randint(3, 10)
    cd_len = random.randint(3, 10)
    de_len = random.randint(3, 10)

    # Constraint 1: `2 * af_len - cd_len - de_len` must be positive.
    # This implies `af_len > (cd_len + de_len) / 2`.
    # Also, `af_len` must be between 8 and 15 (inclusive).
    min_af_len_derived = (cd_len + de_len) // 2 + 1
    min_af_len = max(8, min_af_len_derived)
    af_len = random.randint(min_af_len, 15)

    # Constraint 2: `(ab_len * af_len + bc_len_ans * (2 * af_len - cd_len - de_len) - de_len * ab_len)`
    # must be even to ensure `area_bdf` is an integer. This expression is `2 * area_bdf`.
    while True:
        expression_for_2_area_bdf = (
            ab_len * af_len +
            bc_len_ans * (2 * af_len - cd_len - de_len) -
            de_len * ab_len
        )
        if expression_for_2_area_bdf % 2 == 0:
            break
        # If not even, re-roll af_len within its valid range
        af_len = random.randint(min_af_len, 15)

    # Calculations for `area_bdf` as per spec
    ac_len = ab_len + bc_len_ans
    area_acef = ac_len * af_len
    area_abf = 0.5 * ab_len * af_len
    area_bcd = 0.5 * bc_len_ans * cd_len
    area_def = 0.5 * de_len * ac_len  # EF = AC
    
    area_bdf = int(area_acef - area_abf - area_bcd - area_def)

    question_text = (
        f"如右圖，四邊形 ACEF 為長方形，已知三角形 BDF 的面積為 ${area_bdf}$，"
        f"則 BC 線段的長度為多少？(圖中 AF=${af_len}$, AB=${ab_len}$, CD=${cd_len}$, DE=${de_len}$)"
    )
    correct_answer = str(bc_len_ans)
    return {'question_text': question_text, 'answer': correct_answer, 'correct_answer': correct_answer}


def generate_type_2_problem():
    """
    Generates a Type 2 problem (Trapezoid area word problem) for Level 2,
    based on Example 2 from the Architect's Spec.
    """
    # Variables as per spec
    u_ans = random.randint(4, 10)  # The upper base, which is the answer
    m = random.choice([2, 3, 4])   # Multiplier for the upper base
    
    # `k` must ensure `l_val > 0`, so `k` must be less than `m * u_ans`.
    k = random.randint(1, m * u_ans - 1)
    l_val = m * u_ans - k  # Calculated lower base

    h_val = random.randint(5, 12)  # Height of the trapezoid

    # Constraint: `(u_ans + l_val) * h_val` must be even to ensure `area_val` is an integer.
    while ((u_ans + l_val) * h_val) % 2 != 0:
        h_val = random.randint(5, 12)  # Re-roll `h_val` until condition met

    area_val = int(0.5 * (u_ans + l_val) * h_val)

    question_text = (
        f"已知梯形下底比上底的 ${m}$ 倍少 ${k}$ 公分，"
        f"若此梯形的高為 ${h_val}$ 公分，面積為 ${area_val}$ 平方公分，"
        f"則此梯形的上底為多少公分？"
    )
    # The spec explicitly includes "公分" in the answer for this type
    correct_answer = f"{u_ans} 公分" 
    return {'question_text': question_text, 'answer': correct_answer, 'correct_answer': correct_answer}


def generate(level=1):
    """
    Generates a math problem based on the specified difficulty level for
    the jh_數學1上_GeometryProblems skill.

    Args:
        level (int): The difficulty level (1 for Basic, 2 for Advanced).

    Returns:
        dict: A dictionary containing 'question_text', 'answer', and 'correct_answer'.
    """
    if level == 1:
        # Implemented a basic rectangle area problem for Level 1 as per completeness rule.
        return generate_type_1_basic_problem()
    elif level == 2:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem,
        ]
        return random.choice(problem_types)()
    else:
        # Handle invalid level input as per spec
        raise ValueError("Invalid level. Please choose 1 or 2.")

