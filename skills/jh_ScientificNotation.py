import random
from fractions import Fraction
import re
from decimal import Decimal, getcontext

# Set precision for Decimal calculations to avoid floating point issues
getcontext().prec = 20

def parse_scientific_notation_string(s):
    """
    Parses a string representing a number in scientific notation or a general number
    and returns its canonical (a, n) pair where 1 <= |a| < 10.
    Handles various formats like "9.3x10^8", "9.3E8", "930000000".
    Returns (Decimal(a), int(n)) or (None, None) if parsing fails.
    """
    s = s.strip()
    if s.startswith('$') and s.endswith('$'):
        s = s[1:-1] # Remove LaTeX dollar signs if present
    
    # Normalize input for easier parsing
    s = s.replace(' ', '').replace(',', '') # Remove spaces and thousands commas
    s = s.replace('\\times', 'x') # Replace LaTeX times with 'x' for regex
    
    # Attempt to parse as scientific notation (e.g., 9.3x10^8, 9.3E8)
    # The exponent might be within ^{...} or just ^... or directly after E/e
    # Pattern: (a_part) (exponent_indicator) (n_part)
    # This regex is designed to capture common formats without being overly strict on optional braces.
    pattern = r"([+\-]?\d+\.?\d*)(?:x10\^\{?|E|e)([+\-]?\d+)\}?"
    match = re.match(pattern, s)
    
    if match:
        try:
            a_val = Decimal(match.group(1))
            n_val = int(match.group(2))
            
            # Convert to canonical form 1 <= |a| < 10
            if a_val == 0:
                return Decimal('0'), 0
            
            temp_a = a_val
            temp_n = n_val

            if abs(temp_a) >= 10:
                while abs(temp_a) >= 10:
                    temp_a /= 10
                    temp_n += 1
            elif abs(temp_a) < 1 and temp_a != 0:
                while abs(temp_a) < 1:
                    temp_a *= 10
                    temp_n -= 1
            
            # Quantize 'a' to a reasonable number of decimal places for consistent comparison
            return temp_a.quantize(Decimal('0.00001')), temp_n # 5 decimal places for 'a'
        except (ValueError, TypeError):
            pass # Fall through to try raw number parsing if scientific notation parsing fails

    # If parsing as 'a x 10^n' fails, try parsing as a raw number
    try:
        val_decimal = Decimal(s)
        if val_decimal == 0:
            return Decimal('0'), 0
        
        sign = 1
        if val_decimal < 0:
            sign = -1
            val_decimal = -val_decimal

        exp_val = 0
        if val_decimal >= 1:
            while val_decimal >= 10:
                val_decimal /= 10
                exp_val += 1
        elif val_decimal > 0 and val_decimal < 1:
            while val_decimal < 1:
                val_decimal *= 10
                exp_val -= 1
        
        return (val_decimal.quantize(Decimal('0.00001')) * sign, exp_val)
    except (ValueError, TypeError):
        return None, None # Cannot parse at all

def generate(level=1):
    """
    生成科學記號相關題目。
    包含：
    1. 將一般數轉換為科學記號
    2. 根據科學記號判斷位數或小數點後第一位非零數字的位置
    3. 比較科學記號表示的數的大小
    """
    problem_type = random.choice([
        'to_scientific_notation', 
        'digit_count_or_decimal_place', 
        'comparison'
    ])
    
    if problem_type == 'to_scientific_notation':
        return generate_to_scientific_notation()
    elif problem_type == 'digit_count_or_decimal_place':
        return generate_digit_count_or_decimal_place_problem()
    else: # 'comparison'
        return generate_comparison_problem()

