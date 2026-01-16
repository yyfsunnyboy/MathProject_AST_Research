# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 數學題目生成腳本的核心引擎，負責生成、驗證、修復 Python 程式碼，並包含標準數學工具庫 (Perfect Utils) 的注入與程式碼安全防護。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
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
'''

def inject_perfect_utils(code_str):
    # [V16.0 強力清掃] 擴大刪除範圍，確保不留下任何「孤兒縮進」
    # 只要偵測到 AI 試圖寫 patch 或 checker，就把該區塊連根拔起
    patterns = [
        r'def\s+_patch_all_returns\(.*?\):.*?(?=\n\S|$)',
        r'def\s+check\(user_answer, correct_answer\):.*?(?=\n\S|$)',
        r'for _name, _func in list\(globals\(\)\.items\(\)\):.*'
    ]
    for pat in patterns:
        code_str = re.sub(pat, '', code_str, flags=re.DOTALL | re.MULTILINE)
    
    # 移除重複的 import
    code_str = code_str.replace("import random", "").replace("import math", "")
    
    return PERFECT_UTILS + "\n" + code_str


# ==============================================================================
# UNIVERSAL SYSTEM PROMPT (v9.2 Optimized - Lean & Powerful)
# 結合了「規則防護」與「範例引導」，用最少的 Token 達到最強的約束力
# ==============================================================================

UNIVERSAL_GEN_CODE_PROMPT = r"""
You are a Senior Python Developer (V14.0 Professional Guard).

### ⛔ 系統底層鐵律 (不可違背):
1. **方程式生成鎖死 (Equation Robustness)**:
   - 嚴禁使用 f-string 組合 `ax + by = c`。
   - 【強制流程】：必須分別判定 a, b 的正負與是否為 1，手動組合字串片段後合併。
   - 範例：`parts = []; if a==1: parts.append("x"); ... eq_str = "".join(parts) + " = " + str(c)`。

2. **視覺絕對淨化 (Zero-Graph Protocol)**:
   - 針對「判斷點是否在直線上」題型，`image_base64` 【嚴禁包含任何線段或點】。
   - 僅提供 1x1 的淺灰色網格、座標軸與原點 '0'。

3. **LaTeX 單層大括號**:
   - 所有的 \frac 必須使用 `r"\frac{n}{d}"` 結構，嚴禁出現 `{{ }}`。
   - 所有的變數代換必須使用 `.replace("{n}", str(val))`。

4. **閱卷與反饋**:
   - check(u, c) 僅限回傳 True/False。
   - 系統 Patch 會自動移除 $ 與 \ 符號。

5. **座標精度**: 座標值僅限整數或 0.5。
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
def inject_robust_dispatcher(code_str):
    if re.search(r'^def generate\s*\(', code_str, re.MULTILINE):
        return code_str 
    
    # 搜尋所有 generate_ 開頭的函式
    candidates = re.findall(r'^def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str, re.MULTILINE)
    valid_funcs = [f for f in candidates if f not in ['generate', 'check', 'solve', 'to_latex', 'fmt_num']]
    
    if not valid_funcs: return code_str
    
    # Heuristic Split: First half -> Level 1, Second half -> Level 2
    mid_point = (len(valid_funcs) + 1) // 2
    level_1_funcs = valid_funcs[:mid_point]
    level_2_funcs = valid_funcs[mid_point:] if len(valid_funcs) > 1 else valid_funcs

    dispatcher_code = "\n\n# [Auto-Injected Smart Dispatcher v8.7]\n"
    dispatcher_code += "def generate(level=1):\n"
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
        dispatcher_code += f"    if selected == '{func}': return {func}()\n"
    
    dispatcher_code += f"    return {valid_funcs[0]}()\n"
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
        path = os.path.join(current_app.root_path, 'skills', 'Example_Program.py')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        print(f"⚠️ Warning: Could not load Example_Program.py: {e}")
    return "def generate_type_1_problem(): return {}"


def fix_missing_answer_key(code_str):
    """[V10.3.1] 增加換行修復、回傳格式強化與全面中文化反饋"""
    patch_code = r"""
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
                # 解決 r-string 導致的 \\n 問題
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            
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
                res['question_text'] = res['question_text'].rstrip() + "\\n(請在手寫區作答!)"

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
"""
    return code_str + patch_code

# ==============================================================================
# --- THE REGEX ARMOR (v8.7.3 - Full Math Protection) ---
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    fixed_code = code_str
    total_fixes = 0
    
    # 1. 基礎反斜線修復 (Regex Armor)
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 2. [智慧冪等修復] 僅在缺失 \begin 時補全 cases
    lines = fixed_code.split('\n')
    cleaned_lines = []
    for line in lines:
        # IME 全形自癒：抹除行末非法標點
        line = re.sub(r'[。，；：]\s*$', '', line)
        if not re.search(r'["\']', line):
            line = line.replace('，', ',').replace('；', ';').replace('：', ':')
        
        # LaTeX cases 安全網：防止 \begin{\\begin{cases}}
        if "{cases}" in line and "\\begin{cases}" not in line:
            line = line.replace("{cases}", "\\\\begin{cases}")
            total_fixes += 1
        
        # 指數保護
        line = re.sub(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', line)
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines), total_fixes


def validate_and_fix_code(code_content):
    """
    [V10.2 Pure] 採用「隔離注入」與「字典封裝」策略。
    解決引號不對稱 (SyntaxError) 與 500 錯誤。
    """
    total_fixes = 0
    
    # --- [V10.2] 隔離注入：使用 r-string 三引號保護補丁 ---
    if ("matplotlib" in code_content or "Figure" in code_content) and "font.sans-serif" not in code_content:
        font_style_patch = r'''
