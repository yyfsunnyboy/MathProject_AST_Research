# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: gemini-2.5-flash | Strategy: V44.2 Standard-Template
# Ablation ID: 3 | Env: RTX 5060 Ti 16GB
# Performance: 42.72s | Tokens: In=4436, Out=3401
# Created At: 2026-01-22 15:19:03
# Fix Status: [Repaired] | Fixes: Regex=18, AST=0
# Verification: Internal Logic Check = PASSED
# ==============================================================================


# [INJECTED UTILS]

import random
import math
from fractions import Fraction
import re

# [Research Standard Utils]

def to_latex(num):
    """將數字轉換為 LaTeX 格式 (支援分數、整數、小數)"""
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
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    格式化數字 (標準樣板要求)：
    - signed=True: 強制顯示正負號 (+3, -5)
    - op=True: 用於運算子連接 (自動加空格: " + 3", " - 5")
    - 負數自動加括號
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    
    if op: return f" - {abs_str}" if is_neg else f" + {abs_str}"
    if signed: return f"-{abs_str}" if is_neg else f"+{abs_str}"
    if is_neg: return f"({latex_val})"
    return latex_val

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

def check(user_answer, correct_answer):
    """標準化字串比對批改"""
    if not user_answer: return {"correct": False, "result": "未作答"}
    
    def clean(s):
        return str(s).strip().replace(" ", "").replace("$", "").replace("\\", "").lower()
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    if u == c: return {"correct": True, "result": "正確"}
    
    try:
        if math.isclose(float(eval(u)), float(eval(c)), rel_tol=1e-9):
             return {"correct": True, "result": "正確"}
    except: pass

    return {"correct": False, "result": f"正確答案: {correct_answer}"}


# [AI GENERATED CODE]
# ---------------------------------------------------------


