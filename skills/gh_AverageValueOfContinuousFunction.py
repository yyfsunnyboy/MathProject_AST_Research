import random
from fractions import Fraction
import math

def format_polynomial(coeffs_dict, var='x'):
    """
    格式化多項式字符串，支援 LaTeX 格式。
    coeffs_dict: 字典 {power: coefficient}，例如 {2: 1, 1: -6, 0: 10} 代表 x^2 - 6x + 10。
    var: 變量名稱，預設為 'x'。
    """
    terms = []
    sorted_powers = sorted(coeffs_dict.keys(), reverse=True)

    for power in sorted_powers:
        coeff = coeffs_dict[power]
        if coeff == 0:
            continue

        coeff_str = ""
        # 處理係數前的符號和數字
        if power > 0: # 非常數項
            if abs(coeff) != 1:
                coeff_str = str(coeff)
            elif coeff == -1:
                coeff_str = "-"
        else: # 常數項
            coeff_str = str(coeff)

        # 組合項
        if power > 0:
            if power == 1:
                term_str = f"{coeff_str}{var}"
            else:
                term_str = f"{coeff_str}{var}^{{{{ {power} }}}}" # LaTeX 指數用雙括號
        else: # 常數項
            term_str = coeff_str

        # 添加 '+' 符號
        if coeff > 0 and len(terms) > 0:
            terms.append(f"+{term_str}")
        else:
            terms.append(term_str)
        
    if not terms:
        return "0" # 如果所有係數都為0，則多項式為0
    
    # 清理開頭的 '+'
    if terms[0].startswith('+') and len(terms[0]) > 1:
        terms[0] = terms[0][1:]
    
    return "".join(terms).replace("+-", "-") # 替換 "+-" 為 "-"

def generate_linear_function_problem():
    """
    生成線性函數 $f(x) = Ax + B$ 的平均值問題。
    此類型問題的 $c$ 值總是區間中點，易於求解。
    """
    # 確保 A 不為 0
    A = random.choice([-3, -2, -1, 1, 2, 3])
    B = random.randint(-10, 10)
    a = random.randint(-5, 0)
    b = random.randint(a + 3, a + 8) # 確保 b > a，且區間足夠寬

    # 函數字符串
    f_x_str = format_polynomial({1: A, 0: B}, 'x')

    # 計算平均值 h
    # 定積分 ∫(Ax+B)dx = A/2 x^2 + Bx
    # h = (1/(b-a)) * [ (A/2 b^2 + Bb) - (A/2 a^2 + Ba) ]
    # h = (1/(b-a)) * [ A/2 (b^2-a^2) + B(b-a) ]
    # h = A/2 (b+a) + B
    integral_val = Fraction(A * (b**2 - a**2), 2) + Fraction(B * (b - a), 1)
    h = integral_val / (b - a)

    # 對於線性函數 $f(x)=Ax+B$，滿足 $f(c)=h$ 的 $c$ 值總是區間中點 $(a+b)/2$
    c_val = Fraction(a + b, 2)

    question_text = (
        f"設函數 $f(x) = {f_x_str}$。<br>"
        f"(1)求 $f(x)$ 在區間 $[{a}, {b}]$ 內函數值的平均 $h$。<br>"
        f"(2)已知 $c \\in [{a}, {b}]$，且 $f(c) = h$，求 $c$ 的值。"
    )
    
    correct_answer_part1 = str(h)
    correct_answer_part2 = str(c_val)
    
    # 答案以逗號分隔，Part(1) 答案在前，Part(2) 答案在後
    correct_answer = f"{correct_answer_part1}, {correct_answer_part2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_quadratic_function_problem():
    """
    生成二次函數 $f(x) = Ax^2 + Bx + C$ 的平均值問題。
    此函數會透過迭代確保 $f(c)=h$ 具有整數或簡單分數解，並在區間內。
    """
    attempts = 0
    max_attempts = 100 # 最多嘗試次數，避免無限迴圈

    while attempts < max_attempts:
        A = random.choice([-2, -1, 1, 2]) # 二次項係數
        B = random.choice([-3, -2, -1, 1, 2, 3]) # 一次項係數
        C = random.randint(-10, 10) # 常數項
        a = random.randint(-3, 1) # 區間左端點
        b = random.randint(a + 3, a + 7) # 區間右端點，確保 b > a 且區間足夠寬

        # 函數字符串
        f_x_str = format_polynomial({2: A, 1: B, 0: C}, 'x')

        # 計算平均值 h
        # 定積分 ∫(Ax^2+Bx+C)dx = A/3 x^3 + B/2 x^2 + Cx
        integral_val = (Fraction(A, 3) * (b**3 - a**3) +
                        Fraction(B, 2) * (b**2 - a**2) +
                        Fraction(C, 1) * (b - a))
        h = integral_val / (b - a)

        # 求解 $f(c) = h$ => $Ac^2 + Bc + C = h$ => $Ac^2 + Bc + (C - h) = 0$
        # $A_{quad}c^2 + B_{quad}c + C_{quad} = 0$
        A_quad = A
        B_quad = B
        C_quad = C - h # C_quad 可能是分數

        # 為了使用二次公式並確保整數運算，將係數轉為整數
        # 乘以分母的最小公倍數 (此處 C_quad 分母即為最小公倍數)
        den = C_quad.denominator
        A_coeff = A_quad * den
        B_coeff = B_quad * den
        C_coeff = C_quad.numerator

        # 計算判別式 D = B^2 - 4AC
        discriminant = B_coeff**2 - 4 * A_coeff * C_coeff

        if discriminant < 0: # 無實數解
            attempts += 1
            continue

        sqrt_discriminant = int(math.sqrt(discriminant))

        if sqrt_discriminant * sqrt_discriminant == discriminant: # 判別式為完全平方數，有整數或簡單分數解
            # 計算兩個根 c1, c2
            c1_num = -B_coeff + sqrt_discriminant
            c2_num = -B_coeff - sqrt_discriminant
            den_c = 2 * A_coeff

            c1 = Fraction(c1_num, den_c)
            c2 = Fraction(c2_num, den_c)

            # 過濾在區間 [a, b] 內的根
            valid_c_roots = []
            # 使用 float() 進行區間檢查，因為 Fraction 可能導致比較誤差
            if float(a) <= float(c1) <= float(b):
                valid_c_roots.append(c1)
            # 避免重複添加相同的根 (例如判別式為0時)
            if float(a) <= float(c2) <= float(b) and c2 != c1: 
                valid_c_roots.append(c2)
            
            if len(valid_c_roots) > 0: # 找到至少一個有效根
                # 將有效根轉換為字符串並排序，以便答案檢查
                valid_c_roots_str = sorted([str(r) for r in valid_c_roots], key=lambda x: Fraction(x))
                correct_answer_part2 = ", ".join(valid_c_roots_str)

                question_text = (
                    f"設函數 $f(x) = {f_x_str}$。<br>"
                    f"(1)求 $f(x)$ 在區間 $[{a}, {b}]$ 內函數值的平均 $h$。<br>"
                    f"(2)已知 $c \\in [{a}, {b}]$，且 $f(c) = h$，求 $c$ 的值。"
                )
                
                correct_answer_part1 = str(h)
                correct_answer = f"{correct_answer_part1}, {correct_answer_part2}"

                return {
                    "question_text": question_text,
                    "answer": correct_answer,
                    "correct_answer": correct_answer
                }
        attempts += 1
    
    # 如果經過多次嘗試仍未能生成符合條件的二次函數問題，則回退到線性函數問題
    return generate_linear_function_problem()

