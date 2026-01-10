# ==============================================================================
# ID: jh_數學1上_RateProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 13.23s | RAG: 2 examples
# Created At: 2026-01-09 22:59:29
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
    # Concept: Two individuals move in the same direction on a circular path.
    # Given their speeds and the distance remaining for the slower person when the faster person finishes,
    # find the total length of the path. Both run for the same amount of time.

    speed_fast = random.randint(8, 15) # km/h
    # Ensure speed_slow is less than speed_fast
    speed_slow = random.randint(5, speed_fast - 1) # km/h
    
    time_taken = random.uniform(2.0, 6.0) # hours, total time for the race
    
    # Calculate total_distance and distance_remaining based on time_taken for consistency
    total_distance = round(speed_fast * time_taken, 1) # km
    distance_remaining = round(total_distance - speed_slow * time_taken, 1) # km

    name_fast = random.choice(['小翊', '阿明', '志豪'])
    name_slow = random.choice(['小妍', '小華', '美玲']) # Ensure name_fast != name_slow (lists are distinct)
    location = random.choice(['蘭嶼島上的東清國小', '校園操場', '環山步道'])

    q = (
        f"{name_slow}與{name_fast}約定於{location}同時同方向環島路跑，"
        f"已知{name_fast}每小時跑 {to_latex(speed_fast)} 公里，"
        f"{name_slow}每小時跑 {to_latex(speed_slow)} 公里。"
        f"當{name_fast}跑回終點{location}時，{name_slow}還離終點 {to_latex(distance_remaining)} 公里，"
        f"求環島公路全長多少公里？"
    )
    
    # Answer MUST be clean (NO $ signs)
    a = str(total_distance) 
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate_type_2_problem():
    # Concept: A person travels a fixed distance (mountain path) up and down.
    # Speeds for going up and down are different. Given total time, find one-way path length.

    speed_up = random.randint(2, 6) # km/h
    # Ensure speed_down is greater than speed_up
    speed_down = random.randint(speed_up + 1, 10) # km/h
    
    total_time = random.randint(1, 5) # hours
    person_name = random.choice(['宗彥', '小明', '阿華'])

    # Calculate the path length (D) using the formula:
    # D/speed_up + D/speed_down = total_time
    # D * (1/speed_up + 1/speed_down) = total_time
    # D * ((speed_down + speed_up) / (speed_up * speed_down)) = total_time
    # D = total_time * speed_up * speed_down / (speed_up + speed_down)
    path_length_fraction = Fraction(total_time * speed_up * speed_down, speed_up + speed_down)

    q = (
        f"{person_name}沿著相同的路徑上山、下山共需要 {to_latex(total_time)} 小時，"
        f"如果{person_name}上山每小時可走 {to_latex(speed_up)} 公里，"
        f"下山每小時可走 {to_latex(speed_down)} 公里，"
        f"則這條山路長多少公里？"
    )
    
    # Answer using Fraction for precise calculation and to_latex for output
    a = to_latex(path_length_fraction)
    return {'question_text': q, 'answer': a, 'correct_answer': a}

def generate(level=1):
    """
    Dispatcher function to generate problems based on the specified level.
    """
    if level == 1:
        # Select randomly from Level 1 types
        problem_type = random.choice([
            generate_type_1_problem,
        ])
        return problem_type()
    elif level == 2:
        # Select randomly from Level 2 types
        problem_type = random.choice([
            generate_type_2_problem,
        ])
        return problem_type()
    else:
        raise ValueError("Invalid level. Please choose level 1 or 2.")

