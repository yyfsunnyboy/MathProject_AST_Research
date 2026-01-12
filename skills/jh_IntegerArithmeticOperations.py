import random
from fractions import Fraction

# Helper function to format numbers for display, especially negative ones, with parentheses
def _format_num_for_latex(num):
    if num < 0:
        return f"({num})"
    return str(num)

# Helper for operations display in LaTeX
def _get_op_display(op):
    if op == '*':
        return r"\\times"
    elif op == '/':
        return r"\\div"
    return op # For '+' and '-'

# Helper for calculation (using Python's operators)
def _get_op_calc(op):
    return op # Python operators are fine as is for eval()

def generate(level=1):
    """
    生成「整數四則運算優先順序」相關題目。
    包含：
    1. 基本四則運算 (先乘除後加減)
    2. 括號優先
    3. 絕對值優先
    4. 乘法分配律 (簡化計算)
    5. 應用題 (在較高難度或隨機選擇時出現)
    """
    
    problem_types = [
        '_generate_basic_pemdas',
        '_generate_with_parentheses',
        '_generate_with_absolute_value',
        '_generate_distributive_factor_out',
        '_generate_distributive_expand'
    ]
    
    # Introduce word problem at higher levels or with less frequency
    if level >= 2 or random.random() < 0.2: # 20% chance for word problem even at level 1
        problem_types.append('_generate_word_problem')
    
    # Randomly select a problem generation function
    generator_func_name = random.choice(problem_types)
    generator_func = globals()[generator_func_name]
    
    return generator_func(level)

# --- Problem Generation Functions ---

