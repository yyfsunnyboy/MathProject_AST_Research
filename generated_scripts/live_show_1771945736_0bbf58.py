import random

def generate(level=1, **kwargs):
    def fmt(n):
        return f"({n})" if n < 0 else str(n)
    while True:
        try:
            t = random.randint(1, 4)
            if t == 1:
                a, b, c = random.randint(-15, 15), random.randint(-15, 15), random.randint(-30, 30)
                op = random.choice(['+', '-'])
                val = (a * b + c) if op == '+' else (a * b - c)
                expr = f"{fmt(a)}×{fmt(b)}{op}{fmt(c)}"
            elif t == 2:
                b, c = random.randint(-20, 20), random.randint(-20, 20)
                op = random.choice(['+', '-'])
                inner = (b + c) if op == '+' else (b - c)
                if inner == 0: continue
                res = random.randint(-15, 15)
                a = inner * res
                val = res
                expr = f"{fmt(a)}÷[{fmt(b)}{op}{fmt(c)}]"
            elif t == 3:
                b, c, d = random.randint(-10, 10), random.randint(-10, 10), random.randint(-20, 20)
                op = random.choice(['+', '-'])
                inner = (b * c + d) if op == '+' else (b * c - d)
                if inner == 0: continue
                res = random.randint(-10, 10)
                a = inner * res
                val = res
                expr = f"{fmt(a)}÷[{fmt(b)}×{fmt(c)}{op}{fmt(d)}]"
            else:
                a, b, c, d = [random.randint(-10, 10) for _ in range(4)]
                op1, op2 = random.choice(['+', '-']), random.choice(['+', '-'])
                v1 = (a + b) if op1 == '+' else (a - b)
                v2 = (c + d) if op2 == '+' else (c - d)
                val = v1 * v2
                expr = f"[{fmt(a)}{op1}{fmt(b)}]×[{fmt(c)}{op2}{fmt(d)}]"
            return {
                'question_text': f"計算{expr}的值。",
                'answer': '',
                'correct_answer': str(int(val)),
                'mode': 1
            }
        except:
            continue

def check(user_answer, correct_answer):
    try:
        is_correct = int(user_answer) == int(correct_answer)
    except:
        is_correct = str(user_answer).strip() == str(correct_answer).strip()
    return {
        'correct': is_correct,
        'result': '正確' if is_correct else '錯誤'
    }