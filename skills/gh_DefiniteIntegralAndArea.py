import random
from fractions import Fraction
import math

# Helper functions for polynomial operations
def poly_add(p1_coeffs, p2_coeffs):
    """Adds two polynomials (coefficient lists)."""
    max_len = max(len(p1_coeffs), len(p2_coeffs))
    result = [Fraction(0)] * max_len
    for i in range(len(p1_coeffs)):
        result[i] += p1_coeffs[i]
    for i in range(len(p2_coeffs)):
        result[i] += p2_coeffs[i]
    return trim_poly(result)

def poly_mult(p1_coeffs, p2_coeffs):
    """Multiplies two polynomials (coefficient lists)."""
    result_len = len(p1_coeffs) + len(p2_coeffs) - 1
    result = [Fraction(0)] * result_len
    for i, c1 in enumerate(p1_coeffs):
        for j, c2 in enumerate(p2_coeffs):
            result[i + j] += c1 * c2
    return trim_poly(result)

def poly_eval(coeffs, x_val):
    """Evaluates a polynomial at a given x value."""
    result = Fraction(0)
    for i, c in enumerate(coeffs):
        result += c * (x_val**i)
    return result

def poly_integrate_indefinite(coeffs):
    """Computes the indefinite integral of a polynomial."""
    if not coeffs or all(c == Fraction(0) for c in coeffs):
        return [Fraction(0)]
    integral_coeffs = [Fraction(0)] # Constant of integration, effectively x^0 term
    for i, c in enumerate(coeffs):
        integral_coeffs.append(c / Fraction(i + 1))
    return trim_poly(integral_coeffs)

def poly_definite_integral(coeffs, a, b):
    """Computes the definite integral of a polynomial from a to b."""
    integral_F_coeffs = poly_integrate_indefinite(coeffs)
    Fb = poly_eval(integral_F_coeffs, Fraction(b))
    Fa = poly_eval(integral_F_coeffs, Fraction(a))
    return Fb - Fa

def trim_poly(coeffs):
    """Removes trailing zero coefficients."""
    while len(coeffs) > 1 and coeffs[-1] == Fraction(0):
        coeffs.pop()
    return coeffs

def poly_to_latex(coeffs):
    """Converts a polynomial (coefficient list) to its LaTeX string representation."""
    terms = []
    if not coeffs or all(c == Fraction(0) for c in coeffs):
        return "0"
    
    trimmed_coeffs = trim_poly(list(coeffs)) # Work on a copy
    if not trimmed_coeffs:
        return "0"

    for i in range(len(trimmed_coeffs) - 1, -1, -1): # Iterate from highest power down
        c = trimmed_coeffs[i]
        if c == Fraction(0):
            continue
        
        coeff_str = ""
        abs_c = abs(c)
        
        sign_str = ""
        if c < 0:
            sign_str = "-"
        elif terms: # If not the first term, add '+'
            sign_str = "+"

        if abs_c.denominator == 1:
            val_str = str(abs_c.numerator)
        else:
            val_str = r"\\frac{{{}}}{{{}}}".format(abs_c.numerator, abs_c.denominator)
            
        if i == 0: # Constant term
            coeff_str = val_str
        elif abs_c == Fraction(1): # Coeff is 1 or -1, don't show '1' for x terms
            coeff_str = ""
        else:
            coeff_str = val_str

        var_str = ""
        if i == 1:
            var_str = "x"
        elif i > 1:
            var_str = f"x^{{{i}}}"
        
        terms.append(f"{sign_str}{coeff_str}{var_str}")

    result = "".join(terms)
    # Remove leading '+' if any
    if result.startswith("+"):
        result = result[1:]
    
    return result

