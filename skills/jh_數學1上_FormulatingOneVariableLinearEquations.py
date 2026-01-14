# ==============================================================================
# ID: jh_數學1上_FormulatingOneVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 32.09s | RAG: 2 examples
# Created At: 2026-01-09 21:30:31
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

def fmt_num(num):
    """Format negative numbers with parentheses for LaTeX display."""
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



#  # Not explicitly needed for these problem types

# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    """
    Generates a Type 1 problem based on the Architect's Specification.
    Concept: Formulate a one-variable linear equation directly from a word problem
             involving two types of costs/quantities (one variable-based, one fixed),
             summing up to a total.
    """
    variable_name = random.choice(['x', 'y', 'z'])
    num_units = random.randint(2, 10)
    
    # fixed_cost: ensure it's a multiple of 10 or 5 for realism, as per spec.
    # The spec explicitly states `random.choice([x for x in range(50, 501, 10)])`
    fixed_cost = random.choice(list(range(50, 501, 10))) 
    
    # total_amount: Calculated to ensure total_amount > fixed_cost and leads to a plausible cost per unit.
    # Generate a plausible unit cost for calculation purposes.
    unit_cost_for_calc = random.randint(10, 50)
    total_amount = fixed_cost + num_units * unit_cost_for_calc

    item_name_variable = random.choice(["牛奶", "蘋果", "鉛筆", "筆記本"])
    item_name_fixed = random.choice(["麵包", "飲料", "餅乾", "糖果"])
    person_name = random.choice(["媽媽", "小明", "老師", "爸爸"])

    # Question needs LaTeX wrapping for the variable name.
    q = f"{person_name}買了 {num_units} 盒{item_name_variable}，每盒都是 ${variable_name}$ 元，另外又買了 {fixed_cost} 元的{item_name_fixed}，結帳時總共付了 {total_amount} 元，依題意可列出一元一次方程式為何？"
    
    # Answer MUST be clean (NO $ signs).
    a = f"{num_units}{variable_name}+{fixed_cost}={total_amount}"
    
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate_type_2_problem():
    """
    Generates a Type 2 problem based on the Architect's Specification.
    Concept: First, formulate an algebraic expression based on a relative quantity.
             Second, use that expression and a given total value to formulate a
             one-variable linear equation.
    """
    variable_name = random.choice(['y', 'x', 'a'])
    multiplier = random.randint(2, 5)
    
    # Offset can be positive or negative, as per spec (random.randint(1, 15) or -random.randint(1, 15)).
    offset_magnitude = random.randint(1, 15)
    offset = random.choice([offset_magnitude, -offset_magnitude]) # 50/50 chance for "多" or "少"

    offset_text = "多" if offset > 0 else "少"
    abs_offset = abs(offset)

    # Calculate child_age_for_solution to ensure parent_actual_age is positive and realistic (e.g., >= 10).
    # We want (multiplier * child_age_for_solution) + offset >= 10 (a reasonable minimum age for a 'parent').
    # This implies child_age_for_solution >= (10 - offset) / multiplier.
    
    min_child_age_base = 5 # Minimum conceptual age for the child in the problem.
    min_child_age_required_for_parent = math.ceil((10 - offset) / multiplier)
    
    # Ensure child_age_for_solution is within a reasonable range (e.g., 5 to 20)
    # and also satisfies the minimum required for the parent's age to be >= 10.
    child_age_for_solution = random.randint(max(min_child_age_base, min_child_age_required_for_parent), 20)

    parent_actual_age = (multiplier * child_age_for_solution) + offset
    
    child_name = random.choice(["書萍", "小華", "莉莉", "大雄"])
    parent_name = random.choice(["爸爸", "媽媽", "老師", "叔叔"])
    quantity_unit = random.choice(["歲", "公斤", "元"])

    # Construct the algebraic expression for part ⑴.
    # If offset is positive, explicitly add a '+'. If negative, the '-' sign is part of the number.
    if offset > 0:
        expression_str = f"{multiplier}{variable_name}+{offset}"
    else: # offset is negative
        expression_str = f"{multiplier}{variable_name}{offset}" # e.g., "2y-5"

    # Question needs LaTeX wrapping for the variable name.
    q = f"今年{parent_name}的年齡恰好是{child_name}年齡的 {multiplier} 倍{offset_text} {abs_offset} {quantity_unit}，若{child_name}今年 ${variable_name}$ {quantity_unit}，則：\\n⑴ {parent_name}今年幾{quantity_unit}？(以 ${variable_name}$ 列式)\\n⑵ 承⑴，若{parent_name}今年 {parent_actual_age} {quantity_unit}，則可列出一元一次方程式為何？"
    
    # Answer MUST be clean (NO $ signs).
    a = f"⑴ {expression_str}\n⑵ {expression_str}={parent_actual_age}"
    
    return {'question_text': q, 'answer': a, 'correct_answer': a}


def generate(level=1):
    """
    Dispatches problem generation based on the specified level.
    """
    if level == 1:
        # Choose randomly from Level 1 problem types
        problem_func = random.choice([
            generate_type_1_problem,
            # Add other Level 1 functions here if more are introduced
        ])
        return problem_func()
    elif level == 2:
        # Choose randomly from Level 2 problem types
        problem_func = random.choice([
            generate_type_2_problem,
            # Add other Level 2 functions here if more are introduced
        ])
        return problem_func()
    else:
        raise ValueError("Invalid level. Please choose 1 or 2.")

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
