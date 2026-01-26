def generate(level=1, **kwargs):
    template = random.choice(['chained_arithmetic_operations', 'distributive_property_arithmetic'])
    if template == 'chained_arithmetic_operations':
        num_terms = random.choice([3, 4])
        term_types = [random.choice(['integer', 'fraction', 'decimal', 'mixed_number']) for _ in range(num_terms)]
        operator_choices = [random.choice(['+', '-', '*', '/']) for _ in range(num_terms - 1)]
        parentheses_structure = random.choice(['none', 'first_pair', 'last_pair'])
        allow_negatives = random.choice([True, False])

        def _rand_num(term_type):
            if term_type == 'integer':
                return Fraction(random.randint(-100, -1) if allow_negatives else 1, 1)
            elif term_type == 'fraction':
                for _safety_loop_var in range(1000):
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(num, den)
            elif term_type == 'decimal':
                for _safety_loop_var in range(1000):
                    num = random.uniform(-50.0, -1.0) if allow_negatives else random.uniform(1.0, 50.0)
                    if abs(num) > 0:
                        return Fraction(str(round(num, 2)))
            elif term_type == 'mixed_number':
                for _safety_loop_var in range(1000):
                    whole = random.randint(-10, -1) if allow_negatives else random.randint(1, 10)
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(whole * den + num, den)
        numbers = [_rand_num(term_type) for term_type in term_types]

        def _safe_divide(a, b):
            while b == 0:
                b = _rand_num(term_types[1])
            return a / b
        if parentheses_structure == 'none':
            result = numbers[0]
            for i in range(1, num_terms):
                if operator_choices[i - 1] == '/':
                    result = _safe_divide(result, numbers[i])
                else:
                    result = result + numbers[i] if operator_choices[i - 1] == '+' else result - numbers[i] if operator_choices[i - 1] == '-' else result * numbers[i]
        elif parentheses_structure == 'first_pair':
            result = _safe_divide(numbers[0], numbers[1]) if operator_choices[0] == '/' else numbers[0] + numbers[1] if operator_choices[0] == '+' else numbers[0] - numbers[1] if operator_choices[0] == '-' else numbers[0] * numbers[1]
            result = _safe_divide(result, numbers[2]) if operator_choices[1] == '/' else result + numbers[2] if operator_choices[1] == '+' else result - numbers[2] if operator_choices[1] == '-' else result * numbers[2]
        elif parentheses_structure == 'last_pair':
            result = _safe_divide(numbers[num_terms - 2], numbers[num_terms - 1]) if operator_choices[-1] == '/' else numbers[num_terms - 2] + numbers[num_terms - 1] if operator_choices[-1] == '+' else numbers[num_terms - 2] - numbers[num_terms - 1] if operator_choices[-1] == '-' else numbers[num_terms - 2] * numbers[num_terms - 1]
            result = _safe_divide(numbers[0], result) if operator_choices[0] == '/' else numbers[0] + result if operator_choices[0] == '+' else numbers[0] - result if operator_choices[0] == '-' else numbers[0] * result
        elif parentheses_structure == 'middle_pair':
            result = _safe_divide(numbers[1], numbers[2]) if operator_choices[1] == '/' else numbers[1] + numbers[2] if operator_choices[1] == '+' else numbers[1] - numbers[2] if operator_choices[1] == '-' else numbers[1] * numbers[2]
            result = _safe_divide(numbers[0], result) if operator_choices[0] == '/' else numbers[0] + result if operator_choices[0] == '+' else numbers[0] - result if operator_choices[0] == '-' else numbers[0] * result
            result = _safe_divide(result, numbers[3]) if operator_choices[2] == '/' else result + numbers[3] if operator_choices[2] == '+' else result - numbers[3] if operator_choices[2] == '-' else result * numbers[3]
        q = ''
        for i in range(num_terms):
            if i > 0:
                op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
                q += f' {op_latex[operator_choices[i - 1]]} '
            if parentheses_structure == 'first_pair' and i == 0:
                q += '('
            elif parentheses_structure == 'last_pair' and i == num_terms - 2:
                q += '('
            elif parentheses_structure == 'middle_pair' and i == 1:
                q += '('
            q += fmt_num(numbers[i])
            if parentheses_structure == 'first_pair' and i == 1:
                q += ')'
            elif parentheses_structure == 'last_pair' and i == num_terms - 1:
                q += ')'
            elif parentheses_structure == 'middle_pair' and i == 2:
                q += ')'
        q = clean_latex_output(q)
        a = fmt_num(result)
    elif template == 'distributive_property_arithmetic':
        common_factor_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        term1_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        term2_type = random.choice(['integer', 'fraction', 'decimal', 'mixed_number'])
        middle_operator = random.choice(['+', '-'])
        allow_negatives = random.choice([True, False])

        def _rand_num(term_type):
            if term_type == 'integer':
                return Fraction(random.randint(-100, -1) if allow_negatives else 1, 1)
            elif term_type == 'fraction':
                for _safety_loop_var in range(1000):
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(num, den)
            elif term_type == 'decimal':
                for _safety_loop_var in range(1000):
                    num = random.uniform(-50.0, -1.0) if allow_negatives else random.uniform(1.0, 50.0)
                    if abs(num) > 0:
                        return Fraction(str(round(num, 2)))
            elif term_type == 'mixed_number':
                for _safety_loop_var in range(1000):
                    whole = random.randint(-10, -1) if allow_negatives else random.randint(1, 10)
                    num = random.randint(-50, 50)
                    den = random.randint(2, 15)
                    if num != 0 and den != 0:
                        return Fraction(whole * den + num, den)
        A = _rand_num(common_factor_type)
        B = _rand_num(term1_type)
        C = _rand_num(term2_type)
        term1_product = A * B
        term2_product = A * C
        final_result = term1_product + term2_product if middle_operator == '+' else term1_product - term2_product
        q = f'{fmt_num(A)} \\times {fmt_num(B)} {op_latex[middle_operator]} {fmt_num(A)} \\times {fmt_num(C)}'
        q = clean_latex_output(q)
        a = fmt_num(final_result)
    if isinstance(q, str):
        q = re.sub('^計算下列.*[: :]?', '', q).strip()
        q = re.sub('^\\(?\\d+[\\)）]\\.?\\s*', '', q).strip()
    if isinstance(a, str):
        if '=' in a:
            a = a.split('=')[-1].strip()
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}