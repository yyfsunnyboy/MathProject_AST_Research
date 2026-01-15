# ==============================================================================
# ID: jh_數學1下_GraphOfTwoVariableLinearEquation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 116.33s | RAG: 3 examples
# Created At: 2026-01-15 15:07:21
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
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import json
import re # For Pure Feedback Protocol in check()
from fractions import Fraction # For robust fraction handling

# 設定字體以支援繁體中文 (台灣)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 使用微軟正黑體，並提供通用無襯線字體作為備用
plt.rcParams['axes.unicode_minus'] = False # 確保負號能正確顯示

# --- 輔助函式 (Helper Functions) ---
# 這些函式必須以 '_' 開頭，且回傳值若用於 question_text 必須轉為字串。
# 所有輔助函式最後一行必須明確使用 'return' 語句回傳結果。

def _gcd(a, b):
    # 計算最大公因數
    # 必須回傳
    return math.gcd(a, b)

def _simplify_fraction(numerator, denominator):
    # 簡化分數
    # 必須回傳
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    if numerator == 0:
        return 0, 1 # 0/1
    
    common = _gcd(abs(numerator), abs(denominator))
    return numerator // common, denominator // common

def _float_to_structured_coord(val):
    """
    將浮點數值轉換為結構化座標數據 (float_val, (abs_int_part, abs_num, den, is_neg_flag))。
    - val: 實際的浮點數值。
    - abs_int_part: 整數部分的絕對值。
    - abs_num: 分數部分的分子絕對值。
    - den: 分數部分的分母。
    - is_neg_flag: 布林值，表示數字是否為負。
    必須回傳 (float_val, (abs_int_part, abs_num, den, is_neg_flag))。
    """
    is_neg_flag = val < 0
    abs_val = abs(val)
    
    # 使用 Fraction 處理浮點數精度並簡化，限制分母大小以符合 K12 數學
    try:
        f = Fraction(abs_val).limit_denominator(100) # 限制分母最大為100
    except OverflowError: # 處理可能出現的極大數值
        f = Fraction(round(abs_val * 1000), 1000).limit_denominator(100)

    abs_int_part = int(f)
    frac_part = f - abs_int_part
    
    abs_num = frac_part.numerator
    den = frac_part.denominator
    
    if abs_num == 0: # 如果是整數
        return val, (abs_int_part, 0, 0, is_neg_flag)
    else: # 如果是分數或帶分數
        return val, (abs_int_part, abs_num, den, is_neg_flag)

