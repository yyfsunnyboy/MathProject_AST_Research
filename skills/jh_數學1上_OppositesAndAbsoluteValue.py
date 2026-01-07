# ==============================================================================
# ID: jh_數學1上_OppositesAndAbsoluteValue
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 53.74s | RAG: 7 examples
# Created At: 2026-01-07 16:08:32
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
    num = random.randint(-20, -5)
    answer_str = f"{num} 比較大"
    return f"1. 分別寫出 \\( {num} \\) 與 \\( {num} \\) 的絕對值，並比較這兩數絕對值的大小。\\\\ 2. 承 1，判斷 \\( {num} \\) 與 \\( {num} \\) 哪一個比較大？", answer_str

def generate_type_2_problem():
    num = random.randint(-20, -5)
    answer_str = f"{abs(num)}"
    return f"寫出下列各數的值。\\\\ (1) \\( |{num}| \\)", answer_str

def generate_type_3_problem():
    num1 = random.randint(-15, -2)
    num2 = random.randint(-15, -2)
    while num1 == num2:
        num2 = random.randint(-15, -2)
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    comparison_sign = '<' if abs_num1 < abs_num2 else '>'
    answer_str = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{comparison_sign}|{num2}|"
    return f"分別寫出 \\( {num1} \\) 和 \\( {num2} \\) 的絕對值，並比較這兩數絕對值的大小。", answer_str

def generate_type_4_problem():
    num1 = random.randint(-20, -5)
    num2 = random.randint(-20, -5)
    while num1 == num2:
        num2 = random.randint(-20, -5)
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    abs_comparison_sign = '<' if abs_num1 < abs_num2 else '>'
    answer_str = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{abs_comparison_sign}|{num2}|"
    larger_num = max(num1, num2)
    num_answer_str = f"{larger_num} 比較大"
    return f"1. 分別寫出 \\( {num1} \\) 與 \\( {num2} \\) 的絕對值，並比較這兩數絕對值的大小。\\\\ 2. 承 1，判斷 \\( {num1} \\) 與 \\( {num2} \\) 哪一個比較大？", f"{answer_str}\n{num_answer_str}"

def generate_type_5_problem():
    abs_val = random.randint(3, 15)
    answer_str = f"a = {abs_val} 或 a = {-abs_val}"
    return f"在數線上，有一數 \\( a \\)，若 \\( |a|={abs_val} \\)，則 \\( a \\) 是多少？", answer_str

def generate_type_6_problem():
    upper_bound = random.randint(4, 8)
    integers_list = list(range(-(upper_bound - 1), upper_bound))
    answer_str = "、".join(map(str, integers_list))
    return f"寫出絕對值小於 \\( {upper_bound} \\) 的所有整數。", answer_str

def generate_type_7_problem():
    upper_bound = random.randint(3, 7)
    integers_list = list(range(-(upper_bound - 1), 0))
    answer_str = "、".join(map(str, integers_list))
    return f"已知 \\( c \\) 為負整數，且 \\( |c| < {upper_bound} \\)，則 \\( c \\) 可能是多少？", answer_str

def generate_type_1_problem():
    num = random.randint(-20, -5)
    answer_str = f"{num} 比較大"
    return f"1. 分別寫出 \\( {num} \\) 與 \\( {num} \\) 的絕對值，並比較這兩數絕對值的大小。\\\\ 2. 承 1，判斷 \\( {num} \\) 與 \\( {num} \\) 哪一個比較大？", answer_str

def generate_type_2_problem():
    num = random.randint(-20, -5)
    answer_str = f"{abs(num)}"
    return f"寫出下列各數的值。\\\\ (1) \\( |{num}| \\)", answer_str

def generate_type_3_problem():
    num1 = random.randint(-15, -2)
    num2 = random.randint(-15, -2)
    while num1 == num2:
        num2 = random.randint(-15, -2)
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    comparison_sign = '<' if abs_num1 < abs_num2 else '>'
    answer_str = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{comparison_sign}|{num2}|"
    return f"分別寫出 \\( {num1} \\) 和 \\( {num2} \\) 的絕對值，並比較這兩數絕對值的大小。", answer_str

def generate_type_4_problem():
    num1 = random.randint(-20, -5)
    num2 = random.randint(-20, -5)
    while num1 == num2:
        num2 = random.randint(-20, -5)
    abs_num1 = abs(num1)
    abs_num2 = abs(num2)
    abs_comparison_sign = '<' if abs_num1 < abs_num2 else '>'
    answer_str = f"|{num1}|={abs_num1}, |{num2}|={abs_num2}, |{num1}|{abs_comparison_sign}|{num2}|"
    larger_num = max(num1, num2)
    num_answer_str = f"{larger_num} 比較大"
    return f"1. 分別寫出 \\( {num1} \\) 與 \\( {num2} \\) 的絕對值，並比較這兩數絕對值的大小。\\\\ 2. 承 1，判斷 \\( {num1} \\) 與 \\( {num2} \\) 哪一個比較大？", f"{answer_str}\n{num_answer_str}"

def generate_type_5_problem():
    abs_val = random.randint(3, 15)
    answer_str = f"a = {abs_val} 或 a = {-abs_val}"
    return f"在數線上，有一數 \\( a \\)，若 \\( |a|={abs_val} \\)，則 \\( a \\) 是多少？", answer_str

def generate_type_6_problem():
    upper_bound = random.randint(4, 8)
    integers_list = list(range(-(upper_bound - 1), upper_bound))
    answer_str = "、".join(map(str, integers_list))
    return f"寫出絕對值小於 \\( {upper_bound} \\) 的所有整數。", answer_str

def generate_type_7_problem():
    upper_bound = random.randint(3, 7)
    integers_list = list(range(-(upper_bound - 1), 0))
    answer_str = "、".join(map(str, integers_list))
    return f"已知 \\( c \\) 為負整數，且 \\( |c| < {upper_bound} \\)，則 \\( c \\) 可能是多少？", answer_str

# Dispatcher List
dispatcher_list = [
    generate_type_1_problem,
    generate_type_2_problem,
    generate_type_3_problem,
    generate_type_4_problem,
    generate_type_5_problem,
    generate_type_6_problem,
    generate_type_7_problem
]

def generate_random_problem():
    problem_func = random.choice(dispatcher_list)
    return problem_func()

# Example usage:
problem, answer = generate_random_problem()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_random_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_random_problem': return generate_random_problem()
        elif selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        else: return generate_random_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_random_problem()
