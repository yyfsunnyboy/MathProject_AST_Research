# skills/remainder.py
import random

def format_term(coeff, power):
    """格式化單一項：如 4x^3 → + 4x³，-3x → - 3x"""
    if coeff == 0:
        return ""
    if coeff == 1 and power > 0:
        return " + x" if power == 1 else f" + x²" if power == 2 else f" + x³"
    if coeff == -1 and power > 0:
        return " - x" if power == 1 else f" - x²" if power == 2 else f" - x³"
    sign = " + " if coeff > 0 else " - "
    abs_coeff = abs(coeff)
    var = "" if power == 0 else ("x" if power == 1 else f"x²" if power == 2 else f"x³")
    return f"{sign}{abs_coeff}{var}"

def generate():
    # 隨機係數
    a = random.randint(1, 5)                    # 3次項 ≥1
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    d = random.randint(-10, 10)

    k = random.randint(-3, 3)
    while k == 0:
        k = random.randint(-3, 3)

    # 計算正確答案 f(k)
    answer = a * (k**3) + b * (k**2) + c * k + d

    # 組裝 f(x) = ax³ + bx² + cx + d 格式
    terms = [
        format_term(a, 3),
        format_term(b, 2),
        format_term(c, 1),
        format_term(d, 0)
    ]
    poly_text = "".join(terms).lstrip(" + ").strip()  # 移除開頭多餘 + 
    if poly_text.startswith("-"):
        poly_text = "-" + poly_text.lstrip("-").strip()  # 確保負號正確

    # 除式
    divisor = f"x - {k}" if k >= 0 else f"x + {abs(k)}"

    # 題目文字
    question_text = (
        f"用餘式定理求：\n"
        f"多項式 f(x) = {poly_text}\n"
        f"被 {divisor} 除的餘數"
    )

    # 給 AI 的 context
    context_string = f"用餘式定理求 f({k})，其中 f(x) = {poly_text}"

    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": "text",
        "context_string": context_string,
        "poly_text": poly_text  # 與 factor_theorem.py 一致！
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    return {
        "correct": user == correct,
        "result": f"正確！餘數是 {correct}" if user == correct else f"錯誤，正確答案：{correct}",
        "next_question": True
    }