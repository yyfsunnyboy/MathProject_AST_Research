# ==============================================================================
# ID: jh_數學1上_SimplestFraction
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 60.71s | RAG: 6 examples
# Created At: 2026-01-09 16:10:59
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

# Helper function to format negative numbers with parentheses for display.


# Example: fraction_to_mixed_latex(Fraction(-7, 3)) -> "$-2 \frac{1}{3}$"
def fraction_to_mixed_latex(frac):
    """Helper: Converts a Fraction object to a mixed number LaTeX string."""
    if frac.denominator == 0:
        return "Undefined" # Should not happen with current generation logic
    
    sign = ""
    # Store the original sign, then work with absolute value for whole/remainder calculation
    if frac < 0:
        sign = "-"
        frac = abs(frac)
    
    # If it's a proper fraction or zero
    if frac.numerator < frac.denominator:
        if frac.numerator == 0: # Handle 0 explicitly, it's not a mixed number
            return "0"
        return f"{sign}{to_latex(frac)}" # e.g., -1/2
    
    whole = frac.numerator // frac.denominator
    remainder = frac.numerator % frac.denominator
    
    if remainder == 0: # Whole number, e.g., 6/3 -> 2
        return f"{sign}{whole}"
    else: # Mixed number, e.g., 7/3 -> 2 1/3
        return f"{sign}{whole} {to_latex(Fraction(remainder, frac.denominator))}"

# Re-implement gcd using math.gcd as it's standard.
def gcd(a, b):
    """Helper: Returns the greatest common divisor."""
    return math.gcd(a, b)

# ==============================================================================
# Skill Specific Implementations (jh_數學1上_SimplestFraction)
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Conceptual understanding of simplest fraction.
    Question: "將一個分數的分子和分母同時除以它們的最大公因數，所得到的分數是最簡分數嗎？說說你的看法。"
    Answer: "是"
    """
    question_text = "將一個分數的分子和分母同時除以它們的最大公因數，所得到的分數是最簡分數嗎？說說你的看法。"
    answer = "是"
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1: Simplifying fractions and identifying simplest form.
    Involves handling positive, negative numerators/denominators.
    """
    while True:
        num = random.randint(-40, 40)
        den = random.randint(2, 50)
        if num == 0: 
            continue # Avoid 0/den for simplification context

        frac_val = Fraction(num, den)
        
        # The Fraction class automatically normalizes the sign and simplifies.
        # E.g., Fraction(1, -2) becomes Fraction(-1, 2).
        # We need to ensure the denominator is positive for the GCD calculation as per spec.
        # This is implicitly handled if we take abs(numerator) and the positive denominator.
        
        question_text = f"判斷分數 ${to_latex(frac_val)}$ 是否為最簡分數，如果不是，請化成最簡分數。"
        
        # Calculate GCD using absolute value of numerator for consistency
        common_divisor = gcd(abs(frac_val.numerator), frac_val.denominator)
        
        if common_divisor == 1:
            answer = "是最簡分數"
        else:
            # Explicitly calculate simplified form as per spec, even though Fraction is already simplified.
            simplified_num = frac_val.numerator // common_divisor
            simplified_den = frac_val.denominator // common_divisor
            answer = to_latex(Fraction(simplified_num, simplified_den))
        
        return {
            "question_text": question_text,
            "answer": answer,
            "correct_answer": answer, # Correct answer is the generated answer string
            "difficulty": 1
        }

