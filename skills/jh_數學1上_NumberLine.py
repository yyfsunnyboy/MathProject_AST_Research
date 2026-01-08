# ==============================================================================
# ID: jh_數學1上_NumberLine
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 44.33s | RAG: 4 examples
# Created At: 2026-01-08 22:59:04
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




# Helper functions for Type 3 and Type 4 problem generation
# These are defined locally within their respective generate functions as per spec,
# but for clarity and potential reusability if moved, they are outlined here.

def generate_type_1_problem():
    """
    Generates a Type 1 problem: Plotting two integer points (one positive, one negative).
    """
    point_a_val = random.randint(1, 10)
    point_b_val = random.randint(-10, -1)
    
    question_text = f"畫一條數線，並標記 A ( {point_a_val} )、B ( {point_b_val} ) 的位置。"
    correct_answer = f"圖示標示 A 點在 {point_a_val}，B 點在 {point_b_val}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # As per gold standard, provide 'answer' key too
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Generates a Type 2 problem: Plotting two integer points and identifying three integer points.
    """
    used_values = set()
    
    # Generate plot_c_val
    plot_c_val = random.randint(1, 10)
    used_values.add(plot_c_val)
    
    # Generate plot_d_val
    retry_count = 0
    while True:
        plot_d_val = random.randint(-10, -1)
        if plot_d_val not in used_values:
            used_values.add(plot_d_val)
            break
        retry_count += 1
        if retry_count > 100:
            raise RuntimeError("Failed to generate unique plot_d_val for Type 2")
    
    # Generate id_e_val, id_f_val, id_g_val
    id_points = []
    for _ in range(3):
        retry_count = 0
        while True:
            val = random.randint(-10, 10)
            if val != 0 and val not in used_values: # Avoid 0 and already used values
                id_points.append(val)
                used_values.add(val)
                break
            retry_count += 1
            if retry_count > 100:
                raise RuntimeError(f"Failed to generate unique id_point {_} for Type 2")
    
    id_e_val, id_f_val, id_g_val = id_points
    
    question_text = (
        f"1. 畫一條數線，並標記 C ( {plot_c_val} )、D ( {plot_d_val} ) 的位置。\n"
        f"2. 寫出數線上 E({id_e_val})、F({id_f_val})、G({id_g_val}) 三點的坐標。"
    )
    correct_answer = (
        f"1. 圖示標示 C 在 {plot_c_val}，D 在 {plot_d_val}\n"
        f"2. E({id_e_val}), F({id_f_val}), G({id_g_val})"
    )
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Generates a Type 3 problem: Plotting one decimal point and one mixed fraction point.
    """
    def format_mixed_fraction_latex(sign, whole, num, den):
        if sign == -1:
            return f"$-{whole} \\frac{{{num}}}{{{den}}}$"
        return f"${whole} \\frac{{{num}}}{{{den}}}$"

    def format_mixed_fraction_answer(sign, whole, num, den):
        if sign == -1:
            return f"-{whole} 又 {num}/{den}"
        return f"{whole} 又 {num}/{den}"
        
    # Generate dec_val
    retry_count = 0
    dec_val = 0.0 # Initialize to ensure loop runs
    while abs(dec_val) < 0.001 or dec_val == int(dec_val): # Avoid 0 and integers
        int_part = random.randint(-5, 5)
        dec_part = random.randint(1, 9) / 10
        # Randomly choose positive or negative for the decimal part
        dec_val = int_part + dec_part if random.choice([True, False]) else int_part - dec_part
        
        retry_count += 1
        if retry_count > 100:
            raise RuntimeError("Failed to generate unique dec_val for Type 3")

    # Generate mixed fraction components
    mixed_val_numerical = 0.0 # Initialize
    retry_count = 0
    # Ensure distinctness from dec_val and not zero itself
    while abs(mixed_val_numerical - dec_val) < 0.001 or abs(mixed_val_numerical) < 0.001: 
        mixed_sign = random.choice([1, -1])
        mixed_whole = random.randint(1, 4)
        mixed_den = random.randint(2, 5)
        
        inner_retry = 0
        mixed_num = 0 # Initialize
        while True:
            mixed_num = random.randint(1, mixed_den - 1) # num < den
            if mixed_num > 0: # Ensure numerator is positive
                break
            inner_retry += 1
            if inner_retry > 100:
                raise RuntimeError("Failed to generate valid mixed_num for Type 3")

        mixed_val_numerical = mixed_sign * (mixed_whole + mixed_num / mixed_den)
        
        retry_count += 1
        if retry_count > 100:
            raise RuntimeError("Failed to generate distinct mixed_fraction_val for Type 3")

    mixed_val_latex = format_mixed_fraction_latex(mixed_sign, mixed_whole, mixed_num, mixed_den)
    mixed_val_answer = format_mixed_fraction_answer(mixed_sign, mixed_whole, mixed_num, mixed_den)
    
    question_text = f"畫一條數線，並標記 A ( ${dec_val}$ )、B ( {mixed_val_latex} ) 的位置。"
    correct_answer = f"圖示標示 A 點在 {dec_val}，B 點在 {mixed_val_answer}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Generates a Type 4 problem: Plotting three points (mixed fraction, mixed fraction/decimal, decimal)
    and identifying two points (mixed fraction, mixed fraction/decimal).
    """
    def _generate_mixed_fraction_internal():
        sign = random.choice([1, -1])
        whole = random.randint(1, 4)
        den = random.randint(2, 5)
        num = random.randint(1, den - 1)
        numerical_val = sign * (whole + num / den)
        latex = f"$-{whole} \\frac{{{num}}}{{{den}}}$" if sign == -1 else f"${whole} \\frac{{{num}}}{{{den}}}$"
        answer_str = f"{sign * whole} 又 {num}/{den}"
        return numerical_val, latex, answer_str

    def _generate_decimal_internal():
        sign = random.choice([1, -1])
        int_part = random.randint(0, 4) # Allow 0 for decimal like 0.3
        dec_part = random.randint(1, 9) / 10
        numerical_val = sign * (int_part + dec_part)
        latex = f"${numerical_val}$"
        answer_str = f"{numerical_val}"
        return numerical_val, latex, answer_str

    used_values_numerical = set()
    
    def get_unique_value(generator_func, max_attempts=100):
        for _ in range(max_attempts):
            num_val, latex_str, ans_str = generator_func()
            if abs(num_val) < 0.001: continue # Avoid generating 0
            is_unique = True
            for existing_val in used_values_numerical:
                if abs(num_val - existing_val) < 0.001: # Check for approximate equality
                    is_unique = False
                    break
            if is_unique:
                used_values_numerical.add(num_val)
                return num_val, latex_str, ans_str
        raise RuntimeError(f"Failed to generate unique value after {max_attempts} attempts for Type 4.")

    # Generate plot points
    plot_c_num, plot_c_latex, plot_c_ans = get_unique_value(_generate_mixed_fraction_internal)
    
    plot_d_generator = random.choice([_generate_mixed_fraction_internal, _generate_decimal_internal])
    plot_d_num, plot_d_latex, plot_d_ans = get_unique_value(plot_d_generator)

    plot_e_num, plot_e_latex, plot_e_ans = get_unique_value(_generate_decimal_internal)

    # Generate identify points
    id_f_num, id_f_latex, id_f_ans = get_unique_value(_generate_mixed_fraction_internal)

    id_g_generator = random.choice([_generate_mixed_fraction_internal, _generate_decimal_internal])
    id_g_num, id_g_latex, id_g_ans = get_unique_value(id_g_generator)
    
    question_text = (
        f"1. 在數線上分別標記 C ( {plot_c_latex} )、D ( {plot_d_latex} ) 與 E ( {plot_e_latex} ) 的位置。\n"
        f"2. 寫出數線上 F ( {id_f_latex} )、G ( {id_g_latex} ) 兩點的坐標。"
    )
    correct_answer = (
        f"1. 圖示標示 C({plot_c_ans}), D({plot_d_ans}), E({plot_e_ans})\n"
        f"2. F({id_f_ans}), G({id_g_ans})"
    )
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Main dispatcher for generating NumberLine problems based on the Architect's Spec.
    Randomly selects and generates a problem from one of the defined types (Type 1-4).
    """
    problem_generators = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
    ]
    
    # Select a generator randomly as per the Architect's Spec.
    selected_generator = random.choice(problem_generators)
    
    return selected_generator()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    (Mimicking the gold standard check function structure)
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # For numerical answers, allow float comparison
            # Note: This part might not be ideal for the multi-line descriptive answers
            # generated by the new problem types, which require exact string matching.
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    # [教學示範] 回傳結果中也可以包含 LaTeX
    # Note: For descriptive answers from new problem types, wrapping in $ will likely break LaTeX.
    # Following the gold standard structure exactly for the check function.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
