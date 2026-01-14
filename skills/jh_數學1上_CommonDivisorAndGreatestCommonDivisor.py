# ==============================================================================
# ID: jh_數學1上_CommonDivisorAndGreatestCommonDivisor
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 28.05s | RAG: 7 examples
# Created At: 2026-01-09 13:20:54
# Fix Status: [Clean Pass]
# ==============================================================================


import random
import math
from fractions import Fraction

def to_latex(num):
    """Convert number to LaTeX (integers, decimals, fractions, mixed numbers)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            if rem == 0: return f"{sign}{abs(num).numerator // abs(num).denominator}"
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses for LaTeX display"""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

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

# Global constant for prime factorization problems
PRIME_LIST = [2, 3, 5, 7, 11, 13, 17] # Extended slightly for more variety


def _format_prime_factorization(factors_dict):
    """
    Helper to format prime factorization string (e.g., {2:3, 3:1} -> "2^3 \\times 3")
    """
    if not factors_dict: return "1" # GCD of coprime numbers is 1
    parts = []
    for p in sorted(factors_dict.keys()):
        e = factors_dict[p]
        if e == 0: continue # Skip primes with exponent 0
        if e == 1: parts.append(str(p))
        else: parts.append(f"{p}^{{{e}}}")
    return " \\times ".join(parts) if parts else "1"

def _generate_random_prime_factorization_dict(num_primes_min=1, num_primes_max=3, exp_min=1, exp_max=4, prime_list=PRIME_LIST):
    """
    Helper to generate a random prime factorization dictionary.
    """
    num_primes = random.randint(num_primes_min, num_primes_max)
    
    # Ensure distinct primes are chosen
    if len(prime_list) < num_primes:
        raise ValueError("Not enough primes in PRIME_LIST to pick from.")
    
    primes = random.sample(prime_list, num_primes)
    
    factors = {}
    for p in primes:
        factors[p] = random.randint(exp_min, exp_max)
    return factors

def _gcd_prime_factorizations(factors1, factors2):
    """
    Helper to calculate GCD of two prime factorizations (dictionaries).
    """
    gcd_factors = {}
    all_primes = set(factors1.keys()) | set(factors2.keys())
    for p in all_primes:
        e1 = factors1.get(p, 0)
        e2 = factors2.get(p, 0)
        if e1 > 0 and e2 > 0: # Only include common primes
            gcd_factors[p] = min(e1, e2)
    return gcd_factors

def _gcd_prime_factorizations_three(factors1, factors2, factors3):
    """
    Helper to calculate GCD of three prime factorizations (dictionaries).
    """
    gcd_factors = {}
    all_primes = set(factors1.keys()) | set(factors2.keys()) | set(factors3.keys())
    for p in all_primes:
        e1 = factors1.get(p, 0)
        e2 = factors2.get(p, 0)
        e3 = factors3.get(p, 0)
        if e1 > 0 and e2 > 0 and e3 > 0: # Only include common primes
            gcd_factors[p] = min(e1, e2, e3)
    return gcd_factors

