# ==============================================================================
# ID: jh_數學1上_SolvingOneVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 53.14s | RAG: 6 examples
# Created At: 2026-01-09 23:00:50
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
    Type 1: Checking potential solutions.
    Concept: Students substitute given values into a linear equation to determine which one is the solution.
    """
    a = random.randint(-5, 5)
    while a == 0:
        a = random.randint(-5, 5)

    correct_x = random.randint(-5, 5)
    b = random.randint(-10, 10)
    c = a * correct_x + b # c is calculated to ensure correct_x is an integer solution

    # Generate distinct distractors close to correct_x
    distractor1 = correct_x + random.choice([-2, -1, 1, 2])
    while distractor1 == correct_x:
        distractor1 = correct_x + random.choice([-2, -1, 1, 2])
    
    distractor2 = correct_x + random.choice([-3, -2, -1, 1, 2, 3])
    while distractor2 == correct_x or distractor2 == distractor1:
        distractor2 = correct_x + random.choice([-3, -2, -1, 1, 2, 3])

    choices = [correct_x, distractor1, distractor2]
    random.shuffle(choices)

    # Format the constant term 'b' with its sign
    question_eq_b = f"+ {fmt_num(b)}" if b >= 0 else fmt_num(b)
    
    question_text = f"檢驗看看，{choices[0]}、{choices[1]}、{choices[2]} 三數中，哪一個是方程式 ${fmt_num(a)}x {question_eq_b} = {fmt_num(c)}$ 的解？"
    answer = str(correct_x) 
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    """
    Type 2: Simple addition/subtraction equations.
    Concept: Students solve linear equations of the form `x + a = b` or `x - a = b`.
    """
    a = random.randint(1, 15) # a is positive
    b = random.randint(-10, 20)
    op = random.choice(['+', '-'])
    
    if op == '+':
        correct_x = b - a
    else: # op == '-'
        correct_x = b + a
    
    question_text = f"解一元一次方程式 $x {op} {a} = {fmt_num(b)}$。"
    answer = str(correct_x)
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_3_problem():
    """
    Type 3: Simple multiplication/division equations.
    Concept: Students solve linear equations of the form `ax = b` or `x/a = b`.
    """
    a = random.randint(-10, 10)
    while a == 0:
        a = random.randint(-10, 10)
    
    op_type = random.choice(['multiply', 'divide'])
    
    if op_type == 'multiply':
        # ax = b, ensure integer solution by picking x first
        correct_x = random.randint(-10, 10)
        b = a * correct_x
        question_text = f"解一元一次方程式 ${fmt_num(a)}x = {fmt_num(b)}$。"
    else: # op_type == 'divide'
        # x/a = b, calculate x = a * b
        b = random.randint(-10, 10)
        correct_x = a * b
        question_text = f"解一元一次方程式 $\\frac{{x}}{{{fmt_num(a)}}} = {fmt_num(b)}$。"
    
    answer = str(correct_x)
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_4_problem():
    """
    Type 4: Variables on both sides.
    Concept: Students solve linear equations with variables and constants on both sides (e.g., `ax + b = cx + d`).
    """
    a = random.randint(-5, 5)
    c = random.randint(-5, 5)
    while a == c: # Ensure `a != c` to avoid no solution/infinite solutions
        c = random.randint(-5, 5)
    
    correct_x = random.randint(-5, 5) # Generate x first to ensure integer solution
    
    b = random.randint(-10, 10)
    # Based on ax + b = cx + d, we need d = (a-c)x + b
    d = (a - c) * correct_x + b
    
    # Format constant terms with their signs
    question_b_str = f"+ {fmt_num(b)}" if b >= 0 else fmt_num(b)
    question_d_str = f"+ {fmt_num(d)}" if d >= 0 else fmt_num(d)
    
    question_text = f"解一元一次方程式 ${fmt_num(a)}x {question_b_str} = {fmt_num(c)}x {question_d_str}$。"
    answer = str(correct_x)
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_5_problem():
    """
    Type 5: Equations with distributive property.
    Concept: Students solve linear equations requiring the distributive property and multiple steps.
    Template: A(Bx + C) = D(Ex + F) + G
    """
    A = random.randint(-3, 3)
    while A == 0: A = random.randint(-3, 3) # A must be non-zero
    B = random.randint(-3, 3)
    while B == 0: B = random.randint(-3, 3) # B must be non-zero for Bx term
    C = random.randint(-5, 5)
    D = random.randint(-3, 3)
    E = random.randint(-3, 3)
    # E can be zero if D is non-zero, it just means no x term on the right from D(Ex+F)
    F = random.randint(-5, 5)
    G = random.randint(-10, 10)

    # Expand the equation:
    # ABx + AC = DEx + DF + G
    # (AB - DE)x = DF + G - AC

    # Calculate coefficients after expansion
    final_coeff_x = (A * B) - (D * E)
    final_const = (D * F + G) - (A * C)

    # Ensure a valid equation with a unique solution (coefficient of x cannot be zero)
    if final_coeff_x == 0:
        return generate_type_5_problem() # Regenerate if x terms cancel out
    
    correct_x = Fraction(final_const, final_coeff_x)

    # Format parts of the question string
    question_left_b_str = f"+ {fmt_num(C)}" if C >= 0 else fmt_num(C)
    question_right_d_str = f"+ {fmt_num(F)}" if F >= 0 else fmt_num(F)
    
    # Handle G term: if G is 0, it should not be displayed
    question_g_str = ""
    if G != 0:
        question_g_str = f"+ {fmt_num(G)}" if G >= 0 else fmt_num(G)

    question_text = f"解一元一次方程式 ${fmt_num(A)}({fmt_num(B)}x {question_left_b_str}) = {fmt_num(D)}({fmt_num(E)}x {question_right_d_str}) {question_g_str}$。"
    answer = to_latex(correct_x) # Answer must not contain $ signs
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}


def generate_type_6_problem():
    """
    Type 6: Equations with fractions.
    Concept: Students solve linear equations involving fractions, requiring finding a common denominator.
    """
    choice = random.choice([1, 2])

    if choice == 1:
        # Template 1: frac1*x = frac2 - frac3*x
        f1 = get_random_fraction(1, 5, den_limit=6) # Positive coefficient for x on left
        f2 = get_random_fraction(-10, 10, den_limit=10) # Constant term on right
        f3 = get_random_fraction(-3, 3, exclude_zero=True, den_limit=6) # Coefficient for x on right, non-zero

        # Equation: f1*x = f2 - f3*x
        # Rearrange: (f1 + f3)*x = f2
        coeff_x = f1 + f3
        if coeff_x == 0: 
            return generate_type_6_problem() # Prevent division by zero if x terms cancel
        
        correct_x = f2 / coeff_x
        
        # Format f3_str for the question: handle its sign
        f3_str = f"- {to_latex(f3)}x" if f3 > 0 else f"+ {to_latex(-f3)}x"
        question_text = f"解一元一次方程式 ${to_latex(f1)}x = {to_latex(f2)} {f3_str}$。"
        
    else: # choice == 2
        # Template 2: frac1*x - (f2_num_a*x + f2_num_b)/f2_den = frac3
        f1 = get_random_fraction(-3, 3, exclude_zero=True, den_limit=5)

        f2_num_a = random.randint(-4, 4)
        f2_num_b = random.randint(-8, 8)
        f2_den = random.randint(2, 6) # Denominator must be > 1
        
        f3 = get_random_fraction(-5, 5, den_limit=10)

        # Equation: f1*x - (f2_num_a*x + f2_num_b)/f2_den = f3
        # Multiply by LCM (f2_den) to clear fractions:
        # f1*f2_den*x - (f2_num_a*x + f2_num_b) = f3*f2_den
        # f1*f2_den*x - f2_num_a*x - f2_num_b = f3*f2_den
        # (f1*f2_den - f2_num_a)*x = f3*f2_den + f2_num_b
        
        # Calculate coefficients for x and constant term
        coeff_x_val = f1 * f2_den - f2_num_a
        const_val = f3 * f2_den + f2_num_b
        
        if coeff_x_val == 0: 
            return generate_type_6_problem() # Prevent division by zero
        
        correct_x = Fraction(const_val, coeff_x_val)

        # Format f2_num_a*x term within the fraction numerator (e.g., 'x', '-x', '2x', '(-3)x')
        f2_num_a_str = ""
        if f2_num_a == 1:
            f2_num_a_str = "x"
        elif f2_num_a == -1:
            f2_num_a_str = "-x"
        else:
            f2_num_a_str = f"{fmt_num(f2_num_a)}x"

        # Format f2_num_b term within the fraction numerator
        f2_num_b_str = f"+ {fmt_num(f2_num_b)}" if f2_num_b >= 0 else fmt_num(f2_num_b)
        
        question_text = f"解一元一次方程式 ${to_latex(f1)}x - \\frac{{{f2_num_a_str} {f2_num_b_str}}}{{{f2_den}}} = {to_latex(f3)}$。"

    answer = to_latex(correct_x) # Answer must not contain $ signs
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}


def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
            generate_type_4_problem,
        ]
    elif level == 2:
        problem_types = [
            generate_type_5_problem,
            generate_type_6_problem,
        ]
    else:
        raise ValueError("Invalid level. Choose 1 or 2.")

    return random.choice(problem_types)()

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
