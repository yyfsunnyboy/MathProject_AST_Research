# ==============================================================================
# ID: jh_數學1上_IntegerMultiplication
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 34.61s | RAG: 5 examples
# Created At: 2026-01-08 22:57:06
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



def generate_type_1_problem():
    """
    Concept: Basic multiplication of two integers with mixed signs.
             One factor is small, the other is also small.
    """
    v1_abs = random.randint(2, 9)
    v2_abs = random.randint(2, 9)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])

    v1 = v1_abs * sign1
    v2 = v2_abs * sign2
    ans = v1 * v2

    question_text = f"計算下列各式的值。\n${v1} \\times {v2}$"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Concept: Basic multiplication of two integers with mixed signs.
             Numbers are slightly larger than Type 1, potentially resulting in larger products.
    """
    v1_abs = random.randint(5, 15)
    v2_abs = random.randint(2, 8)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])

    v1 = v1_abs * sign1
    v2 = v2_abs * sign2
    ans = v1 * v2

    question_text = f"計算下列各式的值。\n${v1} \\times {v2}$"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Concept: Multiplication of three integers with mixed signs.
             One factor is a larger number, while the others are small.
    """
    v1_abs = random.randint(2, 5)
    v2_abs = random.randint(10, 150)
    v3_abs = random.randint(2, 5)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])

    v1 = v1_abs * sign1
    v2 = v2_abs * sign2
    v3 = v3_abs * sign3
    ans = v1 * v2 * v3

    question_text = f"計算下列各式的值。\n${v1} \\times {v2} \\times {v3}$"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Concept: Multiplication of three integers where two factors are strategically chosen
             to simplify calculation (e.g., 25 * 4 = 100).
    """
    strategic_pairs = [(25, 4), (5, 2), (125, 8)]
    v_pair1_abs, v_pair2_abs = random.choice(strategic_pairs)

    v_other_abs = 0
    retry_count = 0
    # Ensure v_other_abs is distinct from the strategic pair
    while retry_count < 100:
        candidate_v_other_abs = random.randint(3, 20)
        if candidate_v_other_abs not in [v_pair1_abs, v_pair2_abs]:
            v_other_abs = candidate_v_other_abs
            break
        retry_count += 1
    # Fallback if distinct number is hard to find (highly unlikely given ranges)
    if v_other_abs == 0:
        v_other_abs = random.randint(3, 20)

    abs_values = [v_pair1_abs, v_pair2_abs, v_other_abs]
    random.shuffle(abs_values) # Randomize order for display

    signs = [random.choice([-1, 1]) for _ in range(3)]

    v1 = abs_values[0] * signs[0]
    v2 = abs_values[1] * signs[1]
    v3 = abs_values[2] * signs[2]
    ans = v1 * v2 * v3

    question_text = f"計算 ${v1} \\times {v2} \\times {v3}$ 的值。"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Concept: Determine the sign of a product of multiple integers without calculating the actual value,
             based on the count of negative factors.
    """
    num_factors = random.randint(5, 9)
    factor_abs_values = []
    
    # Generate distinct absolute values for factors
    for _ in range(num_factors):
        candidate_abs_value = 0
        retry_count = 0
        while retry_count < 100:
            candidate_abs_value = random.randint(10, 25)
            if candidate_abs_value not in factor_abs_values:
                break
            retry_count += 1
        factor_abs_values.append(candidate_abs_value)

    negative_count = 0
    factors_with_signs = []
    
    # Assign signs and count negative factors
    for abs_val in factor_abs_values:
        sign = random.choice([-1, 1])
        factor = abs_val * sign
        factors_with_signs.append(factor)
        if factor < 0:
            negative_count += 1

    # Format factors for LaTeX display
    factors_str = " \\times ".join(map(str, factors_with_signs))
    
    # Determine the overall sign and reason
    sign_result = "正數" if negative_count % 2 == 0 else "負數"
    parity_str = "偶數" if negative_count % 2 == 0 else "奇數"
    reason_str = f"因為式子中有 {negative_count} 個負數相乘，{parity_str}個負數相乘結果為{sign_result}。"

    question_text = f"判斷 ${factors_str}$ 的計算結果是一個正數還是負數？說明你判斷的理由。"
    correct_answer = f"{sign_result}\n{reason_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level: int = 1) -> dict:
    """
    Main dispatcher function to generate an integer multiplication problem.
    The 'level' parameter is currently not used to differentiate problem types.
    """
    problem_types = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
    ]
    
    selected_problem_func = random.choice(problem_types)
    return selected_problem_func()

def check(user_answer: str, correct_answer: str) -> dict:
    """
    檢查答案是否正確。
    Handles both numerical and multi-line string answers.
    """
    user_answer_processed = user_answer.strip().upper()
    correct_answer_processed = correct_answer.strip().upper()
    
    is_correct = (user_answer_processed == correct_answer_processed)
    
    # Attempt numerical comparison for single-line answers if direct string match fails
    if not is_correct and '\n' not in correct_answer_processed:
        try:
            if float(user_answer_processed) == float(correct_answer_processed):
                is_correct = True
        except ValueError:
            pass

    # [教學示範] 回傳結果中也可以包含 LaTeX
    # Note: For multi-line correct_answer, direct LaTeX embedding in $...$ might not render perfectly.
    # The current approach follows the provided gold standard's check function structure.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}

