import random
from fractions import Fraction
import math

def format_number(num):
    """
    格式化數字為字串，特別處理分數和整數型浮點數，以便在LaTeX中正確顯示。
    """
    if isinstance(num, int):
        return str(num)
    elif isinstance(num, float):
        if num == int(num): # 如果是整數值的浮點數 (e.g., 5.0)
            return str(int(num))
        return str(num)
    elif isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        
        # 處理負分數：將負號放在分數前面
        if num.numerator < 0:
            return r"-\\frac{{{}}}{{{}}}".format(abs(num.numerator), num.denominator)
        else:
            return r"\\frac{{{}}}{{{}}}".format(num.numerator, num.denominator)
    return str(num)

def generate_number(level, include_zero=True):
    """
    根據等級生成不同類型的數字。
    Level 1: 較小的整數。
    Level 2: 較大的整數或小數。
    Level 3: 整數、小數、分數。
    """
    num_type_weights = [5, 3, 1, 1] # int, int (larger), decimal, fraction
    if level == 1:
        num_type_choice = 'int_small'
    elif level == 2:
        num_type_choice = random.choices(['int_small', 'int_large', 'decimal'], weights=[4, 3, 2], k=1)[0]
    else: # level 3+
        num_type_choice = random.choices(['int_large', 'decimal', 'fraction'], weights=[3, 3, 4], k=1)[0]
    
    val = 0
    if num_type_choice == 'int_small':
        val = random.randint(-15, 15)
    elif num_type_choice == 'int_large':
        val = random.randint(-30, 30)
    elif num_type_choice == 'decimal':
        val = round(random.uniform(-15.0, 15.0), random.randint(1, 2))
    else: # 'fraction'
        numerator = random.randint(-20, 20)
        denominator = random.randint(2, 10)
        # 確保不是整數且不是零
        while numerator % denominator == 0 or numerator == 0:
            numerator = random.randint(-20, 20)
        val = Fraction(numerator, denominator)

    # 確保在 include_zero=False 時不生成 0
    if not include_zero and (val == 0 or (isinstance(val, float) and math.isclose(val, 0.0)) or (isinstance(val, Fraction) and val == 0)):
        return generate_number(level, include_zero=False) # 重新生成
        
    return val

