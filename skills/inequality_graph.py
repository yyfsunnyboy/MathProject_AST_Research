import random
from core.helpers import format_linear_equation_lhs

def generate_inequality_region_question():
    """動態生成一道「圖示不等式解區域」的題目。"""
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 and b == 0:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    while c == 0:
        c = random.randint(-9, 9)
    sign = random.choice(['>', '<', '>=', '<='])
    inequality_lhs = format_linear_equation_lhs(a, b)
    c_str = ""
    if c > 0:
        c_str = f" + {c}"
    elif c < 0:
        c_str = f" - {abs(c)}"
    inequality_expression = f"{inequality_lhs}{c_str}"
    full_inequality_string = f"{inequality_expression} {sign} 0"
    question_text = (
        f"請在下方的「數位計算紙」上，圖示二元一次不等式：\n\n"
        f"    {full_inequality_string}\n\n"
        f"畫完後，請點擊「AI 檢查計算」按鈕。"
    )
    return {
        "text": question_text,
        "answer": None,
        "validation_function_name": None,
        "inequality_string": full_inequality_string
    }
