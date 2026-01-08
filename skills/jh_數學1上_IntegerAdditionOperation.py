# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 50.88s | RAG: 10 examples
# Created At: 2026-01-08 22:55:09
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


 # Although not used in this specific skill, it's part of the GOLD STANDARD structure.

# --- Internal Helper Functions (if any, not explicitly requested by spec for this problem, but good practice) ---
# For this problem, the regeneration logic is embedded directly in each type function
# as per the "Loop max 100 times to regenerate" instruction.

# --- Type-specific Problem Generation Functions ---

def generate_type_1_problem():
    """
    Type 1: Addition of two negative integers, typically visualized on a number line.
    Example: 利用數線求 (-2 )＋(-5 ) 的值。 -> -7
    """
    max_attempts = 100
    
    v1 = random.randint(-10, -2)
    
    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(-10, -2)
        if temp_v2 != v1:
            v2 = temp_v2
            break
    if v2 is None: # Fallback if distinct value cannot be found in attempts
        v2 = random.choice([x for x in range(-10, -1) if x != v1]) # Guaranteed to find one if range > 1 element

    ans = v1 + v2
    
    question_text = f"利用數線求 ({v1})＋({v2}) 的值。"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_problem():
    """
    Type 2: Addition of two negative integers, similar to Type 1 but with slightly different ranges or distinctness rules.
    Example: 利用數線求 (-3 )＋(-4 ) 的值。 -> -7
    """
    max_attempts = 100
    
    v1 = random.randint(-12, -3)
    
    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(-12, -3)
        if temp_v2 != v1 and abs(temp_v2) != abs(v1):
            v2 = temp_v2
            break
    if v2 is None: # Fallback
        # This fallback is more complex as it needs to avoid both v1 and abs(v1).
        # We can iterate the range directly if max_attempts fails.
        possible_v2s = [x for x in range(-12, -2) if x != v1 and abs(x) != abs(v1)]
        if not possible_v2s: # If no such v2 exists, which is unlikely for these ranges
            # As a last resort, just pick something, might violate constraint in rare edge cases.
            v2 = random.randint(-12, -3)
        else:
            v2 = random.choice(possible_v2s)


    ans = v1 + v2
    
    question_text = f"利用數線求 ({v1})＋({v2}) 的值。"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_problem():
    """
    Type 3: Direct calculation of addition of two negative integers, presented as two sub-problems.
    Example:
    ⑴ (-9 )＋(-7 )
    ⑵ (-13 )＋(-28 ) -> ⑴ -16, ⑵ -41
    """
    max_attempts = 100
    
    v1_a = random.randint(-15, -5)
    
    v1_b = None
    for _ in range(max_attempts):
        temp_v1_b = random.randint(-15, -5)
        if temp_v1_b != v1_a:
            v1_b = temp_v1_b
            break
    if v1_b is None: v1_b = random.choice([x for x in range(-15, -4) if x != v1_a])

    v2_a = None
    for _ in range(max_attempts):
        temp_v2_a = random.randint(-30, -10)
        if abs(temp_v2_a) != abs(v1_a) and abs(temp_v2_a) != abs(v1_b):
            v2_a = temp_v2_a
            break
    if v2_a is None:
        possible_v2_as = [x for x in range(-30, -9) if abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_a = random.choice(possible_v2_as) if possible_v2_as else random.randint(-30, -10)

    v2_b = None
    for _ in range(max_attempts):
        temp_v2_b = random.randint(-30, -10)
        if temp_v2_b != v2_a and abs(temp_v2_b) != abs(v1_a) and abs(temp_v2_b) != abs(v1_b):
            v2_b = temp_v2_b
            break
    if v2_b is None:
        possible_v2_bs = [x for x in range(-30, -9) if x != v2_a and abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_b = random.choice(possible_v2_bs) if possible_v2_bs else random.randint(-30, -10)

    ans_a = v1_a + v1_b
    ans_b = v2_a + v2_b
    
    question_text = f"計算下列各式的值。\n⑴ ({v1_a})＋({v1_b})\n⑵ ({v2_a})＋({v2_b})"
    correct_answer = f"⑴ {ans_a}\n⑵ {ans_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_4_problem():
    """
    Type 4: Direct calculation of addition of two negative integers, similar to Type 3 but with different ranges/distinctness for variety.
    Example:
    ⑴ (-6 )＋(-3 )
    ⑵ (-16 )＋(-8 ) -> ⑴ -9, ⑵ -24
    """
    max_attempts = 100
    
    v1_a = random.randint(-12, -3)
    
    v1_b = None
    for _ in range(max_attempts):
        temp_v1_b = random.randint(-12, -3)
        if temp_v1_b != v1_a:
            v1_b = temp_v1_b
            break
    if v1_b is None: v1_b = random.choice([x for x in range(-12, -2) if x != v1_a])
    
    v2_a = None
    for _ in range(max_attempts):
        temp_v2_a = random.randint(-25, -7)
        if abs(temp_v2_a) != abs(v1_a) and abs(temp_v2_a) != abs(v1_b):
            v2_a = temp_v2_a
            break
    if v2_a is None:
        possible_v2_as = [x for x in range(-25, -6) if abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_a = random.choice(possible_v2_as) if possible_v2_as else random.randint(-25, -7)

    v2_b = None
    for _ in range(max_attempts):
        temp_v2_b = random.randint(-25, -7)
        if temp_v2_b != v2_a and abs(temp_v2_b) != abs(v1_a) and abs(temp_v2_b) != abs(v1_b):
            v2_b = temp_v2_b
            break
    if v2_b is None:
        possible_v2_bs = [x for x in range(-25, -6) if x != v2_a and abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_b = random.choice(possible_v2_bs) if possible_v2_bs else random.randint(-25, -7)

    ans_a = v1_a + v1_b
    ans_b = v2_a + v2_b
    
    question_text = f"計算下列各式的值。\n⑴ ({v1_a})＋({v1_b})\n⑵ ({v2_a})＋({v2_b})"
    correct_answer = f"⑴ {ans_a}\n⑵ {ans_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_5_problem():
    """
    Type 5: Addition of a positive integer and a negative integer (positive first), often visualized on a number line.
    Example: 利用數線求 2＋(-6 ) 的值。 -> -4
    """
    max_attempts = 100
    
    v1 = random.randint(2, 10)
    
    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(-10, -2)
        if abs(temp_v2) != v1 and v1 + temp_v2 != 0:
            v2 = temp_v2
            break
    if v2 is None: # Fallback
        possible_v2s = [x for x in range(-10, -1) if abs(x) != v1 and v1 + x != 0]
        v2 = random.choice(possible_v2s) if possible_v2s else random.randint(-10, -2)

    ans = v1 + v2
    
    question_text = f"利用數線求 {v1}＋({v2}) 的值。"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_6_problem():
    """
    Type 6: Addition of a negative integer and a positive integer (negative first), often visualized on a number line.
    Example: 利用數線求 (-3 )＋6 的值。 -> 3
    """
    max_attempts = 100
    
    v1 = random.randint(-10, -2)
    
    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(2, 10)
        if abs(v1) != temp_v2 and v1 + temp_v2 != 0:
            v2 = temp_v2
            break
    if v2 is None: # Fallback
        possible_v2s = [x for x in range(2, 11) if abs(v1) != x and v1 + x != 0]
        v2 = random.choice(possible_v2s) if possible_v2s else random.randint(2, 10)

    ans = v1 + v2
    
    question_text = f"利用數線求 ({v1})＋{v2} 的值。"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_7_problem():
    """
    Type 7: Direct calculation of addition of mixed sign integers, presented as two sub-problems.
    Example:
    ⑴ 13＋(-4 )
    ⑵ (-15 )＋9 -> ⑴ 9, ⑵ -6
    """
    max_attempts = 100
    
    v1_a = random.randint(10, 25)
    
    v1_b = None
    for _ in range(max_attempts):
        temp_v1_b = random.randint(-15, -2)
        if abs(temp_v1_b) != v1_a and v1_a + temp_v1_b != 0:
            v1_b = temp_v1_b
            break
    if v1_b is None:
        possible_v1_bs = [x for x in range(-15, -1) if abs(x) != v1_a and v1_a + x != 0]
        v1_b = random.choice(possible_v1_bs) if possible_v1_bs else random.randint(-15, -2)

    v2_a = None
    for _ in range(max_attempts):
        temp_v2_a = random.randint(-25, -10)
        if abs(temp_v2_a) != abs(v1_a) and abs(temp_v2_a) != abs(v1_b):
            v2_a = temp_v2_a
            break
    if v2_a is None:
        possible_v2_as = [x for x in range(-25, -9) if abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_a = random.choice(possible_v2_as) if possible_v2_as else random.randint(-25, -10)

    v2_b = None
    for _ in range(max_attempts):
        temp_v2_b = random.randint(2, 15)
        if (temp_v2_b != abs(v2_a) and v2_a + temp_v2_b != 0 and
            temp_v2_b != v1_a and temp_v2_b != abs(v1_b)):
            v2_b = temp_v2_b
            break
    if v2_b is None:
        possible_v2_bs = [x for x in range(2, 16) if (x != abs(v2_a) and v2_a + x != 0 and
                                                      x != v1_a and x != abs(v1_b))]
        v2_b = random.choice(possible_v2_bs) if possible_v2_bs else random.randint(2, 15)

    ans_a = v1_a + v1_b
    ans_b = v2_a + v2_b
    
    question_text = f"計算下列各式的值。\n⑴ {v1_a}＋({v1_b})\n⑵ ({v2_a})＋{v2_b}"
    correct_answer = f"⑴ {ans_a}\n⑵ {ans_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_8_problem():
    """
    Type 8: Direct calculation of addition of mixed sign integers, similar to Type 7 but with different ranges/distinctness.
    Example:
    ⑴ 24＋(-11 )
    ⑵ (-22 )＋6 -> ⑴ 13, ⑵ -16
    """
    max_attempts = 100
    
    v1_a = random.randint(20, 40)
    
    v1_b = None
    for _ in range(max_attempts):
        temp_v1_b = random.randint(-20, -5)
        if abs(temp_v1_b) != v1_a and v1_a + temp_v1_b != 0:
            v1_b = temp_v1_b
            break
    if v1_b is None:
        possible_v1_bs = [x for x in range(-20, -4) if abs(x) != v1_a and v1_a + x != 0]
        v1_b = random.choice(possible_v1_bs) if possible_v1_bs else random.randint(-20, -5)

    v2_a = None
    for _ in range(max_attempts):
        temp_v2_a = random.randint(-40, -20)
        if abs(temp_v2_a) != abs(v1_a) and abs(temp_v2_a) != abs(v1_b):
            v2_a = temp_v2_a
            break
    if v2_a is None:
        possible_v2_as = [x for x in range(-40, -19) if abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_a = random.choice(possible_v2_as) if possible_v2_as else random.randint(-40, -20)

    v2_b = None
    for _ in range(max_attempts):
        temp_v2_b = random.randint(5, 20)
        if (temp_v2_b != abs(v2_a) and v2_a + temp_v2_b != 0 and
            temp_v2_b != v1_a and temp_v2_b != abs(v1_b)):
            v2_b = temp_v2_b
            break
    if v2_b is None:
        possible_v2_bs = [x for x in range(5, 21) if (x != abs(v2_a) and v2_a + x != 0 and
                                                      x != v1_a and x != abs(v1_b))]
        v2_b = random.choice(possible_v2_bs) if possible_v2_bs else random.randint(5, 20)

    ans_a = v1_a + v1_b
    ans_b = v2_a + v2_b
    
    question_text = f"計算下列各式的值。\n⑴ {v1_a}＋({v1_b})\n⑵ ({v2_a})＋{v2_b}"
    correct_answer = f"⑴ {ans_a}\n⑵ {ans_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_9_problem():
    """
    Type 9: Properties of zero in addition (additive identity) and additive inverses, presented as four sub-problems.
    Example:
    ⑴ (-18 )＋0
    ⑵ 0＋(-12 )
    ⑶ (-8 )＋8
    ⑷ 13＋(-13 ) -> ⑴ -18, ⑵ -12, ⑶ 0, ⑷ 0
    """
    max_attempts = 100
    
    v1 = random.randint(-30, -5) # v1 != 0 is covered by range
    
    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(-30, -5)
        if temp_v2 != v1:
            v2 = temp_v2
            break
    if v2 is None: v2 = random.choice([x for x in range(-30, -4) if x != v1])

    v3 = None
    for _ in range(max_attempts):
        temp_v3 = random.randint(-20, -3)
        if temp_v3 != v1 and temp_v3 != v2:
            v3 = temp_v3
            break
    if v3 is None: v3 = random.choice([x for x in range(-20, -2) if x != v1 and x != v2])
    
    v5 = None
    for _ in range(max_attempts):
        temp_v5 = random.randint(3, 20)
        if temp_v5 != abs(v1) and temp_v5 != abs(v2) and temp_v5 != abs(v3):
            v5 = temp_v5
            break
    if v5 is None:
        possible_v5s = [x for x in range(3, 21) if x != abs(v1) and x != abs(v2) and x != abs(v3)]
        v5 = random.choice(possible_v5s) if possible_v5s else random.randint(3, 20)
            
    v4 = -v3
    v6 = -v5
    
    ans_a = v1 + 0
    ans_b = 0 + v2
    ans_c = v3 + v4
    ans_d = v5 + v6
    
    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ ({v1})＋0\n"
        f"⑵ 0＋({v2})\n"
        f"⑶ ({v3})＋{v4}\n" # If v4 is positive, no parentheses.
        f"⑷ {v5}＋({v6})"  # If v6 is negative, with parentheses.
    )
    correct_answer = (
        f"⑴ {ans_a}\n"
        f"⑵ {ans_b}\n"
        f"⑶ {ans_c}\n"
        f"⑷ {ans_d}"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_10_problem():
    """
    Type 10: Addition of three integers, including a larger number, often demonstrating grouping for easier calculation.
    Example: 計算 (-23 )＋1205＋(-77 ) 的值。 -> 1105
    """
    max_attempts = 100
    
    v1 = None
    for _ in range(max_attempts):
        temp_v1 = random.randint(-50, -10)
        if temp_v1 % 10 != 0:
            v1 = temp_v1
            break
    if v1 is None: v1 = random.choice([x for x in range(-50, -9) if x % 10 != 0])

    v3 = None
    for _ in range(max_attempts):
        temp_v3 = random.randint(-50, -10)
        if temp_v3 != v1 and (v1 + temp_v3) % 10 == 0:
            v3 = temp_v3
            break
    if v3 is None:
        possible_v3s = [x for x in range(-50, -9) if x != v1 and (v1 + x) % 10 == 0]
        v3 = random.choice(possible_v3s) if possible_v3s else random.randint(-50, -10) # Fallback, might not satisfy condition

    v2 = None
    for _ in range(max_attempts):
        temp_v2 = random.randint(1000, 2000)
        if temp_v2 % 100 != 0 and abs(temp_v2) != abs(v1 + v3):
            v2 = temp_v2
            break
    if v2 is None:
        possible_v2s = [x for x in range(1000, 2001) if x % 100 != 0 and abs(x) != abs(v1 + v3)]
        v2 = random.choice(possible_v2s) if possible_v2s else random.randint(1000, 2000)

    ans = v1 + v2 + v3
    
    question_text = f"計算 ({v1})＋{v2}＋({v3}) 的值。"
    correct_answer = str(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_11_problem():
    """
    Type 11: Addition of three integers, demonstrating associative property and grouping,
             including additive inverse cancellation, presented as two sub-problems.
    Example:
    ⑴ 120＋(-50 )＋(-120 )
    ⑵ (-35 )＋1500＋(-65 ) -> ⑴ -50, ⑵ 1400
    """
    max_attempts = 100
    
    v1_a = random.randint(100, 200)
    
    v1_b = None
    for _ in range(max_attempts):
        temp_v1_b = random.randint(-100, -20)
        if abs(temp_v1_b) != v1_a:
            v1_b = temp_v1_b
            break
    if v1_b is None: v1_b = random.choice([x for x in range(-100, -19) if abs(x) != v1_a])

    v1_c = -v1_a
    ans_a = v1_a + v1_b + v1_c

    v2_a = None
    for _ in range(max_attempts):
        temp_v2_a = random.randint(-50, -10)
        if abs(temp_v2_a) != abs(v1_a) and abs(temp_v2_a) != abs(v1_b):
            v2_a = temp_v2_a
            break
    if v2_a is None:
        possible_v2_as = [x for x in range(-50, -9) if abs(x) != abs(v1_a) and abs(x) != abs(v1_b)]
        v2_a = random.choice(possible_v2_as) if possible_v2_as else random.randint(-50, -10)

    v2_b = None
    for _ in range(max_attempts):
        temp_v2_b = random.randint(1000, 2000)
        if (temp_v2_b % 10 != 0 and abs(temp_v2_b) != abs(v1_a) and
            abs(temp_v2_b) != abs(v1_b)):
            v2_b = temp_v2_b
            break
    if v2_b is None:
        possible_v2_bs = [x for x in range(1000, 2001) if (x % 10 != 0 and abs(x) != abs(v1_a) and
                                                          abs(x) != abs(v1_b))]
        v2_b = random.choice(possible_v2_bs) if possible_v2_bs else random.randint(1000, 2000)

    v2_c = None
    for _ in range(max_attempts):
        temp_v2_c = random.randint(-50, -10)
        if (temp_v2_c != v2_a and abs(temp_v2_c) != abs(v1_a) and
            abs(temp_v2_c) != abs(v1_b) and (v2_a + temp_v2_c) % 10 == 0):
            v2_c = temp_v2_c
            break
    if v2_c is None:
        possible_v2_cs = [x for x in range(-50, -9) if (x != v2_a and abs(x) != abs(v1_a) and
                                                        abs(x) != abs(v1_b) and (v2_a + x) % 10 == 0)]
        v2_c = random.choice(possible_v2_cs) if possible_v2_cs else random.randint(-50, -10)

    ans_b = v2_a + v2_b + v2_c
    
    question_text = (
        f"計算下列各式的值。\n"
        f"⑴ {v1_a}＋({v1_b})＋({v1_c})\n"
        f"⑵ ({v2_a})＋{v2_b}＋({v2_c})"
    )
    correct_answer = (
        f"⑴ {ans_a}\n"
        f"⑵ {ans_b}"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Dispatcher ---

def generate(level=1):
    """
    Generates a random integer addition problem based on the defined types.
    The 'level' parameter can be used to bias problem selection, but currently
    it defaults to a uniform random selection across all types.
    """
    problem_generators = [
        generate_type_1_problem,
        generate_type_2_problem,
        generate_type_3_problem,
        generate_type_4_problem,
        generate_type_5_problem,
        generate_type_6_problem,
        generate_type_7_problem,
        generate_type_8_problem,
        generate_type_9_problem,
        generate_type_10_problem,
        generate_type_11_problem,
    ]

    # For now, a simple random choice.
    # In a more advanced system, 'level' could filter or weight choices.
    selected_generator = random.choice(problem_generators)
    return selected_generator()

# --- Check Function (as per GOLD STANDARD structure) ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles both single-line and multi-line answers.
    """
    user_answer_processed = user_answer.strip().replace(' ', '').replace('\t', '').upper()
    correct_answer_processed = correct_answer.strip().replace(' ', '').replace('\t', '').upper()
    
    is_correct = (user_answer_processed == correct_answer_processed)
    
    if not is_correct:
        # Attempt float comparison for single numerical answers
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # Not a simple float comparison, rely on string comparison

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：\n${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}

