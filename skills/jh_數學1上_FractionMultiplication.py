# ==============================================================================
# ID: jh_數學1上_FractionMultiplication
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 57.03s | RAG: 4 examples
# Created At: 2026-01-09 14:10:22
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

# Helper functions provided in the architect's spec or common template.

def _generate_fraction_part(max_num=5, max_den=7, ensure_proper=True):
    """Generates a proper fraction (numerator, denominator) tuple as a Fraction object."""
    # Ensure numerator < denominator for proper fraction
    numerator = random.randint(1, max_num)
    # Denominator must be strictly greater than numerator if ensure_proper is True
    denominator = random.randint(numerator + 1 if ensure_proper else 2, max_den)
    return Fraction(numerator, denominator)

def _generate_fraction_obj(allow_negative=True, max_abs_num=10, max_den=12, proper=False):
    """Generates a random Fraction object."""
    num = random.randint(1, max_abs_num)
    # Denominator must be strictly greater than numerator if proper is True
    den = random.randint(num + 1 if proper else 2, max_den)
    
    frac = Fraction(num, den)
    if allow_negative and random.choice([True, False]):
        frac *= -1
    return frac

def _generate_mixed_number_obj(allow_negative=True, max_int=3, max_frac_num=4, max_frac_den=7):
    """Generates a random mixed number as a Fraction object."""
    integer_part = random.randint(1, max_int)
    frac_part = _generate_fraction_part(max_frac_num, max_frac_den, ensure_proper=True)
    
    # Convert mixed number to improper fraction (e.g., 2 1/3 = 2 + 1/3 = 7/3)
    frac = integer_part + frac_part
    
    if allow_negative and random.choice([True, False]):
        frac *= -1
    return frac

def _format_fraction_for_display(f: Fraction) -> str:
    """
    Formats a fraction for display in the question, including mixed numbers
    and wrapping negative fractions in parentheses.
    """
    is_negative = f < 0
    abs_f = abs(f)

    if abs_f.denominator == 1:
        # It's an integer
        return fmt_num(abs_f.numerator * (-1 if is_negative else 1))
    
    if abs_f.numerator > abs_f.denominator:
        # It's an improper fraction, display as mixed number
        integer_part = abs_f.numerator // abs_f.denominator
        proper_frac_part = abs_f - integer_part
        
        # Format the proper fraction part using to_latex
        frac_latex = to_latex(proper_frac_part) # This will be \frac{num}{den}
        
        # Combine into mixed number string with a space
        display_str = f"{integer_part} {frac_latex}"
    else:
        # It's a proper fraction, display directly
        display_str = to_latex(abs_f) # This will be \frac{num}{den}

    if is_negative:
        # Ensure negative sign is inside parentheses, but not if it's 0.
        return f"({'-' if abs_f.numerator != 0 else ''}{display_str})"
    return display_str


# ------------------------------------------------------------------------------
# Problem Type Implementations
# ------------------------------------------------------------------------------

def generate_type_1_problem():
    """
    Level 1: Multiplication of two fractions (proper or improper), involving negative signs.
    Focus on smaller number ranges.
    """
    frac1 = _generate_fraction_obj(allow_negative=True, max_abs_num=5, max_den=7)
    frac2 = _generate_fraction_obj(allow_negative=True, max_abs_num=5, max_den=7)
    
    question_text = (
        f"計算下列各式的值。\\n"
        f"$"
        f"{_format_fraction_for_display(frac1)} \\times {_format_fraction_for_display(frac2)}"
        f"$"
    )
    
    result = frac1 * frac2
    
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 1
    }

