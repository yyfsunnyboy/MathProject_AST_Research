# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 237.99s | RAG: 8 examples
# Created At: 2026-01-07 22:34:10
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
    a = random.randint(-100, 100)
    b = random.randint(-100, 100)
    expr1 = f"({a} + {b}) * ({a} - {b})"
    expr2 = f"{a}^2 - {b}^2"
    return {'question_text': expr1, 'answer': expr2, 'correct_answer': expr2}
def generate_type_2_problem():
    a = random.randint(-100, 100)
    b = random.randint(-100, 100)
    expr1 = f"{a} * {b}"
    expr2 = f"({a} + {b}) * ({a} - {b})"
    return {'question_text': expr1, 'answer': expr2, 'correct_answer': expr2}
def generate_type_3_problem():
    a = random.randint(-100, 100)
    b = random.randint(-100, 100)
    c = random.randint(-100, 100)
    expr1 = f"({a} + {b}) * {c}"
    expr2 = f"{a} * {c} + {b} * {c}"
    return {'question_text': expr1, 'answer': expr2, 'correct_answer': expr2}
def generate_type_4_problem():
    a = random.randint(-100, 100)
    b = random.randint(-100, 100)
    c = random.randint(-100, 100)
    expr1 = f"({a} + {b}) * ({c} - {d})"
    expr2 = f"{a} * {c} - {a} * {d} + {b} * {c} - {b} * {d}"
    return {'question_text': expr1, 'answer': expr2, 'correct_answer': expr2}
def generate_type_5_problem():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    expr1_left = f"-({a} + {b})"
    expr1_right = f"-{a} - {b}"
    return {'question_text': expr1_left, 'answer': expr1_right, 'correct_answer': expr1_right}
def generate_type_6_problem():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    expr1_left = f"-(-{a} + {b})"
    expr1_right = f"{a} - {b}"
    return {'question_text': expr1_left, 'answer': expr1_right, 'correct_answer': expr1_right}
def generate_type_7_problem():
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    expr1_left = f"{a} + ({b} + {c})"
    expr1_right = f"{a} + {b} + {c}"
    return {'question_text': expr1_left, 'answer': expr1_right, 'correct_answer': expr1_right}
def generate_type_8_problem():
    a = random.randint(100, 500)
    b = random.randint(50, 200)
    c = random.randint(100, 500)
    d = random.randint(50, 200)
    expr1 = f"{a} - ({b} + {a})"
    expr2 = f"({a} + {b}) - ({a} - {d})"
    return {'question_text': expr1, 'answer': expr2, 'correct_answer': expr2}
# Dispatcher function to call the appropriate problem generator based on type
def generate_problem(problem_type):
    if problem_type == 1:
        return generate_type_1_problem()
    elif problem_type == 2:
        return generate_type_2_problem()
    elif problem_type == 3:
        return generate_type_3_problem()
    elif problem_type == 4:
        return generate_type_4_problem()
    elif problem_type == 5:
        return generate_type_5_problem()
    elif problem_type == 6:
        return generate_type_6_problem()
    elif problem_type == 7:
        return generate_type_7_problem()
    elif problem_type == 8:
        return generate_type_8_problem()
    else:
        raise ValueError("Unknown problem type")

# Example usage:
# problem = generate_problem(1)

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem', 'generate_type_8_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_problem': return generate_problem()
        elif selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        elif selected_type == 'generate_type_8_problem': return generate_type_8_problem()
        else: return generate_problem()
    except TypeError:
        return generate_problem()
