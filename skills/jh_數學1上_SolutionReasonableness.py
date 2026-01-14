# ==============================================================================
# ID: jh_數學1上_SolutionReasonableness
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 28.07s | RAG: 2 examples
# Created At: 2026-01-09 22:59:57
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

def generate_type_2_problem():
    """
    Generates a Level 1 problem (Type 2 from spec).
    Concept: Determine the reasonableness of a total cost given a fixed-price item
             and a variable-quantity item, where all item prices are directly provided.
    """
    name = random.choice(["巴奈", "小華", "阿明"])
    place = random.choice(["水族館", "文具店", "玩具店"])
    fixed_item_name = random.choice(["魚缸", "鉛筆盒", "積木組"])
    fixed_item_price = random.randint(80, 250)
    fixed_item_qty = 1 # Matches example, one fixed item
    variable_item_name = random.choice(["孔雀魚", "原子筆", "小汽車"])
    variable_item_price = random.choice([5, 10, 15, 20, 25, 30]) # Ensures divisibility check is meaningful, min 5
    num_variable_items_actual = random.randint(3, 12)

    base_cost = fixed_item_price * fixed_item_qty
    actual_total_cost = base_cost + (num_variable_items_actual * variable_item_price)

    is_reasonable = random.choice([True, False])
    proposed_total_cost = 0
    if is_reasonable:
        proposed_total_cost = actual_total_cost
    else:
        # Ensures remainder is not 0. variable_item_price is >= 5, so variable_item_price - 1 >= 4.
        proposed_total_cost = actual_total_cost + random.randint(1, variable_item_price - 1)

    question_text = (
        f"{name}去{place}買{variable_item_name}，收費如右表：{fixed_item_name} {fixed_item_price} 元／個，"
        f"{variable_item_name} {variable_item_price} 元／隻。{name}買了 {fixed_item_qty} 個{fixed_item_name}跟數隻{variable_item_name}，"
        f"結帳時老闆跟他收了 {proposed_total_cost} 元。請問收費 {proposed_total_cost} 元是否合理？"
    )

    correct_answer_str = "合理" if is_reasonable else "不合理"

    return {
        'question_text': question_text,
        'answer': correct_answer_str,
        'correct_answer': correct_answer_str
    }

def generate_type_1_problem():
    """
    Generates a Level 2 problem (Type 1 from spec).
    Concept: Determine the reasonableness of a total cost given two types of items
             with different quantities, where one item's price is derived relative to the other.
    """
    person_name = random.choice(["琦瑋", "小玉", "志明"])
    place = random.choice(["游泳池", "遊樂園", "電影院"])
    item_type1_name = random.choice(["全票", "成人票", "一般票"])
    item_type1_qty = random.randint(2, 5)
    item_type2_name = random.choice(["優待票", "兒童票", "學生票"])
    price_diff = random.choice([20, 30, 40, 50, 60])
    is_type1_more_expensive = random.choice([True, False])

    item_type1_price = 0
    item_type2_price = 0

    if is_type1_more_expensive:
        # Ensure item_type2_price > 10.
        # item_type1_price - price_diff > 10  => item_type1_price > price_diff + 10
        # The lower bound for item_type1_price should be at least (price_diff + 11) to guarantee item_type2_price >= 11.
        item_type1_price = random.randint(max(100, price_diff + 11), 300)
        item_type2_price = item_type1_price - price_diff
    else:
        item_type1_price = random.randint(100, 300)
        item_type2_price = item_type1_price + price_diff
    
    # item_type2_price is guaranteed to be > 10:
    # If is_type1_more_expensive is True, it's >= 11 by generation logic.
    # If is_type1_more_expensive is False, it's item_type1_price (>=100) + price_diff (>=20) = >=120.

    num_item_type2_actual = random.randint(3, 10)

    base_cost = item_type1_price * item_type1_qty
    actual_total_cost = base_cost + (num_item_type2_actual * item_type2_price)

    is_reasonable = random.choice([True, False])
    proposed_total_cost = 0
    if is_reasonable:
        proposed_total_cost = actual_total_cost
    else:
        # Ensures remainder is not 0. item_type2_price is guaranteed > 10, so item_type2_price - 1 >= 10.
        proposed_total_cost = actual_total_cost + random.randint(1, item_type2_price - 1)

    price_comparison_phrase = ""
    if is_type1_more_expensive:
        price_comparison_phrase = f"貴 ${price_diff}$ 元"
    else:
        price_comparison_phrase = f"便宜 ${price_diff}$ 元"

    question_text = (
        f"{person_name}和家人去{place}，買了 {item_type1_qty} 張{item_type1_name}和若干張{item_type2_name}，"
        f"已知一張{item_type1_name} ${item_type1_price}$ 元比一張{item_type2_name}{price_comparison_phrase}，"
        f"{person_name}計算後認為應付 {proposed_total_cost} 元，請問付費 {proposed_total_cost} 元是否合理？"
    )

    correct_answer_str = "合理" if is_reasonable else "不合理"

    return {
        'question_text': question_text,
        'answer': correct_answer_str,
        'correct_answer': correct_answer_str
    }

def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        # Level 1 problems are based on Example 2 (Type 2 in this plan)
        return generate_type_2_problem()
    elif level == 2:
        # Level 2 problems are based on Example 1 (Type 1 in this plan)
        return generate_type_1_problem()
    else:
        raise ValueError("Invalid level. Level must be 1 or 2.")

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
