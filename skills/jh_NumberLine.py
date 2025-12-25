import random
from fractions import Fraction
import math # For math.floor, math.ceil, math.fabs

# --- Helper functions for formatting ---
def format_number(num):
    """
    Formats a number (integer, float, or Fraction) into a string,
    converting fractions to mixed numbers with LaTeX formatting.
    """
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        else:
            # Handle mixed numbers for fractions with absolute value >= 1
            if abs(num) >= 1:
                integer_part = num.numerator // num.denominator
                fraction_part_num = abs(num.numerator % num.denominator)
                fraction_part_den = num.denominator
                
                # If negative, integer_part will be negative.
                # Mixed number format for negative is - (integer part) (fraction part)
                # e.g., -3 2/3, not -3 -2/3
                if integer_part < 0 and fraction_part_num > 0:
                    return f"{integer_part} \\frac{{{fraction_part_num}}}{{{fraction_part_den}}}"
                elif integer_part == 0 and num < 0: # e.g. -1/2
                     return f"-\\frac{{{fraction_part_num}}}{{{fraction_part_den}}}"
                else: # positive mixed number or integer (already handled by denom=1)
                    return f"{integer_part} \\frac{{{fraction_part_num}}}{{{fraction_part_den}}}"
            else: # Proper fraction (absolute value < 1)
                return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    elif isinstance(num, float):
        if num == int(num): # If float is an integer value, display as int
            return str(int(num))
        else:
            # Limit decimal places to avoid long floats
            return f"{num:.1f}" if num * 10 == int(num * 10) else f"{num:.2f}"
    else: # integer
        return str(num)

