import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「分數化小數」的題目。
    level 1: 產生有限小數或整數。分母為 2, 4, 5, 8, 10 的組合。
    level 2: 產生循環小數。分母為 3, 6, 7, 9, 11, 12。
    """
    if level == 1:
        # Level 1: 有限小數
        denominator = random.choice([2, 4, 5, 8, 10, 20, 25, 50])
        numerator = random.randint(1, denominator * 3)
        question_text = f"請將分數 {numerator}/{denominator} 化為小數。"
        # 使用 Fraction 來處理精確的除法
        correct_answer = str(Fraction(numerator, denominator))
        # 避免出現 .0 的情況
        if correct_answer.endswith('.0'):
            correct_answer = correct_answer[:-2]

    else:
        # Level 2: 循環小數 (這裡我們只要求近似值)
        denominator = random.choice([3, 6, 7, 9, 11, 12])
        numerator = random.randint(1, denominator * 2)
        question_text = f"請將分數 {numerator}/{denominator} 化為小數。（四捨五入至小數點後第三位）"
        correct_answer = str(round(numerator / denominator, 3))

    context_string = f"學習分數與小數的互換。題目：將 {numerator}/{denominator} 化為小數。"

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
    考慮到浮點數精度問題，進行比較。
    """
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()

    is_correct = False
    try:
        # 嘗試將兩者都轉換為浮點數進行比較
        if abs(float(user) - float(correct)) < 1e-9:
            is_correct = True
    except (ValueError, TypeError):
        # 如果轉換失敗，則進行字串比較
        if user == correct:
            is_correct = True

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }