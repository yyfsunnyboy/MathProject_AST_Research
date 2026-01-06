# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Gemini Plan + Qwen Code)
# Duration: 295.67s | RAG: 8 examples
# Created At: 2026-01-06 16:13:53
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
    # Generate two numbers a and b
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    
    # Ensure a and b are not zero
    while a == 0 or b == 0:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
    
    # Create the expressions
    expr1 = f"{a} + {b}"
    expr2 = f"{a} - (-{b})"
    
    # Calculate the results
    result1 = a + b
    result2 = a - (-b)
    
    # Determine if they are equal
    if result1 == result2:
        answer = "相同"
    else:
        answer = "不相同"
    
    # Return the question and answer
    return f"比較下列各題中，兩式的運算結果是否相同。\n⑴ {expr1} 和 {expr2}\n答案: {answer}"

def generate_type_B_problem():
    # Generate three numbers a, b, c
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    
    # Ensure a, b, and c are not zero
    while a == 0 or b == 0 or c == 0:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
    
    # Create the expressions
    expr1 = f"{c} - ({a} + {b})"
    expr2 = f"{c} - {a} - {b}"
    
    # Calculate the results
    result1 = c - (a + b)
    result2 = c - a - b
    
    # Determine if they are equal
    if result1 == result2:
        answer = "相同"
    else:
        answer = "不相同"
    
    # Return the question and answer
    return f"比較下列各題中，兩式的運算結果是否相同。\n⑴ {expr1} 和 {expr2}\n答案: {answer}"

def generate_type_C_problem():
    # Generate two numbers a and b
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    
    # Ensure a and b are not zero
    while a == 0 or b == 0:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
    
    # Create the expressions
    expr1 = f"{a} + {b}"
    expr2 = f"{a} - (-{b})"
    
    # Calculate the results
    result1 = a + b
    result2 = a - (-b)
    
    # Determine if they are equal
    if result1 == result2:
        answer = "相同"
    else:
        answer = "不相同"
    
    # Return the question and answer
    return f"比較下列各題中，兩式的運算結果是否相同。\n⑴ {expr1} 和 {expr2}\n答案: {answer}"

# Example usage