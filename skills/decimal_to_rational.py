import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「小數化分數」的題目。
    level 1: 有限小數。
    level 2: 循環小數 (目前簡化為有限小數)。
    """
    if level == 1:
        # Level 1: 有限小數
        decimal_places = random.choice([1, 2])
        if decimal_places == 1:
            num = random.randint(1, 99) / 10.0
        else:
            num = random.randint(1, 399) / 100.0
        
        question_text = f"請將小數 {num} 化為最簡分數。（格式：a/b）"
        frac = Fraction(num).limit_denominator()
        correct_answer = f"{frac.numerator}/{frac.denominator}"

    else:
        # Level 2: 為了簡化，暫時也使用有限小數，但位數更多
        decimal_places = random.choice([2, 3])
        if decimal_places == 2:
            num = random.randint(101, 599) / 100.0
        else:
            num = random.randint(1001, 9999) / 1000.0
        
        question_text = f"請將小數 {num} 化為最簡分數。（格式：a/b）"
        frac = Fraction(num).limit_denominator()
        correct_answer = f"{frac.numerator}/{frac.denominator}"

    context_string = f"學習小數與分數的互換。題目：將 {num} 化為最簡分數。"

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
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }