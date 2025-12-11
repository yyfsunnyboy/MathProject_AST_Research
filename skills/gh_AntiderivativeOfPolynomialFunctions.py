import random
from fractions import Fraction
import re

def format_polynomial_term_for_display(coeff, power):
    """
    Generates a LaTeX-formatted string for a single polynomial term.
    e.g., $2x^{2}$, $-x$, $5$, $x^3$, $\\frac{1}{2}x^2$
    """
    if coeff == 0:
        return ""

    coeff_str = ""
    if coeff == 1 and power != 0: # For x^n or x, coefficient 1 is implicit
        coeff_str = ""
    elif coeff == -1 and power != 0: # For -x^n or -x, coefficient -1 is implicit
        coeff_str = "-"
    else:
        # Format Fraction for display. Use \\frac if it's not an integer.
        if coeff.denominator == 1:
            coeff_str = str(coeff.numerator)
        else:
            # Using raw string for fraction in LaTeX.
            # Python f-string requires double braces for literal braces.
            # So, \\frac{{num}}{{den}}
            coeff_str = r"\\frac{{" + str(coeff.numerator) + r"}}{{" + str(coeff.denominator) + r"}}"

    if power == 0: # Constant term
        return coeff_str
    elif power == 1: # x^1 term (e.g., 2x instead of 2x^1)
        return f"{coeff_str}x"
    else: # x^n term (n > 1)
        # Double braces are crucial for LaTeX exponents inside an f-string
        return f"{coeff_str}x^{{{power}}}"

def format_polynomial_string_for_display(terms, include_C=True):
    """
    Combines a list of polynomial terms into a full LaTeX-formatted polynomial string.
    Terms are sorted by power in descending order.
    `terms` is a list of {'coeff': Fraction, 'power': int}
    """
    
    # Filter out zero terms and sort by power in descending order
    sorted_terms = sorted([t for t in terms if t['coeff'] != 0], key=lambda x: x['power'], reverse=True)
    
    parts = []
    for i, term in enumerate(sorted_terms):
        term_str = format_polynomial_term_for_display(term['coeff'], term['power'])
        if not term_str:
            continue
            
        # Add '+' for subsequent positive terms.
        # Handle negative fractions as well, which might start with \\frac{{-
        is_negative_term = term_str.startswith('-') or term_str.startswith(r"\\frac{{-")
        if i > 0 and not is_negative_term:
            parts.append(f"+{term_str}")
        else:
            parts.append(term_str)
            
    if not parts: # If all terms cancelled out, it's just '0'
        poly_str = "0"
    else:
        poly_str = "".join(parts)
        
    if include_C:
        if poly_str == "0": # If the polynomial is just 0, the antiderivative is C
            return "C"
        return f"{poly_str} + C"
    else:
        return poly_str

def format_polynomial_string_for_check(terms, include_C=True):
    """
    Generates a canonical string representation for internal checking purposes.
    No LaTeX, specific fraction format (e.g., '1/2'), strict term order, no spaces.
    """
    
    sorted_terms = sorted([t for t in terms if t['coeff'] != 0], key=lambda x: x['power'], reverse=True)
    
    parts = []
    for i, term in enumerate(sorted_terms):
        coeff = term['coeff']
        power = term['power']

        coeff_str = ""
        if coeff == 1 and power != 0:
            coeff_str = ""
        elif coeff == -1 and power != 0:
            coeff_str = "-"
        else:
            # Use standard string representation for Fraction (e.g., '1/2', '-3/4')
            coeff_str = str(coeff)
        
        term_str = ""
        if power == 0: # Constant term
            term_str = str(coeff)
        elif power == 1: # x^1 term should be 'x'
            term_str = f"{coeff_str}x"
        else: # x^n term
            term_str = f"{coeff_str}x^{power}" # No LaTeX braces here for internal check
        
        if not term_str:
            continue
            
        if i > 0 and not term_str.startswith('-'):
            parts.append(f"+{term_str}")
        else:
            parts.append(term_str)
            
    if not parts:
        poly_str = "0"
    else:
        poly_str = "".join(parts)
        
    if include_C:
        if poly_str == "0":
            return "C"
        return f"{poly_str}+C" # No space before +C for strict check
    else:
        return poly_str

