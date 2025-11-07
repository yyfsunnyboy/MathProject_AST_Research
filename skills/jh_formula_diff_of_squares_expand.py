# skills/jh_formula_diff_of_squares_expand.py
import random

def generate(level=1):
    """
    生成一道「平方差」展開題目。
    (a+b)(a-b) = a² - b²
    """
    # 隨機生成 a 和 b
    a = random.randint(1, 9)
    b = random.randint(1, 9)

    # 處理 a=1 的情況
    if a == 1:
        question_text = f"請展開 (x + {b})(x - {b})"
        # 答案: x² - b²
        correct_answer = f"x^2-{b**2}"
    else:
        question_text = f"請展開 ({a}x + {b})({a}x - {b})"
        # 答案: (a²)*x² - b²
        correct_answer = f"{a**2}x^2-{b**2}"

    context_string = f"使用平方差公式 (a+b)(a-b) = a² - b² 展開題目。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的展開式是否正確。
    """
    user = user_answer.strip().replace(" ", "").replace("**", "^")
    correct = correct_answer.strip().replace(" ", "")

    if user == correct:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer.replace('^2', '²')}。", "next_question": True}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer.replace('^2', '²')}", "next_question": False}