# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 46.17s | RAG: 8 examples
# Created At: 2026-01-08 22:58:20
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

# --- Type 1 Implementation ---
def generate_type_1_problem():
    """
    Concept: Mixed addition and subtraction of three integers.
    The problem involves evaluating an expression with three integers and two operations.
    Template: (v1) - (v2) ＋ (v3)
    """
    max_retries = 100
    
    v1 = 0
    retry_count = 0
    while v1 == 0 and retry_count < max_retries:
        v1 = random.randint(-100, 100)
        retry_count += 1
    
    v2 = 0
    retry_count = 0
    while (v2 == v1 or v2 == 0) and retry_count < max_retries:
        v2 = random.randint(-100, 100)
        retry_count += 1
    
    v3 = 0
    retry_count = 0
    while (v3 == v1 or v3 == v2 or v3 == 0) and retry_count < max_retries:
        v3 = random.randint(-100, 100)
        retry_count += 1
    
    ans = v1 - v2 + v3
    
    question_text = f"計算下列各式的值。\n⑴ ({v1}) - ({v2}) ＋ ({v3})"
    
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }

# --- Type 2 Implementation ---
def generate_type_2_problem():
    """
    Concept: Mixed addition and subtraction of three integers with a specific structure: a + b - c.
    Template: (v1) ＋ (v2) - (v3)
    """
    max_retries = 100

    v1 = 0
    retry_count = 0
    while v1 == 0 and retry_count < max_retries:
        v1 = random.randint(-200, 200)
        retry_count += 1

    v2 = 0
    retry_count = 0
    while (v2 == v1 or v2 == 0) and retry_count < max_retries:
        v2 = random.randint(-100, 100)
        retry_count += 1

    v3 = 0
    retry_count = 0
    while (v3 == v1 or v3 == v2 or v3 == 0) and retry_count < max_retries:
        v3 = random.randint(-200, 200)
        retry_count += 1

    ans = v1 + v2 - v3
    
    question_text = f"計算下列各式的值。\n⑴ ({v1}) ＋ ({v2}) - ({v3})"
    
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }

# --- Type 3 Implementation ---
def generate_type_3_problem():
    """
    Concept: Mixed addition/subtraction with absolute values, specifically a + |b + c| - d.
    Template: v1 ＋｜(v2) ＋ v3｜ - v4
    """
    max_retries = 100

    v1 = 0
    retry_count = 0
    while v1 == 0 and retry_count < max_retries:
        v1 = random.randint(-50, 50)
        retry_count += 1

    v4 = 0
    retry_count = 0
    while (v4 == v1 or v4 == 0) and retry_count < max_retries:
        v4 = random.randint(-50, 50)
        retry_count += 1

    v2 = random.randint(-100, -10) # Must be negative

    v3 = 0
    retry_count = 0
    while (v3 == 0 or v2 + v3 == 0) and retry_count < max_retries: # v3 must be positive, and v2+v3 != 0
        v3 = random.randint(10, 100)
        retry_count += 1

    ans = v1 + abs(v2 + v3) - v4
    
    question_text = f"計算下列各式的值。\n⑴ {v1} ＋｜({v2}) ＋ {v3}｜ - {v4}"
    
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }

# --- Type 4 Implementation ---
def generate_type_4_problem():
    """
    Concept: Mixed addition/subtraction with absolute values, specifically |a| - b - |c + d|.
    Template: ｜(v1)｜ - (v2) - ｜(v3) ＋ v4｜
    """
    max_retries = 100

    v1 = random.randint(-100, -10) # Must be negative
    
    v2 = 0
    retry_count = 0
    while v2 == 0 and retry_count < max_retries:
        v2 = random.randint(-50, 50)
        retry_count += 1
    
    v3 = random.randint(-100, -10) # Must be negative

    v4 = 0
    retry_count = 0
    while (v4 == 0 or v3 + v4 == 0) and retry_count < max_retries: # v4 must be positive, and v3+v4 != 0
        v4 = random.randint(10, 100)
        retry_count += 1

    ans = abs(v1) - v2 - abs(v3 + v4)
    
    question_text = f"計算下列各式的值。\n⑴ ｜({v1})｜ - ({v2}) - ｜({v3}) ＋ {v4}｜"
    
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }

