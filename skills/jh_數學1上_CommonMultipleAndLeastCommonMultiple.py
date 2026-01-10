# ==============================================================================
# ID: jh_數學1上_CommonMultipleAndLeastCommonMultiple
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 65.41s | RAG: 8 examples
# Created At: 2026-01-09 13:22:00
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

# ==============================================================================
# Helper Functions & Constants
# ==============================================================================

# Helper to format numbers, especially negatives (though not used in these specific problems)

def _get_prime_factors(n):
    factors = {}
    if n == 1:
        return {} # 1 has no prime factors in the usual sense
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

# Helper to format prime factorization into LaTeX string
def _format_prime_factorization(factors_dict):
    if not factors_dict:
        return "1" # Represents the number 1
    parts = []
    for prime in sorted(factors_dict.keys()):
        exponent = factors_dict[prime]
        if exponent == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{{{exponent}}}")
    return " \\times ".join(parts)

# Helper to calculate LCM of two numbers
def _lcm(a, b):
    return (a * b) // math.gcd(a, b)

# Helper to calculate LCM of three numbers
def _lcm_three(a, b, c):
    return _lcm(_lcm(a, b), c)

# Helper to calculate LCM from prime factorizations (dicts)
def _lcm_prime_factors(factors1, factors2, factors3=None):
    lcm_factors = {}
    all_primes = set(factors1.keys()) | set(factors2.keys())
    if factors3:
        all_primes |= set(factors3.keys())

    for p in all_primes:
        max_exponent = max(factors1.get(p, 0), factors2.get(p, 0))
        if factors3:
            max_exponent = max(max_exponent, factors3.get(p, 0))
        if max_exponent > 0: # Only include primes with positive exponents
            lcm_factors[p] = max_exponent
    return lcm_factors

# Helper to calculate GCD from prime factorizations (dicts)
def _gcd_prime_factors(factors1, factors2):
    gcd_factors = {}
    common_primes = set(factors1.keys()) & set(factors2.keys())
    for p in common_primes:
        min_exponent = min(factors1.get(p, 0), factors2.get(p, 0))
        if min_exponent > 0: # Only include primes with positive exponents
            gcd_factors[p] = min_exponent
    return gcd_factors

# Helper to get number from prime factorization dict
def _get_number_from_prime_factors(factors_dict):
    num = 1
    for p, e in factors_dict.items():
        num *= (p ** e)
    return num

# Common prime bases for factorization problems
COMMON_PRIMES = [2, 3, 5, 7]

# Function to check if candidate factors are a multiple of base factors
def _is_multiple_of_prime_factors(candidate_factors, base_factors):
    for prime, base_exp in base_factors.items():
        if candidate_factors.get(prime, 0) < base_exp:
            return False
    return True

# Ensure distinct numbers for problem generation
def _get_distinct_numbers(count, min_val, max_val):
    numbers = set()
    while len(numbers) < count:
        numbers.add(random.randint(min_val, max_val))
    return sorted(list(numbers))

# ==============================================================================
# Problem Type Implementations (Level 1)
# ==============================================================================

