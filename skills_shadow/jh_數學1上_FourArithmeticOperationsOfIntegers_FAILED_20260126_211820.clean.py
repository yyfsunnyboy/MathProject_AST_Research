def generate(level=1, **kwargs):
    # [Step 1] 模板選擇
    template = 'chained_integer_operations'
    
    # [Step 2] 變數生成
    def _rand_num():
        return random.randint(-50, 50)
    
    def _rand_non_zero_num():
        while True:
            num = random.randint(-50, 50)
            if num != 0:
                return num
    
    num_ops = random.choice([2, 3])
    operators_list = []
    operand_list = [_rand_num()]
    
    for i in range(num_ops):
        op_i = random.choice(['+', '-', '*', '/'])
        operators_list.append(op_i)
        
        if op_i in ['*', '+', '-']:
            next_n = _rand_num()
        elif op_i == '/':
            previous_operand = operand_list[-1]
            divisor = _rand_non_zero_num()
            quotient = _rand_num()
            modified_previous_operand = divisor * quotient
            operand_list[-1] = modified_previous_operand
            next_n = divisor
        
        operand_list.append(next_n)
    
    # [Step 3] 運算
    temp_expr = operand_list[:]
    for i in range(len(operators_list)):
        temp_expr.insert(2 * i + 1, operators_list[i])
    
    while '*' in temp_expr or '/' in temp_expr:
        for i in range(len(temp_expr) - 2):
            if temp_expr[i + 1] == '*':
                result = temp_expr[i] * temp_expr[i + 2]
                temp_expr[i:i+3] = [result]
                break
            elif temp_expr[i + 1] == '/':
                result = temp_expr[i] // temp_expr[i + 2]
                temp_expr[i:i+3] = [result]
                break
    
    while '+' in temp_expr or '-' in temp_expr:
        for i in range(len(temp_expr) - 2):
            if temp_expr[i + 1] == '+':
                result = temp_expr[i] + temp_expr[i + 2]
                temp_expr[i:i+3] = [result]
                break
            elif temp_expr[i + 1] == '-':
                result = temp_expr[i] - temp_expr[i + 2]
                temp_expr[i:i+3] = [result]
result = temp_expr[0]; break
    
    # [Step 4] 題幹
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    q_parts = []
    for i in range(len(operators_list)):
        q_parts.append(fmt_num(operand_list[i]))
        q_parts.append(op_latex[operators_list[i]])
    q_parts.append(fmt_num(operand_list[-1]))
    q = ' '.join(q_parts)
    
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