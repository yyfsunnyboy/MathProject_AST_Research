# ==============================================================================
# ID: jh_數學1上_PositiveAndNegativeNumbers
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 44.45s | RAG: 3 examples
# Created At: 2026-01-07 16:09:16
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
    # Generate a reference point and its LaTeX representation
    ref_sign = random.choice([-1, 1])
    ref_val_abs = round(random.uniform(1.0, 5.0), 1)
    reference_num_value = ref_sign * ref_val_abs
    reference_num_latex = f"{reference_num_value:.1f}"

    # Generate a list of numbers and their LaTeX representations
    num_data_list = []
    for _ in range(6):
        val = random.randint(-20, 20)
        if val == 0:
            continue
        latex_str = str(val)
        num_data_list.append((val, latex_str))

    # Shuffle the list to randomize the order of numbers
    random.shuffle(num_data_list)

    # Construct the LaTeX string for the list of numbers
    num_list_latex = "、".join([latex_str for _, latex_str in num_data_list])

    # Classify numbers and build answer lists
    negative_numbers_latex_list = []
    same_sign_numbers_latex_list = []
    for val, latex_str in num_data_list:
        if val < 0:
            negative_numbers_latex_list.append(latex_str)
        if (val > 0 and reference_num_value > 0) or (val < 0 and reference_num_value < 0):
            same_sign_numbers_latex_list.append(latex_str)

    # Format the final answer strings
    negative_numbers_latex = "、".join(negative_numbers_latex_list) if negative_numbers_latex_list else "無"
    same_sign_numbers_latex = "、".join(same_sign_numbers_latex_list) if same_sign_numbers_latex_list else "無"

    # Construct the question and answer
    question = f"下列各數中，哪些是負數？哪些與${{{reference_num_latex}}}$是同號數？\n\n${{{num_list_latex}}}$"
    answer = {
        "負數": negative_numbers_latex,
        f"${{{reference_num_latex}}}$的同號數": same_sign_numbers_latex
    }

    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_2_problem():
    # Generate a reference point and its LaTeX representation
    ref_sign = random.choice([-1, 1])
    ref_val_abs = round(random.uniform(1.0, 5.0), 1)
    reference_num_value = ref_sign * ref_val_abs
    reference_num_latex = f"{reference_num_value:.1f}"

    # Generate a list of numbers and their LaTeX representations
    num_data_list = []
    for _ in range(6):
        val = round(random.uniform(-10.0, 10.0), 1)
        if val == 0.0:
            continue
        latex_str = f"{val:.1f}"
        num_data_list.append((val, latex_str))

    # Shuffle the list to randomize the order of numbers
    random.shuffle(num_data_list)

    # Construct the LaTeX string for the list of numbers
    num_list_latex = "、".join([latex_str for _, latex_str in num_data_list])

    # Classify numbers and build answer lists
    negative_numbers_latex_list = []
    same_sign_numbers_latex_list = []
    for val, latex_str in num_data_list:
        if val < 0.0:
            negative_numbers_latex_list.append(latex_str)
        if (val > 0.0 and reference_num_value > 0) or (val < 0.0 and reference_num_value < 0):
            same_sign_numbers_latex_list.append(latex_str)

    # Format the final answer strings
    negative_numbers_latex = "、".join(negative_numbers_latex_list) if negative_numbers_latex_list else "無"
    same_sign_numbers_latex = "、".join(same_sign_numbers_latex_list) if same_sign_numbers_latex_list else "無"

    # Construct the question and answer
    question = f"下列各數中，哪些是負數？哪些與${{{reference_num_latex}}}$是同號數？\n\n${{{num_list_latex}}}$"
    answer = {
        "負數": negative_numbers_latex,
        f"${{{reference_num_latex}}}$的同號數": same_sign_numbers_latex
    }

    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
def generate_type_3_problem():
    # Generate a reference point and its LaTeX representation
    ref_sign = random.choice([-1, 1])
    ref_val_abs = round(random.uniform(1.0, 5.0), 1)
    reference_num_value = ref_sign * ref_val_abs
    reference_num_latex = f"{reference_num_value:.1f}"

    # Generate a list of numbers and their LaTeX representations
    num_data_list = []
    for _ in range(6):
        val = random.randint(-20, 20)
        if val == 0:
            continue
        latex_str = str(val)
        num_data_list.append((val, latex_str))

    # Shuffle the list to randomize the order of numbers
    random.shuffle(num_data_list)

    # Construct the LaTeX string for the list of numbers
    num_list_latex = "、".join([latex_str for _, latex_str in num_data_list])

    # Classify numbers and build answer lists
    negative_numbers_latex_list = []
    same_sign_numbers_latex_list = []
    for val, latex_str in num_data_list:
        if val < 0:
            negative_numbers_latex_list.append(latex_str)
        if (val > 0 and reference_num_value > 0) or (val < 0 and reference_num_value < 0):
            same_sign_numbers_latex_list.append(latex_str)

    # Format the final answer strings
    negative_numbers_latex = "、".join(negative_numbers_latex_list) if negative_numbers_latex_list else "無"
    same_sign_numbers_latex = "、".join(same_sign_numbers_latex_list) if same_sign_numbers_latex_list else "無"

    # Construct the question and answer
    question = f"下列各數中，哪些是負數？哪些與${{{reference_num_latex}}}$是同號數？\n\n${{{num_list_latex}}}$"
    answer = {
        "負數": negative_numbers_latex,
        f"${{{reference_num_latex}}}$的同號數": same_sign_numbers_latex
    }

    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
# Dispatcher list to select a problem type randomly
dispatcher_list = [generate_type_1_problem, generate_type_2_problem, generate_type_3_problem]

def generate_problem():
    # Select a random problem generator from the dispatcher list
    selected_generator = random.choice(dispatcher_list)
    # Generate and return the problem and answer
    question, answer = selected_generator()
    return {'question_text': question, 'answer': answer, 'correct_answer': answer}
# Example usage:
question, answer = generate_problem()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_problem': return generate_problem()
        elif selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        else: return generate_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_problem()
