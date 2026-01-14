# ==============================================================================
#ID: jh_數學1上_RepresentingQuantitiesWithAlgebraicExpressions
#Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
#Duration: 51.11s | RAG: 6 examples
#Created At: 2026-01-09 21:33:58
#Fix Status: [Clean Pass]
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





# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    val_var_char = random.choice(['a', 'b', 'x', 'y', 'z'])
    val_num = random.randint(5, 30)
    val_operation_type = random.choice(['add', 'subtract', 'multiply', 'divide'])

    q_text = ""
    ans = ""

    if val_operation_type == 'add':
        q_text = f"一件商品 ${val_var_char}$ 元，漲價 ${val_num}$ 元，則現在的價格為 ______ 元。"
        ans = f"{val_var_char}+{val_num}"
    elif val_operation_type == 'subtract':
        q_text = f"一本書 ${val_var_char}$ 元，降價 ${val_num}$ 元，則現在的價格為 ______ 元。"
        ans = f"{val_var_char}-{val_num}"
    elif val_operation_type == 'multiply':
        q_text = f"每天讀 ${val_num}$ 頁書，連續讀 ${val_var_char}$ 天，總共讀了 ______ 頁。"
        ans = f"{val_num}{val_var_char}"
    elif val_operation_type == 'divide':
        q_text = f"總共有 ${val_var_char}$ 個蘋果，平分給 ${val_num}$ 個人，則每人分到 ______ 個。"
        ans = f"{val_var_char}/{val_num}"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}

def generate_type_2_problem():
    val_var_char = random.choice(['a', 'b', 'x', 'y', 'z'])
    
    # Add 'one' to coeff_type to explicitly allow coeff = 1, as the answer logic for it exists.
    val_coeff_type = random.choice(['pos_int', 'neg_one', 'float', 'neg_float', 'fraction', 'neg_int', 'one'])
    
    val_coeff = 0 # Initialize
    if val_coeff_type == 'pos_int':
        val_coeff = random.randint(2, 20)
    elif val_coeff_type == 'neg_one':
        val_coeff = -1
    elif val_coeff_type == 'float':
        val_coeff = round(random.uniform(0.1, 5.0), 1)
    elif val_coeff_type == 'neg_float':
        val_coeff = round(random.uniform(-5.0, -0.1), 1)
    elif val_coeff_type == 'fraction':
        val_coeff = get_random_fraction(1, 5) # get_random_fraction usually returns positive fractions
    elif val_coeff_type == 'neg_int':
        val_coeff = random.randint(-20, -2)
    elif val_coeff_type == 'one':
        val_coeff = 1
    
    q_text = f"簡記下列各代數式: ${to_latex(val_coeff)} \\times {val_var_char}$"
    
    ans = ""
    if val_coeff == 1:
        ans = val_var_char
    elif val_coeff == -1:
        ans = f"-{val_var_char}"
    else:
        ans = f"{to_latex(val_coeff)}{val_var_char}"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}

def generate_type_3_problem():
    val_var_char = random.choice(['x', 'y'])
    
    # coeff1: random.randint(-10, 10) (excluding 0, 1, -1)
    val_coeff1 = 0
    while val_coeff1 in [0, 1, -1]:
        val_coeff1 = random.randint(-10, 10)
    
    val_constant = random.randint(-20, 20)
    val_is_division = random.choice([True, False])

    q_text = ""
    ans = ""

    if not val_is_division: # Pattern 1 (Multiplication)
        q_text = f"簡記下列各代數式: ${fmt_num(val_coeff1)} \\times {val_var_char} {fmt_num(val_constant, '+')}$"
        ans = f"{fmt_num(val_coeff1)}{val_var_char}{fmt_num(val_constant, '+')}"
    else: # Pattern 2 (Division)
        val_divisor_frac = get_random_fraction(1, 5) # Returns positive fraction
        
        q_text = f"簡記下列各代數式: ${val_var_char} \\div {to_latex(val_divisor_frac)} {fmt_num(val_constant, '+')}$"
        
        # Answer: var_char / (a/b) = var_char * (b/a)
        val_reciprocal_frac = Fraction(val_divisor_frac.denominator, val_divisor_frac.numerator)
        
        coeff_str = ""
        if val_reciprocal_frac == 1:
            coeff_str = "" # For 'x' instead of '1x'
        elif val_reciprocal_frac == -1: # Highly unlikely as val_divisor_frac is positive
            coeff_str = "-" # For '-x' instead of '-1x'
        else:
            coeff_str = to_latex(val_reciprocal_frac)
        
        ans = f"{coeff_str}{val_var_char}{fmt_num(val_constant, '+')}"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}

