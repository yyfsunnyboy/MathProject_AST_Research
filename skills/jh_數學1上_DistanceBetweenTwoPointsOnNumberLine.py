# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 20.77s | RAG: 5 examples
# Created At: 2026-01-14 00:22:21
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{rem_num}}{{abs_num.denominator}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
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

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result # [必須補上這行]    

# --- 4. High-Level Math Objects (Vector/Matrix/Calculus) ---
class Vector3:
    """Simple 3D Vector Class for Geometry."""
    def __init__(self, x, y, z=0): self.x, self.y, self.z = x, y, z
    def __add__(self, o): return Vector3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vector3(self.x-o.x, self.y-o.y, self.z-o.z)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o): return Vector3(self.y*o.z-self.z*o.y, self.z*o.x-self.x*o.z, self.x*o.y-self.y*o.x)
    def mag(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def __repr__(self): return f"({self.x}, {self.y}, {self.z})"

class Matrix:
    """Simple Matrix (2x2 or 3x3) for transformations."""
    def __init__(self, rows): self.rows = rows
    def det(self):
        if len(self.rows) == 2: return self.rows[0][0]*self.rows[1][1] - self.rows[0][1]*self.rows[1][0]
        return 0 # Placeholder for 3x3
    def mv(self, v): # Matrix-Vector multiplication
        return Vector3(
            self.rows[0][0]*v.x + self.rows[0][1]*v.y,
            self.rows[1][0]*v.x + self.rows[1][1]*v.y, 0
        )

def draw_integral_area(func_lambda, x_range, color='blue', alpha=0.3):
    """
    [Visual] Helper to plot area under curve. 
    Usage: In generate(), ax.fill_between(x, y, ...).
    Actually, this is just a placeholder to remind AI to use fill_between.
    """
    pass

# --- 5. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案 (No answer)"}
    
    # 1. Normalize strings (字串正規化)
    def normalize(s):
        s = str(s).strip()
        # 移除空格、LaTeX間距
        s = s.replace(" ", "").replace("\\,", "").replace("\\;", "")
        # [Fix] 支援中文全形逗號，轉為半形，避免判錯
        s = s.replace("，", ",") 
        return s
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy (精確比對)
    if user_norm == correct_norm:
        return {"correct": True, "result": "Correct!"}
        
    # 3. Float Match Strategy (數值容錯比對)
    try:
        # 嘗試將兩者都轉為浮點數，如果誤差極小則算對
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # 無法轉為數字，可能是代數式或座標，維持字串比對結果
        
    # [Fix] 錯誤訊息優化：中文、換行顯示，去除不必要的符號
    # 這裡回傳的 result 會直接顯示在前端 Result 區域
    return {"correct": False, "result": f"答案錯誤。正確答案為：\n{correct_answer}"}



from datetime import datetime
import base64 # 雖然本實現中 image_base64 為 None，但依規範保留此 import。

# --- 視覺化工具規範 (Visuals): 數線工具 ---

def generate(level=1):
    """
    生成 K12 數學「數線上兩點的距離」的題目。
    根據 `level` 參數（目前未使用，但依規範保留）和隨機邏輯，產生不同題型。
    嚴禁使用 class 封裝，必須直接定義於模組最外層。
    確保代碼不依賴全域狀態，以便系統執行 importlib.reload。
    """
    # 隨機分流：實作至少 3 種不同的題型變體
    problem_type = random.choice([1, 2, 3])

    question_text_part = ""
    correct_answer_value = None
    points_for_visual = {}

    if problem_type == 1:
        # 題型 1: 直接計算 (Direct Calculation)
        # 隨機生成兩個不同的整數座標
        a = random.randint(-15, 15)
        b = random.randint(-15, 15)
        while a == b: # 確保兩點不同
            b = random.randint(-15, 15)

        correct_answer_value = abs(a - b)

        # 排版與 LaTeX 安全: 嚴禁使用 f-string 處理 LaTeX 區塊
        question_template = r"數線上兩點 $A({a})$ 和 $B({b})$ 之間的距離是多少？"
        question_latex_safe = question_template.replace("{a}", str(a)).replace("{b}", str(b))
        
        question_text_part = f"請計算以下問題：<br>{question_latex_safe}"
        points_for_visual = {"A": a, "B": b}

    elif problem_type == 2:
        # 題型 2: 逆向求解（已知距離求座標）
        # 數線上一點 A，已知與另一點 B 的距離和方向，求 B 的座標。
        start_point = random.randint(-15, 15)
        distance = random.randint(3, 12) # 距離至少為 3
        
        # 隨機決定未知點 B 在 A 的左側或右側
        direction_multiplier = random.choice([-1, 1]) # -1 代表左側, 1 代表右側
        
        unknown_point_coord = start_point + direction_multiplier * distance
        correct_answer_value = unknown_point_coord

        direction_text = "右側" if direction_multiplier == 1 else "左側"
        
        # 排版與 LaTeX 安全: 嚴禁使用 f-string 處理 LaTeX 區塊
        question_template = r"數線上一點 $A({start_point})$，若它與另一點 $B$ 的距離為 ${distance}$，且 $B$ 點在 $A$ 點的{direction_text}，則 $B$ 點的座標為何？"
        
        question_latex_safe = question_template \
            .replace("{start_point}", str(start_point)) \
            .replace("{distance}", str(distance)) \
            .replace("{direction_text}", direction_text)
            
        question_text_part = f"請計算以下問題：<br>{question_latex_safe}"
        # 視覺化時顯示起始點和最終結果點
        points_for_visual = {"A": start_point, "B": unknown_point_coord}

    elif problem_type == 3:
        # 題型 3: 情境應用（如移動點）
        # 一個點 P 從某座標開始，經過多次移動，求最終座標。
        p_start = random.randint(-15, 15)
        d1 = random.randint(2, 10) # 第一次移動距離
        d2 = random.randint(2, 10) # 第二次移動距離

        # 隨機決定兩次移動的方向
        dir1_multiplier = random.choice([-1, 1])
        dir2_multiplier = random.choice([-1, 1])

        p_intermediate = p_start + dir1_multiplier * d1
        p_final = p_intermediate + dir2_multiplier * d2
        correct_answer_value = p_final

        dir1_text = "向右" if dir1_multiplier == 1 else "向左"
        dir2_text = "向右" if dir2_multiplier == 1 else "向左"

        # 排版與 LaTeX 安全: 嚴禁使用 f-string 處理 LaTeX 區塊
        question_template = r"數線上一點 $P$ 原先在座標 ${p_start}$。若 $P$ 先{dir1_text}移動 ${d1}$ 單位，再{dir2_text}移動 ${d2}$ 單位，則 $P$ 點最終的座標為何？"
        
        question_latex_safe = question_template \
            .replace("{p_start}", str(p_start)) \
            .replace("{dir1_text}", dir1_text) \
            .replace("{d1}", str(d1)) \
            .replace("{dir2_text}", dir2_text) \
            .replace("{d2}", str(d2))

        question_text_part = f"請計算以下問題：<br>{question_latex_safe}"
        # 視覺化時顯示起始點和最終點，中間點可省略以保持簡潔
        points_for_visual = {"P_起始": p_start, "P_最終": p_final}

    # 視覺化工具規範: question_text 必須由「文字題目 + <br> + 視覺化 HTML」組成。
    visual_html = draw_number_line(points_for_visual)
    final_question_text = question_text_part + "<br>" + visual_html


    # 數據與欄位 (Standard Fields): 返回字典必須且僅能包含指定欄位
    return {
        "question_text": final_question_text,
        "correct_answer": str(correct_answer_value), # 確保為字串類型
        "answer": str(correct_answer_value),         # 確保為字串類型，用於顯示
        "image_base64": None,                        # 本範例不生成圖片，因此為 None
        "created_at": datetime.now().isoformat(),    # 時間戳記 (ISO 8601 格式)
        "version": "9.6.0"                           # 系統版本號
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    嚴禁使用 class 封裝，必須直接定義於模組最外層。
    user_answer: 使用者輸入的答案 (字串)。
    correct_answer: 系統生成的正確答案 (字串)。
    """
    try:
        # 將答案轉換為浮點數進行比較，以處理潛在的數字格式問題
        user_ans_float = float(user_answer)
        correct_ans_float = float(correct_answer)
        # 考慮浮點數精度問題，使用 math.isclose 進行比較
        return math.isclose(user_ans_float, correct_ans_float, rel_tol=1e-9, abs_tol=1e-9)
    except ValueError:
        # 如果轉換失敗 (例如，使用者輸入非數字字串)，則答案錯誤
        return False

# [Auto-Injected Patch v9.2] Universal Return Fixer
# 1. Ensures 'answer' key exists (copies from 'correct_answer')
# 2. Ensures 'image_base64' key exists (extracts from 'visuals')
def _patch_return_dict(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            # Fix 1: Answer Key
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            
            # Fix 2: Image Key (Flatten visuals for legacy frontend)
            if 'image_base64' not in res and 'visuals' in res:
                try:
                    # Extract first image value from visuals list
                    for item in res['visuals']:
                        if item.get('type') == 'image/png':
                            res['image_base64'] = item.get('value')
                            break
                except: pass
        return res
    return wrapper

# Apply patch to ALL generator functions in scope
import sys
# Iterate over a copy of globals keys to avoid modification issues
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'generate'):
        globals()[_name] = _patch_return_dict(_func)
