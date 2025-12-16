import random
import math
from fractions import Fraction

def binomial_pmf(n, k, p):
    """
    Calculates the probability mass function (PMF) for a binomial distribution.
    P(X=k) = C(n, k) * p^k * (1-p)^(n-k)
    
    Args:
        n (int): Number of trials.
        k (int): Number of successful trials.
        p (Fraction): Probability of success on a single trial.
        
    Returns:
        Fraction: The probability P(X=k). Returns Fraction(0) if k is out of range.
    """
    if not (0 <= k <= n):
        return Fraction(0)
    
    # Calculate combinations C(n, k)
    combinations = math.comb(n, k)
    
    # Calculate p^k
    p_k = p**k
    
    # Calculate (1-p)^(n-k)
    q = Fraction(1) - p
    q_n_minus_k = q**(n - k)
    
    return combinations * p_k * q_n_minus_k

def generate_exact_prob_problem(level):
    """
    Generates a problem asking for the exact probability P(X=k) for a binomial distribution.
    """
    # Determine n (number of trials)
    n = random.randint(4, 7 + level * 2) # n increases with level
    
    # Generate scenario and determine p (probability of success)
    scenario_type = random.choice(['coin', 'dice', 'mcq', 'bag'])
    
    question_parts = []
    success_event = ""
    p = Fraction(0) # Initialize p
    
    if scenario_type == 'coin':
        question_parts.append(f"丟一枚均勻硬幣 ${n}$ 次，")
        success_event = "出現正面"
        p = Fraction(1, 2)
        
    elif scenario_type == 'dice':
        target_number = random.randint(1, 6)
        question_parts.append(f"丟擲一個公正骰子 ${n}$ 次，")
        success_event = f"出現數字 ${target_number}$"
        p = Fraction(1, 6)
        
    elif scenario_type == 'mcq':
        num_options = random.choice([3, 4, 5])
        question_parts.append(f"有 ${n}$ 題 ${num_options}$ 選 ${1}$ 的單選題，某生每題皆隨意選擇一個選項作答。")
        success_event = "答對"
        p = Fraction(1, num_options)
        
    else: # 'bag' (drawing with replacement)
        total_balls = random.randint(3, 8)
        favorable_balls = random.randint(1, total_balls - 1) # Ensure p is between 0 and 1
            
        color_favorable = random.choice(["紅", "藍", "綠"])
        color_other = random.choice(["白", "黑", "黃"])
        while color_other == color_favorable: # Ensure distinct colors
            color_other = random.choice(["白", "黑", "黃"])

        question_parts.append(f"袋中有大小相同的{color_favorable}球 ${favorable_balls}$ 顆、{color_other}球 ${total_balls - favorable_balls}$ 顆。每次從袋中取出一球，觀察顏色後再放回袋中，共取球 ${n}$ 次。")
        success_event = f"取到{color_favorable}球"
        p = Fraction(favorable_balls, total_balls)
    
    # Determine k (number of successes)
    k = random.randint(0, n)
    
    # Calculate probability
    correct_prob = binomial_pmf(n, k, p)
    
    question_text = f"{''.join(question_parts)} 求恰 {success_event} ${k}$ 次的機率。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_prob),
        "correct_answer": str(correct_prob)
    }

def generate_cumulative_prob_problem(level):
    """
    Generates a problem asking for a cumulative probability (P(X<=k), P(X>=k), etc.)
    for a binomial distribution.
    """
    n = random.randint(4, 7 + level)
    
    scenario_type = random.choice(['coin', 'dice', 'mcq', 'bag'])
    
    question_parts = []
    success_event = ""
    p = Fraction(0) # Initialize p
    
    if scenario_type == 'coin':
        question_parts.append(f"丟一枚均勻硬幣 ${n}$ 次，")
        success_event = "出現正面"
        p = Fraction(1, 2)
        
    elif scenario_type == 'dice':
        target_number = random.randint(1, 6)
        question_parts.append(f"丟擲一個公正骰子 ${n}$ 次，")
        success_event = f"出現數字 ${target_number}$"
        p = Fraction(1, 6)
        
    elif scenario_type == 'mcq':
        num_options = random.choice([3, 4])
        question_parts.append(f"有 ${n}$ 題 ${num_options}$ 選 ${1}$ 的單選題，某生每題皆隨意選擇一個選項作答。")
        success_event = "答對"
        p = Fraction(1, num_options)
        
    else: # 'bag' (drawing with replacement)
        total_balls = random.randint(3, 8)
        favorable_balls = random.randint(1, total_balls - 1)
        
        color_favorable = random.choice(["紅", "藍", "綠"])
        color_other = random.choice(["白", "黑", "黃"])
        while color_other == color_favorable:
            color_other = random.choice(["白", "黑", "黃"])

        question_parts.append(f"袋中有大小相同的{color_favorable}球 ${favorable_balls}$ 顆、{color_other}球 ${total_balls - favorable_balls}$ 顆。每次從袋中取出一球，觀察顏色後再放回袋中，共取球 ${n}$ 次。")
        success_event = f"取到{color_favorable}球"
        p = Fraction(favorable_balls, total_balls)
        
    correct_prob = Fraction(0)
    comparison_type = random.choice(['at_most', 'at_least', 'less_than', 'more_than'])
    
    k_limit_value = 0 # This will be the value for comparison in the question (e.g., 'at most K')

    if comparison_type == 'at_most':
        k_limit_value = random.randint(0, n)
        question_phrase = f"至多 {success_event} ${k_limit_value}$ 次"
        for i in range(k_limit_value + 1):
            correct_prob += binomial_pmf(n, i, p)
    elif comparison_type == 'at_least':
        k_limit_value = random.randint(0, n)
        question_phrase = f"至少 {success_event} ${k_limit_value}$ 次"
        for i in range(k_limit_value, n + 1):
            correct_prob += binomial_pmf(n, i, p)
    elif comparison_type == 'less_than':
        # P(X < k_limit_value), so k_limit_value must be at least 1 to be non-trivial
        k_limit_value = random.randint(1, n)
        question_phrase = f"少於 {success_event} ${k_limit_value}$ 次"
        for i in range(k_limit_value): # Sum from 0 to k_limit_value - 1
            correct_prob += binomial_pmf(n, i, p)
    else: # 'more_than'
        # P(X > k_limit_value), so k_limit_value must be at most n-1 to be non-trivial
        k_limit_value = random.randint(0, n - 1)
        question_phrase = f"多於 {success_event} ${k_limit_value}$ 次"
        for i in range(k_limit_value + 1, n + 1): # Sum from k_limit_value + 1 to n
            correct_prob += binomial_pmf(n, i, p)

    question_text = f"{''.join(question_parts)} 求 {question_phrase} 的機率。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_prob),
        "correct_answer": str(correct_prob)
    }

def generate(level=1):
    """
    Generates a binomial distribution problem based on the specified level.
    """
    problem_type = random.choice(['exact_prob', 'cumulative_prob'])
    
    if problem_type == 'exact_prob':
        return generate_exact_prob_problem(level)
    else: # cumulative_prob
        return generate_cumulative_prob_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, handling fraction input.
    """
    try:
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        
        is_correct = (user_fraction == correct_fraction)
        
        result_text = ""
        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
        return {"correct": is_correct, "result": result_text, "next_question": True}
        
    except ValueError:
        # User might have entered a non-fraction or invalid input
        result_text = f"您的輸入格式不正確，請以分數形式（如 '1/2'）或整數形式輸入。<br>正確答案應為：${correct_answer}$"
        return {"correct": False, "result": result_text, "next_question": False}