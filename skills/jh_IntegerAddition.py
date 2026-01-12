import random
from fractions import Fraction

# Helper function to format numbers for LaTeX expression strings
def _format_number_for_question(n):
    """
    Formats an integer for display in a LaTeX math expression.
    Negative numbers are enclosed in parentheses.
    """
    if n < 0:
        # Double curly braces {{}} are used to escape literal braces for f-strings
        # so LaTeX can render them correctly as parentheses.
        return f"({{n}})"
    else:
        return str(n)

def _generate_same_sign_num_line_problem():
    """
    生成同號數加法 (數線情境) 題目。
    例如: (-2) + (-5) 或 3 + 4 (例子多為負數)。
    """
    sign = random.choice([-1, 1]) # Determines if both numbers are positive or negative
    val1_abs = random.randint(1, 10) # Absolute value of first number
    val2_abs = random.randint(1, 10) # Absolute value of second number
    
    val1 = sign * val1_abs
    val2 = sign * val2_abs
    
    num1_str = _format_number_for_question(val1)
    num2_str = _format_number_for_question(val2)
    
    question_text = f"利用數線求 ${num1_str} + {num2_str}$ 的值。"
    correct_answer = str(val1 + val2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_same_sign_direct_problem():
    """
    生成同號數加法 (直接計算) 題目。
    例如: (-9) + (-7) 或 13 + 28。
    """
    sign = random.choice([-1, 1])
    val1_abs = random.randint(5, 50)
    val2_abs = random.randint(5, 50)
    
    val1 = sign * val1_abs
    val2 = sign * val2_abs
    
    num1_str = _format_number_for_question(val1)
    num2_str = _format_number_for_question(val2)
    
    question_text = f"計算 ${num1_str} + {num2_str}$ 的值。"
    correct_answer = str(val1 + val2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_diff_sign_num_line_problem():
    """
    生成異號數加法 (數線情境) 題目。
    例如: 2 + (-6)。
    """
    val1_abs = random.randint(1, 10)
    val2_abs = random.randint(1, 10)
    
    # Ensure different signs for the two numbers
    val1_sign = random.choice([-1, 1])
    val2_sign = -val1_sign
    
    val1 = val1_abs * val1_sign
    val2 = val2_abs * val2_sign
    
    num1_str = _format_number_for_question(val1)
    num2_str = _format_number_for_question(val2)
    
    question_text = f"利用數線求 ${num1_str} + {num2_str}$ 的值。"
    correct_answer = str(val1 + val2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_diff_sign_direct_problem():
    """
    生成異號數加法 (直接計算) 題目。
    例如: 13 + (-4) 或 (-15) + 9。
    """
    val1_abs = random.randint(5, 100)
    val2_abs = random.randint(5, 100)
    
    # Ensure different signs for the two numbers
    val1_sign = random.choice([-1, 1])
    val2_sign = -val1_sign
    
    val1 = val1_abs * val1_sign
    val2 = val2_abs * val2_sign
    
    num1_str = _format_number_for_question(val1)
    num2_str = _format_number_for_question(val2)
    
    question_text = f"計算 ${num1_str} + {num2_str}$ 的值。"
    correct_answer = str(val1 + val2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_multi_term_addition_problem():
    """
    生成多項整數加法題目，應用交換律與結合律。
    例如: (-23) + 1205 + (-77)。
    """
    num_terms = random.randint(3, 5) # 3 to 5 terms
    terms = []
    for _ in range(num_terms):
        term = random.randint(-150, 150)
        # Ensure not too many zeros if it makes the problem trivial
        while term == 0 and num_terms > 1 and len(terms) < num_terms - 1:
            term = random.randint(-150, 150)
        terms.append(term)
    
    # Format terms for the question string
    terms_str = []
    for i, term in enumerate(terms):
        if i == 0 and term >= 0: # First positive term often doesn't need parentheses
            terms_str.append(str(term))
        else:
            terms_str.append(_format_number_for_question(term))
            
    # Join the formatted terms with " + " for the LaTeX expression
    question_latex_expression = " + ".join(terms_str)
    
    question_text = f"計算 ${question_latex_expression}$ 的值。"
    correct_answer = str(sum(terms))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_zero_or_opposite_problem():
    """
    生成與零或相反數相加的特殊情形題目。
    例如: (-5) + 0 或 7 + (-7)。
    """
    problem_subtype = random.choice(['add_zero', 'add_opposite'])
    val = random.randint(-100, 100)
    
    if problem_subtype == 'add_zero':
        num_str = _format_number_for_question(val)
        question_text = f"計算 ${num_str} + 0$ 的值。"
        correct_answer = str(val)
    else: # add_opposite
        num_str = _format_number_for_question(val)
        opposite_str = _format_number_for_question(-val)
        question_text = f"計算 ${num_str} + {opposite_str}$ 的值。"
        correct_answer = str(0) # A + (-A) = 0
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「整數加法」相關題目。
    根據情境和運算規則，隨機選擇不同類型的加法問題。
    """
    
    # List of problem generator functions
    problem_generators = [
        _generate_same_sign_num_line_problem,
        _generate_same_sign_direct_problem,
        _generate_diff_sign_num_line_problem,
        _generate_diff_sign_direct_problem,
        _generate_multi_term_addition_problem,
        _generate_zero_or_opposite_problem
    ]
    
    # Randomly select a problem generator
    selected_generator = random.choice(problem_generators)
    return selected_generator()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    # First, try direct string comparison
    if user_answer == correct_answer:
        is_correct = True
    else:
        # If strings don't match, try numeric comparison
        try:
            # Convert to float for robust numeric comparison (e.g., "5.0" == "5")
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            # User's answer is not a valid number
            pass 
        
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}