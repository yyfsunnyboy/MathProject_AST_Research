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
'''

def inject_perfect_utils(code_str):
    """
    Injects PERFECT_UTILS at the top.
    CRITICAL: Strips AI-generated duplicates to prevent redefinition errors.
    """
    # 1. Strip known helper functions if AI wrote them despite instructions
    pattern = r'def\s+(check|to_latex|fmt_num|get_positive_factors|is_prime|get_prime_factorization|gcd|lcm|simplify_fraction|get_random_fraction|draw_number_line|draw_integral_area|_calculate_distance_1d|draw_geometry_composite)\(.*?(\n\s+.*)+'
    clean = re.sub(pattern, '', code_str, flags=re.MULTILINE)
    
    # 2. Strip standard imports to avoid duplication
    clean = clean.replace("import random", "").replace("import math", "").replace("from fractions import Fraction", "").replace("from functools import reduce", "")
    
    return PERFECT_UTILS + "\n" + clean


# ==============================================================================
# UNIVERSAL SYSTEM PROMPT (v9.2 Optimized - Lean & Powerful)
# 結合了「規則防護」與「範例引導」，用最少的 Token 達到最強的約束力
# ==============================================================================

UNIVERSAL_GEN_CODE_PROMPT = """
You are a Senior Python Developer (V10.2 Elite). Execute the ARCHITECT'S SPEC precisely.

### ⛔ INFRASTRUCTURE RULES:
1. **NO `matplotlib.pyplot`**: Always use `from matplotlib.figure import Figure` for thread-safety.
2. **Top-level functions ONLY**: Define `generate(level=1)` and `check(user, correct)` at module level.
3. **Traditional Chinese (Taiwan)**: All text MUST be in 繁體中文.
4. **LaTeX Integrity (Regex=0)**: For LaTeX strings (\\frac, \\sqrt), MUST use r"template".replace("{a}", str(a)).
5. **Visual Style (V10.2)**: 
   - Set `plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']`.
   - Number line ONLY shows origin '0' with fontsize 18. Point labels (A, B) set to 16+.
6. **Result Feedback**: The `result` field in `check()` function MUST be "正確！" or "答案錯誤...".
7. **Forbidden**: 【絕對禁令】：嚴禁自定義 check()、to_latex() 與 is_prime()，系統會自動注入 V10.6 鎖死版工具庫。
8. **Data Prohibition**: generate() MUST use random.randint for geometric properties. Calculate answers/coords via formulas. DO NOT hardcode values.
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
            triggers = ['^', '/', ',', '|', '(', '[', '{', '\\']
            
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
    """
    [V9.8 Upgrade] Returns (fixed_code, fix_count)
    保留 v8.8 Omni-Fix 的所有邏輯，並加入修復次數統計。
    """
    fixed_code = code_str
    total_fixes = 0
    
    # 輔助函式：執行置換並回傳次數
    def apply_fix(pattern, replacement, code):
        new_code, count = re.subn(pattern, replacement, code, flags=re.MULTILINE)
        return new_code, count

    # Step 0: Critical Escape Fixes (反斜線修復)
    fixed_code, c = apply_fix(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)
    total_fixes += c

    # 1. Invalid escapes (常見錯誤)
    fixed_code, c = apply_fix(r'(?<!\\)\\e', r'\\\\e', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(?<!\\)\\q', r'\\\\q', fixed_code)
    total_fixes += c

    # 2. f-string single brace fixes (精確化防禦邏輯)
    # 2. f-string single brace fixes (精確化防禦邏輯 - Token Based)
    def fix_latex_braces(match):
        content = match.group(1)
        # 1. Filter: Must have LaTeX-like backslashes (and not just \n)
        if not (re.search(r'\\[a-zA-Z]+', content) and not re.search(r'^\\n', content)):
            return f'f"{content}"'
            
        # 2. Tokenize: Match {Var}, {, or }
        pattern = r'(\{[a-zA-Z_][a-zA-Z0-9_]*\})|(\{)|(\})'
        
        def token_sub(m):
            if m.group(1): return m.group(1)
            if m.group(2): return "{{"
            if m.group(3): return "}}"
            return m.group(0)
            
        new_content = re.sub(pattern, token_sub, content)
        return f'f"{new_content}"'

    # 套用精確化的修復邏輯
    new_code, c = re.subn(r'f"(.*?)"', fix_latex_braces, fixed_code)
    if new_code != fixed_code: total_fixes += 1
    fixed_code = new_code
    
    new_code, c = re.subn(r"f'(.*?)'", fix_latex_braces, fixed_code)
    if new_code != fixed_code: total_fixes += 1
    fixed_code = new_code
    
    # 3. cases environment fixes (The "Smart Board" Issue)
    # 3.1 針對 f-string 內的 cases 修復
    fixed_code, c = apply_fix(r'(f"[^"]*?\\begin)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r"(f'[^']*?\\begin)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r'(f"[^"]*?\\end)\{cases\}([^"]*")', r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    fixed_code, c = apply_fix(r"(f'[^']*?\\end)\{cases\}([^']*')", r'\1{{cases}}\2', fixed_code)
    total_fixes += c
    
    # 3.2 [關鍵恢復] 手動逐行檢查 (Manual line-by-line check)
    # 這是為了修復不在 f-string 內，但被寫成 {cases} 的情況，且避免誤傷 f-string
    lines = fixed_code.split('\n')
    new_lines = []
    cases_manual_fixes = 0
    
    for line in lines:
        # 如果這一行沒有 f-string 的特徵 (f" 或 f')，才進行暴力修復
        if not re.search(r'f["\']', line): 
            new_line, c = re.subn(r'(?<!\\begin)\{cases\}', r'\\\\begin{cases}', line)
            if c > 0:
                cases_manual_fixes += c
                line = new_line
        new_lines.append(line)
    
    if cases_manual_fixes > 0:
        fixed_code = '\n'.join(new_lines)
        total_fixes += cases_manual_fixes

    # 4. General LaTeX double brace enforcement (通用數學指令保護)
    # [V9.8.9 Deprecated] Superseded by Token-Based Smart Logic in Step 2.
    # Disabling to prevent conflict with mixed python/latex strings.
    latex_patterns = [] 
    #     r'sqrt', r'frac', r'text', r'angle', r'overline', r'degree', 
    #     r'mathbf', r'mathrm', r'mathbb', r'mathcal', 
    #     r'hat', r'vec', r'bar', r'dot', 
    #     r'times', r'div', r'pm', r'mp',
    #     r'sin', r'cos', r'tan', r'cot', r'sec', r'csc',
    #     r'log', r'ln', r'lim', 
    #     r'sum', r'prod', r'binom', r'sigma', 
    #     r'perp', r'phi', r'pi', r'theta', 
    #     r'%' 
    # ]
    # for pat in latex_patterns:
    #     if pat == r'%': 
    #         fixed_code, c = apply_fix(r'\\%\{(?!\{)', r'\\%{{', fixed_code)
    #         total_fixes += c
    #     else: 
    #         fixed_code, c = apply_fix(rf'\\{pat}\{{(?!\{{)', rf'\\{pat}{{{{', fixed_code)
    #         total_fixes += c

    # v8.7.2: Exponent Protection (指數保護)
    fixed_code, c = apply_fix(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', fixed_code)
    total_fixes += c

    # 5. Brute force fallback (暴力救援模式 - 僅在錯誤訊息吻合時觸發)
    if any(k in error_msg for k in ["single '}'", "single '{'", "invalid escape sequence"]):
        fallback_fixes = 0
        fixed_code, c = apply_fix(r'\\frac\{', r'\\frac{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\}\{', r'}}{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'_\{(-?\w+)\}', r'_{{\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\^\{(-?\w+)\}', r'^{{{\1}}}', fixed_code); fallback_fixes += c # Aggressive exponent fix
        
        # [v8.7.3 Fix] 高中數學符號修復
        fixed_code, c = apply_fix(r'\\(sum|prod|binom|sigma)\_\{', r'\\\1_{{', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\\(sum|prod|binom|sigma)\^\{', r'\\\1^{{', fixed_code); fallback_fixes += c

        # Protect single char subscripts
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\$)', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\s|\,|\.)', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'(\d|\w|\))\}(?=\"|\')', r'\1}}', fixed_code); fallback_fixes += c
        fixed_code, c = apply_fix(r'\\(sin|cos|tan|cot|sec|csc)\((.*?)\)', r'\\\1(\2)', fixed_code); fallback_fixes += c
        
        total_fixes += fallback_fixes

    # 6. Python 2 print statement fix (Legacy model compatibility)
    if "expected '('" in error_msg:
        fixed_code, c = apply_fix(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        total_fixes += c
        fixed_code, c = apply_fix(r'print\s+(.*)', r'print(\1)', fixed_code)
        total_fixes += c

    # [V11.8 Punctuation Hardening Patch]
    # 暴力修復非字串區塊的全形標點符號
    # 邏輯：將行末或運算符旁的全形句號、逗號轉換或刪除
    lines = fixed_code.split('\n')
    cleaned_lines = []
    for line in lines:
        if not re.search(r'["\']', line): # 僅針對不含引號的純代碼行
            line = line.replace('。', '').replace('，', ',').replace('；', ';').replace('：', ':')
        cleaned_lines.append(line)
    fixed_code = '\n'.join(cleaned_lines)

    return fixed_code, total_fixes


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


def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired, 
                   actual_model_name="Unknown", actual_provider="google",
                   regex_fixes=0, logic_fixes=0, prompt_tokens=0, completion_tokens=0, 
                   prompt_version=1, strategy="Standard", raw_output_len=0, utils_len=0):
    """
    [V9.9.9 最終修正版] 解決重複參數問題，確保數據精確入庫。
    """
    try:
        duration = time.time() - start_time
        cpu, ram, gpu, gpuram = get_system_snapshot() # 真實硬體監控
        
        # 錯誤分類邏輯
        err_cat = None
        if error_msg and error_msg != "None":
            err_low = error_msg.lower()
            if "syntax" in err_low: err_cat = "SyntaxError"
            elif "list" in err_low: err_cat = "FormatError"
            elif "attribute" in err_low: err_cat = "StructureError"
            else: err_cat = "RuntimeError"

        log = ExperimentLog(
            timestamp=datetime.now(), # 確保頂部有 from datetime import datetime
            skill_id=skill_id,
            ai_provider=actual_provider,
            model_name=actual_model_name,
            duration_seconds=round(duration, 2),
            input_length=input_len,
            raw_output_length=raw_output_len,   # AI 產出的真實純度
            perfect_utils_length=utils_len,     # 系統注入的工具庫長度
            output_length=output_len,           # 最終存檔總長度
            is_success=success,
            syntax_error_initial=str(error_msg)[:500] if error_msg else None,
            error_category=err_cat,
            ast_repair_triggered=repaired,
            experiment_batch=getattr(Config, 'EXPERIMENT_BATCH', 'Run_V2.5_Elite'),
            prompt_strategy=strategy,
            prompt_version=prompt_version,
            regex_fix_count=regex_fixes,
            logic_fix_count=logic_fixes,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            code_complexity=raw_output_len // 40, # [Refined] Reflects AI logic only
            cpu_usage=cpu,
            ram_usage=ram,
            gpu_usage=gpu,
            gpuram_usage=gpuram
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"🚨 Experiment Log 寫入失敗: {e}")


def auto_generate_skill_code(skill_id, queue=None):
    start_time = time.time()
    
    # 1. Determine Target Tag based on Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    current_provider = role_config.get('provider', 'Unknown') # 抓取實際 provider
    target_tag = infer_model_tag(current_model)

    # 2. [Strict Mode] Fetch ONLY the matching Architect Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=target_tag, is_active=True).first()
    
    # 3. Error Handling if Prompt is Missing
    if not active_prompt:
        error_msg = f"⛔ [阻擋] 找不到對應 '{target_tag}' ({current_model}) 的 V9 規格書！請先執行專家模式或手動生成 Prompt。"
        if current_app: current_app.logger.error(f"{skill_id}: {error_msg}")
        return False, error_msg

    # Pre-fetch skill info (needed for fallback or logging)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()


    gold_standard_code = load_gold_standard_example()
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(5).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\\n"

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
    prompt_tokens = 0
    completion_tokens = 0

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        code = response.text
        
        # [V9.8] 嘗試獲取 Token 用量 (視 API 而定)
        try:
            # 適用於 Google Gemini / Vertex AI
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            # 如果是其他 API，可能需要調整這裡
        except:
            pass # 取不到就算了，保持 0
        
        match = re.search(r'```(?:python)?\s*(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if match: code = match.group(1)
        elif "import random" in code: code = code[code.find("import random"):]
        
        # [V9.5 Check] Integrity Validation
        if "def generate" not in code:
            # If critical function is missing, it implies truncation.
            # We attempt a naive fix by appending a default dispatcher if at least generate_problem exists.
            if "def generate_problem" in code:
                code += "\n\n# [Auto-Recovered Dispatcher]\ndef generate(level=1):\n    return generate_problem()"
            else:
                return False, "Critical Error: Generated code is incomplete (missing 'generate' function)."
        
        # [V9.9.9 Code Metrics] Intercept raw length before injection
        raw_len = len(code)
        
        code = inject_perfect_utils(code)
        
        # Calculate injected utils length
        utils_len = len(PERFECT_UTILS)
        total_len = len(code)
        
        # [V9.8.2 Defense] Hard Validation for 7B Models
        code, pre_fixes = validate_and_fix_code(code)
        
        # [V9.9.5 Data Flow] Accumulate preventive fixes
        regex_fixes = pre_fixes

        # [V9.9.9] Universal Helper Patcher
        # Patches all draw_* functions to ensure they return values
        code, patch_fixes = universal_function_patcher(code)
        regex_fixes += patch_fixes
        
        code = fix_return_format(code)
        code = clean_global_scope_execution(code)
        code = inject_robust_dispatcher(code) 
        code = fix_missing_answer_key(code)
        
        # [V9.8] 驗證與修復 (使用新版函式)
        is_valid, syntax_err = validate_python_code(code)
        repaired = (pre_fixes > 0) # 如果預防性修復動過，狀態改為已修復
        
        if not is_valid:
            # 呼叫新版 fix_code_syntax，接收次數
            code, r_count = fix_code_syntax(code, syntax_err)
            regex_fixes += r_count # 累加
            
            is_valid, syntax_err = validate_python_code(code)
            repaired = True
            
        is_valid_log, logic_err = validate_logic_with_pyflakes(code)
        if not is_valid_log:
            # 呼叫新版 fix_logic_errors，接收次數
            code, l_count = fix_logic_errors(code, logic_err)
            logic_fixes += l_count # 累加
            repaired = True

        # =========================================================
        # [V11.4] "Final Intercept" (The Last Line of Defense)
        # =========================================================

        # 1. String Deduplication (防止提示語堆疊)
        # 合併 question_text 中連續重複的括號引導語
        if code.count("請輸入") > 1 or code.count("例如：") > 1 or code.count("答案格式") > 1:
            code = re.sub(r'(\(請輸入.*?\))(\s*\\n\1)+', r'\1', code)
            code = re.sub(r'(\(例如：.*?\))(\s*\\n\1)+', r'\1', code)
            code = re.sub(r'(\(答案格式：.*?\))(\s*\\n\1)+', r'\1', code)

        # 2. Answer Purge (答案欄位淨化) - 強制清除引導語
        # 若 answer 欄位包含「例如：」或「請輸入」，強制還原為 str(correct_answer)
        if "例如：" in code or "請輸入" in code:
             code = re.sub(r"'answer':\s*['\"](.*?(?:例如|請輸入).*?)['\"]", r"'answer': str(correct_answer)", code)

        # 3. Quote Hardening (引號鎖死) [Final Intercept]
        # 強制修正為標準格式 ['Microsoft JhengHei']，無論 AI 產出為何
        font_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*(?:\[[^\]]*\]|['\"].*?['\"])"
        code = re.sub(font_pattern, "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']", code)

        # 4. Physical Newline Hardening (物理換行硬化)
        # 將程式碼中所有文字態的 \\n 替換為物理換行符號 \n (解決單引號/f-string 內的換行顯示問題)
        code = code.replace('\\\\n', '\\n')

        # 4. Truncation Detection (斷頭偵測) [NEW]
        # Scan for calls to _generate_type_... inside generate()
        # And ensure they are defined in the code.
        generate_match = re.search(r'def generate\(.*?\):(.*?)(?=\ndef|\Z)', code, re.DOTALL)
        if generate_match:
            generate_body = generate_match.group(1)
            calls = re.findall(r'(_generate_type_\w+)\(', generate_body)
            definitions = re.findall(r'def\s+(_generate_type_\w+)\s*\(', code)
            missing_funcs = [c for c in calls if c not in definitions]
            if missing_funcs:
                error_msg = f"Critical Error: Called functions not defined: {missing_funcs}. Code truncated?"
                log_experiment(
                    skill_id, start_time, len(prompt), len(code), False, 
                    error_msg, repaired,
                    current_model,
                    actual_provider=current_provider,
                    regex_fixes=regex_fixes, 
                    raw_output_len=raw_len,
                    utils_len=utils_len
                )
                return False, error_msg

        # 4. Logic Self-Healing (邏輯自癒)
        # 若發現 is_prime 或 _check_divisibility 函式內部包含 return {'correct': False...} 這種錯誤格式
        # 強制將其替換為標準的 return False 或 return True
        # 注意：這裡使用較為保守的替換，避免誤傷主 check 函式
        
        def fix_bool_return(match):
            func_body = match.group(0)
            if "def check" in func_body: return func_body # Skip main check function
            # Replace dict returns with bools
            fixed = re.sub(r"return\s+\{['\"]correct['\"]\s*:\s*False.*?\}", "return False", func_body)
            fixed = re.sub(r"return\s+\{['\"]correct['\"]\s*:\s*True.*?\}", "return True", fixed)
            return fixed

        # 掃描 helper functions (此處假設 helper 函式較短，且由 def 開頭)
        # 為了安全，我們針對特定函式名稱進行掃描
        for func_name in ['is_prime', '_check_divisibility', 'check_divisibility']:
            pattern = rf"(def {func_name}\(.*?\):.*?)(?=\ndef|\Z)"
            code = re.sub(pattern, fix_bool_return, code, flags=re.DOTALL)


        # 2. Handwriting Prompt Injection (Logic Enhancement) - [Cleaned up in V11.1]
        # 由於 fix_missing_answer_key 已包含增強邏輯，此處僅做備援檢查或是移除舊的 runtime patch
        if "_patch_all_returns" in code:
             # 如果 AI 沒有寫 input_mode，我們不需要強制 runtime patch 去 check 變數
             # 因為 fix_missing_answer_key 的 patch 已經很強大了
             pass
        # =========================================================

        duration = time.time() - start_time
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'}
# Fixes: Regex={regex_fixes}, Logic={logic_fixes}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + code)
            
        # [V9.8] 呼叫 Log，傳入完整數據
        log_experiment(
            skill_id, start_time, len(prompt), len(code), True, 
            syntax_err if not is_valid else "None", repaired,
            current_model,
            actual_provider=current_provider, # 傳入實際供應商
            regex_fixes=regex_fixes,      # New
            logic_fixes=logic_fixes,      # New
            prompt_tokens=prompt_tokens,  # New
            completion_tokens=completion_tokens, # New
            prompt_version=active_prompt.version if active_prompt else 1,
            strategy=active_prompt.model_tag if active_prompt else "Legacy",
            raw_output_len=raw_len,   # [新增]
            utils_len=utils_len       # [新增]
        )
        return True, "Success"

    except Exception as e:
        # [核心修復] 即使程式崩潰，也要將錯誤存入資料庫
        log_experiment(
            skill_id, start_time, len(prompt) if 'prompt' in locals() else 0, 0, False, 
            str(e), False, 
            current_model if 'current_model' in locals() else "Unknown",
            current_provider if 'current_provider' in locals() else "google",
            regex_fixes=regex_fixes, 
            prompt_version=active_prompt.version if 'active_prompt' in locals() and active_prompt else 1,
            raw_output_len=raw_len if 'raw_len' in locals() else 0, # [新增] 防止變數未定義
            utils_len=utils_len if 'utils_len' in locals() else 0   # [新增]
        )
        return False, str(e)
