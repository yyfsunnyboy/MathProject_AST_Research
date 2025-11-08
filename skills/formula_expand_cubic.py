import random

def generate(level=1):
    """
    生成一道「立方和/差公式展開」的題目。
    (a+b)(a^2-ab+b^2) = a^3+b^3
    (a-b)(a^2+ab+b^2) = a^3-b^3
    level 1: a=x, b 為整數
    level 2: a=kx, b 為整數, k > 1
    """
    is_sum = random.choice([True, False])
    b = random.randint(2, 5)

    if level == 1:
        k = 1
        a_term = "x"
    else: # level 2
        k = random.randint(2, 4)
        a_term = f"{k}x"

    a_sq = k*k
    ab = k*b
    b_sq = b*b
    
    a_cub = k*k*k
    b_cub = b*b*b

    if is_sum:
        # (a+b)(a^2-ab+b^2)
        question_text = f"請展開並化簡： ({a_term} + {b})({a_sq}x^2 - {ab}x + {b_sq})"
        correct_answer = f"{a_cub}x^3+{b_cub}"
    else:
        # (a-b)(a^2+ab+b^2)
        question_text = f"請展開並化簡： ({a_term} - {b})({a_sq}x^2 + {ab}x + {b_sq})"
        correct_answer = f"{a_cub}x^3-{b_cub}"

    context_string = f"練習立方和/差的乘法公式展開。題目：{question_text}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
        "standard_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }