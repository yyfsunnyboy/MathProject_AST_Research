# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: gemini-2.5-flash | Strategy: V40.0 Full-Function-Replace
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 10.98s | Tokens: In=5003, Out=1842
# Created At: 2026-01-21 18:05:22
# Fix Status: [Repaired] | Fixes: Regex=12, AST=1
# Verification: Internal Logic Check = PASSED
# ==============================================================================
import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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
plt.rcParams['font.sans-serif"] = ["Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int):
        return str(num)
    if isinstance(num, float):
        num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0:
            return '0'
        if num.denominator == 1:
            return str(num.numerator)
        sign = '-' if num < 0 else ''
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0:
                return '{s}{w}'.replace('{s}', sign).replace('{w}', str(whole))
            return '{s}{w} \\frac{{n}}{{d}}'.replace('{s}', sign).replace('{w}', str(whole)).replace('{n}', str(rem_num)).replace('{d}', str(abs_num.denominator))
        return '\\frac{{n}}{{d}}'.replace('{n}', str(num.numerator)).replace('{d}', str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and (not signed) and (not op):
        return '0'
    is_neg = num < 0
    abs_str = to_latex(abs(num))
    if op:
        if is_neg:
            return ' - {v}'.replace('{v}', abs_str)
        return ' + {v}'.replace('{v}', abs_str)
    if signed:
        if is_neg:
            return '-{v}'.replace('{v}', abs_str)
        return '+{v}'.replace('{v}', abs_str)
    if is_neg:
        return '({v})'.replace('{v}', latex_val)
    return latex_val

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
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

def gcd(a, b):
    return math.gcd(int(a), int(b))

def lcm(a, b):
    return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return (n // common, d // common)

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0:
            continue
        val = Fraction(num, den)
        if simple and val.denominator == 1:
            continue
        if val == 0:
            continue
        return val
    return Fraction(1, 2)

def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals:
            values.append(float(inter['start']))
    if x_min is None:
        x_min = math.floor(min(values)) - 2
    if x_max is None:
        x_max = math.ceil(max(values)) + 2
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)
    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')
    ax.set_yticks([])
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    if lines:
        import numpy as np
        for line in lines:
            m, k = (line.get('m', 0), line.get('k', 0))
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0] + 0.2, p[1] + 0.2, p.get('label', ''), fontsize=14, fontweight='bold')
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xticks([0])
    ax.set_yticks([0])
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0, 10), y_limit=(0, 10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = ([], [])
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = (min(all_x), max(all_x))
        min_y, max_y = (min(all_y), max(all_y))
        rx = (max_x - min_x) * 0.3 if max_x - min_x > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if max_y - min_y > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def check(user_answer, correct_answer):
    if user_answer is None:
        return {'correct': False, 'result': '未提供答案。'}

    def _format_ans(a):
        if isinstance(a, dict):
            if 'quotient' in a:
                return '{q}, {r}'.replace('{q}', str(a.get('quotient', ''))).replace('{r}', str(a.get('remainder', '')))
            return ', '.join(['{k}={v}'.replace('{k}', str(k)).replace('{v}', str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        return str(s).strip().replace(' ', '').replace(', ', ',').replace('$', '').replace('\\', '').lower()
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    if u == c:
        return {'correct': True, 'result': '正確！'}
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-06):
            return {'correct': True, 'result': '正確！'}
    except:
        pass
    return {'correct': False, 'result': '答案錯誤。正確答案為: {ans}'.replace('{ans}', c_raw)}
    return template.format(**safe_values)

def generate(level=1, **kwargs):
    q = ''
    a = ''
    problem_type = random.randint(1, 4)
    if problem_type == 1:
        A = random.randint(1, 10) * random.choice([-1, 1])
        B = random.randint(2, 12)
        product_AB = A * B
        divisors_of_product_AB = []
        for i in range(1, abs(product_AB) + 1):
            if product_AB % i == 0:
                divisors_of_product_AB.append(i)
                divisors_of_product_AB.append(-i)
        C = random.choice(divisors_of_product_AB)
        result = product_AB // C
        q = f"計算下列各式的值。{fmt_num(A)} × {fmt_num(B)} ÷ {fmt_num(C)}"
        a = f"{fmt_num(A)} × {fmt_num(B)} ÷ {fmt_num(C)} = {fmt_num(product_AB)} ÷ {fmt_num(C)} = {fmt_num(result)}"
    elif problem_type == 2:
        B = random.randint(1, 10) * random.choice([-1, 1])
        multiplier = random.randint(1, 10) * random.choice([-1, 1])
        A = B * multiplier
        C = random.randint(-10, 10)
        first_div_result = A // B
        result = first_div_result * C
        q = f"計算下列各式的值。{fmt_num(A)} ÷ {fmt_num(B)} × {fmt_num(C)}"
        a = f"{fmt_num(A)} ÷ {fmt_num(B)} × {fmt_num(C)} = {fmt_num(first_div_result)} × {fmt_num(C)} = {fmt_num(result)}"
    elif problem_type == 3:
        A = random.randint(-20, 20)
        B = random.randint(-10, 10)
        C = random.randint(-10, 10)
        product_BC = B * C
        result = A + product_BC
        q = f"計算下列各式的值。{fmt_num(A)} ＋ {fmt_num(B)} × {fmt_num(C)}"
        a = f"{fmt_num(A)} ＋ {fmt_num(B)} × {fmt_num(C)} = {fmt_num(A)} ＋ {fmt_num(product_BC)} = {fmt_num(result)}"
    else:
        A = random.randint(-10, 10)
        B = random.randint(-10, 10)
        D = random.randint(1, 10) * random.choice([-1, 1])
        multiplier_CD = random.randint(1, 10) * random.choice([-1, 1])
        C = D * multiplier_CD
        product_AB = A * B
        quotient_CD = C // D
        result = product_AB - quotient_CD
        q = f"計算下列各式的值。{fmt_num(A)} × {fmt_num(B)} - {fmt_num(C)} ÷ {fmt_num(D)}"
        answer_parts = [f"{fmt_num(A)} × {fmt_num(B)} - {fmt_num(C)} ÷ {fmt_num(D)}"]
        answer_parts.append(f"{fmt_num(product_AB)} - {fmt_num(quotient_CD)}")
        if quotient_CD < 0:
            answer_parts.append(f"{fmt_num(product_AB)} ＋ {fmt_num(abs(quotient_CD))}")
        answer_parts.append(f"{fmt_num(result)}")
        a = ' = '.join(answer_parts)
    c_ans = str(a)
    if any((t in c_ans for t in ['^', '/', '|', '[', '{', '\\'])):
        if 'input_mode' not in kwargs:
            kwargs['input_mode'] = 'handwriting'
            if '(請在手寫區作答!)' not in q:
                q = q.rstrip() + '\\n(請在手寫區作答!)'
    if isinstance(q, str):
        q = re.sub('^計算下列各式的值[。:: ]?', '', q).strip()
        q = re.sub('^[\\(（]?\\d+[\\)）]?', '', q).strip()
    if isinstance(a, str):
        if '=' in a:
            a = a.split('=')[-1].strip()
    return {'question_text': q, 'correct_answer': a, 'input_mode': kwargs.get('input_mode', 'text')}