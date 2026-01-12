import random
from fractions import Fraction
import re

def generate_power_to_value():
    """
    生成將 $10^n$ 轉換為整數、小數或分數的題目。
    - n 為正整數時，表示為整數。
    - n 為零時，表示為 1。
    - n 為負整數時，表示為分數、小數或兩者。
    """
    exponent = random.randint(-6, 6) # Level 1: exponents from -6 to 6

    if exponent == 0:
        question_text = f"請以整數表示 $10^{{0}}$。"
        correct_answer = "1"
    elif exponent > 0:
        value = 10**exponent
        question_text = f"請以整數表示 $10^{{{exponent}}}$。"
        correct_answer = str(value)
    else: # exponent < 0
        abs_exponent = abs(exponent)

        # 計算小數形式 (e.g., 0.0001)
        decimal_str = f"0.{'0' * (abs_exponent - 1)}1"

        # 計算分數形式 (e.g., 1/10000)
        fraction_denominator = 10**abs_exponent
        fraction_str = f"1/{fraction_denominator}"

        # 隨機選擇要問的格式：小數、分數或兩者
        ask_for = random.choice(['fraction', 'decimal', 'both'])

        if ask_for == 'fraction':
            question_text = f"請以分數表示 $10^{{{exponent}}}$。"
            correct_answer = fraction_str
        elif ask_for == 'decimal':
            question_text = f"請以小數表示 $10^{{{exponent}}}$。"
            correct_answer = decimal_str
        else: # ask_for == 'both'
            question_text = f"請以分數和小數分別表示 $10^{{{exponent}}}$。<br>(請以逗號分隔，分數在前)"
            correct_answer = f"{fraction_str}, {decimal_str}"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_value_to_power_blanks():
    """
    生成將小數或分數轉換為 $10^n$ 形式的填空題。
    例：$0.000001 = 1/(\quad) = 1/10^{()} = 10^{()}$
    例：$1/100000 = 1/10^{()} = 10^{()}$
    """
    
    problem_subtype = random.choice(['decimal_start', 'fraction_start'])
    
    if problem_subtype == 'decimal_start':
        # 從小數開始，轉換為分數形式和 $10^n$ 形式
        neg_exponent = random.randint(-6, -2) # 例如：從 0.01 ($10^{-2}$) 到 0.000001 ($10^{-6}$)
        abs_exponent = abs(neg_exponent)
        
        decimal_val_str = f"0.{'0' * (abs_exponent - 1)}1"
        denominator = 10**abs_exponent
        
        question_text = (
            f"在括號內填入適當的數。<br>"
            f"${decimal_val_str} = 1/(\\quad) = 1/10^{{()}} = 10^{{()}}$"
        )
        
        # 正確答案依序為：分母數字、分母的指數、最終的負指數
        correct_answer = f"{denominator}, {abs_exponent}, {neg_exponent}"
        
    else: # problem_subtype == 'fraction_start'
        # 從分數開始，轉換為 $1/10^n$ 形式和 $10^n$ 形式
        pos_exponent = random.randint(2, 6) # 例如：從 1/100 ($10^2$) 到 1/1000000 ($10^6$)
        denominator = 10**pos_exponent
        
        question_text = (
            f"在括號內填入適當的數。<br>"
            f"r$\\frac{{1}}{{{denominator}}}$ = 1/10^{{()}} = 10^{{()}}$"
        )
        
        # 正確答案依序為：分母的指數、最終的負指數
        correct_answer = f"{pos_exponent}, {-pos_exponent}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「以 10 為底數的指數運算」相關題目。
    """
    # 根據 level 選擇不同的題型或數值範圍
    # Level 1 包含兩種主要題型：指數形式轉數值，數值轉指數形式填空
    problem_type = random.choice(['power_to_value', 'value_to_power_blanks'])
    
    if problem_type == 'power_to_value':
        return generate_power_to_value()
    else: # 'value_to_power_blanks'
        return generate_value_to_power_blanks()


def parse_answer_part(s):
    """
    嘗試將字串解析為分數、浮點數或整數。
    """
    s = s.strip()
    if not s:
        return "" # 處理空字串

    # 優先嘗試解析為分數
    if '/' in s:
        try:
            return Fraction(s)
        except ValueError:
            pass # 無法解析為分數，繼續嘗試其他類型
            
    # 接著嘗試解析為浮點數
    try:
        return float(s)
    except ValueError:
        pass # 無法解析為浮點數，繼續嘗試整數
        
    # 最後嘗試解析為整數
    try:
        return int(s)
    except ValueError:
        pass # 無法解析為整數，將其視為普通字串
        
    return s # 如果都無法解析，則返回原始字串

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援多部分答案 (以逗號分隔)，並能識別分數、小數和整數。
    """
    user_parts_str = [p.strip() for p in user_answer.strip().split(',')]
    correct_parts_str = [p.strip() for p in correct_answer.strip().split(',')]

    is_correct = True
    if len(user_parts_str) != len(correct_parts_str):
        is_correct = False
    else:
        for u_s, c_s in zip(user_parts_str, correct_parts_str):
            u_parsed = parse_answer_part(u_s)
            c_parsed = parse_answer_part(c_s)

            # 比較解析後的數值或字串。
            # 由於要求特定形式 (分數/小數/整數)，類型差異會導致不匹配，這是預期的。
            if u_parsed != c_parsed:
                is_correct = False
                break
                
    result_text = ""
    if is_correct:
        # 將正確答案中的 LaTeX 符號轉換為顯示格式，用於回饋
        display_correct_answer = correct_answer.replace(r'/', r'\textfractionsolidus') # 確保分數顯示
        result_text = f"完全正確！答案是 ${display_correct_answer}$。"
    else:
        display_correct_answer = correct_answer.replace(r'/', r'\textfractionsolidus')
        result_text = f"答案不正確。正確答案應為：${display_correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}