# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Gemini Plan + Qwen Code)
# Duration: 144.94s | RAG: 2 examples
# Created At: 2026-01-06 16:08:57
# Fix Status: [Repaired]
# ==============================================================================

from fractions import Fraction
import random

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")



def generate_type_A_problem():
    # Logic for Concept A
    raw_num1 = random.randint(-150, 150)
    while raw_num1 == 0:
        raw_num1 = random.randint(-150, 150)
    
    raw_num2 = random.randint(-50, 50)
    while raw_num2 == 0:
        raw_num2 = random.randint(-50, 50)
    
    str_num1 = f"({raw_num1})" if raw_num1 < 0 else str(raw_num1)
    str_num2 = f"({raw_num2})" if raw_num2 < 0 else str(raw_num2)
    
    result = raw_num1 - raw_num2
    
    return {
        'question_text': f"計算下列各式的值。\n{str_num1} - {str_num2}",
        'answer': to_latex(result),
        'correct_answer': result
    }

def generate_type_B_problem():
    # Logic for Concept B
    raw_num1 = random.randint(-40, 40)
    while raw_num1 == 0:
        raw_num1 = random.randint(-40, 40)
    
    raw_num2 = random.randint(-30, 30)
    while raw_num2 == 0:
        raw_num2 = random.randint(-30, 30)
    
    str_num1 = f"({raw_num1})" if raw_num1 < 0 else str(raw_num1)
    str_num2 = f"({raw_num2})" if raw_num2 < 0 else str(raw_num2)
    
    result = raw_num1 - raw_num2
    
    return {
        'question_text': f"計算下列各式的值。\n{str_num1} - {str_num2}",
        'answer': to_latex(result),
        'correct_answer': result
    }

def generate_type_C_problem():
    # Logic for Concept C
    raw_num1 = random.randint(-500, 500)
    while raw_num1 == 0:
        raw_num1 = random.randint(-500, 500)
    
    temp_abs_num2 = random.randint(1, 200)
    
    if random.random() < 0.7:
        raw_num2 = -temp_abs_num2
    else:
        raw_num2 = temp_abs_num2
    
    str_num1 = f"({raw_num1})" if raw_num1 < 0 else str(raw_num1)
    str_num2 = f"({raw_num2})" if raw_num2 < 0 else str(raw_num2)
    
    result = raw_num1 - raw_num2
    
    return {
        'question_text': f"計算下列各式的值。\n{str_num1} - {str_num2}",
        'answer': to_latex(result),
        'correct_answer': result
    }

def generate(level=1):
    type = random.choice(['type_A', 'type_B', 'type_C'])
    if type == 'type_A': return generate_type_A_problem()
    elif type == 'type_B': return generate_type_B_problem()
    else: return generate_type_C_problem()