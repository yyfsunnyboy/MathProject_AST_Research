import random
from fractions import Fraction

# Helper class to represent polynomial functions
class Polynomial:
    def __init__(self, coeffs):
        """
        Initializes a Polynomial object.
        coeffs: A dictionary where keys are powers and values are coefficients.
                Example: {2: 3, 1: -2, 0: 5} represents 3x^2 - 2x + 5.
        Coefficients are stored as Fractions for precision.
        """
        self.coeffs = {power: Fraction(coeff) for power, coeff in coeffs.items() if coeff != 0}
        # Ensure a canonical representation for the zero polynomial
        if not self.coeffs:
            self.coeffs[0] = Fraction(0)

    def __str__(self):
        """
        Returns a LaTeX-formatted string representation of the polynomial.
        Example: "3x^{{ 2 }} - 2x + 5"
        """
        terms = []
        # Sort terms by power in descending order for standard polynomial notation
        sorted_powers = sorted(self.coeffs.keys(), reverse=True)

        for power in sorted_powers:
            coeff = self.coeffs[power]
            if coeff == 0:
                continue

            coeff_str = ""
            abs_coeff = abs(coeff)

            # Determine coefficient string part
            if power == 0:  # Constant term
                coeff_str = str(abs_coeff)
            elif power == 1:  # Linear term
                coeff_str = "x" if abs_coeff == 1 else f"{abs_coeff}x"
            else:  # Higher power terms
                coeff_str = f"x^{{ {power} }}" if abs_coeff == 1 else f"{abs_coeff}x^{{ {power} }}"

            # Add sign and combine with existing terms
            if coeff > 0:
                terms.append(f"+ {coeff_str}")
            else:  # coeff < 0
                terms.append(f"- {coeff_str}")
        
        if not terms:
            return "0"
        
        # Remove leading "+" if the first term is positive
        full_poly_str = " ".join(terms).strip()
        if full_poly_str.startswith("+ "):
            full_poly_str = full_poly_str[2:]
        return full_poly_str

    def antiderivative(self):
        """
        Calculates the antiderivative of the polynomial (indefinite integral).
        Assumes the constant of integration C = 0.
        """
        anti_coeffs = {}
        for power, coeff in self.coeffs.items():
            if coeff != 0:
                anti_coeffs[power + 1] = coeff / (power + 1)
        return Polynomial(anti_coeffs)

    def derivative(self):
        """
        Calculates the derivative of the polynomial.
        """
        deriv_coeffs = {}
        for power, coeff in self.coeffs.items():
            if power > 0:
                deriv_coeffs[power - 1] = coeff * power
        return Polynomial(deriv_coeffs)

    def evaluate(self, x_val):
        """
        Evaluates the polynomial at a given x value.
        x_val can be an integer or a Fraction.
        """
        result = Fraction(0)
        x_val_frac = Fraction(x_val)
        for power, coeff in self.coeffs.items():
            result += coeff * (x_val_frac**power)
        return result

# Helper function to generate a random polynomial
def generate_polynomial(max_degree, max_coeff_abs, num_terms):
    """
    Generates a random polynomial for problem creation.
    """
    if max_degree < 0: max_degree = 0
    if num_terms > max_degree + 1: num_terms = max_degree + 1
    if num_terms < 1: num_terms = 1

    degree = random.randint(1, max_degree) if max_degree > 0 else 0
    coeffs = {}
    
    # Ensure the highest degree term exists and is not zero
    if degree >= 0:
        coeffs[degree] = random.randint(-max_coeff_abs, max_coeff_abs)
        while coeffs[degree] == 0:
            coeffs[degree] = random.randint(-max_coeff_abs, max_coeff_abs)
    
    # Add remaining terms
    powers_to_use = set(coeffs.keys())
    while len(powers_to_use) < num_terms:
        p = random.randint(0, degree) # Can include 0 for constant term
        if p not in powers_to_use:
            coeffs[p] = random.randint(-max_coeff_abs, max_coeff_abs)
            powers_to_use.add(p)
    
    # Clean up any zero coefficients that might have been generated
    coeffs = {k: v for k, v in coeffs.items() if v != 0}
    
    # Ensure at least a constant if all other terms are zero (edge case if max_degree=0)
    if not coeffs:
        coeffs[0] = random.randint(1, max_coeff_abs)

    return Polynomial(coeffs)

