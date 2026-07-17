import random

def generate(level=1, **kwargs):
    def p(n):
        return f"({n})" if n < 0 else str(n)
    def op(n):
        return f"+{n}" if n >= 0 else str(n)
    case = random.randint(1, 4)
    if case == 1:
        a, b, c = random.randint(-15, 15), random.randint(-15, 15), random.randint(-50, 50)
        txt = f"{p(a)}×{p(b)}{op(c)}"
        ans = a * b + c
    elif case == 2:
        a, b, c, d = random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10)
        txt = f"{p(a)}×{p(b)}-{p(c)}×{p(d)}"
        ans = a * b - c * d
    elif case == 3:
        a, b, c, d, e = random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10), random.randint(-20, 20)
        txt = f"{p(a)}×{p(b)}+|{p(c)}×{d}{op(e)}|"
        ans = a * b + abs(c * d + e)
    else:
        d = random.choice([i for i in range(-10, 11) if i != 0])
        res = random.randint(-10, 10)
        dividend = d * res
        b = random.randint(-20, 20)
        a = dividend - b
        c = random.randint(-20, 20)
        txt = f"({p(a)}{op(b)})÷{p(d)}{op(c)}"
        ans = res + c
    return {
        'question_text': f"計算{txt}的值。",
        'answer': '',
        'correct_answer': str(ans),
        'mode': 1
    }

def check(user_answer, correct_answer):
    try:
        is_correct = str(user_answer).strip() == str(correct_answer).strip()
    except:
        is_correct = False
    return {
        'correct': is_correct,
        'result': '正確' if is_correct else '錯誤'
    }