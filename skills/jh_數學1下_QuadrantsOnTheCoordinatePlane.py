# ==============================================================================
# ID: jh_數學1下_QuadrantsOnTheCoordinatePlane
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 74.27s | RAG: 4 examples
# Created At: 2026-01-15 15:08:35
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
import re
from datetime import datetime

# Mandatory: Use Figure for thread-safety, not pyplot directly
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import matplotlib.patches as patches

# --- INFRASTRUCTURE RULES: Font Configuration ---
# Set plt.rcParams for font. This is a global setting for matplotlib.
# Even if Figure is used for plotting, rcParams affects text rendering.
# This must be done at the module level.
try:
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # Add fallback font
    plt.rcParams['axes.unicode_minus'] = False # Solve minus sign problem in plots
except ImportError:
    # If matplotlib.pyplot is not available, log a warning or handle gracefully.
    # The spec implies it should be available for rcParams configuration.
    print("Warning: matplotlib.pyplot not available for font configuration. Fonts might not render as expected.")


# --- 頂層函式 ---
def generate(level=1):
    """
    根據難度等級生成 K12 數學「坐標平面上的象限」題目。
    """
    # 隨機選擇題型
    # 嚴格遵循 Architect's Spec 中的題型名稱
    problem_type_choices = [
        "Type 1: Identify Quadrant/Axis from Point",
        "Type 2: Identify Quadrant from Conditions",
        "Type 3: Determine Quadrant of Derived Point",
        "Type 4: Plot Points on Coordinate Plane"
    ]
    
    problem_type = random.choice(problem_type_choices)

    if problem_type == "Type 1: Identify Quadrant/Axis from Point":
        return _generate_type1_problem(level)
    elif problem_type == "Type 2: Identify Quadrant from Conditions":
        return _generate_type2_problem(level)
    elif problem_type == "Type 3: Determine Quadrant of Derived Point":
        return _generate_type3_problem(level)
    elif problem_type == "Type 4: Plot Points on Coordinate Plane":
        return _generate_type4_problem(level)


    """
    檢查使用者答案是否正確。
    【Result Feedback (Pure Feedback Protocol)】: 
    - `result` 欄位必須提供「去 LaTeX 化」的純淨答案。
    - 【強力清洗】：在組合回饋字串前，必須定義 `sanitized_ans = re.sub(r"[\$\\]", "", str(correct_answer))`。
    - 【回傳限制】：錯誤回饋必須嚴格使用 `r"答案錯誤。正確答案為：{ans}".replace("{ans}", sanitized_ans)`。
    """
    # 強力清洗 correct_answer，移除 LaTeX 符號
    sanitized_ans = re.sub(r"[\$\\]", "", str(correct_answer))

    # 根據 Spec，check 函式目前主要處理字串比較
    if isinstance(user_answer, str) and isinstance(correct_answer, str):
        # 對於 Type 4，correct_answer 是 JSON 字串，user_answer 也應是字串形式
        # 進行字串比較
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    else:
        # 如果類型不匹配，則視為不正確
        is_correct = False
    
    return {
        "is_correct": is_correct,
        "result": "正確" if is_correct else r"答案錯誤。正確答案為：{ans}".replace("{ans}", sanitized_ans)
    }

# --- 輔助函式通用規範 (Generic Helper Rules) ---
# 所有輔助函式必須回傳結果，若用於拼接 question_text 則強制轉為 str。
# 視覺化函式僅接收題目已知數據，嚴禁洩漏答案。

