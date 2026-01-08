# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 38.84s | RAG: 10 examples
# Created At: 2026-01-08 22:32:51
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


 # Included for consistency with reference, though not strictly used in this skill

# --- Helper Functions for generating specific problem types ---

def _get_non_zero_int(min_val, max_val):
    """Generates a random integer in a range, ensuring it's not zero."""
    val = 0
    while val == 0:
        val = random.randint(min_val, max_val)
    return val

def generate_type_1_problem():
    """
    Type 1: Basic mixed integer operations (multiplication, division, addition, subtraction) with multiple parts.
    """
    # Part 1: v1_a * v1_b // v1_c
    v1_a = random.randint(-12, 12)
    v1_b = random.randint(-12, 12)
    v1_c = 0
    retry_count = 0
    while retry_count < 100 and (v1_c == 0 or (v1_a * v1_b) % v1_c != 0):
        v1_c = random.randint(-12, 12)
        retry_count += 1
    if retry_count == 100: # Fallback if no suitable v1_c found
        v1_a, v1_b, v1_c = 6, 4, 3 # Example values that work
    ans1 = (v1_a * v1_b) // v1_c

    # Part 2: v2_a // v2_b * v2_c
    v2_a = random.randint(-12, 12)
    v2_b = 0
    retry_count = 0
    while retry_count < 100 and (v2_b == 0 or v2_a % v2_b != 0):
        v2_b = random.randint(-12, 12)
        retry_count += 1
    if retry_count == 100: # Fallback
        v2_a, v2_b = 12, 4
    v2_c = random.randint(-12, 12)
    ans2 = (v2_a // v2_b) * v2_c

    # Part 3: v3_a + v3_b * v3_c
    v3_a = random.randint(-12, 12)
    v3_b = random.randint(-12, 12)
    v3_c = random.randint(-12, 12)
    ans3 = v3_a + v3_b * v3_c

    # Part 4: v4_a * v4_b - v4_c // v4_d
    v4_a = random.randint(-12, 12)
    v4_b = random.randint(-12, 12)
    v4_c = random.randint(-12, 12)
    v4_d = 0
    retry_count = 0
    while retry_count < 100 and (v4_d == 0 or v4_c % v4_d != 0):
        v4_d = random.randint(-12, 12)
        retry_count += 1
    if retry_count == 100: # Fallback
        v4_c, v4_d = 10, 5
    ans4 = v4_a * v4_b - (v4_c // v4_d)

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ {v1_a}×{v1_b}÷{v1_c}\n"
        f"⑵ {v2_a}÷{v2_b}×{v2_c}\n"
        f"⑶ {v3_a}＋{v3_b}×{v3_c}\n"
        f"⑷ {v4_a}×{v4_b}-{v4_c}÷{v4_d}"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}\n⑶ {ans3}\n⑷ {ans4}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Type 2: Basic mixed integer operations with more negative numbers and multiple parts.
    """
    # Part 1: (-v1_a) * (-v1_b) // v1_c
    v1_a = random.randint(2, 9)
    v1_b = random.randint(2, 9)
    v1_c = 0
    retry_count = 0
    while retry_count < 100 and (v1_c == 0 or (v1_a * v1_b) % v1_c != 0):
        v1_c = random.randint(2, 9)
        retry_count += 1
    if retry_count == 100:
        v1_a, v1_b, v1_c = 4, 9, 3
    ans1 = (-v1_a) * (-v1_b) // v1_c

    # Part 2: v2_a // (-v2_b) * (-v2_c)
    v2_a = random.randint(2, 9)
    v2_b = 0
    retry_count = 0
    while retry_count < 100 and (v2_b == 0 or v2_a % v2_b != 0):
        v2_b = random.randint(2, 9)
        retry_count += 1
    if retry_count == 100:
        v2_a, v2_b = 6, 2
    v2_c = random.randint(2, 9)
    ans2 = v2_a // (-v2_b) * (-v2_c)

    # Part 3: (-v3_a) - (-v3_b) * v3_c
    v3_a = random.randint(2, 9)
    v3_b = random.randint(2, 9)
    v3_c = random.randint(2, 9)
    ans3 = (-v3_a) - (-v3_b) * v3_c

    # Part 4: (-v4_a) * v4_b + (-v4_c) // v4_d
    v4_a = random.randint(2, 9)
    v4_b = random.randint(2, 9)
    v4_c = random.randint(2, 9)
    v4_d = 0
    retry_count = 0
    while retry_count < 100 and (v4_d == 0 or v4_c % v4_d != 0):
        v4_d = random.randint(2, 9)
        retry_count += 1
    if retry_count == 100:
        v4_c, v4_d = 8, 4
    ans4 = (-v4_a) * v4_b + (-v4_c) // v4_d

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ ({ -v1_a })×({ -v1_b })÷{v1_c}\n"
        f"⑵ {v2_a}÷({ -v2_b })×({ -v2_c })\n"
        f"⑶ ({ -v3_a })-({ -v3_b })×{v3_c}\n"
        f"⑷ ({ -v4_a })×{v4_b}＋({ -v4_c })÷{v4_d}"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}\n⑶ {ans3}\n⑷ {ans4}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Type 3: Order of operations with nested brackets involving multiplication, subtraction, and division.
    """
    v1_outer = random.randint(-100, -20)
    v2_mult1 = random.randint(-10, -2)
    v3_mult2 = random.randint(2, 10)
    v4_sub = random.randint(1, 5)

    inner_val = 0
    retry_count = 0
    while retry_count < 100:
        inner_val = v2_mult1 * v3_mult2 - v4_sub
        if inner_val != 0 and v1_outer % inner_val == 0:
            break
        v1_outer = random.randint(-100, -20)
        v2_mult1 = random.randint(-10, -2)
        v3_mult2 = random.randint(2, 10)
        v4_sub = random.randint(1, 5)
        retry_count += 1
    
    if retry_count == 100: # Fallback to a working set
        v1_outer, v2_mult1, v3_mult2, v4_sub = -60, -7, 2, 1
        inner_val = v2_mult1 * v3_mult2 - v4_sub # -7*2-1 = -14-1 = -15

    ans = v1_outer // inner_val

    question_text = f"計算 ({v1_outer})÷[ ({v2_mult1})×{v3_mult2}-{v4_sub} ] 的值。"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Type 4: Order of operations with nested brackets involving addition, division, and multiplication.
    """
    v1_add1 = random.randint(-30, -10)
    v2_add2 = random.randint(-20, -5)
    v4_mult = random.randint(2, 5)

    sum_val = v1_add1 + v2_add2
    v3_div = 0
    retry_count = 0
    while retry_count < 100 and (v3_div == 0 or sum_val % v3_div != 0):
        v3_div = random.randint(-10, -2)
        retry_count += 1
    
    if retry_count == 100: # Fallback
        v1_add1, v2_add2, v3_div, v4_mult = -20, -10, -5, 3
        sum_val = v1_add1 + v2_add2 # -30

    ans = (sum_val // v3_div) * v4_mult

    question_text = f"計算 [ ({v1_add1})＋({v2_add2}) ]÷({v3_div})×{v4_mult} 的值。"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Type 5: Absolute value in an expression with mixed operations (multiplication, subtraction, addition).
    """
    v1_mult1 = random.randint(-10, -2)
    v2_mult2 = random.randint(2, 8)
    v3_abs_mult1 = random.randint(-8, -2)
    v4_abs_mult2 = random.randint(5, 10)
    v5_abs_sub = random.randint(1, 5)

    abs_inner = v3_abs_mult1 * v4_abs_mult2 - v5_abs_sub
    ans = v1_mult1 * v2_mult2 + abs(abs_inner)

    question_text = f"計算 ({v1_mult1})×{v2_mult2}＋｜({v3_abs_mult1})×{v4_abs_mult2}-{v5_abs_sub}｜的值。"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_6_problem():
    """
    Type 6: Absolute value in an expression with mixed operations (multiplication, subtraction, division, multiplication).
    """
    v1_abs_mult1 = random.randint(2, 8)
    v2_abs_mult2 = random.randint(-8, -2)
    v3_abs_sub = random.randint(1, 5)
    v5_mult = random.randint(-5, -2)

    abs_inner_raw = v1_abs_mult1 * v2_abs_mult2 - v3_abs_sub
    abs_inner = abs(abs_inner_raw)
    
    v4_div = 0
    retry_count = 0
    while retry_count < 100 and (v4_div == 0 or abs_inner % v4_div != 0):
        v4_div = random.randint(2, 5)
        retry_count += 1
    
    if retry_count == 100: # Fallback
        v1_abs_mult1, v2_abs_mult2, v3_abs_sub, v4_div, v5_mult = 8, -2, 5, 7, -3
        abs_inner = abs(v1_abs_mult1 * v2_abs_mult2 - v3_abs_sub) # abs(8*-2 - 5) = abs(-16-5) = abs(-21) = 21

    ans = (abs_inner // v4_div) * v5_mult

    question_text = f"計算 ｜{v1_abs_mult1}×({v2_abs_mult2})-{v3_abs_sub}｜÷{v4_div}×({v5_mult}) 的值。"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_7_problem():
    """
    Type 7: Distributive property (e.g., `a*c + b*c = (a+b)*c`) with positive and negative common factors.
    """
    # Part 1: v1_a * v1_common + v1_b * v1_common
    v1_common = random.randint(-10, -2)
    v1_a = random.randint(10, 100)
    v1_b = random.randint(10, 100)
    ans1 = v1_a * v1_common + v1_b * v1_common

    # Part 2: v2_a * v2_common - v2_b * v2_common
    v2_common = random.randint(-10, -2)
    v2_a = random.randint(10, 100)
    v2_b = random.randint(10, 100)
    ans2 = v2_a * v2_common - v2_b * v2_common

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ {v1_a}×({v1_common})＋{v1_b}×({v1_common})\n"
        f"⑵ {v2_a}×({v2_common})-{v2_b}×({v2_common})"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_8_problem():
    """
    Type 8: Distributive property with larger numbers, often resulting in multiples of 100 or 1000.
    """
    # Part 1: (v1_common_neg) * v1_a + (v1_common_neg) * v1_b -> (v1_common_neg) * (v1_a + v1_b)
    v1_common_neg = random.randint(-150, -50)
    v1_a = random.randint(20, 80)
    v1_b = 100 - v1_a
    ans1 = v1_common_neg * (v1_a + v1_b)

    # Part 2: v2_large * v2_common_mult - v2_small * v2_common_mult -> (v2_large - v2_small) * v2_common_mult
    v2_common_mult = random.randint(-50, -10)
    v2_small = random.randint(1, 9)
    v2_large = 1000 + v2_small # Ensures (v2_large - v2_small) is 1000
    ans2 = (v2_large - v2_small) * v2_common_mult

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ ({v1_common_neg})×{v1_a}＋({v1_common_neg})×{v1_b}\n"
        f"⑵ {v2_large}×({v2_common_mult})-{v2_small}×({v2_common_mult})"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_9_problem():
    """
    Type 9: Mental math for multiplication, rewriting numbers as `(X + a) * b` or `a * (Y - b)` where X, Y are powers of 10.
    """
    # Part 1: num1 * v1_factor, where num1 = 1000 + v1_offset
    v1_base = 1000
    v1_offset = random.randint(1, 9)
    v1_factor = random.randint(-200, -100)
    num1 = v1_base + v1_offset
    ans1 = num1 * v1_factor

    # Part 2: v2_factor * num2, where num2 = 1000 - v2_offset
    v2_base = 1000
    v2_offset = random.randint(1, 9)
    v2_factor = random.randint(-300, -100)
    num2 = v2_base - v2_offset
    ans2 = v2_factor * num2

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ {num1}×({v1_factor})\n"
        f"⑵ ({v2_factor})×{num2}"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_10_problem():
    """
    Type 10: Mental math for multiplication, rewriting numbers as `(A00 - x) * b` or `a * (B00 + y)`.
    """
    # Part 1: num1 * v1_factor, where num1 = 200 - v1_offset
    v1_base = 200
    v1_offset = random.randint(1, 5)
    v1_factor = random.randint(-20, -10)
    num1 = v1_base - v1_offset
    ans1 = num1 * v1_factor

    # Part 2: v2_factor * num2, where num2 = (400 or 500) + v2_offset
    v2_base = random.choice([400, 500])
    v2_offset = random.randint(1, 5)
    v2_factor = random.randint(-60, -40)
    num2 = v2_base + v2_offset
    ans2 = v2_factor * num2

    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ {num1}×({v1_factor})\n"
        f"⑵ ({v2_factor})×{num2}"
    )
    correct_answer = f"⑴ {ans1}\n⑵ {ans2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_11_problem():
    """
    Type 11: Word problem involving integer arithmetic, accumulating position on a number line based on event outcomes.
    """
    even_move_right = random.randint(3, 7)
    odd_move_left = random.randint(3, 7)
    while even_move_right == odd_move_left: # Ensure distinct values for more interesting problems
        odd_move_left = random.randint(3, 7)

    total_rolls = random.randint(8, 15)
    even_count = random.randint(2, total_rolls - 2) # Ensure at least 2 odd and 2 even rolls
    odd_count = total_rolls - even_count

    final_position = even_count * even_move_right - odd_count * odd_move_left

    question_text = (
        f"小翊投擲一顆點數為 1、2、3、4、5、6 的骰子，並將一個棋子放在數線上，依照下列規則移動。\n"
        f"擲出偶數點：棋子往數線右方移動 {even_move_right} 個單位；\n"
        f"擲出奇數點：棋子往數線左方移動 {odd_move_left} 個單位。\n"
        f"已知小翊一開始將棋子放在原點，共投擲了 {total_rolls} 次，其中出現 {even_count} 次偶數點，則棋子最後的位置在哪個坐標上？"
    )
    correct_answer = str(final_position)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_12_problem():
    """
    Type 12: Word problem involving integer arithmetic, calculating scores for two players in a game based on win/lose/draw conditions.
    """
    win_points = random.randint(2, 5)
    lose_deduct = random.randint(1, 3)
    draw_points = random.randint(0, 2)
    
    total_games = random.randint(8, 15)
    
    p1_wins = random.randint(2, total_games - 2) # Ensure p1 wins at least 2 games
    
    p2_wins = 0
    draws = -1
    retry_count = 0
    while retry_count < 100:
        p2_wins = random.randint(1, total_games - p1_wins - 1) # Ensure p2 wins at least 1, and enough games left for draws
        draws = total_games - p1_wins - p2_wins
        if draws >= 0:
            break
        retry_count += 1
    
    if retry_count == 100: # Fallback to a working set
        total_games, p1_wins, p2_wins = 10, 4, 3
        draws = total_games - p1_wins - p2_wins # 3
        win_points, lose_deduct, draw_points = 3, 2, 1
        
    p1_score = p1_wins * win_points - p2_wins * lose_deduct + draws * draw_points
    p2_score = p2_wins * win_points - p1_wins * lose_deduct + draws * draw_points

    question_text = (
        f"小妍與小美玩猜拳遊戲，遊戲規則為贏的人得{win_points}分，輸的人扣{lose_deduct}分，平手則各得{draw_points}分。\n"
        f"已知兩人共猜了 {total_games} 次拳，其中小妍贏 {p1_wins} 次，小美贏 {p2_wins} 次，平手 {draws} 次，分別求出兩人最後的分數為何？"
    )
    correct_answer = f"小妍{p1_score}分，小美{p2_score}分"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Standard Check Function (copied from reference) ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Attempt to compare as floats for numerical answers, if direct string comparison fails
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass
        except TypeError: # Handle cases where correct_answer might not be directly floatable (e.g., multiline answers)
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}


# --- Main Dispatcher ---

def generate(level=1):
    """
    Generates a Four Arithmetic Operations Of Integers problem based on a random type.
    The 'level' parameter is ignored for now, as per spec.
    """
    problem_type = random.randint(1, 12) # Randomly pick one of the 12 types
    
    if problem_type == 1:
        return generate_type_1_problem()
    elif problem_type == 2:
        return generate_type_2_problem()
    elif problem_type == 3:
        return generate_type_3_problem()
    elif problem_type == 4:
        return generate_type_4_problem()
    elif problem_type == 5:
        return generate_type_5_problem()
    elif problem_type == 6:
        return generate_type_6_problem()
    elif problem_type == 7:
        return generate_type_7_problem()
    elif problem_type == 8:
        return generate_type_8_problem()
    elif problem_type == 9:
        return generate_type_9_problem()
    elif problem_type == 10:
        return generate_type_10_problem()
    elif problem_type == 11:
        return generate_type_11_problem()
    elif problem_type == 12:
        return generate_type_12_problem()
    else:
        raise ValueError("Invalid problem type generated.")

