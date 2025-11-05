# skills/rational_eq_solve.py
import random

def generate(level=1):
    """
    生成一道「分式方程式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 構造題目: a/(x-r1) + b/(x-r2) = 0
    # 確保有解且解不為增根
    r1 = random.randint(-5, 5)
    r2 = random.randint(-5, 5)
    while r1 == r2: r2 = random.randint(-5, 5)

    a = random.randint(1, 5)
    b = random.randint(1, 5)

    # a(x-r2) + b(x-r1) = 0
    # (a+b)x - (a*r2 + b*r1) = 0
    # x = (a*r2 + b*r1) / (a+b)
    
    # 為了讓解是整數，我們反向構造
    sol = random.randint(-5, 5)
    while sol == r1 or sol == r2: # 確保解不是增根
        sol = random.randint(-5, 5)

    # a(sol-r2) = -b(sol-r1)
    # a / b = -(sol-r1) / (sol-r2) = (r1-sol) / (sol-r2)
    # 我們可以設 a = r1-sol, b = sol-r2
    a = r1 - sol
    b = sol - r2
    if a == 0 or b == 0: return generate() # 避免係數為0，重新生成

    # 格式化題目
    term1 = f"{a}/(x {'-' if r1 > 0 else '+'} {abs(r1)})" if r1 != 0 else f"{a}/x"
    term2 = f"{b}/(x {'-' if r2 > 0 else '+'} {abs(r2)})" if r2 != 0 else f"{b}/x"

    question_text = f"請求解分式方程式： {term1} + {term2} = 0\n\n(注意：需檢查解是否為增根)"
    correct_answer = str(sol)
    context_string = f"解分式方程式 {term1} + {term2} = 0"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的解是否正確"""
    user = user_answer.strip()
    correct = correct_answer.strip()
    if user == correct:
        return {"correct": True, "result": f"完全正確！答案是 x = {correct}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：x = {correct}"}