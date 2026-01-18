# ==============================================================================
# ID: jh_數學1下_GeometricMeaningOfSystemOfTwoVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 82.72s | RAG: 4 examples
# Created At: 2026-01-15 15:05:24
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
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
from io import BytesIO
import matplotlib.pyplot as plt # Temporarily keep for rcParams, will ensure Figure is used for plotting
from matplotlib.figure import Figure # V1. Infrastructure Rule 1: Use Figure for thread-safety
import numpy as np
from datetime import datetime

import re # V6. Result Feedback: For sanitizing LaTeX

# V5. Visual Style (Coordinate Scale Protocol): Set font for Traditional Chinese
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False # To correctly display minus sign with JhengHei font

# --- V10.2 Coordinate Hardening Spec A: Data Structure Lock-down ---
# 必須指示 Coder 定義 _generate_coordinate_value() 並統一回傳固定格式：(float_val, (int_part, num, den, is_neg))。
# 格式化函式必須嚴格執行 int_part, num, den, is_neg = data[1] 的解包方式。
# 若為整數，num 與 den 設為 0；若為分數，則 int_part 為帶分數整數部。
def _generate_coordinate_value(min_val=-5, max_val=5, allow_fractions=False):
    """
    Generates a coordinate value (float) and its fractional/integer representation.
    Returns: (float_val, (int_part, numerator, denominator, is_negative))
    """
    # For K12, especially lower levels, prefer integers.
    # Set allow_fractions to True for higher levels or specific problem types if needed.
    if random.random() < 0.8 or not allow_fractions: # 80% chance of integer
        val = random.randint(min_val, max_val)
        return float(val), (val, 0, 0, val < 0)
    else:
        # Generate a simple fraction (e.g., 1/2, 3/4)
        int_part_range_limit = max(1, min(abs(min_val), abs(max_val)) // 2)
        int_part = random.randint(-int_part_range_limit, int_part_range_limit) # Keep magnitude smaller for fractions
        numerator = random.randint(1, 4) # Small numerator
        denominator = random.choice([2, 3, 4, 5]) # Small denominator
        
        # Ensure proper fraction for the fractional part
        if numerator >= denominator: # e.g., if num=3, den=2, regenerate or adjust
            numerator = random.randint(1, denominator - 1)
            if numerator == 0: numerator = 1 # Avoid 0/den

        sign = random.choice([-1, 1])
        
        float_val_abs_frac_part = numerator / denominator
        
        if int_part == 0:
            float_val = sign * float_val_abs_frac_part
            is_neg = (sign == -1)
            return float_val, (0, numerator, denominator, is_neg)
        else:
            # For mixed fractions, the sign applies to the whole number.
            # Example: -2.5 is -(2 + 1/2). So int_part is -2, num is 1, den is 2.
            # Our _format_coordinate_latex handles the display as -2\frac{1}{2}.
            # The int_part in the tuple should be the integer part of the mixed number.
            
            # Create a temporary float value for calculation
            temp_float_val = abs(int_part) + float_val_abs_frac_part
            if int_part < 0:
                temp_float_val = -temp_float_val
            
            is_neg = (temp_float_val < 0)

            # Adjust int_part for mixed fraction representation
            if is_neg:
                abs_float_val = abs(temp_float_val)
                abs_int_part_for_display = math.floor(abs_float_val)
                frac_part_val = abs_float_val - abs_int_part_for_display
                
                # Convert frac_part_val back to num/den for the current denominator
                # Find the closest integer numerator for the given denominator
                num_approx = round(frac_part_val * denominator)
                if num_approx == 0 and frac_part_val > 0: num_approx = 1 # ensure non-zero numerator if frac_part exists
                if num_approx == denominator: # if it rounded up to 1, make it 0 and increment int_part
                    abs_int_part_for_display += 1
                    num_approx = 0

                return temp_float_val, (-abs_int_part_for_display if abs_int_part_for_display > 0 else 0, num_approx, denominator if num_approx > 0 else 0, True)
            else:
                return temp_float_val, (int_part, numerator, denominator, False)


# V10.2 C: LaTeX 模板規範 (No Double Braces)
# 嚴禁指示 Coder 使用 f"{{...}}" 這種寫法。
# 必須規範 LaTeX 模板使用單層大括號（如 {n}, {d}），並搭配 .replace("{n}", str(num)) 進行代換。
def _format_coordinate_latex(coord_data):
    """
    Formats a coordinate value (from _generate_coordinate_value) into a LaTeX string.
    """
    float_val, (int_part, num, den, is_neg) = coord_data

    if num == 0:  # It's an integer
        return str(int_part)
    else:  # It's a fraction or mixed number
        sign_str = r"-" if is_neg else ""
        if int_part == 0:
            # Proper fraction
            expr = r"\frac{n}{d}".replace("{n}", str(num)).replace("{d}", str(den))
            return sign_str + expr
        else:
            # Mixed number
            # For negative mixed numbers, LaTeX typically shows -(A \frac{B}{C})
            # So, we take the absolute value of int_part for display.
            expr = r"{i}\frac{n}{d}".replace("{i}", str(abs(int_part))).replace("{n}", str(num)).replace("{d}", str(den))
            return sign_str + expr


# Helper function to convert matplotlib plot to base64 image
# 必須回傳 'return' 語句回傳結果。回傳值必須強制轉為字串 (str)。
def _plot_to_base64(fig):
    """Converts a matplotlib figure to a base64 encoded PNG image."""
    buf = BytesIO()
    # V11.6: Resolution: dpi=300
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close(fig) # Use plt.close for the figure object
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# --- V10.2 D: Visual Consistency ---
# 必須鎖定 ax.set_aspect('equal') 確保網格為正方形。
# 坐標軸標註：僅顯示原點 0 (18號加粗)，點標籤須加白色光暈 (bbox)。
# 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
def _draw_coordinate_plane(lines_data=None, points_data=None, x_range=(-10, 10), y_range=(-10, 10)):
    """
    Draws a coordinate plane with optional lines and points.
    lines_data: List of dictionaries { 'equation': (a, b, c), 'label': 'L1', 'color': 'blue' }
                where ax + by = c
    points_data: List of dictionaries { 'coord': (x, y), 'label': 'P', 'color': 'red' }
    """
    if lines_data is None:
        lines_data = []
    if points_data is None:
        points_data = []

    # V1. Infrastructure Rule 1: Use Figure for thread-safety
    fig = Figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    
    ax.set_aspect('equal') # V10.2 D: Ensure square grid

    # Set grid and axes
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)

    # Set x, y limits
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # Tick labels for major intervals (e.g., every 1 unit)
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))

    # V5. Visual Style (Coordinate Scale Protocol): Hide all tick labels except origin '0'
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # V10.2 D: Origin label
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    # Draw lines
    for line in lines_data:
        a, b, c = line['equation']
        color = line.get('color', 'blue')
        label = line.get('label', '')
        linestyle = line.get('linestyle', '-')

        if b != 0: # Not a vertical line
            # Determine x values to plot to ensure the line crosses the entire graph
            # Find points at the boundary of the plot
            y_at_xmin = (-a * x_range[0] + c) / b
            y_at_xmax = (-a * x_range[1] + c) / b
            
            # Find x values where y crosses y_range boundaries
            x_at_ymin = (c - b * y_range[0]) / a if a != 0 else float('inf')
            x_at_ymax = (c - b * y_range[1]) / a if a != 0 else float('inf')
            
            plot_x = []
            plot_y = []

            # Consider points at x_range boundaries
            if y_range[0] <= y_at_xmin <= y_range[1]:
                plot_x.append(x_range[0])
                plot_y.append(y_at_xmin)
            if y_range[0] <= y_at_xmax <= y_range[1]:
                plot_x.append(x_range[1])
                plot_y.append(y_at_xmax)

            # Consider points at y_range boundaries
            if x_range[0] <= x_at_ymin <= x_range[1]:
                plot_x.append(x_at_ymin)
                plot_y.append(y_range[0])
            if x_range[0] <= x_at_ymax <= x_range[1]:
                plot_x.append(x_at_ymax)
                plot_y.append(y_range[1])
            
            # Remove duplicates and sort by x-coordinate
            unique_points = sorted(list(set(zip(plot_x, plot_y))))
            if len(unique_points) >= 2:
                final_plot_x = [p[0] for p in unique_points]
                final_plot_y = [p[1] for p in unique_points]
                ax.plot(final_plot_x, final_plot_y, color=color, label=label, linewidth=2, linestyle=linestyle)
            elif len(unique_points) == 1: # Line is just a point or very short segment
                ax.plot(unique_points[0][0], unique_points[0][1], 'o', color=color) # Plot as a point
            else: # Fallback for very steep lines or lines outside view
                # Choose two arbitrary points on the line that are far apart
                x_vals = np.array([x_range[0] - 50, x_range[1] + 50])
                y_vals = (-a * x_vals + c) / b
                ax.plot(x_vals, y_vals, color=color, label=label, linewidth=2, linestyle=linestyle)
        else: # Vertical line: x = c/a (b is 0)
            if a != 0:
                x_val = c / a
                if x_range[0] <= x_val <= x_range[1]:
                    ax.plot([x_val, x_val], [y_range[0], y_range[1]], color=color, label=label, linewidth=2, linestyle=linestyle)
            elif c == 0: # a=0, b=0, c=0 => 0=0, an infinite line (whole plane). Not representable.
                pass # Should not happen for valid line generation
            else: # a=0, b=0, c!=0 => 0=c, no solution. Not representable as a line.
                pass # Should not happen for valid line generation


    # Draw points
    for point in points_data:
        x, y = point['coord']
        label = point.get('label', '')
        color = point.get('color', 'red')
        ax.plot(x, y, 'o', color=color, markersize=8, zorder=5)
        # V10.2 D: Point labels with white bbox (V11.6 Ultra Visual Standards: Label Halo)
        ax.text(x, y + 0.5, label, color='black', ha='center', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    if lines_data: # Only show legend if there are lines
        ax.legend()
    return _plot_to_base64(fig)


# Helper to calculate the intersection of two lines (ax + by = c)
# 數據禁絕常數: 嚴禁硬編碼答案或座標。所有目標答案與圖形座標必須根據隨機生成的數據，透過幾何公式反向計算得出。
def _calculate_intersection(eq1, eq2):
    """
    Calculates the intersection point of two linear equations.
    eq: (a, b, c) representing ax + by = c
    Returns: (x, y) if unique solution, "infinite_solutions" for coincident, "no_solution" for parallel.
    """
    a1, b1, c1 = eq1
    a2, b2, c2 = eq2

    det = a1 * b2 - a2 * b1

    if det == 0:
        # Lines are parallel or coincident
        # Check if coincident: if all determinants are zero, or one equation is a multiple of the other
        det_x = c1 * b2 - c2 * b1
        det_y = a1 * c2 - a2 * c1
        
        # Using a small tolerance for float comparison
        tolerance = 1e-9 
        if abs(det_x) < tolerance and abs(det_y) < tolerance:
            # If all three determinants (main, x, y) are zero, lines are coincident
            return "infinite_solutions"
        else:
            # If main determinant is zero, but x or y determinant is not, lines are parallel
            return "no_solution"
    else:
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        return x, y

# Helper to generate random linear equation coefficients (ax + by = c)
def _generate_equation_coeffs(x_intersect, y_intersect, min_coeff=-4, max_coeff=4, non_zero_b=False):
    """
    Generates coefficients (a, b, c) for a linear equation ax + by = c
    that passes through (x_intersect, y_intersect).
    Ensures a and b are not both zero.
    If non_zero_b is True, ensures b is not zero (for non-vertical lines).
    """
    while True:
        a = random.randint(min_coeff, max_coeff)
        b = random.randint(min_coeff, max_coeff)
        
        if a == 0 and b == 0:
            continue # Not a valid line
        if non_zero_b and b == 0:
            continue # For non-vertical lines, b cannot be zero
            
        c = a * x_intersect + b * y_intersect
        
        return a, b, c


# Helper to simplify equation coefficients by dividing by GCD
def _simplify_equation(a, b, c):
    """Simplifies coefficients (a, b, c) by dividing by their GCD."""
    coeffs = [a, b, c]
    
    # Find a common multiplier to convert all coefficients to integers if they are fractions
    common_multiplier = 1
    for val in coeffs:
        if isinstance(val, float) and not val.is_integer():
            temp_str = str(val)
            if '.' in temp_str:
                decimal_places = len(temp_str) - temp_str.index('.') - 1
                common_multiplier = max(common_multiplier, 10**decimal_places)
    
    if common_multiplier > 1:
        # Apply multiplier and round to nearest integer to handle float inaccuracies
        a, b, c = round(a * common_multiplier), round(b * common_multiplier), round(c * common_multiplier)
    else:
        # If no fractional floats, ensure they are integers for GCD
        a, b, c = int(a), int(b), int(c)
    
    # Filter out zeros for GCD calculation
    non_zero_coeffs = [val for val in [a, b, c] if val != 0]

    if not non_zero_coeffs: # All zero, not a valid equation (0=0)
        return 0, 0, 0
    
    current_gcd = abs(non_zero_coeffs[0])
    for i in range(1, len(non_zero_coeffs)):
        current_gcd = math.gcd(current_gcd, abs(non_zero_coeffs[i]))

    if current_gcd > 0:
        a = a // current_gcd
        b = b // current_gcd
        c = c // current_gcd
    
    # Ensure leading coefficient (a) is positive if possible
    # (or b if a is zero, to normalize the equation form)
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
        
    return a, b, c

# Helper to convert equation (a, b, c) to LaTeX string
# 排版與 LaTeX 安全: 凡字串包含 LaTeX 指令 (如 \frac, \sqrt, \pm)，嚴禁使用 f-string 或 % 格式化。
# 必須嚴格執行以下模板：expr = r"x = {a}".replace("{a}", str(ans_val))
def _format_equation_latex(a, b, c):
    """Formats ax + by = c into a LaTeX string."""
    parts = []
    
    # Handle 'a' term
    if a != 0:
        if a == 1:
            parts.append("x")
        elif a == -1:
            parts.append(r"-x")
        else:
            parts.append(str(a) + "x")
            
    # Handle 'b' term
    if b != 0:
        if b > 0:
            if parts: # If 'a' term already added, add '+'
                parts.append(r"+")
            if b == 1:
                parts.append("y")
            else:
                parts.append(str(b) + "y")
        else: # b < 0
            if b == -1:
                parts.append(r"-y")
            else:
                parts.append(str(b) + "y")
                
    # If both a and b are 0, this is an invalid equation (e.g., 0 = c)
    if not parts:
        # This case should ideally not happen for valid lines
        # But if it does, represent as '0 = c'
        expr = r"0 = {c}".replace("{c}", str(c))
        return expr
        
    equation_str = " ".join(parts)
    expr = equation_str + r" = {c}".replace("{c}", str(c))
    return expr

# --- Main functions ---

# 頂層函式: 嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# 自動重載: 確保代碼不依賴全域狀態。
def generate(level=1):
    # 隨機分流: generate() 內部必須使用 random.choice 或 if/elif 邏輯，明確對應到 RAG 中的例題。
    # 範例: Spec 必須描述如何將 RAG 例題中的數據「動態化」(Dynamize)，而不是創造新題型。
    problem_type = random.choice([1, 2, 3, 4, 5, 6]) # Randomly select problem type

    # Common parameters for coordinate generation
    x_range = (-8, 8)
    y_range = (-8, 8)
    coord_min_val = -5
    coord_max_val = 5

    # Use _generate_coordinate_value for all coordinate generation
    # For K12, we prioritize integer intersection points for simplicity, especially at lower levels.
    # [數據禁絕常數]: 隨機生成所有幾何長度、角度與面積。
    # V7. Coordinate Logic Hardening: Generate values first, then check.
    x_intersect_float, x_intersect_data = _generate_coordinate_value(coord_min_val, coord_max_val, allow_fractions=(level>=2))
    y_intersect_float, y_intersect_data = _generate_coordinate_value(coord_min_val, coord_max_val, allow_fractions=(level>=2))

    intersection_point = (x_intersect_float, y_intersect_float)
    intersection_point_latex = r"({x}, {y})".replace("{x}", _format_coordinate_latex(x_intersect_data)).replace("{y}", _format_coordinate_latex(y_intersect_data))

    # To ensure a unique solution for most types, generate equations that definitely intersect.
    # We must ensure they are not parallel or coincident for unique solution types.
    
    a1, b1, c1, a2, b2, c2 = 0, 0, 0, 0, 0, 0 # Initialize to avoid UnboundLocalError
    
    # Generate equations for unique solutions (default)
    while True:
        # Generate equation 1 (a1x + b1y = c1)
        a1, b1, c1 = _generate_equation_coeffs(x_intersect_float, y_intersect_float, min_coeff=-4, max_coeff=4)
        a1, b1, c1 = _simplify_equation(a1, b1, c1)

        # Generate equation 2 (a2x + b2y = c2)
        a2, b2, c2 = _generate_equation_coeffs(x_intersect_float, y_intersect_float, min_coeff=-4, max_coeff=4)
        a2, b2, c2 = _simplify_equation(a2, b2, c2)
        
        # Check if lines are parallel or coincident
        det_coeffs = a1 * b2 - a2 * b1
        if det_coeffs != 0: # Unique solution
            break
        # If det_coeffs == 0, they are parallel or coincident. Regenerate.

    eq1_latex = _format_equation_latex(a1, b1, c1)
    eq2_latex = _format_equation_latex(a2, b2, c2)

    question_text = ""
    image_base64 = None
    correct_answer = ""
    answer = {} # 欄位鎖死: 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。

    if problem_type == 1:
        # Type 1 (Maps to Example 1): Solve System Algebraically.
        # Goal: Find the intersection point (x, y) of two lines given their equations.
        question_text = r"請找出下列二元一次聯立方程式的解，並說明其在坐標平面上的幾何意義："
        question_text += r"$" + eq1_latex + r"$"
        question_text += r"$" + eq2_latex + r"$"
        
        # correct_answer will be formatted at the end for consistency
        
        # No image needed for algebraic solution.
        image_base64 = None

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): Verify Point as Solution.
        # Goal: Given two equations and a point, determine if the point is the solution.
        test_point_is_solution = random.choice([True, False])
        
        if test_point_is_solution:
            test_x_float, test_x_data = x_intersect_float, x_intersect_data
            test_y_float, test_y_data = y_intersect_float, y_intersect_data
            correct_answer_text = "是"
        else:
            # Generate a point that is NOT the intersection
            while True:
                test_x_float, test_x_data = _generate_coordinate_value(coord_min_val, coord_max_val, allow_fractions=(level>=2))
                test_y_float, test_y_data = _generate_coordinate_value(coord_min_val, coord_max_val, allow_fractions=(level>=2))
                # Ensure it's not the actual solution AND not on both lines
                is_on_L1 = abs(a1 * test_x_float + b1 * test_y_float - c1) < 1e-6
                is_on_L2 = abs(a2 * test_x_float + b2 * test_y_float - c2) < 1e-6
                
                if not (is_on_L1 and is_on_L2): # If it's not the actual solution
                    # Also ensure it's not the exact intersection point (redundant with above, but good for robustness)
                    if abs(test_x_float - x_intersect_float) > 1e-6 or abs(test_y_float - y_intersect_float) > 1e-6:
                        break
            correct_answer_text = "否"

        test_point_latex = r"({x}, {y})".replace("{x}", _format_coordinate_latex(test_x_data)).replace("{y}", _format_coordinate_latex(test_y_data))
        
        question_text = r"點 $" + test_point_latex + r"$ 是否為下列聯立方程式的解？"
        question_text += r"$" + eq1_latex + r"$"
        question_text += r"$" + eq2_latex + r"$"
        
        correct_answer = correct_answer_text
        image_base64 = None

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): Find Unknown Coefficient.
        # Goal: Given an intersection point and two equations (one with an unknown), find the unknown.
        
        # Randomly choose which equation has the unknown and which coefficient is unknown
        coeff_to_hide = random.choice(['a', 'b', 'c'])
        which_equation = random.choice([1, 2])

        k_val = 0 # Initialize k_val
        
        if which_equation == 1:
            # Hide a coefficient in eq1
            if coeff_to_hide == 'a':
                k_val = a1
                # Temporarily use 'K_placeholder' as a placeholder to generate LaTeX, then replace 'K_placeholder' with 'k'
                question_eq1_latex = _format_equation_latex("K_placeholder", b1, c1).replace("K_placeholder", r"k") 
            elif coeff_to_hide == 'b':
                k_val = b1
                question_eq1_latex = _format_equation_latex(a1, "K_placeholder", c1).replace("K_placeholder", r"k")
            else: # coeff_to_hide == 'c'
                k_val = c1
                question_eq1_latex = _format_equation_latex(a1, b1, "K_placeholder").replace("K_placeholder", r"k")
            
            question_text = r"已知點 $" + intersection_point_latex + r"$ 是下列聯立方程式的解，求 $k$ 的值："
            question_text += r"$" + question_eq1_latex + r"$"
            question_text += r"$" + eq2_latex + r"$"

        else: # which_equation == 2
            # Hide a coefficient in eq2
            if coeff_to_hide == 'a':
                k_val = a2
                question_eq2_latex = _format_equation_latex("K_placeholder", b2, c2).replace("K_placeholder", r"k")
            elif coeff_to_hide == 'b':
                k_val = b2
                question_eq2_latex = _format_equation_latex(a2, "K_placeholder", c2).replace("K_placeholder", r"k")
            else: # coeff_to_hide == 'c'
                k_val = c2
                question_eq2_latex = _format_equation_latex(a2, b2, "K_placeholder").replace("K_placeholder", r"k")
            
            question_text = r"已知點 $" + intersection_point_latex + r"$ 是下列聯立方程式的解，求 $k$ 的值："
            question_text += r"$" + eq1_latex + r"$"
            question_text += r"$" + question_eq2_latex + r"$"
        
        correct_answer = str(k_val) # K value can be float if intersection point was fractional
        image_base64 = None

    elif problem_type == 4:
        # Type 4 (Maps to Example 4): Read Intersection from Graph.
        # Goal: Interpret a given graph to find the intersection point.
        question_text = r"下圖顯示了兩個二元一次方程式的圖形。請從圖中找出它們的交點坐標。"
        
        lines_to_draw = [
            {'equation': (a1, b1, c1), 'label': r'$L_1$', 'color': 'blue'}, # Don't put full equation in label for image clarity
            {'equation': (a2, b2, c2), 'label': r'$L_2$', 'color': 'red'}
        ]
        
        # V10.2 B: Reading Type - show points and labels
        # 防洩漏原則: 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式，確保學生無法從圖形中直接看到答案。
        # For "reading type", the point IS part of the known data presented to the student to read.
        points_to_draw = [
            {'coord': intersection_point, 'label': intersection_point_latex, 'color': 'green'}
        ]
        
        image_base64 = _draw_coordinate_plane(lines_data=lines_to_draw, points_data=points_to_draw, x_range=x_range, y_range=y_range)
        # correct_answer will be formatted at the end for consistency

    elif problem_type == 5:
        # Type 5 (Maps to Example 5): Graph and Find Intersection.
        # Goal: Given two equations, students need to graph them and find the intersection.
        question_text = r"請在坐標平面上繪製下列兩個二元一次方程式的圖形，並找出它們的交點坐標。"
        question_text += r"$" + eq1_latex + r"$"
        question_text += r"$" + eq2_latex + r"$"
        
        lines_to_draw = [
            {'equation': (a1, b1, c1), 'label': r'$L_1$', 'color': 'blue'},
            {'equation': (a2, b2, c2), 'label': r'$L_2$', 'color': 'red'}
        ]
        
        # V10.2 B: 標點題防洩漏協定 (Anti-Leak Protocol):
        # 針對「在平面上標出點」的題型 (Plotting Type)，Spec 必須明確指示 Coder：
        # 在呼叫繪圖函式時，`points` 參數必須傳入 空列表 `[]`。
        # 圖形僅能顯示網格與坐標軸，學生需根據題目文字自行判斷位置。
        image_base64 = _draw_coordinate_plane(lines_data=lines_to_draw, points_data=[], x_range=x_range, y_range=y_range)
        # correct_answer will be formatted at the end for consistency
        
    elif problem_type == 6:
        # Type 6 (Maps to Example 6): Special Cases (Parallel/Coincident).
        # Goal: Identify if lines are parallel, coincident, or intersecting, and state the number of solutions.
        
        # Randomly choose between parallel, coincident, or intersecting (unique)
        # Adjust probability based on level. Higher level => more special cases.
        if level >= 2:
            case_type = random.choice(['unique', 'unique', 'parallel', 'coincident']) # More special cases
        else: # level 1, mostly unique
            case_type = random.choice(['unique', 'unique', 'unique', 'parallel']) # Higher chance of unique
        
        if case_type == 'unique':
            # Already generated unique solutions (a1,b1,c1) and (a2,b2,c2)
            correct_answer = "唯一解"
            question_text = r"下列聯立方程式在坐標平面上的圖形關係為何？有幾個解？"
            question_text += r"$" + eq1_latex + r"$"
            question_text += r"$" + eq2_latex + r"$"
            
            lines_to_draw = [
                {'equation': (a1, b1, c1), 'label': r'$L_1$', 'color': 'blue'},
                {'equation': (a2, b2, c2), 'label': r'$L_2$', 'color': 'red'}
            ]
            # For unique case, we can show the intersection point as part of the "known" visual
            points_to_draw = [{'coord': intersection_point, 'label': intersection_point_latex, 'color': 'green'}]
            image_base64 = _draw_coordinate_plane(lines_data=lines_to_draw, points_data=points_to_draw, x_range=x_range, y_range=y_range)

        elif case_type == 'parallel':
            # Generate parallel lines (same slope, different y-intercept)
            # Use existing a1, b1. Generate a new c2 such that it's parallel but not coincident.
            while True:
                k = random.choice([-2, -1, 1, 2, 3]) # Multiplier for a1, b1
                if k == 0: continue # Multiplier cannot be zero
                
                a2_parallel = a1 * k
                b2_parallel = b1 * k
                
                # Ensure c2_parallel is different from c1*k
                # Add a non-zero, small integer offset to make it parallel but not coincident
                offset = random.choice([-2, -1, 1, 2])
                c2_parallel = c1 * k + offset
                
                if c2_parallel != c1 * k: # Ensure they are not coincident
                    # Also ensure a2_parallel and b2_parallel are not both zero
                    if a2_parallel != 0 or b2_parallel != 0:
                        break

            a2_parallel, b2_parallel, c2_parallel = _simplify_equation(a2_parallel, b2_parallel, c2_parallel)
            
            eq2_parallel_latex = _format_equation_latex(a2_parallel, b2_parallel, c2_parallel)
            
            correct_answer = "無解"
            question_text = r"下列聯立方程式在坐標平面上的圖形關係為何？有幾個解？"
            question_text += r"$" + eq1_latex + r"$"
            question_text += r"$" + eq2_parallel_latex + r"$"
            
            lines_to_draw = [
                {'equation': (a1, b1, c1), 'label': r'$L_1$', 'color': 'blue'},
                {'equation': (a2_parallel, b2_parallel, c2_parallel), 'label': r'$L_2$', 'color': 'red'}
            ]
            # For parallel lines, no intersection point to show
            image_base64 = _draw_coordinate_plane(lines_data=lines_to_draw, points_data=[], x_range=x_range, y_range=y_range)

        elif case_type == 'coincident':
            # Generate coincident lines (one is a multiple of the other)
            k = random.choice([-2, -1, 2, 3]) # Multiplier for eq1
            if k == 0: k = 1 # Multiplier cannot be zero for generating a multiple
            
            a2_coincident = a1 * k
            b2_coincident = b1 * k
            c2_coincident = c1 * k
            
            a2_coincident, b2_coincident, c2_coincident = _simplify_equation(a2_coincident, b2_coincident, c2_coincident)

            eq2_coincident_latex = _format_equation_latex(a2_coincident, b2_coincident, c2_coincident)
            
            correct_answer = "無限多組解"
            question_text = r"下列聯立方程式在坐標平面上的圖形關係為何？有幾個解？"
            question_text += r"$" + eq1_latex + r"$"
            question_text += r"$" + eq2_coincident_latex + r"$"
            
            lines_to_draw = [
                {'equation': (a1, b1, c1), 'label': r'$L_1$', 'color': 'blue'},
                {'equation': (a2_coincident, b2_coincident, c2_coincident), 'label': r'$L_2$', 'color': 'red', 'linestyle': '--'} # Use different style to show two distinct lines that are coincident
            ]
            # For coincident lines, no single intersection point to show
            image_base64 = _draw_coordinate_plane(lines_data=lines_to_draw, points_data=[], x_range=x_range, y_range=y_range)
    
    # Final check for correct_answer type for specific problem types (coordinates should be formatted)
    if problem_type in [1, 4, 5]: # Intersection point
        ans_x_formatted = _format_coordinate_latex(x_intersect_data)
        ans_y_formatted = _format_coordinate_latex(y_intersect_data)
        correct_answer = r"({x}, {y})".replace("{x}", ans_x_formatted).replace("{y}", ans_y_formatted)
        
    # Other problem types (2, 3, 6) already have their correct_answer as strings ("是", "否", k_val, "唯一解" etc.)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": {}, # Placeholder for structured answer if needed, currently empty as per spec
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # 時間戳記: 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
        "version": "1.0"
    }

