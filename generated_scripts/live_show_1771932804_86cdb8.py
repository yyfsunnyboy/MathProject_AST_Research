import random

def generate(level=1, **kwargs):
    def f(n):
        return f"({n})" if n < 0 else str(n)

    def calc(a, b, op):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '×': return a * b
        if op == '÷': return a // b
        return 0

    ops = ['+', '-', '×', '÷']
    r = 10 + level * 5

    while True:
        try:
            mode = random.randint(1, 3)
            if mode == 1:
                op2 = random.choice(ops)
                b, c = random.randint(-r, r), random.randint(-r, r)
                if op2 == '÷':
                    if c == 0: c = random.choice([-2, -1, 1, 2])
                    b = c * random.randint(-5, 5)
                v_inner = calc(b, c, op2)
                op1 = random.choice(ops)
                a = random.randint(-r, r)
                if op1 == '÷':
                    if v_inner == 0: continue
                    a = v_inner * random.randint(-5, 5)
                v_total = calc(a, v_inner, op1)
                q = f"{f(a)}{op1}({f(b)}{op2}{f(c)})"
            elif mode == 2:
                op1, op3 = random.choice(ops), random.choice(ops)
                a, b = random.randint(-r, r), random.randint(-r, r)
                if op1 == '÷':
                    if b == 0: b = random.choice([-2, -1, 1, 2])
                    a = b * random.randint(-5, 5)
                v1 = calc(a, b, op1)
                c, d = random.randint(-r, r), random.randint(-r, r)
                if op3 == '÷':
                    if d == 0: d = random.choice([-2, -1, 1, 2])
                    c = d * random.randint(-5, 5)
                v2 = calc(c, d, op3)
                op2 = random.choice(ops)
                if op2 == '÷':
                    if v2 == 0: continue
                    v1 = v2 * random.randint(-3, 3)
                    if op1 == '+': a, b = v1 - 5, 5
                    elif op1 == '-': a, b = v1 + 5, 5
                    elif op1 == '×': a, b = v1, 1
                    else: a, b = v1, 1
                v_total = calc(v1, v2, op2)
                q = f"({f(a)}{op1}{f(b)}){op2}({f(c)}{op3}{f(d)})"
            else:
                op3 = random.choice(['×', '÷'])
                c, d = random.randint(-r, r), random.randint(-r, r)
                if op3 == '÷':
                    if d == 0: d = random.choice([-2, -1, 1, 2])
                    c = d * random.randint(-5, 5)
                v_inner = calc(c, d, op3)
                op2 = random.choice(['+', '-'])
                b = random.randint(-r, r)
                v_mid = calc(b, v_inner, op2)
                op1 = random.choice(['×', '÷'])
                a = random.randint(-r, r)
                if op1 == '÷':
                    if v_mid == 0: continue
                    a = v_mid * random.randint(-3, 3)
                v_total = calc(a, v_mid, op1)
                q = f"{f(a)}{op1}[{f(b)}{op2}{f(c)}{op3}{f(d)}]"
            
            return {
                'question_text': q,
                'answer': '',
                'correct_answer': str(v_total),
                'mode': 1
            }
        except ZeroDivisionError:
            continue

def check(user_answer, correct_answer):
    try:
        is_correct = str(user_answer).strip() == str(correct_answer).strip()
    except:
        is_correct = False
    return {
        'correct': is_correct,
        'result': '正確' if is_correct else '錯誤'
    }