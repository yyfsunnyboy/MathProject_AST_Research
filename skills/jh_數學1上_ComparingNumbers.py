# ==============================================================================
# ID: jh_數學1上_ComparingNumbers
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 29.93s | RAG: 3 examples
# Created At: 2026-01-08 22:54:18
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


#  # Not strictly needed based on the architect's spec for _generate_random_number_and_latex

def _generate_random_number_and_latex():
    """
    Generates a random number (int, fraction, or decimal) and its LaTeX string.
    Ensures fractions are not reducible to integers.
    Returns: (float_value, latex_string)
    """
    num_type = random.choice(['int', 'frac', 'dec'])
    
    if num_type == 'int':
        val = random.randint(-10, 10) # Range for integers
        latex_str = str(val)
    elif num_type == 'frac':
        retry_count = 0
        numerator = 0
        denominator = 0
        while retry_count < 100:
            numerator = random.randint(1, 15) # Numerator range
            denominator = random.randint(2, 10) # Denominator range, avoids 0 and 1
            if numerator % denominator != 0: # Ensure it's not an integer (e.g., 4/2)
                break
            retry_count += 1
        
        if retry_count == 100: # Fallback to a guaranteed non-integer fraction if loop fails
            numerator = 3
            denominator = 4

        sign = random.choice([-1, 1]) # Randomly assign positive or negative
        val = sign * numerator / denominator
        if sign == -1:
            latex_str = f"-\\frac{{{numerator}}}{{{denominator}}}"
        else:
            latex_str = f"\\frac{{{numerator}}}{{{denominator}}}"
    else: # dec
        val = round(random.uniform(-10.0, 10.0), random.choice([1, 2])) # Decimals with 1 or 2 places
        latex_str = str(val)
    
    return val, latex_str

def generate_type_1_problem():
    """
    Concept: Comparing the magnitude of two distinct rational numbers (integers, fractions, or decimals).
    """
    num_list = []
    # Generate 4 distinct numbers
    while len(num_list) < 4:
        val, latex_str = _generate_random_number_and_latex()
        # Ensure distinct values, especially important for floats
        # Check if the float value is already in the list (with a small epsilon for comparison)
        if not any(abs(existing_val - val) < 1e-9 for existing_val, _ in num_list):
            num_list.append((val, latex_str))

    # Select two distinct indices
    idx1 = random.randint(0, 3)
    idx2 = -1 # Initialize to an invalid value
    retry_count = 0
    while True:
        idx2 = random.randint(0, 3)
        if idx2 != idx1:
            break
        retry_count += 1
        if retry_count >= 100: # Fallback for extreme unlikelihood
            idx2 = (idx1 + 1) % 4 # Ensures a distinct index if possible
            break
            
    val_a, latex_a = num_list[idx1]
    val_b, latex_b = num_list[idx2]

    # Determine the comparison symbol
    if val_a < val_b:
        ans_symbol = "＜"
    elif val_a > val_b:
        ans_symbol = "＞"
    else: # val_a == val_b (highly unlikely but possible with floating point comparisons)
        ans_symbol = "＝"

    question_text = f"比較 ${latex_a}$ 和 ${latex_b}$ 的大小。"
    correct_answer = ans_symbol

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Concept: Deductive reasoning based on "not greater than" and "not less than" implying equality.
    If a number `a` is neither greater than `X` nor less than `X`, then `a` must be equal to `X`.
    """
    target_val, target_latex_str = _generate_random_number_and_latex()

    question_text = (
        f"老師心中想了一個數 $a$，小翊猜說：「這個數比${target_latex_str}$大。」"
        f"小妍猜說：「這個數比${target_latex_str}$小。」結果老師說兩個人都猜錯了，"
        f"那麼 $a$ 應該是多少呢？"
    )
    correct_answer = str(target_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Concept: Transitive property of inequality. Given `a < X` and `X < b`, deduce that `a < b`,
    and thus `b` is greater than `a`.
    """
    pivot_val, pivot_latex_str = _generate_random_number_and_latex() # pivot_val is not directly used in the question text.

    question_text = (
        f"已知 $a$ 和 $b$ 分別代表一個數，若 $a < {pivot_latex_str}$ 且 ${pivot_latex_str} < b$，"
        f"則 $a$ 和 $b$ 何者較大？"
    )
    correct_answer = "b 較大" # As per spec

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem based on the specified level or randomly selects a type.
    Args:
        level (int): Reserved for future use, currently defaults to 1 and ignores.
                     Problems are randomly selected from the available types.
    Returns:
        dict: A dictionary containing the question text, answer, and correct answer.
    """
    problem_type = random.choice([1, 2, 3])
    
    if problem_type == 1:
        return generate_type_1_problem()
    elif problem_type == 2:
        return generate_type_2_problem()
    elif problem_type == 3:
        return generate_type_3_problem()
    else:
        # Fallback, though random.choice should prevent this
        return generate_type_1_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(' ', '').upper()
    correct_answer = correct_answer.strip().replace(' ', '').upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Attempt numerical comparison only if direct string comparison fails.
            # This handles cases where correct_answer is a number (e.g., "1.5" or "-0.75")
            # and user_answer might be numerically equivalent but different string (e.g. "1.50")
            # or for fractions (e.g. correct is "0.75", user inputs "3/4" - this check
            # will fail if user inputs "3/4" as float("3/4") is ValueError, but the spec's check
            # implies the user input is a number that can be converted to float).
            # The prompt says `correct_answer = str(target_val)` for Type 2, where `target_val` is a float.
            # So float(correct_answer) will always succeed for Type 2.
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # If conversion to float fails for either answer, it's not a numerical match.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
