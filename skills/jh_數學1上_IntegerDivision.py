# ==============================================================================
# ID: jh_數學1上_IntegerDivision
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Gemini Plan + Qwen Code)
# Duration: 143.81s | RAG: 2 examples
# Created At: 2026-01-06 15:59:25
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



def generate_type_A_problem():
    quotient_abs = random.randint(2, 12)
    divisor_abs = random.randint(2, 9)
    sign_dividend = random.choice([1, -1])
    sign_divisor = random.choice([1, -1])
    dividend = quotient_abs * divisor_abs * sign_dividend
    divisor = divisor_abs * sign_divisor
    question_text = f"計算 ({dividend}) ÷ ({divisor})"
    answer = to_latex(dividend / divisor)
    correct_answer = str(int(dividend / divisor))
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate_type_B_problem():
    quotient_abs = random.randint(5, 20)
    divisor_abs = random.randint(4, 18)
    sign_dividend = random.choice([1, -1])
    sign_divisor = random.choice([1, -1])
    dividend = quotient_abs * divisor_abs * sign_dividend
    divisor = divisor_abs * sign_divisor
    question_text = f"計算 ({dividend}) ÷ ({divisor})"
    answer = to_latex(dividend / divisor)
    correct_answer = str(int(dividend / divisor))
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate_type_C_problem():
    quotient1_abs = random.randint(2, 10)
    divisor1_abs = random.randint(2, 8)
    sign1_dividend = random.choice([1, -1])
    sign1_divisor = random.choice([1, -1])
    dividend1 = quotient1_abs * divisor1_abs * sign1_dividend
    divisor1 = divisor1_abs * sign1_divisor
    
    quotient2_abs = random.randint(2, 10)
    divisor2_abs = random.randint(2, 8)
    sign2_dividend = random.choice([1, -1])
    sign2_divisor = random.choice([1, -1])
    dividend2 = quotient2_abs * divisor2_abs * sign2_dividend
    divisor2 = divisor2_abs * sign2_divisor
    
    operator = random.choice(['+', '-'])
    
    question_text = f"計算 (({dividend1}) ÷ ({divisor1})) {operator} (({dividend2}) ÷ ({divisor2}))"
    if operator == '+':
        answer = to_latex((dividend1 / divisor1) + (dividend2 / divisor2))
        correct_answer = str(int((dividend1 / divisor1) + (dividend2 / divisor2)))
    else:
        answer = to_latex((dividend1 / divisor1) - (dividend2 / divisor2))
        correct_answer = str(int((dividend1 / divisor1) - (dividend2 / divisor2)))
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate(level=1):
    type = random.choice(['type_A', 'type_B', 'type_C'])
    if type == 'type_A': return generate_type_A_problem()
    elif type == 'type_B': return generate_type_B_problem()
    else: return generate_type_C_problem()