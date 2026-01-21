# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 
    V16.8 Research Edition (Final Alignment)
    1. 修正 V16_SKELETON_HEAD 命名錯誤。
    2. 加入動態標頭 (Header) 生成邏輯，包含 Ablation ID 與效能數據。
    3. 強制繁體中文輸出與變數對齊 (q, a)。

版本資訊 (Version): V15.0
更新日期 (Date): 2026-01-18
維護團隊 (Maintainer): Math AI Project Team
=============================================================================    
"""
# ==============================================================================

import os
import re
import sys
import io
import time
import ast
import random
import importlib
import textwrap
import sqlite3
from datetime import datetime  # [核心修復] 補齊遺失的 datetime
import psutil                 # [數據強化] CPU/RAM 監控
try:
    import GPUtil             # [數據強化] GPU 監控
except ImportError:
    GPUtil = None

def get_system_snapshot():
    """獲取當前環境的真實硬體數據"""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu, gpuram = 0.0, 0.0
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0].load * 100
                gpuram = gpus[0].memoryUtil * 100
        except:
            pass
    return cpu, ram, gpu, gpuram

def categorize_error(error_msg):
    """根據錯誤訊息進行自動分類 [V9.9.9 Precision]"""
    if not error_msg or error_msg == "None": return None
    err_low = error_msg.lower()
    if "syntax" in err_low: return "SyntaxError"
    if "list" in err_low: return "FormatError"
    return "RuntimeError"
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
from models import db, SkillInfo, TextbookExample, ExperimentLog, SkillGenCodePrompt
from config import Config



# ==============================================================================
# --- Perfect Utils (Standard Math Tools v3.1) ---
# Description: The "Standard Library" injected into every generated skill.
# ==============================================================================
PERFECT_UTILS = r'''
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
# [修正點]：全部改為單引號，確保對稱
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

    return template.format(**safe_values)
'''

# New: SCENARIO_UTILS container for dynamic injection
SCENARIO_UTILS = r'''
# [Scenario Library]
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
    template = SCENARIO_TEMPLATES.get(template_key, {}).get(action, "")
    if not template: return f"計算：{values.get('n1', 0)} + {values.get('n2', 0)}"
    safe_values = {k: abs(v) if isinstance(v, (int, float)) and k != 'n1' else v for k, v in values.items()}
    return template.format(**safe_values)
'''

# ==============================================================================
# DYNAMIC SKELETON ENGINES (V17 Broad-Spectrum)
# ==============================================================================

# Common Tail (Shared across all skeletons)
# Removed 'mode' from return as requested (Abolish Mode 1-6)
SKELETON_TAIL = r'''
    # [AI LOGIC END]
    c_ans = str(a)
    if any(t in c_ans for t in ['^', '/', '|', '[', '{', '\\']):
        if 'input_mode' not in kwargs:
            kwargs['input_mode'] = 'handwriting'
            if "(請在手寫區作答!)" not in q: q = q.rstrip() + "\\n(請在手寫區作答!)"
    return {'question_text': q, 'correct_answer': a, 'input_mode': kwargs.get('input_mode', 'text')}

def check(user_answer, correct_answer):
    u_s = str(user_answer).strip().replace(" ", "").replace("$", "")
    c_s = str(correct_answer).strip().replace(" ", "").replace("$", "")
    return {'correct': u_s == c_s, 'result': '正確！' if u_s == c_s else '錯誤'}
'''

BASIC_HEAD = r'''
import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# [Injected Utils]
''' + PERFECT_UTILS + r'''

# ==============================================================================
# BASIC ARITHMETIC SKELETON (Dynamic)
# ==============================================================================
def generate(level=1, **kwargs):
    q, a = "", ""
    
    # [CODER_START] - Implement logic
    # ----------------------------------------------------------------------
    # Example:
    # n = random.randint(1, 100)
    # q, a = f"${n}$", str(n)
    # ----------------------------------------------------------------------
    
    # [RAG_LOGIC_HERE]
'''

GEOMETRY_HEAD = r'''
import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# [Injected Utils]
''' + PERFECT_UTILS + r'''

# ==============================================================================
# GEOMETRY & VISUAL SKELETON (Dynamic)
# ==============================================================================
def generate(level=1, **kwargs):
    q, a = "", ""
    
    # [CODER_START] - Implement visual logic using draw_* functions
    # ----------------------------------------------------------------------
    
    # [RAG_LOGIC_HERE]
'''

CALCULUS_HEAD = r'''
import random, math, io, base64, re, ast
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

# [Injected Utils]
''' + PERFECT_UTILS + r'''

# ==============================================================================
# CALCULUS & FUNCTION SKELETON (Dynamic)
# ==============================================================================
def generate(level=1, **kwargs):
    q, a = "", ""
    
    # [CODER_START] - Implement function analysis or limits
    # ----------------------------------------------------------------------
    
    # [RAG_LOGIC_HERE]
'''

def get_dynamic_skeleton(skill_id):
    """
    [V17 Structure Selector]
    Selects the appropriate skeleton based on skill characteristics.
    """
    if not skill_id: return BASIC_HEAD + SKELETON_TAIL
    
    skill_lower = skill_id.lower()
    
    # 1. Geometry / Visual Skills
    if any(k in skill_lower for k in ['geometry', 'graph', 'coordinate', 'triangle', 'circle', 'area']):
        return GEOMETRY_HEAD + SKELETON_TAIL
        
    # 2. Calculus / Function Analysis
    if any(k in skill_lower for k in ['calculus', 'limit', 'derivative', 'function', 'quadratic']):
        return CALCULUS_HEAD + SKELETON_TAIL

    # 3. Application Problems (Scenario Injection)
    # 注入 SCENARIO_UTILS 只有在應用題時
    if "應用題" in skill_id or "scenario" in skill_lower:
        return BASIC_HEAD + SCENARIO_UTILS + SKELETON_TAIL
        
    # 4. Basic Arithmetic (Default)
    return BASIC_HEAD + SKELETON_TAIL




# ==============================================================================
# UNIVERSAL SYSTEM PROMPT (v9.2 Optimized - Lean & Powerful)
# 結合了「規則防護」與「範例引導」，用最少的 Token 達到最強的約束力
# ==============================================================================
# [UNIVERSAL_GEN_CODE_PROMPT] V40.0 - 整函式替換協議
UNIVERSAL_GEN_CODE_PROMPT = r"""【Python 邏輯生成指令】：
1. **[任務目標]**：請根據 MASTER_SPEC，寫出完整的 `generate` 函式。
2. **[核心要求]**：
   - 輸出必須包含完整的函式定義：`def generate(level=1, **kwargs):`
   - 必須自行處理函式內部的所有縮進 (4 spaces)。
   - 嚴禁只輸出邏輯片段。
