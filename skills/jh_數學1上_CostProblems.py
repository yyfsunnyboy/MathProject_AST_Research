# ==============================================================================
# ID: jh_數學1上_CostProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 19.95s | RAG: 2 examples
# Created At: 2026-01-09 21:28:33
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





# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    """
    Generates a Level 2, Type 1 problem based on Ex 1.
    Concept: Solving a system of linear equations for two unknowns in a cost scenario.
    One item's price is a fixed amount more than another, and a total cost for a mixed
    quantity purchase is given.
    """
    item_more_expensive_name_options = ["蛋", "肉鬆", "牛奶", "雞肉", "豬肉"]
    item_cheaper_name_options = ["豆腐", "麵包", "果汁", "青菜", "米"]

    item_more_expensive_name = random.choice(item_more_expensive_name_options)
    item_cheaper_name = random.choice(item_cheaper_name_options)

    # The chosen name lists are disjoint, so item_more_expensive_name will always be different from item_cheaper_name.

    diff_price = random.choice([x for x in range(10, 101, 10)])
    qty_more_expensive = random.randint(1, 3)
    qty_cheaper = random.randint(2, 6)
    price_cheaper = random.randint(10, 80) # Ensures positive integer solution

    price_more_expensive = price_cheaper + diff_price
    total_cost = qty_more_expensive * price_more_expensive + qty_cheaper * price_cheaper

    question_text = f"在超市裡，1 盒{item_more_expensive_name}比 1 盒{item_cheaper_name}貴 {diff_price} 元。小明拿了 {qty_more_expensive} 盒{item_more_expensive_name}和 {qty_cheaper} 盒{item_cheaper_name}，共付了 {total_cost} 元。請問 1 盒{item_more_expensive_name}和 1 盒{item_cheaper_name}的價錢分別為多少元？"
    answer = f"1 盒{item_cheaper_name} {price_cheaper} 元，1 盒{item_more_expensive_name} {price_more_expensive} 元"

    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    """
    Generates a Level 2, Type 2 problem based on Ex 2.
    Concept: Solving a system of linear equations for two unknowns in a ticket cost scenario.
    One ticket type is a fixed amount more expensive than another, and a total cost for a mixed
    quantity purchase is given.
    """
    ticket_more_expensive_name_options = ["全票", "成人票", "貴賓票", "優待票"]
    ticket_cheaper_name_options = ["學生票", "兒童票", "普通票", "半票"]

    ticket_more_expensive_name = random.choice(ticket_more_expensive_name_options)
    ticket_cheaper_name = random.choice(ticket_cheaper_name_options)

    # The chosen name lists are disjoint, so ticket_more_expensive_name will always be different from ticket_cheaper_name.

    diff_price = random.choice([x for x in range(50, 301, 50)])
    qty_more_expensive = random.randint(1, 4)
    qty_cheaper = random.randint(2, 5)
    price_cheaper = random.randint(100, 800) # Ensures positive integer solution

    price_more_expensive = price_cheaper + diff_price
    total_cost = qty_more_expensive * price_more_expensive + qty_cheaper * price_cheaper

    question_text = f"小華與家人到遊樂園，買 {qty_more_expensive} 張{ticket_more_expensive_name}與 {qty_cheaper} 張{ticket_cheaper_name}共付了 {total_cost} 元。已知{ticket_more_expensive_name}每張比{ticket_cheaper_name}貴 {diff_price} 元，則 1 張{ticket_cheaper_name}和 1 張{ticket_more_expensive_name}各多少元？"
    answer = f"1 張{ticket_cheaper_name} {price_cheaper} 元，1 張{ticket_more_expensive_name} {price_more_expensive} 元"

    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate(level=1):
    """
    Dispatches problem generation based on the specified level.
    Level 1 problems default to Level 2 as per Architect's Spec.
    """
    if level == 1:
        # As per spec, no Level 1 problems are defined, so default to Level 2.
        return random.choice([generate_type_1_problem, generate_type_2_problem])()
    elif level == 2:
        return random.choice([generate_type_1_problem, generate_type_2_problem])()
    else:
        # Fallback for invalid level, though spec implies only 1 or 2 will be inputs.
        return generate_type_1_problem() # Or raise an error

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
