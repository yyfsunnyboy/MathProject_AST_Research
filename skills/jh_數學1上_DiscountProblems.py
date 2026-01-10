# ==============================================================================
# ID: jh_數學1上_DiscountProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 40.42s | RAG: 2 examples
# Created At: 2026-01-09 22:54:52
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



# Helper functions like to_latex, fmt_num, etc. are auto-injected.
# DO NOT DEFINE THEM HERE.

def generate_type_1_level_1_problem():
    """
    Generates a Level 1 problem: Calculate discounted price given original price and discount rate.
    This type is invented to fulfill the Level 1 completeness requirement,
    as no Level 1 examples were provided in the Architect's Spec.
    """
    # To ensure discounted_price is always an integer, choose original_price as a multiple of 20.
    # The denominators for discount rates 0.6, 0.7, 0.75, 0.8, 0.9 are 5, 10, 4, 5, 10 respectively.
    # The least common multiple of these denominators (4, 5, 10) is 20.
    original_price = random.choice(range(500, 5001, 20)) 
    discount_percent = random.choice([60, 70, 75, 80, 90]) # Common discount percentages (e.g., 80 for 8折)
    discount_decimal = discount_percent / 100.0

    discounted_price = int(original_price * discount_decimal)
    
    q = f"一件商品原價 ${original_price}$ 元，現在打 ${discount_percent}$ 折，請問打折後的價格是多少元？"
    a = str(discounted_price)
    return {'question_text': q, 'answer': a, 'correct_answer': a}


def generate_type_1_problem():
    """
    Generates a Level 2, Type 1 problem (based on Architect's Ex 1).
    Concept: Solving for an unknown budget ($B$) given an initial price ($P_1 = B + A$)
    and a discounted price ($P_2 = B - C$), where $P_2 = D \times P_1$.
    The core equation is $D \times (B + A) = B - C$.
    """
    while True:
        budget = random.choice(range(3000, 15001, 100))
        discount_rate_decimal = random.choice([0.6, 0.7, 0.75, 0.8, 0.9])
        
        # Determine divisor for original_price based on discount_rate to ensure discounted_price is integer
        if discount_rate_decimal == 0.75: divisor = 4
        elif discount_rate_decimal in [0.7, 0.9]: divisor = 10
        else: divisor = 5 # for 0.6, 0.8
        
        price_over_budget_initial = random.choice(range(500, 3001, 100))
        
        original_price = budget + price_over_budget_initial
        if original_price % divisor != 0:
            needed_addition = divisor - (original_price % divisor)
            price_over_budget_initial += needed_addition
            original_price = budget + price_over_budget_initial # Recalculate
        
        discounted_price = int(discount_rate_decimal * original_price)
        price_under_budget_discounted = budget - discounted_price
        
        # Check conditions as per spec: C must be positive and within a reasonable range, A also within range
        if 50 <= price_under_budget_discounted <= 1000 and 500 <= price_over_budget_initial <= 5000:
            break
            
    discount_rate_percent = int(discount_rate_decimal * 100)
    
    q = f"阿樂想在網路上購買一雙限量籃球鞋，但售價比他預算多 ${price_over_budget_initial}$ 元。經過一段時間後，他發現這雙鞋還沒被買走，且變成 ${discount_rate_percent}$ 折出售，這樣就比他預算少 ${price_under_budget_discounted}$ 元，請問阿樂預算是多少元？"
    a = str(budget)
    return {'question_text': q, 'answer': a, 'correct_answer': a}


def generate_type_2_problem():
    """
    Generates a Level 2, Type 2 problem (based on Architect's Ex 2).
    Concept: Identical to Type 1, but presented in a dialogue format with slightly different variable ranges.
    Solving for an unknown budget ($B$) given an initial price ($P_1 = B + A$)
    and a discounted price ($P_2 = B - C$), where $P_2 = D \times P_1$.
    The core equation is $D \times (B + A) = B - C$.
    """
    while True:
        budget = random.choice(range(4000, 12001, 100)) # Slightly different range
        discount_rate_decimal = random.choice([0.65, 0.7, 0.75, 0.8, 0.85]) # Slightly different rates
        
        # Determine divisor for original_price based on discount_rate
        if discount_rate_decimal == 0.75: divisor = 4
        elif discount_rate_decimal in [0.7, 0.85]: divisor = 20 # 0.7 = 7/10, 0.85 = 17/20
        elif discount_rate_decimal == 0.65: divisor = 20 # 0.65 = 13/20
        else: divisor = 5 # for 0.8
        
        price_over_budget_initial = random.choice(range(600, 3501, 100)) # Slightly different range
        original_price = budget + price_over_budget_initial
        
        if original_price % divisor != 0:
            needed_addition = divisor - (original_price % divisor)
            price_over_budget_initial += needed_addition
            original_price = budget + price_over_budget_initial
        
        discounted_price = int(discount_rate_decimal * original_price)
        price_under_budget_discounted = budget - discounted_price
        
        # Check conditions as per spec
        if 80 <= price_under_budget_discounted <= 1200 and 600 <= price_over_budget_initial <= 6000:
            break
            
    discount_rate_percent = int(discount_rate_decimal * 100)
    
    q = f"根據以下對話紀錄，求出哥哥買遊戲機的預算為多少元？(對話內容：哥，你之前提到的遊戲機買了沒？ 還沒，因為它的售價比我的預算還多 ${price_over_budget_initial}$ 元。 這臺遊戲機正在打 ${discount_rate_percent}$ 折促銷耶！ 這樣比我的預算還少 ${price_under_budget_discounted}$ 元耶！)"
    a = str(budget)
    return {'question_text': q, 'answer': a, 'correct_answer': a}


def generate(level=1):
    """
    Dispatcher function to generate discount problems based on the specified level.
    """
    if level == 1:
        return generate_type_1_level_1_problem()
    elif level == 2:
        return random.choice([generate_type_1_problem, generate_type_2_problem])()
    else:
        raise ValueError(f"Invalid level: {level}. Level must be 1 or 2.")

