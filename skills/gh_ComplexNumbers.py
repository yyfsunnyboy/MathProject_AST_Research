import random
from fractions import Fraction
import math
import re

# Helper function for GCD, used in Fraction simplification (though Fraction handles it automatically)
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Helper function to simplify square roots for x^2 = -k problem
def simplify_sqrt(n):
    if n < 0:
        raise ValueError("Cannot simplify sqrt of negative number for real part.")
    if n == 0:
        return 0, 1 # 0*sqrt(1) -> 0
    
    coeff = 1
    radical = n
    
    i = 2
    while i * i <= radical:
        if radical % (i * i) == 0:
            coeff *= i
            radical //= (i * i)
        else:
            i += 1
    return coeff, radical

# Helper function to format a complex number (Fraction real, Fraction imag) into a string "a+bi"
def format_complex(real_part, imag_part):
    """
    Formats a complex number (Fraction real_part, Fraction imag_part) into a+bi string.
    Handles fractions, negative signs, 0, 1, and -1 coefficients for i.
    """
    real_str = str(real_part) if real_part.denominator != 1 else str(real_part.numerator)
    imag_str = str(imag_part) if imag_part.denominator != 1 else str(imag_part.numerator)

    # If both parts are zero
    if real_part == 0 and imag_part == 0:
        return "0"
    
    # If imaginary part is zero
    if imag_part == 0:
        return real_str
    
    # If real part is zero
    if real_part == 0:
        if imag_part == 1:
            return "i"
        elif imag_part == -1:
            return "-i"
        else:
            return f"{imag_str}i"
            
    # Both parts are non-zero
    op = "+" if imag_part > 0 else "-"
    abs_imag_part = abs(imag_part)
    abs_imag_str = str(abs_imag_part) if abs_imag_part.denominator != 1 else str(abs_imag_part.numerator)

    if abs_imag_part == 1:
        return f"{real_str}{op}i"
    else:
        return f"{real_str}{op}{abs_imag_str}i"


# --- Problem Generation Functions ---