def generate_type_1_problem():
    """
    Level 1, Type 1: Find the greatest common divisor (GCD) of two or three positive integers.
    Focuses on direct computation for relatively smaller numbers.
    """
    num_count = random.choice([2, 3])
    numbers = []
    while len(set(numbers)) != num_count: # Ensure numbers are distinct
        numbers = [random.randint(10, 100) for _ in range(num_count)]
    
    numbers_str = ""
    if num_count == 2:
        numbers_str = f"{numbers[0]}、{numbers[1]}"
        gcd_val = math.gcd(numbers[0], numbers[1])
    else: # num_count == 3
        numbers_str = f"{numbers[0]}、{numbers[1]}、{numbers[2]}"
        gcd_val = math.gcd(numbers[0], numbers[1])
        gcd_val = math.gcd(gcd_val, numbers[2])
    
    question_text = f"求 {numbers_str} 的最大公因數。"
    
    return {
        "question_text": question_text,
        "answer": str(gcd_val),
        "correct_answer": str(gcd_val),
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1, Type 2: Determine if two given positive integers are coprime.
    """
    a = random.randint(1, 50)
    b = random.randint(a + 1, 100) # Ensure b > a
    
    is_coprime = (math.gcd(a, b) == 1)
    
    question_text = f"判斷下列各組數是否互質。\n({a}, {b})"
    answer_text = "是" if is_coprime else "否"
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 1, Type 3: Calculate the greatest common divisor (GCD) of two or three positive integers.
    Uses slightly larger numbers than Type 1 to encourage more systematic methods.
    """
    num_count = random.choice([2, 3])
    numbers = []
    while len(set(numbers)) != num_count: # Ensure numbers are distinct
        numbers = [random.randint(50, 200) for _ in range(num_count)]

    numbers_tuple_str = f"({', '.join(map(str, numbers))})"
    
    gcd_val = math.gcd(numbers[0], numbers[1])
    if num_count == 3:
        gcd_val = math.gcd(gcd_val, numbers[2])
    
    question_text = f"求下列各組數的最大公因數。\n{numbers_tuple_str}"
    
    return {
        "question_text": question_text,
        "answer": str(gcd_val),
        "correct_answer": str(gcd_val),
        "difficulty": 1
    }

def generate_type_4_problem():
    """
    Level 2, Type 4: Identify which numbers, given in prime factorization form,
    are factors of a target number also given in prime factorization form.
    """
    target_factors = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=2, exp_min=2, exp_max=4)
    target_num_str = _format_prime_factorization(target_factors)
    
    options = []
    correct_answers = []
    
    # Generate correct options
    num_correct = random.randint(1, 2)
    for _ in range(num_correct):
        factor_option = {}
        for p, e in target_factors.items():
            factor_option[p] = random.randint(0, e) # Exponent can be 0 (meaning prime not present)
        option_str = _format_prime_factorization(factor_option)
        if option_str not in options: # Avoid duplicates
            options.append(option_str)
            correct_answers.append(option_str)
    
    # Generate incorrect options
    num_incorrect = 3 - len(correct_answers) # Total 3 options
    while len(options) < 3:
        incorrect_factor = {}
        # Option 1: Exponent too high for a prime
        if random.random() < 0.5 and target_factors:
            p_to_change = random.choice(list(target_factors.keys()))
            incorrect_factor[p_to_change] = target_factors[p_to_change] + random.randint(1, 2)
            for p, e in target_factors.items():
                if p != p_to_change:
                    incorrect_factor[p] = random.randint(0, e)
        # Option 2: Contains a prime not in target_factors
        else:
            # Ensure new_prime is actually new and not already in target_factors
            available_primes = [p for p in PRIME_LIST if p not in target_factors]
            if available_primes: # Only add if there are available primes
                new_prime = random.choice(available_primes)
                incorrect_factor[new_prime] = random.randint(1, 2)
            
            # Add existing primes with valid or slightly varied exponents
            for p, e in target_factors.items():
                if p not in incorrect_factor: # Don't overwrite if it was p_to_change
                    incorrect_factor[p] = random.randint(0, e)
        
        option_str = _format_prime_factorization(incorrect_factor)
        if option_str not in options: # Avoid duplicates
            options.append(option_str)
        
    random.shuffle(options)
    options_list_str = "\n".join([f"({chr(97+i)}) ${opt}$" for i, opt in enumerate(options)]) # (a) $2^...$
    
    # Map correct answers to their letter labels
    final_correct_labels = []
    for ans_str in correct_answers:
        for i, opt_str in enumerate(options):
            if opt_str == ans_str:
                final_correct_labels.append(chr(97+i))
                break
    final_correct_labels_str = " 和 ".join(sorted(final_correct_labels))
    
    question_text = f"下列各數中，哪些是 ${target_num_str}$ 的因數？\n{options_list_str}"
    
    return {
        "question_text": question_text,
        "answer": final_correct_labels_str,
        "correct_answer": final_correct_labels_str,
        "difficulty": 2
    }

