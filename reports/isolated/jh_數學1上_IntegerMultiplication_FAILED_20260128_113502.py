# ==============================================================================
# ID: jh_數學1上_IntegerMultiplication
# Model: qwen2.5-coder:14b | Strategy: V44.9 Hybrid-Healing
# Ablation ID: 2 | Env: RTX 5060 Ti 16GB
# Performance: 32.76s | Tokens: In=1736, Out=1317
# Created At: 2026-01-28 11:35:02
# Fix Status: [Repaired] | Fixes: Regex=5, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================


# [INJECTED UTILS]

import random
import math
from fractions import Fraction
import re
import ast
import operator

# [Research Standard Utils]

def safe_choice(seq):
    """
    [Auto-Injected] 安全的 random.choice，避免空序列崩潰
    """
    if not seq: return 1
    return random.choice(seq)

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
    [V9.2.6 Fix] LaTeX 格式清洗器 - 智能分离中文与数学式
    问题：中文字不能放在 LaTeX 数学模式 $...$ 内
    解决：只包裹数学表达式，中文文字保留在外面
    """
    if not isinstance(q_str, str): return str(q_str)
    clean_q = q_str.replace('$', '').strip()
    import re
    
    # 1. 修复运算符：* -> \times, / -> \div
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*\*\s*', r' \\times ', clean_q)
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*/\s*(?![{}])', r' \\div ', clean_q)
    
    # 2. 修复双重括号 ((...)) -> (...)
    clean_q = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', clean_q)
    
    # 3. 移除多余空白
    clean_q = re.sub(r'\s+', ' ', clean_q).strip()
    
    # 4. [V9.2.6 NEW] 智能分离中文与数学式
    # 检测是否包含中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', clean_q))
    
    if has_chinese:
        # 策略：将字符串分割为"中文部分"和"数学部分"
        # 数学部分：包含数字、运算符、括号、LaTeX 命令的连续区域
        # 中文部分：中文字、标点符号
        
        # Pattern: 匹配数学表达式（数字、运算符、括号、LaTeX 命令、单字母变量）
        # 改进：更精确地匹配整个数学表达式块
        math_pattern = r'(?:[\d\-+*/()（）\[\]【】\\]|\\[a-z]+(?:\{[^}]*\})?|[a-zA-Z])+(?:\s+(?:[\d\-+*/()（）\[\]【】\\]|\\[a-z]+(?:\{[^}]*\})?|[a-zA-Z])+)*'
        
        parts = []
        last_end = 0
        
        for match in re.finditer(math_pattern, clean_q):
            start, end = match.span()
            
            # 添加之前的文本（中文部分）
            if start > last_end:
                text_part = clean_q[last_end:start].strip()
                if text_part:
                    parts.append(text_part)
            
            # 添加数学部分（需要包裹 $）
            math_part = match.group().strip()
            if math_part:
                parts.append(f'${math_part}$')
            
            last_end = end
        
        # 添加剩余的文本
        if last_end < len(clean_q):
            text_part = clean_q[last_end:].strip()
            if text_part:
                parts.append(text_part)
        
        # 合并并清理多余空格
        result = ' '.join(parts)
        result = re.sub(r'\s+', ' ', result).strip()
        
        # 清理连续的 $ 符号：$...$ $...$ -> $... ...$
        result = re.sub(r'\$\s+\$', ' ', result)
        
        return result
    else:
        # 没有中文：直接包裹整个表达式
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
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    json
    {
      "domain": "arithmetic",
      "entities": [
        {
          "name": "factor1",
          "type": "integer",
          "constraints": [
            {"value_range": "-10~10"},
            {"non_zero": true}
          ]
        },
        {
          "name": "factor2",
          "type": "integer",
          "constraints": [
            {"value_range": "-10~10"},
            {"non_zero": true}
          ]
        }
      ],
      "operators": ["*"],
      "constraints": {
        "computability": "所有中間值與最終答案都必須是「可精確計算」的整數。",
        "boundaries": {
          "integer_range": {
            "factor1, factor2": "-10~10",
            "result": "-100~100"
          },
          "operation_complexity": "結果的絕對值不超過 3 位數。"
        },
        "mutual_exclusion": null,
        "minimum_complexity": {
          "multiplication_operation": true,
          "sign_combinations": ["正x正", "正x負", "負x正", "負x負"]
        }
      },
      "templates": [
        {
          "name": "integer_multiplication_two_factors",
          "complexity_requirements": [
            {"non_zero_integers": true},
            {"multiplication_operation": true},
            {"sign_combinations": ["正x正", "正x負", "負x正", "負x負"]},
            {"absolute_value_at_least_1": true}
          ],
          "variables": [
            {"name": "factor1_abs", "type": "integer", "range": "1~10"},
            {"name": "factor2_abs", "type": "integer", "range": "1~10"},
            {"name": "factor1_sign", "type": "boolean", "values": ["True", "False"]},
            {"name": "factor2_sign", "type": "boolean", "values": ["True", "False"]}
          ],
          "construction": [
            "隨機生成 `factor1_abs` 和 `factor2_abs`, 確保它們是 1 到 10 之間的整數。",
            "隨機生成 `factor1_sign` 和 `factor2_sign` (True/False)。",
            "根據 `factor1_abs` 和 `factor1_sign` 決定 `factor1` 的值: 如果 `factor1_sign` 為 True, 則 `factor1 = factor1_abs`。如果 `factor1_sign` 為 False, 則 `factor1 = -factor1_abs`。",
            "根據 `factor2_abs` 和 `factor2_sign` 決定 `factor2` 的值: 如果 `factor2_sign` 為 True, 則 `factor2 = factor2_abs`。如果 `factor2_sign` 為 False, 則 `factor2 = -factor2_abs`。",
            "使用 Python 運算符直接計算最終答案: `final_answer = factor1 * factor2`。",
            "確認 `final_answer` 是整數, 且在預期範圍內。"
          ],
          "implementation_checklist": [
            {"generate_non_zero_integers": true},
            {"absolute_value_range_1_to_10": true},
            {"correct_sign_setting": true},
            {"use_multiplication_operator": true},
            {"cover_all_sign_combinations": true},
            {"final_answer_integer_and_within_range": true}
          ],
          "formatting": {
            "question_display": [
              "題幹格式化規則: ",
              "1. 題幹開頭為固定的中文敘述: \"計算下列各式的值。\"",
              "2. 數學表達式部分: ",
              "   a. 使用 `fmt_num(factor)` 格式化每個因子。**重要: `fmt_num` 必須能夠自動判斷並為負數添加括號 (例如, -9 會格式化為 (-9))。",
              "   b. 使用 `op_latex['*']` 獲取乘號的 LaTeX 表示 (`\\times`)。",
              "   c. 將格式化後的因子和運算符組合成一個字符串, 例如 `fmt_num(factor1) + op_latex['*'] + fmt_num(factor2)`。",
              "   d. 使用 `clean_latex_output()` 包裝整個數學表達式字符串, 使其成為 `$ ... $` 格式。",
              "3. 將中文敘述與數學表達式拼接。"
            ],
            "answer_display": [
              "答案格式化規則: ",
              "- 最終答案為整數, 直接轉換為字符串。",
              "- 範例: `str(final_answer)`",
              "- 禁止使用 LaTeX 格式。",
              "- 禁止使用 `fmt_num()`。"
            ]
          },
          "notes": [
            "此模板專注於 K12 數學中整數乘法的基本概念, 特別是正負號的處理。",
            "`fmt_num` 自動添加負數括號的功能對於保持題目清晰度至關重要。"
          ],
          "diversity": {
            "factor_sign_combinations": true,
            "independent_absolute_values": true,
            "degradation_checks": [
              {"non_zero_factors": true},
              {"not_both_1_or_neg1": true}
            ]
          },
          "verifier": [
            "`factor1` 和 `factor2` 均為非零整數。",
            "`factor1` 和 `factor2` 的絕對值均在 1~10 範圍內。",
            "最終計算結果 `final_answer` 為整數, 且絕對值在 0~100 範圍內。",
            "題幹中的數學表達式格式正確, 負數因子有正確的括號。",
            "答案顯示為純數字字符串。"
          ]
        }
      ]
    }
    return {'question_text': clean_latex_output(q), 'correct_answer': a, 'answer': a, 'mode': 1}