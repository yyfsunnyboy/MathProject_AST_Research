# ==============================================================================
# ID: jh_數學1上_PowersOfTen
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 10.98s | RAG: 1 examples
# Created At: 2026-01-07 16:09:27
# Fix Status: [Repaired]
# ==============================================================================

import random

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}}{{abs(num).numerator // abs(num).denominator} \\frac{{{{{rem.numerator}}}}{{{{rem.denominator}}}"
        return f"\\frac{{{{{num.numerator}}}}{{{{num.denominator}}}"
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
        l_n += f"{str(i):^{{u_w}}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{{u_w}}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")



def generate_type_1_problem():
    magnitude_n = random.randint(2, 8)
    negative_exponent = -magnitude_n
    fraction_ans_part1 = f"\\frac{{{{1}}}{{{{10**magnitude_n}}}"
    decimal_ans_part1 = f"0.{'0' * (magnitude_n - 1)}1"
    decimal_fill_in_val = decimal_ans_part1
    fill_in_ans_1 = 10**magnitude_n
    fill_in_ans_2 = magnitude_n
    fill_in_ans_3 = negative_exponent
    
    question_text = f"1. 分別以分數和小數表示 ${{10^{{{negative_exponent}}}}}}$。\n2. 在括號內填入適當的數。\n${{ {decimal_fill_in_val} = \\frac{{{{1}}}{{{(~~~)}} = \\frac{{{{1}}}{{{10^{{(~)}}}} = 10^{{(~)}} }}$"
    answer = f"1. {fraction_ans_part1}, {decimal_ans_part1}\n2. {fill_in_ans_1}, {fill_in_ans_2}, {fill_in_ans_3}"
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

# Example usage
problem = generate_type_1_problem()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_type_1_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        else: return generate_type_1_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
