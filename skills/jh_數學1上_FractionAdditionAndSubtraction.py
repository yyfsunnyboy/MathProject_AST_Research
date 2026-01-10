# ==============================================================================
# ID: jh_數學1上_FractionAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 65.69s | RAG: 8 examples
# Created At: 2026-01-09 14:08:37
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


# Problem Generation Functions
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Addition/Subtraction of two fractions with the same denominator.
    Numerators can be negative.
    """
    den = random.randint(2, 15)
    num1 = random.randint(-15, 15)
    num2 = random.randint(-15, 15)
    op = random.choice(['+', '-'])

    f1 = Fraction(num1, den)
    f2 = Fraction(num2, den)
    result_frac = f1 + f2 if op == '+' else f1 - f2
    
    # Ensure result is not trivial (e.g., 0)
    while result_frac == 0:
        num1 = random.randint(-15, 15)
        num2 = random.randint(-15, 15)
        f1 = Fraction(num1, den)
        f2 = Fraction(num2, den)
        result_frac = f1 + f2 if op == '+' else f1 - f2
    
    question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den}}} {op} \\frac{{{fmt_num(num2)}}}{{{den}}}$"
    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1: Addition/Subtraction of two fractions with the same denominator,
    often involving mixed signs.
    """
    den = random.randint(2, 15)
    num1 = random.randint(-15, 15)
    num2 = random.randint(1, 15) # Positive numerator for second fraction
    op = random.choice(['+', '-'])
    
    # To create mixed sign scenarios, ensure at least one negative numerator
    # or a subtraction that creates a negative numerator interaction.
    # If num1 is positive, make it negative 50% of the time to ensure mixed signs.
    if num1 >= 0 and random.choice([True, False]):
        num1 = -num1

    f1 = Fraction(num1, den)
    f2 = Fraction(num2, den)
    result_frac = f1 + f2 if op == '+' else f1 - f2
    
    # Avoid trivial cases like 0
    while result_frac == 0:
        num1 = random.randint(-15, 15)
        num2 = random.randint(1, 15)
        if num1 >= 0 and random.choice([True, False]):
            num1 = -num1
        f1 = Fraction(num1, den)
        f2 = Fraction(num2, den)
        result_frac = f1 + f2 if op == '+' else f1 - f2

    question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den}}} {op} \\frac{{{num2}}}{{{den}}}$"
    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 2: Addition/Subtraction of two or three fractions with different denominators.
    """
    num_terms = random.choice([2, 3])
    
    den1 = random.randint(2, 12)
    den2 = random.randint(2, 12)
    while den1 == den2: den2 = random.randint(2, 12) # Ensure distinct denominators
    
    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)
    
    op1 = random.choice(['+', '-'])
    
    f1 = Fraction(num1, den1)
    f2 = Fraction(num2, den2)
    
    if num_terms == 2:
        question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op1} \\frac{{{fmt_num(num2)}}}{{{den2}}}$"
        result_frac = f1 + f2 if op1 == '+' else f1 - f2
    else: # num_terms == 3
        den3 = random.randint(2, 12)
        # Ensure den3 is distinct from den1 and den2
        while den3 in [den1, den2]: den3 = random.randint(2, 12)
        num3 = random.randint(-10, 10)
        op2 = random.choice(['+', '-'])
        
        f3 = Fraction(num3, den3)
        
        question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op1} \\frac{{{fmt_num(num2)}}}{{{den2}}} {op2} \\frac{{{fmt_num(num3)}}}{{{den3}}}$"
        
        result_frac = f1 + f2 if op1 == '+' else f1 - f2
        result_frac = result_frac + f3 if op2 == '+' else result_frac - f3
    
    # Avoid trivial zero results
    # Regenerate numerators if result is zero
    while result_frac == 0:
        num1 = random.randint(-10, 10)
        num2 = random.randint(-10, 10)
        f1 = Fraction(num1, den1)
        f2 = Fraction(num2, den2)
        if num_terms == 2:
            result_frac = f1 + f2 if op1 == '+' else f1 - f2
        else:
            num3 = random.randint(-10, 10)
            f3 = Fraction(num3, den3)
            result_frac = f1 + f2 if op1 == '+' else f1 - f2
            result_frac = result_frac + f3 if op2 == '+' else result_frac - f3

    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

def generate_type_4_problem():
    """
    Level 2: Addition/Subtraction of fractions with different denominators,
    often with one denominator being a multiple of another.
    """
    num_terms = random.choice([2, 3])
    
    den1_base = random.randint(2, 10)
    multiplier = random.randint(2, 4)
    den1 = den1_base
    den2 = den1_base * multiplier # den2 is a multiple of den1
    
    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)
    
    op1 = random.choice(['+', '-'])
    
    f1 = Fraction(num1, den1)
    f2 = Fraction(num2, den2)

    if num_terms == 2:
        question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op1} \\frac{{{fmt_num(num2)}}}{{{den2}}}$"
        result_frac = f1 + f2 if op1 == '+' else f1 - f2
    else: # num_terms == 3
        den3 = random.randint(2, 10)
        # Ensure den3 is not den1 or den2, and LCM isn't too large
        # Chaining math.lcm for three arguments:
        while den3 in [den1, den2] or math.lcm(den1, math.lcm(den2, den3)) > 100:
             den3 = random.randint(2, 10)
        num3 = random.randint(-10, 10)
        op2 = random.choice(['+', '-'])
        
        f3 = Fraction(num3, den3)
        
        question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op1} \\frac{{{fmt_num(num2)}}}{{{den2}}} {op2} \\frac{{{fmt_num(num3)}}}{{{den3}}}$"
        
        result_frac = f1 + f2 if op1 == '+' else f1 - f2
        result_frac = result_frac + f3 if op2 == '+' else result_frac - f3
    
    # Avoid trivial zero results
    while result_frac == 0:
        num1 = random.randint(-10, 10)
        num2 = random.randint(-10, 10)
        f1 = Fraction(num1, den1)
        f2 = Fraction(num2, den2)
        if num_terms == 2:
            result_frac = f1 + f2 if op1 == '+' else f1 - f2
        else:
            num3 = random.randint(-10, 10)
            f3 = Fraction(num3, den3)
            result_frac = f1 + f2 if op1 == '+' else f1 - f2
            result_frac = result_frac + f3 if op2 == '+' else result_frac - f3

    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

def generate_type_5_problem():
    """
    Level 2: Fractions with parentheses, requiring order of operations.
    """
    den1 = random.randint(2, 15)
    den2 = random.randint(2, 15)
    den3 = random.randint(2, 15)
    
    # Ensure denominators are reasonably distinct and LCM is manageable
    while (len(set([den1, den2, den3])) < 3 or 
           math.lcm(den1, math.lcm(den2, den3)) > 150):
        den1 = random.randint(2, 15)
        den2 = random.randint(2, 15)
        den3 = random.randint(2, 15)

    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)
    num3 = random.randint(-10, 10)
    
    op_outer = random.choice(['+', '-'])
    op_inner = random.choice(['+', '-'])
    
    # Structure: A op_outer (B op_inner C)
    question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op_outer} (\\frac{{{fmt_num(num2)}}}{{{den2}}} {op_inner} \\frac{{{fmt_num(num3)}}}{{{den3}}})$"
    
    f1 = Fraction(num1, den1)
    f2 = Fraction(num2, den2)
    f3 = Fraction(num3, den3)
    
    inner_result = f2 + f3 if op_inner == '+' else f2 - f3
    final_result = f1 + inner_result if op_outer == '+' else f1 - inner_result
    
    # Avoid trivial zero results
    while final_result == 0:
        num1 = random.randint(-10, 10)
        num2 = random.randint(-10, 10)
        num3 = random.randint(-10, 10)
        f1 = Fraction(num1, den1)
        f2 = Fraction(num2, den2)
        f3 = Fraction(num3, den3)
        inner_result = f2 + f3 if op_inner == '+' else f2 - f3
        final_result = f1 + inner_result if op_outer == '+' else f1 - inner_result

    answer_latex = to_latex(final_result)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Level 2: Fractions with parentheses, potentially larger denominators,
    or strategic cancellation/grouping.
    """
    den1 = random.randint(10, 30)
    den2 = random.randint(10, 30)
    den3 = random.randint(10, 30)
    
    # Ensure distinct and manageable LCM
    # LCM of three numbers can be large, set a reasonable cap.
    # Also ensure denominators are distinct.
    while (len(set([den1, den2, den3])) < 3 or
           math.lcm(den1, math.lcm(den2, den3)) > 500):
        den1 = random.randint(10, 30)
        den2 = random.randint(10, 30)
        den3 = random.randint(10, 30)

    num1 = random.randint(-20, 20)
    num2 = random.randint(-20, 20)
    num3 = random.randint(-20, 20)
    
    op_outer = random.choice(['+', '-'])
    op_inner = random.choice(['+', '-'])
    
    question_text = f"計算下列各式的值。\n$\\frac{{{fmt_num(num1)}}}{{{den1}}} {op_outer} (\\frac{{{fmt_num(num2)}}}{{{den2}}} {op_inner} \\frac{{{fmt_num(num3)}}}{{{den3}}})$"
    
    f1 = Fraction(num1, den1)
    f2 = Fraction(num2, den2)
    f3 = Fraction(num3, den3)
    
    inner_result = f2 + f3 if op_inner == '+' else f2 - f3
    final_result = f1 + inner_result if op_outer == '+' else f1 - inner_result

    # Avoid trivial zero results
    while final_result == 0:
        num1 = random.randint(-20, 20)
        num2 = random.randint(-20, 20)
        num3 = random.randint(-20, 20)
        f1 = Fraction(num1, den1)
        f2 = Fraction(num2, den2)
        f3 = Fraction(num3, den3)
        inner_result = f2 + f3 if op_inner == '+' else f2 - f3
        final_result = f1 + inner_result if op_outer == '+' else f1 - inner_result
        
    answer_latex = to_latex(final_result)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

