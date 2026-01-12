import random
from fractions import Fraction

def generate_calculation_problem():
    """
    生成正負整數除法運算的計算題。
    包含：負正、正負、負負、零除以非零整數。
    """
    problem_type_choice = random.choice(['neg_pos', 'pos_neg', 'neg_neg', 'zero_div'])
    
    if problem_type_choice == 'neg_pos':
        # Negative ÷ Positive: (-A) ÷ B = -(A ÷ B)
        divisor_abs = random.randint(2, 12)
        quotient_abs = random.randint(1, 10)
        dividend = -(divisor_abs * quotient_abs)
        divisor = divisor_abs
        correct_answer_val = -quotient_abs
        
    elif problem_type_choice == 'pos_neg':
        # Positive ÷ Negative: A ÷ (-B) = -(A ÷ B)
        divisor_abs = random.randint(2, 12)
        quotient_abs = random.randint(1, 10)
        dividend = divisor_abs * quotient_abs
        divisor = -divisor_abs
        correct_answer_val = -quotient_abs
        
    elif problem_type_choice == 'neg_neg':
        # Negative ÷ Negative: (-A) ÷ (-B) = A ÷ B
        divisor_abs = random.randint(2, 12)
        quotient_abs = random.randint(1, 10)
        dividend = -(divisor_abs * quotient_abs)
        divisor = -divisor_abs
        correct_answer_val = quotient_abs
        
    else: # zero_div
        # Zero ÷ Non-zero integer: 0 ÷ A = 0
        dividend = 0
        divisor = random.randint(1, 15)
        if random.random() < 0.5:
            divisor = -divisor # Divisor can be negative
        correct_answer_val = 0

    # 格式化數字以便在 LaTeX 中顯示：負數需要括號
    dividend_str = f"({dividend})" if dividend < 0 else str(dividend)
    divisor_str = f"({divisor})" if divisor < 0 else str(divisor)
    
    question_text = f"計算下列各式的值。<br>${dividend_str} \\div {divisor_str}$"
    correct_answer = str(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conceptual_problem():
    """
    生成關於整數除法不具交換律和結合律的觀念判斷題。
    """
    conceptual_type = random.choice(['commutative', 'associative'])
    
    if conceptual_type == 'commutative':
        # 判斷交換律
        question_text = r"判斷下列敘述是否正確：<br>「整數除法具有交換律，即對於任意非零整數 $a, b$，恆有 $a \\div b = b \\div a$。」"
        correct_answer = "不正確" 

    else: # associative
        # 判斷結合律
        question_text = r"判斷下列敘述是否正確：<br>「整數除法具有結合律，即對於任意非零整數 $a, b, c$，恆有 $(a \\div b) \\div c = a \\div (b \\div c)$。」"
        correct_answer = "不正確" 
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「整數除法」相關題目。
    包含：
    1. 正負整數的除法運算（歸納同號相除為正、異號相除為負）
    2. 零除以非零整數的結果
    3. 除法不具交換律和結合律的觀念判斷
    """
    
    # 根據難度等級調整問題類型
    if level == 1:
        # 等級1主要聚焦於計算，偶爾出現觀念題
        if random.random() < 0.8: # 80% 機率是計算題
            return generate_calculation_problem()
        else: # 20% 機率是觀念題
            return generate_conceptual_problem()
    else:
        # 其他等級（此處未詳細定義，預設行為與等級1相同）
        return generate_calculation_problem()


def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    # 移除使用者答案中的空白並轉為大寫，方便比較
    user_answer = user_answer.strip().replace(' ', '').upper()
    correct_answer = correct_answer.strip().replace(' ', '').upper()
    
    is_correct = False
    result_text = ""

    # 嘗試將答案轉換為整數進行數值比較（適用於計算題）
    try:
        user_num = int(user_answer)
        correct_num = int(correct_answer)
        if user_num == correct_num:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。請檢查您的計算。正確答案應為：${correct_answer}$"
    except ValueError:
        # 如果無法轉換為整數，則視為觀念題的文字答案（例如「不正確」）
        if user_answer == correct_answer:
            is_correct = True
            result_text = f"完全正確！答案是「{correct_answer}」。"
        else:
            result_text = f"答案不正確。正確答案應為：「{correct_answer}」"

    return {"correct": is_correct, "result": result_text, "next_question": True}