def generate_type_2_problem():
    """
    Level 1: Multiplication of two fractions (proper or improper), involving negative signs.
    Numbers might be slightly larger, often leading to simplification.
    """
    frac1 = _generate_fraction_obj(allow_negative=True, max_abs_num=10, max_den=15)
    frac2 = _generate_fraction_obj(allow_negative=True, max_abs_num=10, max_den=15)
    
    question_text = (
        f"計算下列各式的值。\\n"
        f"$"
        f"{_format_fraction_for_display(frac1)} \\times {_format_fraction_for_display(frac2)}"
        f"$"
    )
    
    result = frac1 * frac2
    
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Level 2: Multiplication of three fractions (can include mixed numbers) OR repeated multiplication (powers of 3 or 4).
    """
    sub_type = random.choice(['three_fractions', 'power'])
    
    if sub_type == 'three_fractions':
        terms = []
        for _ in range(3):
            if random.random() < 0.5: # Decide if it's a mixed number or simple fraction
                terms.append(_generate_mixed_number_obj(allow_negative=True, max_int=2, max_frac_num=3, max_frac_den=5))
            else:
                terms.append(_generate_fraction_obj(allow_negative=True, max_abs_num=5, max_den=7))
        
        frac1, frac2, frac3 = terms[0], terms[1], terms[2]
        
        question_text = (
            f"計算下列各式的值。\\n"
            f"$"
            f"{_format_fraction_for_display(frac1)} \\times {_format_fraction_for_display(frac2)} \\times {_format_fraction_for_display(frac3)}"
            f"$"
        )
        result = frac1 * frac2 * frac3
    
    else: # sub_type == 'power'
        base_frac = _generate_fraction_obj(allow_negative=True, max_abs_num=3, max_den=5, proper=True)
        exponent = random.randint(3, 4)
        
        question_text = (
            f"計算下列各式的值。\\n"
            f"$"
            f"({_format_fraction_for_display(base_frac)})^{{{exponent}}}"
            f"$"
        )
        result = base_frac ** exponent
        
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 2
    }

def generate_type_4_problem():
    """
    Level 2: Similar to Type 3, but with potentially more complex mixed number combinations or higher powers (4 or 5).
    """
    sub_type = random.choice(['three_fractions', 'power'])
    
    if sub_type == 'three_fractions':
        terms = []
        for _ in range(3):
            if random.random() < 0.6: # Slightly higher chance for mixed numbers
                terms.append(_generate_mixed_number_obj(allow_negative=True, max_int=3, max_frac_num=4, max_frac_den=7))
            else:
                terms.append(_generate_fraction_obj(allow_negative=True, max_abs_num=7, max_den=10))
        
        frac1, frac2, frac3 = terms[0], terms[1], terms[2]
        
        question_text = (
            f"計算下列各式的值。\\n"
            f"$"
            f"{_format_fraction_for_display(frac1)} \\times {_format_fraction_for_display(frac2)} \\times {_format_fraction_for_display(frac3)}"
            f"$"
        )
        result = frac1 * frac2 * frac3
    
    else: # sub_type == 'power'
        base_frac = _generate_fraction_obj(allow_negative=True, max_abs_num=3, max_den=5, proper=True)
        exponent = random.randint(4, 5) # Higher exponent
        
        question_text = (
            f"計算下列各式的值。\\n"
            f"$"
            f"({_format_fraction_for_display(base_frac)})^{{{exponent}}}"
            f"$"
        )
        result = base_frac ** exponent
        
    return {
        "question_text": question_text,
        "answer": to_latex(result),
        "correct_answer": to_latex(result),
        "difficulty": 2
    }

# ------------------------------------------------------------------------------
# Main Dispatcher and Checker
# ------------------------------------------------------------------------------

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations.
    - Level 2: Advanced applications, multi-step problems, powers.
    """
    if level == 1:
        problem_func = random.choice([
            generate_type_1_problem,
            generate_type_2_problem
        ])
        return problem_func()
    elif level == 2:
        problem_func = random.choice([
            generate_type_3_problem,
            generate_type_4_problem
        ])
        return problem_func()
    else:
        raise ValueError("Invalid level. Level must be 1 or 2.")

# Helper for parsing various fraction string formats (including LaTeX) into Fraction objects.
def _parse_fraction_string(s: str) -> Fraction:
    s = s.strip()
    
    # Handle overall negative sign for the expression
    is_negative = False
    if s.startswith("(-") and s.endswith(")"):
        is_negative = True
        s = s[2:-1].strip() # Remove "(-" and ")"
        # Handle cases like (-(1/2))
        if s.startswith("-"):
            is_negative = not is_negative # Double negative means positive
            s = s[1:].strip()
    elif s.startswith("-"):
        is_negative = True
        s = s[1:].strip()

    # Try parsing as a mixed number first (e.g., "1 2/3" or "1 \frac{2}{3}")
    parts = s.split(' ', 1) # Split only on the first space
    if len(parts) == 2 and parts[0].strip().isdigit():
        integer_part = int(parts[0].strip())
        fraction_part_str = parts[1].strip()
        frac_part = _parse_fraction_string(fraction_part_str) # Recursive call for the fractional part
        val = integer_part + frac_part
    # Case 1: Simple integer
    elif s.isdigit():
        val = Fraction(int(s))
    # Case 2: Standard fraction string "N/D"
    elif '/' in s:
        parts = s.split('/')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            val = Fraction(int(parts[0]), int(parts[1]))
        else:
            raise ValueError(f"Invalid fraction format: {s}")
    # Case 3: LaTeX fraction "\\frac{N}{D}"
    elif s.startswith("\\frac{") and s.endswith("}"):
        # Find the split between numerator and denominator by counting braces
        brace_level = 0
        split_index = -1
        # s[6:] starts after "\frac{"
        for i, char in enumerate(s[6:]):
            if char == '{':
                brace_level += 1
            elif char == '}':
                if brace_level == 0:
                    split_index = i + 6 # Position of '}' after numerator
                    break
                brace_level -= 1
        
        if split_index == -1:
            raise ValueError(f"Invalid LaTeX fraction format (numerator brace mismatch): {s}")

        numerator_str = s[6:split_index]
        denominator_str = s[split_index + 2:-1] # +2 to skip '}{', -1 to remove last '}'

        num = int(numerator_str.strip())
        den = int(denominator_str.strip())
        val = Fraction(num, den)
    else:
        raise ValueError(f"Unknown fraction format: {s}")

    return val * (-1 if is_negative else 1)

def check(user_answer, correct_answer):
    """
    Standard Answer Checker for fractions.
    Handles LaTeX fraction strings and mixed numbers by converting to Fraction objects.
    """
    # Do NOT replace spaces globally, as they are significant for mixed numbers.
    user_ans_clean = user_answer.strip()
    correct_ans_clean = correct_answer.strip()

    try:
        user_frac = _parse_fraction_string(user_ans_clean)
        correct_frac = _parse_fraction_string(correct_ans_clean)
        
        if user_frac == correct_frac:
            return {"correct": True, "result": "正確！"}
    except ValueError:
        # If fraction parsing fails, it's likely an incorrect format or non-fraction.
        # For this skill, answers *should* be fractions, so no float fallback.
        pass
    except Exception:
        # Catch any unexpected errors during parsing, treat as incorrect
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
