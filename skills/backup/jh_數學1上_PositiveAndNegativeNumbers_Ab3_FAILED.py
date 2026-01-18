
import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# [INJECTED UTILS]

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

# --- [V15.5 新增：全能解析工具] ---
def parse_num(s):
    """解析字串(整數, 小數, 分數, 帶分數)為 float，供 check() 比對"""
    s = str(s).strip().replace(" ", "").replace("＋", "+").replace("－", "-")
    if not s: return None
    try:
        if "/" in s:
            # 處理帶分數 (例如 -4 2/3 -> 需處理為 -(4 + 2/3))
            is_neg = s.startswith("-")
            s = s.lstrip("-")
            # 尋找是否存在空格（帶分數格式）
            match = re.match(r"(\d+)?(?:(\d+)/(\d+))", s)
            if match:
                whole = float(match.group(1)) if match.group(1) else 0.0
                num = float(match.group(2))
                den = float(match.group(3))
                val = whole + (num / den)
                return -val if is_neg else val
        return float(s)
    except: return None

# --- [V15.5 新增：標準出題工具] ---
def generate_val(v_range=(-15, 15), exclude=[0], type_choice=['int', 'float', 'frac']):
    """標準化隨機數生成，支援多種格式"""
    t = random.choice(type_choice)
    for _ in range(100):
        if t == 'int': val = random.randint(v_range[0], v_range[1])
        elif t == 'float': val = round(random.uniform(v_range[0], v_range[1]), 1)
        else: # frac
            d = random.randint(2, 10)
            n = random.randint(v_range[0]*d, v_range[1]*d)
            val = Fraction(n, d)
        if val not in exclude: return val
    return random.randint(1, 5)

def check_standard(u, c):
    """科研級標準比對：支援字串、數字與 LaTeX 符號"""
    if u is None or c is None: return False
    u_p, c_p = parse_num(u), parse_num(c)
    
    # 數值比對 (處理 0.5 vs 1/2)
    if u_p is not None and c_p is not None:
        return math.isclose(u_p, c_p, abs_tol=1e-7)
    
    # 字串比對 (移除空格與常見干擾)
    u_s = str(u).strip().replace(" ", "").replace("。", "")
    c_s = str(c).strip().replace(" ", "").replace("。", "")
    return u_s == c_s
    return u_s == c_s

# [END UTILS]

def generate(mode=1, **kwargs):
    """
    [V16 Skeleton] Logic Filling Mode
    """
    q, a = "", ""
    # [AI LOGIC START]
    SCENARIO_DB = [
        {"主題": "學校位置", "正向描述": "東邊", "負向描述": "西邊", "單位": "公里"},
        {"主題": "考試成績變化", "正向描述": "進步", "負向描述": "退步", "單位": "分"},
        {"主題": "交易盈虧", "正向描述": "賺錢", "負向描述": "賠錢", "單位": "元"},
        {"主題": "數字集合分類", "正向描述": "正數集合", "負向描述": "負數集合", "單位": "數值"}
    ]

    if mode == 1:
        q = f'情境主題: {input["情境主題"]}, 方向: {input["方向"]}, 數值: {input["數值"]}, 單位: {input["單位"]}'
        for s in SCENARIO_DB:
            if s["主題"] == input["情境主題"]:
                if input["方向"] == s["正向描述"]:
                    a = f'+{input["數值"]}'
                else:
                    a = f'-{input["數值"]}'
                break

    if mode == 2:
        q = f'情境主題: {input["情境主題"]}, 數字: {input["數字"]}, 單位: {input["單位"]}'
        sign = input["數字"][0]
        for s in SCENARIO_DB:
            if s["主題"] == input["情境主題"]:
                dir_desc = s["正向描述"] if sign == '+' else s["負向描述"]
                a = f'{dir_desc} {abs(float(input["數字"][1:]))} {s["單位"]}'
                break

    if mode == 3:
        q = f'情境主題: {input["情境主題"]}, 成本: {input["成本"]}, 售價: {input["售價"]}, 單位: {input["單位"]}'
        profit = input["售價"] - input["成本"]
        a = f'{ "+" if profit > 0 else "-"}{abs(profit)}'

    if mode == 4:
        q = f'情境主題: {input["情境主題"]}, 數字: {input["數字"]}, 單位: {input["單位"]}'
        sign = input["數字"][0]
        for s in SCENARIO_DB:
            if s["主題"] == input["情境主題"]:
                result = s["正向描述"] if sign == '+' else s["負向描述"]
                a = f'{result} {abs(float(input["數字"][1:]))} {s["單位"]}'
                break

    if mode == 5:
        q = f'數字清單: {input["數字清單"]}, 篩選條件: {input["篩選條件"]}'
        lst = input["數字清單"]
        cond = input["篩選條件"]
        result = []
        for item in lst:
            num = item
            if isinstance(num, str):
                if ' ' in num:
                    int_part, frac = num.split(' ')
                    frac_num = frac.split('/')
                    num = float(int_part) + float(frac_num[0])/float(frac_num[1])
                else:
                    num = float(num)
            if cond == "負數" and num < 0:
                result.append(num)
            elif cond == "整數" and num.is_integer():
                result.append(num)
            elif cond == "與-2.4同號數" and num < 0:
                result.append(num)
        a = str(result)

    if mode == 6:
        q = f'數字: {input["數字"]}'
        num = input["數字"]
        attrs = []
        if isinstance(num, str):
            if ' ' in num:
                int_part, frac = num.split(' ')
                frac_num = frac.split('/')
                num = float(int_part) + float(frac_num[0])/float(frac_num[1])
            else:
                num = float(num)
        if num > 0:
            attrs.append("正數")
        elif num < 0:
            attrs.append("負數")
        else:
            attrs.append("非正非負")
        if isinstance(num, float) and not num.is_integer():
            attrs.append("非整數")
        else:
            attrs.append("整數")
        a = str({"屬性": attrs})

    # [AI LOGIC END]
    
    # [V16.1 Auto-Handwriting Detection]
    # Check if answer contains LaTeX symbols that require handwriting interface
    c_ans = str(a)
    triggers = ['^', '/', '|', '[', '{', '\\']
    if any(t in c_ans for t in triggers):
         if 'input_mode' not in locals(): locals()['input_mode'] = 'text' # init if missing
         # simpler: just use a new dict key to signal
         pass # Actually, we can't easily modify kwargs inside this tail unless we assume kwargs exists.
         # But the generation skeleton has `def generate(mode=1, **kwargs):`
         if 'input_mode' not in kwargs:
             kwargs['input_mode'] = 'handwriting'
             if "(請在手寫區作答!)" not in q:
                 q = q.rstrip() + "\\n(請在手寫區作答!)"

    # Final Safety Return
    ret = {'question_text': q, 'correct_answer': a, 'mode': mode}
    if 'input_mode' in kwargs: ret['input_mode'] = kwargs['input_mode']
    return ret

def check(user_answer, correct_answer):
    """
    Standard Research Checker
    """
    # 使用 PERFECT_UTILS 中的標準比對函式
    if 'check_standard' in globals():
        res = check_standard(user_answer, correct_answer)
        return {'correct': res, 'result': '正確' if res else '錯誤'}
        
    # Fallback Logic
    u_val = parse_num(user_answer)
    c_val = parse_num(correct_answer)
    if u_val is not None and c_val is not None:
        return {'correct': math.isclose(u_val, c_val, abs_tol=1e-7), 'result': '...'}
    return {'correct': str(user_answer).strip() == str(correct_answer).strip(), 'result': '...'}
