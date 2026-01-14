# ==============================================================================
# ID: jh_數學1上_PrimeNumbersAndPrimeFactorization
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 21.95s | RAG: 8 examples
# Created At: 2026-01-09 14:12:05
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




from itertools import permutations

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


# Internal Helper Functions for Prime Numbers and Prime Factorization
# ==============================================================================

def is_prime(n):
    """Checks if a number n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def get_positive_factors(n):
    """Returns a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    """Returns a dictionary of prime factors and their exponents for n."""
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

# ==============================================================================
# Problem Type Implementations (Level 1)
# ==============================================================================

def generate_type_1_problem():
    """
    Type 1: Identify Prime or Composite Numbers
    Concept: Determine whether given positive integers are prime or composite.
    """
    prime_pool = [p for p in range(10, 101) if is_prime(p)]
    composite_pool = [c for c in range(10, 101) if not is_prime(c)]

    n1 = random.choice(prime_pool)
    
    # Ensure n2 is composite and distinct from n1
    while True:
        n2 = random.choice(composite_pool)
        if n2 != n1:
            break
            
    ans_n1 = "質數" if is_prime(n1) else "合數"
    ans_n2 = "質數" if is_prime(n2) else "合數"
    
    question_text = f"分別判斷 {n1} 和 {n2} 兩數是質數還是合數？"
    correct_answer = f"{n1} 是 {ans_n1}，{n2} 是 {ans_n2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # For direct answer matching
        "correct_answer": correct_answer,
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Type 2: Number of Rectangles from Unit Squares
    Concept: Find the number of distinct rectangular shapes that can be formed from n unit squares.
             This is equivalent to finding the number of unique factor pairs of n.
    """
    n = random.choice([12, 18, 24, 30, 36, 40, 48, 60, 72, 80, 90, 100])
    
    factors = get_positive_factors(n)
    num_rectangles = (len(factors) + 1) // 2 # Number of unique factor pairs
    
    question_text = f"欲將 {n} 個邊長為 1 的小正方形緊密排列拼成矩形，且不會剩下任何小正方形，則可以拼出幾種不同形狀的矩形？"
    correct_answer = f"{num_rectangles} 種"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Type 3: Prime Factorization and List Prime Factors
    Concept: Express a composite number in its standard prime factorization form and list all its unique prime factors.
    """
    # Generate a random composite number between 50 and 500
    while True:
        n = random.randint(50, 500)
        if not is_prime(n):
            break
            
    prime_factorization_dict = get_prime_factorization(n)
    prime_factors_list = sorted(list(prime_factorization_dict.keys()))

    # Convert dictionary to LaTeX standard form string
    latex_factorization = ""
    for prime, exponent in prime_factorization_dict.items():
        if exponent == 1:
            latex_factorization += f"{prime} \\times "
        else:
            latex_factorization += f"{prime}^{{{exponent}}} \\times "
    latex_factorization = latex_factorization.rstrip(" \\times ") # Remove trailing " \times "

    prime_factors_str = "、".join(map(str, prime_factors_list))
    
    correct_answer = f"標準分解式為 ${latex_factorization}$，質因數為 {prime_factors_str}"
    question_text = f"將 {n} 以標準分解式表示，並寫出所有的質因數。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 1
    }

# ==============================================================================
# Problem Type Implementations (Level 2)
# ==============================================================================