def generate_opposite_problem(level):
    """
    生成尋找相反數的題目。
    """
    val = generate_number(level, include_zero=True)
    opposite_val = -val

    val_str = format_number(val)
    opposite_val_str = format_number(opposite_val)

    question_text = f"寫出數 ${val_str}$ 的相反數。"
    correct_answer = opposite_val_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_abs_value_calculation_problem(level):
    """
    生成計算絕對值的題目。
    """
    val = generate_number(level, include_zero=True)
    abs_val = abs(val)

    val_str = format_number(val)
    abs_val_str = format_number(abs_val)
    
    question_text = f"寫出 $|{val_str}|$ 的值。"
    correct_answer = abs_val_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_abs_value_comparison_problem(level):
    """
    生成比較絕對值大小的題目。
    要求寫出兩個數的絕對值並比較其大小。
    """
    num1 = generate_number(level, include_zero=True)
    num2 = generate_number(level, include_zero=True)

    # 確保兩個數的絕對值不完全相同，避免過於簡單的題目，除非是0
    while abs(num1) == abs(num2) and not (num1 == 0 and num2 == 0):
        num2 = generate_number(level, include_zero=True)

    abs_num1_val = abs(num1)
    abs_num2_val = abs(num2)

    if abs_num1_val < abs_num2_val:
        comparison = "<"
    elif abs_num1_val > abs_num2_val:
        comparison = ">"
    else:
        comparison = "="

    num1_str = format_number(num1)
    num2_str = format_number(num2)
    abs_num1_str = format_number(abs_num1_val)
    abs_num2_str = format_number(abs_num2_val)

    question_text = (
        f"分別寫出 ${num1_str}$ 和 ${num2_str}$ 的絕對值，並比較這兩數絕對值的大小。"
        f"<br>($|{num1_str}| = ?$, $|{num2_str}| = ?$, 比較結果：請填入 '>', '<' 或 '=')"
    )
    # 正確答案格式: "Abs1_Value, Abs2_Value, Comparison_Symbol"
    correct_answer = f"{abs_num1_str}, {abs_num2_str}, {comparison}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_number_from_abs_problem(level):
    """
    生成從絕對值找出原數的題目 (例如：若 |a| = X, 則 a 是多少)。
    """
    abs_val_limit = random.randint(1, 25) # 絕對值限制
    
    question_text = f"在數線上，有一數 $a$，若 $|a| = {abs_val_limit}$，則 $a$ 是多少？"
    correct_answer = f"{abs_val_limit}, -{abs_val_limit}" # 答案可能為兩個數
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_integers_in_abs_range_problem(level):
    """
    生成尋找滿足絕對值條件的所有整數的題目 (例如：寫出絕對值小於 X 的所有整數)。
    """
    limit = random.randint(2, 12) # 絕對值範圍限制
    
    # 隨機選擇 < 或 <=
    if random.random() < 0.5: # 絕對值小於
        operator_str = "<"
        # 整數為 -(limit-1) 到 (limit-1)
        integers = list(range(-(limit - 1), limit))
        question_text = f"寫出絕對值小於 ${limit}$ 的所有整數。"
    else: # 絕對值小於或等於
        operator_str = r"\\le"
        # 整數為 -limit 到 limit
        integers = list(range(-limit, limit + 1))
        question_text = f"寫出絕對值小於或等於 ${limit}$ 的所有整數。"
        
    correct_answer = ", ".join(map(str, sorted(integers)))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「相反數與絕對值」相關題目。
    """
    problem_types_by_level = {
        1: ['opposite', 'abs_value_calculation', 'find_number_from_abs'],
        2: ['opposite', 'abs_value_calculation', 'abs_value_comparison', 'find_number_from_abs', 'find_integers_in_abs_range'],
        3: ['opposite', 'abs_value_calculation', 'abs_value_comparison', 'find_number_from_abs', 'find_integers_in_abs_range']
    }
    
    # Ensure level is within bounds for problem type selection
    chosen_level = min(level, max(problem_types_by_level.keys()))
    problem_type = random.choice(problem_types_by_level[chosen_level])

    if problem_type == 'opposite':
        return generate_opposite_problem(level)
    elif problem_type == 'abs_value_calculation':
        return generate_abs_value_calculation_problem(level)
    elif problem_type == 'abs_value_comparison':
        return generate_abs_value_comparison_problem(level)
    elif problem_type == 'find_number_from_abs':
        return generate_find_number_from_abs_problem(level)
    elif problem_type == 'find_integers_in_abs_range':
        return generate_find_integers_in_abs_range_problem(level)
    
    # Fallback, though ideally one of the above will always be chosen.
    return generate_opposite_problem(level)


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    處理多種答案格式，例如單一數值、逗號分隔的數值列表、絕對值比較符號等。
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()

    is_correct = False
    feedback = ""

    # Helper to parse and convert to float from string or Fraction string
    def safe_float_convert(s):
        s = s.replace(r'\\frac{', '').replace('{', '').replace('}', '').replace(' ', '')
        if '/' in s: # Handle fractions written as "a/b"
            parts = s.split('/')
            if len(parts) == 2 and parts[1] != '0':
                return float(Fraction(int(parts[0]), int(parts[1])))
        try:
            return float(s)
        except ValueError:
            return None # Indicate conversion failure

    # Specific handling for 'find_number_from_abs' type (e.g. "6, -6")
    if ", " in correct_answer and any(c.isdigit() for c in correct_answer):
        correct_nums = set()
        for p in correct_answer.split(','):
            val = safe_float_convert(p.strip())
            if val is not None:
                correct_nums.add(val)
        
        user_nums = set()
        for p in user_answer.replace('或', ',').split(','): # allow "6 或 -6"
            val = safe_float_convert(p.strip())
            if val is not None:
                user_nums.add(val)
        
        # Compare sets of numbers
        if correct_nums and user_nums and len(correct_nums) == len(user_nums):
            # Use math.isclose for robust float comparison within sets
            all_match = True
            for c_num in correct_nums:
                found_match = False
                for u_num in user_nums:
                    if math.isclose(c_num, u_num, rel_tol=1e-9, abs_tol=1e-9):
                        found_match = True
                        break
                if not found_match:
                    all_match = False
                    break
            if all_match:
                is_correct = True
    
    # Specific handling for 'abs_value_comparison_problem' type (e.g., "3, 9, <")
    elif len(correct_answer.split(',')) == 3 and any(c in correct_answer for c in ['<', '>', '=']):
        try:
            correct_parts = [s.strip() for s in correct_answer.split(',')]
            correct_abs1 = safe_float_convert(correct_parts[0])
            correct_abs2 = safe_float_convert(correct_parts[1])
            correct_symbol = correct_parts[2]

            user_parts = [s.strip() for s in user_answer.split(',')]
            
            if len(user_parts) == 3: # User provided full answer: abs1, abs2, symbol
                user_abs1 = safe_float_convert(user_parts[0])
                user_abs2 = safe_float_convert(user_parts[1])
                user_symbol = user_parts[2]
                
                if user_abs1 is not None and user_abs2 is not None:
                    # Check for direct match
                    if math.isclose(user_abs1, correct_abs1) and \
                       math.isclose(user_abs2, correct_abs2) and \
                       user_symbol == correct_symbol:
                        is_correct = True
                    # Check for swapped order of abs values (user might input them in different order)
                    elif math.isclose(user_abs1, correct_abs2) and \
                         math.isclose(user_abs2, correct_abs1) and \
                         user_symbol == correct_symbol:
                        is_correct = True
            elif len(user_parts) == 1 and user_parts[0] in ['<', '>', '=']: # User only provides the symbol
                if user_parts[0] == correct_symbol:
                    is_correct = True
                    
        except (ValueError, IndexError):
            # Fallback to simple string comparison if parsing fails (e.g., non-numeric parts)
            if user_answer == correct_answer:
                is_correct = True

    # General case for single value or list of comma-separated numbers (integers in range)
    else:
        # Try to convert to numbers for robust comparison
        correct_parts = [p.strip() for p in correct_answer.split(',')]
        user_parts = [p.strip() for p in user_answer.split(',')]

        try:
            # Attempt to convert all parts to floats for comparison
            correct_nums_list = sorted([safe_float_convert(item) for item in correct_parts if safe_float_convert(item) is not None])
            user_nums_list = sorted([safe_float_convert(item) for item in user_parts if safe_float_convert(item) is not None])

            if len(correct_nums_list) == len(user_nums_list):
                all_match = True
                for c_num, u_num in zip(correct_nums_list, user_nums_list):
                    if not math.isclose(c_num, u_num, rel_tol=1e-9, abs_tol=1e-9):
                        all_match = False
                        break
                if all_match:
                    is_correct = True
        except (ValueError, TypeError): # Handle cases where conversion to float fails
            # Fallback to direct string comparison for lists if numeric conversion isn't robust
            if correct_parts == user_parts:
                is_correct = True
            
            # Additional check for raw string comparisons, e.g., fractions
            if correct_answer == user_answer:
                is_correct = True


    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}