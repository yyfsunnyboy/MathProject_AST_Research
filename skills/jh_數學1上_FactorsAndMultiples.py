# ==============================================================================
# ID: jh_數學1上_FactorsAndMultiples
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 124.52s | RAG: 4 examples
# Created At: 2025-12-31 23:43:35
# Fix Status: [Clean Pass]
# ==============================================================================

import random
from fractions import Fraction

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")

def generate_factor_problem():
    # 產生一個正整數，其因數由小到大排列為 1, 2, 3, a, 6, b, 15, M
    # 要求學生找出 a 和 b 的值
    # 因數排列為 1, 2, 3, a, 6, b, 15, M
    # 所以 M = 15 × something = 15 × 2 = 30（因為 15 是最大因數）
    # 因此 M = 30，且因數為 1, 2, 3, 5, 6, 10, 15, 30
    # 所以 a = 5, b = 10
    
    # 為了增加變化，我們隨機選擇一個數字，並找出其因數
    num = random.choice([30, 36, 42, 48, 54, 60])
    
    factors = []
    for i in range(1, int(num**0.5)+1):
        if num % i == 0:
            factors.append(i)
            if i != num // i:
                factors.append(num // i)
    factors.sort()
    
    # 假設我們知道因數的排列方式，例如 1, 2, 3, a, 6, b, 15, M
    # 所以我們要找出 a 和 b 的值
    if len(factors) >= 8:
        # 假設因數為 1, 2, 3, a, 6, b, 15, M
        # 因此 a = factors[3], b = factors[5], M = factors[7]
        a = factors[3]
        b = factors[5]
        M = factors[7]
        return {
            'question_text': f'有一正整數 $N$ 的所有因數由小到大排列為 $1, 2, 3, a, 6, b, 15, N$，則 $a$、$b$ 的值為何？',
            'answer': f'a = {a}, b = {b}',
            'correct_answer': f'a = {a}, b = {b}'
        }
    else:
        # 如果因數少於 8 個，則重新生成
        return generate_factor_problem()

def generate_app_problem():
    # 產生應用題
    num = random.choice([30, 36, 42, 48, 54, 60])
    
    factors = []
    for i in range(1, int(num**0.5)+1):
        if num % i == 0:
            factors.append(i)
            if i != num // i:
                factors.append(num // i)
    factors.sort()
    
    # 隨機選擇兩個因數
    a, b = random.sample(factors, 2)
    
    return {
        'question_text': f'請問 $36$ 的所有因數中，小於 $10$ 的因數有哪幾個？',
        'answer': ', '.join([str(f) for f in factors if f < 10]),
        'correct_answer': ', '.join([str(f) for f in factors if f < 10])
    }

def generate_calc_problem():
    # 產生基本計算題
    val_a = random.randint(-10, -1)
    val_b = random.randint(-10, 10)
    
    # 混合絕對值
    if random.random() < 0.3: 
        return {
            'question_text': f'請計算 $|{val_a}| + {fmt_num(val_b)}$ 的值為何？', 
            'answer': str(abs(val_a)+val_b), 
            'correct_answer': str(abs(val_a)+val_b)
        }
    
    # 標準計算
    ans = val_a + val_b 
    return {
        'question_text': f'請計算 ${fmt_num(val_a)} + {fmt_num(val_b)}$ 的值為何？', 
        'answer': str(ans), 
        'correct_answer': str(ans)
    }

def generate(level=1):
    type = random.choice(['calc', 'app', 'factor'])
    if type == 'calc': 
        return generate_calc_problem()
    elif type == 'factor':
        return generate_factor_problem()
    else: 
        return generate_app_problem()