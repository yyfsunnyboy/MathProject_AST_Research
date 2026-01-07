# ==============================================================================
# ID: jh_數學1上_IntegerExponentiation
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 224.58s | RAG: 7 examples
# Created At: 2026-01-07 22:20:37
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
    exponent = random.choice([3, 4, 5])
    ans = (-base) ** exponent if random.random() < 0.5 else base ** exponent
    return f"⑴ ${{ ({-base})^{{ {exponent} }} }}$", [(-base) ** exponent]

def generate_type_2_problem():
    a1 = random.randint(3, 7)
    b1 = random.choice([f for f in range(2, 6) if (a1**2) % f == 0])
    c1 = random.randint(2, 4)
    ans = (-(a1**2)) // b1 - (c1**3)
    return f"⑴ ${{ ({-a1}^{{2}}) \\div {b1} - {c1}^{{3}} }}$", [ans]

def generate_type_3_problem():
    base = random.randint(2, 5)
    exponent = 3
    ans = (-base) ** exponent if random.random() < 0.5 else base ** exponent
    return f"⑴ ${{ ({-base})^{{ {exponent} }} }}$", [ans]

def generate_type_4_problem():
    base = random.randint(2, 4)
    exponent = 3
    ans = (-base) ** exponent if random.random() < 0.5 else base ** exponent
    return f"⑴ ${{ ({-base})^{{ {exponent} }} }}$", [ans]

def generate_type_5_problem():
    base = random.randint(2, 4)
    exponent = 5
    ans = (-base) ** exponent if random.random() < 0.5 else base ** exponent
    return f"⑴ ${{ ({-base})^{{ {exponent} }} }}$", [ans]

def generate_type_6_problem():
    a1 = random.randint(3, 7)
    b1 = random.choice([f for f in range(2, 6) if (a1**2) % f == 0])
    c1 = random.randint(2, 4)
    ans1 = (-(a1**2)) // b1 - (c1**3)
    
    a2 = random.randint(8, 15)
    b2 = random.randint(2, 3)
    d2 = random.randint(2, 4)
    val_in_bracket = random.randint(2, 7)
    c2 = val_in_bracket + d2**2
    ans2 = a2 - (b2**3) * (c2 + (-(d2**2)))
    
    return f"⑴ ${{ ({-a1}^{{2}}) \\div {b1} - {c1}^{{3}} }}$", [ans1], \
           f"⑵ ${{ {a2} - {b2}^{{3}} \\times [ {c2} + ({-d2}^{{2}}) ] }}$", [ans2]

def generate_type_7_problem():
    base1 = random.randint(2, 5)
    add1 = random.randint(2, 7)
    intermediate_val = -((-base1)**2) + add1
    divisor1_options = [d for d in range(2, 11) if intermediate_val % d == 0]
    if not divisor1_options: return "", []
    divisor1 = random.choice(divisor1_options)
    ans1 = intermediate_val // divisor1
    
    start_num = random.randint(-150, -50)
    base2 = random.randint(2, 5)
    denominator_val = (-base2)**2
    numerator2_options = [n for n in range(50, 101) if n % denominator_val == 0]
    if not numerator2_options: return "", []
    numerator2 = random.choice(numerator2_options)
    ans2 = start_num - (-numerator2) // denominator_val
    
    return f"⑴ ${{ [ - ({-base1})^{{2}} + {add1} ] \\div {divisor1} }}$", [ans1], \
           f"⑵ ${{ {start_num} - ({-numerator2}) \\div ({-base2})^{{2}} }}$", [ans2]

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
