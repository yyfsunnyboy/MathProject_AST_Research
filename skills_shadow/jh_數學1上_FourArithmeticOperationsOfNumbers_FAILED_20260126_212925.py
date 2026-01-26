# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: qwen2.5-coder:14b | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 57.13s | Tokens: In=4769, Out=2048
# Created At: 2026-01-26 21:29:25
# Fix Status: [Repaired] | Fixes: Regex=8, AST=0
# Verification: Internal Logic Check = FAILED
# ==============================================================================


# [INJECTED UTILS]

import random
import math
from fractions import Fraction
import re
import ast
import operator

# [Research Standard Utils]

def to_latex(num):
    """
    將數字轉換為 LaTeX 格式 (支援分數、整數、小數)
    [V46.2 Fix]: 強制限制分數的複雜度 (分母 <= 100)，避免出現百萬級大數。
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    
    if isinstance(num, Fraction):
        # [Critical Fix] 強制整形：如果分母太大，強制找最接近的簡單分數
        # 這能把 1060591/273522 自動變成合理的 K12 數字 (如 3 7/8)
        if num.denominator > 100:
            num = num.limit_denominator(100)

        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        
        # 統一處理正負號
        is_neg = num < 0
        sign_str = "-" if is_neg else ""
        abs_num = abs(num)
        
        # 帶分數處理 (Mixed Number)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: 
                return f"{sign_str}{whole}"
            # ✅ 修正: 整數部分不加大括號 (V46.5)
            return f"{sign_str}{whole}\\frac{{{rem_num}}}{{{abs_num.denominator}}}"
            
        # 真分數處理 (Proper Fraction)
        return f"{sign_str}\\frac{{{abs_num.numerator}}}{{{abs_num.denominator}}}"
        
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    格式化數字 (標準樣板要求)：
    - 自動括號：負數會自動被包在括號內 (-5) 或 (-\frac{1}{2})
    - signed=True: 強制顯示正負號 (+3, -5)
    """
    # 1. 取得基礎 LaTeX 字串
    latex_val = to_latex(num)
    
    # 2. 判斷是否為 0
    if num == 0 and not signed and not op: return "0"
    
    # 3. 判斷正負 (依賴數值本身)
    is_neg = (num < 0)
    
    # 為了處理 op=True 或 signed=True，我們需要絕對值的字串
    if is_neg:
        # 移除開頭的負號以取得絕對值內容
        # 注意: to_latex 可能回傳 "-{1}\frac..." 或 "-\frac..."
        if latex_val.startswith("-"):
            abs_latex_val = latex_val[1:] 
        else:
            abs_latex_val = latex_val # Should not happen but safe fallback
    else:
        abs_latex_val = latex_val

    # 4. 組裝回傳值
    if op: 
        return f" - {abs_latex_val}" if is_neg else f" + {abs_latex_val}"
    
    if signed: 
        return f"-{abs_latex_val}" if is_neg else f"+{abs_latex_val}"
    
    if is_neg: 
        return f"({latex_val})"
        
    return latex_val

# [AST Healer Inject] 安全運算核心
def safe_eval(expr_str):
    """
    [AST Healer 專用] 安全的數學表達式解析器
    [V46.4 Fix]: Python 3.12+ 兼容性修復，移除 ast.Num 依賴。
    """
    # 允許的運算子白名單
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv, 
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval(node):
        # [Python 3.12+ Fix] ast.Num 已被移除，使用 ast.Constant
        if isinstance(node, ast.Constant):
            return node.value
        # [Legacy] 保留 ast.Num 以支持舊版 Python (< 3.8)
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            # 關鍵：遇到除法，自動轉 Fraction
            if isinstance(node.op, ast.Div):
                return Fraction(left, right)
            return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'Fraction':
                args = [_eval(a) for a in node.args]
                return Fraction(*args)
        raise TypeError(f"Unsupported type: {node}")

    try:
        # 預處理：將 LaTeX 運算符轉回 Python
        clean_expr = str(expr_str).replace('\\times', '*').replace('\\div', '/')
        # 解析並計算
        result = _eval(ast.parse(clean_expr, mode='eval').body)
        
        # [Clamp] 強制整形：運算結果如果是複雜分數，直接化簡
        if isinstance(result, Fraction):
            if result.denominator > 100 or abs(result.numerator) > 10000:
                result = result.limit_denominator(100)
                
        return result
    except Exception as e:
        return 0

