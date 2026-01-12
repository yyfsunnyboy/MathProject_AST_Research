# ==============================================================================
# ID: jh_數學1上_PositiveAndNegativeNumbers
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 37.32s | RAG: 3 examples
# Created At: 2026-01-12 10:52:25
# Fix Status: [Clean Pass]
# Fixes: Regex=0, Logic=0
#==============================================================================


import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

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
# --- 4. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案 (No answer)"}
    
    # 1. Normalize strings (字串正規化)
    def normalize(s):
        s = str(s).strip()
        # 移除空格、LaTeX間距
        s = s.replace(" ", "").replace("\\,", "").replace("\\;", "")
        # [Fix] 支援中文全形逗號，轉為半形，避免判錯
        s = s.replace("，", ",") 
        return s
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy (精確比對)
    if user_norm == correct_norm:
        return {"correct": True, "result": "Correct!"}
        
    # 3. Float Match Strategy (數值容錯比對)
    try:
        # 嘗試將兩者都轉為浮點數，如果誤差極小則算對
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # 無法轉為數字，可能是代數式或座標，維持字串比對結果
        
    # [Fix] 錯誤訊息優化：中文、換行顯示，去除不必要的符號
    # 這裡回傳的 result 會直接顯示在前端 Result 區域
    return {"correct": False, "result": f"答案錯誤。正確答案為：\n{correct_answer}"}


import matplotlib.pyplot as plt
import numpy as np
import io
import base64

from decimal import Decimal, getcontext

# Set precision for Decimal operations if needed, though for basic
# positive/negative numbers, float usually suffices.
getcontext().prec = 28

# --- Matplotlib Font Setup (CRITICAL for Chinese display) ---
# Ensure these fonts are available in the execution environment.
# 'Microsoft JhengHei' is common on Windows for Traditional Chinese.
# 'SimHei' is common on Windows/Linux for Simplified Chinese, but often supports Traditional.
# 'Arial Unicode MS' is another option.
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'Arial']
plt.rcParams['axes.unicode_minus'] = False # Solve the problem of '-' sign display