# --- Type 5 Implementation ---
def generate_type_5_problem():
    """
    Concept: Comparison of expressions demonstrating the distributive property of negation: -(a + b) vs -a - b.
    Template: -(v1 ＋ v2) 和 -v1 - v2
    """
    max_retries = 100

    v1 = random.randint(2, 15) # Must be positive
    
    v2 = 0
    retry_count = 0
    while (v2 == v1) and retry_count < max_retries:
        v2 = random.randint(2, 15) # Must be positive
        retry_count += 1

    # val1 = -(v1 + v2) # Not strictly needed as answer is always "相同"
    # val2 = -v1 - v2
    ans = "相同" 

    question_text = f"比較下列各題中，兩式的運算結果是否相同。\n⑴ -({v1} ＋ {v2}) 和 -{v1} - {v2}"
    
    return {
        "question_text": question_text,
        "answer": ans,
        "correct_answer": ans
    }

# --- Type 6 Implementation ---
def generate_type_6_problem():
    """
    Concept: Comparison of expressions demonstrating distributive property of negation with negative numbers: -(-a + b) vs a - b.
    Template: -(-v1 ＋ v2) 和 v1 - v2
    """
    max_retries = 100

    v1 = random.randint(2, 15) # Must be positive
    
    v2 = 0
    retry_count = 0
    while (v2 == v1) and retry_count < max_retries:
        v2 = random.randint(2, 15) # Must be positive
        retry_count += 1

    # val1 = -(-v1 + v2) # Not strictly needed as answer is always "相同"
    # val2 = v1 - v2
    ans = "相同" 

    question_text = f"比較下列各題中，兩式的運算結果是否相同。\n⑴ -(-{v1} ＋ {v2}) 和 {v1} - {v2}"
    
    return {
        "question_text": question_text,
        "answer": ans,
        "correct_answer": ans
    }

# --- Type 7 Implementation ---
def generate_type_7_problem():
    """
    Concept: Comparison of expressions demonstrating associativity/distributivity for subtraction: a - (b + c) vs a - b - c.
    Template: (v1) - (v2 ＋ v3) 和 (v1) - v2 - v3
    """
    max_retries = 100

    v1 = 0
    retry_count = 0
    while v1 == 0 and retry_count < max_retries:
        v1 = random.randint(-15, 15)
        retry_count += 1

    v2 = 0
    retry_count = 0
    while (v2 == v1 or v2 == 0) and retry_count < max_retries:
        v2 = random.randint(-15, 15)
        retry_count += 1

    v3 = 0
    retry_count = 0
    while (v3 == v1 or v3 == v2 or v3 == 0 or v2 + v3 == 0) and retry_count < max_retries:
        v3 = random.randint(-15, 15)
        retry_count += 1
    
    # val1 = v1 - (v2 + v3) # Not strictly needed as answer is always "相同"
    # val2 = v1 - v2 - v3
    ans = "相同" 

    question_text = f"比較下列各題中，兩式的運算結果是否相同。\n⑴ ({v1}) - ({v2} ＋ {v3}) 和 ({v1}) - {v2} - {v3}"
    
    return {
        "question_text": question_text,
        "answer": ans,
        "correct_answer": ans
    }

# --- Type 8 Implementation ---
def generate_type_8_problem():
    """
    Concept: Subtraction involving parentheses, designed for simplification by reordering or cancellation, specifically a - (b + a).
    Template: v1 - (v2 ＋ v1)
    """
    max_retries = 100

    v1 = random.randint(100, 500)
    
    v2 = 0
    retry_count = 0
    while (v2 == v1) and retry_count < max_retries:
        v2 = random.randint(10, 100)
        retry_count += 1

    ans = v1 - (v2 + v1) # This simplifies to -v2
    
    question_text = f"計算下列各式的值。\n⑴ {v1} - ({v2} ＋ {v1})"
    
    return {
        "question_text": question_text,
        "answer": str(ans),
        "correct_answer": str(ans)
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_normalized = user_answer.strip().upper()
    correct_answer_normalized = correct_answer.strip().upper()
    
    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    if not is_correct:
        try:
            # Attempt numeric comparison if string comparison fails
            user_float = float(user_answer_normalized)
            correct_float = float(correct_answer_normalized)
            if user_float == correct_float:
                is_correct = True
        except ValueError:
            pass # One or both answers are not numeric, so stick to string comparison result.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}


def generate(level=1):
    """
    Generates a mixed integer addition and subtraction problem based on the specified types.
    The 'level' parameter is currently not used but can be extended to control problem difficulty.
    """
    problem_types = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
        generate_type_6_problem,
        generate_type_7_problem,
        generate_type_8_problem,
    ]
    
    selected_generator = random.choice(problem_types)
    return selected_generator()

