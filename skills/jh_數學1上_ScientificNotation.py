# ==============================================================================
# ID: jh_數學1上_ScientificNotation
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 33.50s | RAG: 7 examples
# Created At: 2026-01-08 23:02:34
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


#  # Not needed for this skill

def generate_type_1_problem():
    """
    Concept: Convert a large integer, a small decimal, and a fraction (with a power of 10 denominator) into scientific notation.
    """
    # Part 1 (Large Integer)
    int_val_a = random.randint(1, 9)
    int_val_b = random.randint(0, 9)
    num_zeros1 = random.randint(6, 8)
    
    q1_num = str(int_val_a) + str(int_val_b) + '0' * num_zeros1
    ans_exp1 = num_zeros1 + 1
    ans1 = f"{int_val_a}.{int_val_b} \\times 10^{{{ans_exp1}}}"

    # Part 2 (Small Decimal)
    dec_val_a = random.randint(1, 9)
    dec_val_b = random.randint(0, 9)
    dec_val_c = random.randint(0, 9)
    num_zeros2 = random.randint(5, 7)
    
    q2_num = f"0.{'0' * num_zeros2}{dec_val_a}{dec_val_b}{dec_val_c}"
    ans_exp2 = -(num_zeros2 + 1)
    ans2 = f"{dec_val_a}.{dec_val_b}{dec_val_c} \\times 10^{{{ans_exp2}}}"

    # Part 3 (Fraction)
    frac_num = random.randint(1, 9)
    frac_den_exp = random.randint(5, 7)
    
    q3_num = f"\\frac{{{frac_num}}}{{10^{{{frac_den_exp}}}}}"
    ans_exp3 = -frac_den_exp
    ans3 = f"{frac_num} \\times 10^{{{ans_exp3}}}"
    
    question_text = f"以科學記號表示下列各數。\n⑴ {q1_num}\n⑵ {q2_num}\n⑶ ${q3_num}$"
    correct_answer = f"⑴ ${ans1}$ ⑵ ${ans2}$ ⑶ ${ans3}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Concept: Convert a large integer, a small decimal, and a fraction (with a power of 10 denominator) into scientific notation.
    (Similar to Type 1 but with slightly different numerical ranges to ensure distinct problem generation).
    """
    # Part 1 (Large Integer)
    int_val_a = random.randint(1, 9)
    int_val_b = random.randint(0, 9)
    num_zeros1 = random.randint(7, 9) # Range 7-9
    
    q1_num = str(int_val_a) + str(int_val_b) + '0' * num_zeros1
    ans_exp1 = num_zeros1 + 1
    ans1 = f"{int_val_a}.{int_val_b} \\times 10^{{{ans_exp1}}}"

    # Part 2 (Small Decimal)
    dec_val_a = random.randint(1, 9)
    dec_val_b = random.randint(0, 9)
    dec_val_c = random.randint(0, 9)
    num_zeros2 = random.randint(6, 8) # Range 6-8
    
    q2_num = f"0.{'0' * num_zeros2}{dec_val_a}{dec_val_b}{dec_val_c}"
    ans_exp2 = -(num_zeros2 + 1)
    ans2 = f"{dec_val_a}.{dec_val_b}{dec_val_c} \\times 10^{{{ans_exp2}}}"

    # Part 3 (Fraction)
    frac_num = random.randint(1, 9)
    frac_den_exp = random.randint(6, 8) # Range 6-8
    
    q3_num = f"\\frac{{{frac_num}}}{{10^{{{frac_den_exp}}}}}"
    ans_exp3 = -frac_den_exp
    ans3 = f"{frac_num} \\times 10^{{{ans_exp3}}}"
    
    question_text = f"以科學記號表示下列各數。\n⑴ {q1_num}\n⑵ {q2_num}\n⑶ ${q3_num}$"
    correct_answer = f"⑴ ${ans1}$ ⑵ ${ans2}$ ⑶ ${ans3}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Concept: Convert a small decimal number presented in a real-world context into scientific notation.
    """
    val_a = random.randint(1, 9)
    val_b = random.randint(0, 9)
    val_c = random.randint(0, 9)
    num_zeros_after_decimal = random.randint(6, 9)
    
    object_name = random.choice(["諾羅病毒", "細菌", "紅血球", "灰塵顆粒"])
    unit_name = random.choice(["奈米", "微米", "毫米"])
    
    decimal_str = f"0.{'0' * num_zeros_after_decimal}{val_a}{val_b}{val_c}"
    exp = -(num_zeros_after_decimal + 1)
    mantissa = f"{val_a}.{val_b}{val_c}"
    
    question_text = f"{object_name}的直徑大小約為 {val_a}{val_b}{val_c} {unit_name}，即 {decimal_str} 公尺。試將 {decimal_str} 以科學記號表示。"
    correct_answer = f"${mantissa} \\times 10^{{{exp}}}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Concept: For a number in scientific notation, determine its number of digits (for positive exponents)
    or the position of the first non-zero digit after the decimal point (for negative exponents).
    """
    # Part 1 (Positive Exponent)
    mantissa1_int = random.randint(1, 9)
    mantissa1_dec = random.randint(0, 9)
    exp1 = random.randint(6, 9)
    ans1 = exp1 + 1
    
    # Part 2 (Negative Exponent)
    mantissa2_int = random.randint(1, 9)
    mantissa2_dec = random.randint(0, 9)
    exp2 = random.randint(4, 6) # Absolute value
    ans2 = exp2
    
    question_text = (
        f"⑴ 若將 ${mantissa1_int}.{mantissa1_dec} \\times 10^{{{exp1}}}$ 乘開，則這個數是幾位數？\n"
        f"⑵ 若將 ${mantissa2_int}.{mantissa2_dec} \\times 10^{{{-exp2}}}$ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
    )
    correct_answer = f"⑴ {ans1} 位數 ⑵ 第 {ans2} 位"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Concept: For a number in scientific notation, determine its number of digits (for positive exponents)
    or the position of the first non-zero digit after the decimal point (for negative exponents).
    (Similar to Type 4 but with slightly different numerical ranges and mantissa precision).
    """
    # Part 1 (Positive Exponent)
    mantissa1_int = random.randint(1, 9)
    mantissa1_dec = random.randint(0, 9)
    exp1 = random.randint(5, 8)
    ans1 = exp1 + 1
    
    # Part 2 (Negative Exponent)
    mantissa2_int = random.randint(1, 9)
    mantissa2_dec1 = random.randint(0, 9)
    mantissa2_dec2 = random.randint(0, 9)
    exp2 = random.randint(5, 7) # Absolute value
    ans2 = exp2
    
    question_text = (
        f"1. 若將 ${mantissa1_int}.{mantissa1_dec} \\times 10^{{{exp1}}}$ 乘開，則這個數是幾位數？\n"
        f"2. 若將 ${mantissa2_int}.{mantissa2_dec1}{mantissa2_dec2} \\times 10^{{{-exp2}}}$ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
    )
    correct_answer = f"1. {ans1} 位數 2. 第 {ans2} 位"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_6_problem():
    """
    Concept: Compare two scientific notation numbers, focusing on cases where exponents are often distinct,
    using `與` to separate the numbers.
    """
    # Part 1 (Positive Exponents)
    retry_count = 0
    while retry_count < 100:
        m1_int = random.randint(1, 9)
        m1_dec = random.randint(0, 9)
        e1_val = random.randint(3, 6)
        mantissa1_str = f"{m1_int}.{m1_dec}"
        mantissa1 = float(mantissa1_str)

        m2_int = random.randint(1, 9)
        m2_dec = random.randint(0, 9)
        e2_val = random.randint(3, 6)
        mantissa2_str = f"{m2_int}.{m2_dec}"
        mantissa2 = float(mantissa2_str)
        
        # Ensure numbers are distinct enough for comparison, avoiding identical representations
        if abs(e1_val - e2_val) >= 1 or (e1_val == e2_val and mantissa1 != mantissa2):
            break
        retry_count += 1
    if retry_count == 100:
        raise RuntimeError("Failed to generate distinct numbers for Type 6 Part 1 after 100 retries.")

    num1_val = mantissa1 * (10**e1_val)
    num2_val = mantissa2 * (10**e2_val)
    ans_op1 = ">" if num1_val > num2_val else "<"

    # Part 2 (Negative Exponents)
    retry_count = 0
    while retry_count < 100:
        m3_int = random.randint(1, 9)
        m3_dec = random.randint(0, 9)
        e3_val = random.randint(4, 7)
        mantissa3_str = f"{m3_int}.{m3_dec}"
        mantissa3 = float(mantissa3_str)

        m4_int = random.randint(1, 9)
        m4_dec = random.randint(0, 9)
        e4_val = random.randint(4, 7)
        mantissa4_str = f"{m4_int}.{m4_dec}"
        mantissa4 = float(mantissa4_str)

        # Ensure numbers are distinct enough for comparison, avoiding identical representations
        if abs(e3_val - e4_val) >= 1 or (e3_val == e4_val and mantissa3 != mantissa4):
            break
        retry_count += 1
    if retry_count == 100:
        raise RuntimeError("Failed to generate distinct numbers for Type 6 Part 2 after 100 retries.")

    num3_val = mantissa3 * (10**(-e3_val))
    num4_val = mantissa4 * (10**(-e4_val))
    ans_op2 = ">" if num3_val > num4_val else "<"
    
    question_text = (
        f"比較下列各題中兩數的大小。\n"
        f"⑴ ${mantissa1_str} \\times 10^{{{e1_val}}}$ 與 ${mantissa2_str} \\times 10^{{{e2_val}}}$ \n"
        f"⑵ ${mantissa3_str} \\times 10^{{{-e3_val}}}$ 與 ${mantissa4_str} \\times 10^{{{-e4_val}}}$"
    )
    correct_answer = (
        f"⑴ ${mantissa1_str} \\times 10^{{{e1_val}}}$ {ans_op1} ${mantissa2_str} \\times 10^{{{e2_val}}}$ "
        f"⑵ ${mantissa3_str} \\times 10^{{{-e3_val}}}$ {ans_op2} ${mantissa4_str} \\times 10^{{{-e4_val}}}$"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_7_problem():
    """
    Concept: Compare two scientific notation numbers, allowing for same exponents and equality, using `__` as a placeholder.
    """
    # Part 1 (Positive Exponents)
    retry_count = 0
    while retry_count < 100:
        m1_int = random.randint(1, 9)
        m1_dec1 = random.randint(0, 9)
        m1_dec2 = random.randint(0, 9)
        e1_val = random.randint(4, 7)
        mantissa1_str = f"{m1_int}.{m1_dec1}{m1_dec2}"
        mantissa1 = float(mantissa1_str)

        m2_int = random.randint(1, 9)
        m2_dec1 = random.randint(0, 9)
        m2_dec2 = random.randint(0, 9)
        mantissa2_str = f"{m2_int}.{m2_dec1}{m2_dec2}"
        mantissa2 = float(mantissa2_str)
        
        # Randomly set e2_val relative to e1_val
        e2_val_offset = random.choice([-1, 0, 1])
        e2_val = e1_val + e2_val_offset
        # Ensure e2_val is within range [4, 7]
        e2_val = max(4, min(7, e2_val))

        # Ensure the *representation* is not identical unless specific logic allows for it.
        # The spec says: "If (mantissa1 != mantissa2 or e1_val != e2_val), break loop."
        # This means it will loop until they are NOT identically represented.
        if mantissa1 != mantissa2 or e1_val != e2_val:
            break
        retry_count += 1
    if retry_count == 100:
        raise RuntimeError("Failed to generate distinct numbers for Type 7 Part 1 after 100 retries.")

    num1_val = mantissa1 * (10**e1_val)
    num2_val = mantissa2 * (10**e2_val)
    
    if num1_val > num2_val:
        ans_op1 = ">"
    elif num1_val < num2_val:
        ans_op1 = "<"
    else:
        ans_op1 = "="

    # Part 2 (Negative Exponents)
    retry_count = 0
    while retry_count < 100:
        m3_int = random.randint(1, 9)
        m3_dec1 = random.randint(0, 9)
        m3_dec2 = random.randint(0, 9)
        e3_val = random.randint(5, 8)
        mantissa3_str = f"{m3_int}.{m3_dec1}{m3_dec2}"
        mantissa3 = float(mantissa3_str)

        m4_int = random.randint(1, 9)
        m4_dec1 = random.randint(0, 9)
        m4_dec2 = random.randint(0, 9)
        mantissa4_str = f"{m4_int}.{m4_dec1}{m4_dec2}"
        mantissa4 = float(mantissa4_str)
        
        # Randomly set e4_val relative to e3_val
        e4_val_offset = random.choice([-1, 0, 1])
        e4_val = e3_val + e4_val_offset
        # Ensure e4_val is within range [5, 8]
        e4_val = max(5, min(8, e4_val))

        # Ensure the *representation* is not identical
        if mantissa3 != mantissa4 or e3_val != e4_val:
            break
        retry_count += 1
    if retry_count == 100:
        raise RuntimeError("Failed to generate distinct numbers for Type 7 Part 2 after 100 retries.")

    num3_val = mantissa3 * (10**(-e3_val))
    num4_val = mantissa4 * (10**(-e4_val))
    
    if num3_val > num4_val:
        ans_op2 = ">"
    elif num3_val < num4_val:
        ans_op2 = "<"
    else:
        ans_op2 = "="
    
    question_text = (
        f"比較兩數的大小，在 __ 中填入＞、＜或=。\n"
        f"⑴ ${mantissa1_str} \\times 10^{{{e1_val}}}$ __ ${mantissa2_str} \\times 10^{{{e2_val}}}$ \n"
        f"⑵ ${mantissa3_str} \\times 10^{{{-e3_val}}}$ __ ${mantissa4_str} \\times 10^{{{-e4_val}}}$"
    )
    correct_answer = f"⑴ {ans_op1} ⑵ {ans_op2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Main dispatcher for Scientific Notation problems.
    Randomly selects one of the 7 problem types.
    """
    problem_types = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
        generate_type_6_problem,
        generate_type_7_problem,
    ]
    
    chosen_problem_func = random.choice(problem_types)
    return chosen_problem_func()

# The check function from the gold standard is not explicitly part of the specification
# for this skill's implementation, so it is omitted.
# If a check function were required, it would look similar to the reference:
# def check(user_answer, correct_answer):
#     user_answer = user_answer.strip().replace(' ', '').replace('$', '') # Basic cleanup for comparison
#     correct_answer = correct_answer.strip().replace(' ', '').replace('$', '') # Basic cleanup for comparison
#
#     is_correct = (user_answer == correct_answer)
#
#     # Add more robust parsing for scientific notation if needed, e.g., to handle 1.0e5 vs 10e4
#     # For now, strict string comparison might be sufficient based on how answers are formatted.
#     # Example for numerical comparison for scientific notation:
#     # try:
#     #     # Simple parsing, might need more complex regex for full LaTeX support
#     #     def parse_scientific(s):
#     #         s = s.replace('\\times', '*').replace('^', '**').replace('{', '').replace('}', '')
#     #         return eval(s)
#     #     if "times 10" in user_answer and "times 10" in correct_answer:
#     #         if abs(parse_scientific(user_answer) - parse_scientific(correct_answer)) < 1e-9:
#     #             is_correct = True
#     #     elif float(user_answer) == float(correct_answer): # For simple numbers
#     #         is_correct = True
#     # except (ValueError, SyntaxError):
#     #     pass
#
#     result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
#     return {"correct": is_correct, "result": result_text, "next_question": True}

