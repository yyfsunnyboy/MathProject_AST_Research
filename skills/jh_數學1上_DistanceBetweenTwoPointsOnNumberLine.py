# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 212.58s | RAG: 6 examples
# Created At: 2026-01-07 22:05:27
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
    a_coord = random.randint(-15, -1)
    b_coord = random.randint(1, 15)
    while a_coord >= b_coord:
        a_coord = random.randint(-15, -1)
        b_coord = random.randint(1, 15)
    
    answer = abs(b_coord - a_coord)
    question_text = f"數線上有 A ( {a_coord} )、B ( {b_coord} ) 兩點，則 A、B 兩點的距離 AB 為多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    c_coord = random.randint(-20, -10)
    d_coord = random.randint(-9, -1)
    while c_coord >= d_coord:
        c_coord = random.randint(-20, -10)
        d_coord = random.randint(-9, -1)
    
    answer = abs(d_coord - c_coord)
    question_text = f"數線上有 C ( {c_coord} )、D ( {d_coord} ) 兩點，則 C、D 兩點的距離 CD 為多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_3_problem():
    b_coord = random.randint(2, 12)
    distance = random.randint(2, 10)
    
    a1 = b_coord + distance
    a2 = b_coord - distance
    
    answer = sorted([a1, a2])
    question_text = f"數線上有 A ( a )、B ( {b_coord} ) 兩點，如果 AB={distance}，則 a 可能是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_4_problem():
    d_coord = random.randint(5, 15)
    distance = random.randint(3, 8)
    
    c1 = d_coord + distance
    c2 = d_coord - distance
    
    answer = sorted([c1, c2])
    question_text = f"數線上有 C ( c )、D ( {d_coord} ) 兩點，如果 CD={distance}，則 c 可能是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_5_problem():
    a_coord = random.randint(5, 15)
    b_coord = random.randint(-15, -5)
    while (a_coord + b_coord) % 2 != 0:
        a_coord = random.randint(5, 15)
        b_coord = random.randint(-15, -5)
    
    answer = (a_coord + b_coord) // 2
    question_text = f"數線上有 A ( {a_coord} )、B ( {b_coord} )、C ( c ) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_6_problem():
    a_coord = random.randint(-15, -5)
    b_coord = random.randint(5, 15)
    while (a_coord + b_coord) % 2 != 0:
        a_coord = random.randint(-15, -5)
        b_coord = random.randint(5, 15)
    
    answer = (a_coord + b_coord) // 2
    question_text = f"數線上有 A ( {a_coord} )、B ( {b_coord} )、C ( c ) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
