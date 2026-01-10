# ==============================================================================
# ID: jh_數學1上_LawsOfExponents
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 35.47s | RAG: 7 examples
# Created At: 2026-01-09 14:10:57
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
# Helper Functions (as per Architect's Spec)
# ==============================================================================


# Problem Generation Functions (Level 1)
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Product of powers with the same base (a^m × a^n = a^(m+n))
    """
    base_options = [random.randint(-5, -2), random.randint(2, 9)]
    # Add fraction option
    if random.random() < 0.5: # 50% chance for fraction base
        num = random.randint(1, 9)
        den = random.randint(2, 9)
        base_options.append(Fraction(num, den))
    base = random.choice(base_options)
    
    exp1 = random.randint(2, 6)
    exp2 = random.randint(2, 6)
    
    answer_val = exp1 + exp2
    
    # Format base for display, especially for negative numbers and fractions
    base_display = fmt_num(base) if isinstance(base, (int, Fraction)) else str(base)
    if isinstance(base, Fraction):
        base_display = f"({to_latex(base)})" # Ensure fractions are parenthesized as a base
        
    question_text = f"在下列□中填入適當的數，使等號成立。\n${base_display}^{exp1} \\times {base_display}^{exp2} = {base_display}^{{\\Box}}$"
    
    return {
        "question_text": question_text,
        "answer": str(answer_val),
        "correct_answer": str(answer_val),
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1: Quotient of powers with the same base (a^m ÷ a^n = a^(m-n))
    """
    base_options = [random.randint(-5, -2), random.randint(2, 9)]
    if random.random() < 0.5:
        num = random.randint(1, 9)
        den = random.randint(2, 9)
        base_options.append(Fraction(num, den))
    base = random.choice(base_options)
    
    exp1 = random.randint(5, 9)
    exp2 = random.randint(2, exp1 - 1) # ensure exp1 > exp2
    
    answer_val = exp1 - exp2
    
    base_display = fmt_num(base) if isinstance(base, (int, Fraction)) else str(base)
    if isinstance(base, Fraction):
        base_display = f"({to_latex(base)})"
        
    question_text = f"在下列□中填入適當的數，使等號成立。\n${base_display}^{exp1} \\div {base_display}^{exp2} = {base_display}^{{\\Box}}$"
    
    return {
        "question_text": question_text,
        "answer": str(answer_val),
        "correct_answer": str(answer_val),
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 1: Power of a power ((a^m)^n = a^(m*n))
    """
    base_options = [random.randint(2, 9)]
    if random.random() < 0.5:
        num = random.randint(1, 9)
        den = random.randint(2, 9)
        base_options.append(Fraction(num, den))
    base = random.choice(base_options)
    
    exp1 = random.randint(2, 4)
    exp2 = random.randint(2, 4)
    
    answer_val = exp1 * exp2
    
    base_display = fmt_num(base) if isinstance(base, (int, Fraction)) else str(base)
    if isinstance(base, Fraction):
        base_display = f"({to_latex(base)})"
        
    question_text = f"在下列□中填入適當的數，使等號成立。\n$({base_display}^{exp1})^{exp2} = {base_display}^{{\\Box}}$"
    
    return {
        "question_text": question_text,
        "answer": str(answer_val),
        "correct_answer": str(answer_val),
        "difficulty": 1
    }

def generate_type_4_problem():
    """
    Level 1: Power of a product ((a×b)^n = a^n × b^n)
    """
    val1 = random.randint(2, 9)
    val2 = random.randint(2, 9)
    while val1 == val2: # ensure distinct values
        val2 = random.randint(2, 9)
    
    exp = random.randint(2, 5)
    
    # The spec example includes fractions, but variable generation is int.
    # Sticking to int for val1, val2 as per spec's variable generation.
    val1_display = to_latex(val1)
    val2_display = to_latex(val2)
    
    question_text = f"在下列□中填入適當的數，使等號成立。\n$({val1_display} \\times {val2_display})^{exp} = {val1_display}^{{\\Box}} \\times {val2_display}^{{\\Box}}$"
    
    return {
        "question_text": question_text,
        "answer": str(exp),
        "correct_answer": str(exp),
        "difficulty": 1
    }

# ==============================================================================
# Problem Generation Functions (Level 2)
# ==============================================================================

def generate_type_5_problem():
    """
    Level 2: Conceptual understanding of negative bases and order of operations.
    """
    base = random.randint(2, 5)
    exp_inner1 = random.randint(2, 4)
    exp_outer1 = random.randint(2, 4)
    while exp_inner1 == exp_outer1: # ensure distinct exponents
        exp_outer1 = random.randint(2, 4)
        
    exp_inner2 = exp_outer1
    exp_outer2 = exp_inner1
    
    # Calculate values
    # -(base**exp_inner1) is -(value)
    term1_base_val = -(base**exp_inner1)
    term1_val = term1_base_val ** exp_outer1
    
    term2_base_val = -(base**exp_inner2)
    term2_val = term2_base_val ** exp_outer2
    
    question_text = (
        f"判斷 $({fmt_num(term1_base_val)})^{exp_outer1}$ 與 $({fmt_num(term2_base_val)})^{exp_outer2}$ 的值是否相同？"
    )
    
    answer_text = "相同" if term1_val == term2_val else "不相同"
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Level 2: Mixed operations and calculation.
    """
    C_val = random.randint(2, 4)
    A_val = C_val * random.randint(2, 5) # A_val is a multiple of C_val
    
    B_val = random.randint(2, 7)
    while B_val == A_val or B_val == C_val: # Ensure B_val is distinct
        B_val = random.randint(2, 7)
        
    N = random.randint(3, 5)
    M = random.randint(2, N - 1)
    
    D_val_base = A_val // C_val # Simplified base for the (A/C)^N part
    neg_base_prob = random.random()
    D_signed = D_val_base if neg_base_prob < 0.5 else -D_val_base
    
    # Calculations
    # (A_val/B_val)^N * (B_val/C_val)^N = ((A_val/B_val) * (B_val/C_val))^N = (A_val/C_val)^N
    simplified_base_fraction = Fraction(A_val, C_val)
    numerator_term_val = simplified_base_fraction ** N
    denominator_term_val = D_signed ** M
    
    final_result = numerator_term_val / denominator_term_val
    
    question_text = (
        f"計算下列各式的值。\n"
        f"$({to_latex(Fraction(A_val, B_val))})^{N} \\times ({to_latex(Fraction(B_val, C_val))})^{N} \\div {fmt_num(D_signed)}^{M}$"
    )
    
    return {
        "question_text": question_text,
        "answer": to_latex(final_result),
        "correct_answer": to_latex(final_result),
        "difficulty": 2
    }

def generate_type_7_problem():
    """
    Level 2: Error analysis in applying exponent laws.
    """
    A_val = random.randint(3, 6)
    B_val = random.randint(2, A_val - 1)
    M_exp = random.choice([4, 6, 8]) # Even exponent
    
    # Correct Solution Logic
    # (-A_val)^M_exp = A_val^M_exp (since M_exp is even)
    # (-(B_val^M_exp)) is simply -(B_val^M_exp)
    # So, A_val^M_exp * (-(B_val^M_exp)) = -(A_val^M_exp * B_val^M_exp)
    # = -((A_val * B_val)^M_exp)
    correct_answer_value = -((A_val * B_val)**M_exp)
    
    # Student 1 (Xiao Yan) Incorrect Steps
    # Assumes (-(B_val**M_exp)) is (-B_val)**M_exp, which is incorrect.
    # ((-A_val) * (-B_val))^M_exp = (A_val * B_val)^M_exp
    step1_yan = f"[({fmt_num(-A_val)}) \\times ({fmt_num(-B_val)})]^{M_exp}"
    step2_yan = f"({A_val * B_val})^{M_exp}"
    
    # Student 2 (Xiao Yi) Incorrect Steps
    # Ignores the negative sign from (-(B_val**M_exp))
    # (-A_val)^M_exp * (B_val^M_exp) = A_val^M_exp * B_val^M_exp = (A_val * B_val)^M_exp
    step1_yi = f"({A_val})^{M_exp} \\times ({B_val})^{M_exp}" # (-A_val)^M_exp becomes A_val^M_exp
    step2_yi = f"({A_val * B_val})^{M_exp}"
    
    question_text = (
        f"以下是小妍和小翊計算「$({fmt_num(-A_val)})^{M_exp} \\times ({fmt_num(-(B_val**M_exp))})$」的過程。判斷他們的解法是否正確？若不正確，請標出開始發生錯誤的部分，並寫出正確的解法。\n\n"
        f"小妍：$({fmt_num(-A_val)})^{M_exp} \\times ({fmt_num(-(B_val**M_exp))}) = {step1_yan} = {step2_yan} = {to_latex((A_val*B_val)**M_exp)}$\n\n"
        f"小翊：$({fmt_num(-A_val)})^{M_exp} \\times ({fmt_num(-(B_val**M_exp))}) = {step1_yi} = {step2_yi} = {to_latex((A_val*B_val)**M_exp)}$"
    )
    
    correct_solution_steps = (
        f"兩位同學的解法皆不正確。\n"
        f"小妍的錯誤在於將 $({fmt_num(-(B_val**M_exp))})$ 誤認為 $({fmt_num(-B_val)})^{M_exp}$。\n"
        f"小翊的錯誤在於忽略了 $({fmt_num(-(B_val**M_exp))})$ 中的負號。\n"
        f"正確的解法為：\n"
        f"$({fmt_num(-A_val)})^{M_exp} \\times ({fmt_num(-(B_val**M_exp))})$\n"
        f"$= ({A_val})^{M_exp} \\times ({fmt_num(-(B_val**M_exp))})$\n"
        f"$= -({A_val}^{M_exp} \\times {B_val}^{M_exp})$\n"
        f"$= -({A_val} \\times {B_val})^{M_exp}$\n"
        f"$= {to_latex(correct_answer_value)}$"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_solution_steps,
        "correct_answer": correct_solution_steps,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher for Laws of Exponents skill.
    - Level 1: Basic concepts, direct calculations.
    - Level 2: Advanced applications, multi-step problems, error analysis.
    """
    if level == 1:
        return random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
            generate_type_4_problem,
        ])()
    elif level == 2:
        return random.choice([
            generate_type_5_problem,
            generate_type_6_problem,
            generate_type_7_problem,
        ])()
    else:
        raise ValueError("Invalid level. Choose 1 or 2.")

# ==============================================================================
# Answer Checker (Standard, not part of the generation task but often included)
# ==============================================================================

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "").replace("$", "").replace("\\", "")
    correct = correct_answer.strip().replace(" ", "").replace("$", "").replace("\\", "")
    
    # Try direct string comparison first
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    # Attempt numeric comparison if possible (e.g., for simple numerical answers)
    try:
        user_num = float(user)
        correct_num = float(correct)
        if abs(user_num - correct_num) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # Not a simple numeric answer, continue to more complex checks if needed
    
    # For complex answers like error analysis, direct string comparison is usually the only way
    # If the question asks for a specific format, minor deviations might lead to 'incorrect'.
    # For this skill, Type 7 especially requires exact string matching for the explanation.
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}

