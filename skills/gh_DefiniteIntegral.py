import random
from fractions import Fraction

# Helper to format numbers for display in LaTeX
def format_number_for_display(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Use double backslashes for LaTeX commands inside normal strings or f-strings
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    elif isinstance(num, float) and num.is_integer():
        return str(int(num))
    else:
        return str(num)

# Helper to format numbers for the actual answer string (e.g., "1/2" not "\\frac{1}{2}")
def format_number_for_answer(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        return f"{num.numerator}/{num.denominator}"
    elif isinstance(num, float) and num.is_integer():
        return str(int(num))
    else:
        return str(num)

def generate_additivity_problem():
    """
    生成關於定積分區間可加性 (additivity of intervals) 的題目。
    例如：已知 int_a^b f(x) dx = K, int_b^c f(x) dx = M，求 int_a^c f(x) dx。
    """
    a, b, c = sorted(random.sample(range(-5, 6), 3))
    val_ab = random.randint(-20, 20)
    val_bc = random.randint(-20, 20)
    val_ac = val_ab + val_bc

    question_text = (
        f"已知連續函數 $f(x)$ 滿足 $\\int_{{{a}}}^{{{b}}} f(x) \\, dx = {val_ab}$ 且 $\\int_{{{b}}}^{{{c}}} f(x) \\, dx = {val_bc}$。"
        f"請問 $\\int_{{{a}}}^{{{c}}} f(x) \\, dx$ 的值為何？"
    )
    correct_answer = str(val_ac)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_limit_problem():
    """
    生成關於定積分上下限交換 (reverse limits) 的題目。
    例如：已知 int_a^b f(x) dx = K，求 int_b^a f(x) dx。
    """
    a, b = sorted(random.sample(range(-5, 6), 2))
    while a == b: # Ensure a != b for a meaningful interval
        b = random.randint(-5, 6)
    val_ab = random.randint(-20, 20)
    val_ba = -val_ab

    question_text = (
        f"已知連續函數 $f(x)$ 滿足 $\\int_{{{a}}}^{{{b}}} f(x) \\, dx = {val_ab}$。"
        f"請問 $\\int_{{{b}}}^{{{a}}} f(x) \\, dx$ 的值為何？"
    )
    correct_answer = str(val_ba)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linearity_problem():
    """
    生成關於定積分線性性質 (linearity) 的題目。
    例如：已知 int_a^b f(x) dx = K, int_a^b g(x) dx = M，求 int_a^b (c f(x) + d g(x)) dx。
    """
    a, b = sorted(random.sample(range(-5, 6), 2))
    while a == b: # Ensure a != b for non-zero interval
        b = random.randint(-5, 6)

    val_f = random.randint(-15, 15)
    val_g = random.randint(-15, 15)
    c_factor = random.randint(-3, 3)
    d_factor = random.randint(-3, 3)
    
    # Avoid trivial cases where both factors are zero, which would make the integrand 0
    while c_factor == 0 and d_factor == 0:
        c_factor = random.randint(-3, 3)
        d_factor = random.randint(-3, 3)

    integrand_parts = []
    if c_factor != 0:
        if c_factor == 1: integrand_parts.append("f(x)")
        elif c_factor == -1: integrand_parts.append("-f(x)")
        else: integrand_parts.append(f"{c_factor}f(x)")
    
    if d_factor != 0:
        if d_factor == 1:
            integrand_parts.append("g(x)")
        elif d_factor == -1:
            integrand_parts.append("-g(x)")
        else:
            integrand_parts.append(f"{d_factor}g(x)")
    
    # Combine with appropriate '+' sign if needed
    integrand_display = ""
    for i, part in enumerate(integrand_parts):
        if i > 0 and not part.startswith('-'): # If not the first term and not negative, add '+'
            integrand_display += "+"
        integrand_display += part
            
    correct_value = c_factor * val_f + d_factor * val_g

    question_text = (
        f"已知連續函數 $f(x)$ 和 $g(x)$ 滿足 $\\int_{{{a}}}^{{{b}}} f(x) \\, dx = {val_f}$ 且 $\\int_{{{a}}}^{{{b}}} g(x) \\, dx = {val_g}$。"
        f"請問 $\\int_{{{a}}}^{{{b}}} ({integrand_display}) \\, dx$ 的值為何？"
    )
    correct_answer = str(correct_value)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_constant_integral_problem():
    """
    生成求常數函數定積分的題目。
    例如：求 int_a^b C dx。
    """
    a, b = sorted(random.sample(range(-5, 6), 2))
    while a == b: # Ensure a != b
        b = random.randint(-5, 6)
    
    C = random.randint(-10, 10)
    
    correct_value = C * (b - a)
    
    question_text = (
        f"請問定積分 $\\int_{{{a}}}^{{{b}}} {C} \\, dx$ 的值為何？"
    )
    correct_answer = str(correct_value)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linear_integral_problem():
    """
    生成求線性函數 (mx+c) 定積分的題目，其值可透過幾何或基本定理計算。
    強調定積分可以為正、負、零。
    """
    a, b = sorted(random.sample(range(-3, 4), 2)) # Keep range small for simpler numbers
    while a == b: # Ensure a != b
        b = random.randint(-3, 4)

    m = random.randint(-2, 2)
    c = random.randint(-5, 5)

    # Integral of mx+c is (m/2)x^2 + cx evaluated from a to b
    val_at_b = Fraction(m, 2) * b**2 + c * b
    val_at_a = Fraction(m, 2) * a**2 + c * a
    
    correct_value = val_at_b - val_at_a
    
    # Format the integrand expression
    func_str = ""
    if m == 0: # It's a constant function C
        func_str = format_number_for_display(c)
    else: # It's a linear function mx+c
        if m == 1:
            func_str_m_part = "x"
        elif m == -1:
            func_str_m_part = "-x"
        else:
            func_str_m_part = f"{format_number_for_display(m)}x"

        c_str_display = ""
        if c > 0:
            c_str_display = f"+{format_number_for_display(c)}"
        elif c < 0:
            c_str_display = format_number_for_display(c) # Negative sign already included
        
        func_str = f"{func_str_m_part}{c_str_display}"
    
    question_text = (
        f"請問定積分 $\\int_{{{a}}}^{{{b}}} ({func_str}) \\, dx$ 的值為何？"
    )
    correct_answer = format_number_for_answer(correct_value)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conceptual_signed_area_problem():
    """
    生成關於定積分作為有向面積的觀念題。
    例如：若函數在某區間上方/下方，或上方/下方面積總和大小關係，判斷積分值的正負或零。
    """
    scenario_type = random.choice(['positive_above', 'negative_below', 'mixed_above_greater', 'mixed_below_greater', 'mixed_equal'])
    
    a, b = sorted(random.sample(range(-5, 6), 2))
    while a == b:
        b = random.randint(-5, 6)

    # Use a, b in the question text to make it concrete, but they don't affect the conceptual answer.
    a_display = format_number_for_display(a)
    b_display = format_number_for_display(b)

    if scenario_type == 'positive_above':
        question_text = (
            f"若連續函數 $f(x)$ 在區間 $[{a_display}, {b_display}]$ 上恆在 $x$ 軸上方，請問 $\\int_{{{a_display}}}^{{{b_display}}} f(x) \\, dx$ 的值會是正數、負數還是零？"
        )
        correct_answer = "正數"
    elif scenario_type == 'negative_below':
        question_text = (
            f"若連續函數 $f(x)$ 在區間 $[{a_display}, {b_display}]$ 上恆在 $x$ 軸下方，請問 $\\int_{{{a_display}}}^{{{b_display}}} f(x) \\, dx$ 的值會是正數、負數還是零？"
        )
        correct_answer = "負數"
    elif scenario_type == 'mixed_above_greater':
        question_text = (
            f"若連續函數 $f(x)$ 在區間 $[{a_display}, {b_display}]$ 上有部分在 $x$ 軸上方，有部分在 $x$ 軸下方，"
            f"且上方區域的面積總和大於下方區域的面積總和，請問 $\\int_{{{a_display}}}^{{{b_display}}} f(x) \\, dx$ 的值會是正數、負數還是零？"
        )
        correct_answer = "正數"
    elif scenario_type == 'mixed_below_greater':
        question_text = (
            f"若連續函數 $f(x)$ 在區間 $[{a_display}, {b_display}]$ 上有部分在 $x$ 軸上方，有部分在 $x$ 軸下方，"
            f"且下方區域的面積總和大於上方區域的面積總和，請問 $\\int_{{{a_display}}}^{{{b_display}}} f(x) \\, dx$ 的值會是正數、負數還是零？"
        )
        correct_answer = "負數"
    else: # mixed_equal
        question_text = (
            f"若連續函數 $f(x)$ 在區間 $[{a_display}, {b_display}]$ 上有部分在 $x$ 軸上方，有部分在 $x$ 軸下方，"
            f"且上方區域的面積總和等於下方區域的面積總和，請問 $\\int_{{{a_display}}}^{{{b_display}}} f(x) \\, dx$ 的值會是正數、負數還是零？"
        )
        correct_answer = "零"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成定積分相關題目。
    """
    problem_types = [
        'additivity',
        'reverse_limit',
        'linearity',
        'constant_integral',
        'linear_integral',
        'conceptual_signed_area'
    ]
    
    problem_type = random.choice(problem_types)
    
    if problem_type == 'additivity':
        return generate_additivity_problem()
    elif problem_type == 'reverse_limit':
        return generate_reverse_limit_problem()
    elif problem_type == 'linearity':
        return generate_linearity_problem()
    elif problem_type == 'constant_integral':
        return generate_constant_integral_problem()
    elif problem_type == 'linear_integral':
        return generate_linear_integral_problem()
    elif problem_type == 'conceptual_signed_area':
        return generate_conceptual_signed_area_problem()
    

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    # Try to compare as numbers (float/fraction) first, then as strings for conceptual answers
    try:
        user_num = Fraction(user_answer)
        correct_num = Fraction(correct_answer)
        if user_num == correct_num:
            is_correct = True
    except ValueError:
        # If not a number, compare as strings (case-insensitive for "正數", "負數", "零")
        if user_answer.lower() == correct_answer.lower():
            is_correct = True
            
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        # For numerical answers, display the correct answer in LaTeX format for feedback
        try:
            correct_fraction = Fraction(correct_answer)
            formatted_correct_answer = format_number_for_display(correct_fraction)
            result_text = f"答案不正確。正確答案應為：${formatted_correct_answer}$"
        except ValueError: # If conceptual answer, display as is
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}