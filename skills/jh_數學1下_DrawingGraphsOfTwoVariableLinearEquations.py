# ==============================================================================
# ID: jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 88.54s | RAG: 5 examples
# Created At: 2026-01-15 15:04:02
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# --- 2. Number Theory Helpers ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
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

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度，僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理：剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}



import base64
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
import numpy as np
import re # For check function's feedback

# Infrastructure Rule 5: Font settings
# Set font to Microsoft JhengHei for Traditional Chinese, with a sans-serif fallback.
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
# Ensure minus signs are displayed correctly with Chinese fonts.
plt.rcParams['axes.unicode_minus'] = False

# --- V10.2 Coordinate Hardening Spec: Helper Functions ---
def _generate_coordinate_value(min_val, max_val, allow_fractions=False):
    """
    [A. 資料結構鎖死]
    Generates a coordinate value (float_val, (int_part, num, den, is_neg)).
    If allow_fractions is False, num and den will be 0.
    """
    is_neg = random.choice([True, False])
    sign = -1 if is_neg else 1

    # Mostly integers for K12, increased probability to 90% for integers.
    if not allow_fractions or random.random() < 0.9:
        int_part = random.randint(min_val, max_val)
        float_val = float(int_part) * sign # Use float(int_part) * sign to handle -0 correctly as 0.0
        return (float_val, (abs(int_part), 0, 0, is_neg))
    else:
        int_part = random.randint(0, max_val)
        num = random.randint(1, 4) # Numerator 1-4
        den = random.choice([2, 3, 4, 5]) # Denominator 2-5
        while num >= den: # Ensure proper fraction
            num = random.randint(1, 4)
            den = random.choice([2, 3, 4, 5])

        float_val = float(sign * (int_part + num / den))
        return (float_val, (int_part, num, den, is_neg))

def _format_coordinate_latex(data):
    """
    [C. LaTeX 模板規範]
    Formats the coordinate value into a LaTeX string.
    data: (float_val, (int_part, num, den, is_neg))
    """
    float_val, (int_part, num, den, is_neg) = data
    
    # Handle the case where float_val is -0.0, should be 0.0
    if float_val == 0.0:
        return "0"

    sign_str = "-" if is_neg else ""

    if num == 0: # Integer
        return str(int(float_val))
    else: # Fraction or mixed number
        if int_part == 0:
            expr = r"{s}\frac{{{n}}}{{{d}}}".replace("{s}", sign_str).replace("{n}", str(num)).replace("{d}", str(den))
            return expr
        else:
            expr = r"{s}{i}\frac{{{n}}}{{{d}}}".replace("{s}", sign_str).replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))
            return expr

