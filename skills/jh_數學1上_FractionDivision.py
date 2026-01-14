# ==============================================================================
# ID: jh_數學1上_FractionDivision
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 47.34s | RAG: 3 examples
# Created At: 2026-01-09 14:09:25
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

# ==============================================================================
# Built-in Helpers (Mimicking system environment)
# ==============================================================================


# Custom Helper for Question Formatting (Coder MUST implement)
# ==============================================================================

def _format_number_for_question(frac_obj: Fraction) -> str:
    """
    Formats a fractions.Fraction object into a LaTeX string suitable for questions,
    adhering to specific formatting rules from examples:
    - Integers: uses fmt_num (e.g., -5 -> (-5), 5 -> 5)
    - Positive mixed numbers: 'whole \frac{num}{den}' (e.g., 3 2/5 -> 3 \frac{2}{5})
    - Negative mixed numbers: '(-whole \frac{num}{den})' (e.g., -3 1/3 -> (-3 \frac{1}{3}))
    - Positive proper/improper fractions: '\frac{num}{den}' (e.g., 5/6 -> \frac{5}{6})
    - Negative proper/improper fractions: '(-\frac{num}{den})' (e.g., -2/3 -> (-\frac{2}{3}))
    """
    is_neg = frac_obj < 0
    abs_frac = abs(frac_obj)

    if abs_frac.denominator == 1: # It's an integer
        return fmt_num(frac_obj.numerator)
    elif abs_frac.numerator > abs_frac.denominator and abs_frac.numerator % abs_frac.denominator != 0: # It's an improper fraction, can be mixed
        whole = abs_frac.numerator // abs_frac.denominator
        rem_num = abs_frac.numerator % abs_frac.denominator
        mixed_str = f"{whole} \\frac{{{rem_num}}}{{{abs_frac.denominator}}}"
        if is_neg:
            return f"(-{mixed_str})" # Example: (-3 1/3)
        else:
            return mixed_str # Example: 3 2/5
    else: # It's a proper fraction or an improper fraction that simplifies to an integer (handled above)
        # For fractions, to_latex already handles the sign correctly (e.g., -\frac{2}{3})
        # But examples like (-2/3) suggest surrounding negative fractions with parentheses.
        latex_str = to_latex(frac_obj)
        if is_neg and latex_str.startswith('-'):
            return f"({latex_str})" # If to_latex already added '-', keep it and add outer parentheses.
        elif is_neg and not latex_str.startswith('-'): # Fallback if to_latex didn't add the sign
             return f"({latex_str})"
        else:
            return latex_str

def _generate_random_fraction_obj(
    num_type_choice=None,
    max_whole=5, min_whole=1,
    max_den=10, min_den=2,
    max_num_for_proper=9, min_num_for_proper=1,
    max_num_for_improper=15, min_num_for_improper_factor=1,
    allow_zero=False,
    allow_negative=True
) -> Fraction:
    """
    Generates a random fractions.Fraction object based on specified types and ranges.
    Ensures denominator is not zero. Can control if zero or negative numbers are allowed.
    """
    if num_type_choice is None:
        num_type_choice = random.choice(['integer', 'proper_fraction', 'improper_fraction', 'mixed_number'])

    sign = random.choice([1, -1]) if allow_negative else 1
    
    frac_obj = Fraction(0, 1) # Initialize

    if num_type_choice == 'integer':
        val = random.randint(min_whole, max_whole) # Ensure non-zero integer initially
        frac_obj = Fraction(val * sign)
    elif num_type_choice == 'proper_fraction':
        den = random.randint(min_den, max_den)
        num = random.randint(min_num_for_proper, min(den - 1, max_num_for_proper))
        # Reroll if it results in zero and zero is not allowed (e.g., if min_num_for_proper was 0)
        while num == 0 and not allow_zero:
            num = random.randint(min_num_for_proper, min(den - 1, max_num_for_proper))
        frac_obj = Fraction(num, den) * sign
    elif num_type_choice == 'improper_fraction':
        den = random.randint(min_den, max_den)
        # Ensure num > den
        num = random.randint(den + min_num_for_improper_factor, den + max_num_for_improper)
        frac_obj = Fraction(num, den) * sign
    elif num_type_choice == 'mixed_number':
        whole = random.randint(min_whole, max_whole)
        den = random.randint(min_den, max_den)
        num = random.randint(min_num_for_proper, min(den - 1, max_num_for_proper))
        # Reroll if it results in zero and zero is not allowed
        while num == 0 and not allow_zero:
            num = random.randint(min_num_for_proper, min(den - 1, max_num_for_proper))
        frac_obj = Fraction(whole * den + num, den) * sign
    
    # Final check to ensure non-zero if allow_zero is False
    if not allow_zero and frac_obj == Fraction(0):
        # Recursively call to generate a non-zero fraction
        return _generate_random_fraction_obj(num_type_choice, max_whole, min_whole, max_den, min_den,
                                              max_num_for_proper, min_num_for_proper,
                                              max_num_for_improper, min_num_for_improper_factor,
                                              allow_zero=False, allow_negative=allow_negative)
    return frac_obj