# [數論工具箱]
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

def get_factors(n):
    n = abs(n)
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def clean_latex_output(q_str):
    """
    [V46.6 Fix] LaTeX 格式清洗器 (移除帶分數大括號邏輯)
    修復常見的 LaTeX 運算符錯誤與格式問題
    """
    if not isinstance(q_str, str): return str(q_str)
    clean_q = q_str.replace('$', '').strip()
    import re
    
    # 1. 修復運算符：* -> \times, / -> \div
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*\*\s*', r' \\times ', clean_q)
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*/\s*(?![{}])', r' \\div ', clean_q)
    
    # 2. 修復雙重括號 ((...)) -> (...)
    clean_q = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', clean_q)
    
    # 3. [REMOVED V46.6] 不再自動添加帶分數大括號
    # 原邏輯: clean_q = re.sub(r'(\d+)\s*(\\frac)', r'{\1}\2', clean_q)
    # 原因: to_latex() 已經正確處理格式，此步驟會誤傷
    
    # 4. 移除多餘空白
    clean_q = re.sub(r'\s+', ' ', clean_q).strip()
    
    return f"${clean_q}$"

def check(user_answer, correct_answer):
    """
    [V45.7 Smart Validator]
    """
    if not user_answer: return {"correct": False, "result": "未作答"}
    
    def parse_value(val_str):
        s = str(val_str).strip().replace(" ", "").replace("$", "").replace("\\", "")
        s = s.replace("times", "*").replace("div", "/")
        try:
            s = re.sub(r'frac\{(\d+)\}\{(\d+)\}', r'(\1/\2)', s)
            s = re.sub(r'(?<=\d)\(', r'*(', s)  # NEW [V47.3]: 將 "3(1/2)" 轉為 "3*(1/2)" 避免 eval 視為函式呼叫
            return float(eval(s))
        except:
            return None

    val_u = parse_value(user_answer)
    val_c = parse_value(correct_answer)

    if val_u is not None and val_c is not None:
        if math.isclose(val_u, val_c, rel_tol=1e-7):
            return {"correct": True, "result": "正確"}
    
    u_clean = str(user_answer).strip().replace(" ", "")
    c_clean = str(correct_answer).strip().replace(" ", "")
    if u_clean == c_clean:
        return {"correct": True, "result": "正確"}

    return {"correct": False, "result": f"正確答案: {correct_answer}"}

# [V47.4 跨領域工具組]

def clamp_fraction(fr, max_den=1000, max_num=100000):
    """防止分數爆炸：限制分子分母"""
    if not isinstance(fr, Fraction):
        fr = Fraction(fr)
    if abs(fr.numerator) > max_num or fr.denominator > max_den:
        fr = fr.limit_denominator(max_den)
    return fr

def safe_pow(base, exp, max_abs_exp=10):
    """安全指數運算，避免溢出"""
    if abs(exp) > max_abs_exp:
        return Fraction(0)  # 或其他安全默認
    try:
        if isinstance(base, Fraction) and exp >= 0:
            return Fraction(base.numerator ** exp, base.denominator ** exp)
        elif isinstance(base, Fraction) and exp < 0:
            return Fraction(base.denominator ** (-exp), base.numerator ** (-exp))
        else:
            return Fraction(int(base ** exp), 1)
    except:
        return Fraction(0)

def factorial_bounded(n, max_n=1000):
    """有界階乘"""
    if not (0 <= n <= max_n):
        return None
    result = 1
    for i in range(2, int(n) + 1):
        result *= i
    return result

def nCr(n, r, max_n=5000):
    """組合數 C(n,r)"""
    n, r = int(n), int(r)
    if not (0 <= r <= n <= max_n):
        return None
    if r > n - r:
        r = n - r
    result = 1
    for i in range(r):
        result = result * (n - i) // (i + 1)
    return result

def nPr(n, r, max_n=5000):
    """排列數 P(n,r)"""
    n, r = int(n), int(r)
    if not (0 <= r <= n <= max_n):
        return None
    result = 1
    for i in range(n, n - r, -1):
        result *= i
    return result

def rational_gauss_solve(a, b, p, c, d, q):
    """2x2 線性系統求解器 (用 Fraction)
    a*x + b*y = p
    c*x + d*y = q
    返回 {'x': Fraction, 'y': Fraction} 或 None
    """
    a, b, p, c, d, q = [Fraction(x) for x in [a, b, p, c, d, q]]
    det = a * d - b * c
    if det == 0:
        return None  # 無解或無窮解
    x = (p * d - b * q) / det
    y = (a * q - p * c) / det
    return {'x': x, 'y': y}

