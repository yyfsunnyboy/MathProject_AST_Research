# ==============================================================================
# ID: jh_數學1上_ComparingNumbers
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 300.92s | RAG: 3 examples
# Created At: 2026-01-07 22:01:55
# Fix Status: [Clean Pass]
# ==============================================================================

import random
import math
from fractions import Fraction

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
    def _get_random_rational_number_display():
        while True:
            choice = random.choice([0, 1, 2, 3])
            if choice == 0:
                val = random.randint(-10, 10)
                return str(val), float(val)
            elif choice == 1:
                val = round(random.uniform(-10.0, 10.0), 1)
                return str(val), val
            elif choice == 2:
                denominator = random.randint(2, 10)
                numerator = random.randint(-20, 20)
                while numerator % denominator == 0:
                    numerator = random.randint(-20, 20)
                return f"\\frac{{{numerator}}}{{{denominator}}}", float(numerator) / denominator
            elif choice == 3:
                whole_part = random.randint(-5, 5)
                if whole_part == 0:
                    denominator = random.randint(2, 10)
                    numerator = random.randint(1, denominator - 1)
                    return f"\\frac{{{numerator}}}{{{denominator}}}", float(numerator) / denominator
                else:
                    denominator = random.randint(2, 10)
                    numerator = random.randint(1, denominator - 1)
                    if whole_part < 0:
                        val = float(-abs(whole_part)) - (float(numerator) / denominator)
                        return f"-{{abs({whole_part})}}\\frac{{{numerator}}}{{{denominator}}}", val
                    else:
                        val = float(whole_part) + (float(numerator) / denominator)
                        return f"{whole_part}\\frac{{{numerator}}}{{{denominator}}}", val
    
    num_a_str, num_a_val = _get_random_rational_number_display()
    num_b_str, num_b_val = _get_random_rational_number_display()
    
    while num_a_val == num_b_val:
        num_b_str, num_b_val = _get_random_rational_number_display()
    
    if num_a_val < num_b_val:
        comparison_op = "<"
    else:
        comparison_op = ">"
    
    question_text = f"比較下列各組數的大小： ${{ {num_a_str} }}$ 和 ${{ {num_b_str} }}$"
    answer = comparison_op
    
    return {'question_text': question_text, 'answer': str(answer), 'correct_answer': str(answer)}

def generate_type_2_problem():
    def _get_random_rational_number_display():
        while True:
            choice = random.choice([0, 1, 2, 3])
            if choice == 0:
                val = random.randint(-10, 10)
                return str(val), float(val)
            elif choice == 1:
                val = round(random.uniform(-10.0, 10.0), 1)
                return str(val), val
            elif choice == 2:
                denominator = random.randint(2, 10)
                numerator = random.randint(-20, 20)
                while numerator % denominator == 0:
                    numerator = random.randint(-20, 20)
                return f"\\frac{{{numerator}}}{{{denominator}}}", float(numerator) / denominator
            elif choice == 3:
                whole_part = random.randint(-5, 5)
                if whole_part == 0:
                    denominator = random.randint(2, 10)
                    numerator = random.randint(1, denominator - 1)
                    return f"\\frac{{{numerator}}}{{{denominator}}}", float(numerator) / denominator
                else:
                    denominator = random.randint(2, 10)
                    numerator = random.randint(1, denominator - 1)
                    if whole_part < 0:
                        val = float(-abs(whole_part)) - (float(numerator) / denominator)
                        return f"-{{abs({whole_part})}}\\frac{{{numerator}}}{{{denominator}}}", val
                    else:
                        val = float(whole_part) + (float(numerator) / denominator)
                        return f"{whole_part}\\frac{{{numerator}}}{{{denominator}}}", val
    
    target_str, target_val = _get_random_rational_number_display()
    
    question_text = f"老師心中想了一個數 a，小翊猜說：「這個數比 ${{ {target_str} }}$ 大。」小妍猜說：「這個數比 ${{ {target_str} }}$ 小。」結果老師說兩個人都猜錯了，那麼 a 應該是多少呢？"
    answer = target_str
    
    return {'question_text': question_text, 'answer': str(answer), 'correct_answer': str(answer)}

def generate_type_3_problem():
    x_val = random.choice([random.randint(-5, 5), round(random.uniform(-5.0, 5.0), 1)])
    x_str = str(x_val)
    a_val = x_val - random.uniform(0.1, 5.0)
    b_val = x_val + random.uniform(0.1, 5.0)
    
    question_text = f"已知 a 和 b 分別代表一個數，若 a＜${{ {x_str} }}$ 且 ${{ {x_str} }}$＜b，則 a 和 b 何者較大？"
    answer = "b 較大"
    
    return {'question_text': question_text, 'answer': str(answer), 'correct_answer': str(answer)}

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
