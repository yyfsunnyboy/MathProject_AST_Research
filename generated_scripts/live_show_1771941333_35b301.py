import random

def generate(level=1, **kwargs):
    def f(n):
        return "(" + str(n) + ")" if n < 0 else str(n)
    t = random.randint(0, 3)
    if t == 0:
        a = random.randint(-12, 12)
        b = random.randint(-12, 12)
        c = random.randint(-12, 12)
        ans = a * (b + c)
        txt = f(a) + "×(" + f(b) + "+" + f(c) + ")"
    elif t == 1:
        a = random.randint(-20, 20)
        b = random.randint(-12, 12)
        c = random.randint(-12, 12)
        ans = a - b * c
        txt = f(a) + "-" + f(b) + "×" + f(c)
    elif t == 2:
        c = random.choice([i for i in range(-12, 13) if i != 0])
        p = random.randint(-12, 12)
        a = c * p
        b = random.randint(-20, 20)
        ans = p + b
        txt = f(a) + "÷" + f(c) + "+" + f(b)
    else:
        a = random.randint(-10, -2)
        b = random.randint(10, 25)
        c = random.randint(2, 8)
        d = random.randint(-10, -2)
        ans = a * (b - c * d)
        txt = f(a) + "×[" + str(b) + "-" + str(c) + "×" + f(d) + "]"
    return {
        'question_text': txt,
        'answer': '',
        'correct_answer': str(ans),
        'mode': 1
    }

def check(user_answer, correct_answer):
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    return {
        'correct': is_correct,
        'result': '正確' if is_correct else '錯誤'
    }