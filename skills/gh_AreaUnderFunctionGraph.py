import random
from fractions import Fraction

def generate(level=1):
    """
    生成「函數圖形下面積」相關題目。
    包含：
    1. 線性函數在 [0, 1] 上的面積 (黎曼和與梯形面積驗證)
    2. 線性函數在 [0, b] 上的面積 (黎曼和與三角形面積驗證)
    """
    problem_type = random.choice(['linear_0_1', 'linear_0_b'])
    
    if problem_type == 'linear_0_1':
        return generate_linear_on_0_1_problem(level)
    else: # 'linear_0_b'
        return generate_linear_on_0_b_problem(level)

def generate_linear_on_0_1_problem(level):
    """
    生成 f(x) = ax + b 在 [0, 1] 上的面積題目。
    """
    # Ensure a > 0 for monotonically increasing function on [0,1]
    # This simplifies upper/lower sum logic if we were to derive them explicitly,
    # though for level 1 we just ask for the area.
    a = random.randint(1, 4)
    b = random.randint(1, 5)

    # Area calculation:
    # f(0) = b
    # f(1) = a + b
    # Area of trapezoid = (f(0) + f(1)) * height / 2 = (b + (a + b)) * 1 / 2 = (a + 2b) / 2
    numerator = a + 2 * b
    denominator = 2
    
    # Correct answer as a Fraction for precise comparison
    correct_area = Fraction(numerator, denominator)

    question_text = (
        f"設函數 $f(x) = {a}x + {b}$ 的圖形與 $x$ 軸、 $x=0$ 及 $x=1$ 所圍成的區域為 $R$。<br>"
        r"(1) 請利用黎曼和 (或上和/下和的極限) 的概念計算此區域 $R$ 的面積。<br>"
        r"(2) 此區域 $R$ 為何種幾何圖形？請利用其面積公式驗證(1)的結果。<br>"
        r"(請回答面積的數值，若為分數請填寫最簡分數，例如 $\\frac{{3}}{{2}}$)"
    )
    
    # If level is higher, we could ask for U_n or L_n expressions
    # For now, just the final area.
    
    return {
        "question_text": question_text,
        "answer": str(correct_area), # Storing as string "numerator/denominator"
        "correct_answer": str(correct_area)
    }

def generate_linear_on_0_b_problem(level):
    """
    生成 f(x) = ax 在 [0, B] 上的面積題目 (三角形)。
    """
    a = random.randint(1, 3)
    B_val = random.randint(2, 6) # Using B_val to avoid conflict with 'b' coefficient if used

    # Area calculation:
    # This forms a triangle with base B_val and height f(B_val) = a * B_val
    # Area = base * height / 2 = (B_val * a * B_val) / 2 = (a * B_val**2) / 2
    numerator = a * B_val**2
    denominator = 2

    correct_area = Fraction(numerator, denominator)

    question_text = (
        f"設函數 $f(x) = {a}x$ 的圖形與 $x$ 軸、 $x=0$ 及 $x={B_val}$ 所圍成的區域為 $R$。<br>"
        r"(1) 請利用黎曼和 (例如取右端點 $c_k = x_k = \\frac{{kB}}{{\text{{n}}}}$) 的概念計算此區域 $R$ 的面積。<br>"
        r"(2) 此區域 $R$ 為何種幾何圖形？請利用其面積公式驗證(1)的結果。<br>"
        r"(請回答面積的數值，若為分數請填寫最簡分數，例如 $\\frac{{3}}{{2}}$)"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_area),
        "correct_answer": str(correct_area)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 和 correct_answer 預期為分數形式的字串 (e.g., "3/2" 或 "2")。
    """
    try:
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        
        is_correct = (user_fraction == correct_fraction)
        
        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
        return {"correct": is_correct, "result": result_text, "next_question": True}

    except ValueError:
        return {"correct": False, "result": "請輸入有效的數字或分數形式。", "next_question": False}