def generate_factored_polynomial(degree):
    """Generates a polynomial with integer roots for simpler problem generation."""
    if degree == 2:
        r1 = random.randint(-4, 4)
        r2 = random.randint(r1 + 1, r1 + 5) # Ensure distinct roots
        
        # f(x) = (x-r1)(x-r2)
        poly_x_minus_r1 = [Fraction(-r1), Fraction(1)] # x - r1
        poly_x_minus_r2 = [Fraction(-r2), Fraction(1)] # x - r2
        coeffs = poly_mult(poly_x_minus_r1, poly_x_minus_r2)
        return coeffs, sorted([Fraction(r1), Fraction(r2)])
    elif degree == 3:
        # f(x) = x(x-r1)(x-r2)
        r1 = random.randint(-3, -1)
        r2 = random.randint(1, 3)
        
        poly_x = [Fraction(0), Fraction(1)]
        poly_x_minus_r1 = [Fraction(-r1), Fraction(1)]
        poly_x_minus_r2 = [Fraction(-r2), Fraction(1)]
        
        coeffs = poly_mult(poly_x, poly_mult(poly_x_minus_r1, poly_x_minus_r2))
        return coeffs, sorted([Fraction(0), Fraction(r1), Fraction(r2)])
    else:
        return None, []

def generate(level=1):
    """
    Generates a definite integral and area problem.
    Problems include:
    1. Area of a polynomial with consistent sign over an interval.
    2. Area of a polynomial with mixed signs over an interval (requires splitting).
    3. Definite integral of an absolute value function |ax+b|.
    """
    problem_type_weights = {
        'polynomial_area_simple_sign': 4,
        'polynomial_area_mixed_sign': 5,
        'absolute_value_integral': 1,
    }
    
    problem_type = random.choices(
        list(problem_type_weights.keys()),
        weights=list(problem_type_weights.values()),
        k=1
    )[0]

    if problem_type == 'polynomial_area_simple_sign':
        return generate_polynomial_area_simple_sign_problem(level)
    elif problem_type == 'polynomial_area_mixed_sign':
        return generate_polynomial_area_mixed_sign_problem(level)
    elif problem_type == 'absolute_value_integral':
        return generate_absolute_value_integral_problem(level)

