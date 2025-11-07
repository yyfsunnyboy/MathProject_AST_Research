# skills/jh_poly_ops_multiply_mono.py
import random
import numpy as np

def poly_to_string(p_coeffs):
    """將係數列表轉換為多項式字串"""
    p = np.poly1d(p_coeffs)
    terms = []
    for i, c in enumerate(p.coeffs):
        power = p.order - i
        if np.isclose(c, 0): continue
        c = int(round(c))
        if c == 1 and power != 0: coeff_str = ""
        elif c == -1 and power != 0: coeff_str = "-"
        else: coeff_str = str(c)
        if power == 0: var_str = str(abs(c))
        elif power == 1: var_str = f"{coeff_str}x"
        else: var_str = f"{coeff_str}x²"
        if power == 0: terms.append(str(c))
        else: terms.append(var_str)
    if not terms: return "0"
    return " + ".join(terms).replace("+ -", "- ").replace("1x", "x").lstrip(" +")

def generate(level=1):
    """生成多項式乘以單項式題目 (圖形題)"""
    poly_coeffs = [random.randint(-5, 5) for _ in range(random.randint(2, 3))]
    mono_coeff = random.randint(-5, 5)
    while mono_coeff == 0: mono_coeff = random.randint(-5, 5)
    mono_power = random.randint(1, 2)
    
    poly_str = f"({poly_to_string(poly_coeffs)})"
    mono_str = f"({mono_coeff}x)" if mono_power == 1 else f"({mono_coeff}x²)"

    question_text = f"請在下方的「數位計算紙」上，計算 {poly_str} × {mono_str} 的結果。\n\n完成後，請點擊「AI 檢查」按鈕。"
    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"計算 {poly_str} 乘以 {mono_str}"
    }

def check(user_answer, correct_answer):
    return {"correct": False, "result": "請在數位計算紙上寫下您的計算過程，然後點選「AI 檢查」。", "next_question": False}