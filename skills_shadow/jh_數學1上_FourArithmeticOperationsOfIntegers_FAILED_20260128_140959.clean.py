def fmt_num(x):
    return f'({x})' if x < 0 else str(x)
op_latex = {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}

def generate(level=1, **kwargs):
    max_attempts = 50
    for attempt in range(max_attempts):
        op1 = safe_choice(['+', '-', '*'])
        op2 = safe_choice(['+', '-', '*', '/'])
        op3 = safe_choice(['+', '-', '*', '/'])
        if op1 not in ['*', '/'] and op2 not in ['*', '/'] and (op3 not in ['*', '/']):
            continue
        n1, n2 = (random.randint(-20, -1) if random.random() < 0.5 else random.randint(1, 20), random.randint(-20, -1) if random.random() < 0.5 else random.randint(1, 20))
        n3, n4 = (random.randint(-10, -1) if random.random() < 0.5 else random.randint(1, 10), random.randint(-10, -1) if random.random() < 0.5 else random.randint(1, 10))
        if n1 > 0 and n2 > 0 and (n3 > 0) and (n4 > 0):
            if safe_choice([True, False]):
                n1 = -n1
            elif safe_choice([True, False]):
                n2 = -n2
            elif safe_choice([True, False]):
                n3 = -n3
            else:
                n4 = -n4
        temp1 = safe_eval(f'{n1} {op1} {n2}')
        if abs(temp1) > 100:
            continue
        if op2 == '/':
            if n3 == 0 or temp1 % n3 != 0:
                divisors = [d for d in range(-10, -1) + list(range(1, 11)) if d != 0 and temp1 % d == 0]
                if not divisors:
                    continue
                n3 = safe_choice(divisors)
            temp2 = safe_eval(f'{temp1} {op2} {n3}')
        else:
            temp2 = safe_eval(f'{temp1} {op2} {n3}')
        if abs(temp2) > 100:
            continue
        if op3 == '/':
            if n4 == 0 or temp2 % n4 != 0:
                divisors = [d for d in range(-10, -1) + list(range(1, 11)) if d != 0 and temp2 % d == 0]
                if not divisors:
                    continue
                n4 = safe_choice(divisors)
            final_result = safe_eval(f'{temp2} {op3} {n4}')
        else:
            final_result = safe_eval(f'{temp2} {op3} {n4}')
        if abs(final_result) > 200 or not isinstance(final_result, int):
            continue
        q_str = f'[{fmt_num(n1)} {op_latex[op1]} {fmt_num(n2)}] {op_latex[op2]} {fmt_num(n3)} {op_latex[op3]} {fmt_num(n4)}'
        q_str = clean_latex_output(q_str)
        answer = str(final_result)
        return {'question_text': q_str, 'answer': answer, 'mode': 1}
    raise Exception('Failed to generate a valid arithmetic problem within the specified constraints.')