def generate_polynomial_area_simple_sign_problem(level):
    """
    Generates a problem where f(x) has a consistent sign over the integration interval.
    Uses a quadratic function f(x) = (x-r1)(x-r2).
    """
    coeffs, roots_frac = generate_factored_polynomial(2)
    r1_val, r2_val = roots_frac[0], roots_frac[1] # Fraction objects, r1_val < r2_val

    a_calc, b_calc = 0, 0 # These will be integers for the interval [a, b]
    
    choice = random.choice(['between_roots', 'outside_roots_left', 'outside_roots_right'])

    if choice == 'between_roots':
        # Integrate between roots: f(x) <= 0 for (x-r1)(x-r2)
        a_calc = int(r1_val)
        b_calc = int(r2_val)
        # Adjust bounds slightly if there's enough room, keeping them integers
        if b_calc - a_calc > 2: # At least 3 units span
            a_calc += random.randint(0, 1)
            b_calc -= random.randint(0, 1)
        if a_calc >= b_calc: # Fallback if adjustment made it invalid
            a_calc = int(r1_val)
            b_calc = int(r2_val)
            if a_calc >= b_calc: # Ensure at least a 1-unit interval
                b_calc = a_calc + 1 
    else:
        # Integrate outside roots: f(x) >= 0 for (x-r1)(x-r2)
        interval_length = random.randint(1, 3)
        if choice == 'outside_roots_left':
            b_calc = int(r1_val)
            a_calc = b_calc - interval_length
        else: # outside_roots_right
            a_calc = int(r2_val)
            b_calc = a_calc + interval_length
        
        if a_calc >= b_calc: # Fallback to a simple positive interval if random selection failed
            a_calc = 0
            b_calc = 1

    integral_val = poly_definite_integral(coeffs, a_calc, b_calc)
    area = abs(integral_val) # Area is always non-negative

    f_x_latex = poly_to_latex(coeffs)
    
    question_text = (
        f"求函數 $f(x) = {f_x_latex}$ 的圖形與 $x$ 軸在區間 $[{a_calc}, {b_calc}]$ 所圍成的區域面積。"
    )
    correct_answer = str(area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_polynomial_area_mixed_sign_problem(level):
    """
    Generates a problem where f(x) changes sign within the integration interval.
    Uses quadratic or cubic functions.
    """
    degree = random.choice([2, 3])
    coeffs, roots = generate_factored_polynomial(degree)
    
    min_root_val = min(r.numerator / r.denominator for r in roots)
    max_root_val = max(r.numerator / r.denominator for r in roots)
    
    # Define an interval [a, b] that spans across roots, ensuring sign changes
    a = math.floor(min_root_val - random.randint(1, 2))
    b = math.ceil(max_root_val + random.randint(1, 2))
    
    # Ensure a < b and a reasonable span
    if b - a < 2:
        a -= 1
        b += 1
    
    # Collect all roots within [a, b] and add interval endpoints to create sub-intervals
    critical_points = sorted(list(set([Fraction(a), Fraction(b)] + [r for r in roots if a <= r <= b])))
    
    total_area = Fraction(0)

    for i in range(len(critical_points) - 1):
        sub_a = critical_points[i]
        sub_b = critical_points[i+1]
        
        if sub_a == sub_b: continue # Skip if interval is a single point

        # The area is the sum of the absolute values of definite integrals over sub-intervals
        integral_val = poly_definite_integral(coeffs, sub_a, sub_b)
        
        total_area += abs(integral_val)
        
    f_x_latex = poly_to_latex(coeffs)
    
    question_text = (
        f"求函數 $f(x) = {f_x_latex}$ 的圖形與 $x$ 軸在區間 $[{a}, {b}]$ 所圍成的區域面積。"
    )
    correct_answer = str(total_area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_absolute_value_integral_problem(level):
    """
    Generates a problem to calculate the definite integral of a function of the form |ax+b|.
    """
    a_coeff = random.choice([-2, -1, 1, 2])
    b_coeff = random.randint(-5, 5)
    
    # Critical point where ax+b = 0
    critical_point = Fraction(-b_coeff, a_coeff)
    
    # Define integration interval [L, R]
    L_val = math.floor(critical_point - random.randint(1, 3))
    R_val = math.ceil(critical_point + random.randint(1, 3))
    
    # Ensure L < R and a reasonable span
    if R_val - L_val < 2:
        L_val -= 1
        R_val += 1

    total_integral_value = Fraction(0)
    
    # Split the interval at the critical point if it's within [L, R]
    split_points = sorted(list(set([Fraction(L_val), Fraction(R_val), critical_point])))
    split_points = [p for p in split_points if Fraction(L_val) <= p <= Fraction(R_val)]

    for i in range(len(split_points) - 1):
        sub_L = split_points[i]
        sub_R = split_points[i+1]
        
        if sub_L == sub_R: continue

        test_x = (sub_L + sub_R) / 2
        
        # Evaluate ax+b at a test point to determine its sign in the sub-interval
        linear_val = a_coeff * test_x + b_coeff
        
        # Construct coefficients for the piecewise function (ax+b) or -(ax+b)
        if linear_val >= 0:
            coeffs_for_segment = [Fraction(b_coeff), Fraction(a_coeff)] # [b, a] for ax+b
        else:
            coeffs_for_segment = [Fraction(-b_coeff), Fraction(-a_coeff)] # [-b, -a] for -(ax+b)
        
        total_integral_value += poly_definite_integral(coeffs_for_segment, sub_L, sub_R)
        
    linear_func_latex = poly_to_latex([Fraction(b_coeff), Fraction(a_coeff)])
    f_x_latex = f"|{linear_func_latex}|"
    
    question_text = (
        f"求 $\\int_{{{L_val}}}^{{{R_val}}} {f_x_latex} dx$ 的值。"
    )
    correct_answer = str(total_integral_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Converts both answers to fractions for precise comparison.
    """
    is_correct = False
    feedback = ""

    try:
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        
        if user_frac == correct_frac:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"
    except ValueError:
        feedback = "請輸入有效的數字或分數（例如 '3/4' 或 '5'）。"

    return {"correct": is_correct, "result": feedback, "next_question": True}