# [V10.2 Elite Font & Style]
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def _apply_v10_visual_style(ax):
    ax.set_xticks([0])
    for tick in ax.get_xticklabels():
        tick.set_fontsize(18); tick.set_fontweight('bold')
    ax.set_title(""); ax.set_xlabel("")
'''
        # 放在最頂部，避開後續 Regex 掃描
        code_content = font_style_patch + "\n" + code_content
        total_fixes += 1

    # [V10.6.2 Elite] 針對字體設定行的「全方位引號對齊」手術
    # 增加對 matplotlib.rcParams, plt.rcParams 與 rcParams 的全面支援
    font_conf_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*\[['\"]Microsoft JhengHei['\"]\]"
    replacement = "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']"
    
    # 執行置換並精確統計修復次數
    code_content, f_count = re.subn(font_conf_pattern, replacement, code_content)
    total_fixes += f_count
    
    if f_count > 0:
        print(f"   🔧 [Font-Fix] Aligned quotes in matplotlib config ({f_count} lines).")

    # --- [V10.2] 答案驗證格式自癒 ---
    # 如果 AI 寫了裸露的 return True/False，自動包裝並加入正確答案顯示



    # LaTeX 精確修復 (避開 \n)
    def smart_fix(match):
        nonlocal total_fixes
        c = match.group(1)
        if re.search(r'\\[a-zA-Z]+', c) and not re.search(r'^\\n', c) and "{" in c and "{{" not in c:
            if not re.search(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', c):
                total_fixes += 1
                return f'f"{c.replace("{", "{{").replace("}", "}}")}"'
        return f'f"{c}"'
    
    code_content = re.sub(r'f"(.*?)"', smart_fix, code_content)
    code_content = re.sub(r"f'(.*?)'", smart_fix, code_content)
    
    # [新增] 偵測過度轉義的 Python 變數 (例如 {{ans}})
    # 這通常是 AI 被 LaTeX 規則搞混的結果
    over_escaped_pattern = r'f".*?\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}.*?"'
    matches = re.findall(over_escaped_pattern, code_content)
    if matches:
        # 將 {{var}} 修正為 {var}
        for m in matches:
            fixed = m.replace("{{", "{").replace("}}", "}")
            code_content = code_content.replace(m, fixed)
            total_fixes += 1 # 這下子實驗數據就不會是 0 了！
    
    # =========================================================
    # 防線 3：變數名稱防呆 (防止 Target_val 錯誤)
    # =========================================================
    if "return {" in code_content and "target_val" in code_content:
         if "target_val =" not in code_content and "ans =" in code_content:
             code_content = code_content.replace("str(target_val)", "str(ans)")
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


def auto_generate_skill_code(skill_id, queue=None, **kwargs):
    """
    更新後的生成函式，支援 3x3 實驗數據採集。
    """
    start_time = time.time()
    
    # 1. Determine Target Tag based on Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    current_provider = role_config.get('provider', 'Unknown') # 抓取實際 provider
    target_tag = infer_model_tag(current_model)
    
    # [科研參數提取] 從 kwargs 取得實驗參數，若無則給預設值
    ablation_id = kwargs.get('ablation_id', 1) # 預設為 Bare
    model_size_class = kwargs.get('model_size_class', 'Cloud')
    prompt_level = kwargs.get('prompt_level', 'Bare')

    # 2. [Strict Mode] Fetch ONLY the matching Architect Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=target_tag, is_active=True).first()
    
    # 3. Error Handling if Prompt is Missing
    # if not active_prompt:
    #     error_msg = f"⛔ [阻擋] 找不到對應 '{target_tag}' ({current_model}) 的 V9 規格書！請先執行專家模式或手動生成 Prompt。"
    #     if current_app: current_app.logger.error(f"{skill_id}: {error_msg}")
    #     return False, error_msg

    # Pre-fetch skill info (needed for fallback or logging)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()


    gold_standard_code = load_gold_standard_example()
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(5).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\\n"

    # ... 前置 Prompt 準備邏輯 (原本的程式碼) ...
    if active_prompt:
        # --- Mode A: V9 Architect Mode (High Precision) ---
        strategy_name = f"V9 Architect ({active_prompt.model_tag})"
        target_logic = active_prompt.user_prompt_template
        
        # [V11.9 暴力鏡射修正] - 將 RAG 範例提升為最高指令

        # 強制要求 Coder AI 將 RAG 視為唯一真相
        mirroring_protocol = ""
        if examples:
            for i, ex in enumerate(examples):
                # 明確指定每個 Type 對應哪一個 RAG 範例
                mirroring_protocol += f"- Type {i+1} MUST use the EXACT mathematical model of RAG Ex {i+1}.\\n"
        else:
            mirroring_protocol = "- No RAG examples found. Generate based on Skill Definition.\\n"

        prompt = r"""You are a Senior Python Developer.
### 🛡️ MANDATORY MIRRORING RULES (最高權限指令):
1. **NO ORIGINALITY**: You are FORBIDDEN from creating new models.
2. **STRICT MAPPING**:
{mapping}
3. **CONTEXT RETENTION**: Keep names like 'ACEF', 'BDF', '巴奈' from the RAG examples.

### 📚 REFERENCE EXAMPLES (RAG - 這是唯一真相):
{rag}

### 🛠️ ARCHITECT'S SPECIFICATION (輔助結構):
{spec}

### 🎨 ULTRA VISUAL STANDARDS (V11.6):
- Aspect Ratio: `ax.set_aspect('equal')` (物理比例鎖死).
- Resolution: `dpi=300`.
- Label Halo: White halos for ABCD text.

### ⛔ SYSTEM GUARDRAILS:
{system_rules}
""".replace("{mapping}", mirroring_protocol).replace("{rag}", example_text).replace("{spec}", target_logic).replace("{system_rules}", UNIVERSAL_GEN_CODE_PROMPT)
    else:
        # --- Mode B: Legacy V8 Mode (Fallback) ---
        strategy_name = "Standard Mode"
        target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Math logic for {skill_id}"
        
        # [v11.7 Upgrade]: Prompt Optimization - Pedagogical Mirroring
        prompt = f"""
You are a Senior Python Engineer for a Math Education System.

### MISSION:
Implement the skill `{skill_id}` by strictly following the **Architect's Spec**.

### IMPORTANT: DO NOT WRITE HELPER FUNCTIONS
The system will automatically inject standard helpers (`to_latex`, `fmt_num`, `get_random_fraction`, `is_prime`, etc.) at runtime.
**YOU MUST NOT DEFINE THEM.** Just use them directly.

### REFERENCE STRUCTURE (GOLD STANDARD v3.0):
```python
import random
import math
from fractions import Fraction

# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    val = get_random_fraction()
    # Question needs LaTeX wrapping:
    q = f"What is ${{to_latex(val)}}?"
    # Answer MUST be clean (NO $ signs):
    a = to_latex(val) 
    return {{'question_text': q, 'answer': a, 'correct_answer': a}}

def generate(level=1):
    # Dispatcher logic
    ...
ARCHITECT'S SPECIFICATION: {target_logic}

### REFERENCE EXAMPLES (RAG):
{example_text}

### 💡 INSTRUCTION:
Your task is to dynamize (Dynamize) the following examples into Python code, strictly adhering to their mathematical models.

### 🛡️ PEDAGOGICAL PRIORITY PROTOCOL (V11.7):
1. **Type 1 - Textbook Mirroring (Mirror Mode)**:
   - You MUST generate `generate_type_1` by strictly mirroring the first RAG example.
   - **NO ORIGINALITY**: Use the EXACT same mathematical model. ONLY Randomize the numbers.
   - **Context**: Keep keywords like "Aquarium", "Ticket". Do not change context.

2. **Data Linkage (Integer Guarantee)**:
   - For Reverse Calculation problems, generate the integer ANSWER first, then derive the question parameters.

CODING RULES:

1. **NO HELPERS**: Do NOT define `to_latex`, `fmt_num`, `check`, etc. They are auto-injected. Use them directly.

2. **Smart Dispatcher**: Implement `def generate(level=1):` to handle difficulty levels.
   - **[重要：函式命名規範]** 不論題目類型為何，主生成函式必須統一命名為 `generate()`。
   - 禁止使用 `generate_number_line()` 或 `generate_logic()` 等自定義名稱。
   - 如果有繪圖輔助函式（如 `draw_graph`），請在 `generate()` 函式內部呼叫它。
   - 必須確保檔案中存在 `def generate():` 和 `def check(user_answer, correct_answer):`。

3. **LaTeX Formatting (CRITICAL)**: 
   - All mathematical expressions (integers, fractions, equations) in `question_text` MUST be wrapped in single dollar signs `$`.
   - Example: `f"計算 ${fmt_num(a)} + {fmt_num(b)}$ 的值"` -> "計算 $3 + 5$ 的值".
   - **NO BACKTICKS**: Never use backticks (`) to wrap numbers or lists. BAD: `[1, 2]`. GOOD: $1, 2$.

4. **Answer Format Hint (CRITICAL)**:
   - You **MUST** append a clear format hint at the very end of `question_text`.
   - Format: `\\n(答案格式：...)`.
   - Example 1 (Values): `... \\n(答案格式：請填寫整數)` or `... \\n(答案格式：最簡分數)`.
   - Example 2 (Variables): `... \\n(答案格式：x=_, y=_)` (This ensures specific ordering).
   - Example 3 (Coordinates): `... \\n(答案格式：(x,y))`.

5. **Return Keys**: Return dict with keys: `'question_text'`, `'answer'`, `'correct_answer'`.
   - `correct_answer`: Must be a clean string for checking (e.g., "-5", "3/4", "x=2, y=3"). 
   - Do NOT use LaTeX (`$`) in `correct_answer` or `answer` keys, as this makes user input matching difficult. Keep it raw text.

6. **Language**: Traditional Chinese (Taiwan) ONLY (繁體中文). Use local terminology (e.g., 座標, 聯立方程式).

7. **Level Completeness**: Implement both Level 1 (Basic) and Level 2 (Advanced/Applied).

OUTPUT: Return ONLY the Python code. Start with `import random`.

[防呆輸出要求] 在 Python 檔案的最末尾，請務必包含以下代碼，確保進入點相容性：
```python
# 確保主進入點存在 (別名掛載)
if 'generate' not in globals() and any(k.startswith('generate_') for k in globals()):
    generate = next(v for k, v in globals().items() if k.startswith('generate_'))
``` """

    # 初始化計數器
    regex_fixes = 0
    logic_fixes = 0
    ast_repairs = 0
    prompt_tokens = 0
    completion_tokens = 0

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        # 1. 取得 LLM 原始回覆 (攔截點)
        
        # 模擬 ai_wrapper 回傳 (內容, tokens) 的行為
        # 這裡假設你的 get_ai_client 回傳的 client 仍然是 google.generativeai 的物件
        response = client.generate_content(prompt)
        raw_response = response.text
        
        # [V9.8] 嘗試獲取 Token 用量
        try:
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
        except:
            pass

        raw_len = len(raw_response)
        
        # 2. 啟動自癒流水線與計時
        healing_start = time.time()
        
        processed_code = raw_response
        
        # 簡單清理 markdown
        match = re.search(r'```(?:python)?\s*(.*?)```', processed_code, re.DOTALL | re.IGNORECASE)
        if match: processed_code = match.group(1)
        elif "import random" in processed_code: processed_code = processed_code[processed_code.find("import random"):]
        
        # 根據實驗組別 (ablation_id) 決定修復強度
        # 1: Bare (不修復) | 2: Regex Only | 3: Full Healing (Regex + AST)
        
        final_code = processed_code
        
        if ablation_id >= 2:
            # Regex Armor
            final_code = inject_perfect_utils(final_code)
            
            # [V9.8.2 Defense] Hard Validation for 7B Models
            # validate_and_fix_code 包含了 regex 修復
            final_code, pre_fixes = validate_and_fix_code(final_code)
            regex_fixes += pre_fixes

            final_code, patch_fixes = universal_function_patcher(final_code)
            regex_fixes += patch_fixes
            
            final_code = fix_return_format(final_code)
            final_code = clean_global_scope_execution(final_code)
            final_code = inject_robust_dispatcher(final_code) 
            final_code = fix_missing_answer_key(final_code)
            
        
        if ablation_id == 3:
            # Full Healing (AST + Logic)
            # [V9.8] 驗證與修復
            is_valid, syntax_err = validate_python_code(final_code)
            if not is_valid:
                final_code, r_count = fix_code_syntax(final_code, syntax_err)
                regex_fixes += r_count # Count this as regex/syntax fix
                ast_repairs += 1 # Count as a repair event
                
            is_valid_log, logic_err = validate_logic_with_pyflakes(final_code)
            if not is_valid_log:
                final_code, l_count = fix_logic_errors(final_code, logic_err)
                logic_fixes += l_count
                ast_repairs += 1 # Count as a repair event

            # Final Logic Hardening
             # 1. String Deduplication
            if final_code.count("請輸入") > 1 or final_code.count("例如：") > 1:
                final_code = re.sub(r'(\(請輸入.*?\))(\s*\\n\1)+', r'\1', final_code)
            
             # 2. Quote Hardening
            font_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*(?:\[[^\]]*\]|['\"].*?['\"])"
            final_code = re.sub(font_pattern, "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']", final_code)
            
             # 3. Physical Newline Hardening
            final_code = final_code.replace('\\\\n', '\\n')


        healing_duration = time.time() - healing_start

        # 3. 實驗評分：語法正確性校驗 (score_syntax)
        try:
            ast.parse(final_code)
            score_syntax = 100.0
        except SyntaxError:
            score_syntax = 0.0
            
        # 寫入檔案
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {time.time() - start_time:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: Ablation={ablation_id}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + final_code)

        # 4. 呼叫更新後的 log_experiment (科研對接)
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=len(prompt),
            code_len=len(final_code),
            is_valid=(score_syntax == 100.0),
            error_msg="None" if score_syntax == 100.0 else "Syntax Error",
            repaired=(ast_repairs > 0 or regex_fixes > 0 or logic_fixes > 0),
            model_name=current_model,
            actual_provider=current_provider,
            # --- 傳入科研專用 kwargs ---
            model_size_class=model_size_class,
            prompt_level=prompt_level,
            raw_response=raw_response,       # 存下 AI 的「原始幻覺」
            final_code=final_code,           # 存下你的「醫療成果」
            score_syntax=score_syntax,
            healing_duration=healing_duration,
            ablation_id=ablation_id,
            ast_repair_count=ast_repairs,
            regex_fix_count=regex_fixes,
            logic_fix_count=logic_fixes,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            resource_cleanup_flag=True # 標記資源釋放
        )

        return True, "Success", {
            'raw_response': raw_response,
            'score_syntax': score_syntax,
            'fixes': regex_fixes + logic_fixes + ast_repairs,
            'healing_duration': healing_duration
        }

    except Exception as e:
        # 即使崩潰也要紀錄，這對分析模型穩定性非常重要
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=0,
            code_len=0,
            is_valid=False,
            error_msg=str(e),
            repaired=False,
            model_name=current_model if 'current_model' in locals() else "Unknown",
            raw_response=raw_response if 'raw_response' in locals() else "LLM API Failure",
            ablation_id=ablation_id,
            model_size_class=model_size_class,
            prompt_level=prompt_level
        )
        return False, str(e), {}

