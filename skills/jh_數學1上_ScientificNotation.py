# ==============================================================================
# ID: jh_數學1上_ScientificNotation
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Dynamic & Robust)
# Duration: 48.14s | RAG: 7 examples
# Created At: 2026-01-07 10:52:02
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



def _generate_scientific_coeff_str(min_int_part=1, max_int_part=9, decimal_places=None):
    """
    Generates a float coefficient (e.g., 1.23, 5.0, 9.8) for scientific notation,
    and returns its string representation suitable for LaTeX display.
    
    Args:
        min_int_part (int): Minimum value for the integer part (1-9).
        max_int_part (int): Maximum value for the integer part (1-9).
        decimal_places (int, optional): Number of decimal places (0, 1, or 2).
                                        If None, a random choice is made.
    Returns:
        str: The coefficient as a string (e.g., "5", "1.2", "9.87").
    """
    integer_part = random.randint(min_int_part, max_int_part)
    
    if decimal_places is None:
        actual_decimal_places = random.choice([0, 1, 2])
    else:
        actual_decimal_places = decimal_places

    if actual_decimal_places == 0:
        return str(integer_part)
    elif actual_decimal_places == 1:
        decimal_part = random.randint(0, 9)
        return f"{integer_part}.{decimal_part}"
    else: # actual_decimal_places == 2
        decimal_part = random.randint(0, 99)
        return f"{integer_part}.{decimal_part:02d}" # :02d ensures two digits, e.g., 5.03 not 5.3

def _parse_scientific_coeff_float(coeff_str):
    """
    Converts the string representation of a coefficient (e.g., "5", "1.2", "9.87")
    back to its float value for calculations.
    
    Args:
        coeff_str (str): The coefficient as a string.
    Returns:
        float: The float value of the coefficient.
    """
    return float(coeff_str)

def generate_type_1_problem():
    scientific_coeff_str = _generate_scientific_coeff_str()
    exponent = random.randint(5, 12)
    question = f"若將 ${{ {scientific_coeff_str} \\times 10^{{{exponent}}} }}$ 乘開，則這個數是幾位數？"
    answer = f"{exponent + 1} 位數"
    return question, answer

def generate_type_2_problem():
    scientific_coeff_str = _generate_scientific_coeff_str()
    exponent = random.randint(-12, -5)
    position = abs(exponent)
    question = f"若將 ${{ {scientific_coeff_str} \\times 10^{{{exponent}}} }}$ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
    answer = f"第 {position} 位"
    return question, answer

def generate_type_3_problem():
    coeff1_str = _generate_scientific_coeff_str()
    coeff2_str = _generate_scientific_coeff_str()
    exponent1 = random.randint(5, 10)
    exponent2 = random.randint(-10, -5)
    val1 = _parse_scientific_coeff_float(coeff1_str) * (10 ** exponent1)
    val2 = _parse_scientific_coeff_float(coeff2_str) * (10 ** exponent2)
    if val1 > val2:
        comparison_op = ">"
    elif val1 < val2:
        comparison_op = "<"
    else:
        comparison_op = "="
    question = f"比較兩數的大小，在 __ 中填入＞、＜或=。 ${{ {coeff1_str} \\times 10^{{{exponent1}}} }}$ __ ${{ {coeff2_str} \\times 10^{{{exponent2}}} }}$"
    answer = comparison_op
    return question, answer

def generate_type_4_problem():
    coeff1_str = _generate_scientific_coeff_str()
    coeff2_str = _generate_scientific_coeff_str()
    exponent1 = random.randint(5, 10)
    exponent2 = random.randint(-10, -5)
    val1 = _parse_scientific_coeff_float(coeff1_str) * (10 ** exponent1)
    val2 = _parse_scientific_coeff_float(coeff2_str) * (10 ** exponent2)
    if val1 > val2:
        comparison_op = ">"
    elif val1 < val2:
        comparison_op = "<"
    else:
        comparison_op = "="
    question = f"比較兩數的大小，在 __ 中填入＞、＜或=。 ${{ {coeff1_str} \\times 10^{{{exponent1}}} }}$ __ ${{ {coeff2_str} \\times 10^{{{exponent2}}} }}$"
    answer = comparison_op
    return question, answer

def generate_type_5_problem():
    scientific_coeff_str = _generate_scientific_coeff_str()
    exponent = random.randint(5, 12)
    num_digits = exponent + 1
    question = f"若將 ${{ {scientific_coeff_str} \\times 10^{{{exponent}}} }}$ 乘開，則這個數是幾位數？"
    answer = f"{num_digits} 位數"
    return question, answer

def generate_type_6_problem():
    scientific_coeff_str = _generate_scientific_coeff_str()
    exponent = random.randint(-12, -5)
    position = abs(exponent)
    question = f"若將 ${{ {scientific_coeff_str} \\times 10^{{{exponent}}} }}$ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
    answer = f"第 {position} 位"
    return question, answer

def generate_type_7_problem():
    coeff1_str = _generate_scientific_coeff_str()
    coeff2_str = _generate_scientific_coeff_str()
    exponent1 = random.randint(5, 10)
    exponent2 = random.randint(-10, -5)
    val1 = _parse_scientific_coeff_float(coeff1_str) * (10 ** exponent1)
    val2 = _parse_scientific_coeff_float(coeff2_str) * (10 ** exponent2)
    if val1 > val2:
        comparison_op = ">"
    elif val1 < val2:
        comparison_op = "<"
    else:
        comparison_op = "="
    question = f"比較兩數的大小，在 __ 中填入＞、＜或=。 ${{ {coeff1_str} \\times 10^{{{exponent1}}} }}$ __ ${{ {coeff2_str} \\times 10^{{{exponent2}}} }}$"
    answer = comparison_op
    return question, answer

dispatcher_list = [
    generate_type_1_problem,
    generate_type_2_problem,
    generate_type_3_problem,
    generate_type_4_problem,
    generate_type_5_problem,
    generate_type_6_problem,
    generate_type_7_problem
]

def get_random_question():
    problem_generator = random.choice(dispatcher_list)
    question, answer = problem_generator()
    return question, answer

# Example usage:
question, answer = get_random_question()

# [Auto-Injected Robust Dispatcher by v7.9 System]
def generate(level=1):
    # Automatically dispatch to available type functions found in the code
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem']
    selected_type = random.choice(available_types)
    if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
    elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
    elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
    elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
    elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
    elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
    elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
    else: return generate_type_1_problem()
