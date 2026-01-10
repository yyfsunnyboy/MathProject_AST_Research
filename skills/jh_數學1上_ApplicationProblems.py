# ==============================================================================
# ID: jh_數學1上_ApplicationProblems
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.7)
# Duration: 31.82s | RAG: 8 examples
# Created At: 2026-01-09 13:19:48
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
    """Format negative numbers with parentheses for LaTeX display"""
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





# ==============================================================================
# GOLD STANDARD TEMPLATE v8.7 (Universal)
# ==============================================================================
# Rules for AI Coder:
# 1. LATEX: Use f-string with DOUBLE BRACES for LaTeX commands. 
#    Ex: f"\\frac{{{a}}}{{{b}}}" -> \frac{a}{b}
#    Ex: f"\\begin{{bmatrix}} {a} & {b} \\\\ {c} & {d} \\end{{bmatrix}}"
# 2. NEGATIVES: Use fmt_num(val) to handle negative numbers like (-5).
# 3. LEVEL: Level 1 = Basic Concept/Direct Calc. Level 2 = Application/Mixed.
# 4. RETURN: Must return dict with 'question_text', 'answer', 'correct_answer'.
# ==============================================================================


def gcd(a, b):
    return math.gcd(a, b)

def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

def lcm_three(a, b, c):
    return lcm(lcm(a, b), c)

# [Level 1: Basic Types]

def generate_type_1_problem():
    """
    Concept: Finding the Greatest Common Divisor (GCD) of two numbers in a direct "grouping" context.
    """
    common_factor = random.choice([2, 3, 4, 5, 6, 8, 10, 12, 15])
    factor1 = random.randint(3, 10)
    factor2 = random.randint(3, 10)
    while factor1 == factor2: # Ensure distinct factors
        factor2 = random.randint(3, 10)
    num1 = common_factor * factor1
    num2 = common_factor * factor2
    # Ensure numbers are within a reasonable range for fruit counts
    num1 = max(30, num1)
    num2 = max(30, num2)

    ans_val = math.gcd(num1, num2)
    question_text = f"水果店老闆想將 {num1} 個梨子和 {num2} 個蘋果分裝成禮盒出售，梨子禮盒和蘋果禮盒內的水果個數要一樣多，且全部分裝完。那麼一盒最多可以放幾個水果？"
    
    return {
        "question_text": question_text,
        "answer": str(ans_val),
        "correct_answer": str(ans_val),
        "difficulty": 1
    }

def generate_type_3_problem():
    """
    Concept: Finding the Least Common Multiple (LCM) of three numbers in a "simultaneous event" context.
    """
    days = random.sample(range(6, 21), 3) # Pick 3 distinct days between 6 and 20
    day1, day2, day3 = days[0], days[1], days[2]
    
    ans_val = lcm_three(day1, day2, day3)
    question_text = f"小翊每 {day1} 天到中央公園跑步一次，小妍每 {day2} 天到中央公園跑步一次，小靖每 {day3} 天到中央公園跑步一次。今天三人都到中央公園跑步，那麼最少要再幾天，三人才會再度在同一天到此公園跑步？"
    
    return {
        "question_text": question_text,
        "answer": str(ans_val),
        "correct_answer": str(ans_val),
        "difficulty": 1
    }

def generate_type_4_problem():
    """
    Concept: Finding the Least Common Multiple (LCM) of three numbers in a "simultaneous event" context (different scenario).
    """
    hours = random.sample([15, 18, 20, 24, 30, 36, 40, 45, 50, 60], 3)
    h1, h2, h3 = hours[0], hours[1], hours[2]
    
    ans_val = lcm_three(h1, h2, h3)
    question_text = f"小妍玩《健康農場》遊戲時發現，高麗菜每 {h1} 小時可收成一次，小白菜每 {h2} 小時可收成一次，空心菜每 {h3} 小時可收成一次。某次小妍同時收成這三種蔬菜，那麼最少要再幾小時，小妍才可以再度同時收成這三種蔬菜？"
    
    return {
        "question_text": question_text,
        "answer": str(ans_val),
        "correct_answer": str(ans_val),
        "difficulty": 1
    }

# [Level 2: Advanced Types]

