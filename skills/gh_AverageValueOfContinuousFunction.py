import random
from fractions import Fraction
import math
import uuid

# Helper function to generate a random polynomial string and its parsed terms
# Returns (list of (coefficient, exponent) tuples, string representation)
def generate_polynomial_data(max_degree, max_coeff, min_degree=0):
    num_terms = random.randint(1, max_degree + 1)
    terms = []
    
    # Get distinct exponents
    exponents_pool = list(range(min_degree, max_degree + 1))
    random.shuffle(exponents_pool)
    selected_exponents = exponents_pool[:num_terms]
    selected_exponents.sort(reverse=True) # Sort for consistent display

    for exp in selected_exponents:
        coeff = random.randint(-max_coeff, max_coeff)
        # Ensure non-zero coefficients for non-constant terms, and generally avoid a zero polynomial
        # This condition allows a coefficient of 0 only if it's the last term being added AND it's a constant term (exp=0)
        # which will be filtered out later, ensuring a non-empty polynomial.
        while coeff == 0 and (len(terms) < num_terms - 1 or exp != 0):
            coeff = random.randint(-max_coeff, max_coeff)
        terms.append((Fraction(coeff), exp))
    
    # Filter out zero coefficient terms
    terms = [(c, e) for c, e in terms if c != 0]
    
    # If all selected coefficients turned out to be 0 or no terms were added (e.g., if max_coeff was 0)
    if not terms:
        # Force a non-zero constant term if polynomial ends up empty or all zero
        terms = [(Fraction(random.randint(1, max_coeff) if max_coeff > 0 else 1), 0)]
    
    # Sort terms by exponent in descending order for standard representation
    terms.sort(key=lambda x: x[1], reverse=True)
    
    poly_str_parts = []
    for i, (coeff, exp) in enumerate(terms):
        coeff_abs = abs(coeff)
        sign = "+" if coeff > 0 else "-"
        
        if i == 0 and sign == "+": # Don't print + for the first term if positive
            sign = ""
        
        term_str = ""
        if exp == 0:
            term_str = f"{coeff_abs}"
        elif exp == 1:
            if coeff_abs == 1:
                term_str = "x"
            else:
                term_str = f"{coeff_abs}x"
        else: # exp > 1
            if coeff_abs == 1:
                term_str = f"x^{{{exp}}}"
            else:
                term_str = f"{coeff_abs}x^{{{exp}}}"
        
        poly_str_parts.append(f"{sign}{term_str}")
    
    # If after all filtering, the polynomial string parts are empty, it means the polynomial is 0.
    if not poly_str_parts:
        return [(Fraction(0), 0)], "0"
        
    return terms, "".join(poly_str_parts).lstrip('+') # Return parsed terms and string representation

# Helper function to get antiderivative terms of a polynomial
def get_antiderivative_terms(poly_terms):
    antiderivative_terms = []
    for coeff, exp in poly_terms:
        # For polynomial terms ax^n, antiderivative is (a/(n+1))x^(n+1)
        # Handle n=-1 for ln, but for this skill, we generally deal with polynomial integration where n != -1.
        if exp == -1: # Should not occur with current generate_polynomial_data setup
            # This case would yield ln(x), not handled in current scope for simplicity.
            continue
        new_coefficient = coeff / Fraction(exp + 1)
        new_exponent = exp + 1
        antiderivative_terms.append((new_coefficient, new_exponent))
    return antiderivative_terms

# Helper function to evaluate a polynomial (or antiderivative) at a given value
def evaluate_at(terms, x_val):
    result = Fraction(0)
    for coeff, exp in terms:
        # x_val can be int/Fraction, convert to Fraction for consistent arithmetic
        result += coeff * (Fraction(x_val)**exp)
    return result

# Helper function to format a Fraction into a string suitable for LaTeX display
def format_fraction(frac):
    if frac.denominator == 1:
        return str(frac.numerator)
    # Use r-string for \\frac to avoid issues with backslashes
    return r"\\frac{{{}}}{{{}}}".format(frac.numerator, frac.denominator)

def generate(level=1):
    problem_type = random.choice([
        'definite_integral', 
        'average_value', 
        'kinematics_displacement',
        'kinematics_average_velocity'
    ])

    if level == 1:
        max_degree = 2 # Max x^2
        max_coeff = 5
        range_limit = 5 # Limits for integral bounds
    else: # level 2 and up
        max_degree = 3 # Max x^3
        max_coeff = 7
        range_limit = 7

    # Generate integral bounds [a, b]
    a = random.randint(-range_limit, range_limit - 1)
    b = random.randint(a + 1, range_limit) # Ensure b > a, and b is within range_limit

    # Generate polynomial
    func_terms, func_str = generate_polynomial_data(max_degree, max_coeff)
    
    # Calculate antiderivative terms
    antideriv_terms = get_antiderivative_terms(func_terms)
    
    # Evaluate antiderivative at b and a
    F_b = evaluate_at(antideriv_terms, b)
    F_a = evaluate_at(antideriv_terms, a)
    
    integral_value = F_b - F_a
    
    question_text = ""
    correct_answer = ""

    if problem_type == 'definite_integral':
        question_text = f"求定積分 $\\int_{{{a}}}^{{{b}}} ({func_str})dx$ 的值。"
        correct_answer = format_fraction(integral_value)
    
    elif problem_type == 'average_value':
        average_value = integral_value / Fraction(b - a)
        question_text = f"求函數 $f(x) = {func_str}$ 在閉區間 $[{a}, {b}]$ 上的平均值。"
        correct_answer = format_fraction(average_value)

    elif problem_type == 'kinematics_displacement':
        # Use t instead of x for kinematics
        func_str_t = func_str.replace('x', 't')
        question_text = f"一質點沿直線運動，其在時間 $t$ 時的速度函數為 $v(t) = {func_str_t}$。求此質點在時間區間 $[{a}, {b}]$ 內的位移。"
        correct_answer = format_fraction(integral_value)
    
    elif problem_type == 'kinematics_average_velocity':
        # Use t instead of x for kinematics
        func_str_t = func_str.replace('x', 't')
        average_velocity = integral_value / Fraction(b - a)
        question_text = f"一質點沿直線運動，其在時間 $t$ 時的速度函數為 $v(t) = {func_str_t}$。求此質點在時間區間 $[{a}, {b}]$ 內的平均速度。"
        correct_answer = format_fraction(average_velocity)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    try:
        # Clean user answer for comparison, removing spaces and potential LaTeX for fractions
        user_answer_cleaned = user_answer.strip().replace(" ", "").replace(r"\\frac", "").replace("{", "").replace("}", "")
        
        # Convert user_answer to Fraction. Handle potential integer input.
        if '/' in user_answer_cleaned:
            user_frac = Fraction(user_answer_cleaned)
        else:
            user_frac = Fraction(int(user_answer_cleaned))

        correct_frac = Fraction(correct_answer)
        
        is_correct = (user_frac == correct_frac)
    except (ValueError, ZeroDivisionError):
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}