def generate_solve_x_squared():
    """
    題目: 以i表示下列各方程式的解。 $x^2 = -k$
    """
    k_raw = random.randint(2, 50) 
    coeff, radical = simplify_sqrt(k_raw)

    radical_str = ""
    if radical > 1:
        radical_str = f"\\sqrt{{{radical}}}"
    
    if coeff == 1 and radical == 1: # k_raw = 1
        val_str = "i"
    elif coeff == 1: # e.g. k_raw = 5 -> sqrt(5)i
        val_str = f"{radical_str}i"
    elif radical == 1: # e.g. k_raw = 4 -> 2i
        val_str = f"{coeff}i"
    else: # e.g. k_raw = 12 -> 2sqrt(3)i
        val_str = f"{coeff}{radical_str}i"

    question_text = f"以 $i$ 表示下列方程式的解：$x^{{2}} = -{k_raw}$。"
    correct_answer = f"$\\pm {val_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_real_imag_parts():
    """
    題目: 求下列各複數的實部與虛部。
    """
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    
    # Ensure not both are zero
    if a == 0 and b == 0:
        a = random.randint(1, 10) 

    problem_case = random.choice(['general', 'real_only', 'imag_only'])
    
    if problem_case == 'real_only':
        b = 0
        while a == 0: # Ensure 'a' is not 0 for purely real
            a = random.randint(-10, 10)
    elif problem_case == 'imag_only':
        a = 0
        while b == 0: # Ensure 'b' is not 0 for purely imaginary
            b = random.randint(-10, 10)
            
    complex_str = format_complex(Fraction(a), Fraction(b))
    
    question_text = f"求下列複數的實部與虛部：${complex_str}$。"
    correct_answer = f"實部: {a}, 虛部: {b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_complex_equality():
    """
    題目: 已知實數 $x, y$ 滿足 $(expr_x) + (expr_y)i = (rhs_a) + (rhs_b)i$，求 $x, y$ 的值。
    """
    val_x = random.randint(-5, 5)
    val_y = random.randint(-5, 5)
    
    coeff_x = random.choice([1, random.randint(2, 3)])
    offset_x = random.randint(-5, 5)
    
    coeff_y = random.choice([1, random.randint(2, 3)])
    offset_y = random.randint(-5, 5)
    
    rhs_real = coeff_x * val_x + offset_x
    rhs_imag = coeff_y * val_y + offset_y

    expr_real_str = f"{coeff_x}x"
    if offset_x > 0:
        expr_real_str += f"+{offset_x}"
    elif offset_x < 0:
        expr_real_str += str(offset_x)

    expr_imag_str = f"{coeff_y}y"
    if offset_y > 0:
        expr_imag_str += f"+{offset_y}"
    elif offset_y < 0:
        expr_imag_str += str(offset_y)

    question_text = (
        f"已知實數 $x, y$ 滿足 $({expr_real_str}) + ({expr_imag_str})i "
        f"= {format_complex(Fraction(rhs_real), Fraction(rhs_imag))} $，求 $x, y$ 的值。"
    )
    correct_answer = f"$x={val_x}, y={val_y}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_complex_arithmetic_sum_sub():
    """
    題目: 已知複數 $z_1 = a+bi, z_2 = c+di$，求 $z_1 \\pm z_2$ 的值。
    """
    a1, b1 = random.randint(-10, 10), random.randint(-10, 10)
    a2, b2 = random.randint(-10, 10), random.randint(-10, 10)

    # Ensure at least one imaginary part is non-zero
    while b1 == 0 and b2 == 0:
        b1, b2 = random.randint(-10, 10), random.randint(-10, 10)
    # Ensure at least one real part is non-zero
    while a1 == 0 and a2 == 0:
        a1, a2 = random.randint(-10, 10), random.randint(-10, 10)

    z1_str = format_complex(Fraction(a1), Fraction(b1))
    z2_str = format_complex(Fraction(a2), Fraction(b2))

    op = random.choice(['+', '-'])
    
    if op == '+':
        res_real = Fraction(a1 + a2)
        res_imag = Fraction(b1 + b2)
    else: # op == '-'
        res_real = Fraction(a1 - a2)
        res_imag = Fraction(b1 - b2)
        
    result_str = format_complex(res_real, res_imag)

    question_text = (
        f"已知複數 $z_1 = {z1_str}, z_2 = {z2_str}$，求 $z_1 {op} z_2$ 的值。"
    )
    correct_answer = f"${result_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_complex_arithmetic_mult():
    """
    題目: 已知複數 $z_1 = a+bi, z_2 = c+di$，求 $z_1 z_2$ 的值。
    """
    a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
    a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
    
    # Ensure both complex numbers are not trivial (0 or purely real/imaginary resulting in trivial product)
    while (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0) or \
          (b1 == 0 and b2 == 0) or (a1 == 0 and a2 == 0):
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)

    z1_str = format_complex(Fraction(a1), Fraction(b1))
    z2_str = format_complex(Fraction(a2), Fraction(b2))
    
    # (a1 + b1*i)(a2 + b2*i) = (a1*a2 - b1*b2) + (a1*b2 + b1*a2)*i
    res_real = Fraction(a1 * a2 - b1 * b2)
    res_imag = Fraction(a1 * b2 + b1 * a2)
    
    result_str = format_complex(res_real, res_imag)

    question_text = (
        f"已知複數 $z_1 = {z1_str}, z_2 = {z2_str}$，求 $z_1 z_2$ 的值。"
    )
    correct_answer = f"${result_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_i_powers():
    """
    題目: 1. 求 $i^n$ 的值。 2. 求 $i + i^2 + ... + i^N$ 的值。
    """
    problem_type = random.choice(['single_power', 'sum_of_powers'])
    
    if problem_type == 'single_power':
        n = random.randint(1, 100)
        remainder = n % 4
        
        if remainder == 1:
            result_str = "i"
        elif remainder == 2:
            result_str = "-1"
        elif remainder == 3:
            result_str = "-i"
        else: # remainder == 0 (i^4 = 1)
            result_str = "1"
            
        question_text = f"求 $i^{{{n}}}$ 的值。"
        correct_answer = f"${result_str}$"
        
    else: # sum_of_powers
        N = random.randint(4, 100) 
        remainder = N % 4
        
        if remainder == 0:
            result_str = "0"
        elif remainder == 1: # i^1 + ... + i^(4k+1) = i
            result_str = "i"
        elif remainder == 2: # i^1 + ... + i^(4k+2) = i + i^2 = i-1
            result_str = "i-1"
        else: # remainder == 3 (i^1 + ... + i^(4k+3) = i + i^2 + i^3 = i-1-i = -1)
            result_str = "-1"
            
        question_text = f"求 $i + i^{{2}} + ... + i^{{{N}}}$ 的值。"
        correct_answer = f"${result_str}$"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_complex_arithmetic_div():
    """
    題目: 將下列各複數表示成 $a+bi$ （其中 $a,b$ 為實數）的形式。 $\\frac{z_1}{z_2}$
    """
    a1, b1 = random.randint(-10, 10), random.randint(-10, 10)
    a2, b2 = random.randint(-5, 5), random.randint(-5, 5)

    # Ensure denominator is not 0
    while a2 == 0 and b2 == 0:
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
    
    # Ensure numerator is not 0
    while a1 == 0 and b1 == 0:
        a1, b1 = random.randint(-10, 10), random.randint(-10, 10)
        
    z1_str = format_complex(Fraction(a1), Fraction(b1))
    z2_str = format_complex(Fraction(a2), Fraction(b2))

    # (a1 + b1*i) / (a2 + b2*i) = (a1 + b1*i)(a2 - b2*i) / (a2^2 + b2^2)
    denominator_sq = a2*a2 + b2*b2
    
    num_real = a1*a2 + b1*b2 
    num_imag = b1*a2 - a1*b2 
    
    res_real = Fraction(num_real, denominator_sq)
    res_imag = Fraction(num_imag, denominator_sq)
    
    result_str = format_complex(res_real, res_imag)

    question_text = (
        f"將下列各複數表示成 $a+bi$ （其中 $a,b$ 為實數）的形式： $\\frac{{{z1_str}}}{{{z2_str}}}$。"
    )
    correct_answer = f"${result_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = [
        'solve_x_squared',
        'real_imag_parts',
        'complex_equality',
        'complex_arithmetic_sum_sub',
        'complex_arithmetic_mult',
        'i_powers',
        'complex_arithmetic_div'
    ]
    
    problem_type = random.choice(problem_types)
    
    if problem_type == 'solve_x_squared':
        return generate_solve_x_squared()
    elif problem_type == 'real_imag_parts':
        return generate_real_imag_parts()
    elif problem_type == 'complex_equality':
        return generate_complex_equality()
    elif problem_type == 'complex_arithmetic_sum_sub':
        return generate_complex_arithmetic_sum_sub()
    elif problem_type == 'complex_arithmetic_mult':
        return generate_complex_arithmetic_mult()
    elif problem_type == 'i_powers':
        return generate_i_powers()
    elif problem_type == 'complex_arithmetic_div':
        return generate_complex_arithmetic_div()


