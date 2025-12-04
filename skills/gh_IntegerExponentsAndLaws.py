import random
from fractions import Fraction

# Helper to format fractions nicely for LaTeX output
def format_fraction(frac):
    """
    Formats a Fraction object into a LaTeX string.
    If the denominator is 1, it returns the integer as a string.
    """
    if frac.denominator == 1:
        return str(frac.numerator)
    # Use double braces for numerator and denominator in \\frac to satisfy f-string LaTeX rule
    return fr"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

def generate_zero_exponent_problem(level):
    """
    Generates a problem involving the zero exponent (A^0 = 1).
    The base can be an integer, a fraction, or a simple sum/difference of integers.
    """
    base_type = random.choice(['integer', 'fraction', 'expression'])
    
    base_str = ""
    base_val = 0 # To check if base itself is zero
    
    if base_type == 'integer':
        base_val = random.randint(-10, 10)
        while base_val == 0: # Avoid 0^0 which is indeterminate
            base_val = random.randint(-10, 10)
        base_str = str(base_val)
    elif base_type == 'fraction':
        numerator = random.randint(1, 10)
        denominator = random.randint(2, 10)
        base_val = Fraction(numerator, denominator)
        base_str = format_fraction(base_val)
    else: # expression type, like (3 + 5)^0 or (7 - 2)^0
        term1 = random.randint(1, 10)
        term2 = random.randint(1, 10)
        op = random.choice(['+', '-'])
        # Evaluate the expression to ensure the base is not zero
        base_val = eval(f"{term1}{op}{term2}") 
        while base_val == 0:
            term1 = random.randint(1, 10)
            term2 = random.randint(1, 10)
            op = random.choice(['+', '-'])
            base_val = eval(f"{term1}{op}{term2}")
        
        base_str = fr"({term1} {op} {term2})"

    question_text = fr"求下列各式的值：${base_str}^{{0}}$"
    correct_answer = "1" # Any non-zero number to the power of 0 is 1

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_negative_exponent_problem(level):
    """
    Generates a problem involving a negative integer exponent (A^-n = 1/A^n).
    The base can be an integer or a fraction.
    """
    base_type = random.choice(['integer', 'fraction'])
    
    base_val = 0
    base_str = ""

    if base_type == 'integer':
        base_val = random.randint(2, 10) # Avoid 0, 1, -1 for more meaningful problems
        if random.random() < 0.3: # Occasionally make base negative
            base_val *= -1
        base_str = str(base_val)
    else: # fraction
        numerator = random.randint(1, 5)
        denominator = random.randint(2, 5)
        base_val = Fraction(numerator, denominator)
        base_str = format_fraction(base_val)

    exponent = random.randint(-4, -1) # Always a negative integer

    question_text = fr"求下列各式的值：${base_str}^{{{exponent}}}$"
    
    # Calculate correct answer using Fraction for precision
    calculated_value = base_val**exponent
    correct_answer = format_fraction(calculated_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_law_product_power_problem(level):
    """
    Generates a problem applying the product rule of exponents:
    A^m * A^n = A^(m+n) (same base)
    or (A*B)^n = A^n * B^n (same exponent)
    """
    sub_type = random.choice(['same_base', 'same_exponent'])

    if sub_type == 'same_base':
        base = random.randint(2, 5)
        exp1 = random.randint(-3, 3)
        exp2 = random.randint(-3, 3)
        # Ensure exponents are not both zero or too trivial
        while (exp1 == 0 and exp2 == 0) or (exp1 == 1 and exp2 == 0) or (exp1 == 0 and exp2 == 1):
            exp1 = random.randint(-3, 3)
            exp2 = random.randint(-3, 3)
        
        question_text = fr"利用指數律求下列各式的值：${base}^{{{exp1}}} \\times {base}^{{{exp2}}}$"
        correct_value = Fraction(base)**(exp1 + exp2)

    else: # same_exponent
        base1 = random.randint(2, 5)
        base2 = random.randint(2, 5)
        while base1 == base2: # Ensure bases are different
            base2 = random.randint(2, 5)
        
        exponent = random.randint(-3, -1) # Often negative for a challenge
        if level > 2 and random.random() < 0.5: # Allow positive exponents at higher levels
            exponent = random.randint(2, 4)

        question_text = fr"利用指數律求下列各式的值：${base1}^{{{exponent}}} \\times {base2}^{{{exponent}}}$"
        correct_value = Fraction(base1 * base2)**exponent
    
    correct_answer = format_fraction(correct_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_law_power_of_power_problem(level):
    """
    Generates a problem applying the power of a power rule: (A^m)^n = A^(mn).
    """
    base = random.randint(2, 5)
    exp1 = random.randint(-2, 2)
    exp2 = random.randint(-2, 2)
    
    # Avoid trivial cases like (A^1)^1 or (A^0)^n or (A^n)^0 resulting in 1
    while (exp1 == 1 and exp2 == 1) or exp1 == 0 or exp2 == 0:
        exp1 = random.randint(-2, 2)
        exp2 = random.randint(-2, 2)

    question_text = fr"利用指數律求下列各式的值：$({base}^{{{exp1}}})^{{{exp2}}}$"
    correct_value = Fraction(base)**(exp1 * exp2)
    correct_answer = format_fraction(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_law_division_problem(level):
    """
    Generates a problem applying the division rule of exponents: A^m / A^n = A^(m-n).
    """
    base = random.randint(2, 5)
    exp1 = random.randint(-3, 3)
    exp2 = random.randint(-3, 3)
    
    # Ensure exponents are different to avoid A^n / A^n = A^0 = 1 too often, and non-trivial operations
    while exp1 == exp2:
        exp2 = random.randint(-3, 3)

    question_text = fr"利用指數律求下列各式的值：$\\frac{{{base}^{{{exp1}}}}}{{{base}^{{{exp2}}}}}$"
    correct_value = Fraction(base)**(exp1 - exp2)
    correct_answer = format_fraction(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simple_combined_problem(level):
    """
    Generates a problem combining two or more basic exponent laws.
    E.g., (A*B)^n, then apply negative exponent definition.
    E.g., (A^m)^n * A^p.
    """
    op_type = random.choice(['product_to_power_then_evaluate', 'power_of_power_and_multiply', 'division_of_product_powers'])

    if op_type == 'product_to_power_then_evaluate': # e.g. $(2 \\times 3)^{-2}$
        base1 = random.randint(2, 4)
        base2 = random.randint(2, 4)
        while base1 == base2:
            base2 = random.randint(2, 4)
        exponent = random.randint(-2, -1) # Negative exponent for fraction result
        question_text = fr"利用指數律求下列各式的值：$({base1} \\times {base2})^{{{exponent}}}$"
        correct_value = Fraction(base1 * base2)**exponent

    elif op_type == 'power_of_power_and_multiply': # e.g. $(2^{-2})^3 \\times 2^4$
        base = random.randint(2, 3)
        exp1_inner = random.randint(-2, 2)
        exp1_outer = random.randint(-2, 2)
        exp2 = random.randint(-3, 3)
        # Ensure the overall exponent is not 0 or 1 for more varied results
        while (exp1_inner * exp1_outer) + exp2 in [0, 1]:
            exp1_inner = random.randint(-2, 2)
            exp1_outer = random.randint(-2, 2)
            exp2 = random.randint(-3, 3)

        question_text = fr"利用指數律求下列各式的值：$({base}^{{{exp1_inner}}})^{{{exp1_outer}}} \\times {base}^{{{exp2}}}$"
        correct_value = Fraction(base)**((exp1_inner * exp1_outer) + exp2)
    
    else: # division_of_product_powers: e.g. $(2^{-3} \\times 3^{-3}) / 6^{-1}$
        base1 = random.randint(2, 4)
        base2 = random.randint(2, 4)
        while base1 == base2:
            base2 = random.randint(2, 4)
        exp_prod = random.randint(-2, -1)
        
        common_base_for_division = base1 * base2
        exp_div = random.randint(-2, -1)
        # Avoid trivial division resulting in 1
        while exp_prod == exp_div:
             exp_div = random.randint(-2, -1)

        question_text = fr"利用指數律求下列各式的值：$\\frac{{{base1}^{{{exp_prod}}} \\times {base2}^{{{exp_prod}}}}}{{{common_base_for_division}^{{{exp_div}}}}}$"
        correct_value = Fraction(common_base_for_division)**(exp_prod - exp_div)

    correct_answer = format_fraction(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem(level):
    """
    Generates a word problem applying integer exponents, similar to the illumination example.
    """
    coeff = random.choice([100, 200, 300, 400, 500]) # Coefficient for the formula
    
    # Generate a 'd' value that results in a manageable calculation
    d_num = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
    d_den = random.choice([2, 4, 5, 8, 10])
    
    d_val = Fraction(d_num, d_den)
    # Ensure d_val is within a reasonable range (e.g., 0.1 to 1.5 meters)
    while not (0.1 <= float(d_val) <= 1.5):
        d_num = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
        d_den = random.choice([2, 4, 5, 8, 10])
        d_val = Fraction(d_num, d_den)

    d_str = format_fraction(d_val)
    # Sometimes present d as a decimal if it's a terminating decimal
    if random.random() < 0.5 and d_val.denominator in [2,4,5,10]:
        d_str = str(float(d_val))

    question_text = (
        fr"設某檯燈與被照明物的距離為 $d$ 公尺時，被照明物表面的照度為 $E$ 勒克斯，"
        fr"且 $E$ 與 $d$ 的關係式為 $E = {coeff}d^{{-2}}$。"
        fr"已知此檯燈高度為 ${d_str}$ 公尺，求放置於桌面上時，檯燈正下方的照度 $E$ 的值。"
    )
    
    correct_value = Fraction(coeff) * (d_val**-2)
    correct_answer = format_fraction(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「整數指數與指數律」相關題目。
    根據 `level` 參數調整題目難度。
    Level 1: 零指數與負整數指數的定義與基本運算。
    Level 2: 簡單指數律的應用（乘法、除法、次方）。
    Level 3: 綜合應用或文字問題，含較複雜的運算。
    """
    
    problem_funcs = []
    
    if level == 1:
        problem_funcs = [
            generate_zero_exponent_problem,
            generate_negative_exponent_problem
        ]
    elif level == 2:
        problem_funcs = [
            generate_zero_exponent_problem, 
            generate_negative_exponent_problem,
            generate_law_product_power_problem,
            generate_law_power_of_power_problem,
            generate_law_division_problem
        ]
    else: # level == 3 or any other value defaults to highest difficulty
        problem_funcs = [
            generate_negative_exponent_problem, 
            generate_law_product_power_problem,
            generate_law_power_of_power_problem,
            generate_law_division_problem,
            generate_simple_combined_problem,
            generate_word_problem
        ]
        
    chosen_problem_func = random.choice(problem_funcs)
    return chosen_problem_func(level)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    接受數字、小數或分數形式的答案，並進行精確比較。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    try:
        # Convert both user's answer and correct answer to Fraction for precise comparison.
        # This handles integers, terminating decimals, and fractions correctly.
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        
        if user_frac == correct_frac:
            is_correct = True
            feedback = fr"完全正確！答案是 ${format_fraction(correct_frac)}$。"
        else:
            feedback = fr"答案不正確。正確答案應為：${format_fraction(correct_frac)}$。"
    except ValueError:
        # If user_answer cannot be converted to a Fraction, it's not a valid number/fraction.
        feedback = fr"你的輸入 '{user_answer}' 不是一個有效的數字或分數。正確答案應為：${correct_answer}$。"
    except ZeroDivisionError:
        # This might happen if user types "1/0"
        feedback = fr"你的輸入導致了除以零的錯誤。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}