def _draw_coordinate_plane(points_to_plot=None, lines_to_plot=None, x_range=(-10, 10), y_range=(-10, 10), title=""):
    """
    [D. 視覺一致性], [6. 視覺化與輔助函式通用規範]
    Draws a coordinate plane with optional points and lines.
    points_to_plot: List of tuples (x, y, label_latex_str, color) for points to mark.
    lines_to_plot: List of tuples (point1_x, point1_y, point2_x, point2_y, color, linestyle, label) for lines to draw.
    """
    if points_to_plot is None:
        points_to_plot = []
    if lines_to_plot is None:
        lines_to_plot = []

    # Infrastructure Rule 1: Use Figure instead of plt.subplots for thread-safety.
    fig = Figure(figsize=(8, 8))
    canvas = FigureCanvasAgg(fig) # Required for saving to buffer
    ax = fig.add_subplot(111)

    ax.set_aspect('equal') # [D. 視覺一致性]

    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    ax.set_xlim(x_range[0] - 1, x_range[1] + 1)
    ax.set_ylim(y_range[0] - 1, y_range[1] + 1)

    # Draw arrows at the ends of the axes.
    ax.plot(x_range[1] + 0.5, 0, ">k", transform=ax.get_yaxis_transform(), color="k", clip_on=False)
    ax.plot(0, y_range[1] + 0.5, "^k", transform=ax.get_xaxis_transform(), color="k", clip_on=False)

    # Origin label [D. 視覺一致性]
    ax.text(-0.5, -0.8, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')

    # Tick labels for x-axis [Infrastructure Rule 5: 刻度數字僅顯示原點 '0']
    x_ticks = [i for i in range(int(x_range[0]), int(x_range[1]) + 1)]
    ax.set_xticks(x_ticks)
    # Label only '0', suppress other tick labels.
    ax.set_xticklabels(['' if i != 0 else '0' for i in x_ticks], fontsize=10)

    # Tick labels for y-axis [Infrastructure Rule 5: 刻度數字僅顯示原點 '0']
    y_ticks = [i for i in range(int(y_range[0]), int(y_range[1]) + 1)]
    ax.set_yticks(y_ticks)
    # Label only '0', suppress other tick labels.
    ax.set_yticklabels(['' if i != 0 else '0' for i in y_ticks], fontsize=10)

    # Plot points (if any, though for this skill, points_to_plot will be empty)
    for x, y, label, color in points_to_plot:
        ax.plot(x, y, 'o', color=color, markersize=8)
        # Point labels with white halo [D. 視覺一致性] & [Infrastructure Rule 5]
        ax.text(x, y + 0.5, label, fontsize=12, ha='center', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    # Plot lines (if any, though for this skill, lines_to_plot will be empty)
    for x1, y1, x2, y2, color, linestyle, label in lines_to_plot:
        ax.plot([x1, x2], [y1, y2], color=color, linestyle=linestyle, linewidth=2, label=label)
        if label:
            ax.text(x2, y2, label, fontsize=10, ha='left', va='bottom', color=color)

    ax.set_title(title)

    # Convert plot to base64 image [ULTRA VISUAL STANDARDS: dpi=300]
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.5, dpi=300) # Added dpi=300
    fig.clear() # Clear the figure to free memory.
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _normalize_equation_coeffs(eq_str):
    """
    Helper function to parse an equation string and return its normalized coefficients (a, b, c).
    Equation format assumed: ax + by = c (or ax + by + c = 0).
    Returns (a, b, c) as integers, where the first non-zero coefficient is positive,
    and gcd(a, b, c) = 1.
    Returns None for invalid formats or 0=C where C != 0.
    """
    eq_str = eq_str.replace(" ", "")
    # Remove LaTeX braces and potential $ signs if they weren't cleaned before
    eq_str = eq_str.replace(r"\{", "").replace(r"\}", "").replace("$", "")
    
    # Standardize signs for easier splitting
    eq_str = eq_str.replace("-", "+-")

    parts = eq_str.split("=")
    if len(parts) != 2:
        return None # Invalid format

    left_terms_str = parts[0]
    right_terms_str = parts[1]

    # Initialize coefficients for A*x + B*y = C
    A_temp, B_temp, C_temp = 0, 0, 0

    # Parse terms on the left side
    terms = [t for t in left_terms_str.split("+") if t]
    for term in terms:
        if 'x' in term:
            coeff_str = term.replace('x', '')
            if coeff_str == '': coeff_val = 1
            elif coeff_str == '-': coeff_val = -1
            else: coeff_val = int(coeff_str)
            A_temp += coeff_val
        elif 'y' in term:
            coeff_str = term.replace('y', '')
            if coeff_str == '': coeff_val = 1
            elif coeff_str == '-': coeff_val = -1
            else: coeff_val = int(coeff_str)
            B_temp += coeff_val
        else: # Constant term on the left, move to right
            if term: C_temp -= int(term)

    # Parse terms on the right side
    terms = [t for t in right_terms_str.split("+") if t]
    for term in terms:
        if 'x' in term: # x term on right, move to left
            coeff_str = term.replace('x', '')
            if coeff_str == '': coeff_val = 1
            elif coeff_str == '-': coeff_val = -1
            else: coeff_val = int(coeff_str)
            A_temp -= coeff_val
        elif 'y' in term: # y term on right, move to left
            coeff_str = term.replace('y', '')
            if coeff_str == '': coeff_val = 1
            elif coeff_str == '-': coeff_val = -1
            else: coeff_val = int(coeff_str)
            B_temp -= coeff_val
        else: # Constant term on the right, stays on right
            if term: C_temp += int(term)
    
    # Now we have A_temp*x + B_temp*y = C_temp
    A, B, C = A_temp, B_temp, C_temp

    # Normalize: make the first non-zero coefficient positive, divide by GCD
    if A == 0 and B == 0:
        return (0, 0, 0) if C == 0 else None # 0=0 is valid, 0=C (C!=0) is invalid
    
    # Prioritize making the first non-zero coefficient positive
    if A < 0:
        A, B, C = -A, -B, -C
    elif A == 0 and B < 0: # If A is 0, make B positive
        A, B, C = -A, -B, -C
    
    # Calculate GCD, handling cases where some coefficients are zero
    common_divisor = abs(math.gcd(A, math.gcd(B, C)))
    if common_divisor == 0: # This case should only happen if A=B=C=0, which is handled above
        return (0,0,0) # Represents the equation 0=0
    
    A //= common_divisor
    B //= common_divisor
    C //= common_divisor
    
    return (A, B, C)


# --- Top-level Functions ---
def generate(level=1):
    """
    [3. 頂層函式], [4. 隨機分流], [10. 隨機生成]
    Generates a K12 math problem for drawing or analyzing linear equations.

    Problem Type Mapping (Strictly following MANDATORY MIRRORING RULES):
    1: Draw general form ax+by=c (Maps to RAG Ex 1, 2)
    2: Find intercepts & quadrant for ax+by=c (Maps to RAG Ex 3, 4)
    3: Draw horizontal line y=k (Maps to RAG Ex 5a)
    4: Draw vertical line x=k (Maps to RAG Ex 5b)
    """
    problem_type = random.choice([1, 2, 3, 4]) 

    x_range = (-10, 10)
    y_range = (-10, 10)

    question_text = ""
    correct_answer_for_check = "" # Used for the `check` function (canonical equation string)
    full_correct_answer_display = "" # The full detailed answer string for display if user is wrong
    image_base64 = ""

    if problem_type == 1: # Type 1 (Maps to RAG Ex 1, 2): General form ax + by = c (DRAW)
        # [10. 數據禁絕常數] - Generate random coefficients.
        a_val, b_val, c_val = 0, 0, 0
        
        # Ensure a, b are non-zero for this general type, and c can be zero.
        # Ensure intercepts are within a reasonable range for drawing.
        while a_val == 0 or b_val == 0 or \
              (c_val != 0 and (abs(c_val / a_val) > 10 or abs(c_val / b_val) > 10)) or \
              (c_val == 0 and (abs(a_val) + abs(b_val) < 2)): # If c=0, ensure not 0x+0y=0
            a_val = random.randint(-4, 4)
            b_val = random.randint(-4, 4)
            c_val = random.randint(-15, 15)

        # Normalize coefficients for canonical equation string.
        gcd_val = math.gcd(a_val, math.gcd(b_val, c_val))
        a_val //= gcd_val
        b_val //= gcd_val
        c_val //= gcd_val

        # Ensure the leading coefficient (a) is positive or if a=0, b is positive.
        if a_val < 0:
            a_val, b_val, c_val = -a_val, -b_val, -c_val
        elif a_val == 0 and b_val < 0:
            a_val, b_val, c_val = -a_val, -b_val, -c_val

        # Format equation string for question text [5. LaTeX 安全]
        a_term_str = ""
        if a_val == 1: a_term_str = "x"
        elif a_val == -1: a_term_str = "-x"
        elif a_val != 0: a_term_str = str(a_val) + "x"

        b_term_str = ""
        if b_val == 1: b_term_str = "y"
        elif b_val == -1: b_term_str = "-y"
        elif b_val != 0: b_term_str = str(b_val) + "y"
        
        if a_term_str and b_term_str:
            if b_val > 0:
                equation_str_for_question = a_term_str + " + " + b_term_str
            else: # b_val < 0
                equation_str_for_question = a_term_str + " " + b_term_str # '-' is already part of b_term_str
        elif a_term_str:
            equation_str_for_question = a_term_str
        elif b_term_str:
            equation_str_for_question = b_term_str
        else: # Should not happen if a_val or b_val is non-zero
            equation_str_for_question = "0"

        equation_str_for_question += " = " + str(c_val)

        question_text = r"在坐標平面上，畫出方程式 $" + equation_str_for_question.replace("{", r"\{").replace("}", r"\}") + r"$ 的圖形。"
        correct_answer_for_check = equation_str_for_question # Canonical form for checking
        full_correct_answer_display = equation_str_for_question # Full answer is just the equation here.

        # [B. 標點題防洩漏協定] For "draw the graph" questions, image_base64 only contains the grid.
        image_base64 = _draw_coordinate_plane(points_to_plot=[], lines_to_plot=[], x_range=x_range, y_range=y_range)

    elif problem_type == 2: # Type 2 (Maps to RAG Ex 3, 4): Find intercepts & quadrant for ax+by=c
        # [10. 數據禁絕常數] - Generate random coefficients.
        a_val, b_val, c_val = 0, 0, 0
        # Ensure a, b, c are non-zero for distinct intercepts and to avoid lines through the origin.
        # Ensure intercepts are within visible range for clarity.
        while a_val == 0 or b_val == 0 or c_val == 0 or \
              (abs(c_val / a_val) > 10 or abs(c_val / b_val) > 10):
            a_val = random.randint(-4, 4)
            b_val = random.randint(-4, 4)
            c_val = random.randint(-15, 15)
        
        # Calculate intercepts
        x_intercept_x = c_val / a_val
        y_intercept_y = c_val / b_val

        # Determine the quadrant the line does NOT pass through.
        quadrant_not_passed = 0
        if x_intercept_x > 0 and y_intercept_y > 0: # Example: (5,0), (0,2) -> Q1, Q2, Q4 -> Not Q3
            quadrant_not_passed = 3
        elif x_intercept_x < 0 and y_intercept_y > 0: # Example: (-4,0), (0,3) -> Q1, Q2, Q3 -> Not Q4
            quadrant_not_passed = 4
        elif x_intercept_x < 0 and y_intercept_y < 0: # Example: (-4,0), (0,-3) -> Q2, Q3, Q4 -> Not Q1
            quadrant_not_passed = 1
        elif x_intercept_x > 0 and y_intercept_y < 0: # Example: (4,0), (0,-3) -> Q1, Q3, Q4 -> Not Q2
            quadrant_not_passed = 2
        
        # Normalize coefficients for question text display.
        gcd_val = math.gcd(a_val, math.gcd(b_val, c_val))
        a_val_q = a_val // gcd_val
        b_val_q = b_val // gcd_val
        c_val_q = c_val // gcd_val

        equation_str_for_question = ""
        if random.random() < 0.5: # Form: ax + by = c (like RAG Ex 3)
            # Ensure leading coefficient (a) is positive or if a=0, b is positive.
            if a_val_q < 0:
                a_val_q, b_val_q, c_val_q = -a_val_q, -b_val_q, -c_val_q
            elif a_val_q == 0 and b_val_q < 0:
                a_val_q, b_val_q, c_val_q = -a_val_q, -b_val_q, -c_val_q
            
            a_term_str = ""
            if a_val_q == 1: a_term_str = "x"
            elif a_val_q != 0: a_term_str = str(a_val_q) + "x"

            b_term_str = ""
            if b_val_q == 1: b_term_str = "y"
            elif b_val_q > 0: b_term_str = " + " + str(b_val_q) + "y"
            elif b_val_q < 0: b_term_str = " " + str(b_val_q) + "y"
            
            equation_str_for_question = a_term_str + b_term_str + " = " + str(c_val_q)
            # Clean up potential leading ' + ' if a_term_str is empty.
            if equation_str_for_question.startswith(" + "):
                equation_str_for_question = equation_str_for_question[3:]

        else: # Form: ax + by + c = 0 (like RAG Ex 4)
            # Convert ax+by=c to ax+by-c=0
            c_val_q = -c_val_q # Move constant to left side
            # Ensure leading coefficient (a) is positive or if a=0, b is positive.
            if a_val_q < 0:
                a_val_q, b_val_q, c_val_q = -a_val_q, -b_val_q, -c_val_q
            elif a_val_q == 0 and b_val_q < 0:
                a_val_q, b_val_q, c_val_q = -a_val_q, -b_val_q, -c_val_q
            
            equation_terms = []
            if a_val_q != 0:
                if a_val_q == 1: equation_terms.append("x")
                elif a_val_q == -1: equation_terms.append("-x")
                else: equation_terms.append(str(a_val_q) + "x")
            
            if b_val_q != 0:
                if b_val_q > 0:
                    if b_val_q == 1: equation_terms.append(" + y")
                    else: equation_terms.append(f" + {b_val_q}y")
                else: # b_val_q < 0
                    if b_val_q == -1: equation_terms.append(" - y")
                    else: equation_terms.append(f" {b_val_q}y") # already negative

            if c_val_q != 0:
                if c_val_q > 0: equation_terms.append(f" + {c_val_q}")
                else: equation_terms.append(f" {c_val_q}")
            
            equation_str_for_question = "".join(equation_terms).strip()
            if not equation_str_for_question: equation_str_for_question = "0" # Should not happen
            equation_str_for_question += " = 0"

        question_text = r"⑴ 求方程式 $" + equation_str_for_question.replace("{", r"\{").replace("}", r"\}") + r"$ 的圖形與 x 軸、 y 軸的交點坐標。⑵ 承⑴，畫出方程式 $" + equation_str_for_question.replace("{", r"\{").replace("}", r"\}") + r"$ 的圖形，並判斷此圖形不通過第幾象限？"
        
        # Format intercepts for the full answer display.
        x_int_str = _format_coordinate_latex((x_intercept_x, _generate_coordinate_value(0,0, allow_fractions=True)[1]))
        y_int_str = _format_coordinate_latex((y_intercept_y, _generate_coordinate_value(0,0, allow_fractions=True)[1]))

        full_correct_answer_display = r"⑴ 與x軸交點$({x_int},0)$，與y軸交點$(0,{y_int})$。⑵ 不通過第{quadrant}象限。".replace("{x_int}", x_int_str).replace("{y_int}", y_int_str).replace("{quadrant}", str(quadrant_not_passed))
        
        correct_answer_for_check = equation_str_for_question # For `check` function, we compare the equation string.

        # [B. 標點題防洩漏協定] For "draw the graph" questions, image_base64 only contains the grid.
        image_base64 = _draw_coordinate_plane(points_to_plot=[], lines_to_plot=[], x_range=x_range, y_range=y_range)

    elif problem_type == 3: # Type 3 (Maps to RAG Ex 5a): Horizontal line y = k (DRAW)
        # [10. 數據禁絕常數]
        k_val_y_float, _ = _generate_coordinate_value(-8, 8, allow_fractions=False)
        k_val_y = int(k_val_y_float) # Ensure integer for simple vertical/horizontal lines
        
        # [5. LaTeX 安全]
        equation_str_for_question = r"y = {k}".replace("{k}", str(k_val_y))

        question_text = r"在坐標平面上，畫出方程式 $" + equation_str_for_question.replace("{", r"\{").replace("}", r"\}") + r"$ 的圖形。"
        correct_answer_for_check = equation_str_for_question
        full_correct_answer_display = equation_str_for_question

        # [B. 標點題防洩漏協定] Only grid.
        image_base64 = _draw_coordinate_plane(points_to_plot=[], lines_to_plot=[], x_range=x_range, y_range=y_range)

    elif problem_type == 4: # Type 4 (Maps to RAG Ex 5b): Vertical line x = k (DRAW)
        # [10. 數據禁絕常數]
        k_val_x_float, _ = _generate_coordinate_value(-8, 8, allow_fractions=False)
        k_val_x = int(k_val_x_float) # Ensure integer for simple vertical/horizontal lines
        
        # [5. LaTeX 安全]
        equation_str_for_question = r"x = {k}".replace("{k}", str(k_val_x))

        question_text = r"在坐標平面上，畫出方程式 $" + equation_str_for_question.replace("{", r"\{").replace("}", r"\}") + r"$ 的圖形。"
        correct_answer_for_check = equation_str_for_question
        full_correct_answer_display = equation_str_for_question

        # [B. 標點題防洩漏協定] Only grid.
        image_base64 = _draw_coordinate_plane(points_to_plot=[], lines_to_plot=[], x_range=x_range, y_range=y_range)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_for_check, # This is the canonical equation string for `check`.
        "answer": full_correct_answer_display, # This is the full detailed answer for display to the user.
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.1" # Version updated due to re-alignment of problem types.
    }


    """
    [3. 頂層函式], [Infrastructure Rule 6]
    Checks if the user's answer (equation string) matches the correct answer.
    This function normalizes both equations to a canonical form for comparison.
    Returns a dictionary with is_correct, result, and feedback.
    """
    # The `correct_answer` parameter here corresponds to the `correct_answer` field
    # returned by `generate`, which is the canonical equation string.

    # Sanitize correct_answer for feedback [Infrastructure Rule 6]
    sanitized_correct_answer = re.sub(r"[\$\\]", "", str(correct_answer))

    normalized_user = _normalize_equation_coeffs(user_answer)
    normalized_correct = _normalize_equation_coeffs(correct_answer)
    
    is_correct = (normalized_user == normalized_correct)
    
    feedback = ""
    if is_correct:
        feedback = "答案正確！"
    else:
        # Infrastructure Rule 6: Error feedback format
        feedback = r"答案錯誤。正確答案為：{ans}".replace("{ans}", sanitized_correct_answer)
    
    return {
        "is_correct": is_correct,
        "result": "Correct" if is_correct else "Incorrect",
        "feedback": feedback
    }

# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', ',', '|', '(', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
