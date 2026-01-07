# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 190.43s | RAG: 10 examples
# Created At: 2026-01-07 22:15:50
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
    num = random.randint(10, 50)
    return f"計算 {num}＋(-{num}) 的值。"

def generate_type_2_problem():
    num = random.randint(10, 50)
    return f"計算 (-{num})＋{num} 的值。"

def generate_type_3_problem():
    num = random.randint(10, 50)
    return f"計算 {num}＋(-{num}) 的值。"

def generate_type_4_problem():
    num = random.randint(10, 50)
    return f"計算 (-{num})＋{num} 的值。"

def generate_type_5_problem():
    num = random.randint(10, 50)
    return f"計算 {num}＋(-{num}) 的值。"

def generate_type_6_problem():
    num = random.randint(10, 50)
    return f"計算 (-{num})＋{num} 的值。"

def generate_type_7_problem():
    val_a = random.randint(10, 50)
    val_b = random.randint(10, 50)
    return f"計算 {val_a}＋(-{val_b}) 的值。"

def generate_type_8_problem():
    num_a_abs = random.randint(15, 35)
    num_b = random.randint(10, 30)
    return f"計算 (-{num_a_abs})＋{num_b} 的值。"

def generate_type_9_problem():
    num_val = random.randint(5, 50)
    return f"計算 {num_val}＋(-{num_val}) 的值。"

def generate_type_10_problem():
    neg1_abs = random.randint(13, 47)
    while True:
        neg2_abs = random.randint(13, 47)
        if neg1_abs != neg2_abs and (neg1_abs + neg2_abs) % 10 == 0:
            break
    pos_num = random.randint(sum([neg1_abs, neg2_abs]) + 50, sum([neg1_abs, neg2_abs]) + 200)
    return f"計算 (-{neg1_abs})＋{pos_num}＋(-{neg2_abs}) 的值。"

def generate_type_11_problem():
    cancel_num = random.randint(50, 200)
    while True:
        remaining_neg_abs = random.randint(20, 100)
        if remaining_neg_abs != cancel_num:
            break
    return f"計算 {cancel_num}＋(-{remaining_neg_abs})＋(-{cancel_num}) 的值。"

# Example usage:

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_10_problem', 'generate_type_11_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem', 'generate_type_8_problem', 'generate_type_9_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_10_problem': return generate_type_10_problem()
        elif selected_type == 'generate_type_11_problem': return generate_type_11_problem()
        elif selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        elif selected_type == 'generate_type_8_problem': return generate_type_8_problem()
        elif selected_type == 'generate_type_9_problem': return generate_type_9_problem()
        else: return generate_type_10_problem()
    except TypeError:
        return generate_type_10_problem()