def generate_type_2_problem():
    """
    Concept: Finding GCD, then using it for a derived calculation (total per group). Multi-part question.
    """
    common_factor = random.choice([2, 3, 4, 5, 6, 8])
    factor_a = random.randint(3, 8)
    factor_b = random.randint(2, 6)
    while factor_a == factor_b: # Ensure distinct factors for variety
        factor_b = random.randint(2, 6)
    a_students = common_factor * factor_a
    b_students = common_factor * factor_b
    # Ensure reasonable student counts
    a_students = max(15, a_students)
    b_students = max(10, b_students)
    
    g = math.gcd(a_students, b_students)
    ans1 = g
    ans2 = (a_students // g) + (b_students // g)
    correct_answer = f"⑴ {ans1} 組 ⑵ {ans2} 位學生"
    question_text = f"臺灣的 A 校為了招待來自新加坡的姐妹學校 B 校，安排 {a_students} 位學生來接待 B 校 {b_students} 位學生，現將其分成若干組進行參觀活動，每組都要包含 A 校及 B 校學生，而且每組 A 校學生人數一樣多、B 校學生人數也一樣多，請問：\n⑴ 最多可分成幾組？\n⑵ 承⑴，此時每組共有多少位學生？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }

def generate_type_5_problem():
    """
    Concept: Finding LCM for dimensions of a rectangle to form a square, then calculating area. Multi-part question.
    """
    dimensions = random.sample([30, 40, 45, 50, 60, 75, 80, 90], 2)
    length, width = dimensions[0], dimensions[1]
    
    side_length = lcm(length, width)
    area = side_length * side_length
    correct_answer = f"邊長 {side_length} 公分，面積 {area} 平方公分"
    question_text = f"將若干塊長 {length} 公分、寬 {width} 公分的長方形磁磚，以長邊接長邊，短邊接短邊的方式，緊密且無縫隙拼貼成一個正方形，則所拼貼的正方形最小邊長為何？此時面積是多少平方公分？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }

def generate_type_6_problem():
    """
    Concept: Finding LCM for side lengths of two types of square tiles to determine the smallest square bulletin board, then calculating its area.
    """
    sides = random.sample([30, 40, 45, 48, 50, 60, 75, 80, 90], 2)
    side1, side2 = sides[0], sides[1]
    
    board_side = lcm(side1, side2)
    area = board_side * board_side
    correct_answer = f"{area} 平方公分"
    question_text = f"小翊想用邊長 {side1} 公分與 {side2} 公分兩種正方形海報紙，貼滿教室後方的正方形布告欄，已知用這兩種海報紙的任一種若干張，皆可在不切割的情況下緊密的將布告欄貼滿，請問此布告欄的面積最小是多少平方公分？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }

def generate_type_7_problem():
    """
    Concept: Finding GCD for dimensions to determine maximum spacing, then calculating the total number of trees around the perimeter. Multi-part question.
    """
    common_factor = random.choice([5, 9, 15, 25, 30, 45])
    factor_l = random.randint(4, 10)
    factor_w = random.randint(2, 6)
    while factor_l == factor_w: # Ensure distinct factors
        factor_w = random.randint(2, 6)
    length = common_factor * factor_l
    width = common_factor * factor_w
    # Ensure reasonable dimensions
    length = max(150, length)
    width = max(90, width)
    
    g = math.gcd(length, width)
    distance = g
    # For a rectangle with trees at all 4 corners, count is (L/g + W/g) * 2
    num_trees = (length // g + width // g) * 2
    correct_answer = f"距離 {distance} 公尺，共 {num_trees} 棵樹"
    question_text = f"王伯伯有一塊長 {length} 公尺、寬 {width} 公尺的長方形土地，他想在其周圍種樹，相鄰兩棵樹之間的距離要相等，且四個頂點都種，則相鄰兩棵樹之間的距離最大是幾公尺？此時總共要種幾棵樹？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }

def generate_type_8_problem():
    """
    Concept: Finding LCM of two intervals to find common positions, then counting within a range, 
             considering "not installed at ends". Multi-part, complex counting.
    """
    intervals = random.sample([15, 20, 24, 25, 30, 36, 40], 2)
    interval1, interval2 = intervals[0], intervals[1]
    
    lcm_intervals = lcm(interval1, interval2)
    # total_length should be a multiple of lcm_val and large enough
    total_length_multiplier = random.randint(10, 25)
    total_length = lcm_intervals * total_length_multiplier
    # Ensure total_length is within a reasonable range (e.g., 1000 to 5000)
    total_length = max(1000, total_length)
    total_length = min(5000, total_length)
    
    distance = lcm_intervals
    # Number of common lights on one side, excluding ends: (total_length / lcm_intervals) - 1
    # Example: total_length=100, lcm=20. Positions: 20, 40, 60, 80. Count = 4 = (100/20)-1.
    num_common_lights_one_side = (total_length // lcm_intervals) - 1
    total_common_lights = num_common_lights_one_side * 2 # For both sides
    correct_answer = f"距離 {distance} 公尺，共 {total_common_lights} 盞"
    question_text = f"澎湖有一全長 {total_length} 公尺的跨海大橋，原來在此橋的兩側每隔 {interval1} 公尺裝設一盞路燈 ( 橋頭與橋尾未裝 )，但因節能考量改為每隔 {interval2} 公尺裝設一盞路燈，則在不需要拆除的路燈中，相鄰兩盞的距離是多少公尺？此時不需要拆除的路燈共有多少盞？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 2
    }


def generate(level=1):
    """
    Generates a math problem based on the specified level.
    Args:
        level (int): The difficulty level (1 for Basic, 2 for Advanced).
    Returns:
        dict: A dictionary containing the question string, the answer string, and the correct answer string.
    """
    if level == 1:
        problem_func = random.choice([
            generate_type_1_problem,
            generate_type_3_problem,
            generate_type_4_problem,
        ])
    elif level == 2:
        problem_func = random.choice([
            generate_type_2_problem,
            generate_type_5_problem,
            generate_type_6_problem,
            generate_type_7_problem,
            generate_type_8_problem,
        ])
    else:
        raise ValueError("Invalid level. Please choose 1 for Basic or 2 for Advanced.")

    return problem_func()

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    try:
        # Attempt float comparison for numerical answers
        user_float = float(user)
        correct_float = float(correct)
        if abs(user_float - correct_float) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # Not a simple float, fall back to string comparison
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}