def normalize_angle(theta, unit='deg'):
    """角度正規化到 [0, 360) 或 [0, 2π)"""
    theta = float(theta)
    if unit == 'deg':
        theta = theta % 360
        if theta < 0:
            theta += 360
        return theta
    else:  # rad
        theta = theta % (2 * math.pi)
        if theta < 0:
            theta += 2 * math.pi
        return theta

def fmt_set(iterable, braces='{}'):
    """集合顯示：元素使用 fmt_num（不含外層 $）"""
    items = [fmt_num(x) for x in iterable]
    inner = ", ".join(items)
    return ("\\{" + inner + "\\}") if braces == '\\{\\}' else ("{" + inner + "}")

def fmt_interval(a, b, left_open=False, right_open=False):
    """區間顯示：(a,b)、[a,b)、(a,b]、[a,b]；端點使用 fmt_num"""
    l = "(" if left_open else "["
    r = ")" if right_open else "]"
    return f"{l}{fmt_num(a)}, {fmt_num(b)}{r}"

def fmt_vec(*coords):
    """向量顯示：分量使用 fmt_num（不含外層 $）"""
    inner = ", ".join(fmt_num(x) for x in coords)
    return "\\langle " + inner + " \\rangle"

# ✅ 預設的 LaTeX 運算子映射（四則）- 全域可用
op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}


# [AI GENERATED CODE]
# ---------------------------------------------------------


