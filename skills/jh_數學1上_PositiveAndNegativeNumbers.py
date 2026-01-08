# ==============================================================================
# ID: jh_數學1上_PositiveAndNegativeNumbers
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 105.44s | RAG: 3 examples
# Created At: 2026-01-08 23:01:42
# Fix Status: [Clean Pass]
# ==============================================================================


import random
import math
from fractions import Fraction

def to_latex(num):
    """Convert number to LaTeX (integers, decimals, fractions, mixed numbers)"""
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            if rem == 0: return f"{sign}{abs(num).numerator // abs(num).denominator}"
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Format negative numbers with parentheses"""
    if num < 0: return f"({to_latex(num)})"
    return to_latex(num)

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result



import re

# --- Helper Functions for Type 3 ---

def _format_number_for_display(num_obj):
    """
    Formats a number (int, float, Fraction) into its display string,
    applying LaTeX for fractions/mixed numbers.
    """
    if isinstance(num_obj, int):
        return str(num_obj)
    elif isinstance(num_obj, float):
        if num_obj.is_integer():
            return str(int(num_obj))
        return str(num_obj)
    elif isinstance(num_obj, Fraction):
        sign = "-" if num_obj < 0 else ""
        abs_frac = abs(num_obj)
        
        if abs_frac.denominator == 1: # It's an integer (e.g., Fraction(4,1))
            return str(int(num_obj))
        
        if abs_frac < 1: # Proper fraction (e.g., 1/2)
            return f"${sign}\\frac{{{abs_frac.numerator}}}{{{abs_frac.denominator}}}$"
        else: # Improper fraction or mixed number (e.g., 5/2 -> 2 1/2)
            integer_part = int(abs_frac)
            fraction_part = abs_frac - integer_part
            # If fraction_part is 0, it means it was an integer fraction like 4/1, already handled.
            return f"${sign}{integer_part}\\frac{{{fraction_part.numerator}}}{{{fraction_part.denominator}}}$"
    return str(num_obj) # Fallback, should not happen

def _parse_display_string_to_float(display_str):
    """
    Parses a display string (potentially with LaTeX fractions) back to a float.
    Handles integers, decimals, proper fractions, and mixed numbers.
    """
    s = display_str.strip()
    
    # Remove outer '$' if present, and then clean up LaTeX commands for regex matching
    if s.startswith('$') and s.endswith('$'):
        s = s[1:-1]
    s = s.replace('\\frac{', 'frac{') # Replace \frac with frac for simpler regex
    s = s.replace('}{', '/') # Replace } { with /
    s = s.replace('}', '') # Remove remaining }
    
    # Check for negative sign
    is_negative = False
    if s.startswith('-'):
        is_negative = True
        s = s[1:]
    
    val = 0.0
    
    # Regex for fractions/mixed numbers: (integer_part)? frac{numerator}/{denominator}
    # Example: "2frac4/5" or "frac4/3"
    match_frac = re.match(r'^(?:(\d+))?\s*frac(\d+)/(\d+)$', s)
    
    if match_frac:
        integer_part_str, numerator_str, denominator_str = match_frac.groups()
        
        numerator = int(numerator_str)
        denominator = int(denominator_str)
        
        fraction_val = Fraction(numerator, denominator)
        
        if integer_part_str:
            integer_part = int(integer_part_str)
            val = float(integer_part + fraction_val)
        else:
            val = float(fraction_val)
    else:
        # Assume it's an integer or decimal
        try:
            val = float(s)
        except ValueError:
            # If parsing fails, return 0.0, but this indicates an issue in string generation/parsing logic.
            # For robust production systems, one might log this or raise an error.
            # For this exercise, assume inputs are well-formed.
            return 0.0

    return val * (-1 if is_negative else 1)

def _get_sign(num_val):
    """Returns 1 for positive, -1 for negative, 0 for zero."""
    if num_val > 0:
        return 1
    elif num_val < 0:
        return -1
    return 0

# --- Problem Type 1 ---
def generate_type_1_problem():
    scenarios = [
        ("學校的位置", "東邊", "西邊", "公里", "超市", "醫院"),
        ("第一次小考分數", "進步", "退步", "分", "小妍", "小翊"),
        ("海平面", "上方", "下方", "公尺", "海鳥", "潛水艇"),
        ("銀行存款", "存入", "提領", "元", "存入", "提領"),
        ("基準點", "向右", "向左", "單位", "甲", "乙")
    ]
    
    ref_point_str, pos_direction_str, neg_direction_str, unit_str, item_pos_str, item_neg_str = random.choice(scenarios)
    
    pos_value = random.randint(3, 20)
    
    retry_count = 0
    while True:
        neg_value = random.randint(3, 20)
        if neg_value != pos_value:
            break
        retry_count += 1
        if retry_count > 100:
            # Fallback for extreme cases, though unlikely with these ranges
            neg_value = pos_value + 1 if pos_value < 20 else pos_value - 1
            if neg_value == pos_value: # If still equal after fallback, adjust again
                neg_value = pos_value + 2 if pos_value <= 18 else pos_value - 2 # Ensure it stays in range
            break

    question_text = (
        f"以{ref_point_str}為基準，{ref_point_str}的{pos_direction_str}當作正向，"
        f"{ref_point_str}的{neg_direction_str}為負向。若{item_pos_str}位在{ref_point_str}的{pos_direction_str} "
        f"${pos_value}$ {unit_str}處，記為「＋{pos_value}」{unit_str}，則{item_neg_str}位在{ref_point_str}的"
        f"{neg_direction_str} ${neg_value}$ {unit_str}處，應該怎麼記錄？"
    )
    correct_answer = f"-{neg_value} {unit_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Problem Type 2 ---
def generate_type_2_problem():
    scenario_data = [
        ("花店老闆每賣出一盆花，就會記錄這筆交易的賺賠情形", "賺錢", "賠錢", "元", "盆花"),
        ("小明在玩一款遊戲，他以『＋』表示獲得金幣，以『-』表示花費金幣", "獲得金幣", "花費金幣", "金幣", "件商品"),
        ("某公司的營收計算方式", "盈利", "虧損", "萬元", "專案"),
        ("便利商店計算庫存變化", "進貨", "出貨", "個", "商品")
    ]
    
    context_prefix, pos_meaning, neg_meaning, unit, item_type = random.choice(scenario_data)
    
    example_pos_val = random.randrange(50, 501, 10)
    
    retry_count = 0
    while True:
        part1_neg_val = random.randrange(50, 501, 10)
        if part1_neg_val != example_pos_val:
            break
        retry_count += 1
        if retry_count > 100:
            part1_neg_val = example_pos_val + 10 if example_pos_val < 500 else example_pos_val - 10
            if part1_neg_val == example_pos_val:
                part1_neg_val = example_pos_val + 20 if example_pos_val <= 480 else example_pos_val - 20
            break
            
    cost_price = random.randrange(300, 1001, 10)
    
    retry_count = 0
    while True:
        selling_price = random.randrange(200, 901, 10)
        if selling_price < cost_price and (cost_price - selling_price) >= 50:
            break
        retry_count += 1
        if retry_count > 100:
            # Force a valid pair if too many retries
            max_selling_price_for_loss = cost_price - 50
            min_selling_price_allowed = 200
            
            # Ensure the range for random.randrange is valid
            if max_selling_price_for_loss < min_selling_price_allowed:
                # This scenario should not happen with current constraints:
                # cost_price min is 300, so max_selling_price_for_loss min is 250.
                # min_selling_price_allowed is 200. So 250 >= 200.
                selling_price = min_selling_price_allowed # Fallback to lowest possible loss
            else:
                selling_price = random.randrange(min_selling_price_allowed, max_selling_price_for_loss + 1, 10)
            break

    part2_diff_val = selling_price - cost_price
    
    question_text = (
        f"{context_prefix}，他以「＋」表示{pos_meaning}，以「-」表示{neg_meaning}，"
        f"例如：{pos_meaning}了 ${example_pos_val}$ {unit}，就記為＋{example_pos_val} {unit}。試回答下列問題：\n"
        f"⑴ 若{neg_meaning}了 ${part1_neg_val}$ {unit}，應該怎麼記錄？\n"
        f"⑵ 若一{item_type}的成本是 ${cost_price}$ {unit}，以 ${selling_price}$ {unit}售出，則老闆應該怎麼記錄？"
    )
    
    correct_answer = f"⑴ -{part1_neg_val} {unit}\n⑵ {part2_diff_val} {unit}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Problem Type 3 ---
def generate_type_3_problem():
    generated_numbers_data = [] # Stores (numerical_value_float, display_string)
    generated_values_set = set() # Stores float values for uniqueness check
    
    num_to_generate = random.randint(6, 8)
    
    # Track types to ensure diversity as per spec (implied by "diverse, including...")
    generated_types_count = {
        "pos_int": 0, "neg_int": 0, "zero": 0, 
        "pos_dec": 0, "neg_dec": 0, 
        "pos_frac": 0, "neg_frac": 0
    }
    all_num_types = list(generated_types_count.keys())
    
    retry_outer_loop = 0
    while len(generated_numbers_data) < num_to_generate and retry_outer_loop < 200:
        # Prioritize types that haven't been generated yet to ensure diversity
        available_types = [t for t, count in generated_types_count.items() if count == 0]
        if not available_types:
            available_types = all_num_types # All types generated at least once, now pick randomly
        
        num_type_choice = random.choice(available_types)
        
        num_obj = None
        
        if num_type_choice == "pos_int":
            num_obj = random.randint(1, 20)
        elif num_type_choice == "neg_int":
            num_obj = random.randint(-20, -1)
        elif num_type_choice == "zero":
            num_obj = 0
        elif num_type_choice == "pos_dec":
            num_obj = round(random.uniform(0.1, 10.0), 1)
        elif num_type_choice == "neg_dec":
            num_obj = round(random.uniform(-10.0, -0.1), 1)
        elif num_type_choice == "pos_frac":
            is_mixed = random.choice([True, False])
            if is_mixed:
                integer_part = random.randint(1, 5)
                numerator = random.randint(1, 5)
                # Ensure denominator > numerator for proper fraction part
                denominator = random.randint(numerator + 1, 6) if numerator < 6 else 6
                if denominator <= numerator: # Fallback if random choice made it improper
                    denominator = numerator + 1
                num_obj = integer_part + Fraction(numerator, denominator)
            else: # Proper or improper fraction
                numerator = random.randint(1, 5)
                denominator = random.randint(2, 6)
                num_obj = Fraction(numerator, denominator)
        elif num_type_choice == "neg_frac":
            is_mixed = random.choice([True, False])
            if is_mixed:
                integer_part = random.randint(1, 5)
                numerator = random.randint(1, 5)
                denominator = random.randint(numerator + 1, 6) if numerator < 6 else 6
                if denominator <= numerator:
                    denominator = numerator + 1
                num_obj = -(integer_part + Fraction(numerator, denominator))
            else: # Proper or improper fraction
                numerator = random.randint(1, 5)
                denominator = random.randint(2, 6)
                num_obj = -Fraction(numerator, denominator)
        
        if num_obj is not None:
            float_val = float(num_obj)
            if float_val not in generated_values_set:
                generated_values_set.add(float_val)
                generated_numbers_data.append((float_val, _format_number_for_display(num_obj)))
                generated_types_count[num_type_choice] += 1
        
        retry_outer_loop += 1
        
    # Fallback to ensure `num_to_generate` is met if `retry_outer_loop` was exhausted
    while len(generated_numbers_data) < num_to_generate:
        num_obj = random.randint(-20, 20) # Simple integers as fallback
        float_val = float(num_obj)
        if float_val not in generated_values_set:
            generated_values_set.add(float_val)
            generated_numbers_data.append((float_val, _format_number_for_display(num_obj)))

    random.shuffle(generated_numbers_data) # Shuffle for display order

    num_list_display_str = [data[1] for data in generated_numbers_data]
    
    ref_num_str = None
    ref_num_val = None
    
    # Select ref_num_str, ensuring it's not 0 and has at least one other same-sign number
    retry_ref_selection = 0
    while retry_ref_selection < 100:
        candidate_data = random.choice(generated_numbers_data)
        candidate_val, candidate_str = candidate_data
        
        if candidate_val == 0: # Reference number cannot be zero
            retry_ref_selection += 1
            continue
        
        same_sign_count = 0
        for val, _ in generated_numbers_data:
            if val != candidate_val and _get_sign(val) == _get_sign(candidate_val):
                same_sign_count += 1
        
        if same_sign_count >= 1: # Must have at least one other number with same sign
            ref_num_str = candidate_str
            ref_num_val = candidate_val
            break
        
        retry_ref_selection += 1
    
    # Fallback if no suitable ref_num_str found after retries (e.g., only one non-zero number)
    if ref_num_str is None:
        # Try to find any non-zero number for reference, even if it doesn't have a same-sign partner
        # This makes the "same sign" question potentially "無", which is valid.
        for val, s_str in generated_numbers_data:
            if val != 0:
                ref_num_str = s_str
                ref_num_val = val
                break
        if ref_num_str is None: # If all numbers are 0 (extremely rare, but robust)
            ref_num_str = generated_numbers_data[0][1]
            ref_num_val = generated_numbers_data[0][0]


    # Classify numbers
    negative_numbers_data = []
    integers_data = []
    same_sign_numbers_data = [] # (float_val, display_string)

    for val, s_str in generated_numbers_data:
        if val < 0:
            negative_numbers_data.append((val, s_str))
        
        if val == int(val): # Check if it's an integer
            integers_data.append((val, s_str))
        
        # Check for same sign, exclude the reference number itself
        if val != ref_num_val and _get_sign(val) == _get_sign(ref_num_val):
            same_sign_numbers_data.append((val, s_str))
            
    # Sort classified lists numerically
    negative_numbers_data.sort(key=lambda x: x[0])
    integers_data.sort(key=lambda x: x[0])
    same_sign_numbers_data.sort(key=lambda x: x[0])

    negative_numbers_display = [data[1] for data in negative_numbers_data]
    integers_display = [data[1] for data in integers_data]
    same_sign_numbers_display = [data[1] for data in same_sign_numbers_data]

    negative_numbers_display_or_無 = negative_numbers_display if negative_numbers_display else ["無"]
    integers_display_or_無 = integers_display if integers_display else ["無"]
    same_sign_numbers_display_or_無 = same_sign_numbers_display if same_sign_numbers_display else ["無"]

    question_text = (
        f"下列各數中，哪些是負數？哪些是整數？哪些與{ref_num_str}是同號數？\n"
        f"{ ' '.join(num_list_display_str) }"
    )
    
    correct_answer = (
        f"負數：{ '、'.join(negative_numbers_display_or_無) }；"
        f"整數：{ '、'.join(integers_display_or_無) }；"
        f"{ref_num_str} 的同號數：{ '、'.join(same_sign_numbers_display_or_無) }"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Check Function (from Gold Standard) ---
def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Try comparing as floats if possible (for simple numerical answers)
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # Not a simple numerical answer, or non-parseable.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}

# --- Main Dispatcher ---
def generate(level=1):
    """
    生成「正負數」相關題目。
    """
    problem_type = random.choice(['type_1', 'type_2', 'type_3'])
    
    if problem_type == 'type_1':
        return generate_type_1_problem()
    elif problem_type == 'type_2':
        return generate_type_2_problem()
    else: # type_3
        return generate_type_3_problem()
