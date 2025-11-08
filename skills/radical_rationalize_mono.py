import random
import math

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def generate(level=1):
    """
    生成一道「單項分母有理化」的題目。
    level 1: 分母為 √b，分子為整數 a。
    level 2: 分母為 c√b，分子為整數 a。
    """
    b = random.choice([2, 3, 5, 6, 7, 10])
    
    if level == 1:
        a = random.randint(1, 10)
        question_text = f"請將 {a}/√{b} 的分母有理化。"
        # a√b / b
        common_divisor = gcd(a, b)
        num = a // common_divisor
        den = b // common_divisor
        if den == 1:
            correct_answer = f"{num}√{b}"
        else:
            correct_answer = f"({num}√{b})/{den}"
    else: # level 2
        c = random.randint(2, 5)
        a = random.randint(1, 10)
        question_text = f"請將 {a}/({c}√{b}) 的分母有理化。"
        # a√b / (cb)
        den_final = c * b
        common_divisor = gcd(a, den_final)
        num = a // common_divisor
        den = den_final // common_divisor
        if den == 1:
            correct_answer = f"{num}√{b}"
        else:
            correct_answer = f"({num}√{b})/{den}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}