def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Special handling for "x^2 = -k" type which expects "pm N i" or "pm N sqrt(M) i"
    if correct_answer.startswith("$\\pm"):
        # Remove LaTeX and 'pm' for canonical comparison
        ua_cleaned = user_answer.replace('$', '').replace('\\pm', '').replace('\\sqrt{', 'sqrt(').replace('}', ')').strip()
        ca_cleaned = correct_answer.replace('$', '').replace('\\pm', '').replace('\\sqrt{', 'sqrt(').replace('}', ')').strip()

        is_correct = (user_answer == correct_answer) # Exact match, including LaTeX formatting

        # Also accept positive form
        if not is_correct:
            is_correct = (ua_cleaned == ca_cleaned)
        
        # Also accept negative form
        if not is_correct:
            # Need to handle potential leading minus for sqrt(N)i or Ni
            if ca_cleaned.startswith('-'): # If correct is already negative e.g. -2sqrt(3)i, this would make it positive
                is_correct = (ua_cleaned == ca_cleaned[1:]) # Compare with the positive version of correct answer
            else: # If correct is positive, compare with user's negative version
                is_correct = (ua_cleaned == '-' + ca_cleaned)
            
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # For '實部: X, 虛部: Y' format
    if correct_answer.startswith("實部:"):
        # Normalize user input: remove spaces, '實部:', '虛部:' and compare parts
        clean_user_answer = user_answer.replace(' ', '').replace('實部:', '實部:').replace('虛部:', '虛部:').strip()
        clean_correct_answer = correct_answer.replace(' ', '').replace('實部:', '實部:').replace('虛部:', '虛部:').strip()
        is_correct = (clean_user_answer == clean_correct_answer)
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
        
    # For 'x=X, y=Y' format
    if correct_answer.startswith("$x="):
        # Remove '$' from both for regex matching
        clean_user_answer = user_answer.replace('$', '').strip()
        clean_correct_answer = correct_answer.replace('$', '').strip()
        
        try:
            user_x_match = re.search(r"x\s*=\s*([+-]?\s*\d+(?:/\d+)?)", clean_user_answer)
            user_y_match = re.search(r"y\s*=\s*([+-]?\s*\d+(?:/\d+)?)", clean_user_answer)
            correct_x_match = re.search(r"x\s*=\s*([+-]?\s*\d+(?:/\d+)?)", clean_correct_answer)
            correct_y_match = re.search(r"y\s*=\s*([+-]?\s*\d+(?:/\d+)?)", clean_correct_answer)
            
            is_correct = False
            if user_x_match and user_y_match and correct_x_match and correct_y_match:
                user_x = Fraction(user_x_match.group(1).replace(' ', ''))
                user_y = Fraction(user_y_match.group(1).replace(' ', ''))
                correct_x = Fraction(correct_x_match.group(1).replace(' ', ''))
                correct_y = Fraction(correct_y_match.group(1).replace(' ', ''))
                
                is_correct = (user_x == correct_x and user_y == correct_y)
            
            result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
            return {"correct": is_correct, "result": result_text, "next_question": True}
        except Exception:
            pass # Fall through to general complex number parsing if parsing fails or regex doesn't match

    # General complex number parsing for a+bi format (e.g., for sum, sub, mult, div, i_powers)
    def parse_complex_str_to_fractions(s):
        s = s.strip().lower().replace(' ', '') # Clean up string
        if not s:
            return None, None
        
        if s == "0":
            return Fraction(0), Fraction(0)
        
        # Canonicalize implicit "1i" or "-1i" from "i" or "-i"
        # Handles cases like "i" -> "1i", "-i" -> "-1i", "1+i" -> "1+1i"
        s = re.sub(r'(?<![\d.])([+-]?)i', r'\11i', s)
        
        real_sum = Fraction(0)
        imag_sum = Fraction(0)
        
        # Regex to find terms: signed number (optionally with fraction) optionally followed by 'i'
        # e.g., "1", "+2i", "-3/4", "+5/2i"
        terms = re.findall(r"[+-]?\s*\d*(?:/\d+)?i?|[+-]?\s*\d+(?:/\d+)?", s)
        
        if not terms and s != "0": # If no terms found and it's not "0", it's invalid
            return None, None

        for term in terms:
            term = term.strip()
            if not term: continue

            if 'i' in term:
                coeff_str = term.replace('i', '')
                try:
                    if not coeff_str: # Should not happen after re.sub, but for robustness
                        imag_sum += Fraction(1)
                    elif coeff_str == '+': # e.g., from a cleaned "1+i" -> "1+1i", term is "+1i" -> coeff is "+"
                        imag_sum += Fraction(1)
                    elif coeff_str == '-': # e.g., from a cleaned "1-i" -> "1-1i", term is "-1i" -> coeff is "-"
                        imag_sum += Fraction(-1)
                    else:
                        imag_sum += Fraction(coeff_str)
                except ValueError:
                    return None, None # Invalid imaginary part
            else: # Real part
                try:
                    real_sum += Fraction(term)
                except ValueError:
                    return None, None # Invalid real part
                    
        return real_sum, imag_sum


    # Parse user and correct answers into canonical (Fraction, Fraction) tuples
    # Remove LaTeX '$' for parsing
    user_real, user_imag = parse_complex_str_to_fractions(user_answer.replace('$', ''))
    correct_real, correct_imag = parse_complex_str_to_fractions(correct_answer.replace('$', ''))
    
    is_correct = False
    if user_real is not None and user_imag is not None and \
       correct_real is not None and correct_imag is not None:
        is_correct = (user_real == correct_real and user_imag == correct_imag)

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}