def generate(level=1, **kwargs):
    # [Step 1] 模板選擇
    template = random.choice(['chained_arithmetic_operations', 'distributive_property_arithmetic'])
    
    if template == 'chained_arithmetic_operations':
        num_terms = random.choice([3, 4])
        term_types = [random.choice(['integer', 'fraction', 'decimal', 'mixed_number']) for _ in range(num_terms)]
        operator_choices = [random.choice(['+', '-', '*', '/']) for _ in range(num_terms - 1)]
        parentheses_structure = random.choice(['none', 'first_pair', 'last_pair'])
        allow_negatives = random.choice([True, False])
        
        # [Step 2] 變數生成
        def _rand_num(term_type):
            if term_type == 'integer':
                return Fraction(random.randint(-100, -1) if allow_negatives else 1, 1)
            elif term_type == 'fraction':
                while True:
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(num, den)
            elif term_type == 'decimal':
                while True:
                    num = round(random.uniform(-50.0, -1.0) if allow_negatives else random.uniform(1.0, 50.0), 2)
                    if num != 0:
                        return Fraction(str(num))
            elif term_type == 'mixed_number':
                whole = random.randint(1, 10)
                frac_num = random.randint(-50, 50)
                frac_den = random.randint(2, 15)
                if frac_num != 0 and frac_den != 0:
                    return Fraction(whole * frac_den + frac_num, frac_den)
        
        numbers = [_rand_num(term_type) for term_type in term_types]
        
        # [Step 3] 運算
        def _safe_divide(a, b):
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        
        result = numbers[0]
        if parentheses_structure == 'first_pair':
            result = _safe_divide(numbers[0], numbers[1]) if operator_choices[0] == '/' else (numbers[0] + numbers[1] if operator_choices[0] == '+' else (numbers[0] - numbers[1] if operator_choices[0] == '-' else numbers[0] * numbers[1]))
            result = _safe_divide(result, numbers[2]) if operator_choices[1] == '/' else (result + numbers[2] if operator_choices[1] == '+' else (result - numbers[2] if operator_choices[1] == '-' else result * numbers[2]))
        elif parentheses_structure == 'last_pair':
            result = _safe_divide(numbers[0], numbers[1]) if operator_choices[0] == '/' else (numbers[0] + numbers[1] if operator_choices[0] == '+' else (numbers[0] - numbers[1] if operator_choices[0] == '-' else numbers[0] * numbers[1]))
            result = _safe_divide(result, numbers[2]) if operator_choices[1] == '/' else (result + numbers[2] if operator_choices[1] == '+' else (result - numbers[2] if operator_choices[1] == '-' else result * numbers[2]))
        elif parentheses_structure == 'middle_pair':
            result = _safe_divide(numbers[0], numbers[1]) if operator_choices[0] == '/' else (numbers[0] + numbers[1] if operator_choices[0] == '+' else (numbers[0] - numbers[1] if operator_choices[0] == '-' else numbers[0] * numbers[1]))
            result = _safe_divide(result, numbers[2]) if operator_choices[1] == '/' else (result + numbers[2] if operator_choices[1] == '+' else (result - numbers[2] if operator_choices[1] == '-' else result * numbers[2]))
        else:
            for i in range(1, num_terms):
                if operator_choices[i-1] == '/':
                    result = _safe_divide(result, numbers[i])
                elif operator_choices[i-1] == '+':
                    result += numbers[i]
                elif operator_choices[i-1] == '-':
                    result -= numbers[i]
                else:
                    result *= numbers[i]
        
        # [Step 4] 題幹
        op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
        q_parts = []
        for i in range(num_terms):
            if term_types[i] == 'integer':
                q_parts.append(fmt_num(numbers[i].numerator))
            elif term_types[i] == 'fraction':
                q_parts.append(fmt_num(numbers[i]))
            elif term_types[i] == 'decimal':
                q_parts.append(fmt_num(float(numbers[i])))
            elif term_types[i] == 'mixed_number':
                whole = numbers[i].numerator // numbers[i].denominator
                frac = Fraction(numbers[i].numerator % numbers[i].denominator, numbers[i].denominator)
                q_parts.append(f"{whole} {fmt_num(frac)}")
        
        if parentheses_structure == 'first_pair':
            q = f"({q_parts[0]} {op_latex[operator_choices[0]]} {q_parts[1]}) {op_latex[operator_choices[1]]} {q_parts[2]}"
        elif parentheses_structure == 'last_pair':
            q = f"{q_parts[0]} {op_latex[operator_choices[0]]} ({q_parts[1]} {op_latex[operator_choices[1]]} {q_parts[2]})"
        elif parentheses_structure == 'middle_pair':
            q = f"{q_parts[0]} {op_latex[operator_choices[0]]} ({q_parts[1]} {op_latex[operator_choices[1]]} {q_parts[2]}) {op_latex[operator_choices[2]]} {q_parts[3]}"
        else:
            q = f"{q_parts[0]} {op_latex[operator_choices[0]]} {q_parts[1]} {op_latex[operator_choices[1]]} {q_parts[2]}"
        
        # [Step 5] 清洗
        q = clean_latex_output(q)
        
        # [Step 6] 答案
        a = fmt_num(result)
        
        # [Step 7] 清洗變數名
        if isinstance(a, str) and "=" in a:
            a = a.split("=")[-1].strip()
    
    elif template == 'distributive_property_arithmetic':
        common_factor_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        term1_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        term2_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        middle_operator = random.choice(['+', '-'])
        allow_negatives = random.choice([True, False])
        
        # [Step 2] 變數生成
        def _rand_num(term_type):
            if term_type == 'integer':
                return Fraction(random.randint(-100, -1) if allow_negatives else 1, 1)
            elif term_type == 'fraction':
                while True:
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(num, den)
            elif term_type == 'decimal':
                while True:
                    num = round(random.uniform(-50.0, -1.0) if allow_negatives else random.uniform(1.0, 50.0), 2)
                    if num != 0:
                        return Fraction(str(num))
            elif term_type == 'mixed_number':
                whole = random.randint(1, 10)
                frac_num = random.randint(-50, 50)
                frac_den = random.randint(2, 15)
                if frac_num != 0 and frac_den != 0:
                    return Fraction(whole * frac_den + frac_num, frac_den)
        
        A = _rand_num(common_factor_type)
        B = _rand_num(term1_type)
        C = _rand_num(term2_type)
        
        # [Step 3] 運算
        term1_product = A * B
        term2_product = A * C
        
        if middle_operator == '+':
            result = term1_product + term2_product
        else:
            result = term1_product - term2_product
        
        # [Step 4] 題幹
        op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
        
        if common_factor_type == 'integer':
            A_str = fmt_num(A.numerator)
        elif common_factor_type == 'fraction':
            A_str = fmt_num(A)
        elif common_factor_type == 'decimal':
            A_str = fmt_num(float(A))
        elif common_factor_type == 'mixed_number':
            whole = A.numerator // A.denominator
            frac = Fraction(A.numerator % A.denominator, A.denominator)
            A_str = f"{whole} {fmt_num(frac)}"
        
        if term1_type == 'integer':
            B_str = fmt_num(B.numerator)
        elif term1_type == '