def generate_type_4_problem():
    """
    Level 1: Comparing two positive proper fractions.
    """
    while True:
        num1 = random.randint(1, 10)
        den1 = random.randint(2, 15)
        num2 = random.randint(1, 10)
        den2 = random.randint(2, 15)

        frac1 = Fraction(num1, den1)
        frac2 = Fraction(num2, den2)
        
        # Ensure proper fractions (numerator < denominator)
        is_proper1 = frac1.numerator < frac1.denominator
        is_proper2 = frac2.numerator < frac2.denominator

        # Ensure distinct and both are proper
        if frac1 != frac2 and is_proper1 and is_proper2:
            break
    
    question_text = f"比較 ${to_latex(frac1)}$ 和 ${to_latex(frac2)}$ 的大小。"
    if frac1 < frac2:
        answer = f"{to_latex(frac1)} < {to_latex(frac2)}"
    else: # frac1 > frac2, since frac1 != frac2 condition ensures they are not equal
        answer = f"{to_latex(frac1)} > {to_latex(frac2)}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 2: Comparing three positive proper/improper fractions.
    """
    fractions_list = []
    while len(fractions_list) < 3:
        num = random.randint(1, 20)
        den = random.randint(2, 20) 
        f = Fraction(num, den)
        # Ensure fractions are distinct
        if f not in fractions_list:
            fractions_list.append(f)
    
    # Sort for answer generation (ascending order as per spec's implicit example for type 3)
    sorted_fractions = sorted(fractions_list)
    
    question_text = (f"比較下列各組數的大小。\n"
                     f"⑴ ${to_latex(fractions_list[0])}$、${to_latex(fractions_list[1])}$、${to_latex(fractions_list[2])}$")
    
    answer = (f"{to_latex(sorted_fractions[0])} < "
              f"{to_latex(sorted_fractions[1])} < "
              f"{to_latex(sorted_fractions[2])}")
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 2
    }

def generate_type_5_problem():
    """
    Level 2: Comparing negative fractions and mixed numbers.
    """
    # Part 1: Two distinct negative fractions
    f_neg1, f_neg2 = None, None
    while f_neg1 is None or f_neg1 == f_neg2:
        f_neg1 = Fraction(random.randint(1, 15), random.randint(2, 15)) * -1
        f_neg2 = Fraction(random.randint(1, 15), random.randint(2, 15)) * -1
    
    # Part 2: Three distinct negative mixed numbers
    mixed_neg_list = []
    while len(mixed_neg_list) < 3:
        mixed_neg_int = random.randint(1, 3)
        mixed_neg_frac_num = random.randint(1, 5)
        # Ensure proper fractional part (numerator < denominator)
        mixed_neg_frac_den = random.randint(mixed_neg_frac_num + 1, 6) 
        
        # Create a positive fraction first, then apply negative sign
        mixed_val = (mixed_neg_int + Fraction(mixed_neg_frac_num, mixed_neg_frac_den)) * -1
        if mixed_val not in mixed_neg_list:
            mixed_neg_list.append(mixed_val)
    
    sorted_mixed_neg = sorted(mixed_neg_list) # Sorts in ascending order
    
    question_text = (f"比較下列各組數的大小。\n"
                     f"⑴ ${to_latex(f_neg1)}$、${to_latex(f_neg2)}$\n"
                     f"⑵ ${fraction_to_mixed_latex(mixed_neg_list[0])}$、${fraction_to_mixed_latex(mixed_neg_list[1])}$、${fraction_to_mixed_latex(mixed_neg_list[2])}$")
    
    # Answers should be in ascending order.
    # For Part 1, compare directly.
    ans_part1 = f"{to_latex(f_neg1)} < {to_latex(f_neg2)}" if f_neg1 < f_neg2 else f"{to_latex(f_neg1)} > {to_latex(f_neg2)}"
    
    # For Part 2, use the sorted list.
    ans_part2 = (f"{fraction_to_mixed_latex(sorted_mixed_neg[0])} < "
                 f"{fraction_to_mixed_latex(sorted_mixed_neg[1])} < "
                 f"{fraction_to_mixed_latex(sorted_mixed_neg[2])}")
    
    answer = f"⑴ {ans_part1}\n⑵ {ans_part2}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Level 2: More complex comparison of negative fractions and mixed numbers.
    """
    # Part 1: Three distinct negative fractions
    f_neg_list = []
    while len(f_neg_list) < 3:
        f = Fraction(random.randint(1, 20), random.randint(2, 20)) * -1
        if f not in f_neg_list:
            f_neg_list.append(f)
    sorted_f_neg = sorted(f_neg_list) # Sorts in ascending order
    
    # Part 2: Two distinct negative mixed numbers
    mixed_neg_list = []
    while len(mixed_neg_list) < 2:
        mixed_neg_int = random.randint(1, 4)
        mixed_neg_frac_num = random.randint(1, 6)
        # Ensure proper fractional part (numerator < denominator)
        mixed_neg_frac_den = random.randint(mixed_neg_frac_num + 1, 7) 
        
        mixed_val = (mixed_neg_int + Fraction(mixed_neg_frac_num, mixed_neg_frac_den)) * -1
        if mixed_val not in mixed_neg_list:
            mixed_neg_list.append(mixed_val)
    sorted_mixed_neg_part2 = sorted(mixed_neg_list) # Sorts in ascending order
    
    question_text = (f"比較下列各組數的大小。\n"
                     f"⑴ ${to_latex(f_neg_list[0])}$、${to_latex(f_neg_list[1])}$、${to_latex(f_neg_list[2])}$\n"
                     f"⑵ ${fraction_to_mixed_latex(mixed_neg_list[0])}$、${fraction_to_mixed_latex(mixed_neg_list[1])}$")
    
    # Answers should be in ascending order.
    ans_part1 = (f"{to_latex(sorted_f_neg[0])} < "
                 f"{to_latex(sorted_f_neg[1])} < "
                 f"{to_latex(sorted_f_neg[2])}")
    
    ans_part2 = (f"{fraction_to_mixed_latex(sorted_mixed_neg_part2[0])} < "
                 f"{fraction_to_mixed_latex(sorted_mixed_neg_part2[1])}")
    
    answer = f"⑴ {ans_part1}\n⑵ {ans_part2}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher and Checker (from Gold Standard Template)
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        problem_type_func = random.choice([
            generate_type_1_problem, 
            generate_type_2_problem,
            generate_type_4_problem
        ])
    elif level == 2:
        problem_type_func = random.choice([
            generate_type_3_problem, 
            generate_type_5_problem,
            generate_type_6_problem
        ])
    else:
        raise ValueError("Invalid level. Please choose level 1 or 2.")
    
    return problem_type_func()

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    # Normalize by removing all whitespace and common LaTeX spacing commands
    user = user_answer.strip().replace(" ", "").replace("\\,", "").replace("\\;", "")
    correct = correct_answer.strip().replace(" ", "").replace("\\,", "").replace("\\;", "")
    
    # Direct string comparison for exact matches (e.g., "是", LaTeX fractions, comparisons)
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    # Attempt float comparison for purely numerical answers, if applicable.
    # This might not be suitable for complex LaTeX strings with operators.
    try:
        # If both can be parsed as floats and are close enough
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # If parsing to float fails, it's not a simple numerical answer.
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}