def generate_to_scientific_notation():
    """生成將一般數轉換為科學記號的題目。"""
    subtype = random.choice(['large_integer', 'small_decimal', 'fraction'])
    
    if subtype == 'large_integer':
        # Generate exponent for 10^n where n is the final exponent
        exponent = random.randint(7, 12) 
        # 'a' part between 1.0 and 9.99, with 1 to 4 decimal places
        a_val = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))
        
        # Construct the original number: a_val * 10^exponent
        # Convert to string and ensure it's an integer for display
        original_num_decimal = a_val * (Decimal('10') ** exponent)
        original_num_str = str(int(original_num_decimal)) # Display as integer string
        
        question_text = f"以科學記號表示下列各數： ${original_num_str}$"
        correct_answer_a = a_val.quantize(Decimal('0.00001'))
        correct_answer = f"${correct_answer_a}\\times10^{{{exponent}}}$"
        
    elif subtype == 'small_decimal':
        exponent = random.randint(-10, -5)
        a_val = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))
        
        original_num_decimal = a_val * (Decimal('10') ** exponent)
        
        # Calculate the number of total decimal places needed for display string
        a_str_parts = str(a_val).split('.')
        a_decimal_places = len(a_str_parts[1]) if len(a_str_parts) > 1 else 0

        # Ensures enough decimal places are shown, especially for leading zeros
        display_precision = max(abs(exponent) + a_decimal_places, 6) 
        original_num_str = f"{original_num_decimal:.{display_precision}f}"
        
        # Remove trailing zeros after the decimal point if they are not significant
        if '.' in original_num_str:
            original_num_str = original_num_str.rstrip('0')
            if original_num_str.endswith('.'): # If it ends with '.', e.g., "0."
                original_num_str += '0' # Make it "0.0"
        
        question_text = f"以科學記號表示下列各數： ${original_num_str}$"
        correct_answer_a = a_val.quantize(Decimal('0.00001'))
        correct_answer = f"${correct_answer_a}\\times10^{{{exponent}}}$"

    else: # fraction
        numerator = random.randint(1, 9)
        exponent = random.randint(5, 10)
        
        question_text = f"以科學記號表示下列各數： $\\frac{{{numerator}}}{{10^{{{exponent}}}}}$"
        correct_answer = f"${numerator}\\times10^{{{-exponent}}}$"
        
    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_digit_count_or_decimal_place_problem():
    """
    生成判斷位數或小數點後第一位非零數字位置的題目。
    """
    subtype = random.choice(['large_num_digits', 'small_num_decimal_place'])
    a_val = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))
    
    if subtype == 'large_num_digits':
        exponent = random.randint(6, 12) # Positive exponent for large numbers
        scientific_num_str = f"${a_val}\\times10^{{{exponent}}}$"
        # For a number like X.YZ * 10^n, it has n+1 digits.
        num_digits = exponent + 1 
        
        question_text = f"若將 ${a_val}\\times10^{{{exponent}}}$ 乘開，則這個數是幾位數？"
        correct_answer = str(num_digits)
    else: # small_num_decimal_place
        exponent = random.randint(-10, -4) # Negative exponent for small numbers
        scientific_num_str = f"${a_val}\\times10^{{{exponent}}}$"
        # For a number like X.YZ * 10^-n, the first non-zero digit appears at the n-th decimal place.
        decimal_place = abs(exponent) 
        
        question_text = f"若將 ${a_val}\\times10^{{{exponent}}}$ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
        correct_answer = str(decimal_place)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    """生成比較科學記號表示的數的大小的題目。"""
    subtype = random.choice(['diff_exponent', 'same_exponent'])
    
    a1 = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))
    a2 = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))
    
    # Ensure a1 != a2. If they are the same after rounding, regenerate.
    while a1 == a2:
        a2 = Decimal(str(round(random.uniform(1.0, 9.99), random.randint(1, 4))))

    # Exponent choices: large positive and large negative to provide distinctness
    exponent_choices = list(range(4, 10)) + list(range(-10, -4)) 
    
    if subtype == 'diff_exponent':
        n1 = random.choice(exponent_choices)
        n2 = random.choice(exponent_choices)
        while n1 == n2: # Ensure exponents are different
            n2 = random.choice(exponent_choices)
        
        val1 = a1 * (Decimal('10') ** n1)
        val2 = a2 * (Decimal('10') ** n2)
        
    else: # same_exponent
        n1 = random.choice(exponent_choices)
        n2 = n1 # Same exponent
        
        val1 = a1 * (Decimal('10') ** n1)
        val2 = a2 * (Decimal('10') ** n2)
        
    num1_str = f"${a1}\\times10^{{{n1}}}$"
    num2_str = f"${a2}\\times10^{{{n2}}}$"
    
    correct_symbol = ">" if val1 > val2 else "<" if val1 < val2 else "="
    
    question_text = f"比較下列兩數的大小： ${a1}\\times10^{{{n1}}}$ 與 ${a2}\\times10^{{{n2}}}$ (請填入 >, < 或 =)"
    correct_answer = correct_symbol
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    處理三種類型的答案：比較符號、整數、科學記號表示的字串。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    # 1. Check for comparison problems (answers are '>', '<', '=')
    if correct_answer in [">", "<", "="]:
        is_correct = (user_answer == correct_answer)
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    
    # 2. Check for digit count / decimal place problems (answers are integers)
    try:
        user_int = int(user_answer)
        correct_int = int(correct_answer)
        is_correct = (user_int == correct_int)
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        pass # Not an integer answer, proceed to scientific notation parsing

    # 3. Check for scientific notation representation problems
    user_a, user_n = parse_scientific_notation_string(user_answer)
    correct_a_parsed, correct_n_parsed = parse_scientific_notation_string(correct_answer)
    
    if user_a is not None and user_n is not None and \
       correct_a_parsed is not None and correct_n_parsed is not None:
        # Compare (a, n) pairs. Decimal comparison requires `==`
        is_correct = (user_a == correct_a_parsed and user_n == correct_n_parsed)
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    else:
        # If parsing failed for user answer, it's incorrect.
        result_text = f"答案格式不正確或計算錯誤。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}