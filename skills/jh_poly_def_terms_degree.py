# skills/jh_poly_def_terms_degree.py
import random

def format_poly(coeffs):
    """格式化多項式字串"""
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        power = degree - i
        if c == 0: continue
        
        # 係數
        if c == 1 and power != 0: coeff_str = ""
        elif c == -1 and power != 0: coeff_str = "-"
        else: coeff_str = str(c)
        
        # 變數
        if power == 0: var_str = ""
        elif power == 1: var_str = "x"
        else: var_str = f"x{ {2:'²', 3:'³', 4:'⁴'}.get(power, f'^{power}') }"
            
        terms.append(f"{coeff_str}{var_str}")
    
    if not terms: return "0"
    return " + ".join(terms).replace(" + -", " - ").lstrip(" + ")

def generate(level=1):
    """生成多項式基本定義題目"""
    degree = random.randint(2, 4)
    coeffs = [random.randint(-9, 9) for _ in range(degree + 1)]
    while coeffs[0] == 0: coeffs[0] = random.randint(1, 9)

    poly_str = format_poly(coeffs)
    
    q_type = random.choice(['degree', 'coeff', 'const'])

    if q_type == 'degree':
        question_text = f"請問多項式 {poly_str} 的次數是多少？"
        correct_answer = str(degree)
    elif q_type == 'coeff':
        target_power = random.randint(1, degree)
        power_str = "x" if target_power == 1 else f"x{ {2:'²', 3:'³', 4:'⁴'}.get(target_power, f'^{target_power}') }"
        question_text = f"請問多項式 {poly_str} 中，{power_str} 項的係數是多少？"
        correct_answer = str(coeffs[degree - target_power])
    else: # 'const'
        question_text = f"請問多項式 {poly_str} 的常數項是多少？"
        correct_answer = str(coeffs[-1])

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"關於多項式 {poly_str} 的基本概念"
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    if user == correct_answer:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。", "next_question": True}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}", "next_question": False}