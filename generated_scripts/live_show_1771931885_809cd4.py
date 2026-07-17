import random

def generate(level=1, **kwargs):
    def fmt(n):
        return f"({n})" if n < 0 else str(n)
    while True:
        t = random.randint(1, 4)
        try:
            if t == 1:
                a, b = random.randint(-12, 12), random.randint(-12, 12)
                c, d = random.randint(-50, 50), random.randint(1, 12) * random.choice([-1, 1])
                if c % d != 0: continue
                op = "+" if c >= 0 else "-"
                q = f"{a} × {fmt(b)} {op} {abs(c)} ÷ {fmt(d)}"
                v = a * b + (c // d)
            elif t == 2:
                a, b, c, d = [random.randint(-10, 10) for _ in range(4)]
                op1, op2 = ("+" if b >= 0 else "-"), ("+" if d >= 0 else "-")
                q = f"({a} {op1} {abs(b)}) × ({c} {op2} {abs(d)})"
                v = (a + b) * (c + d)
            elif t == 3:
                a, b, c = random.randint(-9, 9), random.randint(-9, 9), random.randint(-20, 20)
                d, e = random.randint(1, 10) * random.choice([-1, 1]), random.randint(-9, 9)
                if abs(a * b + c) % d != 0: continue
                op = "+" if c >= 0 else "-"
                q = f"| {a} × {fmt(b)} {op} {abs(c)} | ÷ {fmt(d)} × {fmt(e)}"
                v = (abs(a * b + c) // d) * e
            else:
                a, b, c, d = random.randint(-20, 20), random.randint(-8, 8), random.randint(-8, 8), random.randint(-15, 15)
                op = "+" if d >= 0 else "-"
                q = f"{a} - ({b} × {fmt(c)} {op} {abs(d)})"
                v = a - (b * c + d)
            return {
                'question_text': f"計算 {q} 的值。",
                'answer': '',
                'correct_answer': str(int(v)),
                'mode': 1
            }
        except ZeroDivisionError:
            continue

def check(user_answer, correct_answer):
    try:
        c = str(user_answer).strip() == str(correct_answer).strip()
    except:
        c = False
    return {
        'correct': c,
        'result': '正確' if c else '錯誤'
    }