def generate_type_1_problem():
    """
    Level 1: Listing multiples, identifying common multiples up to a limit,
    and finding the Least Common Multiple (LCM) of two or three numbers.
    Understanding the relationship between common multiples and LCM.
    """
    nums = _get_distinct_numbers(3, 3, 15)
    num1, num2, num3 = nums[0], nums[1], nums[2]
    limit = random.randint(50, 150)

    lcm_val = _lcm_three(num1, num2, num3)

    multiples1 = [i for i in range(num1, limit + 1, num1)]
    multiples2 = [i for i in range(num2, limit + 1, num2)]
    multiples3 = [i for i in range(num3, limit + 1, num3)]

    common_multiples = [i for i in range(lcm_val, limit + 1, lcm_val)]

    question_text = (
        f"1. 分別列出 1 到 {limit} 的整數中，{num1}、{num2}、{num3} 三數的倍數，並圈出它們的公倍數。\n"
        f"2. 以 $[ {num1} , {num2} , {num3} ]$ 表示 {num1}、{num2}、{num3} 的最小公倍數，則 $[ {num1} , {num2} , {num3} ]$=？\n"
        f"3. 第 1 題所圈出的公倍數與第 2 題所求的最小公倍數有何關係？"
    )

    answer_text = (
        f"1.\n"
        f"   {num1} 的倍數: {', '.join(map(str, multiples1))}\n"
        f"   {num2} 的倍數: {', '.join(map(str, multiples2))}\n"
        f"   {num3} 的倍數: {', '.join(map(str, multiples3))}\n"
        f"   公倍數: {', '.join(map(str, common_multiples))}\n"
        f"2. {lcm_val}\n"
        f"3. 公倍數是最小公倍數的倍數。"
    )

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1: Direct calculation of the Least Common Multiple (LCM) for two or three positive integers.
    """
    nums = _get_distinct_numbers(3, 20, 80)
    a, b, c = nums[0], nums[1], nums[2]

    lcm_ab = _lcm(a, b)
    lcm_abc = _lcm_three(a, b, c)

    question_text = (
        f"求下列各組數的最小公倍數。\n"
        f"⑴ {a}、{b}\n"
        f"⑵ {a}、{b}、{c}"
    )

    answer_text = (
        f"⑴ {lcm_ab}\n"
        f"⑵ {lcm_abc}"
    )

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 1: Identifying multiples of a number given in prime factorization form.
    A number X is a multiple of Y if all prime factors of Y are present in X
    with at least the same or higher exponents.
    """
    p1, p2 = random.sample(COMMON_PRIMES, 2)
    exp1_base = random.randint(1, 3)
    exp2_base = random.randint(1, 3)
    base_factors = {p1: exp1_base, p2: exp2_base}
    base_num_formatted = _format_prime_factorization(base_factors)

    candidates = []
    
    # Generate 5 candidates
    for _ in range(5):
        candidate_factors = {}
        # Vary exponents around base, allowing for less or more
        candidate_factors[p1] = random.randint(exp1_base - 1, exp1_base + 2)
        candidate_factors[p2] = random.randint(exp2_base - 1, exp2_base + 2)

        # Introduce other primes sometimes
        other_primes = [p for p in COMMON_PRIMES if p not in [p1, p2]]
        if other_primes and random.random() < 0.5:
            candidate_factors[random.choice(other_primes)] = random.randint(1, 2)
        
        # Remove primes with 0 or negative exponents (not valid in prime factorization)
        candidate_factors = {p: e for p, e in candidate_factors.items() if e > 0}
        candidates.append(candidate_factors)

    # Ensure there's at least one correct answer
    if not any(_is_multiple_of_prime_factors(c, base_factors) for c in candidates):
        correct_candidate_factors = {p1: exp1_base + random.randint(0,1), p2: exp2_base + random.randint(0,1)}
        other_primes = [p for p in COMMON_PRIMES if p not in [p1, p2]]
        if other_primes and random.random() < 0.5:
            correct_candidate_factors[random.choice(other_primes)] = random.randint(1, 2)
        correct_candidate_factors = {p: e for p, e in correct_candidate_factors.items() if e > 0}
        
        replace_idx = random.randint(0, len(candidates) - 1)
        candidates[replace_idx] = correct_candidate_factors

    correct_answers_formatted = []
    for i, candidate_factors in enumerate(candidates):
        if _is_multiple_of_prime_factors(candidate_factors, base_factors):
            correct_answers_formatted.append(f"{chr(ord('⑴')+i)}")

    question_text = (
        f"下列各數中，哪些是 $ {base_num_formatted} $ 的倍數？\n" +
        "\n".join([f"({chr(ord('⑴')+i)}) $ {_format_prime_factorization(c)} $" for i, c in enumerate(candidates)])
    )
    
    answer_text = " 和 ".join(correct_answers_formatted)
    if not answer_text:
        answer_text = "無"

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_4_problem():
    """
    Level 1: Similar to Type 3, identifying multiples from a list of numbers given in prime factorization form.
    Reinforces the understanding of prime factor exponents for multiples.
    """
    p1, p2 = random.sample(COMMON_PRIMES, 2)
    exp1_base = random.randint(1, 3)
    exp2_base = random.randint(1, 3)
    base_factors = {p1: exp1_base, p2: exp2_base}
    base_num_formatted = _format_prime_factorization(base_factors)

    candidates = []
    
    # Generate 4 candidates
    for _ in range(4):
        candidate_factors = {}
        candidate_factors[p1] = random.randint(exp1_base - 1, exp1_base + 2)
        candidate_factors[p2] = random.randint(exp2_base - 1, exp2_base + 2)

        other_primes = [p for p in COMMON_PRIMES if p not in [p1, p2]]
        if other_primes and random.random() < 0.5:
            candidate_factors[random.choice(other_primes)] = random.randint(1, 2)
        
        candidate_factors = {p: e for p, e in candidate_factors.items() if e > 0}
        candidates.append(candidate_factors)

    # Ensure at least one correct answer
    if not any(_is_multiple_of_prime_factors(c, base_factors) for c in candidates):
        correct_candidate_factors = {p1: exp1_base + random.randint(0,1), p2: exp2_base + random.randint(0,1)}
        other_primes = [p for p in COMMON_PRIMES if p not in [p1, p2]]
        if other_primes and random.random() < 0.5:
            correct_candidate_factors[random.choice(other_primes)] = random.randint(1, 2)
        correct_candidate_factors = {p: e for p, e in correct_candidate_factors.items() if e > 0}
        
        replace_idx = random.randint(0, len(candidates) - 1)
        candidates[replace_idx] = correct_candidate_factors

    correct_answers_formatted = []
    for candidate_factors in candidates:
        if _is_multiple_of_prime_factors(candidate_factors, base_factors):
            correct_answers_formatted.append(f"$ {_format_prime_factorization(candidate_factors)} $")

    question_text = (
        f"下列各數中，哪些是 $ {base_num_formatted} $ 的倍數？\n" +
        "、".join([f"$ {_format_prime_factorization(c)} $" for c in candidates])
    )
    
    answer_text = " 與 ".join(correct_answers_formatted)
    if not answer_text:
        answer_text = "無"

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_5_problem():
    """
    Level 1: Calculating the Least Common Multiple (LCM) of two or three numbers
    when they are given in their standard prime factorization form.
    """
    primes = random.sample(COMMON_PRIMES + [11, 13], 3)
    p1, p2, p3 = primes[0], primes[1], primes[2]

    factors_a = {p1: random.randint(1, 3)}
    if random.random() < 0.7:
        factors_a[p2] = random.randint(0, 2)
    factors_a = {p: e for p, e in factors_a.items() if e > 0}

    factors_b = {p1: random.randint(0, 2)}
    factors_b[p2] = random.randint(1, 3)
    if random.random() < 0.7:
        factors_b[p3] = random.randint(1, 2)
    factors_b = {p: e for p, e in factors_b.items() if e > 0}
    
    factors_c = {p1: random.randint(0, 2)}
    factors_c[p3] = random.randint(1, 3)
    if random.random() < 0.5:
        factors_c[random.choice([11,13])] = 1
    factors_c = {p: e for p, e in factors_c.items() if e > 0}

    lcm_ab_factors = _lcm_prime_factors(factors_a, factors_b)
    lcm_abc_factors = _lcm_prime_factors(factors_a, factors_b, factors_c)

    formatted_a = _format_prime_factorization(factors_a)
    formatted_b = _format_prime_factorization(factors_b)
    formatted_c = _format_prime_factorization(factors_c)

    question_text = (
        f"利用標準分解式求最小公倍數\n"
        f"求下列各組數的最小公倍數，並以標準分解式表示。\n"
        f"⑴ a=${formatted_a}$、b=${formatted_b}$\n"
        f"⑵ a=${formatted_a}$、b=${formatted_b}$、c=${formatted_c}$"
    )

    answer_text = (
        f"⑴ $ {_format_prime_factorization(lcm_ab_factors)} $\n"
        f"⑵ $ {_format_prime_factorization(lcm_abc_factors)} $"
    )

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

