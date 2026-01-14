# ==============================================================================
# ID: jh_數學1上_ApplicationProblems_v2
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 18.85s | RAG: 1 examples
# Created At: 2026-01-09 22:54:12
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
    Generates a Level 2 problem based on the Architect's Specification.
    Concept: Solve a word problem involving a percentage discount on multiple items,
             where the discounted price for a quantity of items is compared to the
             original price of a single item, to find the original unit price.
    """
    # Variables defined in the spec
    original_price_options = [10, 20, 30, 40, 50]
    num_bottles_options = [2, 3]
    discount_factor_numerator_options = [6, 7, 8, 9] # Represents 'X' in "打X折"

    # 1. Randomly select original_price. This will be the correct_answer.
    original_price = random.choice(original_price_options)

    # 2. Randomly select num_bottles.
    num_bottles = random.choice(num_bottles_options)

    # 3. Randomly select discount_factor_numerator.
    discount_factor_numerator = random.choice(discount_factor_numerator_options)

    # 4. Calculate discount_multiplier.
    discount_multiplier = discount_factor_numerator / 10.0

    # 5. Calculate price_difference.
    # Logic: (price of num_bottles at discount) - (original price of 1 bottle)
    # Let 'x' be the original_price.
    # Price of num_bottles at discount = num_bottles * (x * discount_multiplier)
    # Original price of 1 bottle = x
    # Difference = num_bottles * x * discount_multiplier - x
    # Difference = x * (num_bottles * discount_multiplier - 1)
    # The constraint (num_bottles * discount_multiplier - 1) is always positive with the given ranges:
    # Smallest: (2 * 0.6 - 1) = 0.2
    # Largest: (3 * 0.9 - 1) = 1.7
    price_difference = round(original_price * (num_bottles * discount_multiplier - 1))

    # Formulate the question text in Traditional Chinese.
    question_text = (
        f"這款汽水正在促銷，買 ${num_bottles}$ 瓶打 ${discount_factor_numerator}$ 折，"
        f"只比買 $1$ 瓶多 ${price_difference}$ 元喔！一瓶原價多少錢？"
    )

    # The answer is the original_price, converted to string without '$'.
    answer = str(original_price)

    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': answer
    }

def generate_type_L1_problem():
    """
    Invented Level 1 problem as per spec "No Level 1 types defined for this skill yet."
    Concept: Calculate the discounted price of a single item given its original price and a discount percentage.
    """
    original_price_options = [50, 100, 150, 200]
    discount_factor_numerator_options = [7, 8, 9] # e.g., '打8折' means 80%

    original_price = random.choice(original_price_options)
    discount_factor_numerator = random.choice(discount_factor_numerator_options)

    discount_multiplier = discount_factor_numerator / 10.0
    discounted_price = int(original_price * discount_multiplier) # Ensure integer result

    question_text = (
        f"一本書原價 ${original_price}$ 元，如果打 ${discount_factor_numerator}$ 折出售，"
        f"請問售價是多少元？"
    )

    answer = str(discounted_price)

    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': answer
    }

def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        # For Level 1, as per spec, no types are defined. We use an invented simplified type.
        return generate_type_L1_problem()
    elif level == 2:
        # For Level 2, only Type 1 is available.
        return generate_type_1_problem()
    else:
        # Default to Level 1 if an unsupported level is requested.
        return generate_type_L1_problem()

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
