def generate(level=1, **kwargs):
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    # [Step 1] 模板選擇
    template = 'chained_integer_operations'
    
    # [Step 2] 變數生成
    num_terms = random.choice([3, 4])
    operands = []
    operators = []
    
    def _rand_num():
        return random.randint(-20, 20)
    
    for i in range(num_terms):
        while True:
            n = _rand_num()
            if abs(n) >= 1 and (i == num_terms - 1 or n != 0):
                operands.append(n)
                break
    
    for i in range(num_terms - 1):
        op = random.choice(['+', '-', '*', '/'])
        if op == '/' and operands[i] % operands[i + 1] != 0:
            continue
        operators.append(op)
    
    # [Step 3] 運算
    expression = []
    for i in range(num_terms - 1):
        expression.extend([operands[i], operators[i]])
    expression.append(operands[-1])
    
    while '*' in expression or '/' in expression:
        for i, op in enumerate(expression):
            if op == '*':
                result = expression[i - 1] * expression[i + 1]
                if abs(result) > 200:
                    continue, expression = expression[:i-1] + [result] + expression[i+2:]
                break
            elif op == '/':
                result = expression[i - 1] // expression[i + 1]
                if abs(result) > 200:
                    continue, expression = expression[:i-1] + [result] + expression[i+2:]
                break
    
    while '+' in expression or '-' in expression:
        for i, op in enumerate(expression):
            if op == '+':
                result = expression[i - 1] + expression[i + 1]
                if abs(result) > 200:
                    continue, expression = expression[:i-1] + [result] + expression[i+2:]
                break
            elif op == '-':
                result = expression[i - 1] - expression[i + 1]
                if abs(result) > 200:
                    continue, expression = expression[:i-1] + [result] + expression[i+2:]
result = expression[0]; break
    
    # [Step 4] 題幹
    q = ""
    for i in range(num_terms - 1):
        q += f"{fmt_num(operands[i])} {op_latex[operators[i]]} "
    q += fmt_num(operands[-1])
    
    # [Step 5] 清洗
    q = clean_latex_output(q)
    
    # [Step 6] 答案
    a = fmt_num(result)
    
    # [Step 7] 清洗變數名
    if isinstance(a, str) and "=" in a:
        a = a.split("=")[-1].strip()
    
    # [Step 8] 回傳
    return {
        'question_text': q,
        'correct_answer': a,
        'answer': a,
        'mode': 1
    }