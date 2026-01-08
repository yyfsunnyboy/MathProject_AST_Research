# ==============================================================================
# ID: jh_數學1上_IntegerExponentiation
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.1 Fix)
# Duration: Fixed manually
# Created At: 2026-01-08
# Fix Status: [Repaired]
# ==============================================================================

import random
import math
from fractions import Fraction

def to_latex(num):
    """Convert number to LaTeX (integers, decimals, fractions, mixed numbers)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            if rem == 0: return f"{sign}{abs(num).numerator // abs(num).denominator}"
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses"""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

# ==============================================================================
# Problem Types
# ==============================================================================

def generate_type_1_problem():
    """
    Type 1: 基礎 - 正整數與負整數的偶次方 (Basic Even Power)
    """
    b = random.randint(2, 9)
    e = 2
    ans1 = b**e
    ans2 = (-b)**e
    ans3 = -(b**e)
    
    question_text = f"計算下列各式的值。\n⑴ $\\text{{{b}}}^\\text{{{e}}}$ \n⑵ $(-\\text{{{b}}})^\\text{{{e}}}$ \n⑶ $-\\text{{{b}}}^\\text{{{e}}}$"
    correct_answer = f"⑴ {ans1} ⑵ {ans2} ⑶ {ans3}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Type 2: 基礎 - 連乘積改寫為指數形式 (Repeated Multiplication to Exponent)
    [Fix]: 修正了 \times 顯示為純文字的問題，加上了 $ 包裹。
    """
    b1 = random.randint(2, 10)
    e1 = random.randint(3, 6)
    b2 = random.randint(-10, -2)
    e2 = random.randint(3, 6)
    
    # 這裡生成的字串包含 LaTeX 語法 \times
    mul_str1 = ' \\times '.join([str(b1)] * e1)
    mul_str2 = ' \\times '.join([f"({b2})"] * e2)
    
    ans1_latex = f"{b1}^{{{e1}}}"
    ans2_latex = f"({b2})^{{{e2}}}"
    
    # [Critical Fix] 加上 $ 符號，讓 \times 正確渲染
    question_text = f"以指數的形式簡記下列各式。\n⑴ ${mul_str1} = \\_\\_\\_\\_\\_$ 。\n⑵ ${mul_str2} = \\_\\_\\_\\_\\_$ 。"
    correct_answer = f"⑴ ${ans1_latex}$ ⑵ ${ans2_latex}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Type 3: 基礎 - 偶次方計算 (Fixed e=4)
    """
    b = random.randint(2, 5)
    e = 4
    ans1 = b**e
    ans2 = (-b)**e
    ans3 = -(b**e)
    
    question_text = f"計算下列各式的值。\n⑴ $\\text{{{b}}}^\\text{{{e}}}$ \n⑵ $(-\\text{{{b}}})^\\text{{{e}}}$ \n⑶ $-\\text{{{b}}}^\\text{{{e}}}$"
    correct_answer = f"⑴ {ans1} ⑵ {ans2} ⑶ {ans3}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Type 4: 基礎 - 奇次方計算 (Fixed e=3)
    """
    b = random.randint(2, 6)
    e = 3
    ans1 = b**e
    ans2 = (-b)**e
    ans3 = -(b**e)
    
    question_text = f"計算下列各式的值。\n⑴ $\\text{{{b}}}^\\text{{{e}}}$ \n⑵ $(-\\text{{{b}}})^\\text{{{e}}}$ \n⑶ $-\\text{{{b}}}^\\text{{{e}}}$"
    correct_answer = f"⑴ {ans1} ⑵ {ans2} ⑶ {ans3}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Type 5: 基礎 - 奇次方計算 (Fixed e=5)
    """
    b = random.randint(2, 4)
    e = 5
    ans1 = b**e
    ans2 = (-b)**e
    ans3 = -(b**e)
    
    question_text = f"計算下列各式的值。\n⑴ $\\text{{{b}}}^\\text{{{e}}}$ \n⑵ $(-\\text{{{b}}})^\\text{{{e}}}$ \n⑶ $-\\text{{{b}}}^\\text{{{e}}}$"
    correct_answer = f"⑴ {ans1} ⑵ {ans2} ⑶ {ans3}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_6_problem():
    """
    Type 6: 進階 - 指數與加減乘除混合運算
    [Fix] 使用半形 + 號，確保 LaTeX 渲染正常。
    """
    # Q1: (-b1^2) / d1 - b2^3
    b1_val, d1_val = None, None
    for _ in range(100):
        b1 = random.randint(2, 6)
        val = b1**2
        for _ in range(20):
            d1 = random.randint(2, 5)
            if val % d1 == 0:
                b1_val, d1_val = b1, d1
                break
        if b1_val: break
    if not b1_val: b1_val, d1_val = 4, 2

    e1 = 2
    b2 = random.randint(2, 5)
    e2 = 3
    ans1 = -(b1_val**e1) // d1_val - (b2**e2)

    # Q2: n1 - b3^3 * (n2 + (-b4^2))
    n1 = random.randint(5, 15)
    b3 = random.randint(2, 4)
    e3 = 3
    n2 = random.randint(5, 15)
    b4 = random.randint(2, 5)
    e4 = 2
    
    ans2 = n1 - (b3**e3) * (n2 + (-(b4**e4)))
    
    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ $(-\\text{{{b1_val}}}^\\text{{{e1}}}) \\div \\text{{{d1_val}}} - \\text{{{b2}}}^\\text{{{e2}}}$ \n"
        f"⑵ $\\text{{{n1}}} - \\text{{{b3}}}^\\text{{{e3}}} \\times [ \\text{{{n2}}} + (-\\text{{{b4}}}^\\text{{{e4}}}) ]$"
    )
    correct_answer = f"⑴ {ans1} ⑵ {ans2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_7_problem():
    """
    Type 7: 進階 - 包含中括號與負數次方的複雜運算
    """
    # Q1
    b1_val, n1_val, d1_val, inter_val = None, None, None, None
    for _ in range(100):
        b1 = random.randint(2, 5)
        n1 = random.randint(2, 10)
        val = -((-b1)**2) + n1
        for _ in range(20):
            d1 = random.randint(2, 10)
            if d1 != 0 and val % d1 == 0:
                b1_val, n1_val, d1_val, inter_val = b1, n1, d1, val
                break
        if b1_val: break
    if not b1_val: b1_val, n1_val, d1_val = 3, 5, -2

    ans1 = inter_val // d1_val

    # Q2
    n2 = random.randint(-150, -50)
    b2_val, n3_val, div_val = None, None, None
    for _ in range(100):
        b2 = random.randint(2, 5)
        d_val = (-b2)**2
        for _ in range(20):
            n3 = random.randint(-100, -20)
            if n3 % d_val == 0:
                b2_val, n3_val, div_val = b2, n3, d_val
                break
        if b2_val: break
    if not b2_val: b2_val, n3_val, div_val = 4, -32, 16

    ans2 = n2 - n3_val // div_val
    
    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ $[ -( (-\\text{{{b1_val}}})^2 ) + \\text{{{n1_val}}} ] \\div \\text{{{d1_val}}}$ \n"
        f"⑵ $(\\text{{{n2}}}) - (\\text{{{n3_val}}}) \\div ((-\\text{{{b2_val}}})^2)$"
    )
    correct_answer = f"⑴ {ans1} ⑵ {ans2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# ==============================================================================
# Main Dispatcher
# ==============================================================================
def generate(level=1):
    """
    難度分級 (Level Design):
    Level 1: 基礎觀念 (指數定義、正負號判斷) -> Type 1, 2, 3, 4, 5
    Level 2: 混合運算 (四則運算、括號優先權) -> Type 6, 7
    """
    if level == 1:
        problem_types = [
            generate_type_1_problem,
            generate_type_2_problem, # 已修復 LaTeX
            generate_type_3_problem,
            generate_type_4_problem,
            generate_type_5_problem
        ]
    else:
        # 進階運算，對應圖片中的混合題
        problem_types = [
            generate_type_6_problem,
            generate_type_7_problem
        ]
    
    selected_problem_func = random.choice(problem_types)
    return selected_problem_func()