def generate(level=1):
    """
    根據難度等級生成連續函數平均值問題。
    level 1 優先生成線性函數問題，確保簡單。
    level > 1 隨機生成線性或二次函數問題。
    """
    if level == 1:
        return generate_linear_function_problem()
    else:
        problem_type = random.choice(['linear', 'quadratic'])
        if problem_type == 'linear':
            return generate_linear_function_problem()
        else:
            return generate_quadratic_function_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    user_answer 和 correct_answer 預期為以逗號分隔的字符串，格式為 "h_val, c_val1, c_val2..."
    """
    user_parts = [p.strip() for p in user_answer.split(',')]
    correct_parts = [p.strip() for p in correct_answer.split(',')]

    is_correct = True
    feedback_messages = []

    if len(user_parts) != len(correct_parts):
        is_correct = False
        feedback_messages.append(f"答案格式不正確。應包含 {len(correct_parts)} 個值（h 值和 c 值），以逗號分隔。")
        result_text = "<br>".join(feedback_messages)
        return {"correct": is_correct, "result": result_text, "next_question": False}

    # 檢查 Part (1) 的 h 值
    try:
        user_h = Fraction(user_parts[0])
        correct_h = Fraction(correct_parts[0])
        if user_h == correct_h:
            feedback_messages.append(f"第(1)小題答案：$h={user_h}$ 正確。")
        else:
            feedback_messages.append(f"第(1)小題答案：$h={user_h}$ 不正確。正確答案應為 $h={correct_h}$。")
            is_correct = False
    except (ValueError, ZeroDivisionError):
        feedback_messages.append(f"第(1)小題答案 '{user_parts[0]}' 格式不正確。請輸入數字或分數。")
        is_correct = False

    # 檢查 Part (2) 的 c 值（可能有多個）
    if len(user_parts) > 1:
        try:
            user_c_vals = sorted([Fraction(p) for p in user_parts[1:]])
            correct_c_vals = sorted([Fraction(p) for p in correct_parts[1:]])

            if user_c_vals == correct_c_vals:
                feedback_messages.append(f"第(2)小題答案：$c={', '.join([str(f) for f in user_c_vals])}$ 正確。")
            else:
                feedback_messages.append(f"第(2)小題答案：$c={', '.join([str(f) for f in user_c_vals])}$ 不正確。正確答案應為 $c={', '.join([str(f) for f in correct_c_vals])}$。")
                is_correct = False
        except (ValueError, ZeroDivisionError):
            feedback_messages.append(f"第(2)小題答案 '{', '.join(user_parts[1:])}' 格式不正確。請輸入數字或分數。")
            is_correct = False

    result_text = "<br>".join(feedback_messages)
    return {"correct": is_correct, "result": result_text, "next_question": True}