3. **[變數規範]**：
   - 題目賦值給 `q`，答案賦值給 `a`。
   - 數字生成使用 `random` 模組。
4. **[格式潔癖]**：
   - `q` 嚴禁包含「計算」、「求解」等引導語。
   - `a` 嚴禁包含計算過程，只保留最終答案。
"""


def infer_model_tag(model_name):
    """
    根據模型名稱自動判斷 V9 架構師的分級 (Model Tag)。
    支援 Qwen, DeepSeek, Phi, Llama 等常見模型。
    """
    name = model_name.lower()
    
    # 1. Cloud Models
    if any(x in name for x in ['gemini', 'gpt', 'claude']): return 'cloud_pro'
    
    # 2. Local Large/Medium (>= 10B)
    # DeepSeek 默認視為強邏輯模型，歸類在 local_14b (除非顯式標註 7b/8b)
    if '70b' in name or '32b' in name or '14b' in name: return 'local_14b'
    if 'deepseek' in name and not any(x in name for x in ['1.5b', '7b', '8b']): return 'local_14b'
    if 'qwen' in name and not any(x in name for x in ['0.5b', '1.5b', '3b', '7b']): return 'local_14b'
    
    # 3. Local Small/Edge (< 10B)
    if 'phi' in name or '7b' in name or '8b' in name: return 'edge_7b'
    
    # Default Fallback
    return 'local_14b'


# ==============================================================================
# --- Dispatcher Injection (v8.7 Level-Aware) ---
# ==============================================================================
def inject_perfect_utils(code_str):
    full_content = PERFECT_UTILS + "\n" + code_str
    lines = full_content.splitlines()
    cleaned_lines, seen_imports = [], set()
    
    for line in lines:
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            if s not in seen_imports:
                cleaned_lines.append(line)
                seen_imports.add(s)
            continue # 跳過重複項
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

# ==============================================================================
# --- Dispatcher Injection (v8.7 Level-Aware) ---
# ==============================================================================
def inject_robust_dispatcher(code_str):
    """
    [V8.7 智能調度器注入]
    如果模型生成了多個 generate_xxxx 函式，此工具會自動生成一個統一的 
    generate(level) 分發邏輯，確保與主程式接口對齊。
    """
    if re.search(r'^def generate\s*\(', code_str, re.MULTILINE):
        return code_str 
    
    # 搜尋所有 generate_ 開頭的函式
    candidates = re.findall(r'^def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str, re.MULTILINE)
    valid_funcs = [f for f in candidates if f not in ['generate', 'check', 'solve', 'to_latex', 'fmt_num']]
    
    if not valid_funcs: return code_str
    
    # 策略性切分：前半部為 Level 1，後半部為 Level 2
    mid_point = (len(valid_funcs) + 1) // 2
    level_1_funcs = valid_funcs[:mid_point]
    level_2_funcs = valid_funcs[mid_point:] if len(valid_funcs) > 1 else valid_funcs

    dispatcher_code = "\n\n# [Auto-Injected Smart Dispatcher v8.7]\n"
    dispatcher_code += "def generate(level=1, **kwargs):\n"
    dispatcher_code += f"    import random\n"
    dispatcher_code += f"    if level == 1:\n"
    dispatcher_code += f"        types = {str(level_1_funcs)}\n"
    dispatcher_code += f"        selected = random.choice(types)\n"
    dispatcher_code += f"    else:\n"
    
    if level_2_funcs:
        dispatcher_code += f"        types = {str(level_2_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"
    else:
        dispatcher_code += f"        types = {str(level_1_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"

    for func in valid_funcs:
        dispatcher_code += f"    if selected == '{func}': return {func}(**kwargs)\n"
    
    dispatcher_code += f"    return {valid_funcs[0]}(**kwargs)\n"
    return code_str + dispatcher_code


def fix_return_format(code_str):
    pattern = r'(^\s*)return\s+(f["\'].*?["\'])\s*,\s*(\[.*?\])\s*$'
    def repl(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2)}, 'answer': str({m.group(3)}[0]), 'correct_answer': str({m.group(3)}[0])}}"
    return re.sub(pattern, repl, code_str, flags=re.MULTILINE)


def universal_function_patcher(code_content):
    total_fixes = 0
    # 1. 找出所有以 draw_ 開頭的函式定義區塊
    # 正則表達式：尋找 def draw_...(): 到下一個 def 或 檔案結尾
    func_blocks = re.finditer(r'def (draw_[a-zA-Z0-9_]+)\(.*?\):(.*?)(\n(?=def)|$)', code_content, re.DOTALL)
    
    for match in func_blocks:
        func_name = match.group(1)
        func_body = match.group(2)
        
        # 2. 如果函式內有賦值給常見的「結果變數」，但沒有 return
        target_vars = ['result', 'html', 'fig_str', 'output', 'svg_data']
        needs_fix = any(f"{v} =" in func_body for v in target_vars) and "return" not in func_body
        
        if needs_fix:
            # 找到最後一個賦值的變數名稱
            found_var = next(v for v in target_vars if f"{v} =" in func_body)
            # 自動在函式末尾補上 return
            lines = func_body.splitlines()
            last_indent = "    "
            if lines:
                # Find last non-empty line to determine indentation or just blindly ensure 4 spaces
                # Better strategy: use the indentation of the last line of the body if available
                # But here we will follow the user provided logic which seemed to copy indentation
                for line in reversed(lines):
                     if line.strip():
                         last_indent = line[:len(line) - len(line.lstrip())]
                         break
            
            patched_body = func_body.rstrip() + f"\n{last_indent}return {found_var}\n"
            code_content = code_content.replace(func_body, patched_body)
            total_fixes += 1
            print(f"   🔧 [Universal-Fix] Patched missing return in {func_name}.")
            
    return code_content, total_fixes


def clean_global_scope_execution(code_str):
    lines = code_str.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if (s.startswith("print(") or s.startswith("generate(")) and "def " not in code_str: 
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def load_gold_standard_example():
    try:
        path = os.path.join(current_app.root_path, 'skills', 'Example_Program_Research.py')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        print(f"⚠️ Warning: Could not load Example_Program_Research.py: {e}")
    return "def generate_type_1_problem(): return {}"


def fix_missing_answer_key(code_str):
    """
    [V9.2] 確保不論 AI 如何命名回傳變數，最終都能映射到 'answer' 與 'correct_answer'。
    """
    patch_code = """