def generate(level=1):
    """
    生成「數線」相關題目。
    包含：
    1. 數線三要素或基本概念
    2. 標記整數點的描述 (填空)
    3. 標記分數/小數點的描述 (填空)
    4. 讀取標記點的座標 (ASCII art)
    5. 相對位置 (A點在B點左/右X單位)
    6. 座標大小比較 (哪一點最左/右)
    7. 中點座標
    8. 數線讀值 (單點填空, ASCII art)
    """
    problem_types = [
        'number_line_basics_identify',
        'mark_integer_fill_in',
        'mark_fraction_decimal_details',
        'read_labeled_points',
        'relative_pos',
        'comparison',
        'midpoint',
        'ascii_read'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'number_line_basics_identify':
        return generate_number_line_basics_identify_problem()
    elif problem_type == 'mark_integer_fill_in':
        return generate_mark_integer_fill_in_problem()
    elif problem_type == 'mark_fraction_decimal_details':
        return generate_mark_fraction_decimal_details_problem()
    elif problem_type == 'read_labeled_points':
        return generate_read_labeled_points_problem()
    elif problem_type == 'relative_pos':
        return generate_relative_pos_problem()
    elif problem_type == 'comparison':
        return generate_comparison_problem()
    elif problem_type == 'midpoint':
        return generate_midpoint_problem()
    else: # ascii_read
        return generate_ascii_read_problem()

def generate_number_line_basics_identify_problem():
    question_template = random.choice([
        "數線上的三要素為何？請依序寫出。",
        "數線上的「原點」代表哪個數字？",
        "在數線上，數字越大表示位置越偏哪一邊？"
    ])

    if question_template.startswith("數線上的三要素"):
        question_text = question_template
        # Canonical answer for auto-grading
        correct_answer = "原點,正向,單位長"
    elif question_template.startswith("數線上的「原點」"):
        question_text = question_template
        correct_answer = "0"
    else: # "數字越大表示位置越偏哪一邊？"
        question_text = question_template
        correct_answer = "右"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_mark_integer_fill_in_problem():
    val = random.randint(-10, 10)
    while val == 0: # Avoid 0 as it's a special case "at origin"
        val = random.randint(-10, 10)

    direction = "右" if val > 0 else "左"
    units = abs(val)

    question_text = f"要在數線上標記 $P({val})$，應從原點向{{方向}}移動{{單位數}}個單位長。請依序填入方向和單位數。"
    correct_answer = f"{direction},{units}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_mark_fraction_decimal_details_problem():
    is_fraction = random.choice([True, False])
    
    if is_fraction:
        denom = random.randint(2, 5) # Denominator for fractions (e.g., 2, 3, 4, 5)
        num_abs = random.randint(denom + 1, denom * 4) # Numerator to create a mixed number
        
        # Ensure it's not an exact integer
        while num_abs % denom == 0:
            num_abs = random.randint(denom + 1, denom * 4)

        num = num_abs if random.random() < 0.5 else -num_abs
        
        val_frac = Fraction(num, denom)
        val_str = format_number(val_frac)

        # Determine bounding integers and description
        if val_frac > 0:
            lower_int = math.floor(val_frac)
            upper_int = math.ceil(val_frac)
            # The fraction part of val_frac (e.g., 1/2 for 3 1/2)
            offset_from_lower_frac = val_frac - lower_int
            subdivisions = offset_from_lower_frac.denominator
            offset_count = offset_from_lower_frac.numerator
            start_point_str = str(lower_int)
            move_direction = "右"
        else: # val_frac < 0
            # For -3 2/3, lower_int is -4, upper_int is -3
            lower_int = math.floor(val_frac)
            upper_int = math.ceil(val_frac)
            
            # The positive fraction part from the upper integer (e.g., 1/3 for -3 2/3 to get to -4)
            offset_from_upper_frac = Fraction(upper_int) - val_frac
            subdivisions = offset_from_upper_frac.denominator
            offset_count = offset_from_upper_frac.numerator
            start_point_str = str(upper_int)
            move_direction = "左"

    else: # Decimal
        integer_part = random.randint(-5, 5)
        decimal_part = random.randint(1, 9) # One decimal place
        val_float = float(f"{integer_part}.{decimal_part}")
        
        # Ensure it's not 0.0, and make it negative sometimes
        if random.random() < 0.5 and val_float == 0.0:
            val_float = float(f"{random.randint(1,5)}.{random.randint(1,9)}")
            if random.random() < 0.5: val_float = -val_float
        elif val_float == 0.0: # If it randomly picked 0.0, pick a new non-zero one.
            val_float = float(f"{random.randint(-5,5)}.{random.randint(1,9)}")

        val_str = format_number(val_float)

        if val_float > 0:
            lower_int = math.floor(val_float)
            upper_int = math.ceil(val_float)
            subdivisions = 10
            offset_count = int(round((val_float - lower_int) * 10))
            start_point_str = str(lower_int)
            move_direction = "右"
        else: # val_float < 0
            lower_int = math.floor(val_float)
            upper_int = math.ceil(val_float)
            subdivisions = 10
            # For -3.7, upper_int is -3. Offset is -3 - (-3.7) = 0.7, so count is 7
            offset_count = int(round((upper_int - val_float) * 10))
            start_point_str = str(upper_int)
            move_direction = "左"

    # Construct the question
    question_text = f"要在數線上標記 $P({{{val_str}}})$，應該：<br>" \
                    f"1. 位於 ${lower_int}$ 和 ${upper_int}$ 兩個整數之間。<br>" \
                    f"2. 將這段整數區間分成 ${subdivisions}$ 等分。<br>" \
                    f"3. 從 ${start_point_str}$ 點開始向{{方向}}數第{{個數}}個等分點。<br>" \
                    f"請依序填入方向和個數。"
    
    correct_answer = f"{move_direction},{offset_count}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_read_labeled_points_problem():
    num_points = random.randint(2, 4)
    start_coord_base = random.randint(-10, 0)
    unit_step = random.randint(1, 3) # Unit step between major ticks

    # Generate distinct coordinates, ensuring they align with multiples of unit_step or simple fractions
    coords = []
    # Make sure we have enough distinct base positions to choose from
    possible_offsets = list(range(-5, 6)) # Offsets from start_coord_base
    random.shuffle(possible_offsets)
    
    for _ in range(num_points):
        # Generate coordinates that are integers for simplicity in reading
        coord = start_coord_base + random.choice(possible_offsets) * unit_step
        while coord in coords:
            coord = start_coord_base + random.choice(possible_offsets) * unit_step
        coords.append(coord)
    coords.sort() 

    labels = random.sample(['A', 'B', 'C', 'D', 'E'], num_points)
    
    labeled_points = {labels[i]: coords[i] for i in range(num_points)}

    # Determine display range for ASCII art
    min_coord_display = min(coords) - unit_step * 2
    max_coord_display = max(coords) + unit_step * 2

    # Round down/up to nearest multiple of unit_step for tick marks
    min_tick_val = math.floor(min_coord_display / unit_step) * unit_step
    max_tick_val = math.ceil(max_coord_display / unit_step) * unit_step

    # Ensure some padding
    min_tick_val -= unit_step if min_tick_val > min(coords) - 3 * unit_step else 0
    max_tick_val += unit_step if max_tick_val < max(coords) + 3 * unit_step else 0

    # Ensure origin is often visible
    if -5 < min_tick_val: min_tick_val = -5
    if 5 > max_tick_val: max_tick_val = 5
    if 0 not in range(min_tick_val, max_tick_val + 1):
        if min_tick_val > 0: min_tick_val = 0 - unit_step
        if max_tick_val < 0: max_tick_val = 0 + unit_step

    # Cap the total length to prevent excessively long lines
    if max_tick_val - min_tick_val > 40:
        max_tick_val = min_tick_val + 40 # Limit to 40 units

    # Generate ASCII line and labels
    line_elements = []
    label_elements = []
    current_label_pos = {} # Map coordinate to a short label like A, B etc.

    for label, coord in labeled_points.items():
        current_label_pos[coord] = label

    # Create the number line visual
    for i in range(min_tick_val, max_tick_val + 1):
        if i % unit_step == 0:
            line_elements.append("|")
            label_str = str(i)
            label_elements.append(label_str)
        else:
            line_elements.append("-")
            label_elements.append(" ") # Placeholder for alignment

    # Adjust label elements to fit under ticks, centering them
    ascii_line_str = []
    ascii_label_str = []
    
    # Calculate desired width for each segment
    segment_width = len(str(unit_step * (max_tick_val // unit_step))) + 1 # Max possible label width + 1 for padding
    if segment_width < 3: segment_width = 3 # Minimum segment width

    # Reconstruct the line and label string with padding
    line_parts = []
    label_parts = []
    
    for i in range(min_tick_val, max_tick_val + 1):
        if i % unit_step == 0:
            tick_val_str = str(i)
            # Find the center for the tick value
            current_line_segment = []
            current_label_segment = []

            # Add spaces before the actual tick mark
            if line_parts: # not first segment
                line_parts.append("-" * ((segment_width - 1 - len(str(i))) // 2))
                label_parts.append(" " * ((segment_width - 1 - len(str(i))) // 2))

            line_parts.append("|") # The actual tick
            label_parts.append(tick_val_str) # The value below it

            # Add spaces after the tick mark
            line_parts.append("-" * (segment_width - len(str(i)) - ((segment_width - 1 - len(str(i))) // 2) ))
            label_parts.append(" " * (segment_width - len(str(i)) - ((segment_width - 1 - len(str(i))) // 2) ))
            
        else: # Minor ticks
            line_parts.append("-")
            label_parts.append(" ")

    # Now, try to place point labels above the line carefully
    # Create an empty line for point labels
    point_label_line = [' '] * len("".join(line_parts))

    current_pos_in_line = 0
    for i in range(min_tick_val, max_tick_val + 1):
        is_major_tick = (i % unit_step == 0)
        
        # Calculate the start of the section for this coordinate
        if is_major_tick:
            s_val = str(i)
            part_len = len(s_val)
            center_offset = (part_len - 1) // 2 # How many chars to the left of the center of the label

            # Find the actual position of the tick character in the 'line_parts' string
            tick_char_idx_in_line = len("".join(line_parts[:current_pos_in_line])) + (segment_width - part_len) // 2
            
            # Place point label above the tick if there is one
            if i in current_label_pos:
                label_char = current_label_pos[i]
                if tick_char_idx_in_line >= 0 and tick_char_idx_in_line < len(point_label_line):
                    point_label_line[tick_char_idx_in_line] = label_char
            current_pos_in_line += segment_width 
        else: # minor tick
            current_pos_in_line += 1
            if i in current_label_pos: # If a label happens to be on a minor tick, place it.
                label_char = current_label_pos[i]
                if current_pos_in_line - 1 >= 0 and current_pos_in_line - 1 < len(point_label_line):
                     point_label_line[current_pos_in_line - 1] = label_char


    final_ascii_line = "".join(point_label_line) + "\n" + "".join(line_parts) + "\n" + "".join(label_parts)

    question_text = f"請觀察數線，並寫出各點的座標。例如：$A(5)$<br>"
    question_text += f"```\n{final_ascii_line}\n```<br>"
    question_text += f"請依序寫出點 {'、'.join(sorted(labeled_points.keys()))} 的座標。"

    # Sort answers by label for consistent checking
    sorted_labels = sorted(labeled_points.keys())
    correct_answer_parts = [f"{label}({labeled_points[label]})" for label in sorted_labels]
    correct_answer = ", ".join(correct_answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_relative_pos_problem():
    # 題型：數線上 A 點座標為 val_a，B 點在 A 點的 [方向] val_diff 單位處
    val_a = random.randint(-10, 10)
    val_diff = random.randint(1, 10)
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b = val_a + val_diff
    else:
        val_b = val_a - val_diff
        
    question_text = f"數線上 $A$ 點座標為 ${val_a}$，$B$ 點在 $A$ 點的{direction}邊 ${val_diff}$ 單位處，請問 $B$ 點座標為何？"
    correct_answer = str(val_b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    # 題型：已知 A(a), B(b), C(c)...
    points = {}
    labels = ['A', 'B', 'C', 'D']
    num_points = random.choice([3, 4])
    used_labels = labels[:num_points]
    
    coords = random.sample(range(-20, 21), num_points)
    
    points_desc = []
    for i, label in enumerate(used_labels):
        points[label] = coords[i]
        points_desc.append(f"${label}({coords[i]})$")
        
    target = random.choice(['左', '右'])
    
    if target == '右':
        correct_label = max(points, key=points.get)
    else:
        correct_label = min(points, key=points.get)
        
    question_text = f"已知數線上 {', '.join(points_desc)}，請問哪一點在最{target}邊？(請填代號)"
    correct_answer = correct_label
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    val_a = random.randint(-15, 15)
    diff = random.randint(1, 10) * 2 
    
    if random.random() < 0.3: # Allow odd difference, leading to decimal/fraction midpoint
        diff = random.randint(1, 10) * 2 + 1
        
    val_b = val_a + diff
    midpoint = (val_a + val_b) / 2
    
    # Convert to fraction for accuracy and desired output format
    midpoint_frac = Fraction(midpoint).limit_denominator(100)
    midpoint_str = format_number(midpoint_frac)
        
    question_text = f"數線上兩點 $A({val_a})$、$B({val_b})$，請問 $A$、$B$ 兩點的中點座標為何？"
    correct_answer = midpoint_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ascii_read_problem():
    start = random.randint(-10, 5)
    step = random.randint(1, 3)
    length = 5
    
    sequence = [start + i*step for i in range(length)]
    missing_idx = random.randint(1, length-2) # Ensure missing is not at ends
    missing_val = sequence[missing_idx]
    
    display_seq = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_seq.append(" ( ? ) ") # Add space for better ASCII display
        else:
            display_seq.append(f" {str(val)} ") # Add space
            
    # Remove leading/trailing spaces from each formatted number for better join
    ascii_art = " -- ".join([s.strip() for s in display_seq])

    question_text = f"請觀察下列數線上的刻度變化，填入括號中的數字：<br>```\n{ascii_art}\n```"
    correct_answer = str(missing_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_norm = user_answer.strip().replace(' ', '').replace('，', ',')
    correct_answer_norm = correct_answer.strip().replace(' ', '').replace('，', ',')
    
    is_correct = False

    # 1. Direct string comparison (case-insensitive for some parts)
    if user_answer_norm.lower() == correct_answer_norm.lower():
        is_correct = True
    else:
        # 2. Try numerical comparison for single numbers
        try:
            # First try float (covers integers and decimals)
            float_user = float(user_answer_norm)
            float_correct = float(correct_answer_norm)
            if math.isclose(float_user, float_correct, rel_tol=1e-9, abs_tol=1e-9):
                is_correct = True
        except ValueError:
            # If float fails, try Fraction comparison (covers fractions)
            try:
                frac_user = Fraction(user_answer_norm)
                frac_correct = Fraction(correct_answer_norm)
                if frac_user == frac_correct:
                    is_correct = True
            except ValueError:
                # 3. For comma-separated answers (e.g., "原點,正向,單位長" or "右,3" or "A(1),B(3)")
                user_parts = [p.strip().lower() for p in user_answer_norm.split(',')]
                correct_parts = [p.strip().lower() for p in correct_answer_norm.split(',')]
                
                if len(user_parts) == len(correct_parts):
                    all_parts_match = True
                    for u_part, c_part in zip(user_parts, correct_parts):
                        if u_part != c_part:
                            # Try numerical comparison for individual parts
                            try:
                                if math.isclose(float(u_part), float(c_part), rel_tol=1e-9, abs_tol=1e-9):
                                    continue
                            except ValueError:
                                # Also check for label-coordinate pairs like A(1)
                                if (u_part.startswith(c_part.split('(')[0]) and # label part matches
                                    len(u_part) > 1 and len(c_part) > 1 and # ensure not just a label
                                    u_part.replace('(', ' ').replace(')', ' ').split()[1] == c_part.replace('(', ' ').replace(')', ' ').split()[1]):
                                    continue # coordinates match for labeled points
                                else:
                                    all_parts_match = False
                                    break
                    if all_parts_match:
                        is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}