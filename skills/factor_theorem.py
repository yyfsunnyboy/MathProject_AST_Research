# skills/factor_theorem.py
import random

def format_polynomial(coeffs):
    """將係數轉為 f(x) = ax³ + bx² + cx + d 格式"""
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        power = degree - i
        if coeff == 1 and power > 0:
            term = "x" if power == 1 else "x³" if power == 3 else "x²"
        elif coeff == -1 and power > 0:
            term = "-x" if power == 1 else "-x³" if power == 3 else "-x²"
        else:
            sign = "" if (coeff > 0 and terms) else ("-" if coeff < 0 else "")
            abs_coeff = abs(coeff)
            term = f"{sign}{abs_coeff}x" if power == 1 else \
                   f"{sign}{abs_coeff}x³" if power == 3 else \
                   f"{sign}{abs_coeff}x²" if power == 2 else \
                   f"{sign}{abs_coeff}"
        terms.append(term)
    if not terms:
        return "0"
    return " + ".join(terms).replace("+ -", "- ").strip()

def generate():
    """生成「因式定理」題目"""
    degree = random.choice([2, 3])
    k = random.randint(-3, 3)
    coeffs = []
    is_factor = random.choice([True, False])

    if degree == 2:
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        if is_factor:
            c = -((a * (k**2)) + (b * k))
        else:
            c = random.randint(-9, 9)
            remainder = (a * (k**2)) + (b * k) + c
            while remainder == 0:
                c = random.randint(-9, 9)
                remainder = (a * (k**2)) + (b * k) + c
        coeffs = [a, b, c]
    elif degree == 3:
        a = random.randint(-2, 2)
        while a == 0:
            a = random.randint(-2, 2)
        b = random.randint(-3, 3)
        c = random.randint(-5, 5)
        if is_factor:
            d = -((a * (k**3)) + (b * (k**2)) + (c * k))
        else:
            d = random.randint(-9, 9)
            remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
            while remainder == 0:
                d = random.randint(-9, 9)
                remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
        coeffs = [a, b, c, d]

    poly_text = format_polynomial(coeffs)
    k_sign = "-" if k >= 0 else "+"
    k_abs = abs(k)
    
    # 修正 k=0 的情況：顯示為 "x" 而不是 "(x)"
    if k == 0:
        divisor_text = "x"
    else:
        divisor_text = f"(x {k_sign} {k_abs})"
    
    question_text = f"請問 {divisor_text} 是否為 f(x) = {poly_text} 的因式？ (請回答 '是' 或 '否')"
    
    # 修正 context_string：與 divisor_text 保持一致
    if k == 0:
        context_string = f"判斷 x 是否為 f(x) = {poly_text} 的因式"
    else:
        context_string = f"判斷 {divisor_text} 是否為 f(x) = {poly_text} 的因式"
    
    correct_answer = "是" if is_factor else "否"

    return {
        "question_text": question_text,
        "answer": "是" if is_factor else "否",
        "correct_answer": "text",
        "context_string": context_string
    }

def check(user_answer, correct_answer):
    if correct_answer is None:
        return {"correct": False, "result": "系統錯誤：缺少正確答案"}
    user = user_answer.strip().lower()
    correct = correct_answer.strip().lower()
    if user in ['是', 'yes', 'y']:
        user = '是'
    elif user in ['否', 'no', 'n']:
        user = '否'
    if user == correct:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}