# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: qwen2.5-coder:14b | Strategy: V15 Architect (Hardening)
# Ablation ID: 3 (Full Healing) | Env: RTX 5060 Ti 16GB
# Performance: 73.65s | Tokens: In=0, Out=0
# RAG Context: 8 examples | Temp: 0.05
# Created At: 2026-01-19 13:16:57
# Fix Status: [Repaired] | Fixes: Regex=1, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================

import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# [Injected Utils]

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

# ==============================================================================
# SCENARIO TEMPLATE LIBRARY (Hardcoded for Reliability)
# ==============================================================================
SCENARIO_TEMPLATES = {
    'altitude': {
        'positive': "登山隊從海拔 {n1} 公尺出發，上升 {n2} 公尺。請問海拔變為多少公尺？",
        'negative': "登山隊從海拔 {n1} 公尺出發，下降 {n2} 公尺。請問海拔變為多少公尺？",
    },
    'bank': {
        'positive': "帳戶原有 {n1} 元，存入 {n2} 元。請問餘額變為多少元？",
        'negative': "帳戶原有 {n1} 元，取出 {n2} 元。請問餘額變為多少元？",
    },
    'temperature': {
        'positive': "氣溫原本是 {n1} 度C，上升 {n2} 度C。請問氣溫變為多少度C？",
        'negative': "氣溫原本是 {n1} 度C，下降 {n2} 度C。請問氣溫變為多少度C？",
    },
    'shopping': {
        'cost': "小明買了 {n1} 枝筆，每枝 {n2} 元。請問總共花費多少元？",
    },
    'speed': {
        'distance': "汽車以時速 {n1} 公里行駛 {n2} 小時。請問行駛距離為多少公里？",
    }
}

def apply_scenario(template_key, action, **values):
    """
    自動套用情境模板（避免 Coder 自己發明）
    
    Args:
        template_key: 'altitude', 'bank', 'temperature', etc.
        action: 'positive', 'negative', 'cost', etc.
        **values: n1, n2, n3, ... (要填入的數值)
    
    Returns:
        str: 完整的情境題目
    """
    template = SCENARIO_TEMPLATES.get(template_key, {}).get(action, "")
    if not template:
        return f"計算：{values.get('n1', 0)} + {values.get('n2', 0)}"  # Fallback
    
    # 自動取絕對值（情境題通常不說「上升 -50 公尺」）
    safe_values = {k: abs(v) if isinstance(v, (int, float)) and k != 'n1' else v for k, v in values.items()}
    
    return template.format(**safe_values)

