import random
from fractions import Fraction
import math
import re

def generate(level=1):
    """
    生成「函數圖形下面積」相關題目 (標準 LaTeX 範本)。
    目前主要生成黎曼和的數值計算題目。
    """
    # For level 1, focus on direct Riemann sum calculation for simple functions.
    problem_type = 'riemann_sum_calc'
    return generate_riemann_sum_calculation_problem(level)

def generate_riemann_sum_calculation_problem(level):
    """
    生成計算黎曼和的題目。
    - 函數類型：線性或簡單二次函數。
    - 區間 [a, b]
    - 子區間數量 n
    - 黎曼和類型：左黎曼和或右黎曼和
    """
    func_type = random.choice(['linear', 'quadratic_simple'])

    # Determine interval [a, b]
    a = random.randint(-3, 1) # Start of interval
    b = a + random.randint(2, 6) # End of interval, b > a (length at least 2)

    # Determine number of subintervals n
    n_choices = [2, 3, 4] # Keep n small for level 1 for manageable calculations
    n = random.choice(n_choices)

    delta_x = Fraction(b - a, n)

    func_str_latex = ""
    f_func = None

    if func_type == 'linear':
        m = random.randint(1, 4) # Slope (positive to ensure increasing or constant)
        
        # Ensure f(x) = mx+c is non-negative on [a, b].
        # For m > 0, the minimum value is at x=a. So, we need f(a) >= 0 => m*a + c >= 0.
        # Thus, c >= -m*a.
        min_c_val = -m * a
        # Ensure c is positive or large enough, but not excessively large.
        c = random.randint(max(0, min_c_val), max(5, min_c_val + 5))

        # Format function string for LaTeX
        if m == 1 and c == 0:
            func_str_latex = "$f(x) = x$"
        elif c == 0:
            func_str_latex = f"$f(x) = {m}x$"
        elif m == 1:
            func_str_latex = f"$f(x) = x + {c}$"
        else:
            func_str_latex = f"$f(x) = {m}x + {c}$"

        def f_func_linear(x_val):
            return m * x_val + c
        f_func = f_func_linear

    elif func_type == 'quadratic_simple':
        # Use f(x) = x^2 + c where c >= 0. This is always non-negative.
        c = random.randint(0, 4) # Constant term
        if c == 0:
            func_str_latex = "$f(x) = x^{{2}}$"
        else:
            func_str_latex = f"$f(x) = x^{{2}} + {c}$"

        def f_func_quadratic(x_val):
            return x_val * x_val + c
        f_func = f_func_quadratic

    # Type of Riemann Sum (left or right endpoint)
    sum_type = random.choice(['left', 'right'])

    current_sum = Fraction(0)
    for i in range(n):
        # Calculate endpoints of the i-th subinterval [x_{i-1}, x_i]
        x_k_start = Fraction(a) + i * delta_x # Left endpoint
        x_k_end = Fraction(a) + (i + 1) * delta_x # Right endpoint

        sample_point = Fraction(0)
        if sum_type == 'left':
            sample_point = x_k_start
        elif sum_type == 'right':
            sample_point = x_k_end
        # Other sum types (midpoint, min/max for upper/lower) can be added for higher levels.

        # Add the area of the current rectangle: f(sample_point) * delta_x
        current_sum += f_func(sample_point) * delta_x

    # Format the correct answer into a string (integer or LaTeX fraction)
    correct_answer_str = _format_fraction_answer(current_sum)

    sum_type_zh = {"left": "左黎曼和", "right": "右黎曼和"}

    question_text = (
        f"計算函數 {func_str_latex} 在區間 $[{a}, {b}]$ 上，使用 ${n}$ 個等寬子區間的{sum_type_zh[sum_type]}。\n"
        f"請以分數或整數形式作答（例如 `1/2` 或 `5`）。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def _format_fraction_answer(fraction_val):
    """Helper to format a Fraction object into a string, using LaTeX for non-integer fractions."""
    if fraction_val.denominator == 1:
        return str(fraction_val.numerator)
    # Use raw string for LaTeX command \\frac, then format with double braces for Python.
    return r"\\frac{{{}}}{{{}}}".format(fraction_val.numerator, fraction_val.denominator)

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援整數、分數 (例如 "1/2") 和 LaTeX 分數格式 (\\frac{1}{2})。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    user_answer_parsed = None
    correct_answer_parsed = None

    # Attempt to parse user_answer (can be "1/2", "5", "0.5")
    try:
        if '/' in user_answer:
            num, den = map(int, user_answer.split('/'))
            if den == 0: raise ZeroDivisionError("Denominator cannot be zero.")
            user_answer_parsed = Fraction(num, den)
        else:
            user_answer_parsed = Fraction(float(user_answer))
    except (ValueError, ZeroDivisionError):
        pass # Parsing failed, user_answer_parsed remains None

    # Attempt to parse correct_answer (can be "5" or r"\\frac{3}{2}")
    try:
        # Check for LaTeX fraction format: \\frac{num}{den}
        match = re.match(r"\\frac\{(\-?\d+)\}\{(\-?\d+)\}", correct_answer)
        if match:
            num = int(match.group(1))
            den = int(match.group(2))
            if den == 0: raise ZeroDivisionError("Denominator cannot be zero.")
            correct_answer_parsed = Fraction(num, den)
        else:
            # Assume it's a simple number string (integer or float)
            correct_answer_parsed = Fraction(float(correct_answer))
    except (ValueError, ZeroDivisionError):
        pass # Parsing failed, correct_answer_parsed remains None

    is_correct = False
    result_text = ""

    if user_answer_parsed is not None and correct_answer_parsed is not None:
        if user_answer_parsed == correct_answer_parsed:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。你輸入的是 ${user_answer}$，但正確答案應為：${correct_answer}$"
    else:
        # Provide specific feedback if parsing failed for user's answer
        if user_answer_parsed is None:
            result_text = f"你的答案格式不正確。請以整數或分數（例如 `1/2`）形式作答。正確答案應為：${correct_answer}$"
        else:
            # This case means correct_answer_parsed is None, indicating an internal error or malformed correct_answer.
            result_text = f"系統內部錯誤，無法檢查你的答案。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}