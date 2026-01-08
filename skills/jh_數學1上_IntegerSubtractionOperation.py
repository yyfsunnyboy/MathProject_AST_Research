# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 27.31s | RAG: 2 examples
# Created At: 2026-01-08 22:57:33
# Fix Status: [Clean Pass]
# ==============================================================================


import random
import math
from fractions import Fraction

def to_latex(num):
    """Convert number to LaTeX (integers, decimals, fractions, mixed numbers)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            if rem == 0: return f"{sign}{abs(num).numerator // abs(num).denominator}"
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses"""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

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




# --- Helper Functions for Problem Generation ---

def generate_type_1_problem():
    """
    Generates an integer subtraction problem based on Type 1 specification.
    Concept: Integer subtraction involving various combinations of positive and negative integers,
             often resulting in negative or large magnitude positive/negative answers.
             Uses larger number ranges.
    """
    problem_type_choice = random.choice([0, 1, 2, 3])
    expression_str = ""
    ans = 0

    if problem_type_choice == 0: # Positive - Larger Positive (e.g., 14 - 23)
        num1 = random.randint(10, 50)
        num2 = random.randint(num1 + 5, num1 + 50) # Ensures num2 > num1
        expression_str = f"{num1}-{num2}"
        ans = num1 - num2
    elif problem_type_choice == 1: # Positive - Negative (e.g., 125 - (-25))
        num1 = random.randint(50, 150)
        num2 = random.randint(10, 50) # This num2 is the absolute value of the negative number
        expression_str = f"{num1}-(-{num2})"
        ans = num1 - (-num2) # Equivalent to num1 + num2
    elif problem_type_choice == 2: # Negative - Positive (e.g., (-63) - 37)
        num1 = random.randint(50, 150) # This num1 is the absolute value of the first negative number
        num2 = random.randint(10, 50)
        expression_str = f"(-{num1})-{num2}"
        ans = (-num1) - num2 # Equivalent to -(num1 + num2)
    elif problem_type_choice == 3: # Negative - Negative, result negative (e.g., (-133) - (-13))
        num1 = random.randint(100, 200) # Absolute value of the first negative number
        num2 = random.randint(10, num1 - 10) # Absolute value of the second negative number, ensuring num1 > num2
        expression_str = f"(-{num1})-(-{num2})"
        ans = (-num1) - (-num2) # Equivalent to -num1 + num2. Since num1 > num2, the result will be negative.
    
    # Wrap mathematical expression in $ for LaTeX formatting as per gold standard and general LaTeX practice.
    question_text = f"計算下列各式的值。 ${expression_str}$"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Generates an integer subtraction problem based on Type 2 specification.
    Concept: Integer subtraction with generally smaller magnitudes, specifically designed
             to include cases where subtracting a larger negative number results in a positive value.
    """
    problem_type_choice = random.choice([0, 1, 2, 3])
    expression_str = ""
    ans = 0

    if problem_type_choice == 0: # Positive - Larger Positive (e.g., 6 - 32)
        num1 = random.randint(5, 30)
        num2 = random.randint(num1 + 2, num1 + 20) # Ensures num2 > num1
        expression_str = f"{num1}-{num2}"
        ans = num1 - num2
    elif problem_type_choice == 1: # Positive - Negative (e.g., 12 - (-27))
        num1 = random.randint(10, 40)
        num2 = random.randint(5, 20)
        expression_str = f"{num1}-(-{num2})"
        ans = num1 - (-num2) # Equivalent to num1 + num2
    elif problem_type_choice == 2: # Negative - Positive (e.g., (-33) - 18)
        num1 = random.randint(10, 40) # Absolute value of the first negative number
        num2 = random.randint(5, 20)
        expression_str = f"(-{num1})-{num2}"
        ans = (-num1) - num2 # Equivalent to -(num1 + num2)
    elif problem_type_choice == 3: # Negative - Negative, result positive (e.g., (-18) - (-27))
        num1 = random.randint(5, 20) # Absolute value of the first negative number
        num2 = random.randint(num1 + 5, num1 + 20) # Absolute value of the second negative number, ensuring num2 > num1
        expression_str = f"(-{num1})-(-{num2})"
        ans = (-num1) - (-num2) # Equivalent to -num1 + num2. Since num2 > num1, the result will be positive.
            
    # Wrap mathematical expression in $ for LaTeX formatting
    question_text = f"計算下列各式的值。 ${expression_str}$"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Dispatcher ---

def generate(level=1):
    """
    Generates an integer subtraction problem based on the specified level.

    Args:
        level (int): The difficulty level.
                     - level 1: Calls generate_type_1_problem.
                     - level 2: Calls generate_type_2_problem.
                     - Default/Other: Randomly selects between type 1 and type 2.

    Returns:
        dict: A dictionary containing the question text, answer, and correct_answer.
    """
    if level == 1:
        return generate_type_1_problem()
    elif level == 2:
        return generate_type_2_problem()
    else: # Default or invalid level, randomly pick
        problem_generator = random.choice([generate_type_1_problem, generate_type_2_problem])
        return problem_generator()

# --- Check Function (Mimicking Gold Standard) ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Attempt numeric comparison for robustness, especially for floats vs integers.
            # While this problem is integer-only, the gold standard includes this.
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # If conversion fails, it's not a numeric match, so keep is_correct as False

    # Return result with LaTeX formatting for the correct answer.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