def generate(level=1, **kwargs):
    # 1. 變數定義 (Variable Definitions)
    # 使用常量而非動態範圍, 以避免在循環中重複計算
    VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX = -12, 12
    VAR_MEDIUM_INT_RANGE_MIN, VAR_MEDIUM_INT_RANGE_MAX = -30, 30
    VAR_LARGE_INT_RANGE_MIN, VAR_LARGE_INT_RANGE_MAX = -100, 100
    VAR_FINAL_RESULT_RANGE_MIN, VAR_FINAL_RESULT_RANGE_MAX = -150, 150

    OPERATORS_MD = ['*', '/']
    OPERATORS_AS = ['+', '-']
    # ALL_OPERATORS = ['+', '-', '*', '/'] # Not directly used for choosing modes, but good to define.

    op_to_latex = {
        '*': '\\times',
        '/': '\\div',
        '+': '+',
        '-': '-'
    }

    # 輔助函數: 生成非零整數
    def get_non_zero_int(min_val, max_val):
        num = random.randint(min_val, max_val)
        while num == 0:
            num = random.randint(min_val, max_val)
        return num

    # 輔助函數: 生成整數除法對 (dividend, divisor, quotient)
    def generate_integer_division_pair(max_abs_dividend_target, max_abs_divisor_range, max_abs_quotient_range):
        while True:
            # 1. 隨機選擇一個 divisor (非零)
            divisor = get_non_zero_int(-max_abs_divisor_range, max_abs_divisor_range)

            # 2. 隨機選擇一個 quotient (非零)
            quotient = get_non_zero_int(-max_abs_quotient_range, max_abs_quotient_range)
            
            # 3. 計算 dividend
            dividend = divisor * quotient
            
            # 4. 檢查 abs(dividend) 是否在 max_abs_dividend_target 範圍內
            if abs(dividend) <= max_abs_dividend_target and dividend != 0: # Ensure dividend is also non-zero
                return dividend, divisor, quotient
            # 如果不符合條件, 則重新執行步驟 1-3

    # 運算邏輯 (Operation Logic)
    # 使用 while True 循環以確保生成的問題滿足所有約束條件
    while True:
        # 隨機選擇一個表達式模式
        mode_choice = random.choice(['A.1', 'A.2', 'B.1'])

        q_parts = [] # 用於構建 LaTeX 題目字符串的部分
        final_answer = None # 最終答案

        if mode_choice == 'A.1':  # 模式 A.1: 純乘除鏈 (MD-MD Chain) $N_1 \\ OP_1 \\ N_2 \\ OP_2 \\ N_3$
            # 反向生成, 確保整除和範圍約束
            
            k_final = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
            
            op2_char = random.choice(OPERATORS_MD)
            n3 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
            
            intermediate_val_target = None
            if op2_char == '/':
                intermediate_val_target = k_final * n3
            else: # op2_char == '*'
                # k_final = intermediate_val_target * n3, 故 intermediate_val_target = k_final / n3
                if k_final % n3 != 0:
                    continue # 不可整除則重試
                intermediate_val_target = k_final // n3
            
            # 檢查中間結果是否在 VAR_LARGE_INT_RANGE 內且非零
            if not (VAR_LARGE_INT_RANGE_MIN <= intermediate_val_target <= VAR_LARGE_INT_RANGE_MAX and intermediate_val_target != 0):
                continue

            op1_char = random.choice(OPERATORS_MD)
            n2 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
            
            n1 = None
            if op1_char == '/':
                n1 = intermediate_val_target * n2
            else: # op1_char == '*'
                # intermediate_val_target = n1 * n2, 故 n1 = intermediate_val_target / n2
                if intermediate_val_target % n2 != 0:
                    continue # 不可整除則重試
                n1 = intermediate_val_target // n2
            
            # 檢查 N1 是否在 VAR_LARGE_INT_RANGE 內且非零
            if not (VAR_LARGE_INT_RANGE_MIN <= n1 <= VAR_LARGE_INT_RANGE_MAX and n1 != 0):
                continue
            
            # 最終驗證: 確保 abs(n1) 在 VAR_MEDIUM_INT_RANGE 內 (n2, n3 已從 SMALL_INT_RANGE 生成, 故在 MEDIUM 內)
            if not (VAR_MEDIUM_INT_RANGE_MIN <= n1 <= VAR_MEDIUM_INT_RANGE_MAX):
                continue
            
            # 計算最終答案
            try:
                if op1_char == '*':
                    temp_val = n1 * n2
                else: # '/'
                    temp_val = n1 // n2
                
                if op2_char == '*':
                    final_answer = temp_val * n3
                else: # '/'
                    final_answer = temp_val // n3
            except ZeroDivisionError: # 應避免, 但作為安全措施
                continue

            # 最終答案範圍檢查
            if not (VAR_FINAL_RESULT_RANGE_MIN <= final_answer <= VAR_FINAL_RESULT_RANGE_MAX):
                continue
            
            # 構建題目字符串
            q_parts.append(fmt_num(n1))
            q_parts.append(op_to_latex[op1_char])
            q_parts.append(fmt_num(n2))
            q_parts.append(op_to_latex[op2_char])
            q_parts.append(fmt_num(n3))
            break # 成功生成, 跳出循環

        elif mode_choice == 'A.2':  # 模式 A.2: 加減與乘除混合 (AS-MD Mixed) $N_1 \\ OP_1 \\ N_2 \\ OP_2 \\ N_3$
            # OP1 從 OPERATORS_AS 中選擇, OP2 從 OPERATORS_MD 中選擇
            n1 = get_non_zero_int(VAR_MEDIUM_INT_RANGE_MIN, VAR_MEDIUM_INT_RANGE_MAX)
            op1_char = random.choice(OPERATORS_AS)
            op2_char = random.choice(OPERATORS_MD)

            n2, n3 = None, None
            term_md_val = None # N2 OP2 N3 的結果

            if op2_char == '*':
                n2 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                n3 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                term_md_val = n2 * n3
            else: # op2_char == '/'
                # 使用 generate_integer_division_pair 確保整除
                n2_dividend, n3_divisor, _ = generate_integer_division_pair(
                    VAR_LARGE_INT_RANGE_MAX, # max_abs_dividend_target
                    VAR_SMALL_INT_RANGE_MAX, # max_abs_divisor_range
                    VAR_SMALL_INT_RANGE_MAX  # max_abs_quotient_range
                )
                n2 = n2_dividend
                n3 = n3_divisor
                term_md_val = n2 // n3
            
            # 檢查 (N2 OP2 N3) 的絕對值是否在 VAR_LARGE_INT_RANGE 內且非零
            if not (VAR_LARGE_INT_RANGE_MIN <= term_md_val <= VAR_LARGE_INT_RANGE_MAX and term_md_val != 0):
                continue

            # 計算最終答案 (注意運算順序: 先乘除後加減)
            try:
                if op1_char == '+':
                    final_answer = n1 + term_md_val
                else: # '-'
                    final_answer = n1 - term_md_val
            except ZeroDivisionError:
                continue

            # 最終答案範圍檢查
            if not (VAR_FINAL_RESULT_RANGE_MIN <= final_answer <= VAR_FINAL_RESULT_RANGE_MAX):
                continue
            
            # 構建題目字符串
            q_parts.append(fmt_num(n1))
            q_parts.append(op_to_latex[op1_char])
            q_parts.append(fmt_num(n2))
            q_parts.append(op_to_latex[op2_char])
            q_parts.append(fmt_num(n3))
            break # 成功生成, 跳出循環

        elif mode_choice == 'B.1':  # 模式 B.1: 四項三運算 (MD-AS-MD Mixed) $N_1 \\ OP_1 \\ N_2 \\ OP_2 \\ N_3 \\ OP_3 \\ N_4$
            # OP1 從 OPERATORS_MD 中選擇, OP2 從 OPERATORS_AS 中選擇, OP3 從 OPERATORS_MD 中選擇
            
            # 生成第一個乘除項 (term1_val = N1 OP1 N2)
            n1, n2 = None, None
            op1_char = random.choice(OPERATORS_MD)
            term1_val = None

            if op1_char == '*':
                n1 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                n2 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                term1_val = n1 * n2
            else: # op1_char == '/'
                n1_dividend, n2_divisor, _ = generate_integer_division_pair(
                    VAR_LARGE_INT_RANGE_MAX, VAR_SMALL_INT_RANGE_MAX, VAR_SMALL_INT_RANGE_MAX)
                n1 = n1_dividend
                n2 = n2_divisor
                term1_val = n1 // n2
            
            # 檢查 term1_val 是否在 VAR_LARGE_INT_RANGE 內且非零
            if not (VAR_LARGE_INT_RANGE_MIN <= term1_val <= VAR_LARGE_INT_RANGE_MAX and term1_val != 0):
                continue

            # 生成第二個乘除項 (term2_val = N3 OP3 N4)
            n3, n4 = None, None
            op3_char = random.choice(OPERATORS_MD)
            term2_val = None

            if op3_char == '*':
                n3 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                n4 = get_non_zero_int(VAR_SMALL_INT_RANGE_MIN, VAR_SMALL_INT_RANGE_MAX)
                term2_val = n3 * n4
            else: # op3_char == '/'
                n3_dividend, n4_divisor, _ = generate_integer_division_pair(
                    VAR_LARGE_INT_RANGE_MAX, VAR_SMALL_INT_RANGE_MAX, VAR_SMALL_INT_RANGE_MAX)
                n3 = n3_dividend
                n4 = n4_divisor
                term2_val = n3 // n4
            
            # 檢查 term2_val 是否在 VAR_LARGE_INT_RANGE 內且非零
            if not (VAR_LARGE_INT_RANGE_MIN <= term2_val <= VAR_LARGE_INT_RANGE_MAX and term2_val != 0):
                continue

            op2_char = random.choice(OPERATORS_AS)

            # 計算最終答案 (注意運算順序: 先乘除後加減)
            try:
                if op2_char == '+':
                    final_answer = term1_val + term2_val
                else: # '-'
                    final_answer = term1_val - term2_val
            except ZeroDivisionError:
                continue

            # 最終答案範圍檢查
            if not (VAR_FINAL_RESULT_RANGE_MIN <= final_answer <= VAR_FINAL_RESULT_RANGE_MAX):
                continue

            # 構建題目字符串
            q_parts.append(fmt_num(n1))
            q_parts.append(op_to_latex[op1_char])
            q_parts.append(fmt_num(n2))
            q_parts.append(op_to_latex[op2_char])
            q_parts.append(fmt_num(n3))
            q_parts.append(op_to_latex[op3_char])
            q_parts.append(fmt_num(n4))
            break # 成功生成, 跳出循環

    # 4. 輸出格式 (Output Format)
    q = f"${' '.join(q_parts)}$"
    a = final_answer

    # 格式潔癖 (Sanitization)
    if isinstance(q, str):
        q = re.sub(r'^計算下列.*[: :]?', '', q).strip()
        q = re.sub(r'^\(?\d+[\)）]\.?\s*', '', q).strip()
    if isinstance(a, str):
        if "=" in a: a = a.split("=")[-1].strip()
    
    return {
        'question_text': q, 
        'correct_answer': a, 
        'answer': a,
        'mode': 1
    }