def _generate_basic_pemdas(level):
    """
    生成基本四則運算題目 (先乘除後加減)。
    例如: (-3) * 12 / (-6)
    """
    num_ops = random.choice([2, 3]) # 2 or 3 operations
    
    nums = [random.randint(-15, 15) for _ in range(num_ops + 1)]
    ops = [random.choice(['*', '/', '+', '-']) for _ in range(num_ops)]
    
    # Ensure division results in integer and avoid zero division
    for i in range(len(ops)):
        if ops[i] == '/':
            current_num = nums[i]
            divisors = [d for d in range(-10, 11) if d != 0 and current_num % d == 0]
            if not divisors: # If no integer divisors, change operation or current_num
                if current_num == 0: # If 0, must change to non-division or change current_num
                    nums[i] = random.choice([-6, -4, -2, 2, 4, 6]) # Change current_num to something divisible
                else: # Try to change operation
                    ops[i] = random.choice(['*', '+', '-'])
                    continue # Skip to next op if changed
                
                # After potential change, re-evaluate divisors
                divisors = [d for d in range(-10, 11) if d != 0 and nums[i] % d == 0]
                if not divisors: return _generate_basic_pemdas(level) # Still no divisors, regenerate entirely

            nums[i+1] = random.choice(divisors) # The next number becomes the divisor

    expression_parts_latex = []
    expression_parts_eval = []
    
    # Build expression string for display and evaluation
    for i in range(num_ops + 1):
        expression_parts_latex.append(_format_num_for_latex(nums[i]))
        expression_parts_eval.append(str(nums[i]))
        if i < num_ops:
            expression_parts_latex.append(_get_op_display(ops[i]))
            expression_parts_eval.append(_get_op_calc(ops[i]))

    question_text = f"計算下列各式的值。<br>$ {' '.join(expression_parts_latex)} $"
    
    try:
        correct_answer_val = int(eval(''.join(expression_parts_eval)))
    except ZeroDivisionError:
        return _generate_basic_pemdas(level) # Regenerate if division by zero occurred despite checks
    
    correct_answer = str(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_with_parentheses(level):
    """
    生成帶有括號的運算題目。
    例如: (-60) / [ (-7) * 2 - 1 ]
    """
    # Structure: (A op1 B) op2 C or A op1 [ B op2 C op3 D ]
    
    if random.random() < 0.6: # Simpler form: (A op1 B) op2 C
        num1 = random.randint(-20, 20)
        num2 = random.randint(-10, 10)
        op_inner = random.choice(['*', '+', '-'])
        op_outer = random.choice(['*', '/', '+', '-'])
        
        # Ensure inner calculation is valid
        if op_inner == '/':
            if num1 == 0: num2 = random.choice([-5, -3, -1, 1, 3, 5])
            else:
                divisors = [d for d in range(-10, 11) if d != 0 and num1 % d == 0]
                if not divisors: return _generate_with_parentheses(level) 
                num2 = random.choice(divisors)

        inner_val = int(eval(f"{num1} {_get_op_calc(op_inner)} {num2}"))
        
        # Ensure outer calculation is valid
        if op_outer == '/':
            if inner_val == 0: return _generate_with_parentheses(level) # Avoid division by zero
            divisors = [d for d in range(-10, 11) if d != 0 and inner_val % d == 0]
            if not divisors: return _generate_with_parentheses(level)
            num3 = random.choice(divisors)
        else:
            num3 = random.randint(-10, 10)

        question_text = f"計算下列各式的值。<br>$ ({_format_num_for_latex(num1)} {_get_op_display(op_inner)} {_format_num_for_latex(num2)}) {_get_op_display(op_outer)} {_format_num_for_latex(num3)} $"
        correct_answer_val = int(eval(f"({num1} {_get_op_calc(op_inner)} {num2}) {_get_op_calc(op_outer)} {num3}"))

    else: # More complex form: A op1 [ B op2 C op3 D ]
        num1 = random.randint(-30, 30)
        op1 = random.choice(['*', '/'])
        
        num2 = random.randint(-10, 10)
        op2 = random.choice(['*', '/', '+', '-'])
        num3 = random.randint(-10, 10)
        op3 = random.choice(['+', '-'])
        num4 = random.randint(1, 10) # Often a small integer for the last op
        
        # Ensure division within bracket
        if op2 == '/':
            if num2 == 0: num3 = random.choice([-5, -3, -1, 1, 3, 5])
            else:
                divisors = [d for d in range(-10, 11) if d != 0 and num2 % d == 0]
                if not divisors: return _generate_with_parentheses(level)
                num3 = random.choice(divisors)

        inner_bracket_str_eval = f"({num2} {_get_op_calc(op2)} {num3} {_get_op_calc(op3)} {num4})"
        try:
            inner_bracket_val = int(eval(inner_bracket_str_eval))
        except ZeroDivisionError:
            return _generate_with_parentheses(level)

        # Ensure outer division
        if op1 == '/':
            if inner_bracket_val == 0: return _generate_with_parentheses(level)
            divisors = [d for d in range(-20, 21) if d != 0 and num1 % d == 0]
            if inner_bracket_val not in divisors: # Ensure num1 is divisible by inner_bracket_val
                # Try to adjust num1 to be a multiple of inner_bracket_val
                if inner_bracket_val != 0:
                    num1 = inner_bracket_val * random.choice([-3, -2, -1, 1, 2, 3])
                else: # Should be caught above, but defensive
                    return _generate_with_parentheses(level)
        
        question_text = (
            f"計算下列各式的值。<br>"
            f"$ {_format_num_for_latex(num1)} {_get_op_display(op1)} "
            f"[ {_format_num_for_latex(num2)} {_get_op_display(op2)} {_format_num_for_latex(num3)} {_get_op_display(op3)} {_format_num_for_latex(num4)} ] $"
        )
        correct_answer_val = int(eval(f"{num1} {_get_op_calc(op1)} {inner_bracket_str_eval}"))
        
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_with_absolute_value(level):
    """
    生成帶有絕對值的題目。
    例如: (-8) * 6 + |(-5) * 10 - 1|
    """
    num1 = random.randint(-10, 10)
    op1 = random.choice(['*', '+', '-'])
    num2 = random.randint(-10, 10)
    
    # Inside absolute value
    num_abs1 = random.randint(-10, 10)
    op_abs = random.choice(['*', '+', '-'])
    num_abs2 = random.randint(-10, 10)
    
    # Ensure division results in integer if used inside abs
    if op_abs == '/':
        if num_abs1 == 0: num_abs2 = random.choice([-5, -3, -1, 1, 3, 5])
        else:
            divisors = [d for d in range(-10, 11) if d != 0 and num_abs1 % d == 0]
            if not divisors: return _generate_with_absolute_value(level)
            num_abs2 = random.choice(divisors)

    inner_abs_expr_eval = f"{num_abs1} {_get_op_calc(op_abs)} {num_abs2}"
    
    # Calculate the full expression
    full_expr_eval = f"{num1} {_get_op_calc(op1)} {num2} + abs({inner_abs_expr_eval})"
    try:
        correct_answer_val = int(eval(full_expr_eval))
    except ZeroDivisionError:
        return _generate_with_absolute_value(level)

    question_text = (
        f"計算下列各式的值。<br>"
        f"$ {_format_num_for_latex(num1)} {_get_op_display(op1)} {_format_num_for_latex(num2)} "
        f"+ \\left| {_format_num_for_latex(num_abs1)} {_get_op_display(op_abs)} {_format_num_for_latex(num_abs2)} \\right| $"
    )
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_distributive_factor_out(level):
    """
    生成利用乘法分配律因式分解的題目。
    例如: 983 * (-5) + 17 * (-5)
    """
    common_factor = random.randint(-10, 10)
    while common_factor == 0: common_factor = random.randint(-10, 10) # Avoid 0 factor
    
    # Ensure (num_a op_between_terms num_b) is a round number like 100, 1000, or -100, -1000
    target_sum_options = [100, 200, 500, 1000, -100, -200, -500, -1000]
    target_sum = random.choice(target_sum_options)
    
    op_between_terms = random.choice(['+', '-'])

    num_a = 0
    num_b = 0

    # Generate num_a and num_b such that their sum/difference is target_sum
    # And they are reasonably large and distinct
    while True:
        num_a = random.randint(10, 990) 
        if op_between_terms == '+':
            num_b = target_sum - num_a
        else: # subtraction
            num_b = num_a - target_sum
        
        # Conditions: num_b is not too small, and num_a != num_b
        if abs(num_b) >= 10 and num_a != num_b:
            break
        
        # Add a safeguard against infinite loops for extreme target_sum values
        # For this specific logic, it should break fairly quickly for the chosen target_sum_options

    expression_latex = (
        f"{_format_num_for_latex(num_a)} {r'\\times'} {_format_num_for_latex(common_factor)} "
        f"{op_between_terms} {_format_num_for_latex(num_b)} {r'\\times'} {_format_num_for_latex(common_factor)}"
    )
    
    correct_answer_val = int(eval(f"({num_a} {op_between_terms} {num_b}) * {common_factor}"))

    question_text = f"計算下列各式的值。<br>$ {expression_latex} $"
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_distributive_expand(level):
    """
    生成利用乘法分配律展開的題目。
    例如: 1002 * (-175) 或 (-273) * 999
    """
    base = random.choice([100, 1000])
    small_num = random.randint(1, 5) # For (1000 + 2) or (1000 - 1)
    
    multiplier = random.randint(-200, 200)
    while multiplier == 0: multiplier = random.randint(-200, 200) # Avoid 0 multiplier

    # Determine if it's (Base + Small) or (Base - Small)
    is_addition = random.random() < 0.5
    
    if is_addition:
        num_main = base + small_num
    else: 
        num_main = base - small_num
    
    # Randomly swap order of (num_main * multiplier) or (multiplier * num_main)
    if random.random() < 0.5:
        expression_latex = f"{_format_num_for_latex(num_main)} {r'\\times'} {_format_num_for_latex(multiplier)}"
    else:
        expression_latex = f"{_format_num_for_latex(multiplier)} {r'\\times'} {_format_num_for_latex(num_main)}"

    correct_answer_val = int(eval(f"{num_main} * {multiplier}")) # Calculation is always straightforward multiplication

    question_text = f"計算下列各式的值。<br>$ {expression_latex} $"
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_word_problem(level):
    """
    生成應用題。
    例如: 骰子移動棋子的題目。
    """
    start_pos = random.randint(-10, 10)
    
    event1_move = random.randint(2, 7) # e.g., move right 5
    event1_count = random.randint(2, 8) # e.g., 3 times
    
    event2_move = random.randint(-7, -2) # e.g., move left 4 (-4)
    event2_count = random.randint(2, 8) # e.g., 7 times

    total_throws = event1_count + event2_count

    # Randomly assign descriptions to positive/negative moves
    move_desc1 = ""
    move_desc2 = ""
    if event1_move > 0:
        move_desc1 = f"往數線右方移動 {event1_move} 個單位"
    else:
        move_desc1 = f"往數線左方移動 {abs(event1_move)} 個單位"

    if event2_move > 0:
        move_desc2 = f"往數線右方移動 {event2_move} 個單位"
    else:
        move_desc2 = f"往數線左方移動 {abs(event2_move)} 個單位"
    
    # Ensure distinct descriptions for clarity
    while move_desc1 == move_desc2:
        event2_move = random.randint(-7, -2)
        if event2_move > 0:
            move_desc2 = f"往數線右方移動 {event2_move} 個單位"
        else:
            move_desc2 = f"往數線左方移動 {abs(event2_move)} 個單位"

    # Decide which event count is given in the problem
    if random.random() < 0.5: # Give event1_count
        given_count_desc = f"其中發生「{move_desc1}」共 ${event1_count}$ 次，"
        remaining_count_desc = f"則發生「{move_desc2}」共 ${total_throws - event1_count}$ 次。"
    else: # Give event2_count
        given_count_desc = f"其中發生「{move_desc2}」共 ${event2_count}$ 次，"
        remaining_count_desc = f"則發生「{move_desc1}」共 ${total_throws - event2_count}$ 次。"

    question_text = (
        f"小明將一個棋子放在數線上，依照下列規則移動：<br>"
        f"狀況一：棋子{move_desc1}；<br>"
        f"狀況二：棋子{move_desc2}。<br>"
        f"已知小明一開始將棋子放在原點 ${start_pos}$，共進行了 ${total_throws}$ 次移動，<br>"
        f"{given_count_desc}"
        f"則棋子最後的位置在哪個坐標上？"
    )
    
    correct_answer_val = start_pos + (event1_move * event1_count) + (event2_move * event2_count)
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        # Try to convert to integer for comparison
        user_val = int(user_answer)
        correct_val = int(correct_answer)
        if user_val == correct_val:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    except ValueError:
        result_text = f"您的輸入 '{user_answer}' 無效，請輸入一個整數。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}