def generate_type_7_problem():
    """
    Level 2: Addition/Subtraction of two mixed numbers.
    """
    int1 = random.randint(-5, 5)
    num1 = random.randint(1, 5)
    den1 = random.randint(2, 7)
    
    int2 = random.randint(-5, 5)
    num2 = random.randint(1, 5)
    den2 = random.randint(2, 7)
    
    # Ensure proper fractional parts (num < den)
    while num1 >= den1: num1 = random.randint(1, 5)
    while num2 >= den2: num2 = random.randint(1, 5)

    # Ensure different denominators for proper challenge
    while den1 == den2: den2 = random.randint(2, 7) 
    
    # Avoid trivial integer parts (both zero)
    while int1 == 0 and int2 == 0:
        int1 = random.randint(-5, 5)
        int2 = random.randint(-5, 5)
    
    op = random.choice(['+', '-'])
    
    # Construct fraction objects from mixed numbers
    # For a mixed number like -2 3/4, it's -(2 + 3/4) = -11/4
    f1_improper = Fraction(abs(int1) * den1 + num1, den1)
    f1 = -f1_improper if int1 < 0 else f1_improper
    
    f2_improper = Fraction(abs(int2) * den2 + num2, den2)
    f2 = -f2_improper if int2 < 0 else f2_improper
    
    result_frac = f1 + f2 if op == '+' else f1 - f2

    # Avoid trivial zero results
    while result_frac == 0:
        int1 = random.randint(-5, 5)
        num1 = random.randint(1, 5)
        den1 = random.randint(2, 7)
        int2 = random.randint(-5, 5)
        num2 = random.randint(1, 5)
        den2 = random.randint(2, 7)

        while num1 >= den1: num1 = random.randint(1, 5)
        while num2 >= den2: num2 = random.randint(1, 5)
        while den1 == den2: den2 = random.randint(2, 7)
        while int1 == 0 and int2 == 0:
            int1 = random.randint(-5, 5)
            int2 = random.randint(-5, 5)

        f1_improper = Fraction(abs(int1) * den1 + num1, den1)
        f1 = -f1_improper if int1 < 0 else f1_improper
        f2_improper = Fraction(abs(int2) * den2 + num2, den2)
        f2 = -f2_improper if int2 < 0 else f2_improper
        result_frac = f1 + f2 if op == '+' else f1 - f2
    
    question_text = f"計算 ${fmt_num(int1)} \\frac{{{num1}}}{{{den1}}} {op} {fmt_num(int2)} \\frac{{{num2}}}{{{den2}}}$ 的值。"
    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

