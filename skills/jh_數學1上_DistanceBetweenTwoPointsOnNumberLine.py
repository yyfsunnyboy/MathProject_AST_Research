# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Gemini Plan + Qwen Code)
# Duration: 154.52s | RAG: 6 examples
# Created At: 2026-01-06 15:47:23
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
    coord1 = random.randint(-20, 20)
    coord2 = random.randint(-20, 20)
    
    while coord1 == coord2:
        coord2 = random.randint(-20, 20)
    
    result = abs(coord1 - coord2)
    
    question_text = f"數線上有 A ({coord1})、B ({coord2}) 兩點，則 A、B 兩點的距離 AB 為多少？"
    answer = to_latex(result)
    correct_answer = str(result)
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate_type_B_problem():
    known_coord = random.randint(-20, 20)
    distance = random.randint(1, 15)
    unknown_char = random.choice(['a', 'b', 'c', 'x', 'y'])
    
    result1 = known_coord + distance
    result2 = known_coord - distance
    
    question_text = f"數線上有 A ({unknown_char})、B ({known_coord}) 兩點，如果 AB={distance}，則 {unknown_char} 可能是多少？"
    answer = to_latex(result1) + " 或 " + to_latex(result2)
    correct_answer = str(result1) + " 或 " + str(result2)
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate_type_C_problem():
    coord1 = random.randint(-20, 20)
    coord2 = random.randint(-20, 20)
    
    while (coord1 + coord2) % 2 != 0:
        coord2 = random.randint(-20, 20)
    
    unknown_char = random.choice(['c', 'm', 'x'])
    
    result = (coord1 + coord2) / 2
    
    question_text = f"數線上有 A ({coord1})、B ({coord2})、C ({unknown_char}) 三點，若 C 為 A、B 的中點，則 {unknown_char} 是多少？"
    answer = to_latex(result)
    correct_answer = str(result)
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate(level=1):
    type = random.choice(['type_A', 'type_B', 'type_C'])
    if type == 'type_A': return generate_type_A_problem()
    elif type == 'type_B': return generate_type_B_problem()
    else: return generate_type_C_problem()