def generate_type_5_problem():
    """
    Level 2, Type 5: Similar to Type 4, but with more options and potentially slightly
    more complex prime factorizations or integer representations.
    """
    PRIME_LIST_EXT = [2, 3, 5, 7, 11, 13, 17] # Slightly extended for variety
    
    target_factors = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=2, exp_max=5, prime_list=PRIME_LIST_EXT)
    target_num_str = _format_prime_factorization(target_factors)
    
    options = []
    correct_answers = []
    
    # Generate correct options (2-3 of them)
    num_correct = random.randint(2, 3)
    for _ in range(num_correct):
        factor_option = {}
        for p, e in target_factors.items():
            factor_option[p] = random.randint(0, e)
        option_str = _format_prime_factorization(factor_option)
        if option_str not in options:
            options.append(option_str)
            correct_answers.append(option_str)
    
    # Generate incorrect options (3-4 of them, total 5-6 options)
    num_total_options = random.randint(5, 6)
    while len(options) < num_total_options:
        incorrect_factor = {}
        if random.random() < 0.6 and target_factors: # Exponent too high
            p_to_change = random.choice(list(target_factors.keys()))
            incorrect_factor[p_to_change] = target_factors[p_to_change] + random.randint(1, 2)
            for p, e in target_factors.items():
                if p != p_to_change:
                    incorrect_factor[p] = random.randint(0, e)
        else: # Contains a prime not in target_factors or mixed
            available_primes = [p for p in PRIME_LIST_EXT if p not in target_factors]
            if available_primes and random.random() < 0.7: # High chance to add a new prime
                new_prime = random.choice(available_primes)
                incorrect_factor[new_prime] = random.randint(1, 2)
            
            for p, e in target_factors.items():
                if p not in incorrect_factor:
                    incorrect_factor[p] = random.randint(0, e) # Include existing primes
                elif p in incorrect_factor and incorrect_factor[p] <= e: # If already added, ensure it's incorrect (e.g. higher exp)
                    incorrect_factor[p] = random.randint(e + 1, e + 2) # Force higher exponent

        option_str = _format_prime_factorization(incorrect_factor)
        if option_str not in options and option_str not in correct_answers: # Avoid duplicates and correct answers
            options.append(option_str)
        
    random.shuffle(options)
    options_list_str = "\n".join([f"({chr(97+i)}) ${opt}$" for i, opt in enumerate(options)])
    
    final_correct_labels = []
    for ans_str in correct_answers:
        for i, opt_str in enumerate(options):
            if opt_str == ans_str:
                final_correct_labels.append(chr(97+i))
                break
    final_correct_labels_str = " 與 ".join(sorted(final_correct_labels))
    
    question_text = f"下列各數中，哪些是 ${target_num_str}$ 的因數？\n{options_list_str}"
    
    return {
        "question_text": question_text,
        "answer": final_correct_labels_str,
        "correct_answer": final_correct_labels_str,
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Level 2, Type 6: Find the greatest common divisor (GCD) of two or three numbers
    given in standard prime factorization form, and express the answer in standard
    prime factorization form.
    """
    num_count = random.choice([2, 3])
    
    factors_a = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)
    factors_b = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)
    
    # Ensure there's at least one common prime factor
    common_primes_ab = set(factors_a.keys()) & set(factors_b.keys())
    if not common_primes_ab:
        prime_to_add = random.choice(PRIME_LIST)
        factors_a[prime_to_add] = random.randint(1, 3)
        factors_b[prime_to_add] = random.randint(1, 3)
    
    num_a_str = _format_prime_factorization(factors_a)
    num_b_str = _format_prime_factorization(factors_b)
    
    if num_count == 2:
        gcd_factors_dict = _gcd_prime_factorizations(factors_a, factors_b)
        question_text_part = f"⑴ a=${num_a_str}$、b=${num_b_str}$"
    else: # num_count == 3
        factors_c = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)
        
        # Ensure at least one common prime factor among all three
        common_primes_all = set(factors_a.keys()) & set(factors_b.keys()) & set(factors_c.keys())
        if not common_primes_all:
            prime_to_add = random.choice(PRIME_LIST)
            factors_a[prime_to_add] = random.randint(1, 3)
            factors_b[prime_to_add] = random.randint(1, 3)
            factors_c[prime_to_add] = random.randint(1, 3)
            
        num_c_str = _format_prime_factorization(factors_c)
        gcd_factors_dict = _gcd_prime_factorizations_three(factors_a, factors_b, factors_c)
        question_text_part = f"⑴ a=${num_a_str}$、b=${num_b_str}$、c=${num_c_str}$"

    gcd_ans_str = _format_prime_factorization(gcd_factors_dict)
    question_text = f"求下列各組數的最大公因數，並以標準分解式表示。\n{question_text_part}"
    
    return {
        "question_text": question_text,
        "answer": gcd_ans_str,
        "correct_answer": gcd_ans_str,
        "difficulty": 2
    }

def generate_type_7_problem():
    """
    Level 2, Type 7: Same as Type 6, but specifically using the `(A, B)` notation for GCD in the question.
    """
    num_count = random.choice([2, 3])
    
    factors_a = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)
    factors_b = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)

    # Ensure at least one common prime factor
    common_primes_ab = set(factors_a.keys()) & set(factors_b.keys())
    if not common_primes_ab:
        prime_to_add = random.choice(PRIME_LIST)
        factors_a[prime_to_add] = random.randint(1, 3)
        factors_b[prime_to_add] = random.randint(1, 3)
    
    num_a_str = _format_prime_factorization(factors_a)
    num_b_str = _format_prime_factorization(factors_b)
    
    if num_count == 2:
        gcd_factors_dict = _gcd_prime_factorizations(factors_a, factors_b)
        question_text_part = f"⑴ ( ${num_a_str}$ , ${num_b_str}$ )="
    else: # num_count == 3
        factors_c = _generate_random_prime_factorization_dict(num_primes_min=2, num_primes_max=3, exp_min=1, exp_max=4)
        
        # Ensure at least one common prime factor among all three
        common_primes_all = set(factors_a.keys()) & set(factors_b.keys()) & set(factors_c.keys())
        if not common_primes_all:
            prime_to_add = random.choice(PRIME_LIST)
            factors_a[prime_to_add] = random.randint(1, 3)
            factors_b[prime_to_add] = random.randint(1, 3)
            factors_c[prime_to_add] = random.randint(1, 3)
            
        num_c_str = _format_prime_factorization(factors_c)
        gcd_factors_dict = _gcd_prime_factorizations_three(factors_a, factors_b, factors_c)
        question_text_part = f"⑴ ( ${num_a_str}$ , ${num_b_str}$ , ${num_c_str}$ )="

    gcd_ans_str = _format_prime_factorization(gcd_factors_dict)
    question_text = f"求下列各組數的最大公因數，並以標準分解式表示。\n{question_text_part}"
    
    return {
        "question_text": question_text,
        "answer": gcd_ans_str,
        "correct_answer": gcd_ans_str,
        "difficulty": 2
    }


def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        # Randomly choose among basic types
        problem_func = random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
        ])
        return problem_func()
    elif level == 2:
        # Randomly choose among advanced types
        problem_func = random.choice([
            generate_type_4_problem,
            generate_type_5_problem,
            generate_type_6_problem,
            generate_type_7_problem,
        ])
        return problem_func()
    else:
        raise ValueError("Invalid level. Please choose 1 or 2.")

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "").replace("\\times", "\\times").replace("$", "")
    correct = correct_answer.strip().replace(" ", "").replace("\\times", "\\times").replace("$", "")
    
    # Simple string comparison for exact matches (especially for prime factorizations)
    if user == correct:
        return {"correct": True, "result": "正確！"}
        
    # Attempt float comparison if it's purely numeric
    try:
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch error if conversion to float fails (e.g., for "是", "否", or prime factor strings)
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