# ==============================================================================
# Problem Generation Functions
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Reciprocals.
    Concept: Calculate the reciprocal of a given number.
    """
    frac_obj = _generate_random_fraction_obj(
        min_den=2, max_den=10, # Denominators for fractions/mixed
        max_whole=5, min_whole=1, # Whole part for integers/mixed
        max_num_for_proper=9, min_num_for_proper=1, # Numerator for proper fractions
        max_num_for_improper=10, # Numerator for improper fractions
        allow_zero=False # Reciprocal cannot be of zero
    )

    question_num_str = _format_number_for_question(frac_obj)
    
    ans_frac = 1 / frac_obj
    
    question_text = f"寫出下列各數的倒數。\n$\\quad {question_num_str}$"
    
    return {
        "question_text": question_text,
        "answer": to_latex(ans_frac),
        "correct_answer": to_latex(ans_frac),
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 2: Single or Double Fraction Division.
    Concept: Perform fraction division involving one or two consecutive operations.
    """
    num_operations = random.choice([1, 2])

    frac_a = _generate_random_fraction_obj(max_whole=5, min_whole=1, max_den=10, min_den=2, max_num_for_improper=10, allow_negative=True)
    frac_b = _generate_random_fraction_obj(max_whole=5, min_whole=1, max_den=10, min_den=2, max_num_for_improper=10, allow_zero=False, allow_negative=True)

    term_a_str = _format_number_for_question(frac_a)
    term_b_str = _format_number_for_question(frac_b)

    if num_operations == 1:
        expression_str = f"{term_a_str} \\div {term_b_str}"
        result_frac = frac_a / frac_b
    else: # num_operations == 2
        frac_c = _generate_random_fraction_obj(max_whole=5, min_whole=1, max_den=10, min_den=2, max_num_for_improper=10, allow_zero=False, allow_negative=True)
        term_c_str = _format_number_for_question(frac_c)
        expression_str = f"{term_a_str} \\div {term_b_str} \\div {term_c_str}"
        result_frac = frac_a / frac_b / frac_c
    
    question_text = f"計算下列各式的值。\n$\\quad {expression_str}$"

    return {
        "question_text": question_text,
        "answer": to_latex(result_frac),
        "correct_answer": to_latex(result_frac),
        "difficulty": 2
    }

def generate_type_3_problem():
    """
    Level 2: Single or Triple Fraction Division.
    Concept: Perform fraction division involving one or three consecutive operations.
    """
    num_operations = random.choice([1, 3])

    frac_a = _generate_random_fraction_obj(max_whole=6, min_whole=1, max_den=12, min_den=2, max_num_for_improper=15, allow_negative=True)
    frac_b = _generate_random_fraction_obj(max_whole=6, min_whole=1, max_den=12, min_den=2, max_num_for_improper=15, allow_zero=False, allow_negative=True)

    term_a_str = _format_number_for_question(frac_a)
    term_b_str = _format_number_for_question(frac_b)

    if num_operations == 1:
        expression_str = f"{term_a_str} \\div {term_b_str}"
        result_frac = frac_a / frac_b
    else: # num_operations == 3
        frac_c = _generate_random_fraction_obj(max_whole=6, min_whole=1, max_den=12, min_den=2, max_num_for_improper=15, allow_zero=False, allow_negative=True)
        frac_d = _generate_random_fraction_obj(max_whole=6, min_whole=1, max_den=12, min_den=2, max_num_for_improper=15, allow_zero=False, allow_negative=True)
        term_c_str = _format_number_for_question(frac_c)
        term_d_str = _format_number_for_question(frac_d)
        expression_str = f"{term_a_str} \\div {term_b_str} \\div {term_c_str} \\div {term_d_str}"
        result_frac = frac_a / frac_b / frac_c / frac_d
    
    question_text = f"計算下列各式的值。\n$\\quad {expression_str}$"

    return {
        "question_text": question_text,
        "answer": to_latex(result_frac),
        "correct_answer": to_latex(result_frac),
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level: int = 1):
    """
    Dispatches to problem generation functions based on the specified level.
    """
    if level == 1:
        return generate_type_1_problem()
    elif level == 2:
        # Randomly choose between Type 2 and Type 3 for advanced problems
        return random.choice([generate_type_2_problem, generate_type_3_problem])()
    else:
        raise ValueError(f"Invalid level: {level}. Level must be 1 or 2.")

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
