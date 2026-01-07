# ==============================================================================
# ID: jh_數學1上_PowersOfTen
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 73.16s | RAG: 1 examples
# Created At: 2026-01-07 22:49:24
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
    n = random.randint(2, 8)
    m = random.randint(2, 8)
    
    fraction_part1_denom = 10**n
    part1_fraction_ans = f"1/{fraction_part1_denom}"
    part1_decimal_ans = f"{1 / fraction_part1_denom:.{n}f}"
    
    decimal_display_part2_zeros = '0' * (m - 1)
    decimal_display_part2_str = f"0.{decimal_display_part2_zeros}1"
    
    part2_blank1_ans = 10**m
    part2_blank2_ans = m
    part2_blank3_ans = -m
    
    question_text = f"""
    1. 分別以分數和小數表示 ${{10^{{-{n}}}}}$。
    2. 在括號內填入適當的數。
    ${{ {decimal_display_part2_str} = \\frac{{1}}{{(~)}} = \\frac{{1}}{{10^{{(~)}}}} = 10^{{(~)}} }}$
    """
    
    answer = {
        "part1_fraction": part1_fraction_ans,  # e.g., "1/10000000"
        "part1_decimal": part1_decimal_ans,    # e.g., "0.0000001"
        "part2_blank1": part2_blank1_ans,      # e.g., 1000000 (int)
        "part2_blank2": part2_blank2_ans,      # e.g., 6 (int)
        "part2_blank3": part2_blank3_ans       # e.g., -6 (int)
    }
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': {
            "part1_fraction": f"1/{10**n}",
            "part1_decimal": f"{1 / (10**n):.{n}f}",
            "part2_blank1": 10**m,
            "part2_blank2": m,
            "part2_blank3": -m
        }
    }

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
