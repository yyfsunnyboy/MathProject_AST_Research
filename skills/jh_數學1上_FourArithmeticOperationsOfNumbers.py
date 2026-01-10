# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 42.83s | RAG: 4 examples
# Created At: 2026-01-09 14:07:32
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
# 4. RETURN: Must return dict with 'question_text', 'answer', 'correct_answer'.
# ==============================================================================


# Problem Type Implementations
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Direct calculation of arithmetic expressions involving fractions,
    decimals, mixed numbers, negative numbers, and order of operations,
    including the distributive property.
    """
    difficulty = 1

    # Part A (Order of operations)
    # a / b * c - d
    a_num = random.randint(-10, 10)
    a_den = random.randint(1, 10)
    a = Fraction(a_num, a_den)

    b = 0.0
    while abs(b) < 0.1 or abs(b) > 5: # Ensure b is not too close to zero and within reasonable range
        b = random.uniform(-5, 5)
    
    c_num = random.randint(-10, 10)
    c_den = random.randint(1, 10)
    c = Fraction(c_num, c_den)
    
    d_num = random.randint(-10, 10)
    d_den = random.randint(1, 10)
    d = Fraction(d_num, d_den)

    q_a = f"⑴ ${to_latex(a)} \\div ({fmt_num(b)}) \\times {to_latex(c)} - {to_latex(d)}$"
    ans_a_val = a / Fraction(b) * c - d
    ans_a = to_latex(ans_a_val)

    # Part B (Distributive property)
    # mixed1 * common_factor - mixed2 * common_factor
    m_int1 = random.randint(1, 5)
    m_num1 = random.randint(1, 10)
    m_den1 = random.randint(m_num1 + 1, 15)
    mixed1 = Fraction(m_int1 * m_den1 + m_num1, m_den1)

    m_int2 = random.randint(1, 5)
    m_num2 = random.randint(1, 10)
    m_den2 = random.randint(m_num2 + 1, 15)
    mixed2 = Fraction(m_int2 * m_den2 + m_num2, m_den2)

    common_factor = random.choice([-1, 1]) * random.randint(10, 100)

    q_b = f"⑵ ${to_latex(mixed1)} \\times ({fmt_num(common_factor)}) - {to_latex(mixed2)} \\times ({fmt_num(common_factor)})$"
    ans_b_val = (mixed1 - mixed2) * common_factor
    ans_b = to_latex(ans_b_val)

    question_text = f"計算下列各式的值。\n{q_a}\n{q_b}"
    answer = f"⑴ {ans_a} ⑵ {ans_b}"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": difficulty
    }

def generate_type_2_problem():
    """
    Level 1: Direct calculation of arithmetic expressions involving fractions,
    decimals, mixed numbers, negative numbers, and order of operations with
    parentheses, including the distributive property.
    """
    difficulty = 1

    # Part A (Parentheses and mixed operations)
    # a * (b + c) / d
    a_num = random.randint(-10, 10)
    a_den = random.randint(1, 10)
    a = Fraction(a_num, a_den)

    b_num = random.randint(-10, 10)
    b_den = random.randint(1, 10)
    b = Fraction(b_num, b_den)

    c = random.uniform(0.5, 3.0) # e.g., 1.5
    
    # Ensure d is not zero
    d_num = random.choice([x for x in range(-10, 11) if x != 0])
    d_den = random.randint(1, 10)
    d = Fraction(d_num, d_den)

    q_a = f"⑴ $({to_latex(a)}) \\times ({to_latex(b)} + {c}) \\div ({to_latex(d)})$"
    ans_a_val = a * (b + Fraction(c)) / d
    ans_a = to_latex(ans_a_val)

    # Part B (Distributive property)
    # mixed * factor1 + mixed * factor2
    m_int = random.randint(1, 10)
    m_num = random.randint(1, 10)
    m_den = random.randint(m_num + 1, 15)
    mixed = Fraction(m_int * m_den + m_num, m_den)

    factor1 = random.randint(100, 300)
    factor2 = random.randint(-50, 50)

    q_b = f"⑵ ${to_latex(mixed)} \\times {factor1} + {to_latex(mixed)} \\times ({fmt_num(factor2)})$"
    ans_b_val = mixed * (factor1 + factor2)
    ans_b = to_latex(ans_b_val)

    question_text = f"計算下列各式的值。\n{q_a}\n{q_b}"
    answer = f"⑴ {ans_a} ⑵ {ans_b}"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": difficulty
    }

def generate_type_3_problem():
    """
    Level 2: Multi-step word problem involving rates, total quantity,
    partial usage, and solving for an initial unknown weight (e.g., drone's empty weight).
    """
    difficulty = 2

    drone_empty_weight = random.randint(20, 35) # kg
    total_spray_minutes = random.choice([40, 50, 60, 80, 100]) # minutes
    
    # Ensure pesticide_per_minute is a clean number (integer or simple decimal)
    # by making total_pesticide_weight a multiple of total_spray_minutes.
    # pesticide_base_rate can be 0.5, 1, 1.5, 2 kg/min
    pesticide_base_rate_choices = [Fraction(1,2), Fraction(1), Fraction(3,2), Fraction(2)]
    pesticide_base_rate = random.choice(pesticide_base_rate_choices)

    total_pesticide_weight = int(pesticide_base_rate * total_spray_minutes) # kg (ensured integer)

    initial_total_weight = drone_empty_weight + total_pesticide_weight # kg

    partial_spray_minutes = random.randint(10, total_spray_minutes - 10) # minutes

    pesticide_sprayed_partial = pesticide_base_rate * partial_spray_minutes
    remaining_pesticide = total_pesticide_weight - pesticide_sprayed_partial
    combined_weight_after_partial = drone_empty_weight + remaining_pesticide

    question_text = (
        f"一臺農用無人機裝滿農藥的重量為 {initial_total_weight} 公斤，"
        f"若每分鐘噴灑的農藥重量皆相等，噴灑飛行 {total_spray_minutes} 分鐘後，"
        f"可將農藥噴完沒有剩下。某次此無人機裝滿農藥噴灑飛行 {partial_spray_minutes} 分鐘後，"
        f"無人機與剩餘農藥重量為 {int(combined_weight_after_partial)} 公斤，"
        f"則此無人機未裝農藥時的重量為多少公斤？"
    )
    answer = str(int(drone_empty_weight))

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": difficulty
    }

def generate_type_4_problem():
    """
    Level 2: Multi-step word problem involving fractions of an unknown quantity
    (juice) and solving for another unknown (empty bottle weight).
    """
    difficulty = 2

    bottle_weight = random.randint(150, 250) # g
    denominator_consumed = random.randint(3, 5) # e.g., 3, 4, 5
    numerator_consumed = random.randint(1, denominator_consumed - 1)
    
    # Ensure total_juice_weight is a multiple of denominator_consumed
    total_juice_weight_base = random.randint(100, 200)
    total_juice_weight = total_juice_weight_base * denominator_consumed # g

    initial_total_weight = bottle_weight + total_juice_weight # g

    fraction_consumed = Fraction(numerator_consumed, denominator_consumed)
    juice_consumed_weight = total_juice_weight * fraction_consumed
    
    remaining_total_weight = initial_total_weight - juice_consumed_weight # g

    question_text = (
        f"有一瓶果汁，連瓶子共重 {initial_total_weight} 公克，"
        f"喝了 ${to_latex(Fraction(numerator_consumed, denominator_consumed))}$ 瓶的果汁後，"
        f"剩餘的果汁連瓶子共重 {int(remaining_total_weight)} 公克，"
        f"求空瓶子重多少公克？"
    )
    answer = str(int(bottle_weight))

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": difficulty
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        problem_type = random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
        ])
    elif level == 2:
        problem_type = random.choice([
            generate_type_3_problem,
            generate_type_4_problem,
        ])
    else:
        raise ValueError("Invalid level. Choose 1 or 2.")
    
    return problem_type()

# ==============================================================================
# Standard Answer Checker
# ==============================================================================

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    # Try direct string comparison first (for formatted fraction answers)
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    try:
        # Attempt to convert to float for numerical comparison
        # This is useful for simple integer/decimal answers.
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # If conversion to float fails, it's not a simple numerical string.

    # For fraction answers (e.g., "1/2" or "\frac{1}{2}"), try converting to Fraction objects for comparison
    try:
        # Normalize LaTeX fraction to standard fraction string for Fraction() constructor
        normalized_user = user.replace('\\frac{', '').replace('}{', '/').replace('}', '')
        normalized_correct = correct.replace('\\frac{', '').replace('}{', '/').replace('}', '')
        
        user_fraction = Fraction(normalized_user)
        correct_fraction = Fraction(normalized_correct)
        if user_fraction == correct_fraction:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # If conversion to Fraction fails

    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}
