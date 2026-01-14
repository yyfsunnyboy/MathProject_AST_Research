# ==============================================================================
# ID: jh_數學1上_PowersOfTen
# Model: gemini-2.5-flash | Strategy: Architect-Engineer (v8.0)
# Duration: 18.43s | RAG: 1 examples
# Created At: 2026-01-08 23:02:01
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



def generate_type_1_problem():
    """
    Generates a problem involving negative powers of ten, their fractional and decimal representations,
    and filling in blanks for equivalences, strictly following the Architect's Spec.
    """
    # Variables & Constraints:
    n_exponent = random.randint(3, 10) # range 3-10

    # Step-by-Step Logic:
    # For Part 1 (Express 10^(-n_exponent) as fraction and decimal):
    fraction_denom = 10 ** n_exponent
    
    # Construct the decimal string: "0." followed by (n_exponent - 1) zeros, then "1"
    # Example: if n_exponent = 3, then 0.001 (two zeros)
    decimal_str = f"0.{'0' * (n_exponent - 1)}1"

    # For Part 2 (Fill in the blanks for the decimal_str derived from 10^(-n_exponent)):
    # The initial decimal value for filling the blanks is the same as decimal_str.
    # This means the target value for the blanks is 10^(-n_exponent).
    fill_blank_1_val = fraction_denom  # Denominator for 1/(...)
    fill_blank_2_val = n_exponent      # Exponent for 1/10^(...)
    fill_blank_3_val = -n_exponent    # Exponent for 10^(...)

    # Question Template:
    question_text = f"""1. 分別以分數和小數表示 $10^{{-{n_exponent}}}$。
2. 在括號內填入適當的數。
${decimal_str} = \\frac{{1}}{{(~~~)}} = \\frac{{1}}{{10^{{(~)}}}} = 10^{{(~)}}$"""

    # Answer:
    # The spec indicates that 'answer' and 'correct_answer' will be the same string for this type.
    correct_answer = f"1. $\\frac{{1}}{{{fraction_denom}}}$, {decimal_str} 2. {fill_blank_1_val}, {fill_blank_2_val}, {fill_blank_3_val}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a math problem based on the specified level.
    For this skill 'jh_數學1上_PowersOfTen', only Type 1 is implemented.
    """
    # As per Architect's Spec, only Type 1 is defined for this skill.
    # The level parameter is present for future expansion but currently always calls Type 1.
    return generate_type_1_problem()

# The Architect's Spec for jh_數學1上_PowersOfTen does not include a 'check' function.
# Therefore, it is omitted from this implementation to strictly follow the provided spec.

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