def generate_type_4_problem():
    val_spent_amount = random.randint(50, 500)
    val_discount_percent = random.choice([70, 75, 80, 85, 90])

    q_text = f"小明以 ${val_discount_percent}\\%$ 優待的價錢買了一些文具，共花了 ${val_spent_amount}$ 元。若沒有此優待，則小明原本應付多少元？"
    
    # Original price = spent_amount / (discount_percent / 100)
    # Original price = spent_amount * (100 / discount_percent)
    val_original_fraction = Fraction(100, val_discount_percent)
    
    # Using the multiplication form with simplified fraction as suggested in spec.
    ans = f"{val_spent_amount} \\times {to_latex(val_original_fraction)}"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}

def generate_type_5_problem():
    val_var_char1 = random.choice(['x', 'y'])
    val_var_char2 = random.choice(['a', 'b']) # These variable sets are distinct, so they will naturally be different.
    val_multiplier = random.randint(2, 5)
    val_adder_subtractor = random.randint(2, 15)
    val_quantity = random.randint(2, 5)
    val_difference = random.randint(5, 30)
    val_problem_type = random.choice(['type_a', 'type_b'])

    q_text = ""
    ans = ""

    if val_problem_type == 'type_a':
        q_text = f"已知小明的體重是 ${val_var_char1}$ 公斤，若爸爸的體重是小明體重的 ${val_multiplier}$ 倍多 ${val_adder_subtractor}$ 公斤，則爸爸的體重是多少公斤？"
        ans = f"{val_multiplier}{val_var_char1}+{val_adder_subtractor}"
    elif val_problem_type == 'type_b':
        q_text = f"已知一枝鉛筆賣 ${val_var_char2}$ 元，若一枝原子筆比一枝鉛筆貴 ${val_difference}$ 元，則買 ${val_quantity}$ 枝原子筆要多少元？"
        ans = f"{val_quantity}({val_var_char2}+{val_difference})"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}

def generate_type_6_problem():
    val_var_char1 = random.choice(['x', 'y'])
    val_var_char2 = random.choice(['a', 'b']) # These variable sets are distinct.
    val_num_sides = 4 # Fixed for square
    val_num_people = random.randint(3, 7)
    val_added_items = random.randint(1, 10)
    val_problem_type = random.choice(['type_a', 'type_b'])

    q_text = ""
    ans = ""

    if val_problem_type == 'type_a':
        q_text = f"已知一正方形周長為 ${val_var_char1}$，則此正方形邊長為何？"
        ans = f"{val_var_char1}/{val_num_sides}"
    elif val_problem_type == 'type_b':
        q_text = f"小翊和朋友一共 ${val_num_people}$ 人，在夜市玩套圈遊戲，已知遊戲每次有 ${val_var_char2}$ 個套圈，若再增加 ${val_added_items}$ 個套圈，就能完全平分給小翊及他的朋友，這樣每人可分得多少個套圈？"
        ans = f"({val_var_char2}+{val_added_items})/{val_num_people}"
    
    return {'question_text': q_text, 'answer': ans, 'correct_answer': ans}


def generate(level=1):
    """
    Dispatches to problem generation functions based on the specified level.
    """
    if level == 1:
        problem_func = random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
        ])
    elif level == 2:
        problem_func = random.choice([
            generate_type_4_problem,
            generate_type_5_problem,
            generate_type_6_problem,
        ])
    else:
        raise ValueError("Invalid level. Choose 1 or 2.")

    return problem_func()

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
