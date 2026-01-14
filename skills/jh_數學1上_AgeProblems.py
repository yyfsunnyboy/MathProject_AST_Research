# ==============================================================================
# ID: jh_數學1上_AgeProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 32.54s | RAG: 2 examples
# Created At: 2026-01-09 22:47:27
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

def generate_level_1_problem():
    """
    Generates a Level 1 basic age problem.
    Concept: Simple calculation of age in the future or past given current age.
    """
    
    names = ["小明", "小華", "小美", "小玉", "小翔"]
    name = random.choice(names)
    
    current_age = random.randint(10, 60) # A reasonable age range for a person
    years_change = random.randint(3, 15) # Years into future or past
    
    problem_type_choice = random.choice(["future", "past"])
    
    question_text = ""
    correct_answer_val = 0

    if problem_type_choice == "future":
        correct_answer_val = current_age + years_change
        question_text = f"今年{name}是 ${to_latex(current_age)}$ 歲，請問 ${to_latex(years_change)}$ 年後，他會是幾歲？"
    else: # "past"
        # Ensure the person was alive in the past (age > 0)
        # Regenerate if the past age would be non-positive
        while current_age - years_change <= 0:
            current_age = random.randint(10, 60)
            years_change = random.randint(3, 15)
        
        correct_answer_val = current_age - years_change
        question_text = f"今年{name}是 ${to_latex(current_age)}$ 歲，請問 ${to_latex(years_change)}$ 年前，他會是幾歲？"
            
    return {
        'question_text': question_text,
        'answer': str(correct_answer_val),
        'correct_answer': str(correct_answer_val)
    }

def generate_type_1_problem():
    """
    Type 1: Sum of current ages, future age relationship, find age difference.
    Concept: Solve a system of two linear equations.
    """
    
    younger_names = ["小妍", "小明", "小華", "小玉", "小翔"]
    older_names = ["媽媽", "爸爸", "老師", "叔叔", "阿姨"]

    # Ensure names are distinct
    younger_name = random.choice(younger_names)
    # Filter older_names to exclude the chosen younger_name, then pick.
    # If by chance the lists are identical and only one name is left, this handles it.
    possible_older_names = [n for n in older_names if n != younger_name]
    if not possible_older_names: # Fallback if no distinct name is possible (e.g., if lists were identical and short)
        older_name = random.choice(older_names)
    else:
        older_name = random.choice(possible_older_names)

    # Regeneration Logic Loop: Ensure current ages are positive and older person is actually older.
    while True:
        years_future = random.randint(5, 10)
        ratio_future = random.randint(2, 4)
        extra_years_future = random.randint(0, 15)
        
        # Younger person's age in the future, chosen to ensure positive current ages
        younger_age_future = random.randint(10, 25) 
        
        # Derive other variables based on future age
        older_age_future = ratio_future * younger_age_future + extra_years_future
        
        younger_age_current = younger_age_future - years_future
        older_age_current = older_age_future - years_future
        
        # Check regeneration conditions:
        # 1. Younger person's current age must be positive.
        # 2. Older person's current age must be greater than younger person's current age.
        if younger_age_current > 0 and older_age_current > younger_age_current:
            break # Conditions met, exit loop

    # Calculate values needed for the question and answer
    sum_current_ages = younger_age_current + older_age_current
    age_difference = older_age_current - younger_age_current

    question = (
        f"今年{younger_name}和{older_name}的年齡和是 ${to_latex(sum_current_ages)}$ 歲，"
        f"${to_latex(years_future)}$ 年後，{older_name}年齡是{younger_name}年齡的 "
        f"${to_latex(ratio_future)}$ 倍多 ${to_latex(extra_years_future)}$ 歲，"
        f"請問{older_name}和{younger_name}相差多少歲？"
    )
    
    return {
        'question_text': question,
        'answer': str(age_difference),
        'correct_answer': str(age_difference)
    }

def generate_type_2_problem():
    """
    Type 2: Current age difference, past age relationship, find younger's current age.
    Concept: Solve a system of two linear equations.
    """

    younger_names = ["小翔", "小君", "小玉", "小華", "小明"]
    older_names = ["爸爸", "媽媽", "叔叔", "阿姨", "老師"]

    # Ensure names are distinct
    younger_name = random.choice(younger_names)
    possible_older_names = [n for n in older_names if n != younger_name]
    if not possible_older_names: # Fallback
        older_name = random.choice(older_names)
    else:
        older_name = random.choice(possible_older_names)

    # Regeneration Logic Loop: Ensure past and current ages are valid.
    while True:
        years_past = random.randint(3, 8)
        ratio_past = random.randint(3, 10)
        
        # Younger person's age in the past, chosen to ensure positive current ages
        # Must be at least 1 for the ratio to make sense, and allows for years_past to be subtracted.
        younger_age_past = random.randint(2, 10) 
        
        # Derive other variables based on past age
        older_age_past = ratio_past * younger_age_past
        
        younger_age_current = younger_age_past + years_past
        older_age_current = older_age_past + years_past
        
        # Check regeneration conditions:
        # 1. Older person's current age must be greater than younger person's current age.
        #    (Implicitly, younger_age_past > 0 ensures current ages are positive)
        if older_age_current > younger_age_current:
            break # Conditions met, exit loop

    # Calculate value needed for the question
    current_age_difference = older_age_current - younger_age_current

    question = (
        f"已知{younger_name}與{older_name}的年齡相差 ${to_latex(current_age_difference)}$ 歲，"
        f"且 ${to_latex(years_past)}$ 年前，{older_name}年齡恰好是{younger_name}年齡的 "
        f"${to_latex(ratio_past)}$ 倍，"
        f"則{younger_name}現在幾歲？"
    )
    
    return {
        'question_text': question,
        'answer': str(younger_age_current),
        'correct_answer': str(younger_age_current)
    }


def generate(level=1):
    """
    Dispatches to the appropriate problem generator based on the level.
    """
    if level == 1:
        # Implement content for Level 1 as per "LEVEL COMPLETENESS" rule
        return generate_level_1_problem()
    elif level == 2:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem,
        ]
        return random.choice(problem_types)()
    else:
        # Adhere to Architect's Spec for invalid level handling
        raise ValueError("Invalid level. Please choose level 1 or 2.")

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
