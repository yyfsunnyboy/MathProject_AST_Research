import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「數線分點公式」的題目。
    level 1: 內分點，比例為整數。
    level 2: 外分點，比例為整數。
    """
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    while abs(a - b) < 5: # 確保兩點有足夠距離
        b = random.randint(-10, 10)
    
    m = random.randint(1, 5)
    n = random.randint(1, 5)
    while m == n:
        n = random.randint(1, 5)

    if level == 1:
        # 內分點 P = (n*a + m*b) / (m+n)
        question_text = f"數線上兩點 A({a}), B({b})，點 P 在線段 AB 上且 AP:PB = {m}:{n}，求 P 點坐標。"
        # 為了讓答案是整數，反向構造
        p = random.randint(min(a,b), max(a,b))
        m = abs(p-a)
        n = abs(b-p)
        if m==0 or n==0: return generate(level) # 重來
        question_text = f"數線上兩點 A({a}), B({b})，點 P 在線段 AB 上且 AP:PB = {m}:{n}，求 P 點坐標。"
        correct_answer = str(p)
    else: # level 2
        # 外分點 P = (-n*a + m*b) / (m-n)
        question_text = f"數線上兩點 A({a}), B({b})，點 P 在直線 AB 上（但在線段 AB 外）且 AP:PB = {m}:{n}，求 P 點坐標。"
        p_num = -n * a + m * b
        p_den = m - n
        p = Fraction(p_num, p_den)
        correct_answer = str(p.numerator) if p.denominator == 1 else f"{p.numerator}/{p.denominator}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}