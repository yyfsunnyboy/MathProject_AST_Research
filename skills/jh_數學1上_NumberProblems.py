# ==============================================================================
# ID: jh_數學1上_NumberProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 21.55s | RAG: 2 examples
# Created At: 2026-01-09 22:56:45
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
    Generates a linear equation word problem of the form ax + b = cx + d
    using "甲數" as the unknown.
    """
    # Helper function _build_side_str as specified, defined locally
    # to avoid creating a global helper and adhere to the "no helpers" rule
    # while still using the provided logic.
    def _build_side_str(coeff, const, var_name):
        s = ""
        if coeff == 1:
            s += var_name
        else:
            s += f"{var_name}的 {fmt_num(coeff)} 倍"

        if const > 0:
            s += f" 加 {fmt_num(const)}"
        elif const < 0:
            s += f" 減 {fmt_num(abs(const))}"
        return s

    x_ans = random.randint(-10, 10)
    left_coeff = random.randint(2, 5)
    right_coeff = random.randint(1, 5)
    # Ensure coefficients are different to avoid trivial or no-solution cases in general,
    # and specifically as per architect's spec.
    while left_coeff == right_coeff:
        right_coeff = random.randint(1, 5)

    left_const = random.randint(-15, 15)
    
    # Derive right_const such that x_ans is the solution for:
    # left_coeff * x_ans + left_const = right_coeff * x_ans + right_const
    # right_const = (left_coeff - right_coeff) * x_ans + left_const
    right_const = (left_coeff - right_coeff) * x_ans + left_const
    
    var_name = "甲數"

    left_str = _build_side_str(left_coeff, left_const, var_name)
    right_str = _build_side_str(right_coeff, right_const, var_name)
    
    question = f"已知 {left_str} 等於 {right_str}，求{var_name}是多少？"
    
    answer = str(x_ans)
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    """
    Generates a linear equation word problem of the form ax + b = cx + d
    using "乙數" as the unknown, with slightly different coefficient ranges.
    """
    # Helper function _build_side_str as specified, defined locally.
    def _build_side_str(coeff, const, var_name):
        s = ""
        if coeff == 1:
            s += var_name
        else:
            s += f"{var_name}的 {fmt_num(coeff)} 倍"

        if const > 0:
            s += f" 加 {fmt_num(const)}"
        elif const < 0:
            s += f" 減 {fmt_num(abs(const))}"
        return s

    x_ans = random.randint(-10, 10)
    left_coeff = random.randint(1, 5) # Different range from Type 1
    right_coeff = random.randint(2, 5) # Different range from Type 1
    # Ensure coefficients are different.
    while left_coeff == right_coeff:
        right_coeff = random.randint(2, 5)

    left_const = random.randint(-15, 15)
    
    # Derive right_const such that x_ans is the solution.
    # right_const = (left_coeff - right_coeff) * x_ans + left_const
    right_const = (left_coeff - right_coeff) * x_ans + left_const
    
    var_name = "乙數"

    left_str = _build_side_str(left_coeff, left_const, var_name)
    right_str = _build_side_str(right_coeff, right_const, var_name)
    
    question = f"已知 {left_str} 等於 {right_str}，求{var_name}是多少？"
    
    answer = str(x_ans)
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}

def generate(level=1):
    """
    Dispatches problem generation based on the specified level.
    For this skill, only Level 1 problems are defined.
    """
    if level == 1:
        return random.choice([generate_type_1_problem, generate_type_2_problem])()
    else:
        # As per Architect's Spec, only Level 1 problems are implemented for this skill.
        raise ValueError("Invalid level. Only level 1 is implemented for this skill.")

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
