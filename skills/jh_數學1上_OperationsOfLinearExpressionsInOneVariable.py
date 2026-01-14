# ==============================================================================
# ID: jh_數學1上_OperationsOfLinearExpressionsInOneVariable
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 150.65s | RAG: 8 examples
# Created At: 2026-01-09 22:59:16
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
    # Inlined answer formatting logic
    # This block of code is repeated in each generate_type_N_problem function
    # to strictly adhere to the "DO NOT WRITE HELPER FUNCTIONS" rule.
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear() # Clear parts for fresh formatting

    def _format_answer_build():
        # Handle coefficient of x
        if _coeff_x_val == 0:
            pass # No x term
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        # Handle constant term
        if _constant_val == 0:
            pass # No constant term
        elif _constant_val > 0:
            if _parts: # If there's an x term, add '+'
                _parts.append(f"+{to_latex(_constant_val)}")
            else: # If no x term, just the constant
                _parts.append(to_latex(_constant_val))
        else: # _constant_val < 0
            _parts.append(to_latex(_constant_val)) # to_latex already includes '-'

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    while True:
        coeff_x = random.randint(-10, 10)
        if coeff_x != 0:
            break
    while True:
        constant_val = random.randint(-10, 10)
        if constant_val != 0:
            break

    operation = random.choice(['multiply', 'divide'])

    if operation == 'multiply':
        q = f"化簡下列各式。 ${fmt_num(constant_val)} \\cdot ({fmt_num(coeff_x)}x)$"
        result_coeff = constant_val * coeff_x
        _format_answer_init(result_coeff, 0)
        answer = _format_answer_build()
    else: # operation == 'divide'
        denominator = random.randint(2, 5)
        divisor_frac = Fraction(constant_val, denominator)
        q = f"化簡下列各式。 ${fmt_num(coeff_x)}x \\div {fmt_num(divisor_frac)}$"
        result_coeff = Fraction(coeff_x, 1) / divisor_frac
        _format_answer_init(result_coeff, 0)
        answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_2_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    use_fractions = random.choice([True, False])

    if use_fractions:
        while True:
            coeff1 = get_random_fraction(-5, 5)
            if coeff1 != 0: break
        while True:
            coeff2 = get_random_fraction(-5, 5)
            if coeff2 != 0: break
    else:
        while True:
            coeff1 = random.randint(-10, 10)
            if coeff1 != 0:
                break
        while True:
            coeff2 = random.randint(-10, 10)
            if coeff2 != 0:
                break
    
    operator = random.choice(['+', '-'])

    term1_str = f"{fmt_num(coeff1)}x"
    term2_str = f"{fmt_num(coeff2)}x"
    
    q = f"化簡下列各式。 ${term1_str} {operator} {term2_str}$"
    
    if operator == '+':
        result_coeff = coeff1 + coeff2
    else: # operator == '-'
        result_coeff = coeff1 - coeff2
    
    _format_answer_init(result_coeff, 0)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_3_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    while True:
        coeff1 = random.randint(-10, 10)
        if coeff1 != 0:
            break
    const1_abs = random.randint(1, 10) # Absolute value for display and calculation with op1
    while True:
        coeff2_abs = random.randint(1, 10) # Absolute value for display and calculation with op2
        if coeff2_abs != 0: 
            break
    const2_abs = random.randint(1, 10) # Absolute value for display and calculation with op3

    op1_symbol = random.choice(['+', '-']) # operator before const1_abs
    op2_symbol = random.choice(['+', '-']) # operator before coeff2_abs x
    op3_symbol = random.choice(['+', '-']) # operator before const2_abs

    # Construct question string
    question_parts = [f"{fmt_num(coeff1)}x"]
    question_parts.append(f"{op1_symbol} {fmt_num(const1_abs)}")
    question_parts.append(f"{op2_symbol} {fmt_num(coeff2_abs)}x")
    question_parts.append(f"{op3_symbol} {fmt_num(const2_abs)}")
    
    q = f"化簡下列各式。 ${' '.join(question_parts)}$"

    # Calculate final coefficient and constant based on operators
    final_coeff = coeff1 + (coeff2_abs if op2_symbol == '+' else -coeff2_abs)
    final_const = (const1_abs if op1_symbol == '+' else -const1_abs) + (const2_abs if op3_symbol == '+' else -const2_abs)

    _format_answer_init(final_coeff, final_const)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_4_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    while True:
        coeff_x = random.randint(-10, 10)
        if coeff_x != 0:
            break
    while True:
        constant_abs = random.randint(1, 10) # Absolute value for display
        if constant_abs != 0:
            break
    
    outer_sign = random.choice(['-', '--']) # '--' means -(-...) = +(...)
    inner_op = random.choice(['+', '-'])

    # Construct inner expression string
    inner_expr_str = f"{fmt_num(coeff_x)}x {inner_op} {fmt_num(constant_abs)}"
    
    q = f"化簡下列各式。 ${outer_sign}({inner_expr_str})$"

    # Calculate final coefficients and constants
    actual_inner_constant = constant_abs if inner_op == '+' else -constant_abs

    if outer_sign == '-': # -(Ax + B) -> -Ax - B, -(Ax - B) -> -Ax + B
        final_coeff = -coeff_x
        final_constant = -actual_inner_constant
    else: # outer_sign == '--' means -(-(...)) which simplifies to +(...)
          # -(-(Ax + B)) -> Ax + B, -(-(Ax - B)) -> Ax - B
        final_coeff = coeff_x
        final_constant = actual_inner_constant
    
    _format_answer_init(final_coeff, final_constant)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_5_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    while True:
        dist_const = random.randint(-10, 10)
        if dist_const != 0:
            break
    while True:
        coeff_x = random.randint(-10, 10)
        if coeff_x != 0:
            break
    while True:
        inner_const_abs = random.randint(1, 10) # Absolute value for display
        if inner_const_abs != 0:
            break
            
    inner_op = random.choice(['+', '-'])

    # Construct question string
    inner_expr_str = f"{fmt_num(coeff_x)}x {inner_op} {fmt_num(inner_const_abs)}"
    q = f"化簡下列各式。 ${fmt_num(dist_const)}({inner_expr_str})$"

    # Calculate final coefficients and constants
    actual_inner_const = inner_const_abs if inner_op == '+' else -inner_const_abs
    
    final_coeff = dist_const * coeff_x
    final_constant = dist_const * actual_inner_const
    
    _format_answer_init(final_coeff, final_constant)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_6_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    style = random.choice(['two_terms', 'nested'])

    if style == 'two_terms':
        while True: # a
            a = random.randint(-5, 5)
            if a != 0: break
        while True: # b (coeff in first term)
            b_abs = random.randint(1, 5)
            if b_abs != 0: break
        c_abs = random.randint(1, 5) # c (constant in first term)
        while True: # d
            d = random.randint(-5, 5)
            if d != 0: break
        while True: # e (coeff in second term)
            e_abs = random.randint(1, 5)
            if e_abs != 0: break
        f_abs = random.randint(1, 5) # f (constant in second term)

        op1_symbol = random.choice(['+', '-']) # for (b_abs x op1_symbol c_abs)
        op_mid_symbol = random.choice(['+', '-']) # between the two terms
        op2_symbol = random.choice(['+', '-']) # for (e_abs x op2_symbol f_abs)

        q = f"化簡下列各式。 ${fmt_num(a)}({fmt_num(b_abs)}x {op1_symbol} {fmt_num(c_abs)}) {op_mid_symbol} {fmt_num(d)}({fmt_num(e_abs)}x {op2_symbol} {fmt_num(f_abs)})$"

        # Calculate first term: a * (b_abs x op1_symbol c_abs)
        term1_coeff_val = b_abs
        term1_const_val = c_abs if op1_symbol == '+' else -c_abs
        
        expanded_term1_coeff = a * term1_coeff_val
        expanded_term1_const = a * term1_const_val

        # Calculate second term: d * (e_abs x op2_symbol f_abs)
        term2_coeff_val = e_abs
        term2_const_val = f_abs if op2_symbol == '+' else -f_abs

        expanded_term2_coeff = d * term2_coeff_val
        expanded_term2_const = d * term2_const_val

        # Combine terms using op_mid_symbol
        final_coeff = expanded_term1_coeff + (expanded_term2_coeff if op_mid_symbol == '+' else -expanded_term2_coeff)
        final_const = expanded_term1_const + (expanded_term2_const if op_mid_symbol == '+' else -expanded_term2_const)

    else: # style == 'nested'
        # Ax op1 B[Cx op2 (Dx op3 E)]
        while True: # a
            a = random.randint(-5, 5)
            if a != 0: break
        while True: # b
            b = random.randint(-5, 5)
            if b != 0: break
        while True: # c
            c_abs = random.randint(1, 5)
            if c_abs != 0: break
        while True: # d
            d_abs = random.randint(1, 5)
            if d_abs != 0: break
        e_abs = random.randint(1, 5) # e

        op1_symbol = random.choice(['+', '-']) # before B[...]
        op2_symbol = random.choice(['+', '-']) # before (D x op3 E)
        op3_symbol = random.choice(['+', '-']) # inside (D x op3 E)

        q = f"化簡下列各式。 ${fmt_num(a)}x {op1_symbol} {fmt_num(b)}[{fmt_num(c_abs)}x {op2_symbol} ({fmt_num(d_abs)}x {op3_symbol} {fmt_num(e_abs)})]$"

        # Evaluate innermost parentheses: (d_abs x op3_symbol e_abs)
        expr_inside_paren_coeff = d_abs
        expr_inside_paren_const = e_abs if op3_symbol == '+' else -e_abs

        # Evaluate inner square bracket: c_abs x op2_symbol (expr_inside_paren_coeff x + expr_inside_paren_const)
        inner_square_coeff = c_abs
        inner_square_const = 0

        if op2_symbol == '+':
            inner_square_coeff += expr_inside_paren_coeff
            inner_square_const += expr_inside_paren_const
        else: # op2_symbol == '-'
            inner_square_coeff -= expr_inside_paren_coeff
            inner_square_const -= expr_inside_paren_const
        
        # Evaluate whole expression: a x op1_symbol b * [inner_square_coeff x + inner_square_const]
        final_coeff = a
        final_const = 0

        if op1_symbol == '+':
            final_coeff += b * inner_square_coeff
            final_const += b * inner_square_const
        else: # op1_symbol == '-'
            final_coeff -= b * inner_square_coeff
            final_const -= b * inner_square_const

    _format_answer_init(final_coeff, final_const)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_7_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    while True:
        num_coeff1 = random.randint(-5, 5)
        num_const1_abs = random.randint(1, 5) # Absolute value for display
        if num_coeff1 != 0 or num_const1_abs != 0:
            break
    while True:
        num_coeff2 = random.randint(-5, 5)
        num_const2_abs = random.randint(1, 5) # Absolute value for display
        if num_coeff2 != 0 or num_const2_abs != 0:
            break

    den1 = random.randint(2, 6)
    while True:
        den2 = random.randint(2, 6)
        if den1 != den2:
            break
    
    operator = random.choice(['+', '-'])
    op_n1_symbol = random.choice(['+', '-']) # operator inside numerator 1
    op_n2_symbol = random.choice(['+', '-']) # operator inside numerator 2

    # Construct numerator strings
    numerator1_str = f"{fmt_num(num_coeff1)}x {op_n1_symbol} {fmt_num(num_const1_abs)}"
    numerator2_str = f"{fmt_num(num_coeff2)}x {op_n2_symbol} {fmt_num(num_const2_abs)}"

    q = f"化簡 $\\frac{{{numerator1_str}}}{{{den1}}} {operator} \\frac{{{numerator2_str}}}{{{den2}}}$"

    # Calculate common denominator and factors
    common_den = lcm(den1, den2)
    factor1 = common_den // den1
    factor2 = common_den // den2

    # Adjust numerator terms for common denominator
    actual_num_const1 = num_const1_abs if op_n1_symbol == '+' else -num_const1_abs
    actual_num_const2 = num_const2_abs if op_n2_symbol == '+' else -num_const2_abs

    term1_coeff_numerator = num_coeff1 * factor1
    term1_const_numerator = actual_num_const1 * factor1

    term2_coeff_numerator = num_coeff2 * factor2
    term2_const_numerator = actual_num_const2 * factor2

    # Combine numerators based on the main operator
    final_num_coeff = term1_coeff_numerator + (term2_coeff_numerator if operator == '+' else -term2_coeff_numerator)
    final_num_const = term1_const_numerator + (term2_const_numerator if operator == '+' else -term2_const_numerator)

    final_coeff = Fraction(final_num_coeff, common_den)
    final_const = Fraction(final_num_const, common_den)

    _format_answer_init(final_coeff, final_const)
    answer = _format_answer_build()
    
    return {'question_text': q, 'answer': answer, 'correct_answer': answer}


