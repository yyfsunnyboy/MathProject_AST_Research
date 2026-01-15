# ==============================================================================
# ID: jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 48.56s | RAG: 5 examples
# Created At: 2026-01-15 16:51:32
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
import io
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import re

# 點標籤白名單 (V13.6 Strict Labeling, 優先遵循系統底層鐵律)
POINT_LABELS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', '小明', '小美', '小翊']

# 確保版本號遞增
__version__ = "1.0.0"

def _generate_coordinate_value():
    """
    功能: 生成一個隨機的座標值，可以是整數或分數。
    回傳格式: (float_val, (int_part, num, den, is_neg))
        float_val: 實際的浮點數值。
        int_part: 帶分數的整數部分 (若為整數則為其本身)。
        num: 分數的分子 (若為整數則為 0)。
        den: 分數的分母 (若為整數則為 0)。
        is_neg: 布林值，表示是否為負數。
    """
    is_neg = random.choice([True, False])
    float_val = 0.0

    if random.random() < 0.3:  # 約 30% 機率生成分數
        int_part = random.randint(-7, 7) # Keep within -8 to 8 range after fraction
        den = random.choice([2, 3, 4, 5, 8])
        num = random.randint(1, den - 1) # 1 <= num < den (V13.1 禁絕假分數)

        float_val = abs(int_part) + num / den
        if is_neg:
            float_val = -float_val
            int_part = -int_part if int_part != 0 else 0 # int_part should reflect sign for mixed fraction string
    else: # 整數
        int_part = random.randint(-8, 8)
        float_val = float(int_part)
        num = 0
        den = 0
        is_neg = float_val < 0

    # Ensure float_val is within -8 to 8 range
    if float_val > 8: float_val = 8.0
    if float_val < -8: float_val = -8.0
    
    # Special handling for -0.0
    if float_val == 0.0:
        is_neg = False # 0 is neither positive nor negative

    return float_val, (int(abs(int_part)), num, den, is_neg)

def _format_coordinate_latex(float_val, data_tuple):
    """
    功能: 將 _generate_coordinate_value() 的輸出格式化為 LaTeX 字串。
    實作細節: 嚴禁使用 f"{{...}}" 寫法，必須使用單層大括號模板。
    """
    int_part_abs, num, den, is_neg = data_tuple

    sign = "-" if is_neg else ""

    if num == 0:  # 整數
        return str(int(float_val))
    else:  # 分數或帶分數
        if int_part_abs == 0:  # 純分數
            return sign + r"\frac{{n}}{{d}}".replace("{n}", str(num)).replace("{d}", str(den))
        else:  # 帶分數
            return sign + str(int_part_abs) + r"\frac{{n}}{{d}}".replace("{n}", str(num)).replace("{d}", str(den))

def _format_coordinate_text(float_val):
    """
    功能: 將 float_val 格式化為適合普通文字敘述的字串。
    實作細節: if val.is_integer(): val = int(val) 確保整數以 int 格式呈現，避免 5.0 (V13.0)。
              處理分數時，顯示為 a/b 或 a b/c 格式。
    """
    if float_val == 0:
        return "0"

    if float_val.is_integer():
        return str(int(float_val))
    else:
        sign = "-" if float_val < 0 else ""
        abs_val = abs(float_val)
        
        # Convert to fraction
        # Use math.gcd to simplify, but handle common denominators like 2,3,4,5,8
        # This is a bit tricky to perfectly mirror the _generate_coordinate_value's fraction generation.
        # A simpler approach is to convert float to fraction with a limited denominator.
        
        # Try to represent as a fraction with a common denominator
        denominators = [2, 3, 4, 5, 8]
        best_frac_str = None
        min_diff = float('inf')

        for den in denominators:
            temp_num = round(abs_val * den)
            temp_val = temp_num / den
            diff = abs(temp_val - abs_val)
            if diff < min_diff:
                min_diff = diff
                # Check if it's a "good enough" approximation (e.g., within a very small epsilon)
                if diff < 1e-9:
                    num_int = int(temp_num)
                    int_part = num_int // den
                    num_rem = num_int % den
                    if num_rem == 0: # It's an integer
                         best_frac_str = str(int(abs_val))
                    elif int_part == 0: # Pure fraction
                         best_frac_str = f"{num_rem}/{den}"
                    else: # Mixed fraction
                         best_frac_str = f"{int_part} {num_rem}/{den}"
                    # Break if an exact or very close representation is found
                    break 
        
        if best_frac_str:
            return sign + best_frac_str
        else:
            # Fallback for floats that don't easily fit a simple fraction or if no suitable match
            # This case should ideally not be hit often if _generate_coordinate_value is well-designed.
            return str(float_val) 

def _format_coordinate_decimal_text(float_val):
    """
    功能: 將 float_val 格式化為適合 `check` 函數解析的字串 (整數或小數)。
    實作細節: 確保整數以 int 格式呈現，避免 5.0。
    """
    if float_val.is_integer():
        return str(int(float_val))
    else:
        return str(float_val)

