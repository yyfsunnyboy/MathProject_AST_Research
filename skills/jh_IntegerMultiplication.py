import random
from fractions import Fraction

def format_num(num):
    """
    Formats an integer for display in LaTeX, adding parentheses if it's negative.
    Examples: 5 -> "5", -8 -> "(-8)"
    """
    return f"({num})" if num < 0 else str(num)

def generate_two_integers_problem():
    """
    Generates a basic multiplication problem with two integers.
    e.g., 7 x 6, 8 x (-9), (-6) x 8, (-4) x (-8)
    """
    # Generate two integers with absolute values between 1 and 12
    a_abs = random.randint(1, 12)
    b_abs = random.randint(1, 12)
    
    # Randomly assign signs
    a = random.choice([-1, 1]) * a_abs
    b = random.choice([-1, 1]) * b_abs
    
    # Construct the question string using format_num for proper LaTeX display
    question_text = f"計算下列各式的值：<br>$ {format_num(a)} \\times {format_num(b)} $"
    
    # Calculate the correct answer
    correct_answer = str(a * b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # The expected answer for user input
        "correct_answer": correct_answer # The canonical correct answer
    }

def generate_multiple_integers_problem(level=1):
    """
    Generates a multiplication problem with 3 or 4 integers,
    potentially including terms that simplify to powers of 10.
    e.g., (-5) x (-129) x (-2), (-231) x (-125) x 8
    """
    num_terms = random.choice([3, 4]) # Number of terms in the multiplication
    terms_abs = [] # Absolute values of the terms
    
    max_abs_val_for_other = 20 if level > 1 else 15 # Max range for non-special numbers
    
    # Introduce 'smart' grouping (e.g., 2*5, 4*25, 8*125) at higher probability for higher levels
    # This reflects the "應用乘法交換律與結合律簡化計算" aspect.
    if random.random() < (0.7 + level * 0.1) and level > 0:
        group_type = random.choice([10, 100, 1000])
        if group_type == 10: # (2, 5)
            terms_abs.extend([2, 5])
        elif group_type == 100: # (4, 25)
            terms_abs.extend([4, 25])
        else: # (8, 125)
            terms_abs.extend([8, 125])
        
        # Add remaining terms with random absolute values
        remaining_terms_count = num_terms - len(terms_abs)
        for _ in range(remaining_terms_count):
            terms_abs.append(random.randint(2, max_abs_val_for_other))
    else: # Generate completely random terms
        for _ in range(num_terms):
            terms_abs.append(random.randint(2, max_abs_val_for_other + 5))
            
    # Shuffle the absolute terms and assign signs
    random.shuffle(terms_abs)
    
    final_terms = []
    product = 1
    
    for term_abs in terms_abs:
        # Assign sign (50% chance for negative)
        sign = random.choice([-1, 1])
        term = sign * term_abs
        final_terms.append(term)
        product *= term
        
    # Construct the question string
    question_parts = [format_num(t) for t in final_terms]
    question_text = f"計算下列各式的值：<br>$ {' \\times '.join(question_parts)} $"
    correct_answer = str(product)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_special_case_problem():
    """
    Generates multiplication problems involving 0, 1, or -1.
    e.g., (-7) x 0, 1 x 15, (-1) x (-20)
    """
    case_type = random.choice(['zero', 'one', 'negative_one'])
    
    # Generate another number to multiply with the special number
    other_num_abs = random.randint(5, 100)
    other_num = random.choice([-1, 1]) * other_num_abs
    
    if case_type == 'zero':
        special_num = 0
    elif case_type == 'one':
        special_num = 1
    else: # negative_one
        special_num = -1
        
    # Randomly determine the order of the two numbers
    if random.random() < 0.5:
        a, b = special_num, other_num
    else:
        a, b = other_num, special_num
        
    question_text = f"計算下列各式的值：<br>$ {format_num(a)} \\times {format_num(b)} $"
    correct_answer = str(a * b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成正負整數乘法運算題目。
    根據 `level` 參數，調整題目的難度或類型分佈。
    """
    # Randomly choose a problem category based on the level.
    # For level 1, all types are equally likely. Higher levels might favor more complex types.
    problem_category = random.choice(['two_integers', 'multiple_integers', 'special_case'])
    
    if problem_category == 'two_integers':
        return generate_two_integers_problem()
    elif problem_category == 'multiple_integers':
        return generate_multiple_integers_problem(level)
    else: # special_case
        return generate_special_case_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    # Clean the user's answer: strip whitespace, handle unicode minus sign
    user_answer_cleaned = user_answer.strip().replace(" ", "").replace("−", "-")
    correct_answer_cleaned = correct_answer.strip().replace(" ", "").replace("−", "-")
    
    is_correct = False
    result_text = ""

    # First, try exact string comparison
    if user_answer_cleaned == correct_answer_cleaned:
        is_correct = True
    else:
        # If not an exact string match, try numeric comparison
        try:
            # Convert to float for robust comparison (e.g., "5.0" vs "5")
            if float(user_answer_cleaned) == float(correct_answer_cleaned):
                is_correct = True
        except ValueError:
            # If conversion fails (e.g., user enters non-numeric text), it's not a match
            pass
            
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_cleaned}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_cleaned}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}