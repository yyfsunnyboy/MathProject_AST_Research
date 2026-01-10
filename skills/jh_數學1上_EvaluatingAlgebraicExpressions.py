# ==============================================================================
# ID: jh_數學1上_EvaluatingAlgebraicExpressions
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 40.21s | RAG: 3 examples
# Created At: 2026-01-09 22:55:51
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

def generate_type_1_problem():
    """
    Generates a Level 1 problem: Evaluate a linear algebraic expression.
    Concept: Evaluate a given algebraic expression for a specific numerical value (integer, decimal, or fraction).
             The expressions are linear with one variable.
    """
    # Ensure x_val is not always 0 or 1, and covers different types (int, float, Fraction)
    x_val_choices = [random.randint(-5, 5) for _ in range(3)] + \
                    [round(random.uniform(-3, 3), 1) for _ in range(3)] + \
                    [get_random_fraction(-2, 2, denominator_limit=5) for _ in range(3)]
    # Filter out 0 to reduce trivial cases, but allow it to occur occasionally if needed
    x_val = random.choice([val for val in x_val_choices if val != 0] + [0]) # Allow 0 occasionally
    
    # Coefficient 'a' for x, ensuring it's not zero
    coeff_a = random.choice([Fraction(random.randint(-10, 10), 1), get_random_fraction(-5, 5, denominator_limit=5)])
    while coeff_a == 0:
        coeff_a = random.choice([Fraction(random.randint(-10, 10), 1), get_random_fraction(-5, 5, denominator_limit=5)])

    # Constant term 'b'
    const_b = random.choice([Fraction(random.randint(-15, 15), 1), get_random_fraction(-10, 10, denominator_limit=5)])
    
    # Randomly choose one of three expression forms
    expression_type = random.choice(["ax", "ax_plus_b", "b_minus_ax"])
    
    expression_str = ""
    correct_answer_val = None

    # Convert all numerical values to Fraction for consistent arithmetic
    # The Fraction constructor handles int, float, and existing Fraction objects correctly.
    x_val_frac = Fraction(x_val)
    coeff_a_frac = Fraction(coeff_a)
    const_b_frac = Fraction(const_b)

    if expression_type == "ax":
        # Question format: $ax$
        expression_str = f"{fmt_num(coeff_a_frac)}x"
        correct_answer_val = coeff_a_frac * x_val_frac
    elif expression_type == "ax_plus_b":
        # Question format: $ax + b$
        # Following spec's template directly, assuming fmt_num handles signs for display.
        expression_str = f"{fmt_num(coeff_a_frac)}x + {fmt_num(const_b_frac)}"
        correct_answer_val = coeff_a_frac * x_val_frac + const_b_frac
    elif expression_type == "b_minus_ax":
        # Question format: $b - ax$
        # Following spec's template directly, assuming fmt_num handles signs for display.
        expression_str = f"{fmt_num(const_b_frac)} - {fmt_num(coeff_a_frac)}x"
        correct_answer_val = const_b_frac - coeff_a_frac * x_val_frac
            
    # Construct the question text in Traditional Chinese
    question_text = f"當 $x={fmt_num(x_val)}$ 時，求代數式 ${expression_str}$ 的值。"
    
    # Format the correct answer using to_latex (no $ signs in answer)
    correct_answer_str = to_latex(correct_answer_val)
    
    return {'question_text': question_text, 'answer': correct_answer_str, 'correct_answer': correct_answer_str}

def generate_type_2_problem():
    """
    Generates a Level 2 problem: Word problem with single algebraic expression evaluation.
    Concept: Solve a word problem by evaluating a given algebraic expression for a single specific value.
    """
    item_name_zh = random.choice(["T恤", "洋裝", "牛仔褲", "夾克"])
    original_price_x = random.choice([100, 150, 200, 250, 300, 400, 500])
    coeff_frac = random.choice([Fraction(1,2), Fraction(2,3), Fraction(3,4), Fraction(3,5), Fraction(4,5)])
    discount_const = random.randint(1, 20)
    currency_zh = random.choice(["元", "歐元", "日圓"])

    # Calculate the price. The result will be a Fraction because of coeff_frac.
    calculated_price = (coeff_frac * original_price_x) - discount_const
    
    # Construct the question text in Traditional Chinese
    question_text = (
        f"某商店販售的{item_name_zh}，其售價為 $(\\frac{{{coeff_frac.numerator}}}{{{coeff_frac.denominator}}}x - {discount_const})$ {currency_zh}，"
        f"其中 $x$ 為原價。若一件{item_name_zh}的原價是 ${original_price_x}$ {currency_zh}，"
        f"請問它的售價是多少？"
    )
    
    # Format the answer, including the currency unit (no $ signs in answer)
    correct_answer_str = f"{to_latex(calculated_price)} {currency_zh}"
    
    return {'question_text': question_text, 'answer': correct_answer_str, 'correct_answer': correct_answer_str}

def generate_type_3_problem():
    """
    Generates a Level 2 problem: Word problem with multiple algebraic expression evaluations.
    Concept: Solve a word problem by evaluating a given algebraic expression for two different specific values.
    """
    person_names_zh = random.sample(["約翰", "麥克", "莎拉", "艾蜜莉", "大衛", "安娜"], 2)
    person_name1_zh, person_name2_zh = person_names_zh[0], person_names_zh[1]
    
    # Two distinct heights
    heights = random.sample(range(160, 195), 2) 
    height_x1, height_x2 = heights[0], heights[1]
    
    const_sub = random.choice([70, 75, 80])
    coeff_dec = random.choice([0.6, 0.65, 0.7, 0.75])
    unit_result_zh = random.choice(["公斤", "磅"]) # Unit for the calculated measurement (e.g., weight)
    measurement_type_zh = random.choice(["標準體重", "理想體重"])

    # Calculate answers for both individuals
    answer1 = (height_x1 - const_sub) * coeff_dec
    answer2 = (height_x2 - const_sub) * coeff_dec
    
    # Format answers to 1 decimal place as specified, then convert to LaTeX string
    answer1_formatted = round(answer1, 1)
    answer2_formatted = round(answer2, 1)

    # Construct the question text in Traditional Chinese
    question_text = (
        f"{measurement_type_zh}的計算公式為 $(x - {const_sub}) \\times {coeff_dec}$ {unit_result_zh}，"
        f"其中 $x$ 為身高（公分）。若{person_name1_zh}的身高是 ${height_x1}$ 公分，且"
        f"{person_name2_zh}的身高是 ${height_x2}$ 公分，請問他們的{measurement_type_zh}分別是多少？"
    )
    
    # Format the answer string (no $ signs in answer)
    correct_answer_str = (
        f"{person_name1_zh}: {to_latex(answer1_formatted)} {unit_result_zh}, "
        f"{person_name2_zh}: {to_latex(answer2_formatted)} {unit_result_zh}"
    )
    
    return {'question_text': question_text, 'answer': correct_answer_str, 'correct_answer': correct_answer_str}

def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        # Level 1 problems are based on Type 1 (Direct Evaluation)
        return generate_type_1_problem()
    elif level == 2:
        # Level 2 problems are based on Type 2 (Word Problem - Single Evaluation)
        # and Type 3 (Word Problem - Multiple Evaluations)
        return random.choice([generate_type_2_problem, generate_type_3_problem])()
    else:
        raise ValueError("Invalid level. Level must be 1 or 2.")