def generate_type_6_problem():
    """
    Level 1: Similar to Type 5, calculating LCM from prime factorizations,
    but with a slightly different input format using bracket notation for LCM.
    """
    primes_set1 = random.sample(COMMON_PRIMES, 2)
    p1_1, p1_2 = primes_set1[0], primes_set1[1]
    
    factors_x = {p1_1: random.randint(2, 4)}
    factors_y = {p1_2: random.randint(2, 4)}
    
    lcm_xy_factors = _lcm_prime_factors(factors_x, factors_y)

    primes_set2 = random.sample(COMMON_PRIMES + [11, 13], 3)
    p2_1, p2_2, p2_3 = primes_set2[0], primes_set2[1], primes_set2[2]

    factors_p = {p2_1: 1, p2_2: random.randint(1, 2)}
    factors_p = {p: e for p, e in factors_p.items() if e > 0}

    factors_q = {p2_1: random.randint(2, 3), p2_2: random.randint(2, 4)}
    if random.random() < 0.7:
        factors_q[p2_3] = random.randint(1, 2)
    factors_q = {p: e for p, e in factors_q.items() if e > 0}

    factors_r = {p2_3: random.randint(1, 2), p2_1: 1, p2_2: 1}
    factors_r = {p: e for p, e in factors_r.items() if e > 0}

    lcm_pqr_factors = _lcm_prime_factors(factors_p, factors_q, factors_r)

    question_text = (
        f"求下列各組數的最小公倍數，並以標準分解式表示。\n"
        f"⑴ $[ {_format_prime_factorization(factors_x)} , {_format_prime_factorization(factors_y)} ]=$\n"
        f"⑵ $[ {_format_prime_factorization(factors_p)} , {_format_prime_factorization(factors_q)} , {_format_prime_factorization(factors_r)} ]=$"
    )

    answer_text = (
        f"⑴ $ {_format_prime_factorization(lcm_xy_factors)} $\n"
        f"⑵ $ {_format_prime_factorization(lcm_pqr_factors)} $"
    )

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 1
    }

