# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 47.14s | RAG: 10 examples
# Created At: 2026-01-07 16:04:42
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
    num = random.randint(-20, 20)
    return f"計算 {num}＋0 的值。", num

def generate_type_2_problem():
    num = random.randint(-20, 20)
    return f"計算 0＋{num} 的值。", num

def generate_type_3_problem():
    val = random.randint(1, 20)
    other_num = random.randint(-100, 100)
    if other_num == 0:
        other_num = random.randint(-100, 100)
    
    order_choice = random.randint(1, 2)
    if order_choice == 1:
        num1 = val
        num2 = other_num
        num3 = -val
    else:
        num1 = -val
        num2 = other_num
        num3 = val
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_type_4_problem():
    num_val = random.randint(1, 20)
    num1 = -num_val
    num2 = num_val
    
    return f"計算 {num1}＋{num2} 的值。", num1 + num2

def generate_type_5_problem():
    neg_sum_target = random.choice([-100, -50, -200, -150, -120, -80])
    num1 = random.randint(-90, -10)
    num3 = neg_sum_target - num1
    
    while not (-90 <= num3 <= -10):
        num1 = random.randint(-90, -10)
        num3 = neg_sum_target - num1
    
    num2 = random.randint(100, 1500)
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_type_6_problem():
    val = random.randint(10, 200)
    other_num = random.randint(-100, 100)
    if other_num == 0:
        other_num = random.randint(-100, 100)
    
    order_choice = random.randint(1, 2)
    if order_choice == 1:
        num1 = val
        num2 = other_num
        num3 = -val
    else:
        num1 = -val
        num2 = other_num
        num3 = val
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_type_7_problem():
    num_val = random.randint(1, 20)
    num1 = -num_val
    num2 = num_val
    
    return f"計算 {num1}＋{num2} 的值。", num1 + num2

def generate_type_8_problem():
    neg_sum_target = random.choice([-100, -50, -200, -150, -120, -80])
    num1 = random.randint(-90, -10)
    num3 = neg_sum_target - num1
    
    while not (-90 <= num3 <= -10):
        num1 = random.randint(-90, -10)
        num3 = neg_sum_target - num1
    
    num2 = random.randint(100, 1500)
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_type_9_problem():
    problem_type = random.randint(1, 4)
    
    if problem_type == 1:
        num1 = random.randint(-20, 20)
        while num1 == 0:
            num1 = random.randint(-20, 20)
        num2 = 0
    elif problem_type == 2:
        num1 = 0
        num2 = random.randint(-20, 20)
        while num2 == 0:
            num2 = random.randint(-20, 20)
    elif problem_type == 3:
        val = random.randint(1, 20)
        num1 = -val
        num2 = val
    else:
        val = random.randint(1, 20)
        num1 = val
        num2 = -val
    
    return f"計算 {num1}＋{num2} 的值。", num1 + num2

def generate_type_10_problem():
    neg_sum_target = random.choice([-100, -50, -200, -150, -120, -80])
    num1 = random.randint(-90, -10)
    num3 = neg_sum_target - num1
    
    while not (-90 <= num3 <= -10):
        num1 = random.randint(-90, -10)
        num3 = neg_sum_target - num1
    
    num2 = random.randint(100, 1500)
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_type_11_problem():
    problem_subtype = random.randint(1, 2)
    
    if problem_subtype == 1:
        val = random.randint(10, 200)
        other_num = random.randint(-100, 100)
        while other_num == 0:
            other_num = random.randint(-100, 100)
        
        order_choice = random.randint(1, 2)
        if order_choice == 1:
            num1 = val
            num2 = other_num
            num3 = -val
        else:
            num1 = -val
            num2 = other_num
            num3 = val
    
    else:
        num1 = random.randint(-50, 50)
        while num1 == 0:
            num1 = random.randint(-50, 50)
        
        num2 = random.randint(100, 1500)
        
        num3 = random.randint(-50, 50)
        while num3 == 0 or num1 + num3 == 0:
            num3 = random.randint(-50, 50)
    
    return f"計算 {num1}＋{num2}＋{num3} 的值。", num1 + num2 + num3

def generate_problem():
    problem_types = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
        generate_type_6_problem,
        generate_type_7_problem,
        generate_type_8_problem,
        generate_type_9_problem,
        generate_type_10_problem,
        generate_type_11_problem
    ]
    
    problem_type = random.choice(problem_types)
    question, answer = problem_type()
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
# Example usage:
question, answer = generate_problem()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_problem', 'generate_type_10_problem', 'generate_type_11_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem', 'generate_type_8_problem', 'generate_type_9_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_problem': return generate_problem()
        elif selected_type == 'generate_type_10_problem': return generate_type_10_problem()
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
        else: return generate_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_problem()
