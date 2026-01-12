import random
from fractions import Fraction
import math

def _get_random_number(level, allow_fraction=True, allow_decimal=True):
    """Generates a random number (int, float, or Fraction) based on level."""
    num_type_options = []
    if not allow_fraction and not allow_decimal:
        num_type_options.append('integer')
    else:
        num_type_options.append('integer')
        if allow_fraction: num_type_options.append('fraction')
        if allow_decimal: num_type_options.append('decimal')

    # Ensure num_type_options is not empty
    if not num_type_options:
        num_type_options.append('integer') # Fallback to integer if no types allowed

    num_type = random.choice(num_type_options)
    
    # Adjust ranges and complexity based on level
    if level == 1: # Basic: smaller integers, simpler fractions/decimals (1 decimal place)
        int_range = (-10, 10)
        frac_denominators = (2, 5)
        decimal_places = 1
        min_abs_val_for_non_zero = 0.2 # Minimum absolute value for non-integer numbers to avoid tiny values
    elif level == 2: # Medium: wider integer range, more complex fractions/decimals (1-2 decimal places)
        int_range = (-20, 20)
        frac_denominators = (2, 10)
        decimal_places = random.choice([1, 2])
        min_abs_val_for_non_zero = 0.1
    else: # Advanced: even wider range, more complex fractions/decimals (1-3 decimal places)
        int_range = (-50, 50)
        frac_denominators = (2, 15)
        decimal_places = random.choice([1, 2, 3])
        min_abs_val_for_non_zero = 0.05

    if num_type == 'integer':
        return random.randint(int_range[0], int_range[1])
    elif num_type == 'fraction':
        # Numerator limit based on integer range and max denominator
        numerator_limit = max(abs(int_range[0]), abs(int_range[1])) * frac_denominators[1]
        while True:
            numerator = random.randint(-numerator_limit, numerator_limit)
            denominator = random.randint(frac_denominators[0], frac_denominators[1])
            temp_frac = Fraction(numerator, denominator)
            # Ensure not zero and not too small in absolute value
            if numerator != 0 and abs(float(temp_frac)) >= min_abs_val_for_non_zero:
                return temp_frac
    elif num_type == 'decimal':
        while True: # Ensure decimal is not too close to zero for comparison
            val = random.uniform(float(int_range[0]), float(int_range[1]))
            rounded_val = round(val, decimal_places)
            # Ensure non-zero and not too small
            if rounded_val != 0.0 and abs(rounded_val) >= min_abs_val_for_non_zero:
                return rounded_val
    
    # Fallback, should not be reached with proper logic
    return random.randint(-5, 5)

def _format_number_for_display(num):
    """Formats a number (int, float, Fraction) into a LaTeX string for display."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator >= abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            remainder = abs_num.numerator % abs_num.denominator
            if remainder == 0:
                return f"{sign}{whole}"
            return f"{sign}{whole}\\frac{{{remainder}}}{{{abs_num.denominator}}}"
        else:
            return f"{sign}\\frac{{{abs_num.numerator}}}{{{abs_num.denominator}}}"
    return str(num)

def _canonical_string_form(num):
    """Converts a number (int, float, Fraction) into a canonical string for internal checking."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Use improper fraction form for consistency in checking
        return f"{num.numerator}/{num.denominator}"
    return str(num)

def _parse_number_string_for_check(s):
    """Parses a string (user input or canonical form) into a float for comparison."""
    s = s.strip()
    
    # Handle mixed numbers first, e.g., "2 1/3" or "-2 1/3"
    # The format -2 1/3 means -(2 + 1/3)
    if ' ' in s:
        try:
            parts = s.split(' ', 1) # Split only on first space
            whole_str = parts[0]
            frac_str = parts[1]
            
            whole = int(whole_str)
            
            if '/' in frac_str:
                frac_parts = frac_str.split('/')
                numerator = int(frac_parts[0])
                denominator = int(frac_parts[1])
                if denominator == 0: raise ValueError("Denominator cannot be zero")
                
                # Calculate value: absolute whole + absolute fraction, then apply sign from whole
                val = abs(whole) + Fraction(numerator, denominator)
                return float(val) * (-1 if whole < 0 else 1)
        except ValueError:
            pass # Fall through to other parsing methods

    # Try simple fraction (e.g., "1/2", "-7/3")
    if '/' in s:
        try:
            parts = s.split('/')
            numerator = int(parts[0])
            denominator = int(parts[1])
            if denominator == 0: raise ValueError("Denominator cannot be zero")
            return float(Fraction(numerator, denominator))
        except ValueError:
            pass # Fall through
    
    # Try integer or float
    try:
        return float(s)
    except ValueError:
        pass
    
    raise ValueError(f"無法解析數字字串: {s}")


def generate_direct_comparison_problem(level):
    """Generates a problem comparing two numbers."""
    num1 = _get_random_number(level)
    num2 = _get_random_number(level)

    # Ensure num1 and num2 are distinct enough for comparison
    while abs(float(num1) - float(num2)) < 1e-6: # Use a small epsilon for float comparison
        num2 = _get_random_number(level)

    val1 = float(num1)
    val2 = float(num2)

    if val1 < val2:
        operator = "<"
    elif val1 > val2:
        operator = ">"
    else:
        operator = "="

    display_num1 = _format_number_for_display(num1)
    display_num2 = _format_number_for_display(num2)

    question_text = f"請比較下列各組數的大小，並填入 $>, <$ 或 $=$.<br>${display_num1} \\text{{ \\quad }} \\square \\text{{ \\quad }} {display_num2}$"
    correct_answer = operator

    return {
        "question_text": question_text,
        "answer": correct_answer, # This is the expected user input format
        "correct_answer": correct_answer # This is the internal checking format
    }

