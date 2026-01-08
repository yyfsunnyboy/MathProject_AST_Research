# ==============================================================================
# ID: jh_數學1上_IntegerDivision
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 30.70s | RAG: 2 examples
# Created At: 2026-01-08 22:55:40
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




def _format_latex_number(num):
    """
    Formats an integer for LaTeX display, wrapping negative numbers in \\left( \\right).
    """
    if num < 0:
        return f"\\left( {num} \\right)"
    return str(num)

def generate_type_1_problem():
    """
    Generates an integer division problem (Type 1) based on Architect's Spec.
    - Concept: Integer division with two-digit dividends and small single/two-digit divisors.
    - Focus: Rules of signs for integers.
    """
    # 1. Generate divisor_abs
    divisor_abs = random.randint(2, 12)
    
    # 2. Initialize retry_count
    retry_count = 0
    dividend_abs = 0 # Initialize to ensure it's defined outside the loop
    
    # 3. Loop while retry_count < 100
    while retry_count < 100:
        # a. Generate quotient_abs
        quotient_abs = random.randint(2, 10)
        # b. Calculate dividend_abs
        dividend_abs = divisor_abs * quotient_abs
        # c. If 10 <= dividend_abs <= 100, break the loop
        if 10 <= dividend_abs <= 100:
            break
        # d. Increment retry_count
        retry_count += 1
    
    # 4. (Safety) If retry_count == 100 after the loop, handle as an error or fallback.
    # The Coder should assume successful generation within 100 retries.
    # In a production system, a more robust fallback might be needed.
    if retry_count == 100:
        # Fallback to ensure valid numbers, though spec assumes success.
        dividend_abs = 63 # Example fallback: 63 = 7 * 9
        divisor_abs = 7
        # quotient_abs implicitly 9

    # 5. Generate sign1 and sign2
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    
    # 6. Calculate num1
    num1 = sign1 * dividend_abs
    # 7. Calculate num2
    num2 = sign2 * divisor_abs
    
    # 8. Calculate ans
    ans = num1 // num2
    
    # 9. Prepare num1_str for LaTeX
    num1_str = _format_latex_number(num1)
    # 10. Prepare num2_str for LaTeX
    num2_str = _format_latex_number(num2)
    
    # Question Template
    question_text = f"計算下列各式的值。\n ${num1_str} \\div {num2_str}$"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Generates an integer division problem (Type 2) based on Architect's Spec.
    - Concept: Integer division with three-digit dividends and small two-digit divisors.
    - Focus: Rules of signs for integers with larger magnitudes.
    """
    # 1. Generate divisor_abs
    divisor_abs = random.randint(4, 20)
    
    # 2. Initialize retry_count
    retry_count = 0
    dividend_abs = 0 # Initialize to ensure it's defined outside the loop
    
    # 3. Loop while retry_count < 100
    while retry_count < 100:
        # a. Generate quotient_abs
        quotient_abs = random.randint(5, 20)
        # b. Calculate dividend_abs
        dividend_abs = divisor_abs * quotient_abs
        # c. If 100 <= dividend_abs <= 300, break the loop
        if 100 <= dividend_abs <= 300:
            break
        # d. Increment retry_count
        retry_count += 1
            
    # 4. (Safety) If retry_count == 100 after the loop, handle as an error or fallback.
    # The Coder should assume successful generation within 100 retries.
    if retry_count == 100:
        # Fallback to ensure valid numbers, though spec assumes success.
        dividend_abs = 200 # Example fallback: 200 = 10 * 20
        divisor_abs = 10
        # quotient_abs implicitly 20

    # 5. Generate sign1 and sign2
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    
    # 6. Calculate num1
    num1 = sign1 * dividend_abs
    # 7. Calculate num2
    num2 = sign2 * divisor_abs
    
    # 8. Calculate ans
    ans = num1 // num2
    
    # 9. Prepare num1_str for LaTeX
    num1_str = _format_latex_number(num1)
    # 10. Prepare num2_str for LaTeX
    num2_str = _format_latex_number(num2)
    
    # Question Template
    question_text = f"計算下列各式的值。\n ${num1_str} \\div {num2_str}$"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Main dispatcher for the 'jh_數學1上_IntegerDivision' skill.
    Randomly selects and generates an integer division problem of Type 1 or Type 2.
    """
    problem_type_functions = [generate_type_1_problem, generate_type_2_problem]
    selected_function = random.choice(problem_type_functions)
    return selected_function()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for integer division problems.
    Handles string comparison and attempts float comparison for numerical answers.
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Attempt float comparison for numerical answers that might have leading zeros
            # or other non-exact string differences but are numerically equivalent.
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # If conversion to float fails, it's not a numerical match.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
