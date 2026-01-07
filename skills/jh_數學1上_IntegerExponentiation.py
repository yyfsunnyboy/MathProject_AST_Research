# ==============================================================================
# ID: jh_數學1上_IntegerExponentiation
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 35.99s | RAG: 7 examples
# Created At: 2026-01-07 16:05:31
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
    base = random.randint(2, 5)
    exp = random.choice([2, 3])
    ans_pos = base ** exp
    ans_neg_base = -base ** exp
    ans_neg_expr = -(base ** exp)
    return f"計算下列各式的值。\n⑴ ${{ {ans_pos} }}$\n⑵ ${{ {ans_neg_base} }}$\n⑶ ${{ {ans_neg_expr} }}$", (ans_pos, ans_neg_base, ans_neg_expr)

def generate_type_2_problem():
    base = random.randint(2, 5)
    exp = random.choice([2, 3])
    divisor = base
    ans = (-(base ** exp) // divisor) - (base ** exp)
    return f"計算下列各式的值。\n⑴ ${{ (-{base}^{exp}) \\div {divisor} - {base}^{exp} }}$", (ans,)

def generate_type_3_problem():
    base = random.randint(2, 5)
    exp = random.choice([2, 3])
    ans_pos = base ** exp
    ans_neg_base = -base ** exp
    ans_neg_expr = -(base ** exp)
    return f"計算下列各式的值。\n⑴ ${{ {ans_pos} }}$\n⑵ ${{ {ans_neg_base} }}$\n⑶ ${{ {ans_neg_expr} }}$", (ans_pos, ans_neg_base, ans_neg_expr)

def generate_type_4_problem():
    base = random.randint(2, 5)
    exp = 3
    divisor = base
    ans = (-(base ** exp) // divisor) - (base ** exp)
    return f"計算下列各式的值。\n⑴ ${{ (-{base}^{exp}) \\div {divisor} - {base}^{exp} }}$", (ans,)

def generate_type_5_problem():
    base = random.randint(2, 4)
    exp = 5
    divisor = base
    ans = (-(base ** exp) // divisor) - (base ** exp)
    return f"計算下列各式的值。\n⑴ ${{ (-{base}^{exp}) \\div {divisor} - {base}^{exp} }}$", (ans,)

def generate_type_6_problem():
    base1_a = random.randint(2, 5)
    exp1_a = random.choice([2, 3])
    divisor_a = base1_a
    base2_a = random.randint(2, 4)
    exp2_a = random.choice([2, 3])
    
    ans_a = (-(base1_a ** exp1_a) // divisor_a) - (base2_a ** exp2_a)

    val1_b = random.randint(5, 15)
    base1_b = random.randint(2, 3)
    exp1_b = random.choice([3, 4])
    val2_b = random.randint(5, 15)
    base2_b = random.randint(2, 4)
    exp2_b = random.choice([2, 3])

    inner_bracket_b = val2_b + (-(base2_b ** exp2_b))
    ans_b = val1_b - ((base1_b ** exp1_b) * inner_bracket_b)

    return f"計算下列各式的值。\n⑴ ${{ (-{base1_a}^{exp1_a}) \\div {divisor_a} - {base2_a}^{exp2_a} }}$\n⑵ ${{ {val1_b} - {base1_b}^{exp1_b} \\times [ {val2_b} + (-{base2_b}^{exp2_b}) ] }}$", (ans_a, ans_b)

def generate_type_7_problem():
    base_a = random.randint(2, 5)
    exp_a = random.choice([2, 3])
    add_val_a = random.randint(2, 6)
    
    while True:
        divisor_a = random.randint(2, 6)
        if (-((-base_a)**exp_a) + add_val_a) % divisor_a == 0:
            break
    
    ans_a = (-((-base_a)**exp_a) + add_val_a) // divisor_a

    val1_b = random.choice([-100, -75, -50])
    base_b = random.randint(2, 5)
    exp_b = 2
    divisor_val_b = (-base_b) ** exp_b
    
    while True:
        val2_b_candidate = random.choice([-100, -75, -50])
        if val2_b_candidate % divisor_val_b == 0:
            break
    
    val2_b = val2_b_candidate
    ans_b = val1_b - (val2_b // divisor_val_b)

    return f"計算下列各式的值。\n⑴ ${{ [-(-{base_a})^{exp_a} + {add_val_a} ] \\div {divisor_a} }}$\n⑵ ${{ ({val1_b}) - ({val2_b}) \\div (-{base_b})^{exp_b} }}$", (ans_a, ans_b)

dispatcher_list = [generate_type_1_problem, generate_type_2_problem, generate_type_3_problem, generate_type_4_problem, generate_type_5_problem, generate_type_6_problem, generate_type_7_problem]

# [Auto-Injected Robust Dispatcher by v7.9.3]
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
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
