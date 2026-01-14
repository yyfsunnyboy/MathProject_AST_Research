# ==============================================================================
# ID: jh_數學1上_DistributionProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 17.95s | RAG: 2 examples
# Created At: 2026-01-09 22:55:10
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

def generate_type_L1_problem():
    """
    Level 1: Simple multiplication for total items in a distribution.
    Concept: Given number of groups and items per group, find the total number of items.
    """
    num_groups = random.randint(5, 15)
    items_per_group = random.randint(10, 25)
    total_items = num_groups * items_per_group
    item_name = random.choice(["鉛筆", "橡皮擦", "貼紙", "糖果", "餅乾"])
    group_name = random.choice(["盒", "包", "堆", "袋", "個"])

    q = f"每{group_name}有 {items_per_group} 枝{item_name}，總共有 {num_groups} {group_name}。請問總共有多少枝{item_name}？"
    a = str(total_items)
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate_type_1_problem():
    """
    Type 1 (Based on Ex 1: Excess and Deficit - Solving for Group Count)
    Concept: Solve for the unknown number of groups given two scenarios where
             distributing items per group leads to an excess in one case and a deficit in another.
    """
    answer_x = random.randint(10, 25)
    per_group_1 = random.randint(20, 35)
    rate_diff = random.randint(2, 5)
    per_group_2 = per_group_1 + rate_diff

    # total_diff_items = (per_group_2 - per_group_1) * answer_x = rate_diff * answer_x
    total_diff_items = answer_x * rate_diff

    # Ensure excess and deficit are positive and sum up to total_diff_items
    excess = random.randint(5, total_diff_items - 1)
    deficit = total_diff_items - excess

    context_group = random.choice(["班級", "盒子", "公車"])
    context_item = random.choice(["學生", "物品", "乘客"])
    school_name = random.choice(["大埔國中", "新華高中", "文山國小"])

    q = f"{school_name}新生編班，{context_group}數固定。若每{context_group} {per_group_1} {context_item}，則多出 {excess} {context_item}；若每{context_group} {per_group_2} {context_item}，則不足 {deficit} {context_item}。請問{context_group}數為多少{context_group}？"
    a = str(answer_x)
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate_type_2_problem():
    """
    Type 2 (Based on Ex 2: Initial Excess, then Adding More to Exact Division - Solving for Recipient Count)
    Concept: Solve for the unknown number of recipients given an initial distribution with an excess,
             and then a second distribution with a different per-recipient amount after adding more items,
             resulting in an exact division.
    """
    answer_x = random.randint(15, 30)
    per_recipient_1 = random.randint(5, 10)
    rate_diff = random.randint(1, 4)
    per_recipient_2 = per_recipient_1 + rate_diff

    # total_diff_items = (per_recipient_2 - per_recipient_1) * answer_x = rate_diff * answer_x
    total_diff_items = answer_x * rate_diff

    # Ensure initial_excess and items_added are positive and sum up to total_diff_items
    initial_excess = random.randint(3, total_diff_items - 1)
    items_added = total_diff_items - initial_excess

    item_name = random.choice(["糖果", "鉛筆", "餅乾", "貼紙"])
    class_name = random.choice(["七年五班", "八年二班", "三年甲班", "四年丙班"])

    q = f"將一包{item_name}平分給{class_name}全班學生，已知每人分到 {per_recipient_1} 顆時，會多出 {initial_excess} 顆{item_name}；若另外再加 {items_added} 顆{item_name}，則每人分到 {per_recipient_2} 顆且恰好分完。請問{class_name}有幾位學生？"
    a = str(answer_x)
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        # Implemented a basic distribution problem for Level 1 as per coding rules.
        return generate_type_L1_problem()
    elif level == 2:
        return random.choice([
            generate_type_1_problem,
            generate_type_2_problem
        ])()
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
