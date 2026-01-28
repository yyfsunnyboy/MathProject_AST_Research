```python
import random

def generate(level=1, **kwargs):
    while True:
        abs_n1 = random.randint(1, 100)
        abs_n2 = random.randint(1, 100)
        
        sign_combination = random.choice(['pos_pos', 'neg_neg', 'pos_neg', 'neg_pos'])
        
        if sign_combination == 'pos_pos':
            n1, n2 = abs_n1, abs_n2
        elif sign_combination == 'neg_neg':
            n1, n2 = -abs_n1, -abs_n2
        elif sign_combination == 'pos_neg':
            n1, n2 = abs_n1, -abs_n2
        elif sign_combination == 'neg_pos':
            n1, n2 = -abs_n1, abs_n2
        
        final_answer = n1 + n2
        
        if -200 <= final_answer <= 200:
            break
    
    math_expr = f"{fmt_num(n1)} {op_latex['+']} {fmt_num(n2)}"
    q_str = f"計算 ${math_expr}$ 的值"
    question_output = clean_latex_output(q_str)
    
    return {'question_text': question_output, 'answer': str(final_answer), 'mode': 1}

# 工具函數（假設已定義）
def fmt_num(x):
    if x < 0:
        return f"({x})"
    else:
        return str(x)

op_latex = {
    '+': '+',
    '-': '-',
    '*': '\\times',
    '/': '\\div'
}

def clean_latex_output(q_str):
    # 假設此函數用於清洗 LaTeX 字串
    return q_str

# 生成題目範例
print(generate())
```