# Helper function to format a Fraction as a string (integer, fraction, or mixed number)
def format_fraction_answer(frac_val):
    if frac_val.denominator == 1:
        return str(frac_val.numerator)
    else:
        # Check if it's a mixed number (e.g., 5_1/2 or -5_1/2)
        if abs(frac_val.numerator) > frac_val.denominator:
            whole_part = frac_val.numerator // frac_val.denominator
            fraction_part = frac_val - whole_part
            if fraction_part == 0:
                return str(whole_part)
            else:
                return f"{whole_part}_{abs(fraction_part.numerator)}/{fraction_part.denominator}"
        else:
            return f"{frac_val.numerator}/{frac_val.denominator}"

def generate_definite_integral_polynomial(level):
    """
    Generates a problem asking to evaluate a definite integral of a polynomial.
    """
    max_degree = 2 if level == 1 else 3
    max_coeff_abs = 5 if level == 1 else 8
    num_terms = random.randint(1, max_degree + 1)

    poly_f = generate_polynomial(max_degree, max_coeff_abs, num_terms)

    # Limits of integration
    lower_limit = random.randint(-3, 1) if level == 1 else random.randint(-5, 0)
    upper_limit = random.randint(2, 5) if level == 1 else random.randint(1, 6)
    
    # Ensure limits are distinct
    while lower_limit == upper_limit:
        upper_limit = random.randint(lower_limit + 1, lower_limit + 5)
        if upper_limit <= lower_limit: # Fallback if random range is too tight
            upper_limit = lower_limit + random.randint(1, 3)

    # Calculate antiderivative and evaluate
    poly_F = poly_f.antiderivative()
    correct_answer_frac = poly_F.evaluate(upper_limit) - poly_F.evaluate(lower_limit)
    correct_answer_str = format_fraction_answer(correct_answer_frac)

    question_text = f"求下列定積分的值：<br>$\\int_{{{lower_limit}}}^{{{upper_limit}}} ({poly_f}) dx$"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_integral_properties_problem(level):
    """
    Generates a problem testing definite integral properties (additivity or linearity).
    """
    prop_type = random.choice(['additivity', 'linearity'])

    if prop_type == 'additivity':
        # Problem: Given int_a^b f(x)dx and int_b^c f(x)dx, find int_a^c f(x)dx
        val1 = random.randint(1, 10)
        val2 = random.randint(1, 10)
        
        a = random.randint(-3, 0)
        b = random.randint(a + 1, a + 4)
        c = random.randint(b + 1, b + 4)

        function_name = random.choice(['f(x)', 'g(x)', 'h(x)'])

        question_text = f"已知 $\\int_{{{a}}}^{{{b}}} {function_name} dx = {val1}$ 且 $\\int_{{{b}}}^{{{c}}} {function_name} dx = {val2}$，求 $\\int_{{{a}}}^{{{c}}} {function_name} dx$ 的值。"
        correct_answer = str(val1 + val2)

    elif prop_type == 'linearity':
        # Problem: Given int_a^b f(x)dx, find int_a^b (k*f(x) +/- l*P(x))dx
        func_val = random.randint(1, 10)
        a = random.randint(-2, 0)
        b = random.randint(1, 3)
        
        k = random.randint(2, 5)
        l = random.randint(1, 3)
        
        function_name = random.choice(['f(x)', 'g(x)', 'h(x)'])
        
        # Add a polynomial term to integrate directly
        max_poly_degree = 1 if level == 1 else 2
        max_poly_coeff_abs = 4 if level == 1 else 6
        poly_g = generate_polynomial(max_poly_degree, max_poly_coeff_abs, random.randint(1, max_poly_degree + 1))
        
        poly_G_anti = poly_g.antiderivative()
        poly_G_val = poly_G_anti.evaluate(b) - poly_G_anti.evaluate(a)
        
        op = random.choice(['+', '-'])
        
        if op == '+':
            integral_expression = f"{k}{function_name} + {l}({poly_g})"
            correct_answer_frac = Fraction(k * func_val) + Fraction(l) * poly_G_val
        else:
            integral_expression = f"{k}{function_name} - {l}({poly_g})"
            correct_answer_frac = Fraction(k * func_val) - Fraction(l) * poly_G_val

        correct_answer = format_fraction_answer(correct_answer_frac)

        question_text = f"已知 $\\int_{{{a}}}^{{{b}}} {function_name} dx = {func_val}$，求 $\\int_{{{a}}}^{{{b}}} ({integral_expression}) dx$ 的值。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_unknown_problem(level):
    """
    Generates a problem where an unknown (limit or coefficient) needs to be found
    using the Fundamental Theorem of Calculus.
    """
    unknown_type = random.choice(['limit', 'coeff'])
    
    if unknown_type == 'limit':
        # Problem: int_L^b P(x) dx = K, find b
        max_degree = 2 if level == 1 else 3
        max_coeff_abs = 4 if level == 1 else 6
        num_terms = random.randint(1, max_degree + 1)

        poly_f = generate_polynomial(max_degree, max_coeff_abs, num_terms)
        poly_F = poly_f.antiderivative()

        lower_limit = random.randint(-2, 1)
        
        # Choose a correct 'b' first to ensure an integer solution
        possible_b_range = list(range(lower_limit + 1, lower_limit + 5)) + list(range(lower_limit - 4, lower_limit))
        possible_b_range = [x for x in possible_b_range if x != lower_limit]
        if not possible_b_range: # Fallback for very restrictive limits
            possible_b_range = [lower_limit + 1]
        
        correct_b = random.choice(possible_b_range)

        # Calculate K based on the chosen 'b'
        K_frac = poly_F.evaluate(correct_b) - poly_F.evaluate(lower_limit)
        K_str = format_fraction_answer(K_frac)

        question_text = f"已知 $\\int_{{{lower_limit}}}^b ({poly_f}) dx = {K_str}$，求實數 $b$ 的值。"
        correct_answer = str(correct_b)

    elif unknown_type == 'coeff':
        # Problem: int_L^U (ax^d + P(x)) dx = K, find a
        max_degree = 2 if level == 1 else 3
        max_coeff_abs = 3 if level == 1 else 5
        
        # Define the power 'd' for the unknown 'a' term
        d_power = random.randint(0, max_degree + 1) # 'a' could be a constant (d=0) or higher power
        
        # Generate other terms for the polynomial
        poly_terms_coeffs = {}
        for _ in range(random.randint(1, max_degree)): # Number of additional terms
            power = random.randint(0, max_degree + 1)
            while power == d_power or power in poly_terms_coeffs: # Ensure no conflict with 'a' term or existing terms
                power = random.randint(0, max_degree + 1)
            poly_terms_coeffs[power] = random.randint(-max_coeff_abs, max_coeff_abs)

        # Determine the true value of 'a' (the unknown)
        true_a_val = random.randint(-4, 4)
        while true_a_val == 0:
            true_a_val = random.randint(-4, 4)

        # Construct the full polynomial for calculation
        full_poly_coeffs = {d_power: Fraction(true_a_val)}
        full_poly_coeffs.update(poly_terms_coeffs)
        poly_f_with_true_a = Polynomial(full_poly_coeffs)
        
        # Construct the display string for the polynomial with 'a' as a variable
        display_terms = []
        # Combine numerical terms and 'a' term (order matters for display)
        all_powers = sorted(list(poly_terms_coeffs.keys()) + [d_power], reverse=True)
        
        for power in all_powers:
            if power == d_power: # This is the 'a' term
                coeff_str = ""
                if power == 0:
                    coeff_str = "a"
                elif power == 1:
                    coeff_str = "ax"
                else:
                    coeff_str = f"ax^{{ {power} }}"
                display_terms.append(coeff_str)
            else: # Numerical term
                coeff = poly_terms_coeffs[power]
                abs_coeff = abs(coeff)
                if power == 0:
                    term_str = str(abs_coeff)
                elif power == 1:
                    term_str = "x" if abs_coeff == 1 else f"{abs_coeff}x"
                else:
                    term_str = f"x^{{ {power} }}" if abs_coeff == 1 else f"{abs_coeff}x^{{ {power} }}"
                
                if coeff > 0:
                    display_terms.append(f"+ {term_str}")
                else:
                    display_terms.append(f"- {term_str}")
        
        # Clean up leading '+' and spaces
        display_poly_str = " ".join(display_terms).strip()
        if display_poly_str.startswith("+ "):
            display_poly_str = display_poly_str[2:]

        lower_limit = random.randint(-2, 0)
        upper_limit = random.randint(1, 3)

        K_frac = poly_f_with_true_a.antiderivative().evaluate(upper_limit) - poly_f_with_true_a.antiderivative().evaluate(lower_limit)
        K_str = format_fraction_answer(K_frac)

        question_text = f"已知 $\\int_{{{lower_limit}}}^{{{upper_limit}}} ({display_poly_str}) dx = {K_str}$，求實數 $a$ 的值。"
        correct_answer = str(true_a_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_leibniz_rule_problem(level):
    """
    Generates a problem related to the Leibniz Integral Rule (First Part of FTC).
    """
    rule_type = random.choice(['find_f', 'find_a'])

    if rule_type == 'find_f':
        # Problem: Given int_a^x f(t)dt = G(x), find f(x)
        # G(x) will be a polynomial, f(x) is its derivative
        degree_G = random.randint(2, 3) if level == 1 else random.randint(3, 4)
        poly_G = generate_polynomial(degree_G, 5, random.randint(2, degree_G + 1))
        
        poly_f = poly_G.derivative() # f(x) = d/dx G(x)
        
        question_text = f"已知函數 $f(t)$ 滿足 $\\int_a^x f(t)dt = {poly_G}$，求 $f(x)$。"
        correct_answer = str(poly_f)

    elif rule_type == 'find_a':
        # Problem: Given int_a^x f(t)dt = G(x), find a.
        # This implies G(a) = 0. G(x) is constructed to have integer roots.
        
        # Construct G(x) from 2 distinct integer roots
        root1 = random.randint(-5, 0)
        root2 = random.randint(1, 5)
        while root1 == root2: # Ensure distinct roots
            root2 = random.randint(1, 5)
            
        # G(x) = (x - root1)(x - root2) = x^2 - (root1+root2)x + root1*root2
        coeffs_G = {
            2: Fraction(1),
            1: Fraction(-(root1 + root2)),
            0: Fraction(root1 * root2)
        }
        poly_G = Polynomial(coeffs_G)
        
        question_text = f"已知 $a$ 為實數，且函數 $f(t)$ 滿足 $\\int_a^x f(t)dt = {poly_G}$，求實數 $a$ 的值。"
        
        # The correct answer can be either root. Provide them sorted, separated by " or ".
        possible_answers = [str(root1), str(root2)]
        correct_answer = " or ".join(sorted(possible_answers))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a math problem related to the Fundamental Theorem of Calculus.
    Problems vary based on the 'level' parameter and random selection.
    """
    problem_type = random.choice([
        'definite_integral_polynomial',
        'integral_properties',
        'find_unknown',
        'leibniz_rule'
    ])

    if problem_type == 'definite_integral_polynomial':
        return generate_definite_integral_polynomial(level)
    elif problem_type == 'integral_properties':
        return generate_integral_properties_problem(level)
    elif problem_type == 'find_unknown':
        return generate_find_unknown_problem(level)
    elif problem_type == 'leibniz_rule':
        return generate_leibniz_rule_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, supporting various answer formats
    including integers, fractions, mixed numbers, polynomials, and multiple choices.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Helper to parse a number string into a Fraction (supports integers, fractions, mixed numbers)
    def parse_number_string_to_fraction(s):
        s = s.replace(" ", "") # Remove spaces
        if '_' in s: # Mixed number e.g., "3_1/2" or "-3_1/2"
            parts = s.split('_')
            if len(parts) == 2:
                try:
                    whole = Fraction(parts[0])
                    frac_part = Fraction(parts[1])
                    return whole + frac_part if whole >= 0 else whole - frac_part
                except ValueError:
                    return None
            else: # Invalid mixed number format
                return None
        elif '/' in s: # Fraction e.g., "1/2"
            try:
                return Fraction(s)
            except ValueError:
                return None
        else: # Integer
            try:
                return Fraction(int(s))
            except ValueError:
                return None # Not a valid number

    # Handle multiple correct answers (e.g., "5 or -2") by splitting and comparing sets
    correct_answers_set = {ans.strip() for ans in correct_answer.split(" or ")}
    user_answers_set = {ans.strip() for ans in user_answer.split(" or ")}

    is_correct = False
    
    # Attempt direct string comparison first
    if correct_answers_set == user_answers_set:
        is_correct = True
    else:
        # Attempt numerical comparison if string comparison fails
        # Convert all possible answers to Fractions for robust comparison
        try:
            parsed_user_nums = sorted([parse_number_string_to_fraction(u_ans) for u_ans in user_answers_set if parse_number_string_to_fraction(u_ans) is not None])
            parsed_correct_nums = sorted([parse_number_string_to_fraction(c_ans) for c_ans in correct_answers_set if parse_number_string_to_fraction(c_ans) is not None])
            
            # Check if all numbers were successfully parsed and if the sets of parsed numbers match
            if len(parsed_user_nums) == len(user_answers_set) and \
               len(parsed_correct_nums) == len(correct_answers_set) and \
               len(parsed_user_nums) == len(parsed_correct_nums) and \
               all(u == c for u, c in zip(parsed_user_nums, parsed_correct_nums)):
                is_correct = True
        except Exception:
            # If any parsing or comparison error occurs, assume non-numeric or invalid input
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}