# --- Helper Function to convert Matplotlib figure to Base64 ---
def _plot_to_base64(fig):
    """
    Converts a matplotlib figure to a Base64 encoded PNG string.
    Closes the figure after conversion to free memory.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)  # Close the figure to free up memory
    return img_base64

# --- Problem Type Implementations ---

def _generate_scenario_problem():
    """
    Generates a real-world scenario problem involving positive and negative numbers.
    Focuses on representation of change or position relative to a reference.
    """
    problem_type = "情境應用題"
    image_base64 = ""

    scenarios = [
        {"context": "氣溫", "unit": "°C", "positive_desc": "上升", "negative_desc": "下降"},
        {"context": "海拔", "unit": "公尺", "positive_desc": "高於海平面", "negative_desc": "低於海平面"},
        {"context": "金錢", "unit": "元", "positive_desc": "賺", "negative_desc": "賠"},
        {"context": "分數", "unit": "分", "positive_desc": "進步", "negative_desc": "退步"},
        {"context": "方向", "unit": "公里", "positive_desc": "向東", "negative_desc": "向西"},
    ]
    
    selected_scenario = random.choice(scenarios)
    context = selected_scenario["context"]
    unit = selected_scenario["unit"]
    pos_desc = selected_scenario["positive_desc"]
    neg_desc = selected_scenario["negative_desc"]

    # Inverse engineering: determine the answer first
    # The answer will be a simple representation of a negative or positive value.
    answer_value = random.randint(1, 100)
    is_negative_answer = random.choice([True, False])

    if is_negative_answer:
        correct_answer = f"-{answer_value}{unit}"
        # Construct question leading to a negative answer
        # e.g., "賺200元記為+200，賠180元如何記？"
        first_value = random.randint(1, 100) # for the positive example
        question_text = (
            f"若以{context}為基準，{pos_desc}{first_value}{unit}記為 +{first_value}。 "
            f"那麼{neg_desc}{answer_value}{unit}應該記為多少？"
        )
    else:
        correct_answer = f"+{answer_value}{unit}"
        # Construct question leading to a positive answer
        # e.g., "賠100元記為-100，賺250元如何記？"
        first_value = random.randint(1, 100) # for the negative example
        question_text = (
            f"若以{context}為基準，{neg_desc}{first_value}{unit}記為 -{first_value}。 "
            f"那麼{pos_desc}{answer_value}{unit}應該記為多少？"
        )
    
    question_text += f"\n(答案格式：正負數{unit})"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": image_base64,
        "problem_type": problem_type
    }

def _generate_classification_problem():
    """
    Generates a problem focused on classifying numbers by their properties
    (positive, negative, integer, absolute value, opposite number).
    """
    problem_type = "數字特性判斷"
    image_base64 = ""

    # Generate a diverse set of numbers
    numbers = []
    num_count = random.randint(5, 8)
    # Ensure variety:
    numbers.append(0) # Always include zero
    for _ in range(num_count - 1):
        choice = random.randint(1, 4)
        if choice == 1: # Positive/Negative Integer
            numbers.append(random.randint(-20, 20))
        elif choice == 2: # Positive/Negative Decimal (one decimal place)
            numbers.append(round(random.uniform(-15.0, 15.0), 1))
        elif choice == 3: # Positive/Negative Simple Fraction
            numerator = random.randint(1, 10)
            denominator = random.choice([2, 3, 4, 5])
            sign = random.choice([-1, 1])
            numbers.append(sign * numerator / denominator)
        else: # Another integer
            numbers.append(random.randint(-20, 20))
    
    # Remove duplicates and ensure zero is only once if it was generated again
    numbers = list(set(numbers))
    random.shuffle(numbers)

    # Format numbers for question text (e.g., 1/2, -3.5, 0)
    # Use Decimal for fractions to avoid floating point inaccuracies in display if needed,
    # but for simple fractions like 1/2, float is often okay.
    # For display, we want to show fractions as fractions, not floats.
    formatted_numbers = []
    for num in numbers:
        if isinstance(num, float) and num % 1 != 0: # Check if it's a decimal
            if abs(num * 10) % 1 == 0: # Simple one decimal place
                 formatted_numbers.append(str(num))
            elif abs(num * 100) % 1 == 0: # Simple two decimal places
                 formatted_numbers.append(str(num))
            else: # Try to represent as fraction if it's a simple one, otherwise keep float
                fraction_str = ""
                if num == 0.5: fraction_str = "1/2"
                elif num == -0.5: fraction_str = "-1/2"
                elif num == 0.25: fraction_str = "1/4"
                elif num == -0.25: fraction_str = "-1/4"
                elif num == 0.75: fraction_str = "3/4"
                elif num == -0.75: fraction_str = "-3/4"
                elif num == 0.2: fraction_str = "1/5"
                elif num == -0.2: fraction_str = "-1/5"
                elif num == 0.4: fraction_str = "2/5"
                elif num == -0.4: fraction_str = "-2/5"
                elif num == 0.6: fraction_str = "3/5"
                elif num == -0.6: fraction_str = "-3/5"
                elif num == 0.8: fraction_str = "4/5"
                elif num == -0.8: fraction_str = "-4/5"
                elif num == 1/3: fraction_str = "1/3"
                elif num == -1/3: fraction_str = "-1/3"
                elif num == 2/3: fraction_str = "2/3"
                elif num == -2/3: fraction_str = "-2/3"
                
                if fraction_str:
                    formatted_numbers.append(fraction_str)
                else:
                    formatted_numbers.append(str(round(num, 2))) # Round to 2 decimal places for display
        elif num % 1 == 0: # It's an integer
            formatted_numbers.append(str(int(num)))
        else: # Should handle other cases, e.g., if num was already an int
            formatted_numbers.append(str(num))

    numbers_str = ", ".join(formatted_numbers)

    # Choose a classification task
    task_type = random.randint(1, 3)

    if task_type == 1: # Identify positive/negative/integers
        sub_task = random.choice(["負數", "正數", "整數", "非負數", "非正數", "非整數"])
        question_text = f"請從下列數字中，找出所有的{sub_task}：{numbers_str}"
        
        answers = []
        for num, formatted_num in zip(numbers, formatted_numbers):
            if sub_task == "負數" and num < 0:
                answers.append(formatted_num)
            elif sub_task == "正數" and num > 0:
                answers.append(formatted_num)
            elif sub_task == "整數" and num == int(num):
                answers.append(formatted_num)
            elif sub_task == "非負數" and num >= 0:
                answers.append(formatted_num)
            elif sub_task == "非正數" and num <= 0:
                answers.append(formatted_num)
            elif sub_task == "非整數" and num != int(num):
                answers.append(formatted_num)
        
        if not answers:
            correct_answer = "無"
        else:
            correct_answer = ", ".join(sorted(answers, key=lambda x: float(eval(x)) if '/' in x else float(x))) # Sort numerically

        question_text += f"\n(答案格式：數字1, 數字2, ...)"

    elif task_type == 2: # Find the opposite number
        target_num = random.choice(numbers)
        formatted_target_num = formatted_numbers[numbers.index(target_num)]
        question_text = f"數字 {formatted_target_num} 的相反數是多少？"
        opposite = -target_num
        # Ensure opposite is formatted correctly
        if opposite == int(opposite):
            correct_answer = str(int(opposite))
        else:
            # Try to represent as fraction if original was fraction
            if '/' in formatted_target_num and formatted_target_num.replace('-', '').replace('/', '').isdigit():
                # Reconstruct fraction
                parts = formatted_target_num.replace('-', '').split('/')
                if len(parts) == 2:
                    try:
                        num = int(parts[0])
                        den = int(parts[1])
                        correct_answer = f"-{num}/{den}" if target_num > 0 else f"{num}/{den}"
                    except ValueError:
                        correct_answer = str(round(opposite, 2))
                else:
                    correct_answer = str(round(opposite, 2))

            else:
                correct_answer = str(round(opposite, 2))
        
        question_text += f"\n(答案格式：數字)"

    else: # Compare absolute values
        threshold = round(random.uniform(0.5, 10.0), 1)
        comparison_type = random.choice(["大於", "小於"])
        question_text = f"請從下列數字中，找出絕對值{comparison_type}{threshold}的數：{numbers_str}"
        
        answers = []
        for num, formatted_num in zip(numbers, formatted_numbers):
            if comparison_type == "大於" and abs(num) > threshold:
                answers.append(formatted_num)
            elif comparison_type == "小於" and abs(num) < threshold:
                answers.append(formatted_num)
        
        if not answers:
            correct_answer = "無"
        else:
            correct_answer = ", ".join(sorted(answers, key=lambda x: float(eval(x)) if '/' in x else float(x))) # Sort numerically
        
        question_text += f"\n(答案格式：數字1, 數字2, ...)"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": image_base64,
        "problem_type": problem_type
    }

def _generate_number_line_problem():
    """
    Generates a number line representation and comparison problem.
    Includes a matplotlib visualization of the number line.
    """
    problem_type = "數線表示與比較"
    
    # Inverse engineering: Generate numbers within a reasonable range
    num_count = random.randint(3, 5)
    numbers = set()
    while len(numbers) < num_count:
        choice = random.randint(1, 3)
        if choice == 1: # Integer
            numbers.add(random.randint(-10, 10))
        else: # Decimal (one decimal place)
            numbers.add(round(random.uniform(-9.5, 9.5), 1))
    
    # Ensure 0 is sometimes included
    if random.random() < 0.5 and 0 not in numbers:
        numbers.add(0)
    
    numbers = sorted(list(numbers))

    # Format numbers for question text (e.g., 1/2, -3.5, 0)
    formatted_numbers = []
    for num in numbers:
        if isinstance(num, float) and num % 1 != 0: # Check if it's a decimal
            formatted_numbers.append(str(num))
        else: # It's an integer
            formatted_numbers.append(str(int(num)))
    
    numbers_str = ", ".join(formatted_numbers)

    question_text = f"請將下列數字標示在數線上，並由小到大排列：{numbers_str}"
    correct_answer = ", ".join(formatted_numbers) # Already sorted

    question_text += f"\n(答案格式：數字1, 數字2, ...)"

    # --- Matplotlib Visualization ---
    fig, ax = plt.subplots(figsize=(8, 2))

    min_val = min(numbers) - 2 if numbers else -5
    max_val = max(numbers) + 2 if numbers else 5
    
    # Ensure the range covers at least -5 to 5 for general visibility
    min_val = min(min_val, -5)
    max_val = max(max_val, 5)

    # Draw the number line
    ax.plot([min_val, max_val], [0, 0], color='black', linewidth=1.5)

    # Mark origin
    ax.plot(0, 0, 'ro', markersize=6) # Red circle for origin
    ax.text(0, -0.25, '0', ha='center', va='top', fontsize=10)

    # Mark unit intervals
    for i in range(math.floor(min_val), math.ceil(max_val) + 1):
        ax.plot([i, i], [-0.1, 0.1], color='black', linewidth=0.8)
        if i != 0: # Don't label 0 again
            ax.text(i, -0.25, str(i), ha='center', va='top', fontsize=9)

    # Plot the given numbers
    for num, formatted_num in zip(numbers, formatted_numbers):
        ax.plot(num, 0, 'bx', markersize=8, markeredgewidth=2) # Blue 'x' for points
        # Adjust label position to avoid overlap if numbers are close
        offset = 0.3 + (random.random() * 0.1 - 0.05) # Small random vertical offset
        ax.text(num, offset, formatted_num, ha='center', va='bottom', fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_yticks([]) # Hide y-axis
    ax.set_xticks([]) # Hide x-axis ticks, as we draw our own
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(-0.5, 0.8) # Adjust y-limits to fit labels
    ax.set_aspect('equal', adjustable='box') # Ensure no distortion
    ax.axis('off') # Hide axes frame

    image_base64 = _plot_to_base64(fig)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": image_base64,
        "problem_type": problem_type
    }

# --- Main Generator Function ---
def generate_positive_negative_number_problem():
    """
    Generates a random problem related to positive and negative numbers
    based on the Architect's specification.
    """
    problem_generators = [
        _generate_scenario_problem,
        _generate_classification_problem,
        _generate_number_line_problem,
    ]

    chosen_generator = random.choice(problem_generators)
    return chosen_generator()

# --- Example Usage (for testing purposes) ---
if __name__ == "__main__":
    print("--- Generating 5 sample problems ---")
    for i in range(5):
        problem = generate_positive_negative_number_problem()
        print(f"\n--- Problem {i+1} ---")
        print(f"Problem Type: {problem['problem_type']}")
        print(f"Question: {problem['question_text']}")
        print(f"Correct Answer: {problem['correct_answer']}")
        if problem['image_base64']:
            print(f"Image Base64: (present, length {len(problem['image_base64'])})")
            # To view the image, you would typically embed it in HTML:
            # <img src="data:image/png;base64,YOUR_BASE64_STRING_HERE">
        else:
            print("Image Base64: (empty)")

    # Test specific types
    print("\n--- Testing specific problem types ---")
    print("\n--- Scenario Problem ---")
    print(f"{_generate_scenario_problem()}")
    print("\n--- Classification Problem ---")
    print(f"{_generate_classification_problem()}")
    print("\n--- Number Line Problem ---")
    print(f"{_generate_number_line_problem()}")


# [Auto-Injected Smart Dispatcher v8.7]
def generate(level=1):
    if level == 1:
        types = ['generate_positive_negative_number_problem']
        selected = random.choice(types)
    else:
        types = ['generate_positive_negative_number_problem']
        selected = random.choice(types)
    if selected == 'generate_positive_negative_number_problem': return generate_positive_negative_number_problem()
    return generate_positive_negative_number_problem()

# [Auto-Injected Patch v9.2] Universal Return Fixer
# 1. Ensures 'answer' key exists (copies from 'correct_answer')
# 2. Ensures 'image_base64' key exists (extracts from 'visuals')
def _patch_return_dict(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            # Fix 1: Answer Key
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            
            # Fix 2: Image Key (Flatten visuals for legacy frontend)
            if 'image_base64' not in res and 'visuals' in res:
                try:
                    # Extract first image value from visuals list
                    for item in res['visuals']:
                        if item.get('type') == 'image/png':
                            res['image_base64'] = item.get('value')
                            break
                except: pass
        return res
    return wrapper

# Apply patch to ALL generator functions in scope
import sys
# Iterate over a copy of globals keys to avoid modification issues
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'generate'):
        globals()[_name] = _patch_return_dict(_func)
