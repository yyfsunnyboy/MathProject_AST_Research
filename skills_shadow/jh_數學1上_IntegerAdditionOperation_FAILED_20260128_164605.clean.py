```python
import random

def generate(level=1, **kwargs):
    while True:
        # Step 1: Generate two positive integers abs_n1 and abs_n2 in the range [1, 100]
        abs_n1 = random.randint(1, 100)
        abs_n2 = random.randint(1, 100)

        # Step 2: Determine sign combination
        sign_combination = random.choice(['pos_pos', 'neg_neg', 'pos_neg', 'neg_pos'])

        # Step 3: Convert abs_n1 and abs_n2 to n1 and n2 based on the sign combination
        if sign_combination == 'pos_pos':
            n1, n2 = abs_n1, abs_n2
        elif sign_combination == 'neg_neg':
            n1, n2 = -abs_n1, -abs_n2
        elif sign_combination == 'pos_neg':
            n1, n2 = abs_n1, -abs_n2
        elif sign_combination == 'neg_pos':
            n1, n2 = -abs_n1, abs_n2

        # Step 4: Calculate the final answer
        final_answer = n1 + n2

        # Step 5: Check if the final answer is within the range [-200, 200]
        if -200 <= final_answer <= 200:
            break

    # Step 6: Format the question text and answer
    math_expr = f"{fmt_num(n1)} {op_latex['+']} {fmt_num(n2)}"
    q_str = f"計算 ${math_expr}$ 的值"
    question_output = clean_latex_output(q_str)

    return {'question_text': question_output, 'answer': str(final_answer), 'mode': 1}

# Dummy implementations for fmt_num, op_latex, and clean_latex_output
def fmt_num(x):
    if x < 0:
        return f"({x})"
    else:
        return str(x)

op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}

def clean_latex_output(q_str):
    # Dummy implementation for demonstration purposes
    return q_str
```