def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    生成一個隨機座標值 (整數或分數)，並回傳其結構化表示。
    必須回傳 (float_val, (abs_int_part, abs_num, den, is_neg_flag))。
    - float_val: 實際的浮點數值。
    - abs_int_part: 整數部分的絕對值。
    - abs_num: 分數部分的分子絕對值。
    - den: 分數部分的分母。
    - is_neg_flag: 布林值，表示數字是否為負。
    """
    val = random.randint(min_val, max_val)
    
    float_val = float(val)

    if allow_fraction and random.random() < 0.5: # 50% 機率生成分數 (如果允許)
        # 生成一個真分數
        numerator = random.randint(1, 9)
        denominator = random.randint(2, 10)
        
        # 確保分數已簡化
        common = _gcd(numerator, denominator)
        numerator //= common
        denominator //= common
        
        if numerator != 0:
            float_val = float(val) + float(numerator) / denominator
        # 如果 numerator == 0，則它已經是整數了，保持 float_val 不變

    # 隨機決定正負號 (如果不是 0)
    if float_val != 0 and random.choice([True, False]):
        float_val = -float_val
        
    # 將浮點數值轉換為結構化座標數據以進行一致的格式化
    return _float_to_structured_coord(float_val)


def _format_coordinate_latex(coord_data_tuple):
    """
    將結構化座標數據格式化為 LaTeX 字串。
    遵循 V10.2 LaTeX 模板規範，嚴禁使用 f"{{...}}"。
    """
    float_val, (abs_int_part, abs_num, den, is_neg_flag) = coord_data_tuple
    
    if float_val == 0:
        return r"0"
    
    sign = r"-" if is_neg_flag else r""
    
    if abs_num == 0: # 整數
        expr = r"{s}{i}".replace("{s}", sign).replace("{i}", str(abs_int_part))
    elif abs_int_part == 0: # 純分數
        expr = r"{s}\frac{{{n}}}{{{d}}}".replace("{s}", sign).replace("{n}", str(abs_num)).replace("{d}", str(den))
    else: # 帶分數
        expr = r"{s}{i}\frac{{{n}}}{{{d}}}".replace("{s}", sign).replace("{i}", str(abs_int_part)).replace("{n}", str(abs_num)).replace("{d}", str(den))
    
    return expr


def _get_two_points_on_line(A, B, C, x_range=(-7, 7), y_range=(-7, 7), max_attempts=100):
    """
    在直線 Ax + By = C 上找到兩個不同的點。
    確保點的座標在指定範圍內，並盡量避免分數。
    必須回傳 (x1, y1), (x2, y2)
    """
    points = []
    
    # 優先嘗試尋找整數點
    for _ in range(max_attempts):
        x_val = random.randint(x_range[0], x_range[1])
        
        if B != 0:
            y_float = (C - A * x_val) / B
            if abs(y_float - round(y_float)) < 1e-9: # 檢查是否接近整數
                y_val = int(round(y_float))
                if y_range[0] <= y_val <= y_range[1]:
                    point = (x_val, y_val)
                    if point not in points:
                        points.append(point)
        elif A != 0: # 垂直線 x = C/A
            x_float = C / A
            if abs(x_float - round(x_float)) < 1e-9: # 檢查是否接近整數
                x_val = int(round(x_float))
                if x_range[0] <= x_val <= x_range[1]:
                    y_val = random.randint(y_range[0], y_range[1])
                    point = (x_val, y_val)
                    if point not in points:
                        points.append(point)
        
        if len(points) >= 2:
            break
            
    # 如果整數點不足，則生成一些浮點數點
    while len(points) < 2:
        if B != 0:
            x_val = random.uniform(x_range[0], x_range[1])
            y_val = (C - A * x_val) / B
            if y_range[0] <= y_val <= y_range[1]:
                point = (round(x_val, 2), round(y_val, 2)) # 四捨五入到兩位小數
                if point not in points:
                    points.append(point)
        elif A != 0: # 垂直線 x = C/A
            x_val = C / A
            if x_range[0] <= x_val <= x_range[1]:
                y_val = random.uniform(y_range[0], y_range[1])
                point = (round(x_val, 2), round(y_val, 2))
                if point not in points:
                    points.append(point)
        else: # A=0, B=0, C=0 (0=0) 或 C!=0 (0=C) - 應在上游避免此情況
            raise ValueError("Invalid line equation (A=0, B=0)")

        # 確保點是不同的
        if len(points) == 2 and points[0] == points[1]:
            points.pop() # 移除重複點並重新嘗試
            
    return points[0], points[1]

def _calculate_line_equation_from_points(p1, p2):
    """
    根據兩點計算直線方程式 Ax + By = C。
    回傳標準化後的 (A, B, C)，其中 A >= 0，且 A, B, C 互質。
    必須回傳 (A, B, C)
    """
    x1, y1 = p1
    x2, y2 = p2

    # 計算 Ax + By = C 的係數
    A_raw = y2 - y1
    B_raw = x1 - x2
    C_raw = A_raw * x1 + B_raw * y1

    # 處理浮點數精度問題並嘗試轉換為整數係數
    multiplier = 1
    max_decimal_places = 0
    
    # 找出最大的小數位數
    for val in [A_raw, B_raw, C_raw]:
        s_val = str(val)
        if '.' in s_val:
            dec_places = len(s_val) - s_val.index('.') - 1
            max_decimal_places = max(max_decimal_places, dec_places)
    
    # 如果有小數，則乘以 10^max_decimal_places 清除小數
    if max_decimal_places > 0:
        multiplier = 10 ** max_decimal_places
        A = round(A_raw * multiplier)
        B = round(B_raw * multiplier)
        C = round(C_raw * multiplier)
    else: # 如果都是整數，直接轉換
        A, B, C = int(A_raw), int(B_raw), int(C_raw)

    # 標準化方程式
    if A == 0 and B == 0:
        if C == 0:
            raise ValueError("Points do not define a unique line (same point).")
        else:
            raise ValueError("Points do not define a line (contradiction).")

    # 確保 A 為正 (除非 A=0，則 B 為正)
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    
    # 簡化 A, B, C 使其互質
    common_divisor = abs(A)
    if B != 0:
        common_divisor = _gcd(common_divisor, abs(B))
    if C != 0:
        common_divisor = _gcd(common_divisor, abs(C))
    
    if common_divisor != 0 and common_divisor != 1:
        A //= common_divisor
        B //= common_divisor
        C //= common_divisor

    return A, B, C

def _is_point_on_line(point, A, B, C, tolerance=1e-9):
    """
    檢查一個點是否在直線上 Ax + By = C。
    必須回傳布林值
    """
    x, y = point
    return abs(A * x + B * y - C) < tolerance

def _format_equation_latex(A, B, C):
    """
    將 A, B, C 格式化為 LaTeX 數學方程式字串 Ax + By = C。
    遵循 V10.2 LaTeX 模板規範。
    """
    parts = []

    # 確保 A, B, C 是整數，以便格式化
    A, B, C = int(A), int(B), int(C)

    if A == 1:
        parts.append(r"x")
    elif A == -1:
        parts.append(r"-x")
    elif A != 0:
        parts.append(r"{a}x".replace("{a}", str(A)))

    if B == 1:
        parts.append(r"+y" if parts else r"y")
    elif B == -1:
        parts.append(r"-y")
    elif B != 0:
        op = r"+" if B > 0 and parts else r""
        parts.append(r"{op}{b}y".replace("{op}", op).replace("{b}", str(B)))

    if not parts: # A=0, B=0 的情況不應發生於有效直線，但為防錯處理
        return r"0 = {c}".replace("{c}", str(C))

    equation_str = "".join(parts)
    expr = r"{eq} = {c}".replace("{eq}", equation_str).replace("{c}", str(C))
    return expr

# --- 視覺化函式 (Visualization Helper) ---
def draw_coordinate_plane(points=[], lines_data=[], x_min=-10, x_max=10, y_min=-10, y_max=10, title="", show_grid=True):
    """
    繪製座標平面，可選顯示點和直線。
    - points: 格式為 [(x, y, label), ...]。
    - lines_data: 格式為 [(A, B, C), ...] 表示 Ax+By=C 的直線。
    - 防洩漏原則: 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
    - 必須回傳 base64 編碼的圖片字串。
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # 確保正方形比例, 設定DPI

    # V10.2 Pure Style: ax.set_aspect('equal')
    ax.set_aspect('equal')

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # 網格
    if show_grid:
        ax.axhline(0, color='black', linewidth=0.8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.grid(True, linestyle='--', alpha=0.6)

    # 坐標軸刻度：必須顯示每 1 單位的「刻度線 (Tick marks)」
    ax.set_xticks(np.arange(x_min, x_max + 1, 1))
    ax.set_yticks(np.arange(y_min, y_max + 1, 1))
    
    # 標籤規範：刻度數字僅顯示原點 '0' (18 號加粗)，其餘刻度嚴禁顯示數字標籤。
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # 標註原點 '0'
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')
    
    # 繪製直線
    for A, B, C in lines_data:
        if B != 0: # 非垂直線
            x_vals = np.array([x_min, x_max])
            y_vals = (C - A * x_vals) / B
            ax.plot(x_vals, y_vals, color='blue', linestyle='-')
        elif A != 0: # 垂直線 x = C/A
            x_val = C / A
            ax.axvline(x=x_val, color='blue', linestyle='-')

    # 繪製點
    for x, y, label in points:
        ax.plot(x, y, 'o', color='red', markersize=8)
        # 點標籤必須加白色光暈 (bbox)
        ax.text(x + 0.2, y + 0.2, label, color='black', fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title(title)
    
    # 將圖片轉換為 base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # 確保 DPI 在此處設定
    plt.close(fig) # 關閉圖形以釋放記憶體
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return image_base64

# --- 頂層函式 ---

def generate(level=1):
    """
    根據難度等級生成 K12 數學「二元一次方程式的圖形」題目。
    - level: 難度等級 (1-3)。
    - 必須回傳包含 question_text, correct_answer, answer, image_base64 的字典。
    - 內部使用 random.choice 或 if/elif 邏輯對應 RAG 例題。
    - 數據隨機生成，答案透過公式計算。
    """
    problem_type = random.choice([1, 2, 3, 4, 5])
    
    question_text = ""
    correct_answer = ""
    image_base64 = ""

    # 座標範圍
    x_min, x_max = -7, 7
    y_min, y_max = -7, 7

    # 動態化參數 A, B, C (for Ax + By = C)
    # 確保 A, B 不全為 0，並標準化方程式
    while True:
        A = random.randint(-5, 5)
        B = random.randint(-5, 5)
        C = random.randint(-15, 15)
        
        if A == 0 and B == 0: # 0x + 0y = C 不是直線
            continue
        
        # 簡化並標準化 A, B, C
        common_divisor = abs(A)
        if B != 0:
            common_divisor = _gcd(common_divisor, abs(B))
        if C != 0:
            common_divisor = _gcd(common_divisor, abs(C))
        
        if common_divisor != 0:
            A //= common_divisor
            B //= common_divisor
            C //= common_divisor
        
        # 確保 A 為正 (除非 A=0，則 B 為正)，以保證方程式形式的唯一性
        if A < 0 or (A == 0 and B < 0):
            A, B, C = -A, -B, -C
        
        # 對於 Type 4 (截距題)，A 和 B 不能為 0
        if problem_type == 4 and (A == 0 or B == 0):
            continue
        
        break # 找到有效的 A, B, C

    equation_latex = _format_equation_latex(A, B, C)

    # 選擇題型並生成題目
    if problem_type == 1: # Type 1 (映射 RAG Ex 1): 繪製一般二元一次方程式的圖形。
        # 題目：請在座標平面上畫出方程式 $Ax + By = C$ 的圖形。
        question_text = r"請在座標平面上畫出二元一次方程式 $" + equation_latex + r"$ 的圖形。"

        # 正確答案：定義該直線的兩個點。
        p1, p2 = _get_two_points_on_line(A, B, C, x_range=(x_min, x_max), y_range=(y_min, y_max))
        correct_answer = json.dumps([p1, p2]) # 將點序列化為 JSON 字串

        # 繪圖：顯示空白座標平面，學生需自行繪製。
        image_base64 = draw_coordinate_plane(points=[], lines_data=[], x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, title=r"座標平面")

    elif problem_type == 2: # Type 2 (映射 RAG Ex 3): 判斷給定點是否在直線上。
        # 題目：判斷點 $(x, y)$ 是否在方程式 $Ax + By = C$ 的圖形上？
        
        # 生成一個測試點
        test_x_float, test_x_data = _generate_coordinate_value(x_min, x_max, allow_fraction=False) # 初始為整數
        test_y_float, test_y_data = _generate_coordinate_value(y_min, y_max, allow_fraction=False) # 初始為整數

        # 50% 機率使點在線上
        is_on_line_flag = random.choice([True, False])
        
        if is_on_line_flag:
            # 調整一個座標，使其位於線上
            if B != 0: # 優先調整 Y 座標
                y_on_line = (C - A * test_x_float) / B
                test_point_float = (test_x_float, y_on_line)
            elif A != 0: # 如果 B=0 (垂直線)，則調整 X 座標
                x_on_line = (C - B * test_y_float) / A
                test_point_float = (x_on_line, test_y_float)
            else: # 不應發生 (A, B 不全為零)
                raise ValueError("Invalid line equation (A=0, B=0)")
            
            # 將調整後的浮點數值重新轉換為結構化座標數據，以用於 LaTeX 格式化
            test_x_float, test_x_data = _float_to_structured_coord(test_point_float[0])
            test_y_float, test_y_data = _float_to_structured_coord(test_point_float[1])
            test_point_float = (test_x_float, test_y_float) # 更新為可能經過四捨五入的值
        else:
            # 如果點不在線上，確保它在初始隨機生成後確實不在線上
            test_point_float = (test_x_float, test_y_float)
            if _is_point_on_line(test_point_float, A, B, C):
                # 輕微擾動 Y 座標 (如果可能)，否則擾動 X 座標
                if B != 0:
                    test_y_float += random.choice([-1, 1]) * 0.5 # 增加或減少 0.5
                else: # A != 0
                    test_x_float += random.choice([-1, 1]) * 0.5
                
                test_x_float, test_x_data = _float_to_structured_coord(test_x_float)
                test_y_float, test_y_data = _float_to_structured_coord(test_y_float)
                test_point_float = (test_x_float, test_y_float)

        point_latex = r"({x_val}, {y_val})".replace("{x_val}", _format_coordinate_latex(test_x_data)).replace("{y_val}", _format_coordinate_latex(test_y_data))
        
        question_text = r"判斷點 $" + point_latex + r"$ 是否在方程式 $" + equation_latex + r"$ 的圖形上？"

        # 計算正確答案
        is_on_line = _is_point_on_line(test_point_float, A, B, C)
        correct_answer = "是" if is_on_line else "否"

        # 繪圖：顯示直線和測試點。
        lines_to_draw = [(A, B, C)]
        points_to_draw = [(test_point_float[0], test_point_float[1], r"P")]
        image_base64 = draw_coordinate_plane(points=points_to_draw, lines_data=lines_to_draw, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, title=r"座標平面")

    elif problem_type == 3: # Type 3 (RAG Ex 1/2 的變體): 繪製水平線或垂直線。
        # 題目：請在座標平面上畫出方程式 $x=k$ 或 $y=k$ 的圖形。
        is_horizontal = random.choice([True, False])
        k_val_float, k_val_data = _generate_coordinate_value(x_min, x_max, allow_fraction=False) # 為了簡潔，通常取整數

        if is_horizontal: # y = k
            A_line, B_line, C_line = 0, 1, k_val_float
            equation_latex_specific = r"y = {k}".replace("{k}", _format_coordinate_latex(k_val_data))
        else: # x = k
            A_line, B_line, C_line = 1, 0, k_val_float
            equation_latex_specific = r"x = {k}".replace("{k}", _format_coordinate_latex(k_val_data))
        
        question_text = r"請在座標平面上畫出二元一次方程式 $" + equation_latex_specific + r"$ 的圖形。"

        # 正確答案：定義該直線的兩個點。
        p1, p2 = _get_two_points_on_line(A_line, B_line, C_line, x_range=(x_min, x_max), y_range=(y_min, y_max))
        correct_answer = json.dumps([p1, p2])

        # 繪圖：顯示空白座標平面。
        image_base64 = draw_coordinate_plane(points=[], lines_data=[], x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, title=r"座標平面")

    elif problem_type == 4: # Type 4 (與 RAG 範例相關，但非直接映射): 找出 x 截距與 y 截距。
        # 題目：找出方程式 $Ax + By = C$ 的 $x$ 截距與 $y$ 截距。
        # A, B 在初始循環中已保證不為零。
        
        question_text = r"找出二元一次方程式 $" + equation_latex + r"$ 的 $x$ 截距與 $y$ 截距。"

        # 計算正確答案
        x_intercept = C / A
        y_intercept = C / B
        
        correct_answer = json.dumps({
            "x_intercept": x_intercept,
            "y_intercept": y_intercept
        })

        # 繪圖：顯示該直線。
        lines_to_draw = [(A, B, C)]
        image_base64 = draw_coordinate_plane(points=[], lines_data=lines_to_draw, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, title=r"座標平面")

    elif problem_type == 5: # Type 5 (映射 RAG Ex 2/3 的逆向問題): 從圖形 (兩點) 找出方程式。
        # 題目：觀察下圖，找出通過兩點 $P_1$ 和 $P_2$ 的直線方程式。
        
        # 生成兩個不同的點
        point1_float_x, _ = _generate_coordinate_value(x_min, x_max, allow_fraction=False)
        point1_float_y, _ = _generate_coordinate_value(y_min, y_max, allow_fraction=False)
        point1 = (point1_float_x, point1_float_y)

        point2_float_x, _ = _generate_coordinate_value(x_min, x_max, allow_fraction=False)
        point2_float_y, _ = _generate_coordinate_value(y_min, y_max, allow_fraction=False)
        point2 = (point2_float_x, point2_float_y)
        
        # 確保兩點不同
        while point1 == point2:
            point2_float_x, _ = _generate_coordinate_value(x_min, x_max, allow_fraction=False)
            point2_float_y, _ = _generate_coordinate_value(y_min, y_max, allow_fraction=False)
            point2 = (point2_float_x, point2_float_y)

        # 計算通過這兩點的直線方程式
        A_line, B_line, C_line = _calculate_line_equation_from_points(point1, point2)
        correct_equation_latex = _format_equation_latex(A_line, B_line, C_line)

        # 格式化問題文字中的點座標
        point1_str_x = _format_coordinate_latex(_float_to_structured_coord(point1[0]))
        point1_str_y = _format_coordinate_latex(_float_to_structured_coord(point1[1]))
        point2_str_x = _format_coordinate_latex(_float_to_structured_coord(point2[0]))
        point2_str_y = _format_coordinate_latex(_float_to_structured_coord(point2[1]))

        question_text = (r"觀察下圖，找出通過點 $({x1_str}, {y1_str})$ 和點 $({x2_str}, {y2_str})$ 的直線方程式。"
                         .replace("{x1_str}", point1_str_x)
                         .replace("{y1_str}", point1_str_y)
                         .replace("{x2_str}", point2_str_x)
                         .replace("{y2_str}", point2_str_y))

        correct_answer = correct_equation_latex # 標準化後的方程式字串

        # 繪圖：顯示兩點和直線。
        lines_to_draw = [(A_line, B_line, C_line)]
        points_to_draw = [(point1[0], point1[1], r"P_1"), (point2[0], point2[1], r"P_2")]
        image_base64 = draw_coordinate_plane(points=points_to_draw, lines_data=lines_to_draw, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, title=r"座標平面")

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 留空，等待用戶輸入
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    檢查用戶答案是否正確。
    - user_answer: 用戶提交的答案字串。
    - correct_answer: generate 函式回傳的正確答案字串。
    - 必須回傳布林值。
    """
    # Pure Feedback Protocol: 規範 `sanitized_ans` 的生成，儘管此 `check` 函式僅回傳布林值。
    sanitized_ans = re.sub(r"[\$\\]", "", str(correct_answer))

    try:
        # Type 1 & 3: 繪製直線。`correct_answer` 是定義直線的兩個點 (JSON 字串)。
        # 假設 `user_answer` 也是包含兩個點的 JSON 字串 (例如: "[[1,2],[3,4]]")。
        if isinstance(correct_answer, str) and correct_answer.strip().startswith('['):
            correct_points = json.loads(correct_answer)
            if not (isinstance(correct_points, list) and len(correct_points) == 2): return False
            
            user_points = json.loads(user_answer)
            if not (isinstance(user_points, list) and len(user_points) == 2): return False
            
            # 從正確答案的兩點計算標準化後的直線方程式
            A_corr, B_corr, C_corr = _calculate_line_equation_from_points(tuple(correct_points[0]), tuple(correct_points[1]))
            
            # 從用戶答案的兩點計算標準化後的直線方程式
            A_user, B_user, C_user = _calculate_line_equation_from_points(tuple(user_points[0]), tuple(user_points[1]))
            
            # 比較標準化後的方程式
            return (A_corr == A_user and B_corr == B_user and C_corr == C_user)

        # Type 2: 判斷點是否在線上。答案為 "是" 或 "否"。
        elif correct_answer == "是" or correct_answer == "否":
            return user_answer == correct_answer

        # Type 4: 找出 x 截距與 y 截距。答案為包含截距的 JSON 字串字典。
        # 假設 `user_answer` 也是 JSON 字典 (例如: '{"x_intercept": 2.5, "y_intercept": 5}')。
        elif isinstance(correct_answer, str) and correct_answer.strip().startswith('{'):
            corr_data = json.loads(correct_answer)
            user_data = json.loads(user_answer)
            
            x_corr = corr_data.get("x_intercept")
            y_corr = corr_data.get("y_intercept")
            x_user = user_data.get("x_intercept")
            y_user = user_data.get("y_intercept")
            
            # 使用容忍度比較浮點數
            x_match = (x_corr is None and x_user is None) or (abs(x_corr - x_user) < 1e-9)
            y_match = (y_corr is None and y_user is None) or (abs(y_corr - y_user) < 1e-9)
            
            return x_match and y_match

        # Type 5: 從圖形找出方程式。答案為 LaTeX 方程式字串。
        # 假設 `user_answer` 也是標準化後的 LaTeX 方程式字串。
        elif isinstance(correct_answer, str) and r"=" in correct_answer:
            # 由於沒有提供符號解析器，目前採用嚴格字串比對。
            # 實際應用中，應將用戶答案解析為 A, B, C 形式並進行標準化比較。
            return user_answer.strip() == correct_answer.strip()

    except Exception as e:
        # 實際系統中，此處應記錄錯誤日誌。
        # print(f"Error in check function: {e}") 
        return False
    
    return False # 如果答案類型無法識別或發生錯誤，預設為錯誤。


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