def generate_ordering_list_problem(level):
    """Generates a problem to order a list of numbers."""
    num_count = random.randint(3, 5)
    numbers = []
    
    # Generate distinct numbers
    generated_values = set()
    for _ in range(num_count):
        new_num = _get_random_number(level)
        # Ensure distinctness by checking its float representation
        while any(abs(float(new_num) - val) < 1e-6 for val in generated_values):
            new_num = _get_random_number(level)
        numbers.append(new_num)
        generated_values.add(float(new_num))

    order_type = random.choice(['ascending', 'descending'])
    
    # Sort by float value, but store original number objects
    sorted_numbers_with_floats = sorted([(float(n), n) for n in numbers])

    if order_type == 'ascending':
        sorted_numbers = [n_orig for _, n_orig in sorted_numbers_with_floats]
        order_desc = "由小到大"
    else: # descending
        sorted_numbers = [n_orig for _, n_orig in sorted_numbers_with_floats[::-1]] # Reverse the sorted list
        order_desc = "由大到小"
        
    display_numbers = [f"${_format_number_for_display(n)}$" for n in numbers]
    # For correct_answer, use canonical string form for parsing in check
    correct_answer = ','.join([_canonical_string_form(n) for n in sorted_numbers])
    
    question_text = f"請將下列各數{order_desc}排列：<br>{', '.join(display_numbers)}<br>(請以逗號分隔，由左至右填寫)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_relative_pos_then_compare_problem(level):
    """Generates a problem involving relative position and then comparison."""
    # For simplicity, start with integer for base point A in relative position problems
    val_a_int = random.randint(-15, 15)
    val_diff = random.randint(1, 10)
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b_coord_float = float(val_a_int) + val_diff
    else:
        val_b_coord_float = float(val_a_int) - val_diff
    
    # Generate another number to compare with B's coordinate
    compare_val_raw = _get_random_number(level)
    
    # Ensure compare_val_raw is not too close to val_b_coord_float
    while abs(float(compare_val_raw) - val_b_coord_float) < 1e-6:
        compare_val_raw = _get_random_number(level)

    if val_b_coord_float < float(compare_val_raw):
        operator = "<"
    elif val_b_coord_float > float(compare_val_raw):
        operator = ">"
    else:
        operator = "="

    display_val_a = _format_number_for_display(val_a_int)
    display_compare_val = _format_number_for_display(compare_val_raw)

    question_text = (
        f"數線上 $A$ 點座標為 ${display_val_a}$，$B$ 點在 $A$ 點的{direction}邊 ${val_diff}$ 單位處。<br>"
        f"請問 $B$ 點座標和 ${display_compare_val}$ 比較，何者較大/小？<br>"
        f"請填入 $>, <$ 或 $=$.<br>$B \\text{{ \\quad }} \\square \\text{{ \\quad }} {display_compare_val}$"
    )
    correct_answer = operator

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    Generates a number comparison problem (jh_ComparingNumbers).
    """
    problem_type = random.choice(['direct_comparison', 'ordering_list', 'relative_pos_then_compare'])
    
    if problem_type == 'direct_comparison':
        return generate_direct_comparison_problem(level)
    elif problem_type == 'ordering_list':
        return generate_ordering_list_problem(level)
    else: # relative_pos_then_compare
        return generate_relative_pos_then_compare_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for number comparison problems.
    """
    user_answer_normalized = user_answer.strip().replace(' ', '').replace('　', '').upper()
    correct_answer_normalized = correct_answer.strip().replace(' ', '').replace('　', '').upper()

    is_correct = False
    feedback = ""

    # Case 1: Direct comparison (>, <, =)
    if correct_answer_normalized in ['<', '>', '=']:
        is_correct = (user_answer_normalized == correct_answer_normalized)
        if is_correct:
            feedback = f"完全正確！答案是 ${correct_answer_normalized}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer_normalized}$"
        return {"correct": is_correct, "result": feedback, "next_question": True}

    # Case 2: Ordering list
    # User might use different separators or extra spaces, try to parse
    # Do not convert user_answer to UPPER case here, as parsing numbers might be case-sensitive (e.g., negative sign)
    user_parts = [p.strip() for p in user_answer.split(',')]
    correct_parts = [p.strip() for p in correct_answer.split(',')]

    # Check if number of elements matches
    if len(user_parts) != len(correct_parts):
        feedback = f"答案的數量不符。正確答案應為：{correct_answer}"
        return {"correct": False, "result": feedback, "next_question": True}

    try:
        user_values = [_parse_number_string_for_check(p) for p in user_parts]
        correct_values = [_parse_number_string_for_check(p) for p in correct_parts]

        # Compare floating point values with tolerance
        # All correct values must match user values in order
        is_correct = all(abs(u - c) < 1e-6 for u, c in zip(user_values, correct_values))

        if is_correct:
            feedback = f"完全正確！答案是 {correct_answer}。"
        else:
            feedback = f"答案不正確。正確答案應為：{correct_answer}"
            
    except ValueError as e:
        feedback = f"答案格式不正確。請確認您輸入的是有效的數字或分數，例如：`{correct_answer}`。詳細錯誤：{e}"
        is_correct = False
    except Exception as e:
        feedback = f"檢查答案時發生未知錯誤: {e}"
        is_correct = False

    return {"correct": is_correct, "result": feedback, "next_question": True}