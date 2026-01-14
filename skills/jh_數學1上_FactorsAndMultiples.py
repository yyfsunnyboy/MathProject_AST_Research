# ==============================================================================
# ID: jh_數學1上_FactorsAndMultiples
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 31.04s | RAG: 4 examples
# Created At: 2026-01-09 14:06:49
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


# Problem Type Implementations for jh_數學1上_FactorsAndMultiples
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1 Problem Type: List all positive factors of a given positive integer.
    Based on Ex 1: "將 54 寫成 a×b，其中 a、b 為正整數，並由小到大寫出 54 的所有因數。"
    """
    n = random.randint(20, 100)
    factors_list = get_positive_factors(n)
    
    question_text = f"將 {n} 寫成 a×b，其中 a、b 為正整數，並由小到大寫出 {n} 的所有因數。"
    answer_str = ", ".join(map(str, factors_list))
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1 Problem Type: List all positive factors of a given positive integer.
    Based on Ex 2: "將 36 寫成 c×d，其中 c、d 為正整數，並由小到大寫出 36 的所有因數。"
    (Conceptually identical to Type 1 but with different variable names in question)
    """
    n = random.randint(20, 100)
    factors_list = get_positive_factors(n)
    
    question_text = f"將 {n} 寫成 c×d，其中 c、d 為正整數，並由小到大寫出 {n} 的所有因數。"
    answer_str = ", ".join(map(str, factors_list))
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 2 Problem Type: Given a partial, sorted list of factors for M,
    identify missing factors (a, b) and M.
    Based on Ex 3: "有一正整數 M 的所有因數由小到大排列為 1、2、3、a、6、b、15、M，則 a、b 的值為何？"
    """
    # Curated list of numbers that fit the specific pattern 1,2,3,a,6,b,15,M
    # For M=30, factors are [1, 2, 3, 5, 6, 10, 15, 30]
    # This means factors[0]=1, factors[1]=2, factors[2]=3, factors[4]=6, factors[6]=15
    # And a=factors[3]=5, b=factors[5]=10, M=factors[7]=30
    num_M_candidates = [30] # As per spec, can be extended if other numbers fit the pattern
    num_M = random.choice(num_M_candidates)
    
    factors = get_positive_factors(num_M)
    
    # Ensure the factors list has enough elements and matches the pattern
    # With num_M_candidates = [30], this condition is always met.
    if not (len(factors) >= 8 and factors[0]==1 and factors[1]==2 and 
            factors[2]==3 and factors[4]==6 and factors[6]==15):
        # This case should ideally not be hit with the curated list [30]
        # For robustness, if candidates were expanded, validation would be needed.
        raise ValueError("Selected number does not fit the Type 3 factor pattern.")

    a_val = factors[3]
    b_val = factors[5]
    M_val = factors[-1] # The last factor is M itself (which is num_M)

    question_text = f"有一正整數 M 的所有因數由小到大排列為 1、2、3、a、6、b、15、{M_val}，則 a、b 的值為何？"
    answer_str = f"a={a_val}, b={b_val}"
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str,
        "difficulty": 2
    }

def generate_type_4_problem():
    """
    Level 2 Problem Type: Given a partial, sorted list of factors for N,
    identify missing factor (c) and N.
    Based on Ex 4: "有一正整數 N 的所有因數由小到大排列為 1、2、c、8、N，則 c、N 的值為何？"
    """
    # Curated list of numbers that fit the specific pattern 1,2,c,8,N
    # For N=16, factors are [1, 2, 4, 8, 16]
    # This means factors[0]=1, factors[1]=2, factors[3]=8
    # And c=factors[2]=4, N=factors[4]=16
    num_N_candidates = [16] # As per spec, can be extended if other numbers fit the pattern
    num_N = random.choice(num_N_candidates)
    
    factors = get_positive_factors(num_N)

    # Ensure the factors list has enough elements and matches the pattern
    # With num_N_candidates = [16], this condition is always met.
    if not (len(factors) >= 5 and factors[0]==1 and factors[1]==2 and factors[3]==8):
        # This case should ideally not be hit with the curated list [16]
        raise ValueError("Selected number does not fit the Type 4 factor pattern.")
        
    c_val = factors[2]
    N_val = factors[-1] # The last factor is N itself (which is num_N)

    question_text = f"有一正整數 N 的所有因數由小到大排列為 1、2、c、8、{N_val}，則 c、N 的值為何？"
    answer_str = f"c={c_val}, N={N_val}"
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher for jh_數學1上_FactorsAndMultiples skill.
    - Level 1: Basic concepts, direct calculations (listing all factors).
    - Level 2: Advanced applications, multi-step problems (identifying missing factors).
    """
    if level == 1:
        problem_type_func = random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
        ])
    elif level == 2:
        problem_type_func = random.choice([
            generate_type_3_problem,
            generate_type_4_problem,
        ])
    else:
        raise ValueError("Invalid level. Please choose level 1 or 2.")
    
    return problem_type_func()

# ==============================================================================
# Standard Answer Checker
# ==============================================================================

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    if user == correct:
        return {"correct": True, "result": "正確！"}
        
    try:
        # This block is primarily for numeric answers and may not apply to all string formats
        # e.g., "a=5,b=10" will fail float conversion.
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch cases where conversion to float fails (e.g., "a=5,b=10" or "1,2,3")
        pass
        
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}

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
    except:
        return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