def generate_type_4_problem():
    """
    Type 4: Birthday Puzzle with Factorization
    Concept: Given a number N which is the product of four distinct positive integers f1, f2, f3, f4,
             find a permutation of these integers such that f_a + f_b is a valid month (1-12)
             and f_c + f_d is a valid day (1-31).
    """
    while True:
        # Generate 4 distinct small primes to ensure unique factors and manageable sums
        # Primes up to 29 for day sum (max 31) are reasonable.
        primes_pool = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] # Added a few more for flexibility
        if len(primes_pool) < 4: continue # Should not happen

        p1, p2, p3, p4 = random.sample(primes_pool, 4)
        factors = sorted([p1, p2, p3, p4]) # Keep sorted for consistent permutation generation

        valid_solutions = set() # Store (month_sum, day_sum) tuples to check for uniqueness
        
        # Iterate over all permutations of the four factors
        for perm in permutations(factors):
            # Try splitting into two pairs: (perm[0], perm[1]) and (perm[2], perm[3])
            month_sum_cand = perm[0] + perm[1]
            day_sum_cand = perm[2] + perm[3]

            if 1 <= month_sum_cand <= 12 and 1 <= day_sum_cand <= 31:
                # Add the solution as a sorted tuple of (month, day) to ensure uniqueness
                # e.g., (5, 15) is the same as (15, 5) if the problem implies unordered pairs
                # However, the problem states "month and day", implying a specific order.
                # So (month_sum, day_sum) should be unique.
                valid_solutions.add((month_sum_cand, day_sum_cand))
        
        # Check if a unique (month, day) combination was found
        if len(valid_solutions) == 1:
            target_num = p1 * p2 * p3 * p4
            month_ans, day_ans = list(valid_solutions)[0]
            break
            
    question_text = (
        f"將 {target_num} 拆成 4 個相異正整數的乘積，再將這 4 個正整數分成 2 組，"
        f"每組 2 個的和，就是我的生日囉！小妍的生日應為幾月幾日？"
    )
    correct_answer = f"{month_ans} 月 {day_ans} 日"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }

def generate_type_5_problem():
    """
    Type 5: Password from Prime Factorization Structure
    Concept: Extract exponents and prime bases from a number's prime factorization
             based on a specific template ($2^a \times b^c \times d$).
    """
    # Choose 'a' (exponent for 2)
    a_val = random.randint(1, 3) 

    # Choose 'b' (prime > 2)
    primes_b = [3, 5, 7]
    b_val = random.choice(primes_b)

    # Choose 'c' (exponent for b)
    c_val = random.randint(1, 2)

    # Choose 'd' (prime > b)
    primes_d_pool = [p for p in [11, 13, 17, 19, 23, 29, 31, 37] if p > b_val]
    
    # Ensure primes_d_pool is not empty. If b_val is large (e.g., 7), d_val must be > 7.
    # The current pool [11, 13, ...] covers this well.
    if not primes_d_pool:
        # This case should ideally not be reached with the current pools,
        # but as a safeguard, regenerate if no suitable 'd' is found.
        # For a robust system, this might require adjusting pools or retry logic.
        # For now, assume valid selection.
        raise ValueError("Could not find a suitable prime 'd'. Adjust prime pools or ranges.")
        
    d_val = random.choice(primes_d_pool)

    # Calculate N
    N = (2**a_val) * (b_val**c_val) * d_val

    # The password is the concatenation of a, b, c, d
    password = f"{a_val}{b_val}{c_val}{d_val}"
    
    question_text = (
        f"小翊設定手機解鎖的密碼為 abcd 四碼，若他是利用 {N} 的標準分解式 "
        f"$2^a \\times {b_val}^c \\times d$ 來設計密碼，則此組密碼為何？"
        # Note: The question template uses $2^a \times b^c \times d$,
        # but for clarity in the question itself, it's better to show the actual b_val.
        # However, the spec says $2^a \times b^c \times d$. Let's stick to the spec's question format.
        # If the b_val is fixed in the question text, it gives away too much.
        # The prompt says: "若他是利用 {N} 的標準分解式 $2^a \times b^c \times d$ 來設計密碼"
        # This implies 'b' and 'd' are variables to be found.
        # So, the question should be exactly as in the spec: $2^a \times b^c \times d$
    )
    
    return {
        "question_text": question_text,
        "answer": password,
        "correct_answer": password,
        "difficulty": 2
    }

# ==============================================================================
# Main Dispatcher and Checker
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        problem_types = [
            generate_type_1_problem, # Identify Prime/Composite
            generate_type_2_problem, # Number of Rectangles
            generate_type_3_problem, # Prime Factorization & List Prime Factors
        ]
        return random.choice(problem_types)()
    elif level == 2:
        problem_types = [
            generate_type_4_problem, # Birthday Puzzle
            generate_type_5_problem, # Password Puzzle
        ]
        return random.choice(problem_types)()
    else:
        raise ValueError("Invalid level. Please choose 1 or 2.")

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
        # Attempt numeric comparison for cases where string format might differ but value is same
        # This is more for general math problems, for string answers like "X 是 Y" or "A 月 B 日",
        # direct string comparison is usually sufficient.
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError:
        pass # Not a number, fall through to default incorrect message
        
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
