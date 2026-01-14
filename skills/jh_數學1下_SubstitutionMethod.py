# ==============================================================================
# ID: jh_數學1下_SubstitutionMethod
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 60.90s | RAG: 3 examples
# Created At: 2026-01-11 22:23:17
# Fix Status: [Repaired]
#==============================================================================


import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
# --- 4. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization (LaTeX spaces).
    """
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
    return result


import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# Environment tools (to_latex, fmt_num) are injected and should not be defined here.
# For local testing, you might use stubs:
# def to_latex(n):
#     # This stub assumes n is a number or a string that should be treated as LaTeX math.
#     # For equation strings like "2x+3y=7", it should ideally return them as-is
#     # when used inside a LaTeX math environment (like `cases`).
#     # For numbers, it would typically format them for math mode.
#     if isinstance(n, (int, float)):
#         return f"${n}$"
#     return str(n) # Assume equation strings are already in a suitable format

# def fmt_num(n):
#     # This stub formats numbers for display in regular text.
#     return str(n) if isinstance(n, int) else f"{n:.2f}"


def generate_problem():
    # 1. Generate integer solutions for x and y
    x_sol = random.randint(-4, 4)
    y_sol = random.randint(-4, 4)

    # Helper function to format a coefficient with its variable (e.g., "x", "-y", "2x")
    def format_term(coeff, variable):
        if coeff == 0:
            return ""
        elif coeff == 1:
            return f"{variable}"
        elif coeff == -1:
            return f"-{variable}"
        else:
            return f"{coeff}{variable}"

    # Helper function to combine x and y terms into an equation side string
    def combine_terms(x_term, y_term):
        if not x_term and not y_term:
            return "0"  # Should not happen if coefficients are properly generated
        elif not x_term:
            return y_term
        elif not y_term:
            return x_term
        else:
            # Handle sign for y_term when combining
            if y_term.startswith('-'):
                return f"{x_term}{y_term}"
            else:
                return f"{x_term}+{y_term}"

    # Helper function to generate coefficients (A, B, C) for an equation Ax + By = C
    # given a solution (x_s, y_s), ensuring A and B are not both zero.
    def get_coeffs(x_s, y_s):
        while True:
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
            if a == 0 and b == 0:  # Avoid trivial equation 0 = C
                continue
            c = a * x_s + b * y_s
            return a, b, c

    # Enforce structural diversity by choosing one of 3 equation structures
    equation_structure_type = random.choice([1, 2, 3])

    eq1_str = ""
    eq2_str = ""
    line1_params = {}  # Parameters for plotting the first line
    line2_params = {}  # Parameters for plotting the second line

    if equation_structure_type == 1:
        # Structure 1: A1x + B1y = C1 and A2x + B2y = C2 (Standard form for both)
        while True:
            a1, b1, c1 = get_coeffs(x_sol, y_sol)
            a2, b2, c2 = get_coeffs(x_sol, y_sol)
            # Ensure a unique solution by checking the determinant (A1*B2 - A2*B1 != 0)
            if a1 * b2 - a2 * b1 != 0:
                break
        
        x1_term = format_term(a1, 'x')
        y1_term = format_term(b1, 'y')
        eq1_str = f"{combine_terms(x1_term, y1_term)} = {c1}"

        x2_term = format_term(a2, 'x')
        y2_term = format_term(b2, 'y')
        eq2_str = f"{combine_terms(x2_term, y2_term)} = {c2}"

        line1_params = {'type': 'standard', 'coeffs': (a1, b1, c1)}
        line2_params = {'type': 'standard', 'coeffs': (a2, b2, c2)}

    elif equation_structure_type == 2:
        # Structure 2: y = M1x + B_const1 and A2x + B2y = C2 (Slope-intercept + Standard)
        m1 = random.randint(-3, 3)  # Slope for the first equation
        b_const1 = y_sol - m1 * x_sol # Calculate y-intercept based on solution

        # Format y = M1x + B_const1
        if m1 == 0:
            eq1_str = f"y = {b_const1}"
        elif m1 == 1:
            eq1_str = f"y = x"
            if b_const1 != 0:
                eq1_str += f" + {b_const1}" if b_const1 > 0 else f" {b_const1}"
        elif m1 == -1:
            eq1_str = f"y = -x"
            if b_const1 != 0:
                eq1_str += f" + {b_const1}" if b_const1 > 0 else f" {b_const1}"
        else:
            eq1_str = f"y = {m1}x"
            if b_const1 != 0:
                eq1_str += f" + {b_const1}" if b_const1 > 0 else f" {b_const1}"
        
        # Generate coefficients for A2x + B2y = C2
        while True:
            a2, b2, c2 = get_coeffs(x_sol, y_sol)
            # Ensure unique solution:
            # If B2 is 0, the second equation is a vertical line (A2x = C2), unique if A2 != 0.
            # If B2 is not 0, substitute y = M1x + B_const1 into A2x + B2y = C2.
            # This gives (A2 + B2*M1)x = C2 - B2*B_const1. Unique if (A2 + B2*M1) != 0.
            if (b2 == 0 and a2 != 0) or (b2 != 0 and (a2 + b2 * m1) != 0):
                break

        x2_term = format_term(a2, 'x')
        y2_term = format_term(b2, 'y')
        eq2_str = f"{combine_terms(x2_term, y2_term)} = {c2}"
        
        line1_params = {'type': 'slope_intercept', 'coeffs': (m1, b_const1)}
        line2_params = {'type': 'standard', 'coeffs': (a2, b2, c2)}

    else: # equation_structure_type == 3
        # Structure 3: A1x + B1y = C1 and M2y = N2x + P2 (Standard + Rearranged)
        while True:
            a1, b1, c1 = get_coeffs(x_sol, y_sol)
            
            m2 = random.randint(-4, 4) # Coefficient of y in the second equation
            n2 = random.randint(-4, 4) # Coefficient of x in the second equation
            
            if m2 == 0 and n2 == 0: # Avoid trivial 0 = P2
                continue
            
            p2 = m2 * y_sol - n2 * x_sol # Calculate constant term based on solution

            # Ensure unique solution:
            # The system is A1x + B1y = C1 and -N2x + M2y = P2.
            # Determinant is A1*M2 - B1*(-N2) = A1*M2 + B1*N2. This must be non-zero.
            if a1 * m2 + b1 * n2 != 0:
                break
        
        x1_term = format_term(a1, 'x')
        y1_term = format_term(b1, 'y')
        eq1_str = f"{combine_terms(x1_term, y1_term)} = {c1}"

        n2_term = format_term(n2, 'x')
        m2_term = format_term(m2, 'y')
        
        # Format M2y = N2x + P2
        if m2 == 0: # This means it's a vertical line: N2x = -P2
            eq2_str = f"{n2_term} = {-p2}" 
        elif n2 == 0: # This means it's a horizontal line: M2y = P2
            eq2_str = f"{m2_term} = {p2}"
        else:
            eq2_str = f"{m2_term} = {n2_term}"
            if p2 != 0:
                eq2_str += f" + {p2}" if p2 > 0 else f" {p2}"

        line1_params = {'type': 'standard', 'coeffs': (a1, b1, c1)}
        line2_params = {'type': 'rearranged', 'coeffs': (m2, n2, p2)} # M2y = N2x + P2

    # --- Plotting the intersection ---
    fig, ax = plt.subplots(figsize=(6, 6))

    # Determine plot range dynamically based on solution, with some padding
    x_range_padding = max(abs(x_sol) + 2, 5) 
    y_range_padding = max(abs(y_sol) + 2, 5)
    x_plot_min, x_plot_max = x_sol - x_range_padding, x_sol + x_range_padding
    y_plot_min, y_plot_max = y_sol - y_range_padding, y_sol + y_range_padding

    x_vals = np.linspace(x_plot_min, x_plot_max, 400)

    # Helper function to plot a line based on its parameters
    def plot_line(params, ax, label, color):
        line_type = params['type']
        if line_type == 'standard': # Ax + By = C
            A, B, C = params['coeffs']
            if B == 0:  # Vertical line Ax = C => x = C/A
                if A != 0:
                    ax.axvline(x=C/A, color=color, linestyle='--', label=label)
            else:  # By = -Ax + C => y = (-A/B)x + (C/B)
                y_vals = (-A/B) * x_vals + (C/B)
                ax.plot(x_vals, y_vals, color=color, label=label)
        elif line_type == 'slope_intercept': # y = Mx + B_const
            m, b = params['coeffs']
            y_vals = m * x_vals + b
            ax.plot(x_vals, y_vals, color=color, label=label)
        elif line_type == 'rearranged': # M2y = N2x + P2
            M2, N2, P2 = params['coeffs']
            if M2 == 0:  # Vertical line N2x = -P2 => x = -P2/N2
                if N2 != 0:
                    ax.axvline(x=-P2/N2, color=color, linestyle='--', label=label)
            else:  # y = (N2/M2)x + (P2/M2)
                y_vals = (N2/M2) * x_vals + (P2/M2)
                ax.plot(x_vals, y_vals, color=color, label=label)

    plot_line(line1_params, ax, 'L1', 'blue')
    plot_line(line2_params, ax, 'L2', 'green')

    # Plot the intersection point
    ax.plot(x_sol, y_sol, 'ro', markersize=8, label=f'交點 ({fmt_num(x_sol)}, {fmt_num(y_sol)})')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('幾何圖形解')
    ax.grid(True)
    ax.axhline(0, color='black',linewidth=0.5)
    ax.axvline(0, color='black',linewidth=0.5)
    ax.set_aspect('equal', adjustable='box')
    ax.legend()

    # Set plot limits to ensure visibility of the intersection and surrounding area
    ax.set_xlim(x_plot_min, x_plot_max)
    ax.set_ylim(y_plot_min, y_plot_max)

    # Save plot to a BytesIO object and encode to Base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig) # Close the plot to free memory
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # --- Construct problem text and correct answer ---
    # Equation strings (eq1_str, eq2_str) are assumed to be in a format
    # suitable for direct inclusion within a LaTeX math environment like `cases`.
    question_text = f"請解以下聯立方程式：\n" \
                    f"\\begin{{cases}}\n" \
                    f"  {eq1_str} \\\\\n" \
                    f"  {eq2_str}\n" \
                    f"\\end{{cases}}\n" \
                    f"(答案格式：x=_, y=_)"

    # Correct answer must be in the exact specified format
    correct_answer = f"x={x_sol},y={y_sol}"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "visual_aids": [{"type": "image/png", "value": image_base64}]
    }


# [Auto-Injected Smart Dispatcher v8.7]
def generate(level=1):
    if level == 1:
        types = ['generate_problem']
        selected = random.choice(types)
    else:
        types = ['generate_problem']
        selected = random.choice(types)
    if selected == 'generate_problem': return generate_problem()
    return generate_problem()

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