# 頂層函式: 嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# 自動重載: 確保代碼不依賴全域狀態。

    """
    Checks the user's answer against the correct answer.
    Handles different answer formats (e.g., (x,y) tuples, strings).
    """
    # V6. Result Feedback (Pure Feedback Protocol): Sanitized answer for feedback
    sanitized_ans = re.sub(r"[\$\\]", "", str(correct_answer))

    # Normalize string answers for comparison
    user_answer_norm = str(user_answer).strip().lower().replace(" ", "")
    correct_answer_norm = str(correct_answer).strip().lower().replace(" ", "")

    # For simple string comparisons (Yes/No, solution types)
    if user_answer_norm == correct_answer_norm:
        return True
    
    # Special handling for coordinate tuples: (x,y)
    # Try to parse as (float, float) for comparison
    try:
        # Remove LaTeX formatting if present in correct_answer (e.g., \frac{1}{2})
        # Use regex to replace \frac{num}{den} with (num/den) for eval
        correct_answer_for_eval = re.sub(r"\\frac\{(\-?\d+)\}\{(\d+)\}", r"(\1/\2)", correct_answer_norm)
        correct_answer_for_eval = correct_answer_for_eval.replace("{", "").replace("}", "") # Remove remaining braces from mixed fractions

        if user_answer_norm.startswith('(') and user_answer_norm.endswith(')'):
            user_coords_str = user_answer_norm[1:-1].split(',')
            user_x = float(eval(user_coords_str[0])) # Using eval to handle fractions like 1/2
            user_y = float(eval(user_coords_str[1]))
            
            # For correct_answer, handle potential mixed numbers like -2(1/2) -> -2-1/2 for eval
            # First, check for negative sign outside a mixed number
            correct_coords_str = correct_answer_for_eval[1:-1].split(',')
            
            # Eval can handle simple numbers, fractions, and negative numbers.
            # Mixed numbers like "2 1/2" are not directly handled by eval, but "2+1/2" is.
            # Our _format_coordinate_latex produces "2\frac{1}{2}" or "-2\frac{1}{2}".
            # After regex conversion, it would be "2(1/2)" or "-2(1/2)".
            # Eval treats "2(1/2)" as 2 * (1/2) = 1.0, which is incorrect for 2 and 1/2.
            # We need to explicitly convert "A(B/C)" to "A+B/C" or "A-B/C".
            
            # Re-process correct_x/y for mixed numbers or negative fractions
            def parse_coord_for_eval(coord_str):
                coord_str = coord_str.strip()
                match_mixed = re.match(r"^(-?)(\d+)\((\d+)/(\d+)\)$", coord_str) # e.g., -2(1/2)
                match_fraction = re.match(r"^(-?)\((\d+)/(\d+)\)$", coord_str) # e.g., -(1/2)
                
                if match_mixed:
                    sign = -1 if match_mixed.group(1) == "-" else 1
                    integer_part = int(match_mixed.group(2))
                    numerator = int(match_mixed.group(3))
                    denominator = int(match_mixed.group(4))
                    return sign * (integer_part + numerator / denominator)
                elif match_fraction:
                    sign = -1 if match_fraction.group(1) == "-" else 1
                    numerator = int(match_fraction.group(2))
                    denominator = int(match_fraction.group(3))
                    return sign * (numerator / denominator)
                else: # Assume it's a simple integer or fraction eval can handle directly
                    return float(eval(coord_str))

            correct_x = parse_coord_for_eval(correct_coords_str[0])
            correct_y = parse_coord_for_eval(correct_coords_str[1])

            # Compare floats with a tolerance
            tolerance = 1e-6
            if abs(user_x - correct_x) < tolerance and abs(user_y - correct_y) < tolerance:
                return True
    except (ValueError, IndexError, SyntaxError, NameError):
        pass # Not a valid coordinate pair, or eval failed

    # For '是'/'否'
    if user_answer_norm in ["是", "否"] and correct_answer_norm in ["是", "否"]:
        return user_answer_norm == correct_answer_norm
        
    # For number of solutions
    solution_mapping = {
        "唯一解": ["唯一解", "1", "一個解", "一組解", "one solution", "unique solution"],
        "無解": ["無解", "0", "零解", "沒有解", "no solution"],
        "無限多組解": ["無限多組解", "無限解", "many solutions", "infinite solutions"]
    }
    
    for key, values in solution_mapping.items():
        if correct_answer_norm == key.lower() and user_answer_norm in values:
            return True

    # For numerical answers (e.g., finding k)
    try:
        user_num = float(eval(user_answer_norm)) # eval to handle "1/2"
        correct_num = float(eval(correct_answer_norm))
        tolerance = 1e-6
        if abs(user_num - correct_num) < tolerance:
            return True
    except (ValueError, SyntaxError, NameError):
        pass # Not a valid number

    return False

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