def calculate_antiderivative_terms(f_terms):
    """
    Calculates the antiderivative for a list of polynomial terms.
    Applies the power rule: $\\int ax^n dx = \\frac{a}{n+1}x^{n+1}$
    """
    F_terms = []
    for term in f_terms:
        coeff = term['coeff']
        power = term['power']
        
        new_power = power + 1
        # For polynomial antiderivatives where input powers are non-negative,
        # new_power will always be >= 1, so division by zero is not a concern.
        
        new_coeff = coeff / new_power
        F_terms.append({'coeff': new_coeff, 'power': new_power})
    return F_terms

def generate_single_term_antiderivative():
    """Generates a problem asking for the antiderivative of a single polynomial term."""
    f_coeff = Fraction(random.choice([-1, 1]) * random.randint(1, 10))
    f_power = random.randint(0, 4) # Allow constant terms (power 0)
    
    f_terms = [{'coeff': f_coeff, 'power': f_power}]
    f_x_display = format_polynomial_string_for_display(f_terms, include_C=False)
    
    F_terms = calculate_antiderivative_terms(f_terms)
    F_x_check_answer = format_polynomial_string_for_check(F_terms, include_C=True)
    
    question_text = f"已知多項式函數 $f(x) = {f_x_display}$，請求出其反導函數 $F(x)$。" \
                    r"<br>（答案請包含積分常數 $C$，並請寫為如 $x^{{2}} + C$ 或 $\\frac{{1}}{{2}}x^{{2}} - 3x + C$ 的形式）"
    
    return {
        "question_text": question_text,
        "answer": F_x_check_answer,
        "correct_answer": F_x_check_answer
    }

def generate_polynomial_antiderivative_general():
    """Generates a problem asking for the general antiderivative of a polynomial."""
    num_terms = random.randint(2, 4)
    f_terms = []
    seen_powers = set()
    
    for _ in range(num_terms):
        while True:
            f_power = random.randint(0, 4)
            if f_power not in seen_powers: # Ensure unique powers in the polynomial
                seen_powers.add(f_power)
                break
        f_coeff = Fraction(random.choice([-1, 1]) * random.randint(1, 8))
        f_terms.append({'coeff': f_coeff, 'power': f_power})

    f_x_display = format_polynomial_string_for_display(f_terms, include_C=False)
    
    F_terms = calculate_antiderivative_terms(f_terms)
    F_x_check_answer = format_polynomial_string_for_check(F_terms, include_C=True)
    
    question_text = f"請求出函數 $f(x) = {f_x_display}$ 的不定積分。" \
                    r"<br>（答案請包含積分常數 $C$，並請寫為如 $x^{{3}} - 2x + C$ 或 $\\frac{{1}}{{2}}x^{{2}} - 3x + C$ 的形式）"
    
    return {
        "question_text": question_text,
        "answer": F_x_check_answer,
        "correct_answer": F_x_check_answer
    }

def generate_polynomial_antiderivative_specific():
    """
    Generates a problem asking for a specific antiderivative given a point,
    thus allowing to determine the constant of integration C.
    """
    num_terms = random.randint(2, 3)
    f_terms = []
    seen_powers = set()
    
    for _ in range(num_terms):
        while True:
            f_power = random.randint(0, 3) # Keep powers low for easier evaluation
            if f_power not in seen_powers:
                seen_powers.add(f_power)
                break
        f_coeff = Fraction(random.choice([-1, 1]) * random.randint(1, 6))
        f_terms.append({'coeff': f_coeff, 'power': f_power})
    
    f_x_display = format_polynomial_string_for_display(f_terms, include_C=False)
    
    # Calculate general antiderivative terms (F_general_terms + C)
    F_general_terms = calculate_antiderivative_terms(f_terms)
    
    # Choose a specific x0 value for the given point (F(x0) = y0)
    x0 = random.randint(-2, 2)
    
    # Generate a random integer value for the constant C (C_initial)
    C_initial = Fraction(random.randint(-5, 5))
    
    # Calculate the corresponding y0 value using C_initial
    y0_val_at_x0 = Fraction(0)
    for term in F_general_terms:
        y0_val_at_x0 += term['coeff'] * (Fraction(x0) ** term['power'])
    y0_val_at_x0 += C_initial 
    
    # Construct the final antiderivative terms, incorporating C_initial into the constant term
    final_F_terms = []
    constant_term_added = False
    for term in F_general_terms:
        if term['power'] == 0:
            final_F_terms.append({'coeff': term['coeff'] + C_initial, 'power': 0})
            constant_term_added = True
        else:
            final_F_terms.append(term)
    if not constant_term_added: # If no constant term in F_general_terms, add C_initial as a new term
        final_F_terms.append({'coeff': C_initial, 'power': 0})

    F_x_final_display = format_polynomial_string_for_display(final_F_terms, include_C=False)
    F_x_final_check_answer = format_polynomial_string_for_check(final_F_terms, include_C=False)

    question_text = f"已知 $F'(x) = {f_x_display}$ 且 $F({x0}) = {y0_val_at_x0}$，請求出 $F(x)$。" \
                    r"<br>（答案不需包含積分常數 $C$，並請寫為如 $x^{{2}} + 3$ 或 $\\frac{{1}}{{2}}x^{{2}} - 3x + 1$ 的形式）"
    
    return {
        "question_text": question_text,
        "answer": F_x_final_check_answer,
        "correct_answer": F_x_final_check_answer
    }

