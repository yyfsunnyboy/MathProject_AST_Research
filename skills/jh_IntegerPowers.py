import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「整數乘方」相關題目。
    包含：
    1. 將連乘式簡記為指數形式。
    2. 計算基本乘方值 (正底數、負底數含括號、負底數不含括號)。
    3. 探討負數奇偶次方。
    4. 將乘方融入四則運算。
    """
    problem_type = random.choice([
        'simplify_to_exponent',
        'calculate_basic_power',
        'calculate_negative_power',
        'order_of_operations_problem'
    ])

    if problem_type == 'simplify_to_exponent':
        return generate_simplify_to_exponent_problem(level)
    elif problem_type == 'calculate_basic_power':
        return generate_calculate_basic_power_problem(level)
    elif problem_type == 'calculate_negative_power':
        return generate_calculate_negative_power_problem(level)
    else: # 'order_of_operations_problem'
        return generate_order_of_operations_problem(level)

def generate_simplify_to_exponent_problem(level):
    """
    生成將連乘式簡記為指數形式的題目。
    例如：8*8*8*8*8 = 8^5
          (-5)*(-5)*(-5)*(-5) = (-5)^4
    """
    base = random.randint(2, 9)
    exponent = random.randint(3, 6) # 指數至少為3，確保簡記有意義

    # 隨機決定底數是否為負數
    if random.random() < 0.4:
        base *= -1

    product_parts = []
    for _ in range(exponent):
        if base < 0:
            product_parts.append(f"({base})") # 負數底數用括號包起來
        else:
            product_parts.append(str(base))
    
    product_string = r" \\times ".join(product_parts)

    question_text = f"以指數的形式簡記下列各式。<br>${product_string} = ?$"

    # `answer` 欄位將直接儲存 LaTeX 格式的正確答案字串，供 `check` 函數比對與顯示
    if base < 0:
        answer_latex = f"$({base})^{{{exponent}}}$"
    else:
        answer_latex = f"${base}^{{{exponent}}}$"
    
    return {
        "question_text": question_text,
        "answer": answer_latex, # 用於比對的標準答案 (LaTeX 格式)
        "correct_answer": answer_latex # 用於顯示的正確答案 (LaTeX 格式)
    }

def generate_calculate_basic_power_problem(level):
    """
    生成計算基本乘方值的題目。
    例如：$3^2$, $(-3)^2$, $-3^2$
    """
    base_val = random.randint(2, 6) # 底數值保持較小，結果易於計算
    exponent_val = random.randint(2, 4) # 指數值保持較小

    # 決定問題形式：正底數、負底數含括號、正底數的負乘方
    problem_forms = ['pos_base', 'neg_paren_base', 'neg_of_pos_base']
    problem_form = random.choice(problem_forms)

    question_latex = ""
    result = 0

    if problem_form == 'pos_base':
        # 例如：$3^2$
        question_latex = f"${base_val}^{{{exponent_val}}}$"
        result = base_val ** exponent_val
    elif problem_form == 'neg_paren_base':
        # 例如：$(-3)^2$
        question_latex = f"$(-{base_val})^{{{exponent_val}}}$"
        result = (-base_val) ** exponent_val
    else: # neg_of_pos_base
        # 例如：$-3^2$ (相當於 $-(3^2)$)
        question_latex = f"$-{base_val}^{{{exponent_val}}}$"
        result = -(base_val ** exponent_val)

    question_text = f"計算下列各式的值。<br>{question_latex}"
    
    return {
        "question_text": question_text,
        "answer": str(result), # 標準答案 (數值字串)
        "correct_answer": str(result) # 顯示答案 (數值字串)
    }

def generate_calculate_negative_power_problem(level):
    """
    生成計算負底數乘方值的題目，強調奇偶次方的影響。
    例如：$(-6)^3$, $-6^3$
    """
    base_val = random.randint(2, 5)
    exponent_val = random.choice([2, 3, 4, 5]) # 混合奇偶數指數

    problem_forms = [
        'neg_paren_even', # $(-a)^{even}$
        'neg_paren_odd',  # $(-a)^{odd}$
        'neg_of_pos'      # $-a^{exponent}$ (底數為正，再取負號)
    ]
    problem_form = random.choice(problem_forms)

    question_latex = ""
    result = 0

    if problem_form == 'neg_paren_even':
        # 確保指數為偶數
        if exponent_val % 2 != 0: 
            exponent_val += 1
        question_latex = f"$(-{base_val})^{{{exponent_val}}}$"
        result = (-base_val) ** exponent_val
    elif problem_form == 'neg_paren_odd':
        # 確保指數為奇數
        if exponent_val % 2 == 0:
            exponent_val += 1
        question_latex = f"$(-{base_val})^{{{exponent_val}}}$"
        result = (-base_val) ** exponent_val
    else: # neg_of_pos
        # $-a^{exponent}$，無論指數奇偶，結果皆為負數（假設 $a > 0$）
        question_latex = f"$-{base_val}^{{{exponent_val}}}$"
        result = -(base_val ** exponent_val)

    question_text = f"計算下列各式的值。<br>{question_latex}"
    return {
        "question_text": question_text,
        "answer": str(result),
        "correct_answer": str(result)
    }

def generate_order_of_operations_problem(level):
    """
    生成包含乘方的四則運算題目。
    例如：($ -5^2 $)$\\div$5$-3^3$ 或 8$-2^3\\times$[ 10$+$($-4^2$) ]
    """
    problem_structure = random.choice(['type1', 'type2_simple']) 

    question_latex = ""
    expression_for_eval = ""
    correct_value = 0

    if problem_structure == 'type1':
        # 結構類似：(Power_Term) Op1 Number Op2 (Power_Term)
        # 例如：($ -5^2 $)$\\div$5$-3^3$

        # 第一個項：乘方表達式
        base_a = random.randint(2, 5)
        exp_a = random.randint(2, 3)
        term_a_form = random.choice(['neg_of_pos', 'pos_paren_neg']) 

        if term_a_form == 'neg_of_pos':
            term_a_str_latex_display = f"$-{base_a}^{{{exp_a}}}$"
            val_a = -(base_a ** exp_a)
        else: # pos_paren_neg
            val_a = (-base_a) ** exp_a
            term_a_str_latex_display = f"$(-{base_a})^{{{exp_a}}}$"

        # 第一個運算符
        op1_latex = random.choice([r"\\div", r"\\times"])
        op1_eval = '/' if op1_latex == r"\\div" else '*'

        # 第二個項：簡單數字 (用於除法或乘法)
        val_b_raw = random.randint(2, 5)
        if op1_eval == '/':
            # 確保被除數 val_a 可以被 val_b 整除，避免小數結果
            if val_a == 0: 
                val_a = random.choice([4, 6, 8, 10]) # 如果 val_a 為 0，重新賦值以避免 0/X
            if val_a % val_b_raw != 0:
                # 調整 val_a 為 val_b_raw 的倍數
                val_a = val_b_raw * random.randint(-5, 5) 
                while val_a == 0: # 避免調整後 val_a 仍為 0
                    val_a = val_b_raw * random.randint(-5, 5)
                # 若 val_a 被調整，顯示時簡化為數字而非乘方形式
                term_a_str_latex_display = f"({val_a})" if val_a < 0 else f"{val_a}"
        elif op1_eval == '*':
            if random.random() < 0.3: # 乘數可能為負
                val_b_raw *= -1
        
        val_b = val_b_raw 

        term_b_str_latex_display = f"({val_b})" if val_b < 0 else f"{val_b}"

        # 第二個運算符
        op2_latex = random.choice(['+', '-'])
        op2_eval = op2_latex

        # 第三個項：另一個乘方表達式
        base_c = random.randint(2, 4)
        exp_c = random.randint(2, 3)
        term_c_form = random.choice(['neg_of_pos', 'pos']) 

        if term_c_form == 'neg_of_pos':
            term_c_str_latex_display = f"$-{base_c}^{{{exp_c}}}$"
            val_c = -(base_c ** exp_c)
        else: # pos
            val_c = base_c ** exp_c
            term_c_str_latex_display = f"${base_c}^{{{exp_c}}}$"

        # 組合 LaTeX 顯示字串
        question_latex = f"($ {term_a_str_latex_display} $){op1_latex}{term_b_str_latex_display}{op2_latex}{term_c_str_latex_display}"
        # 組合 Python eval 用的字串
        expression_for_eval = f"({val_a}){op1_eval}({val_b}){op2_eval}({val_c})"

    elif problem_structure == 'type2_simple':
        # 結構類似：Number Op1 Power_Term * ( Number Op2 Power_Term )
        # 例如：8 $-2^3\\times$[ 10$+$($-4^2$) ] (簡化為 round brackets)
        
        # 第一個數字
        num1 = random.randint(5, 15)

        # 第一個運算符
        op1_latex = random.choice(['+', '-'])
        op1_eval = op1_latex

        # 乘方項
        base_power = random.randint(2, 4)
        exp_power = random.randint(2, 3)
        power_val = base_power ** exp_power
        power_latex_display = f"${base_power}^{{{exp_power}}}$"

        # 括號內的第一個數字
        num2 = random.randint(5, 10)
        inner_op_latex = random.choice(['+', '-'])
        inner_op_eval = inner_op_latex

        # 括號內的乘方項
        inner_base_power = random.randint(2, 4)
        inner_exp_power = random.randint(2, 3)
        
        # 通常設定為負數乘方，以符合例題風格
        inner_power_val = -(inner_base_power ** inner_exp_power) 
        inner_power_latex_display = f"$(-{inner_base_power}^{{{inner_exp_power}}})$" # 顯示時額外括號，強調操作順序
        
        # 預先評估括號內的結果，並檢查是否超出合理範圍
        temp_inner_eval = f"{num2}{inner_op_eval}({inner_power_val})"
        inner_expression_result = eval(temp_inner_eval)
        
        # 設定結果範圍，避免數值過大或過小
        if abs(inner_expression_result) > 20 or abs(power_val * inner_expression_result) > 300:
            return generate_order_of_operations_problem(level) # 若超出範圍，重新生成

        # 組合 LaTeX 顯示字串
        question_latex = f"${num1}{op1_latex}{power_latex_display}{r'\\times'} ( {num2}{inner_op_latex}{inner_power_latex_display} ) $"
        # 組合 Python eval 用的字串
        expression_for_eval = f"{num1}{op1_eval}{power_val}*({num2}{inner_op_eval}({inner_power_val}))"
        
    try:
        correct_value = eval(expression_for_eval)
        if isinstance(correct_value, float) and correct_value.is_integer():
            correct_value = int(correct_value)
    except Exception: # 捕捉所有 eval 錯誤，例如除以零或複雜表達式
        return generate_order_of_operations_problem(level) # 重新生成題目

    question_text = f"計算下列各式的值。<br>{question_latex}"
    return {
        "question_text": question_text,
        "answer": str(correct_value), # 標準答案 (數值字串)
        "correct_answer": str(correct_value) # 顯示答案 (數值字串)
    }

def check(user_answer, correct_answer_from_generate_answer_field):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer_for_comparison = correct_answer_from_generate_answer_field.strip()

    is_correct = False
    
    # 判斷標準答案是 LaTeX 指數形式還是純數字
    if correct_answer_for_comparison.startswith('$'):
        # 這是簡記為指數形式的題目 (例如：$(-5)^{4}$)
        # 我們將正確答案和使用者輸入都轉換為統一的「標準」格式進行比對
        
        # 移除 LaTeX 的 '$'、'{'、'}' 符號，例如："$(-5)^{4}$" 轉換為 "(-5)^4"
        clean_correct = correct_answer_for_comparison.replace('$', '').replace('{', '').replace('}', '')
        
        # 清理使用者輸入：移除空格，並將 Python 的乘方符號 '**' 轉換為 '^'
        clean_user = user_answer.replace(' ', '').replace('**', '^')
        
        if clean_user == clean_correct:
            is_correct = True
        # 對於簡記為指數形式的題目，通常不接受其數值結果作為答案。
        # 因此，此處不進行數值比對。
    else:
        # 這是計算數值結果的題目 (例如：9 或 -32)
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer_for_comparison)
            if user_num == correct_num:
                is_correct = True
        except ValueError:
            # 使用者輸入不是有效的數字，所以不正確
            pass

    # 根據比對結果生成回饋訊息
    if correct_answer_for_comparison.startswith('$'):
        # 如果正確答案是 LaTeX 格式字串，直接使用
        result_text = f"完全正確！答案是 {correct_answer_for_comparison}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer_for_comparison}"
    else:
        # 如果正確答案是數值字串，則用 '$' 包裹以符合 LaTeX 顯示
        result_text = f"完全正確！答案是 ${correct_answer_for_comparison}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_for_comparison}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}