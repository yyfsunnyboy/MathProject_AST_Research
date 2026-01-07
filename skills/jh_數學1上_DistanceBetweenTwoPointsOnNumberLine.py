# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 28.69s | RAG: 6 examples
# Created At: 2026-01-07 16:03:09
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
    point_a = random.randint(-15, -1)
    point_b = random.randint(1, 15)
    answer = abs(point_b - point_a)
    question_text = f"數線上有 A ({point_a})、B ({point_b}) 兩點，則 A、B 兩點的距離 AB 為多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_2_problem():
    val1 = random.randint(-15, -1)
    val2 = random.randint(-15, -1)
    while val1 == val2:
        val2 = random.randint(-15, -1)
    point_c = min(val1, val2)
    point_d = max(val1, val2)
    answer = abs(point_d - point_c)
    question_text = f"數線上有 C ({point_c})、D ({point_d}) 兩點，則 C、D 兩點的距離 CD 為多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_3_problem():
    point_b = random.randint(3, 15)
    distance_ab = random.randint(1, min(5, point_b - 1))
    answer1 = point_b + distance_ab
    answer2 = point_b - distance_ab
    answer = f"{answer1} 或 {answer2}"
    question_text = f"數線上有 A ( a )、B ({point_b}) 兩點，如果 AB={distance_ab}，則 a 可能是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_4_problem():
    point_d = random.randint(1, 10)
    distance_cd = random.randint(max(5, point_d + 1), 12)
    answer1 = point_d + distance_cd
    answer2 = point_d - distance_cd
    answer = f"{answer1} 或 {answer2}"
    question_text = f"數線上有 C ( c )、D ({point_d}) 兩點，如果 CD={distance_cd}，則 c 可能是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_5_problem():
    point_a = random.randint(1, 10)
    sum_target = random.randint(-10, -2) * 2
    point_b = sum_target - point_a
    while not (-15 <= point_b <= -1):
        point_a = random.randint(1, 10)
        sum_target = random.randint(-10, -2) * 2
        point_b = sum_target - point_a
    answer = (point_a + point_b) // 2
    question_text = f"數線上有 A ({point_a})、B ({point_b})、C ( c ) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

def generate_type_6_problem():
    point_a = random.randint(-10, -1)
    sum_target = random.randint(2, 10) * 2
    point_b = sum_target - point_a
    while not (1 <= point_b <= 15):
        point_a = random.randint(-10, -1)
        sum_target = random.randint(2, 10) * 2
        point_b = sum_target - point_a
    answer = (point_a + point_b) // 2
    question_text = f"數線上有 A ({point_a})、B ({point_b})、C ( c ) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    return {'question_text': question_text, 'answer': answer, 'correct_answer': answer}

# Dispatcher list
dispatcher_list = [generate_type_1_problem, generate_type_2_problem, generate_type_3_problem, 
                   generate_type_4_problem, generate_type_5_problem, generate_type_6_problem]

# [Auto-Injected Robust Dispatcher by v7.9.3]
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
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