# ==============================================================================
# Problem Type Implementations (Level 2)
# ==============================================================================

def generate_type_7_problem():
    """
    Level 2: Multi-step problem involving calculating both GCD and LCM from prime factorizations,
    then verifying the property that the product of two numbers equals the product of their GCD and LCM:
    a * b = (a, b) * [a, b].
    """
    primes = random.sample(COMMON_PRIMES + [11, 13], 3)
    p1, p2, p3 = primes[0], primes[1], primes[2]

    factors_a = {p1: random.randint(2, 4), p2: random.randint(1, 3)}
    factors_a = {p: e for p, e in factors_a.items() if e > 0}

    factors_b = {p1: random.randint(1, 3), p2: random.randint(2, 4)}
    if random.random() < 0.7:
        factors_b[p3] = random.randint(1, 2)
    factors_b = {p: e for p, e in factors_b.items() if e > 0}

    a_val = _get_number_from_prime_factors(factors_a)
    b_val = _get_number_from_prime_factors(factors_b)

    gcd_factors = _gcd_prime_factors(factors_a, factors_b)
    lcm_factors = _lcm_prime_factors(factors_a, factors_b)

    gcd_val = _get_number_from_prime_factors(gcd_factors)
    lcm_val = _get_number_from_prime_factors(lcm_factors)
    product_gcd_lcm_factors = _get_prime_factors(gcd_val * lcm_val)

    product_ab_factors = _get_prime_factors(a_val * b_val)

    formatted_a = _format_prime_factorization(factors_a)
    formatted_b = _format_prime_factorization(factors_b)

    question_text = (
        f"已知 a=${formatted_a}$、b=${formatted_b}$，回答下列問題。\n"
        f"⑴ 利用標準分解式求 a 和 b 的最大公因數與最小公倍數。\n"
        f"⑵ 分別以標準分解式表示 $( a , b ) \\times [ a , b ]$ 與 $a \\times b$。\n"
        f"⑶ 由第⑵題中，你有什麼發現？"
    )

    answer_text = (
        f"⑴ $( a , b ) = {_format_prime_factorization(gcd_factors)}$ , $[ a , b ] = {_format_prime_factorization(lcm_factors)}$\n"
        f"⑵ $( a , b ) \\times [ a , b ] = {_format_prime_factorization(product_gcd_lcm_factors)}$ , $a \\times b = {_format_prime_factorization(product_ab_factors)}$\n"
        f"⑶ $( a , b ) \\times [ a , b ] = a \\times b$ (最大公因數與最小公倍數的乘積等於兩數的乘積)"
    )

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 2
    }

def generate_type_8_problem():
    """
    Level 2: Inverse problem applying the property a * b = (a, b) * [a, b]
    to find the Greatest Common Divisor (GCD) when the product of two numbers
    and their Least Common Multiple (LCM) are given.
    """
    while True:
        num1 = random.randint(6, 30)
        num2 = random.randint(6, 30)
        # Ensure distinct numbers, non-trivial GCD, and manageable LCM
        if num1 != num2 and math.gcd(num1, num2) > 1 and _lcm(num1, num2) < 300:
             break

    product_ab = num1 * num2
    lcm_ab = _lcm(num1, num2)
    gcd_ab = math.gcd(num1, num2) # This is the target answer

    assert product_ab == gcd_ab * lcm_ab # Sanity check

    question_text = (
        f"已知兩正整數 a、b，其中 $a \\times b = {product_ab}$、$[ a , b ] = {lcm_ab}$，則 a、b 兩數的最大公因數為何？"
    )

    answer_text = str(gcd_ab)

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
            generate_type_4_problem,
            generate_type_5_problem,
            generate_type_6_problem
        ]
        return random.choice(problem_types)()
    elif level == 2:
        problem_types = [
            generate_type_7_problem,
            generate_type_8_problem
        ]
        return random.choice(problem_types)()
    else:
        raise ValueError("Invalid level. Please choose level 1 or 2.")

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    try:
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # Fallback to string comparison if float conversion fails
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}