def generate_indefinite_integral_notation():
    """Generates a problem using indefinite integral notation $\\int f(x) dx$."""
    num_terms = random.randint(1, 3)
    f_terms = []
    seen_powers = set()
    
    for _ in range(num_terms):
        while True:
            f_power = random.randint(0, 3)
            if f_power not in seen_powers:
                seen_powers.add(f_power)
                break
        f_coeff = Fraction(random.choice([-1, 1]) * random.randint(1, 5))
        f_terms.append({'coeff': f_coeff, 'power': f_power})

    f_x_display = format_polynomial_string_for_display(f_terms, include_C=False)
    
    F_terms = calculate_antiderivative_terms(f_terms)
    F_x_check_answer = format_polynomial_string_for_check(F_terms, include_C=True)
    
    question_text = f"請求出下列不定積分的值：<br>$\\int ({f_x_display}) dx$" \
                    r"<br>（答案請包含積分常數 $C$，並請寫為如 $x^{{3}} - 2x + C$ 或 $\\frac{{1}}{{2}}x^{{2}} - 3x + C$ 的形式）"
    
    return {
        "question_text": question_text,
        "answer": F_x_check_answer,
        "correct_answer": F_x_check_answer
    }


def generate(level=1):
    """
    Generates a question for antiderivatives of polynomial functions.
    The `level` parameter can adjust complexity:
    - Level 1: Focus on single terms or general polynomials, and notation.
    - Level 2-3: Include specific antiderivatives (finding C) which are slightly more complex.
    """
    problem_type_choices = {
        1: ['single_term', 'general_poly', 'notation'],
        2: ['general_poly', 'specific_poly', 'notation'],
        3: ['general_poly', 'specific_poly', 'notation']
    }
    
    # Select a problem type based on level, defaulting to general_poly if level is out of range
    problem_type = random.choice(problem_type_choices.get(level, ['general_poly']))

    if problem_type == 'single_term':
        return generate_single_term_antiderivative()
    elif problem_type == 'general_poly':
        return generate_polynomial_antiderivative_general()
    elif problem_type == 'specific_poly':
        return generate_polynomial_antiderivative_specific()
    elif problem_type == 'notation':
        return generate_indefinite_integral_notation()
    

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for polynomial antiderivative questions.
    Performs basic normalization (whitespace, case for 'C') before string comparison.
    """
    
    # 1. Strip whitespace from user answer and standardize 'c' to 'C'
    normalized_user_answer = user_answer.strip().replace(" ", "").replace("c", "C")
    
    # 2. Correct answer is generated in a canonical form by `format_polynomial_string_for_check`,
    #    so just ensure it's also stripped of any potential whitespace for strict comparison.
    normalized_correct_answer = correct_answer.strip().replace(" ", "")

    # For cases where the correct answer explicitly has '+C' (e.g., 'x^2+C'),
    # and the user provides 'x^2C', adjust user input for comparison.
    if normalized_correct_answer.endswith('+C') and not normalized_user_answer.endswith('+C') and normalized_user_answer.endswith('C'):
        normalized_user_answer = normalized_user_answer.replace('C', '+C')
    
    # Final string comparison for correctness
    is_correct = (normalized_user_answer == normalized_correct_answer)
    
    # Feedback message, using LaTeX for the correct answer display
    result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}