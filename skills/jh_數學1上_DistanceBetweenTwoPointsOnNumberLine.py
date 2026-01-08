# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 47.22s | RAG: 6 examples
# Created At: 2026-01-08 22:27:55
# Fix Status: [Clean Pass]
#==============================================================================


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
    Type 1: Calculate the distance between two points on a number line
            where one coordinate is negative and the other is positive.
    """
    x1 = random.randint(-15, -1)
    x2 = random.randint(1, 15)
    ans = abs(x2 - x1)
    
    question_text = f"數線上有 $A ( {x1} )$、$B ( {x2} )$ 兩點，則 $A$、$B$ 兩點的距離 $AB$ 為多少？"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Type 2: Calculate the distance between two points on a number line
            where both coordinates are negative.
    """
    x1 = random.randint(-20, -10)
    x2 = random.randint(-9, -1)
    ans = abs(x2 - x1)
    
    question_text = f"數線上有 $C ( {x1} )$、$D ( {x2} )$ 兩點，則 $C$、$D$ 兩點的距離 $CD$ 為多少？"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Type 3: Find the possible coordinates of a point given another point and the distance between them.
    """
    x2 = random.randint(-10, 10)
    dist = random.randint(2, 15)
    
    ans1 = x2 + dist
    ans2 = x2 - dist
    
    # Ensure canonical order for the answer string: smaller_value 或 larger_value
    if ans1 < ans2:
        correct_answer = f"{ans1} 或 {ans2}"
    else:
        correct_answer = f"{ans2} 或 {ans1}"
        
    question_text = f"數線上有 $A ( a )$、$B ( {x2} )$ 兩點，如果 $AB={dist}$，則 $a$ 可能是多少？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Type 4: Find the possible coordinates of a point given another point and the distance between them (variant).
    """
    x2 = random.randint(-12, 12)
    dist = random.randint(3, 18)
    
    ans1 = x2 + dist
    ans2 = x2 - dist
    
    # Ensure canonical order for the answer string: smaller_value 或 larger_value
    if ans1 < ans2:
        correct_answer = f"{ans1} 或 {ans2}"
    else:
        correct_answer = f"{ans2} 或 {ans1}"
        
    question_text = f"數線上有 $C ( c )$、$D ( {x2} )$ 兩點，如果 $CD={dist}$，則 $c$ 可能是多少？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Type 5: Calculate the midpoint of two points on a number line (integer midpoint).
    Ensures x1 != x2 and (x1 + x2) is an even number.
    """
    while True:
        x1 = random.randint(-10, 10)
        
        # Determine target parity for x2 to ensure (x1 + x2) is even
        # If x1 is even, x2 must be even. If x1 is odd, x2 must be odd.
        target_parity = x1 % 2
        
        # Generate candidates for x2 that are within range, have the correct parity, and are not equal to x1
        valid_x2_candidates = [i for i in range(-10, 11) if i % 2 == target_parity and i != x1]
        
        if valid_x2_candidates:
            x2 = random.choice(valid_x2_candidates)
            ans = (x1 + x2) // 2
            question_text = f"數線上有 $A ( {x1} )$、$B ( {x2} )$、$C ( c )$ 三點，若 $C$ 為 $A$、$B$ 的中點，則 $c$ 是多少？"
            correct_answer = str(ans)
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
        # If no valid x2 candidates for this x1 (should not happen with given ranges),
        # the loop will continue to regenerate x1.

def generate_type_6_problem():
    """
    Type 6: Calculate the midpoint of two points on a number line (variant, integer midpoint).
    Ensures x1 != x2 and (x1 + x2) is an even number.
    """
    while True:
        x1 = random.randint(-12, 12)
        
        target_parity = x1 % 2
        
        valid_x2_candidates = [i for i in range(-12, 13) if i % 2 == target_parity and i != x1]
        
        if valid_x2_candidates:
            x2 = random.choice(valid_x2_candidates)
            ans = (x1 + x2) // 2
            question_text = f"數線上有 $A ( {x1} )$、$B ( {x2} )$、$C ( c )$ 三點，若 $C$ 為 $A$、$B$ 的中點，則 $c$ 是多少？"
            correct_answer = str(ans)
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }

def generate(level=1):
    """
    Generates a random problem from the defined types.
    The 'level' parameter is a placeholder for future complexity scaling
    and is currently ignored.
    
    Returns:
        dict: A dictionary containing 'question_text', 'answer', and 'correct_answer' for the generated problem.
    """
    problem_generators = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
        generate_type_6_problem,
    ]
    
    selected_generator = random.choice(problem_generators)
    return selected_generator()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_processed = str(user_answer).strip().upper()
    correct_answer_processed = str(correct_answer).strip().upper()
    
    is_correct = (user_answer_processed == correct_answer_processed)
    
    if not is_correct:
        try:
            if float(user_answer_processed) == float(correct_answer_processed):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
