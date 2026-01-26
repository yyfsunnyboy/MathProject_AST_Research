def generate(level=1, **kwargs):
    template = 'chained_integer_operations'

    def _rand_num():
        return random.randint(-50, 50)

    def _rand_non_zero_num():
        for _safety_loop_var in range(1000):
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
            quotient = random.randint(-10, 10)
            modified_previous_operand = divisor * quotient
            operand_list[-1] = modified_previous_operand
            next_n = divisor
        operand_list.append(next_n)
    temp_expr = []
    for i in range(len(operand_list)):
        if i < len(operators_list):
            temp_expr.append(operand_list[i])
            temp_expr.append(operators_list[i])
        else:
            temp_expr.append(operand_list[i])
    i = 0
    while i < len(temp_expr):
        if temp_expr[i] == '*' or temp_expr[i] == '/':
            op = temp_expr[i]
            left = temp_expr[i - 1]
            right = temp_expr[i + 1]
            if op == '*':
                result = left * right
            elif op == '/':
                result = left // right
            temp_expr = temp_expr[:i - 1] + [result] + temp_expr[i + 2:]
        else:
            i += 1
    i = 0
    while i < len(temp_expr):
        if temp_expr[i] == '+' or temp_expr[i] == '-':
            op = temp_expr[i]
            left = temp_expr[i - 1]
            right = temp_expr[i + 1]
            if op == '+':
                result = left + right
            elif op == '-':
                result = left - right
            temp_expr = temp_expr[:i - 1] + [result] + temp_expr[i + 2:]
        else:
            i += 1
    result = temp_expr[0]
    q = ''
    for i in range(len(operand_list)):
        if i < len(operators_list):
            q += f'{fmt_num(operand_list[i])} {op_latex[operators_list[i]]} '
        else:
            q += fmt_num(operand_list[i])
    q = clean_latex_output(q)
    a = fmt_num(result)
    if isinstance(a, str) and '=' in a:
        a = a.split('=')[-1].strip()
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}