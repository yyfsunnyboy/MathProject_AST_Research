# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 36.12s | RAG: 8 examples
# Created At: 2026-01-07 16:06:56
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
    A = random.randint(20, 100)
    B = random.randint(10, 90)
    C = random.randint(-40, 40)
    answer = -A + B + C
    question_text = f"計算下列各式的值。 ${{ {{{A}}} + {{{B}}}| - {{{C}}} }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_2_problem():
    A = random.randint(10, 60)
    B = random.randint(5, 30)
    C = random.randint(10, 40)
    D = random.randint(5, 20)
    while C == D:
        D = random.randint(5, 20)
    inner_abs_val = -C + D
    answer = abs(-A) + B - abs(inner_abs_val)
    question_text = f"計算下列各式的值。 ${{ |-{{{A}}}| - (-{{{B}}}) - |-{{{C}}} + {{{D}}}| }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_3_problem():
    X = random.randint(20, 60)
    A = random.randint(30, 70)
    B = random.randint(10, 40)
    C = random.randint(5, 25)
    inner_val = -A + B
    answer = X + abs(inner_val) - C
    question_text = f"計算下列各式的值。 ${{ {{{X}}} + |(-{{{A}}}) + {{{B}}}| - {{{C}}} }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_4_problem():
    A = random.randint(10, 60)
    B = random.randint(5, 30)
    C = random.randint(10, 40)
    D = random.randint(5, 20)
    while C == D:
        D = random.randint(5, 20)
    inner_abs_val = -C + D
    answer = abs(-A) + B - abs(inner_abs_val)
    question_text = f"計算下列各式的值。 ${{ |-{{{A}}}| - (-{{{B}}}) - |-{{{C}}} + {{{D}}}| }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_5_problem():
    A = random.randint(2, 10)
    B = random.randint(2, 10)
    val1 = -(A + B)
    val2 = -A - B
    is_same = (val1 == val2)
    answer = "相同" if is_same else "不相同"
    question_text = f"比較下列各題中，兩式的運算結果是否相同。 ${{ -( {{{A}}} + {{{B}}} ) }}$ 和 ${{ -{{{A}}} - {{{B}}} }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_6_problem():
    A = random.randint(2, 8)
    B = random.randint(2, 8)
    val1 = -(-A - B)
    val2 = A + B
    is_same = (val1 == val2)
    answer = "相同" if is_same else "不相同"
    question_text = f"比較下列各題中，兩式的運算結果是否相同。 ${{ -(-{{{A}}} - {{{B}}} ) }}$ 和 ${{ {{{A}}} + {{{B}}} }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_7_problem():
    X = random.randint(1, 10)
    A = random.randint(2, 8)
    B = random.randint(2, 8)
    val1 = -X - (-A + B)
    val2 = -X + A - B
    is_same = (val1 == val2)
    answer = "相同" if is_same else "不相同"
    question_text = f"比較下列各題中，兩式的運算結果是否相同。 ${{ (-{{{X}}}) - (-{{{A}}} + {{{B}}}) }}$ 和 ${{ (-{{{X}}}) + {{{A}}} - {{{B}}} }}$"
    return {
        "question": question_text,
        "answer": answer
    }

def generate_type_8_problem():
    A = random.randint(100, 900)
    B = random.randint(10, 500)
    answer = A - (B + A)
    question_text = f"計算下列各式的值。 ${{ {{{A}}} - ( {{{B}}} + {{{A}}} ) }}$"
    return {
        "question": question_text,
        "answer": answer
    }

# Dispatcher list
problem_generators = [
    generate_type_1_problem, 
    generate_type_2_problem, 
    generate_type_3_problem, 
    generate_type_4_problem, 
    generate_type_5_problem, 
    generate_type_6_problem, 
    generate_type_7_problem, 
    generate_type_8_problem
]

# Example usage:
problem = random.choice(problem_generators)()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem', 'generate_type_8_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        elif selected_type == 'generate_type_8_problem': return generate_type_8_problem()
        else: return generate_type_1_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_type_1_problem()
