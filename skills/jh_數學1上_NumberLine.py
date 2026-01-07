# ==============================================================================
# ID: jh_數學1上_NumberLine
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 42.52s | RAG: 4 examples
# Created At: 2026-01-07 16:07:38
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
    pos_int = random.randint(1, 10)
    neg_int = random.randint(-10, -1)
    question_text = f"畫一條數線，並標記 A ( {pos_int} )、B ( {neg_int} ) 的位置。"
    answer_text = f"圖示標示 A 點在 {pos_int}，B 點在 {neg_int}"
    return {'question_text': question_text, 'answer': answer_text, 'correct_answer': answer_text}

def generate_type_2_problem():
    mark_int1 = random.randint(1, 10)
    mark_int2 = random.randint(-10, -1)
    identify_mixed_int3 = random.randint(1, 3)
    identify_mixed_num3 = random.randint(1, 4)
    identify_mixed_denom3 = random.randint(2, 5)
    while identify_mixed_denom3 in {mark_int1, mark_int2}:
        identify_mixed_denom3 = random.randint(2, 5)
    identify_mixed_num3 = random.randint(1, identify_mixed_denom3 - 1)
    question_text = f"在數線上分別標記 C ( {mark_int1} )、D ( ${{-}}{mark_int2}$ ) 與 E ( ${{identify_mixed_int3}}\\frac{{{identify_mixed_num3}}}{{{identify_mixed_denom3}}}$ ) 的位置。\n2. 寫出數線上 F ( ${{identify_mixed_int3}}\\frac{{{identify_mixed_num3}}}{{{identify_mixed_denom3}}}$ )、G ( ${{-}}{identify_mixed_int4}\\frac{{{identify_mixed_num4}}}{{{identify_mixed_denom4}}}$ ) 兩點的坐標。"
    answer_text = f"1. 圖示標示 C({mark_int1}), D(-{mark_int2}), E({identify_mixed_int3} {identify_mixed_num3}/{identify_mixed_denom3})\n2. F({identify_mixed_int3} {identify_mixed_num3}/{identify_mixed_denom3}), G(-{identify_mixed_int4} {identify_mixed_num4}/{identify_mixed_denom4})"
    return {'question_text': question_text, 'answer': answer_text, 'correct_answer': answer_text}

def generate_type_3_problem():
    decimal_int_part = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    decimal_fraction_part = random.randint(1, 9)
    decimal_val = float(f"{decimal_int_part}.{decimal_fraction_part}")
    mixed_int_part = random.randint(1, 4)
    mixed_denom = random.randint(2, 5)
    mixed_num = random.randint(1, mixed_denom - 1)
    question_text = f"畫一條數線，並標記 A ( {decimal_val} )、B ( ${{-}}{mixed_int_part}\\frac{{{mixed_num}}}{{{mixed_denom}}}$ ) 的位置。"
    answer_text = f"圖示標示 A 點在 {decimal_val}，B 點在 -{mixed_int_part} {mixed_num}/{mixed_denom}"
    return {'question_text': question_text, 'answer': answer_text, 'correct_answer': answer_text}

def generate_type_4_problem():
    mark_mixed_int1 = random.randint(1, 3)
    mark_mixed_denom1 = random.randint(2, 5)
    mark_mixed_num1 = random.randint(1, mark_mixed_denom1 - 1)
    mark_mixed_int2 = random.randint(1, 3)
    mark_mixed_denom2 = random.randint(2, 5)
    while mark_mixed_denom2 == mark_mixed_denom1:
        mark_mixed_denom2 = random.randint(2, 5)
    mark_mixed_num2 = random.randint(1, mark_mixed_denom2 - 1)
    mark_decimal_int = random.randint(-3, -1)
    mark_decimal_frac = random.randint(1, 9)
    mark_decimal_val = float(f"{mark_decimal_int}.{mark_decimal_frac}")
    identify_mixed_int3 = random.randint(1, 3)
    identify_mixed_denom3 = random.randint(2, 5)
    while identify_mixed_denom3 in {mark_mixed_denom1, mark_mixed_denom2}:
        identify_mixed_denom3 = random.randint(2, 5)
    identify_mixed_num3 = random.randint(1, identify_mixed_denom3 - 1)
    identify_mixed_int4 = random.randint(1, 3)
    identify_mixed_denom4 = random.randint(2, 5)
    while identify_mixed_denom4 in {mark_mixed_denom1, mark_mixed_denom2, identify_mixed_denom3}:
        identify_mixed_denom4 = random.randint(2, 5)
    identify_mixed_num4 = random.randint(1, identify_mixed_denom4 - 1)
    question_text = f"1. 在數線上分別標記 C ( ${{mark_mixed_int1}}\\frac{{{mark_mixed_num1}}}{{{mark_mixed_denom1}}}$ )、D ( ${{-}}{mark_mixed_int2}\\frac{{{mark_mixed_num2}}}{{{mark_mixed_denom2}}}$ ) 與 E ( {mark_decimal_val} ) 的位置。\n2. 寫出數線上 F ( ${{identify_mixed_int3}}\\frac{{{identify_mixed_num3}}}{{{identify_mixed_denom3}}}$ )、G ( ${{-}}{identify_mixed_int4}\\frac{{{identify_mixed_num4}}}{{{identify_mixed_denom4}}}$ ) 兩點的坐標。"
    answer_text = f"1. 圖示標示 C({mark_mixed_int1} {mark_mixed_num1}/{mark_mixed_denom1}), D(-{mark_mixed_int2} {mark_mixed_num2}/{mark_mixed_denom2}), E({mark_decimal_val})\n2. F({identify_mixed_int3} {identify_mixed_num3}/{identify_mixed_denom3}), G(-{identify_mixed_int4} {identify_mixed_num4}/{identify_mixed_denom4})"
    return {'question_text': question_text, 'answer': answer_text, 'correct_answer': answer_text}

# [Auto-Injected Robust Dispatcher by v7.9.3]
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
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
