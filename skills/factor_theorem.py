# skills/factor_theorem.py
import random
import numpy as np

def poly_to_string(p):
    """將 numpy.poly1d 物件轉換為字串"""
    terms = []
    for i, c in enumerate(p.coeffs):
        power = p.order - i
        if np.isclose(c, 0): continue
        c = int(c) if np.isclose(c, round(c)) else c
        if c == 1 and power != 0: coeff_str = ""
        elif c == -1 and power != 0: coeff_str = "-"
        else: coeff_str = str(c)
        if power == 0: var_str = ""
        elif power == 1: var_str = "x"
        else: var_str = f"x{ {2:'²', 3:'³', 4:'⁴'}.get(power, f'^{power}') }"
        terms.append(f"{coeff_str}{var_str if power > 0 else ''}")
    if not terms: return "0"
    return " + ".join(terms).replace("+ -", "- ").lstrip("+ ")

def generate():
    """
    生成一道「因式定理」題目
    """
    is_factor = random.choice([True, False])
    
    # 生成除式 ax - b
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)
    divisor_str = f"{a}x - {b}" if b > 0 else f"{a}x + {abs(b)}"
    root = b/a

    # 生成多項式 f(x)
    if is_factor:
        # 構造一個以 (ax-b) 為因式的多項式
        other_factor_coeffs = [random.randint(-3, 3) for _ in range(2)]
        f = np.poly1d([a, -b]) * np.poly1d(other_factor_coeffs)
        correct_answer = "是"
    else:
        # 構造一個不以 (ax-b) 為因式的多項式
        coeffs = [random.randint(-5, 5) for _ in range(random.randint(3, 4))]
        f = np.poly1d(coeffs)
        while np.isclose(f(root), 0): # 確保 f(root) 不為 0
            coeffs[-1] += random.randint(1, 5)
            f = np.poly1d(coeffs)
        correct_answer = "否"

    question_text = f"請問 {divisor_str} 是否為多項式 f(x) = {poly_to_string(f)} 的因式？ (請回答 '是' 或 '否')"
    context_string = f"使用因式定理判斷 {divisor_str} 是否為 f(x) = {poly_to_string(f)} 的因式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的是/否是否正確"""
    user = user_answer.strip().lower()
    user_choice = '是' if user in ['是', 'yes', 'y', 'true', 't'] else '否' if user in ['否', 'no', 'n', 'false', 'f'] else None
    if user_choice is None: return {"correct": False, "result": "請回答 '是' 或 '否'。"}
    if user_choice == correct_answer: return {"correct": True, "result": f"完全正確！答案是「{correct_answer}」。"}
    else: return {"correct": False, "result": f"答案不正確。正確答案是「{correct_answer}」。"}