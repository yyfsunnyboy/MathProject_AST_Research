# ==============================================================================
# ID: jh_數學1上_IntegerMultiplication
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 515.62s | RAG: 5 examples
# Created At: 2026-01-07 22:29:13
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



def format_number(num):
    return f"{num}" if num >= 0 else f"({num})"

def generate_type_1_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    answer = num1 * num2
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    question = f"計算 ${{ {num1_str} \\times {num2_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_2_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    val3 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    num3 = val3 * sign3
    answer = num1 * num2 * num3
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_3_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    val3 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    num3 = val3 * sign3
    answer = num1 * num2 * num3
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_4_problem():
    factor_25_val = random.choice([25, -25])
    factor_4_val = random.choice([4, -4])
    other_factor_abs = random.randint(5, 30)
    while other_factor_abs in [10, 20]:
        other_factor_abs = random.randint(5, 30)
    other_factor_sign = random.choice([-1, 1])
    num1 = factor_25_val
    num2 = factor_4_val
    num3 = other_factor_abs * other_factor_sign
    factors = [num1, num2, num3]
    random.shuffle(factors)
    answer = factors[0] * factors[1] * factors[2]
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_5_problem():
    num_factors = random.randint(3, 7)
    factors_raw = []
    negative_count = 0
    for _ in range(num_factors):
        abs_val = random.randint(2, 20)
        sign = random.choice([-1, 1])
        if sign == -1:
            negative_count += 1
        factors_raw.append(abs_val * sign)
    product_sign_str = "正數" if negative_count % 2 == 0 else "負數"
    factors_str = " \\times ".join([format_number(num) for num in factors_raw])
    reasoning_str = f"因為算式中有 {negative_count} 個負數相乘，"
    if negative_count % 2 == 0:
        reasoning_str += "且 {negative_count} 是偶數，所以結果是正數。"
    else:
        reasoning_str += "且 {negative_count} 是奇數，所以結果是負數。"
    question = f"判斷 ${{ {factors_str} }}$ 的計算結果是一個正數還是負數？說明你判斷的理由。"
    return {"question": question, "answer": {"sign": product_sign_str, "reasoning": reasoning_str}}

def generate_type_1_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    answer = num1 * num2
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    question = f"計算 ${{ {num1_str} \\times {num2_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_2_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    val3 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    num3 = val3 * sign3
    answer = num1 * num2 * num3
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_3_problem():
    val1 = random.randint(-20, 20)
    val2 = random.randint(-20, 20)
    val3 = random.randint(-20, 20)
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])
    num1 = val1 * sign1
    num2 = val2 * sign2
    num3 = val3 * sign3
    answer = num1 * num2 * num3
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_4_problem():
    factor_25_val = random.choice([25, -25])
    factor_4_val = random.choice([4, -4])
    other_factor_abs = random.randint(5, 30)
    while other_factor_abs in [10, 20]:
        other_factor_abs = random.randint(5, 30)
    other_factor_sign = random.choice([-1, 1])
    num1 = factor_25_val
    num2 = factor_4_val
    num3 = other_factor_abs * other_factor_sign
    factors = [num1, num2, num3]
    random.shuffle(factors)
    answer = factors[0] * factors[1] * factors[2]
    num1_str = format_number(num1)
    num2_str = format_number(num2)
    num3_str = format_number(num3)
    question = f"計算 ${{ {num1_str} \\times {num2_str} \\times {num3_str} }}$ 的值。"
    return {"question": question, "answer": answer}

def generate_type_5_problem():
    num_factors = random.randint(3, 7)
    factors_raw = []
    negative_count = 0
    for _ in range(num_factors):
        abs_val = random.randint(2, 20)
        sign = random.choice([-1, 1])
        if sign == -1:
            negative_count += 1
        factors_raw.append(abs_val * sign)
    product_sign_str = "正數" if negative_count % 2 == 0 else "負數"
    factors_str = " \\times ".join([format_number(num) for num in factors_raw])
    reasoning_str = f"因為算式中有 {negative_count} 個負數相乘，"
    if negative_count % 2 == 0:
        reasoning_str += "且 {negative_count} 是偶數，所以結果是正數。"
    else:
        reasoning_str += "且 {negative_count} 是奇數，所以結果是負數。"
    question = f"判斷 ${{ {factors_str} }}$ 的計算結果是一個正數還是負數？說明你判斷的理由。"
    return {"question": question, "answer": {"sign": product_sign_str, "reasoning": reasoning_str}}

# Example usage:
problem = generate_type_1_problem()

# [Auto-Injected Robust Dispatcher by v8.0]
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
        return generate_type_1_problem()
