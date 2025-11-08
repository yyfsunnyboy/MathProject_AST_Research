import random

def generate(level=1):
    """
    生成一道「反導函數 (多項式)」的題目。
    """
    if level == 1:
        n = random.randint(1, 5)
        question_text = f"請求出 f(x) = x^{n} 的一個反導函數 F(x)。\n(不需寫常數 C)"
        correct_answer = f"(1/{n+1})x^{n+1}"
    else: # level 2
        a, n = random.randint(2, 5), random.randint(2, 5)
        b, m = random.randint(2, 5), random.randint(1, n-1)
        question_text = f"請求出 f(x) = {a}x^{n} + {b}x^{m} 的一個反導函數 F(x)。\n(不需寫常數 C)"
        correct_answer = f"({a}/{n+1})x^{n+1}+({b}/{m+1})x^{m+1}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("**","^")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}