def generate_type_8_problem():
    # Inlined answer formatting logic
    _parts = []
    _coeff_x_val = None
    _constant_val = None

    def _format_answer_init(coeff, constant):
        nonlocal _coeff_x_val, _constant_val
        _coeff_x_val = coeff
        _constant_val = constant
        _parts.clear()

    def _format_answer_build():
        if _coeff_x_val == 0:
            pass
        elif _coeff_x_val == 1:
            _parts.append("x")
        elif _coeff_x_val == -1:
            _parts.append("-x")
        else:
            _parts.append(f"{to_latex(_coeff_x_val)}x")

        if _constant_val == 0:
            pass
        elif _constant_val > 0:
            if _parts:
                _parts.append(f"+{to_latex(_constant_val)}")
            else:
                _parts.append(to_latex(_constant_val))
        else:
            _parts.append(to_latex(_constant_val))

        if not _parts:
            return "0"
        return "".join(_parts)
    # End of inlined answer formatting logic

    item_names = ['披薩', '漢堡', '蛋糕', '壽司', '麵包', '沙拉']
    item1_name = random.choice(item_names)
    while True:
        item2_name = random.choice(item_names)
        if item2_name != item1_name:
            break
    
    item2_price_diff = random.randint(20, 100)
    num_item1 = random.randint(3, 10)
    num_item2 = random.randint(3, 10)
    total_people = random.randint(5, 15)

    # Part (a) Total cost
    total_coeff_a = num_item1 + num_item2
    total_const_a = num_item2 * item2_price_diff
    
    _format_answer_init(total_coeff_a, total_const_a)
    answer_a_str = _format_answer_build() + " 元"

    # Part (b) Average cost
    avg_coeff_b = Fraction(total_coeff_a, total_people)
    avg_const_b = Fraction(total_const_a, total_people)

    _format_answer_init(avg_coeff_b, avg_const_b)
    answer_b_str = _format_answer_build() + " 元"

    # Combine question and answer parts
    q_part_a = f"已知每個{item1_name} $x$ 元，每個{item2_name}比{item1_name}貴 ${item2_price_diff}$ 元。小華買了 ${num_item1}$ 個{item1_name}、${num_item2}$ 個{item2_name}共需多少元？"
    q_part_b = f"承上題，若最後參與派對的人數共有 ${total_people}$ 人，則每人平均應付多少元？"
    
    q = f"{q_part_a}\n{q_part_b}"
    a = f"(a) {answer_a_str}\n(b) {answer_b_str}"

    return {'question_text': q, 'answer': a, 'correct_answer': a}


def generate(level=1):
    if level == 1:
        problem_type = random.choice([
            generate_type_1_problem,
            generate_type_2_problem,
            generate_type_3_problem,
            generate_type_4_problem,
            generate_type_5_problem,
        ])
    elif level == 2:
        problem_type = random.choice([
            generate_type_6_problem,
            generate_type_7_problem,
            generate_type_8_problem,
        ])
    else:
        raise ValueError("Invalid level. Choose 1 or 2.")

    return problem_type()

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
