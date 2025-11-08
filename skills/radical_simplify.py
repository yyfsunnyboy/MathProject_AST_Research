import random
import math

def simplify_radical(n):
    """輔助函式：化簡根式 sqrt(n)"""
    if n == 0:
        return 0, 1
    i = 2
    limit = int(math.sqrt(n))
    a = 1 # 根號外的係數
    b = n # 根號內的數
    while i <= limit:
        if b % (i*i) == 0:
            b = b // (i*i)
            a = a * i
            limit = int(math.sqrt(b)) # 優化：更新 limit
            continue
        i += 1
    return a, b

def generate(level=1):
    """
    生成一道「根式化簡」的題目。
    level 1: 數字較小。
    level 2: 數字較大。
    """
    if level == 1:
        # Level 1: 較小的數字
        # 從 2, 3, 5, 6, 7 中選一個當作根號內的底
        inner_base = random.choice([2, 3, 5, 6, 7])
        # 從 2, 3, 4, 5 中選一個當作提出去的係數
        outer_coeff = random.randint(2, 5)
    else:
        # Level 2: 較大的數字
        inner_base = random.choice([2, 3, 5, 6, 7, 10, 11])
        outer_coeff = random.randint(6, 12)

    num_inside = inner_base * (outer_coeff ** 2)
    
    question_text = f"請化簡根式： √{num_inside}"
    
    a, b = simplify_radical(num_inside)
    if b == 1:
        correct_answer = str(a)
    else:
        correct_answer = f"{a}√{b}"

    context_string = f"學習化簡根式。題目：化簡 √{num_inside}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
        "standard_answer": correct_answer
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }