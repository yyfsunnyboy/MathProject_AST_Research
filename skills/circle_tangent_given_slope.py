import random
import math

def generate(level=1):
    """
    生成一道「給定斜率求圓的切線方程式」的題目。
    level 1: 圓心在原點，斜率為整數。
    level 2: 圓心不在原點。
    """
    r = random.randint(2, 5)
    m = random.choice([-2, -1, 1, 2])

    if level == 1:
        h, k = 0, 0
        circle_eq = f"x² + y² = {r**2}"
        # y = mx ± r√(m²+1)
        k_part = r * math.sqrt(m**2 + 1)
        k_part_int = int(k_part)
        if k_part != k_part_int: return generate(level) # 確保 k 是整數
        correct_answer = f"y = {m}x ± {k_part_int}".replace("1x","x")
    else: # level 2
        h, k = random.randint(-3, 3), random.randint(-3, 3)
        circle_eq = f"(x-{h})² + (y-{k})² = {r**2}"
        # y-k = m(x-h) ± r√(m²+1)
        k_part = r * math.sqrt(m**2 + 1)
        k_part_int = int(k_part)
        if k_part != k_part_int: return generate(level) # 確保 k 是整數
        correct_answer = f"y - {k} = {m}(x - {h}) ± {k_part_int}"

    question_text = f"請求出圓 C: {circle_eq} 且斜率為 {m} 的所有切線方程式。"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower().replace("+-","±")
    correct = str(correct_answer).strip().replace(" ", "").lower().replace("+-","±")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}