def _generate_coordinate_value(min_val=-10, max_val=10, allow_fraction=False):
    """
    生成一個隨機的坐標值 (整數或分數)，並返回其浮點值及用於格式化的元組。
    回傳: (float_val, (int_part, num, den, is_neg))
    """
    is_neg = random.choice([True, False])
    sign = -1 if is_neg else 1

    if allow_fraction and random.random() < 0.3: # 約30%機率生成分數
        int_part = random.randint(0, abs(max_val) - 1) if abs(max_val) > 0 else 0
        num = random.randint(1, 4) # 分子
        den = random.choice([2, 3, 4, 5]) # 分母
        while num >= den: # 確保真分數
            num = random.randint(1, 4)
        
        float_val_abs = (int_part + num / den)
        float_val = sign * float_val_abs

        # 確保在 min_val 和 max_val 之間
        if float_val < min_val:
            float_val = float(min_val)
        elif float_val > max_val:
            float_val = float(max_val)
        
        # 重新判斷符號和整數部分，以防邊界調整
        is_neg = float_val < 0
        if float_val == 0.0: # 處理 0 的特殊情況
            int_part = 0
            num = 0
            den = 0
            is_neg = False
        elif int_part == 0 and float_val_abs < 1: # 純分數
            pass # num, den already set
        else: # 帶分數
             # Re-extract int_part and fraction for formatting if float_val was adjusted
            abs_float_val = abs(float_val)
            int_part = int(abs_float_val)
            fraction_part = abs_float_val - int_part
            if fraction_part > 1e-9: # If there's a fractional part
                # Try to approximate the original fraction or generate a new simple one
                # This is a simplification; for exact reconstruction, more complex logic is needed.
                # For this problem, as long as the float_val is correct, the latex format can be simplified.
                # Let's keep the original num/den if int_part is the same, otherwise default to int.
                if int(abs_float_val) != int_part or abs(abs_float_val - (int_part + num/den)) > 1e-9:
                    num = 0 # Default to integer format if fraction is complex
                    den = 0
            else:
                num = 0
                den = 0

    else: # 整數
        val = random.randint(min_val, max_val)
        float_val = float(val)
        int_part = abs(val)
        num = 0
        den = 0
        is_neg = val < 0
        if val == 0: is_neg = False # 0 is neither positive nor negative

    return float_val, (int_part, num, den, is_neg)

def _format_coordinate_latex(data):
    """
    將 _generate_coordinate_value 回傳的數據格式化為 LaTeX 字串。
    嚴禁使用 f"{{...}}" 這種寫法。
    """
    float_val, (int_part, num, den, is_neg) = data
    
    if float_val == 0.0:
        return "0"

    if num == 0 and den == 0: # 整數
        if is_neg:
            expr = r"-{v}".replace("{v}", str(int_part))
        else:
            expr = r"{v}".replace("{v}", str(int_part))
    else: # 分數或帶分數
        sign_str = "-" if is_neg else ""
        if int_part == 0: # 純分數
            expr = r"{s}\frac{{{n}}}{{{d}}}".replace("{s}", sign_str).replace("{n}", str(num)).replace("{d}", str(den))
        else: # 帶分數
            expr = r"{s}{i}\frac{{{n}}}{{{d}}}".replace("{s}", sign_str).replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))
    return expr

def _get_quadrant_info(x, y):
    """
    根據坐標 (x, y) 返回其所在的象限或坐標軸名稱。
    """
    # 使用小於 epsilon 的閾值來判斷是否為 0，避免浮點數精度問題
    epsilon = 1e-9 
    
    is_x_zero = abs(x) < epsilon
    is_y_zero = abs(y) < epsilon

    if is_x_zero and is_y_zero:
        return "原點"
    elif is_x_zero:
        return "y軸"
    elif is_y_zero:
        return "x軸"
    elif x > epsilon and y > epsilon:
        return "第一象限"
    elif x < -epsilon and y > epsilon:
        return "第二象限"
    elif x < -epsilon and y < -epsilon:
        return "第三象限"
    else: # x > epsilon and y < -epsilon
        return "第四象限"

