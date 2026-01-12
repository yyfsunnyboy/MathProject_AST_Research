import random
# from fractions import Fraction # Not explicitly used for distance/midpoint calculations here

def generate(level=1):
    """
    生成「數線上兩點間的距離」相關題目。
    包含：
    1. 計算兩點間的距離
    2. 已知距離求未知座標
    3. 計算中點座標
    """
    problem_type = random.choice(['calculate_distance', 'find_unknown_coordinate', 'find_midpoint'])
    
    if problem_type == 'calculate_distance':
        return generate_calculate_distance_problem()
    elif problem_type == 'find_unknown_coordinate':
        return generate_find_unknown_coordinate_problem()
    else: # 'find_midpoint'
        return generate_find_midpoint_problem()

def generate_calculate_distance_problem():
    """
    題型: 數線上有 A ( x1 )、B ( x2 ) 兩點，則 A、B 兩點的距離 AB 為多少？
    """
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    
    # Ensure points are distinct
    while val1 == val2:
        val2 = random.randint(-20, 20)
        
    distance = abs(val1 - val2)
    
    labels = random.sample(['A', 'B', 'C', 'D'], 2)
    label1, label2 = labels[0], labels[1]
    
    question_text = (
        f"數線上有 ${label1} ( {val1} )$、${label2} ( {val2} )$ 兩點，"
        f"則 ${label1}{label2}$ 的距離為多少？"
    )
    correct_answer = str(distance)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_unknown_coordinate_problem():
    """
    題型: 數線上有 A ( a )、B ( 5 ) 兩點，如果 AB=3，則 a 可能是多少？
    """
    fixed_coord = random.randint(-15, 15)
    dist = random.randint(3, 15) # Distance should be reasonable and positive

    labels = random.sample(['P', 'Q', 'R', 'S'], 2)
    label_unknown, label_known = labels[0], labels[1]
    
    # Calculate possible values for 'a'
    val_plus = fixed_coord + dist
    val_minus = fixed_coord - dist

    # Sort for consistent correct answer string for checking
    correct_ans_list = sorted([val_plus, val_minus])
    correct_ans_str = f"{correct_ans_list[0]},{correct_ans_list[1]}"

    question_text = (
        f"數線上有 ${label_unknown}($a$)$、${label_known}({fixed_coord})$ 兩點，"
        f"如果 ${label_unknown}{label_known} = {dist}$，則 $a$ 可能是多少？"
    )

    return {
        "question_text": question_text,
        "answer": correct_ans_str,
        "correct_answer": correct_ans_str
    }

def generate_find_midpoint_problem():
    """
    題型: 數線上有 A ( 5 )、B ( -11 )、C ( c ) 三點，若 C 為 A、B 的中點，則 c 是多少？
    """
    val_a = random.randint(-20, 20)
    
    # To get integer midpoint often, ensure the sum val_a + val_b is even.
    # This means val_a and val_b must have the same parity.
    # Generate diff as an even number, then val_b will have same parity as val_a.
    diff_magnitude = random.randint(1, 10) * 2 # Ensures an even difference, leading to integer midpoint
    
    # Occasionally, allow odd difference for half-integer midpoints.
    if random.random() < 0.2: # ~20% chance of half-integer midpoint
        diff_magnitude = random.randint(1, 10) * 2 - 1
        if diff_magnitude <= 0: diff_magnitude = 1 # Ensure positive odd diff

    # val_b can be to the left or right of val_a
    val_b = val_a + random.choice([-1, 1]) * diff_magnitude

    # Ensure val_a and val_b are distinct (diff_magnitude > 0 already ensures this)
    # This loop is mostly for safety and should rarely be hit.
    while val_a == val_b: 
        val_b = val_a + random.choice([-1, 1]) * diff_magnitude
        
    midpoint_val = (val_a + val_b) / 2.0 # Use 2.0 to ensure float division

    # Format midpoint for display
    if midpoint_val.is_integer():
        midpoint_str = str(int(midpoint_val))
    else:
        midpoint_str = str(midpoint_val)
        
    labels = random.sample(['A', 'B', 'C', 'D'], 3)
    label_a, label_b, label_midpoint = labels[0], labels[1], labels[2]
        
    question_text = (
        f"數線上有 ${label_a} ( {val_a} )$、${label_b} ( {val_b} )$ 兩點，"
        f"若 ${label_midpoint}$ 為 ${label_a}$、${label_b}$ 的中點，則 ${label_midpoint}$ 的座標是多少？"
    )
    correct_answer = midpoint_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援單一數值或逗號分隔的多個數值答案 (例如 "2,8")。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Handle multiple answers (e.g., "2,8" or "8,2")
    if ',' in correct_answer:
        try:
            correct_parts = sorted([float(x) for x in correct_answer.split(',')])
            user_parts = sorted([float(x) for x in user_answer.split(',')])
            if correct_parts == user_parts:
                is_correct = True
        except ValueError:
            # If parsing fails, it's not a valid multiple numeric answer
            pass
    else:
        # Handle single numeric answer
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            # If parsing fails, it's not a valid numeric answer
            pass

    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}