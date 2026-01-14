# ==============================================================================
# ID: jh_數學1上_GeometryProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 109.30s | RAG: 2 examples
# Created At: 2026-01-14 23:37:28
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


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

# --- 1. Formatting Helpers (V10.6 No-F-String LaTeX) ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX using .replace() to avoid f-string conflicts.
    """
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
    """
    Format number for LaTeX (Safe Mode).
    """
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

# Alias
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def is_prime(n):
    """Check primality (Standard Boolean Return)."""
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
# --- 3. Fraction Generator ---
def simplify_fraction(n, d):
    """[V11.3 Standard Helper] 強力化簡分數並回傳 (分子, 分母)"""
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    """[V11.4 Standard Helper] 計算一維距離"""
    return abs(a - b)

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    
    # [Physical Standard] 直角鎖死，防止變形
    ax.set_aspect('equal', adjustable='datalim')

    # 1. 繪製多邊形
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
            
    # 2. 標註頂點 (Label Halo & High Density)
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        # [Label Halo] 白色遮罩確保清晰度
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))

    # [Dynamic Buffer] 動態邊界補償 (容納 大字體)
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
    # [High Density] 300 DPI Hardened
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

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
    
def draw_number_line(points_map, x_min=None, x_max=None, **kwargs):
    """
    [V11.6 Self-Healing] 數線引擎：參數兼容與高解析度
    """
    highlight_segment = kwargs.get('highlight_segment')
    # 1. 數據正規化
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    
    if not values: values = [0]
    
    # 2. 自動計算範圍 (如果未提供)
    if x_min is None: x_min = math.floor(min(values)) - 1
    if x_max is None: x_max = math.ceil(max(values)) + 1
    
    # 3. 建立 Figure (Thread-Safe)
    fig = Figure(figsize=(8, 1.5))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)

    # 4. 繪製數線主體
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5) 
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False) # 右箭頭
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False) # 左箭頭

    # 5. 設定刻度：只顯示 0，並且字體加大 (V10.2 Style)
    ticks = [0] if x_min <= 0 <= x_max else []
    ax.set_xticks(ticks)
    ax.set_xticklabels(['0'] if ticks else [], fontsize=18, fontweight='bold') 
    
    # 6. 移除其他干擾
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # 7. 繪製點與標籤
    for label, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        ax.plot(val, 0, 'ro', markersize=7)
        # 點標籤設為 16 號
        ax.text(val, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    # 8. 繪製線段 (Highlight Segment)
    if highlight_segment:
        try:
            p1_label, p2_label = highlight_segment
            if p1_label in points_map and p2_label in points_map:
                v1 = float(points_map[p1_label])
                v2 = float(points_map[p2_label])
                ax.plot([v1, v2], [0, 0], 'r-', linewidth=3, alpha=0.5)
        except:
            pass

    # 9. 輸出 Base64 [V11.6 High Density]
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V10.6 Hardcoded Golden Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    # [V11.0] 暴力清理 LaTeX 冗餘符號 ($, \) 與空格
    u = str(user_answer).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "")
    
    # 強制還原字典格式 (針對商餘題)
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try: import ast; c_raw = ast.literal_eval(c_raw)
        except: pass

    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q, r = str(c_raw.get("quotient", "")), str(c_raw.get("remainder", ""))
        ans_display = r"{q},{r}".replace("{q}", q).replace("{r}", r)
        try:
            u_parts = u.replace("商", "").replace("餘", ",").split(",")
            if int(u_parts[0]) == int(q) and int(u_parts[1]) == int(r):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(c_raw).strip()

    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        import math
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    # [V11.1] 科學記號自動比對 (1.23*10^4 vs 1.23e4)
    # 支援 *10^, x10^, e 格式
    if "*" in str(ans_display) or "^" in str(ans_display) or "e" in str(ans_display):
        try:
            # 正規化：將常見乘號與次方符號轉為 E-notation
            norm_ans = str(ans_display).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            norm_user = str(u).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            if math.isclose(float(norm_ans), float(norm_user), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
        except: pass

    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}


import base64
from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

### 2. 輔助函式 (Helper Functions)

# 2.1 視覺化輔助函式 (Visualization Helpers)

def _draw_rectangle_base64(width, height, A_coords, C_coords, E_coords, F_coords, label="ACEF"):
    """
    繪製一個帶有尺寸和頂點標籤的長方形，並返回 Base64 編碼的 PNG 圖片字串。
    A_coords, C_coords, E_coords, F_coords 為 (x, y) 座標元組，代表長方形的 A, C, E, F 頂點。
    [防洩漏原則]: 僅接收已知數據 (寬度、高度、座標)。
    [必須回傳]: 返回 Base64 字串。
    [類型一致]: 返回值為字串。
    """
    padding = 40
    
    # Collect all provided coordinates for scaling and centering
    all_x = [A_coords[0], C_coords[0], E_coords[0], F_coords[0]]
    all_y = [A_coords[1], C_coords[1], E_coords[1], F_coords[1]]
    
    min_x_math, max_x_math = min(all_x), max(all_x)
    min_y_math, max_y_math = min(all_y), max(all_y)

    # Determine required image size based on mathematical extent and padding
    # Ensure a minimum size for very small rectangles
    img_width_base = max((max_x_math - min_x_math) * 20, 100)
    img_height_base = max((max_y_math - min_y_math) * 20, 100)
    
    img_width = img_width_base + 2 * padding
    img_height = img_height_base + 2 * padding
    
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    # Calculate transformation to center and scale the math coordinates to image coordinates
    center_x_math = (min_x_math + max_x_math) / 2
    center_y_math = (min_y_math + max_y_math) / 2

    actual_drawable_width = img_width - 2 * padding
    actual_drawable_height = img_height - 2 * padding

    scale_x = actual_drawable_width / (max_x_math - min_x_math + 1e-6) if (max_x_math - min_x_math) > 0 else 1
    scale_y = actual_drawable_height / (max_y_math - min_y_math + 1e-6) if (max_y_math - min_y_math) > 0 else 1
    scale = min(scale_x, scale_y)
    
    # If the math range is zero (e.g., all points on a line), use a default scale.
    if max_x_math - min_x_math == 0 and max_y_math - min_y_math == 0:
        scale = 20 # Default scale
        center_x_math = A_coords[0] # Just pick one point as center
        center_y_math = A_coords[1]
    elif max_x_math - min_x_math == 0: # Only vertical extent
        scale = scale_y
        center_x_math = A_coords[0]
    elif max_y_math - min_y_math == 0: # Only horizontal extent
        scale = scale_x
        center_y_math = A_coords[1]

    center_x_img = img_width / 2
    center_y_img = img_height / 2

    def to_img_coords_final(math_x, math_y):
        img_x = center_x_img + (math_x - center_x_math) * scale
        img_y = center_y_img - (math_y - center_y_math) * scale # Y-axis inverted for PIL
        return img_x, img_y

    # Convert rectangle vertices to image coordinates
    img_A = to_img_coords_final(A_coords[0], A_coords[1])
    img_C = to_img_coords_final(C_coords[0], C_coords[1])
    img_E = to_img_coords_final(E_coords[0], E_coords[1])
    img_F = to_img_coords_final(F_coords[0], F_coords[1])

    # 繪製長方形邊線 (A-C-E-F-A)
    draw.line([img_A, img_C], fill='black', width=2)
    draw.line([img_C, img_E], fill='black', width=2)
    draw.line([img_E, img_F], fill='black', width=2)
    draw.line([img_F, img_A], fill='black', width=2)

    # 繪製頂點標籤
    draw.text((img_A[0] - 10, img_A[1] - 20), label[0], fill='black', font=font) # A
    draw.text((img_C[0] + 5, img_C[1] - 20), label[1], fill='black', font=font) # C
    draw.text((img_E[0] + 5, img_E[1] + 5), label[2], fill='black', font=font) # E
    draw.text((img_F[0] - 10, img_F[1] + 5), label[3], fill='black', font=font) # F

    # 繪製邊長標籤 (width for A-C or F-E, height for C-E or A-F)
    mid_AC_x, mid_AC_y = (img_A[0] + img_C[0]) / 2, (img_A[1] + img_C[1]) / 2
    mid_CE_x, mid_CE_y = (img_C[0] + img_E[0]) / 2, (img_C[1] + img_E[1]) / 2
    
    draw.text((mid_AC_x, mid_AC_y - 15), str(width), fill='blue', font=font)  # Label for width (top side)
    draw.text((mid_CE_x + 5, mid_CE_y), str(height), fill='blue', font=font) # Label for height (right side)

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def _draw_parallel_lines_angles_base64(angle_val_str, angle_type_label_str):
    """
    繪製兩條平行線被一條截線相交的圖形，並標記角度。
    [防洩漏原則]: 僅接收已知數據 (角度值字串、未知角度標籤字串)。
    [必須回傳]: 返回 Base64 字串。
    [類型一致]: 返回值為字串。
    NOTE: This helper is defined in the spec but is NOT used in the final implementation due to
          MANDATORY MIRRORING RULES overriding ARCHITECT'S SPEC for Type 2.
    """
    img_width, img_height = 400, 300
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()

    # 繪製平行線
    line1_y = img_height // 3
    line2_y = 2 * img_height // 3
    draw.line([(0, line1_y), (img_width, line1_y)], fill='black', width=2)
    draw.line([(0, line2_y), (img_width, line2_y)], fill='black', width=2)

    # 繪製截線
    x1_trans = img_width // 2 - 70
    x2_trans = img_width // 2 + 70
    
    slope = (line2_y - line1_y) / (x2_trans - x1_trans)
    
    trans_start_y = line1_y - slope * x1_trans
    trans_end_y = line2_y + slope * (img_width - x2_trans)
    
    draw.line([(0, trans_start_y), (img_width, trans_end_y)], fill='black', width=2)

    # 標記角度
    draw.text((x1_trans - 50, line1_y - 40), angle_val_str, fill='red', font=font)
    draw.text((x2_trans + 10, line2_y + 10), angle_type_label_str, fill='blue', font=font)

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def _draw_triangle_base64(len_AB, len_BC, hypotenuse_label_str, A_coords, B_coords, C_coords, label="ABC"):
    """
    繪製一個直角三角形，標記兩條直角邊和斜邊。
    [防洩漏原則]: 僅接收已知數據 (邊長、座標、斜邊標籤)。
    [必須回傳]: 返回 Base64 字串。
    [類型一致]: 返回值為字串。
    """
    padding = 40
    
    all_x = [A_coords[0], B_coords[0], C_coords[0]]
    all_y = [A_coords[1], B_coords[1], C_coords[1]]
    
    min_x_math, max_x_math = min(all_x), max(all_x)
    min_y_math, max_y_math = min(all_y), max(all_y)

    scale_factor = 20 

    img_width_base = max((max_x_math - min_x_math) * scale_factor, 100)
    img_height_base = max((max_y_math - min_y_math) * scale_factor, 100)
    
    img_width = img_width_base + 2 * padding
    img_height = img_height_base + 2 * padding

    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    center_x_math = (min_x_math + max_x_math) / 2
    center_y_math = (min_y_math + max_y_math) / 2

    actual_drawable_width = img_width - 2 * padding
    actual_drawable_height = img_height - 2 * padding
    
    scale_x = actual_drawable_width / (max_x_math - min_x_math + 1e-6) if (max_x_math - min_x_math) > 0 else 1
    scale_y = actual_drawable_height / (max_y_math - min_y_math + 1e-6) if (max_y_math - min_y_math) > 0 else 1
    scale = min(scale_x, scale_y)
    
    if max_x_math - min_x_math == 0 and max_y_math - min_y_math == 0:
        scale = 20
        center_x_math = A_coords[0]
        center_y_math = A_coords[1]
    elif max_x_math - min_x_math == 0:
        scale = scale_y
        center_x_math = A_coords[0]
    elif max_y_math - min_y_math == 0:
        scale = scale_x
        center_y_math = A_coords[1]

    center_x_img = img_width / 2
    center_y_img = img_height / 2

    def to_img_coords(math_x, math_y):
        img_x = center_x_img + (math_x - center_x_math) * scale
        img_y = center_y_img - (math_y - center_y_math) * scale
        return img_x, img_y

    img_A = to_img_coords(A_coords[0], A_coords[1])
    img_B = to_img_coords(B_coords[0], B_coords[1])
    img_C = to_img_coords(C_coords[0], C_coords[1])

    # 繪製三角形邊線
    draw.line([img_A, img_B], fill='black', width=2)
    draw.line([img_B, img_C], fill='black', width=2)
    draw.line([img_C, img_A], fill='black', width=2)

    # 繪製頂點標籤
    draw.text((img_A[0] - 10, img_A[1] - 20), label[0], fill='black', font=font)
    draw.text((img_B[0] + 5, img_B[1] - 20), label[1], fill='black', font=font)
    draw.text((img_C[0] + 5, img_C[1] + 5), label[2], fill='black', font=font)

    # 繪製邊長標籤
    mid_AB_x, mid_AB_y = (img_A[0] + img_B[0]) / 2, (img_A[1] + img_B[1]) / 2
    mid_BC_x, mid_BC_y = (img_B[0] + img_C[0]) / 2, (img_B[1] + img_C[1]) / 2
    mid_AC_x, mid_AC_y = (img_A[0] + img_C[0]) / 2, (img_A[1] + img_C[1]) / 2

    # Assuming AB is vertical leg (len_AB), BC is horizontal leg (len_BC), AC is hypotenuse
    draw.text((mid_AB_x, mid_AB_y - 15), str(len_AB), fill='blue', font=font)
    draw.text((mid_BC_x + 5, mid_BC_y), str(len_BC), fill='blue', font=font)
    draw.text((mid_AC_x - 10, mid_AC_y - 10), hypotenuse_label_str, fill='green', font=font) # 標記斜邊

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# 2.2 數學運算輔助函式 (Mathematical Helpers)

def _calculate_area_rectangle(width, height):
    """
    計算長方形面積。
    [必須回傳]: 返回數值。
    """
    return width * height

def _calculate_perimeter_rectangle(width, height):
    """
    計算長方形周長。
    [必須回傳]: 返回數值。
    """
    return 2 * (width + height)

def _calculate_hypotenuse(side1, side2):
    """
    計算直角三角形的斜邊長度 (使用畢氏定理)。
    [必須回傳]: 返回數值。
    """
    return math.sqrt(side1**2 + side2**2)

def _calculate_area_triangle_coords(x1, y1, x2, y2, x3, y3):
    """
    計算由三個點座標定義的三角形面積 (使用 Shoelace formula)。
    [必須回傳]: 返回數值。
    """
    return 0.5 * abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))

def _calculate_area_trapezoid(upper_base, lower_base, height):
    """
    計算梯形面積。
    [必須回傳]: 返回數值。
    """
    return 0.5 * (upper_base + lower_base) * height

### 3. 頂層函式 (Top-Level Functions)

def generate(level=1):
    """
    生成 K12 幾何問題。
    [頂層函式]: 定義於模組最外層。
    [自動重載]: 不依賴全域狀態。
    [隨機分流]: 使用 random.choice 選擇問題類型。
    [數據禁絕常數]: 所有幾何長度、角度、面積均隨機生成，答案透過公式計算。
    [欄位鎖死]: 返回字典包含指定欄位。
    [時間戳記]: 包含 created_at 和 version。
    """
    problem_type = random.choice([
        "Type 1",  # Maps to RAG Ex 1: Rectangle ACEF with triangle BDF area
        "Type 2",  # Maps to RAG Ex 2: Trapezoid with algebraic relation
        "Type 3"   # Maps to Architect's Spec Type 3: Pythagorean Theorem
    ])

    question_text = ""
    correct_answer = None
    answer_display = ""
    image_base64 = None

    if problem_type == "Type 1":
        # Type 1 (Maps to RAG Ex 1): Rectangle ACEF with triangle BDF area
        # Mathematical Model based on RAG Ex 1 reverse-engineering:
        # Rectangle ACEF: A=(0,H), C=(W,H), E=(W,0), F=(0,0)
        # B is on AC (top side), D is on CE (right side)
        # Given: AF_H (height), AB_offset (length of segment AB), CD_len, DE_len
        # Problem asks for BC_len.
        
        # 1. Generate random dimensions and offsets, then calculate area and the target answer.
        AF_H = random.randint(8, 15)  # Height of rectangle (AF or CE)
        
        # AB_offset: distance from A along AC. Let A=(0, AF_H), C=(W, AF_H). B=(AB_offset, AF_H)
        AB_offset = random.randint(2, 7) 
        
        # DE_len: distance from D along DE. Let E=(W, 0), C=(W, AF_H). D=(W, DE_len)
        DE_len = random.randint(2, AF_H - 2)
        CD_len = AF_H - DE_len # Length of segment CD
        
        # Determine the desired answer (BC_len) first, then calculate W.
        BC_result = random.randint(2, 6) # The answer for BC segment length
        
        # W (width of rectangle AC or FE) = AB_offset + BC_result
        W = AB_offset + BC_result
        
        # Coordinates for rectangle ACEF:
        A_rect_coords = (0, AF_H)
        C_rect_coords = (W, AF_H)
        E_rect_coords = (W, 0)
        F_rect_coords = (0, 0)

        # Coordinates for triangle BDF:
        B_tri_coords = (AB_offset, AF_H)
        D_tri_coords = (W, DE_len)
        F_tri_coords = (0, 0) # F is also a vertex of the rectangle

        # Calculate the area of triangle BDF using Shoelace formula
        triangle_area = _calculate_area_triangle_coords(
            B_tri_coords[0], B_tri_coords[1],
            D_tri_coords[0], D_tri_coords[1],
            F_tri_coords[0], F_tri_coords[1]
        )
        triangle_area = round(triangle_area) # Ensure integer area for K12 problems
        
        if triangle_area <= 0: # Should not happen with current construction, but a safeguard
            return generate(level)

        image_base64 = _draw_rectangle_base64(W, AF_H, A_rect_coords, C_rect_coords, E_rect_coords, F_rect_coords, label="ACEF")

        q_template = (
            r"如右圖，四邊形 $ACEF$ 為長方形，已知三角形 $BDF$ 的面積為 ${area_val}$ 平方公分。"
            r"圖中 $AF={AF_H}$ 公分，$AB={AB_offset}$ 公分，$CD={CD_len}$ 公分，$DE={DE_len}$ 公分。"
            r"則 $BC$ 線段的長度為多少公分？"
        )
        question_text = q_template.replace("{area_val}", str(triangle_area))\
                                  .replace("{AF_H}", str(AF_H))\
                                  .replace("{AB_offset}", str(AB_offset))\
                                  .replace("{CD_len}", str(CD_len))\
                                  .replace("{DE_len}", str(DE_len))
        
        correct_answer = BC_result
        answer_display = r"${ans}$ 公分".replace("{ans}", str(BC_result))

    elif problem_type == "Type 2":
        # Type 2 (Maps to RAG Ex 2): Trapezoid with algebraic relation
        # Let upper base = x
        # Lower base = 3x - 4
        # Height = h
        # Area = 0.5 * (upper_base + lower_base) * h = 0.5 * (x + 3x - 4) * h = (2x - 2) * h

        # Generate upper_base (x) and height (h)
        upper_base_val = random.randint(5, 10) # Ensure x is large enough for lower base to be positive
        height_val = random.randint(5, 10)
        
        lower_base_val = 3 * upper_base_val - 4
        
        # Regenerate if lower base is not positive
        if lower_base_val <= 0:
            return generate(level)

        area_val = _calculate_area_trapezoid(upper_base_val, lower_base_val, height_val)
        
        # No specific drawing helper for trapezoid is provided in the ARCHITECT'S SPEC,
        # and creating new models (like a trapezoid drawing helper) is forbidden by MANDATORY MIRRORING RULES.
        # Therefore, image_base64 is set to None.
        image_base64 = None 

        q_template = (
            r"已知梯形下底比上底的 3 倍少 4 公分。若此梯形的高為 ${height}$ 公分，"
            r"面積為 ${area}$ 平方公分，則此梯形的上底為多少公分？"
        )
        question_text = q_template.replace("{height}", str(height_val))\
                                  .replace("{area}", str(area_val))
        
        correct_answer = upper_base_val
        answer_display = r"${ans}$ 公分".replace("{ans}", str(upper_base_val))

    elif problem_type == "Type 3":
        # Type 3 (Maps to Architect's Spec Type 3): Pythagorean Theorem
        # [數據禁絕常數]: 隨機生成直角三角形的兩條直角邊長。
        side1 = random.randint(6, 12)  # 直角邊 1 (e.g., BC length)
        side2 = random.randint(8, 15)  # 直角邊 2 (e.g., AB length)
        
        # [公式計算]: 根據隨機數據計算斜邊長度。
        diagonal = _calculate_hypotenuse(side1, side2)
        
        # [座標鎖死]: 定義直角三角形頂點座標。假設直角在 (0,0)。
        # A 點在 (0, side2)，B 點在 (0,0)，C 點在 (side1, 0)。
        A_coords = (0, side2) # Corresponds to AB leg length of side2
        B_coords = (0, 0)
        C_coords = (side1, 0) # Corresponds to BC leg length of side1

        # [排版與 LaTeX 安全]: 準備用於繪圖的字串。
        hypotenuse_label = r"$x$" # 在圖上標記斜邊為 x
        # Pass side2 (AB length) and side1 (BC length) to the drawing helper
        image_base64 = _draw_triangle_base64(side2, side1, hypotenuse_label, A_coords, B_coords, C_coords, label="ABC")
        
        # [排版與 LaTeX 安全]: 嚴禁 f-string，使用 .replace() 替換 LaTeX 變數。
        q_template = r"如圖所示，直角三角形 $ABC$ 中，$\angle B = 90^\circ$。若 $AB = ${s1}$ 公分， $BC = ${s2}$ 公分，試求斜邊 $AC$ 的長度。"
        question_text = q_template.replace("{s1}", str(side2)).replace("{s2}", str(side1)) # AB is side2, BC is side1
        
        correct_answer = round(diagonal, 2) # 將答案四捨五入到小數點後兩位，以符合 K12 實際應用
        ans_val_str = str(correct_answer)
        ans_display_template = r"斜邊 $AC$ 的長度為 ${diag}$ 公分。"
        answer_display = ans_display_template.replace("{diag}", ans_val_str)

    # [欄位鎖死]: 返回字典必須且僅能包含指定欄位。
    # [時間戳記]: 更新 created_at 並遞增 version。
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.1" 
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
