# ==============================================================================
# ID: jh_數學1上_IntegerMultiplication
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 34.85s | RAG: 5 examples
# Created At: 2026-01-07 16:06:06
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
    num1 = random.choice(range(-10, 0)) if random.random() < 0.5 else random.choice(range(1, 11))
    num2 = random.choice(range(-10, 0)) if random.random() < 0.5 else random.choice(range(1, 11))
    answer = num1 * num2
    num1_display = f"( {num1} )" if num1 < 0 else str(num1)
    num2_display = f"( {num2} )" if num2 < 0 else str(num2)
    question_text = f"計算下列各式的值。\n${{ {num1_display} \\times {num2_display} }}$"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    num1 = random.choice(range(-15, 0)) if random.random() < 0.5 else random.choice(range(1, 16))
    num2 = random.choice(range(-12, 0)) if random.random() < 0.5 else random.choice(range(1, 13))
    answer = num1 * num2
    num1_display = f"( {num1} )" if num1 < 0 else str(num1)
    num2_display = f"( {num2} )" if num2 < 0 else str(num2)
    question_text = f"計算下列各式的值。\n${{ {num1_display} \\times {num2_display} }}$"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_3_problem():
    num1 = random.choice(range(-10, 0)) if random.random() < 0.5 else random.choice(range(1, 11))
    num2 = random.choice(range(-10, 0)) if random.random() < 0.5 else random.choice(range(1, 11))
    num3 = random.choice(range(-5, 0)) if random.random() < 0.5 else random.choice(range(1, 6))
    answer = num1 * num2 * num3
    num1_display = f"( {num1} )" if num1 < 0 else str(num1)
    num2_display = f"( {num2} )" if num2 < 0 else str(num2)
    num3_display = f"( {num3} )" if num3 < 0 else str(num3)
    question_text = f"計算下列各式的值。\n${{ {num1_display} \\times {num2_display} \\times {num3_display} }}$"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_4_problem():
    factor_pairs_list = [(2, 5), (4, 25), (5, 2), (8, 125), (25, 4), (50, 2)]
    base, complement = random.choice(factor_pairs_list)
    num_c = random.choice(range(-12, 0)) if random.random() < 0.5 else random.choice(range(1, 13))
    raw_numbers = [base, complement, num_c]
    for i in range(len(raw_numbers)):
        if random.random() < 0.5:
            raw_numbers[i] = -raw_numbers[i]
    n1, n2, n3 = random.sample(raw_numbers, 3)
    answer = n1 * n2 * n3
    n1_display = f"( {n1} )" if n1 < 0 else str(n1)
    n2_display = f"( {n2} )" if n2 < 0 else str(n2)
    n3_display = f"( {n3} )" if n3 < 0 else str(n3)
    question_text = f"計算 ${{ {n1_display} \\times {n2_display} \\times {n3_display} }}$ 的值。"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_5_problem():
    num_factors = random.randint(4, 8)
    factors_list = []
    negative_count = 0
    for _ in range(num_factors):
        abs_value = random.randint(2, 20)
        is_negative = random.choice([True, False])
        if is_negative:
            factor = -abs_value
            negative_count += 1
        else:
            factor = abs_value
        factors_list.append(factor)
    answer = "正數" if negative_count % 2 == 0 else "負數"
    display_factors = [f"( {factor} )" if factor < 0 else str(factor) for factor in factors_list]
    expression_latex = " \\times ".join(display_factors)
    question_text = f"判斷 ${{ {expression_latex} }}$ 的計算結果是一個正數還是負數？說明你判斷的理由。"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

dispatcher_list = [generate_type_1_problem, generate_type_2_problem, generate_type_3_problem, generate_type_4_problem, generate_type_5_problem]

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        else: return generate_type_1_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
