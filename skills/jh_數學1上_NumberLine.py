# ==============================================================================
# ID: jh_數學1上_NumberLine
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 393.92s | RAG: 4 examples
# Created At: 2026-01-07 22:40:44
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



def generate_type_1_problem():
    dec_val_int = random.randint(0, 9)
    dec_val_frac = random.randint(1, 9)
    mix_int = -random.randint(1, 3)
    mix_num = random.randint(1, 4)
    while mix_num >= mix_int:
        mix_num = random.randint(1, 4)
    mix_denom = random.randint(2, 5)
    point_name1 = chr(random.randint(65, 90))
    point_name2 = chr(random.randint(65, 90))
    while point_name2 == point_name1:
        point_name2 = chr(random.randint(65, 90))
    
    problem = f"畫一條數線，並標記 {point_name1} ( {dec_val_int}.{dec_val_frac} )、{point_name2} ( ${{ -{mix_int}\\frac{{{mix_num}}}{{{mix_denom}}} }}$ ) 的位置。"
    answer = f"圖示標註 {point_name1} 點在 {dec_val_int}.{dec_val_frac}，{point_name2} 點在 -{mix_int} 又 {mix_num}/{mix_denom}"
    return {'question_text': problem, 'answer': answer, 'correct_answer': answer}
def generate_type_2_problem():
    pos_mix_int = random.randint(1, 3)
    pos_mix_num = random.randint(1, 4)
    while pos_mix_num >= pos_mix_int:
        pos_mix_num = random.randint(1, 4)
    pos_mix_denom = random.randint(2, 5)
    neg_mix_int = -random.randint(1, 3)
    neg_mix_num = random.randint(1, 4)
    while neg_mix_num >= neg_mix_int:
        neg_mix_num = random.randint(1, 4)
    neg_mix_denom = random.randint(2, 5)
    pos_mix_frac = f"{pos_mix_int} {pos_mix_num}/{pos_mix_denom}"
    neg_mix_frac = f"-{neg_mix_int} {neg_mix_num}/{neg_mix_denom}"
    point_name1 = chr(random.randint(65, 90))
    point_name2 = chr(random.randint(65, 90))
    while point_name2 == point_name1:
        point_name2 = chr(random.randint(65, 90))
    
    problem = f"1. 在數線上分別標記 {point_name1} ( ${{ {pos_mix_int}\\frac{{{pos_mix_num}}}{{{pos_mix_denom}}} }}$ )、{point_name2} ( ${{ -{neg_mix_int}\\frac{{{neg_mix_num}}}{{{neg_mix_denom}}} }}$ ) 與 {point_name3} 的位置。\n2. 寫出數線上 {id_point_name1}、{id_point_name2} 兩點的坐標。"
    answer = f"1. 圖示標註 {point_name1}({pos_mix_int} {pos_mix_num}/{pos_mix_denom}), {point_name2}(-{neg_mix_int} {neg_mix_num}/{neg_mix_denom})\n2. {id_point_name1}({id_mix_int1} {id_mix_num1}/{id_mix_denom1}), {id_point_name2}({id_mix_int2} {id_mix_num2}/{id_mix_denom2})"
    return {'question_text': problem, 'answer': answer, 'correct_answer': answer}
def generate_type_3_problem():
    dec_val_int = random.randint(0, 9)
    dec_val_frac = random.randint(1, 9)
    mix_int = -random.randint(1, 3)
    mix_num = random.randint(1, 4)
    while mix_num >= mix_int:
        mix_num = random.randint(1, 4)
    mix_denom = random.randint(2, 5)
    point_name1 = chr(random.randint(65, 90))
    point_name2 = chr(random.randint(65, 90))
    while point_name2 == point_name1:
        point_name2 = chr(random.randint(65, 90))
    
    problem = f"畫一條數線，並標記 {point_name1} ( {dec_val_int}.{dec_val_frac} )、{point_name2} ( ${{ -{mix_int}\\frac{{{mix_num}}}{{{mix_denom}}} }}$ ) 的位置。"
    answer = f"圖示標註 {point_name1} 點在 {dec_val_int}.{dec_val_frac}，{point_name2} 點在 -{mix_int} 又 {mix_num}/{mix_denom}"
    return {'question_text': problem, 'answer': answer, 'correct_answer': answer}
def generate_type_4_problem():
    pos_mix_int = random.randint(1, 3)
    pos_mix_num = random.randint(1, 4)
    while pos_mix_num >= pos_mix_int:
        pos_mix_num = random.randint(1, 4)
    pos_mix_denom = random.randint(2, 5)
    neg_mix_int = -random.randint(1, 3)
    neg_mix_num = random.randint(1, 4)
    while neg_mix_num >= neg_mix_int:
        neg_mix_num = random.randint(1, 4)
    neg_mix_denom = random.randint(2, 5)
    pos_mix_frac = f"{pos_mix_int} {pos_mix_num}/{pos_mix_denom}"
    neg_mix_frac = f"-{neg_mix_int} {neg_mix_num}/{neg_mix_denom}"
    point_name1 = chr(random.randint(65, 90))
    point_name2 = chr(random.randint(65, 90))
    while point_name2 == point_name1:
        point_name2 = chr(random.randint(65, 90))
    
    problem = f"1. 在數線上分別標記 {point_name1} ( ${{ {pos_mix_int}\\frac{{{pos_mix_num}}}{{{pos_mix_denom}}} }}$ )、{point_name2} ( ${{ -{neg_mix_int}\\frac{{{neg_mix_num}}}{{{neg_mix_denom}}} }}$ ) 與 {point_name3} 的位置。\n2. 寫出數線上 {id_point_name1}、{id_point_name2} 兩點的坐標。"
    answer = f"1. 圖示標註 {point_name1}({pos_mix_int} {pos_mix_num}/{pos_mix_denom}), {point_name2}(-{neg_mix_int} {neg_mix_num}/{neg_mix_denom})\n2. {id_point_name1}({id_mix_int1} {id_mix_num1}/{id_mix_denom1}), {id_point_name2}({id_mix_int2} {id_mix_num2}/{id_mix_denom2})"
    return {'question_text': problem, 'answer': answer, 'correct_answer': answer}

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
