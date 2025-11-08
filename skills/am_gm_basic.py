import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「算幾不等式」的基本應用題。
    (a+b)/2 >= sqrt(ab)
    level 1: a, b 為整數，求最小值。
    level 2: a, b 為倒數關係，求最小值。
    """
    if level == 1:
        # a+b=k, 求 ab 最大值
        k = random.randint(4, 20) * 2 # 確保是偶數
        question_text = f"已知兩正數 x, y 滿足 x + y = {k}，求 x*y 的最大值。"
        # 最大值發生在 x=y=k/2 時
        max_val = (k/2) * (k/2)
        correct_answer = str(int(max_val))
    else: # level 2
        # 求 a*x + b/x 的最小值
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        k = random.randint(1, 4)
        
        # a*k*x + b/(k*x)
        term1 = f"{a*k}x"
        term2 = f"{b}/{k}x"
        
        question_text = f"已知 x > 0，求 {term1} + {term2} 的最小值。"
        # 最小值發生在 a*k*x = b/(k*x) => x^2 = b/(a*k^2)
        # 最小值為 2 * sqrt( (a*k*x) * (b/(k*x)) ) = 2 * sqrt(ab)
        min_val_sq = a * b
        # 為了讓答案漂亮，我們讓 ab 是完全平方數
        a = random.randint(1, 4)
        b = a * random.randint(1, 4)**2
        question_text = f"已知 x > 0，求 {a}x + {b}/x 的最小值。"
        min_val = 2 * int(a**0.5 * b**0.5)
        correct_answer = str(min_val)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}