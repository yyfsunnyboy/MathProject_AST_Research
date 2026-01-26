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
    for _ in range(num_ops):
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
    temp_expr = operand_list[:]
    for i, op in enumerate(operators_list):
        if op == '*':
            result = operator.mul(temp_expr[i], temp_expr[i + 1])
            temp_expr[i:i + 2] = [result]
        elif op == '/':
            result = operator.floordiv(temp_expr[i], temp_expr[i + 1])
            temp_expr[i:i + 2] = [result]
    for i, op in enumerate(operators_list):
        if op == '+':
            result = operator.add(temp_expr[i], temp_expr[i + 1])
            temp_expr[i:i + 2] = [result]
        elif op == '-':
            result = operator.sub(temp_expr[i], temp_expr[i + 1])
            temp_expr[i:i + 2] = [result]
    result = temp_expr[0]
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    q_parts = []
    for i in range(len(operators_list)):
        q_parts.append(fmt_num(operand_list[i]))
        q_parts.append(op_latex[operators_list[i]])
    q_parts.append(fmt_num(operand_list[-1]))
    q = ' '.join(q_parts)
    q = clean_latex_output(q)
    a = fmt_num(result)
    if isinstance(a, str) and '=' in a:
        a = a.split('=')[-1].strip()
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}