def _draw_coordinate_plane(points_with_labels, title="直角坐標平面", highlight_origin=False):
    """
    功能: 繪製直角坐標平面，可選擇性標記點。
    參數:
        points_with_labels: 列表，每個元素為 (x, y, label)。防洩漏原則: 僅能傳入題目已知數據。
        title: 圖形標題。
        highlight_origin: 是否特別標示原點。
    回傳: image_base64 字串。
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=120) # DPI set to 120 as per system guardrails
    ax.set_aspect('equal') # V10.2 D, V11.6 Aspect Ratio

    # 座標範圍 (V13.0, V13.5)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

    # 格線 (V13.0)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    plt.grid(True, linestyle='--', alpha=0.6)

    # 坐標軸 (V13.6 Arrow Ban replacement)
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    # 坐標軸箭頭 (V13.6 Elite Guardrails)
    # x-axis arrow
    ax.plot(10, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    # y-axis arrow
    ax.plot(0, 10, "^k", transform=ax.get_xaxis_transform(), clip_on=False)
    # x, y labels
    ax.text(10.2, -0.5, 'x', ha='center', va='top', fontsize=12)
    ax.text(-0.5, 10.2, 'y', ha='right', va='center', fontsize=12)

    # 原點標註 (V10.2 D)
    ax.text(0, -0.8, '0', ha='center', va='top', fontsize=18, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # 點標註 (V13.0, V13.1, V13.5 標註權限隔離/標籤純淨化/標籤隔離)
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='blue', markersize=6) # 繪製點
        # V10.2 D 點標籤加白色光暈, V13.5 標籤隔離 (ax.text 內容只能是點的名稱)
        ax.text(x + 0.3, y + 0.3, label, fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    plt.title(title)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight') # DPI set to 120
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# 閱卷邏輯鐵則 (Only 4 Lines) - 必須精確複製此邏輯，不得添加 extra 判斷

    u_n = re.findall(r"[-+]?\d*\.?\d+", str(user_answer))
    c_n = re.findall(r"[-+]?\d*\.?\d+", str(correct_answer))
    return [float(x) for x in u_n] == [float(x) for x in c_n] if u_n else False


def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5])
    # problem_type = 5 # For testing specific types

    question_text = ""
    correct_answer = ""
    answer_data = None
    image_base64 = ""
    points_to_plot = [] # For _draw_coordinate_plane's points_with_labels parameter

    # Helper for generating non-zero coordinates for quadrant problems
    def _generate_non_zero_coordinate_value():
        while True:
            float_val, data_tuple = _generate_coordinate_value()
            if float_val != 0:
                return float_val, data_tuple

    # Helper for generating point labels that are distinct
    def _get_distinct_labels(count=1):
        return random.sample(POINT_LABELS, k=count)

    if problem_type == 1: # Type 1 (Maps to Example 1): 讀取坐標 (Reading Coordinates)
        point_label = _get_distinct_labels()[0]
        x_float, x_data = _generate_coordinate_value()
        y_float, y_data = _generate_coordinate_value()

        x_text = _format_coordinate_text(x_float)
        y_text = _format_coordinate_text(y_float)
        x_dec_text = _format_coordinate_decimal_text(x_float)
        y_dec_text = _format_coordinate_decimal_text(y_float)

        points_to_plot = [(x_float, y_float, point_label)]
        image_base64 = _draw_coordinate_plane(points_with_labels=points_to_plot)

        question_text = r"請寫出坐標平面上點 {Label} 的坐標。".replace("{Label}", point_label)
        correct_answer = "{Label}({x_dec_text}, {y_dec_text})".replace("{Label}", point_label)\
                                                        .replace("{x_dec_text}", x_dec_text)\
                                                        .replace("{y_dec_text}", y_dec_text)
        answer_data = (x_float, y_float)

    elif problem_type == 2: # Type 2 (Maps to Example 2): 標出坐標 (Plotting Points)
        point_label = _get_distinct_labels()[0]
        x_float, x_data = _generate_coordinate_value()
        y_float, y_data = _generate_coordinate_value()

        x_text = _format_coordinate_text(x_float)
        y_text = _format_coordinate_text(y_float)
        x_dec_text = _format_coordinate_decimal_text(x_float)
        y_dec_text = _format_coordinate_decimal_text(y_float)

        image_base64 = _draw_coordinate_plane(points_with_labels=[]) # V10.2 B 標點題防洩漏協定

        question_text = r"請在直角坐標平面上標出點 {Label}({x_text}, {y_text}) 的位置。 (無需繪圖，請想像其位置)".replace("{Label}", point_label)\
                                                                                                .replace("{x_text}", x_text)\
                                                                                                .replace("{y_text}", y_text)
        correct_answer = "{Label}({x_dec_text}, {y_dec_text})".replace("{Label}", point_label)\
                                                        .replace("{x_dec_text}", x_dec_text)\
                                                        .replace("{y_dec_text}", y_dec_text)
        answer_data = (x_float, y_float)

    elif problem_type == 3: # Type 3 (Maps to Example 3): 判斷象限 (Quadrant Identification)
        point_label = _get_distinct_labels()[0]
        
        # V12.6 強制運算: 確保 x_float 和 y_float 不會同時為 0
        while True:
            x_float, x_data = _generate_coordinate_value()
            y_float, y_data = _generate_coordinate_value()
            if not (x_float == 0 and y_float == 0):
                break

        x_text = _format_coordinate_text(x_float)
        y_text = _format_coordinate_text(y_float)

        result = ""
        if x_float > 0 and y_float > 0: result = "第一象限"
        elif x_float < 0 and y_float > 0: result = "第二象限"
        elif x_float < 0 and y_float < 0: result = "第三象限"
        elif x_float > 0 and y_float < 0: result = "第四象限"
        elif x_float == 0 and y_float != 0: result = "Y軸上"
        elif x_float != 0 and y_float == 0: result = "X軸上"
        else: result = "原點" # Should not be hit due to while loop, but for completeness

        image_base64 = _draw_coordinate_plane(points_with_labels=[])

        question_text = r"已知點 {Label} 的坐標為 ({x_text}, {y_text})，請問點 {Label} 位於哪一個象限或坐標軸上？".replace("{Label}", point_label)\
                                                                                                        .replace("{x_text}", x_text)\
                                                                                                        .replace("{y_text}", y_text)
        correct_answer = result
        answer_data = result

    elif problem_type == 4: # Type 4 (Maps to Example 4): 坐標變換/對稱 (Coordinate Transformation/Symmetry)
        label_orig, label_new = _get_distinct_labels(count=2)
        
        x_orig_float, x_orig_data = _generate_coordinate_value()
        y_orig_float, y_orig_data = _generate_coordinate_value()

        x_orig_text = _format_coordinate_text(x_orig_float)
        y_orig_text = _format_coordinate_text(y_orig_float)

        transform_type = random.choice(["X軸對稱", "Y軸對稱", "原點對稱"])

        x_new_float, y_new_float = 0, 0
        if transform_type == "X軸對稱":
            x_new_float, y_new_float = x_orig_float, -y_orig_float
        elif transform_type == "Y軸對稱":
            x_new_float, y_new_float = -x_orig_float, y_orig_float
        else: # 原點對稱
            x_new_float, y_new_float = -x_orig_float, -y_orig_float
        
        x_new_dec_text = _format_coordinate_decimal_text(x_new_float)
        y_new_dec_text = _format_coordinate_decimal_text(y_new_float)

        image_base64 = _draw_coordinate_plane(points_with_labels=[])

        question_text = r"已知點 {Label_orig}({x_orig_text}, {y_orig_text})，若點 {Label_new} 是點 {Label_orig} 對 {transform_type} 的對稱點，則 {Label_new} 點的坐標為何？".replace("{Label_orig}", label_orig)\
                                                                                                                                                            .replace("{x_orig_text}", x_orig_text)\
                                                                                                                                                            .replace("{y_orig_text}", y_orig_text)\
                                                                                                                                                            .replace("{Label_new}", label_new)\
                                                                                                                                                            .replace("{transform_type}", transform_type)
        correct_answer = "{Label_new}({x_new_dec_text}, {y_new_dec_text})".replace("{Label_new}", label_new)\
                                                                    .replace("{x_new_dec_text}", x_new_dec_text)\
                                                                    .replace("{y_new_dec_text}", y_new_dec_text)
        answer_data = (x_new_float, y_new_float)

    elif problem_type == 5: # Type 5 (Maps to Example 5): 坐標軸上的點 (Points on Axes)
        point_label = _get_distinct_labels()[0]
        abs_val = random.randint(1, 8)
        axis_type = random.choice(["X軸", "Y軸"])
        
        abs_val_text = str(abs_val)

        possible_coords = []
        correct_answer_parts = []
        question_text_template = ""

        if axis_type == "X軸":
            possible_coords = [(float(abs_val), 0.0), (float(-abs_val), 0.0)]
            question_text_template = r"已知點 {Label} 在 X 軸上，且與 Y 軸的距離為 {abs_val_text} 單位長，則點 {Label} 的坐標可能為何？ (請列出所有可能，以逗號分隔)"
        else: # Y軸
            possible_coords = [(0.0, float(abs_val)), (0.0, float(-abs_val))]
            question_text_template = r"已知點 {Label} 在 Y 軸上，且與 X 軸的距離為 {abs_val_text} 單位長，則點 {Label} 的坐標可能為何？ (請列出所有可能，以逗號分隔)"
        
        # Sort for consistent answer_data and correct_answer string generation
        possible_coords.sort(key=lambda p: (p[0], p[1]))

        for x, y in possible_coords:
            x_dec_text = _format_coordinate_decimal_text(x)
            y_dec_text = _format_coordinate_decimal_text(y)
            correct_answer_parts.append(f"{point_label}({x_dec_text}, {y_dec_text})")
        
        correct_answer = ", ".join(correct_answer_parts)

        image_base64 = _draw_coordinate_plane(points_with_labels=[])

        question_text = question_text_template.replace("{Label}", point_label)\
                                             .replace("{abs_val_text}", abs_val_text)
        answer_data = possible_coords

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_data,
        "image_base64": image_base64,
        "created_at": datetime.now(),
        "version": __version__
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
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
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