# [Auto-Injected Patch] 強制校正回傳格式
def _patch_return_dict(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            # 確保答案是字串，避免前端解析錯誤
            if 'answer' in res: res['answer'] = str(res['answer'])
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and _name.startswith('generate'):
        globals()[_name] = _patch_return_dict(_func)
"""
    return code_str + patch_code

# ==============================================================================
# --- THE REGEX ARMOR (v8.7.3 - Full Math Protection) ---
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    """
    [V9.8+ 重裝裝甲] 
    1. 統計修復次數 (用於實驗數據)
    2. 解決 f-string 與 LaTeX 括號衝突 (Token-Based)
    3. 自動校正 14B 模型常遺失的反斜線
    """
    # [V16.9.1 新增] 強力修正全形逗號與 Markdown 殘留
    fixed_code = code_str.replace("，", ", ").replace("：", ": ")
    
    # 移除可能存在的 Markdown 標記 (防止 AI 不聽話)
    fixed_code = re.sub(r'###.*?\n', '', fixed_code) 
    fixed_code = re.sub(r'```.*?(\n|$)', '', fixed_code)
    
    total_fixes = 0
    
    def apply_fix(pattern, replacement, code):
        new_code, count = re.subn(pattern, replacement, code, flags=re.MULTILINE)
        return new_code, count

    # Step 1: 基礎轉義修復 (防止 Python 語法錯誤)
    fixed_code, c = apply_fix(r'(?<!\\)\\ ', r'\\\\ ', fixed_code); total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code); total_fixes += c

    # Step 2: f-string 智慧防禦 (最核心：區分變數 {ans}, 函數 {func()} 與 LaTeX {content})
    def fix_latex_braces(match):
        content = match.group(1)
        if not (re.search(r'\\[a-zA-Z]+', content) and not re.search(r'^\\n', content)):
            return f'f"{content}"'
        
        # 使用 Token 替換：保留變數與函數呼叫，其餘轉雙括號
        # 修正後的模式：支援變數與簡單的函式呼叫 (含括號與參數)
        pattern = r'(\{[a-zA-Z_][a-zA-Z0-9_]*(\(.*\))?\})|(\{)|(\})'
        def token_sub(m):
            if m.group(1): return m.group(1) # 這裡是 Python 程式碼 (變數或函式)，保留單括號
            if m.group(3): return "{{"        # 純 LaTeX 左括號，轉義為雙括號
            if m.group(4): return "}}"        # 純 LaTeX 右括號，轉義為雙括號
            return m.group(0)
        
        new_content = re.sub(pattern, token_sub, content)
        return f'f"{new_content}"'

    fixed_code, c = re.subn(r'f"(.*?)"', fix_latex_braces, fixed_code); total_fixes += c
    fixed_code, c = re.subn(r"f'(.*?)'", fix_latex_braces, fixed_code); total_fixes += c

    # Step 3: 數學符號強化保護
    # 指數保護 ^{x} -> ^{{{x}}}
    fixed_code, c = apply_fix(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', fixed_code); total_fixes += c
    
    # Cases 環境修復 (針對分段函數)
    fixed_code, c = apply_fix(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code); total_fixes += c

    # Step 4: 暴力救援模式 (僅在發生 SyntaxError 時觸發)
    if any(k in error_msg.lower() for k in ["single '}'", "invalid escape"]):
        fixed_code, c = apply_fix(r'\\frac\{', r'\\frac{{', fixed_code); total_fixes += c
        fixed_code, c = apply_fix(r'\}\{', r'}}{{', fixed_code); total_fixes += c

    return fixed_code, total_fixes

def validate_and_fix_code(code_content):
    """
    [V40.2] 預防性框架修復與引號校準
    """
    total_fixes = 0
    
    # 1. [精準打擊] 修復錯誤的 Matplotlib 引號設定
    # 你的 Log 顯示錯誤為: plt.rcParams['font.sans-serif"] = ["Microsoft JhengHei']
    # 我們直接針對這個錯誤字串進行置換
    bad_line_1 = "plt.rcParams['font.sans-serif\"] = [\"Microsoft JhengHei']"
    bad_line_2 = 'plt.rcParams["font.sans-serif\'] = [\'Microsoft JhengHei"]'
    
    target_line = "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']"
    
    if bad_line_1 in code_content:
        code_content = code_content.replace(bad_line_1, target_line)
        total_fixes += 1
        
    if bad_line_2 in code_content:
        code_content = code_content.replace(bad_line_2, target_line)
        total_fixes += 1
        
    # 通用引號修復 (防止其他變種)
    code_content = re.sub(
        r"plt\.rcParams\[\s*['\"]font\.sans-serif['\"]\s*\]\s*=\s*\[\s*['\"]Microsoft JhengHei['\"]\s*\]",
        target_line,
        code_content
    )

    # 2. 繪圖框架安全化 (Matplotlib thread-safety)
    if "import matplotlib.pyplot" in code_content or "plt." in code_content:
        if "matplotlib.rcParams" not in code_content:
             code_content = code_content.replace("plt.rcParams", "matplotlib.rcParams")
        
        code_content = code_content.replace("import matplotlib.pyplot as plt", "from matplotlib.figure import Figure")
        code_content = code_content.replace("plt.subplots(", "Figure(")
        code_content = re.sub(r'plt\.(show|close|axis|grid|plot|text)\(.*?\)', '', code_content)
        
        total_fixes += 1

    # 3. 修正舊版變數
    if "def generate_math_question" in code_content:
        code_content = code_content.replace("def generate_math_question", "def generate")
        total_fixes += 1

    return code_content, total_fixes


# ==============================================================================
# --- Generator Pipeline ---
# ==============================================================================
def validate_python_code(code_str):
    try: ast.parse(code_str); return True, None
    except SyntaxError as e: return False, f"{e.msg} (Line {e.lineno})"
    except Exception as e: return False, str(e)


def validate_logic_with_pyflakes(code_str):
    log_stream = io.StringIO(); reporter = Reporter(log_stream, log_stream)
    pyflakes_check(code_str, "generated_code", reporter)
    error_log = log_stream.getvalue()
    return "undefined name" not in error_log.lower(), error_log


def fix_logic_errors(code_str, error_log):
    """
    [V9.8 Upgrade] Returns (fixed_code, fix_count)
    """
    fixed_code = code_str
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    
    imports = []
    fix_count = 0
    
    for var in undefined_vars:
        if var in ['random', 'math']: 
            imports.append(f"import {var}")
            fix_count += 1
        if var == 'Fraction': 
            imports.append("from fractions import Fraction")
            fix_count += 1
            
    if imports: 
        fixed_code = "\n".join(imports) + "\n" + fixed_code
        
    return fixed_code, fix_count


def log_experiment(skill_id, start_time, prompt_len, code_len, is_valid, error_msg, repaired, model_name, actual_provider=None, **kwargs):
    """
    更新後的實驗日誌紀錄函式，支援科研欄位。
    """
    duration = time.time() - start_time
    
    # 獲取硬體快照 (保留你原本的功能)
    # snapshot = get_system_snapshot() 
    
    conn = sqlite3.connect(Config.db_path)
    c = conn.cursor()
    
    # 建立對應新欄位的 INSERT 語法
    query = """
    INSERT INTO experiment_log (
        skill_id, start_time, duration_seconds, prompt_len, code_len, 
        is_success, error_msg, repaired, model_name, 
        model_size_class, prompt_level, raw_response, final_code,
        score_syntax, score_math, score_visual, healing_duration, 
        is_executable, ablation_id, missing_imports_fixed, resource_cleanup_flag,
        prompt_tokens, completion_tokens, total_tokens
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # 從 kwargs 中提取數值，若無則給預設值
    params = (
        skill_id, start_time, duration, prompt_len, code_len,
        1 if is_valid else 0, str(error_msg), 1 if repaired else 0, model_name,
        kwargs.get('model_size_class', 'Unknown'),
        kwargs.get('prompt_level', 'Bare'),
        kwargs.get('raw_response', ''),
        kwargs.get('final_code', ''),
        kwargs.get('score_syntax', 0.0),
        kwargs.get('score_math', 0.0),
        kwargs.get('score_visual', 0.0),
        kwargs.get('healing_duration', 0.0),
        kwargs.get('is_executable', 1 if is_valid else 0),
        kwargs.get('ablation_id', 1),
        kwargs.get('missing_imports_fixed', ''),
        1 if kwargs.get('resource_cleanup_flag') else 0,
        kwargs.get('prompt_tokens', 0),
        kwargs.get('completion_tokens', 0),
        kwargs.get('total_tokens', 0)
    )
    
    try:
        c.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"❌ Database Log Error: {e}")
    finally:
        conn.close()

# [core/code_generator.py] V19.5 結構清洗引擎
def clean_and_reindent_logic(raw_logic):
    """
    [V19.5 絕對對齊器]
    1. 移除每行首尾多餘空格，消除 AI 隨機跳格。
    2. 映射常見變數名 (question_text -> q, correct_answer -> a)。
    3. 統一施加 4 空格縮進。
    """
    lines = raw_logic.splitlines()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped or "return {" in stripped or "return q, a" in stripped:
            continue
        
        # 變數自動對齊 (Mapping)
        stripped = stripped.replace("question_text", "q").replace("correct_answer", "a")
        
        # 處理 if/elif/else/for 的基礎縮進保護
        # 如果這一行以關鍵字結尾或是下一行需要縮進，我們這邊維持扁平化
        # 讓系統透過接下來的結構化處理補齊
        cleaned_lines.append(stripped)

    # 重新構建邏輯塊，並補上基本縮進
    # 注意：如果 AI 寫了 if，下一行我們需要手動判斷，但更保險的做法是強制模型寫扁平代碼
    return "\n".join(["    " + l for l in cleaned_lines])

# ==============================================================================
# 核心生成函式
# ==============================================================================
# [core/code_generator.py] V40.0 - Full Function Replacement (斷頭台策略)
def auto_generate_skill_code(skill_id, queue=None, **kwargs):
    start_time = time.time()
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    ablation_id = kwargs.get('ablation_id', 3)
    
    # 1. 讀取 Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, prompt_type="MASTER_SPEC").order_by(SkillGenCodePrompt.created_at.desc()).first()
    spec = active_prompt.prompt_content if active_prompt else "生成簡單數學題。"
    full_template = get_dynamic_skeleton(skill_id)
    
    # Prompt: 要求完整函式
    prompt = UNIVERSAL_GEN_CODE_PROMPT + f"\n\n### MASTER_SPEC:\n{spec}\n\n### SKELETON CONTEXT (For Import Reference):\n{full_template}"
    
    try:
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        raw_output = response.text
        
        # ---------------------------------------------------------
        # [V40.1 Fix] 通用 Token 統計 (兼容 OpenAI 與 Gemini)
        # ---------------------------------------------------------
        prompt_tokens = 0
        completion_tokens = 0
        
        try:
            # 情況 A: Google Gemini (Native API)
            if hasattr(response, 'usage_metadata'):
                # Google 的欄位名稱比較特別
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
                
            # 情況 B: OpenAI / Ollama / Common Format
            elif hasattr(response, 'usage'):
                u = response.usage
                if isinstance(u, dict):
                    prompt_tokens = u.get('prompt_tokens', 0)
                    completion_tokens = u.get('completion_tokens', 0)
                else:
                    # 有些物件是用 dot notation
                    prompt_tokens = getattr(u, 'prompt_tokens', 0)
                    completion_tokens = getattr(u, 'completion_tokens', 0)
                    
        except Exception as e:
            print(f"⚠️ Token extraction failed: {e}")
            prompt_tokens, completion_tokens = 0, 0
        # ---------------------------------------------------------

        # --- [V40.0] 整函式替換引擎 ---
        
        # 1. 提取 AI 寫的完整函式
        clean_code = re.sub(r'```python|```', '', raw_output, flags=re.DOTALL)
        
        ai_function_code = ""
        # 尋找 def generate(level=1, **kwargs): ... 結尾
        # 我們假設 AI 只有寫這一個函式，或者這是它輸出的主要內容
        match = re.search(r"(def\s+generate\s*\(.*?\)\s*:.*)", clean_code, re.DOTALL)
        
        if match:
            ai_function_code = match.group(1)
        else:
            # 如果 AI 還是只給片段，我們只好手動幫它加上頭 (Fallback)
            print("⚠️ AI didn't provide full function header. Wrapping it.")
            ai_function_code = "def generate(level=1, **kwargs):\n" + textwrap.indent(clean_code, '    ')

        # 2. 準備清洗邏輯 (Sanitizer)
        sanitizer_block = """
    # [Auto-Sanitizer]
    if isinstance(q, str):
        q = re.sub(r'^計算下列各式的值[。:：]?', '', q).strip()
        q = re.sub(r'^[\\(（]?\\d+[\\)）]?', '', q).strip()
    if isinstance(a, str):
        if "=" in a:
            a = a.split("=")[-1].strip()
        """

        # 3. 將 Sanitizer 注入到 AI 函式的 return 之前
        # 簡單策略：找到最後一個 return，在它上面插入
        if "return " in ai_function_code:
            # 使用 rsplit 只切分最後一次出現的 return
            parts = ai_function_code.rsplit("return ", 1)
            # 確保 sanitizer 的縮進與 return 一致 (通常是 4 格)
            # 但因為 ai_function_code 是整塊的，我們直接假設標準縮進
            ai_function_code = parts[0] + sanitizer_block + "\n    return " + parts[1]
        else:
            # 如果沒 return (不太可能)，就直接加在最後
            ai_function_code += "\n" + sanitizer_block

        # 4. 處理骨架 (Skeleton) - 斷頭手術
        # 找到骨架中原本的 def generate... 位置，切掉
        if "def generate" in full_template:
            skeleton_head = full_template.split("def generate")[0]
        else:
            skeleton_head = full_template # Should not happen

        # 5. 組合：頭部 (Imports/Utils) + AI 完整函式
        final_code = skeleton_head + "\n" + ai_function_code
        
        # 6. AST 最終驗證 (確保 AI 自己的縮進是對的)
        ast_fixes = 0
        try:
            tree = ast.parse(final_code)
            # 如果能 parse，做一次正規化排版
            final_code = ast.unparse(tree)
            ast_fixes = 1
        except Exception as e:
            print(f"⚠️ AST Normalization Failed: {e}. Saving raw combination.")
            ast_fixes = 0

        # 7. 寫檔與記錄
        regex_fixes = 0
        final_code, r_fixes = fix_code_syntax(final_code)
        regex_fixes += r_fixes
        
        is_valid, error_msg = validate_python_code(final_code)
        repaired = (regex_fixes > 0 or ast_fixes > 0)
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        duration = time.time() - start_time
        
        header = f"""# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: V40.0 Full-Function-Replace
# Ablation ID: {ablation_id} | Env: RTX 5060 Ti 16GB
# Performance: {duration:.2f}s | Tokens: In={prompt_tokens}, Out={completion_tokens}
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'} | Fixes: Regex={regex_fixes}, AST={ast_fixes}
# Verification: Internal Logic Check = {'PASSED' if is_valid else 'FAILED'}
# ==============================================================================
"""
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f'{skill_id}.py'), 'w', encoding='utf-8') as f:
            f.write(header + final_code)

        log_experiment(
            skill_id, start_time, len(prompt), len(final_code), is_valid, 
            str(error_msg) if not is_valid else "Success", repaired, current_model,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            ablation_id=ablation_id, final_code=final_code, raw_response=raw_output,
            score_syntax=ast_fixes
        )
        
        return True, "V40.0 Code Generated", {'tokens': prompt_tokens + completion_tokens}

    except Exception as e:
        print(f"Generate Error: {e}")
        return False, str(e), {}
