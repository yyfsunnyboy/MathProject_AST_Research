def generate(level=1, **kwargs):
    op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
    template = random.choice(['ChainOfArithmeticOperations', 'DistributivePropertyApplication'])
    if template == 'ChainOfArithmeticOperations':
        num_count = random.randint(3, 4)
        operand_types = random.choices(['rational_num_basic', 'rational_num_decimal', 'integer_factor'], k=num_count)
        operator_sequence = random.choices(['+', '-', '*', '/'], k=num_count - 1)
        operands = []
        for op_type in operand_types:
            if op_type == 'rational_num_basic':
                numerator = random.randint(-20, 20)
                while numerator == 0:
                    numerator = random.randint(-20, 20)
                denominator = random.randint(2, 12)
                operands.append(Fraction(numerator, denominator))
            elif op_type == 'rational_num_decimal':
                value = Fraction(random.uniform(-10, 10)).limit_denominator()
                while abs(value.numerator) > 1000 or abs(value.denominator) > 1000:
                    value = Fraction(random.uniform(-10, 10)).limit_denominator()
                operands.append(value)
            elif op_type == 'integer_factor':
                value = random.randint(-100, 100)
                while value == 0:
                    value = random.randint(-100, 100)
                operands.append(Fraction(value))
        result = operands[0]
        for i in range(num_count - 1):
            if operator_sequence[i] == '+':
                result += operands[i + 1]
            elif operator_sequence[i] == '-':
                result -= operands[i + 1]
            elif operator_sequence[i] == '*':
                result *= operands[i + 1]
            elif operator_sequence[i] == '/':
                while operands[i + 1] == 0:
                    operands[i + 1] = Fraction(random.randint(-20, 20), random.randint(2, 12))
                result /= operands[i + 1]
        q_parts = []
        for i in range(num_count - 1):
            q_parts.append(fmt_num(operands[i]))
            q_parts.append(op_latex[operator_sequence[i]])
        q_parts.append(fmt_num(operands[-1]))
        q = ' '.join(q_parts)
        q = clean_latex_output(q)
        a = fmt_num(result)
        if isinstance(a, str) and '=' in a:
            a = a.split('=')[-1].strip()
    elif template == 'DistributivePropertyApplication':
        num_a_type = random.choice(['rational_num_mixed', 'rational_num_basic'])
        num_b_type = random.choice(['rational_num_mixed', 'rational_num_basic'])
        common_factor_c_type = random.choice(['integer_factor', 'rational_num_basic'])
        connecting_operator = random.choice(['+', '-'])
        ensure_simple_inner_operation = random.choice([True, False])
        if common_factor_c_type == 'integer_factor':
            common_factor_c = Fraction(random.randint(-100, 100))
            while common_factor_c == 0:
                common_factor_c = Fraction(random.randint(-100, 100))
        else:
            numerator = random.randint(-20, 20)
            while numerator == 0:
                numerator = random.randint(-20, 20)
            denominator = random.randint(2, 12)
            common_factor_c = Fraction(numerator, denominator)
        if ensure_simple_inner_operation and connecting_operator == '-':
            difference_value = Fraction(random.randint(-5, 5))
            num_b = random_fraction(-10, 10, 1, 1000, 2, 12) if num_b_type == 'rational_num_basic' else random_mixed_number(-10, 10, -20, 20, 2, 12)
            num_a = num_b + difference_value
        else:
            num_a = random_fraction(-10, 10, 1, 1000, 2, 12) if num_a_type == 'rational_num_basic' else random_mixed_number(-10, 10, -20, 20, 2, 12)
            num_b = random_fraction(-10, 10, 1, 1000, 2, 12) if num_b_type == 'rational_num_basic' else random_mixed_number(-10, 10, -20, 20, 2, 12)
        inner_result = num_a + num_b if connecting_operator == '+' else num_a - num_b
        result = inner_result * common_factor_c
        q = f"{fmt_num(num_a)} {op_latex['*']} {fmt_neg_paren(fmt_num(common_factor_c))} {op_latex[connecting_operator]} {fmt_num(num_b)} {op_latex['*']} {fmt_neg_paren(fmt_num(common_factor_c))}"
        q = clean_latex_output(q)
        a = fmt_num(result)
        if isinstance(a, str) and '=' in a:
            a = a.split('=')[-1].strip()
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}