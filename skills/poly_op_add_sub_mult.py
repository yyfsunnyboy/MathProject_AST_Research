# skills/poly_op_add_sub_mult.py
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

def generate(level=1):
    """
    生成一道「多項式的四則運算 (加減乘)」題目 (圖形題)
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成兩個多項式
    f_coeffs = [random.randint(-3, 3) for _ in range(random.randint(2, 3))]
    g_coeffs = [random.randint(-2, 2) for _ in range(random.randint(2, 3))]
    f = np.poly1d(f_coeffs)
    g = np.poly1d(g_coeffs)

    op = random.choice(['+', '-', '*'])
    
    f_str = f"({poly_to_string(f)})"
    g_str = f"({poly_to_string(g)})"

    question_text = f"請在下方的「數位計算紙」上，計算 {f_str} {op} {g_str} 的結果。\n\n完成後，請點擊「AI 檢查」按鈕。"
    context_string = f"計算 {f_str} {op} {g_str}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    return {"correct": False, "result": "請在數位計算紙上寫下您的計算過程，然後點選「AI 檢查」。"}