def generate(mode=1, **kwargs):
    q, a = "", ""
    # [AI LOGIC START]
    import random

    # Define SCENARIO_DB as per MASTER SPEC
    SCENARIO_DB = {
        'altitude': [
            {'probability': 0.7, 'template': r"初始海拔是 [初始海拔] 米，上升了 [值1] 米，然后下降了 [值2] 米。最终的海拔是多少？"},
            {'probability': 0.3, 'template': r"小明从 [初始海拔] 米的地方出发，先上升了 [值1] 米，接着又下降了 [值2] 米。请问他现在在多少米的高度？"}
        ],
        'bank': [
            {'probability': 0.7, 'template': r"小红的账户里有 [初始金额] 元，她存入了 [值1] 元，然后取出了 [值2] 元。她的账户里现在还有多少钱？"},
            {'probability': 0.3, 'template': r"小刚的银行账户里原本有 [初始金额] 元，他先存入了 [值1] 元，接着又取出了 [值2] 元。请问他的账户里还剩多少钱？"}
        ],
        'temperature': [
            {'probability': 0.7, 'template': r"今天的气温是 [初始温度] 度，中午上升了 [值1] 度，晚上下降了 [值2] 度。最终的气温是多少度？"},
            {'probability': 0.3, 'template': r"小丽今天早上测量到气温是 [初始温度] 度，中午上升了 [值1] 度，晚上又下降了 [值2] 度。请问晚上的气温是多少度？"}
        ],
        'score': [
            {'probability': 0.7, 'template': r"小明的数学成绩是 [初始分数] 分，他做了额外的练习后提高了 [值1] 分，但考试时又扣了 [值2] 分。他的最终成绩是多少分？"},
            {'probability': 0.3, 'template': r"小红的英语成绩是 [初始分数] 分，她通过复习提高了 [值1] 分，但在考试中又扣了 [值2] 分。请问她的最终成绩是多少分？"}
        ]
    }

    # Define the modes as per MASTER SPEC
    def generate_question(mode):
        if mode == 1:
            n1 = random.randint(-100, 100)
            op1 = random.choice(['+', '-'])
            n2 = random.randint(-100, 100)
            ans_expr_str = f"{n1}{op1}{n2}".replace('+-', '-').replace('--', '+')
            ans = eval(ans_expr_str)
            expr_str = render_expr([n1, n2], ops=[op1])

            if random.random() < 0.7:
                scene = random.choice(['altitude', 'bank', 'temperature', 'score'])
                q_kwargs = {'初始海拔': n1, '值1': eval(f"{n1}{op1}"), '值2': n2}
                q = apply_scenario(scene, None, **q_kwargs)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        elif mode == 2:
            n1 = random.randint(-100, 100)
            op1 = random.choice(['+', '-'])
            n2 = random.randint(-100, 100)
            op2 = random.choice(['+', '-'])
            n3 = random.randint(-100, 100)
            ans_expr_str = f"{n1}{op1}{n2}{op2}{n3}".replace('+-', '-').replace('--', '+')
            ans = eval(ans_expr_str)
            expr_str = render_expr([n1, n2, n3], ops=[op1, op2])

            if random.random() < 0.7:
                scene = random.choice(['altitude', 'bank', 'temperature', 'score'])
                q_kwargs = {'初始海拔': n1, '值1': eval(f"{n1}{op1}"), '值2': eval(f"{n1}{op1}{n2}{op2}")}
                q = apply_scenario(scene, None, **q_kwargs)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        elif mode == 3:
            num_count = random.choice([4, 5])
            terms = []
            n_base = random.randint(-500, 500)
            n_cancel = random.randint(1, 500)
            terms.append(n_base)
            terms.append(n_cancel)
            terms.append(-n_cancel)

            while len(terms) < num_count:
                terms.append(random.randint(-500, 500))

            random.shuffle(terms)

            nums = [terms[0]]
            ops = []
            for i in range(1, len(terms)):
                ops.append(random.choice(['+', '-']))
                nums.append(terms[i])

            ans_expr_str = f"{nums[0]}"
            for i in range(len(ops)):
                ans_expr_str += f"{ops[i]}{nums[i+1]}"
            ans = eval(ans_expr_str)

            expr_str = render_expr(nums, ops=ops)

            if random.random() < 0.7:
                scene = random.choice(['altitude', 'bank', 'temperature', 'score'])
                q_kwargs = {'初始海拔': nums[0]}
                for i in range(len(ops)):
                    q_kwargs[f'值{i+1}'] = eval(f"{nums[i]}{ops[i]}")
                q = apply_scenario(scene, None, **q_kwargs)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        elif mode == 4:
            num_count = random.choice([4, 5])
            terms = []
            n_base = random.randint(-500, 500)
            n_cancel = random.randint(1, 500)
            terms.append(n_base)
            terms.append(n_cancel)
            terms.append(-n_cancel)

            while len(terms) < num_count:
                terms.append(random.randint(-500, 500))

            random.shuffle(terms)

            nums = [terms[0]]
            ops = []
            for i in range(1, len(terms)):
                ops.append(random.choice(['+', '-']))
                nums.append(terms[i])

            ans_expr_str = f"{nums[0]}"
            for i in range(len(ops)):
                ans_expr_str += f"{ops[i]}{nums[i+1]}"
            ans = eval(ans_expr_str)

            expr_str = render_expr(nums, ops=ops)

            if random.random() < 0.7:
                scene = random.choice(['altitude', 'bank', 'temperature', 'score'])
                q_kwargs = {'初始海拔': nums[0]}
                for i in range(len(ops)):
                    q_kwargs[f'值{i+1}'] = eval(f"{nums[i]}{ops[i]}")
                q = apply_scenario(scene, None, **q_kwargs)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        elif mode == 5:
            n1 = random.randint(-100, 100)
            op1 = random.choice(['+', '-'])
            n2 = random.randint(-100, 100)
            op2 = random.choice(['+', '-'])
            n3 = random.randint(-100, 100)

            abs_idx = random.choice([0, 1, 2])

            val_n1 = abs(n1) if abs_idx == 0 else n1
            val_n2 = abs(n2) if abs_idx == 1 else n2
            val_n3 = abs(n3) if abs_idx == 2 else n3

            ans_expr_str = f"{val_n1}{op1}{val_n2}{op2}{val_n3}".replace('+-', '-').replace('--', '+')
            ans = eval(ans_expr_str)

            expr_str = render_expr([n1, n2, n3], ops=[op1, op2], abs_indices=[abs_idx])

            if random.random() < 0.5:
                q = apply_scenario(None, None, abs_val_present=True, n1=n1, n2=n2, n3=n3)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        elif mode == 6:
            choice = random.choice([1, 2])

            if choice == 1: # |N1| op1 |N2| op2 N3
                n1 = random.randint(-200, 200)
                n2 = random.randint(-200, 200)
                n3 = random.randint(-200, 200)
                op1 = random.choice(['+', '-'])
                op2 = random.choice(['+', '-'])

                ans = eval(f"{abs(n1)}{op1}{abs(n2)}{op2}{n3}".replace('+-', '-').replace('--', '+'))
                expr_str = render_expr([n1, n2, n3], ops=[op1, op2], abs_indices=[0, 1])

                q_kwargs = {'n1': n1, 'n2': n2, 'n3': n3}

            elif choice == 2: # N1 op1 |N2| op2 |N3|
                n1 = random.randint(-200, 200)
                n2 = random.randint(-200, 200)
                n3 = random.randint(-200, 200)
                op1 = random.choice(['+', '-'])
                op2 = random.choice(['+', '-'])

                ans = eval(f"{n1}{op1}{abs(n2)}{op2}{abs(n3)}".replace('+-', '-').replace('--', '+'))
                expr_str = render_expr([n1, n2, n3], ops=[op1, op2], abs_indices=[1, 2])

                q_kwargs = {'n1': n1, 'n2': n2, 'n3': n3}

            if random.random() < 0.5:
                q = apply_scenario(None, None, abs_val_present=True, **q_kwargs)
            else:
                q = f"計算：${expr_str}$"

            a = str(ans)

        return q, a

    def render_expr(nums, ops, abs_indices=None):
        expr = ""
        for i in range(len(nums)):
            if i > 0:
                expr += ops[i-1]
            if i in abs_indices:
                expr += f"|{nums[i]}|"
            else:
                expr += str(nums[i])
        return expr

    def apply_scenario(scene, template, **kwargs):
        if scene not in SCENARIO_DB:
            return None

        scenarios = [s for s in SCENARIO_DB[scene] if random.random() < s['probability']]

        if not scenarios:
            return None

        scenario = random.choice(scenarios)
        q = scenario['template']

        for key, value in kwargs.items():
            q = question.replace(f"[{key}]", str(value))

        return question

    # Example usage
    mode = random.randint(1, 6)
    q, a = generate_question(mode)
    print("Question:", q)
    print("Answer:", a)
    # [AI LOGIC END]
    c_ans = str(a)
    if any(t in c_ans for t in ['^', '/', '|', '[', '{', '\\']):
        if 'input_mode' not in kwargs:
            kwargs['input_mode'] = 'handwriting'
            if "(請在手寫區作答!)" not in q: q = q.rstrip() + "\\n(請在手寫區作答!)"
    return {'question_text': q, 'correct_answer': a, 'mode': mode, 'input_mode': kwargs.get('input_mode', 'text')}

def check(user_answer, correct_answer):
    u_s = str(user_answer).strip().replace(" ", "").replace("$", "")
    c_s = str(correct_answer).strip().replace(" ", "").replace("$", "")
    return {'correct': u_s == c_s, 'result': '正確！' if u_s == c_s else '錯誤'}