def generate_type_8_problem():
    """
    Level 2: Addition/Subtraction of three mixed numbers.
    """
    int1 = random.randint(-3, 3)
    num1 = random.randint(1, 4)
    den1 = random.randint(2, 6)
    
    int2 = random.randint(-3, 3)
    num2 = random.randint(1, 4)
    den2 = random.randint(2, 6)
    
    int3 = random.randint(-3, 3)
    num3 = random.randint(1, 4)
    den3 = random.randint(2, 6)
    
    # Ensure proper fractional parts (num < den)
    while num1 >= den1: num1 = random.randint(1, 4)
    while num2 >= den2: num2 = random.randint(1, 4)
    while num3 >= den3: num3 = random.randint(1, 4)

    # Ensure distinct denominators and not all integer parts are zero
    denominators = [den1, den2, den3]
    while len(set(denominators)) < 3 or all(i == 0 for i in [int1, int2, int3]):
        den1 = random.randint(2, 6)
        den2 = random.randint(2, 6)
        den3 = random.randint(2, 6)
        int1 = random.randint(-3, 3)
        int2 = random.randint(-3, 3)
        int3 = random.randint(-3, 3)
        num1 = random.randint(1, 4)
        num2 = random.randint(1, 4)
        num3 = random.randint(1, 4)
        while num1 >= den1: num1 = random.randint(1, 4)
        while num2 >= den2: num2 = random.randint(1, 4)
        while num3 >= den3: num3 = random.randint(1, 4)
        denominators = [den1, den2, den3]

    op1 = random.choice(['+', '-'])
    op2 = random.choice(['+', '-'])
    
    # Convert mixed numbers to fractions
    f1_improper = Fraction(abs(int1) * den1 + num1, den1)
    f1 = -f1_improper if int1 < 0 else f1_improper
    
    f2_improper = Fraction(abs(int2) * den2 + num2, den2)
    f2 = -f2_improper if int2 < 0 else f2_improper
    
    f3_improper = Fraction(abs(int3) * den3 + num3, den3)
    f3 = -f3_improper if int3 < 0 else f3_improper
    
    result_frac = f1 + f2 if op1 == '+' else f1 - f2
    result_frac = result_frac + f3 if op2 == '+' else result_frac - f3

    # Avoid trivial zero results
    while result_frac == 0:
        int1 = random.randint(-3, 3)
        num1 = random.randint(1, 4)
        den1 = random.randint(2, 6)
        int2 = random.randint(-3, 3)
        num2 = random.randint(1, 4)
        den2 = random.randint(2, 6)
        int3 = random.randint(-3, 3)
        num3 = random.randint(1, 4)
        den3 = random.randint(2, 6)

        while num1 >= den1: num1 = random.randint(1, 4)
        while num2 >= den2: num2 = random.randint(1, 4)
        while num3 >= den3: num3 = random.randint(1, 4)
        denominators = [den1, den2, den3]
        while len(set(denominators)) < 3 or all(i == 0 for i in [int1, int2, int3]):
            den1 = random.randint(2, 6)
            den2 = random.randint(2, 6)
            den3 = random.randint(2, 6)
            int1 = random.randint(-3, 3)
            int2 = random.randint(-3, 3)
            int3 = random.randint(-3, 3)
            num1 = random.randint(1, 4)
            num2 = random.randint(1, 4)
            num3 = random.randint(1, 4)
            while num1 >= den1: num1 = random.randint(1, 4)
            while num2 >= den2: num2 = random.randint(1, 4)
            while num3 >= den3: num3 = random.randint(1, 4)
            denominators = [den1, den2, den3]

        f1_improper = Fraction(abs(int1) * den1 + num1, den1)
        f1 = -f1_improper if int1 < 0 else f1_improper
        f2_improper = Fraction(abs(int2) * den2 + num2, den2)
        f2 = -f2_improper if int2 < 0 else f2_improper
        f3_improper = Fraction(abs(int3) * den3 + num3, den3)
        f3 = -f3_improper if int3 < 0 else f3_improper
        result_frac = f1 + f2 if op1 == '+' else f1 - f2
        result_frac = result_frac + f3 if op2 == '+' else result_frac - f3

    question_text = f"計算下列各式的值。\n$({fmt_num(int1)} \\frac{{{num1}}}{{{den1}}}) {op1} ({fmt_num(int2)} \\frac{{{num2}}}{{{den2}}}) {op2} ({fmt_num(int3)} \\frac{{{num3}}}{{{den3}}})$"
    answer_latex = to_latex(result_frac)
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": answer_latex,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher for jh_數學1上_FractionAdditionAndSubtraction skill.
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        problem_type = random.choice([
            'type_1_basic_same_den',
            'type_2_mixed_sign_same_den'
        ])
        
        if problem_type == 'type_1_basic_same_den': return generate_type_1_problem()
        if problem_type == 'type_2_mixed_sign_same_den': return generate_type_2_problem()
        
    elif level == 2:
        problem_type = random.choice([
            'type_3_diff_den',
            'type_4_multiple_den',
            'type_5_parentheses',
            'type_6_parentheses_larger_den',
            'type_7_two_mixed_numbers',
            'type_8_three_mixed_numbers'
        ])
        
        if problem_type == 'type_3_diff_den': return generate_type_3_problem()
        if problem_type == 'type_4_multiple_den': return generate_type_4_problem()
        if problem_type == 'type_5_parentheses': return generate_type_5_problem()
        if problem_type == 'type_6_parentheses_larger_den': return generate_type_6_problem()
        if problem_type == 'type_7_two_mixed_numbers': return generate_type_7_problem()
        if problem_type == 'type_8_three_mixed_numbers': return generate_type_8_problem()
        
    else:
        raise ValueError("Invalid level. Please choose 1 or 2.")
    
    # Fallback (should not be reached with proper random.choice and if-elif-else)
    return generate_type_1_problem() # Default to a simple problem if something goes wrong
