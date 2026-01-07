# ==============================================================================
# ID: jh_數學1上_OppositesAndAbsoluteValue
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 273.42s | RAG: 7 examples
# Created At: 2026-01-07 23:06:33
# Fix Status: [Repaired]
# ==============================================================================

from fractions import Fraction
import random
import math
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



def generate_type_1_problem():
    num1 = -random.randint(2, 10)
    num2 = -random.randint(2, 10)
    while num2 == num1:
        num2 = -random.randint(2, 10)
    
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    if abs_num1 < abs_num2:
        abs_op = "<"
    else:
        abs_op = ">"
    
    question = f"分別寫出 {num1} 和 {num2} 的絕對值，並比較這兩數絕對值的大小。"
    answer = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{abs_op}|{num2}|"
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_2_problem():
    num1 = -random.randint(2, 10)
    num2 = -random.randint(2, 10)
    while num2 == num1:
        num2 = -random.randint(2, 10)
    
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    if abs_num1 < abs_num2:
        abs_op = "<"
    else:
        abs_op = ">"
    
    question = f"｜{num1}｜"
    answer = f"{abs_num1}"
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_3_problem():
    num1 = -random.randint(2, 10)
    num2 = -random.randint(2, 10)
    while num2 == num1:
        num2 = -random.randint(2, 10)
    
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    if abs_num1 < abs_num2:
        abs_op = "<"
    else:
        abs_op = ">"
    
    question = f"分別寫出 {num1} 和 {num2} 的絕對值，並比較這兩數絕對值的大小。"
    answer = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{abs_op}|{num2}|"
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_4_problem():
    num1 = -random.randint(5, 20)
    num2 = -random.randint(5, 20)
    while num1 == num2:
        num2 = -random.randint(5, 20)
    
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    if abs_num1 < abs_num2:
        abs_op = "<"
    else:
        abs_op = ">"
    
    question = f"1. 分別寫出 {num1} 與 {num2} 的絕對值，並比較這兩數絕對值的大小。 \\\\ 2. 承 1，判斷 {num1} 與 {num2} 哪一個比較大？"
    if num1 > num2:
        larger_num = num1
    else:
        larger_num = num2
    
    answer = f"1. |{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{abs_op}|{num2}|\\n2. {larger_num} 比較大"
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_5_problem():
    k = random.randint(2, 15)
    
    question = f"在數線上，有一數 a，若｜a｜={k}，則 a 是多少？"
    answer = f"a = {k} 或 a = {-k}"
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_6_problem():
    k = random.randint(3, 8)
    
    integers = list(range(-(k-1), k))
    question = f"寫出絕對值小於 {k} 的所有整數。"
    answer = "、".join(map(str, integers))
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_7_problem():
    k = random.randint(3, 8)
    
    negative_integers = list(range(-k+1, -1))
    question = f"已知 c 為負整數，且｜c｜＜{k}，則 c 可能是多少？"
    answer = "、".join(map(str, negative_integers))
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
# Dispatcher List
problem_generators = [
    generate_type_1_problem,
    generate_type_2_problem,
    generate_type_3_problem,
    generate_type_4_problem,
    generate_type_5_problem,
    generate_type_6_problem,
    generate_type_7_problem
]

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