# --- 視覺化與輔助函式通用規範 ---
def _draw_coordinate_plane(points, x_range=(-10, 10), y_range=(-10, 10), title="", show_labels=True, plot_points_only=False):
    """
    繪製坐標平面。
    points: 列表，每個元素為 (x, y, label_text, color)。
    plot_points_only: 若為 True，則 points 參數將被忽略，僅繪製網格和坐標軸 (用於標點題防洩漏)。
    """
    # ULTRA VISUAL STANDARDS: Use Figure for thread-safety, dpi=300
    fig = Figure(figsize=(6, 6), dpi=300) 
    canvas = FigureCanvasAgg(fig) # Required for rendering Figure without pyplot.show()
    ax = fig.add_subplot(111)
    
    # D. 視覺一致性 (V10.2 Pure Style) - 鎖定 ax.set_aspect('equal')
    ax.set_aspect('equal')

    # 設定坐標軸範圍，並稍微超出範圍以確保邊界可見
    ax.set_xlim(x_range[0] - 1, x_range[1] + 1)
    ax.set_ylim(y_range[0] - 1, y_range[1] + 1)

    # 繪製網格
    ax.grid(True, linestyle='--', alpha=0.6)

    # 繪製坐標軸
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # 箭頭 (使用 transform 確保箭頭在坐標軸末端)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    # 坐標軸標籤
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12, rotation=0)

    # 【座標軸刻度】：必須顯示每 1 單位的「刻度線 (Tick marks)」
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))
    
    # 【標籤規範】：刻度數字僅顯示原點 '0' (18 號加粗)，其餘刻度嚴禁顯示數字標籤。
    ax.set_xticklabels(['' for _ in ax.get_xticks()])
    ax.set_yticklabels(['' for _ in ax.get_yticks()])

    # 在原點標註 '0'
    ax.text(-0.5, -0.7, '0', color='black', fontsize=18, fontweight='bold', ha='center', va='center')

    if not plot_points_only: # B. 標點題防洩漏協定: 僅在非標點題時顯示點
        for x, y, label_text, color in points:
            ax.plot(x, y, 'o', color=color, markersize=8)
            if show_labels and label_text:
                # 【防遮擋】：點標籤 (A, B) 必須設定白色光暈 (bbox)
                ax.text(x, y + 0.5, label_text, color='black', fontsize=12, ha='center', va='bottom',
                        bbox={'facecolor':'white', 'alpha':0.7, 'edgecolor':'none', 'boxstyle':'round,pad=0.2'}) # ULTRA VISUAL STANDARDS: alpha=0.7

    ax.set_title(title)
    
    # 將圖形轉換為 base64 字串
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    # No plt.close(fig) as we are not using pyplot directly for figure creation
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64


