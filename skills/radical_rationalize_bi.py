import random

def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

def generate(level=1):
    """
    生成一道「雙項分母有理化」的題目。
    level 1: 分母為 √a ± √b
    level 2: 分母為 c ± √b 或 √a ± d
    """
    if level == 1:
        a = random.choice([2, 3, 5, 7])
        b = random.choice([2, 3, 5, 7])
        while a == b: b = random.choice([2, 3, 5, 7])
        op = random.choice(['+', '-'])
        num = random.randint(1, 5) * (a - b) # 讓分子可以約分
        question_text = f"請將 {num}/(√{a} {op} √{b}) 的分母有理化。"
        
        den_final = a - b
        if op == '+': # 乘以 √a - √b
            num_final_coeff = num
            num_final_term = f"(√{a}-√{b})"
        else: # 乘以 √a + √b
            num_final_coeff = num
            num_final_term = f"(√{a}+√{b})"
        
        common_divisor = gcd(num_final_coeff, den_final)
        num_final_coeff //= common_divisor
        den_final //= common_divisor
        
        if den_final == 1: correct_answer = f"{num_final_coeff}{num_final_term}"
        elif den_final == -1: correct_answer = f"{-num_final_coeff}{num_final_term}"
        else: correct_answer = f"({num_final_coeff}{num_final_term})/{den_final}"
    else: # level 2 is similar, just one term is integer
        a = random.choice([2, 3, 5, 7])
        d = random.randint(2, 5)
        op = random.choice(['+', '-'])
        num = random.randint(1, 3) * (d*d - a) # 讓分子可以約分
        question_text = f"請將 {num}/({d} {op} √{a}) 的分母有理化。"
        den_final = d*d - a
        
        if op == '+': # 乘以 d - √a
            num_final_coeff = num
            num_final_term = f"({d}-√{a})"
        else: # 乘以 d + √a
            num_final_coeff = num
            num_final_term = f"({d}+√{a})"
            
        common_divisor = gcd(num_final_coeff, den_final)
        num_final_coeff //= common_divisor
        den_final //= common_divisor
        
        if den_final == 1: correct_answer = f"{num_final_coeff}{num_final_term}"
        elif den_final == -1: correct_answer = f"{-num_final_coeff}{num_final_term}"
        else: correct_answer = f"({num_final_coeff}{num_final_term})/{den_final}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}