# --- Type 1 (Maps to Example 1, 5): Identify Quadrant/Axis from Point ---
def _generate_type1_problem(level):
    """
    生成 Type 1 題目：從給定點判斷象限或坐標軸。
    """
    x_val_data = _generate_coordinate_value(-10, 10, allow_fraction=True)
    y_val_data = _generate_coordinate_value(-10, 10, allow_fraction=True)
    
    x_float, _ = x_val_data
    y_float, _ = y_val_data

    # 確保不會同時為0，除非是原點。且有一定機率落在軸上。
    if x_float != 0.0 and y_float != 0.0 and random.random() < 0.2: # 20% 機率讓點落在軸上 (非原點)
        if random.choice([True, False]): # 落在 x 軸
            y_val_data = (0.0, (0, 0, 0, False))
            y_float = 0.0
        else: # 落在 y 軸
            x_val_data = (0.0, (0, 0, 0, False))
            x_float = 0.0

    x_latex = _format_coordinate_latex(x_val_data)
    y_latex = _format_coordinate_latex(y_val_data)

    # CONTEXT RETENTION: Keep names like 'ACEF', 'BDF', '巴奈' from the RAG examples.
    point_label = random.choice(["A", "B", "C", "D", "E", "F", "M", "N", "P", "Q", "R", "S", "巴奈"])
    
    question_text_template = r"請判斷坐標平面上點 ${L}({x}, {y})$ 位於第幾象限內或哪條坐標軸上？"
    
    question_text = question_text_template.replace("{L}", point_label)
    question_text = question_text.replace("{x}", x_latex)
    question_text = question_text.replace("{y}", y_latex)

    correct_answer = _get_quadrant_info(x_float, y_float)
    
    # 視覺化：顯示點和標籤
    points_to_draw = [(x_float, y_float, point_label, 'blue')]
    image_base64 = _draw_coordinate_plane(points_to_draw, show_labels=True)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 在這裡 answer 和 correct_answer 相同
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# --- Type 2 (Maps to Example 2): Identify Quadrant from Conditions ---
def _generate_type2_problem(level):
    """
    生成 Type 2 題目：從條件判斷象限。
    """
    quadrant_options = {
        "第一象限": (">0", ">0"),
        "第二象限": ("<0", ">0"),
        "第三象限": ("<0", "<0"),
        "第四象限": (">0", "<0")
    }
    
    correct_quadrant = random.choice(list(quadrant_options.keys()))
    x_condition, y_condition = quadrant_options[correct_quadrant]

    # CONTEXT RETENTION: Keep names like 'M', 'N', 'P', 'Q', 'R', 'S' from RAG Ex 2.
    point_label = random.choice(["M", "N", "P", "Q", "R", "S", "A", "巴奈"])

    question_text_template = r"若點 ${L}(x, y)$ 滿足 $x {xc}$ 且 $y {yc}$，則點 ${L}$ 位於第幾象限？"
    question_text = question_text_template.replace("{L}", point_label)
    question_text = question_text.replace("{xc}", x_condition)
    question_text = question_text.replace("{yc}", y_condition)

    correct_answer = correct_quadrant
    
    # 視覺化：此題型無需繪圖
    image_base64 = ""

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# --- Type 3 (Maps to Example 3): Determine Quadrant of Derived Point ---
def _generate_type3_problem(level):
    """
    生成 Type 3 題目：判斷衍生點的象限。
    """
    # 隨機選擇一個初始象限
    initial_quadrant = random.choice(["第一象限", "第二象限", "第三象限", "第四象限"])
    
    # 根據初始象限設定 a, b 的符號
    a_sign = 0
    b_sign = 0
    if initial_quadrant == "第一象限":
        a_sign = 1
        b_sign = 1
    elif initial_quadrant == "第二象限":
        a_sign = -1
        b_sign = 1
    elif initial_quadrant == "第三象限":
        a_sign = -1
        b_sign = -1
    else: # 第四象限
        a_sign = 1
        b_sign = -1

    # 隨機生成 a, b 的值，並應用符號函數
    # 確保 a, b 不為 0，除非題目特意要求 (RAG Ex 3 implies s, t are not 0 for s/t)
    a_val_abs = random.randint(1, 5) # Absolute value
    b_val_abs = random.randint(1, 5) # Absolute value
    
    a_val = float(a_sign * a_val_abs)
    b_val = float(b_sign * b_val_abs)

    # RAG Ex 3: A ( s , t ) -> B ( t ,｜s｜)、C (-s , s/t )
    # RAG Ex 4: P ( a , b ) -> Q (-a ,｜b｜)、R (-b², ab )
    
    # 【Coordinate Logic Hardening】: 先給變數代入真實隨機數值，進行物理運算判定象限後，再生成題目文字。
    derived_point_expressions = [
        # Based on RAG Ex 3: B ( t ,｜s｜)
        (r"$(t, |s|)$", lambda s, t: (t, abs(s)), "B", "A(s,t)", "s", "t"), 
        # Based on RAG Ex 3: C (-s , s/t )
        (r"$(-s, s/t)$", lambda s, t: (-s, s/s if t == 0 else s/t), "C", "A(s,t)", "s", "t"), # Handle t=0 case for s/t
        # Based on RAG Ex 4: Q (-a ,｜b｜)
        (r"$(-a, |b|)$", lambda a, b: (-a, abs(b)), "Q", "P(a,b)", "a", "b"),
        # Based on RAG Ex 4: R (-b^2, ab )
        (r"$(-b^2, ab)$", lambda a, b: (-b**2, a*b), "R", "P(a,b)", "a", "b"),
        # Additional common variations
        (r"$(a^2, -b)$", lambda a, b: (a**2, -b), random.choice(["D", "E", "F"]), "P(a,b)", "a", "b"),
        (r"$(-a, -b)$", lambda a, b: (-a, -b), random.choice(["D", "E", "F"]), "P(a,b)", "a", "b"),
        (r"$(b, a)$", lambda a, b: (b, a), random.choice(["D", "E", "F"]), "P(a,b)", "a", "b")
    ]
    
    expr_latex, expr_func, derived_label, initial_point_template, initial_x_var, initial_y_var = random.choice(derived_point_expressions)

    # Calculate derived point's actual coordinates using the generated values
    # Pass a_val, b_val correctly based on the variable names used in expr_func
    if initial_x_var == "a":
        derived_x, derived_y = expr_func(a_val, b_val)
    else: # initial_x_var == "s"
        derived_x, derived_y = expr_func(a_val, b_val) # Assuming s=a_val, t=b_val
    
    # Handle float precision for zero, crucial for _get_quadrant_info
    epsilon = 1e-9
    if abs(derived_x) < epsilon: derived_x = 0.0
    if abs(derived_y) < epsilon: derived_y = 0.0

    # CONTEXT RETENTION: Keep names like 'A', 'P' from RAG examples.
    question_text_template = r"已知 {initial_point_template} 位於 {initial_quadrant}，則點 ${derived_label}{expr_latex}$ 位於第幾象限內或哪條坐標軸上？"
    question_text = question_text_template.replace("{initial_point_template}", initial_point_template)
    question_text = question_text.replace("{initial_quadrant}", initial_quadrant)
    question_text = question_text.replace("{derived_label}", derived_label)
    question_text = question_text.replace("{expr_latex}", expr_latex)

    correct_answer = _get_quadrant_info(derived_x, derived_y)

    # 視覺化：此題型無需繪圖
    image_base64 = ""

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# --- Type 4 (Maps to Example 4): Plot Points on Coordinate Plane ---
def _generate_type4_problem(level):
    """
    生成 Type 4 題目：在坐標平面上標出點。
    """
    num_points = random.randint(2, 4) # 隨機生成 2 到 4 個點
    points_info = []
    question_points_latex = []
    
    # 調整繪圖範圍以確保點在可視區域內
    plot_x_range = (-8, 8)
    plot_y_range = (-8, 8)

    for i in range(num_points):
        # 標點題通常使用整數坐標以便學生繪製
        x_val_data = _generate_coordinate_value(plot_x_range[0], plot_x_range[1], allow_fraction=False)
        y_val_data = _generate_coordinate_value(plot_y_range[0], plot_y_range[1], allow_fraction=False)
        
        # CONTEXT RETENTION: Keep names like 'A', 'B', 'C' from RAG examples.
        point_label = chr(ord('A') + i) 
        
        x_latex = _format_coordinate_latex(x_val_data)
        y_latex = _format_coordinate_latex(y_val_data)
        
        points_info.append({
            "label": point_label,
            "x": x_val_data[0],
            "y": y_val_data[0]
        })
        
        question_points_latex.append(r"${L}({x}, {y})$".replace("{L}", point_label).replace("{x}", x_latex).replace("{y}", y_latex))

    points_list_str = "、".join(question_points_latex)
    question_text_template = r"請在坐標平面上標出點 {points_list_str}。"
    question_text = question_text_template.replace("{points_list_str}", points_list_str)

    # correct_answer 應為一個 JSON 字串表示的點列表，以便未來擴展 check 函式
    import json
    correct_answer = json.dumps([{"label": p["label"], "x": p["x"], "y": p["y"]} for p in points_info], ensure_ascii=False)
    
    # B. 標點題防洩漏協定: _draw_coordinate_plane 的 points 參數必須傳入空列表 []
    image_base64 = _draw_coordinate_plane([], x_range=plot_x_range, y_range=plot_y_range, show_labels=False, plot_points_only=True)

    # answer 欄位，對於標點題，與 correct_answer 相同
    answer = correct_answer

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
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
