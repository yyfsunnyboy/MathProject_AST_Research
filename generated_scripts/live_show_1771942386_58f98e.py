import random

def generate(level=1, **kwargs):
    ops = ['+', '-', '×', '÷']
    o1 = random.choice(ops)
    o2 = random.choice(ops)
    if o1 == '÷':
        v2 = random.randint(-12, 12)
        if v2 == 0: v2 = 1
        v1_r = random.randint(-12, 12)
        v1 = v1_r * v2
    elif o1 == '×':
        v1 = random.randint(-12, 12)
        v2 = random.randint(-12, 12)
        v1_r = v1 * v2
    else:
        v1 = random.randint(-40, 40)
        v2 = random.randint(-40, 40)
        v1_r = v1 + v2 if o1 == '+' else v1 - v2
    if o2 == '÷':
        ds = [i for i in range(-15, 16) if i != 0 and v1_r % i == 0]
        v3 = random.choice(ds)
        res = v1_r // v3
    elif o2 == '×':
        v3 = random.randint(-12, 12)
        res = v1_r * v3
    else:
        v3 = random.randint(-40, 40)
        res = v1_r + v3 if o2 == '+' else v1_r - v3
    def f(n, first=False):
        if n < 0 and not first: return "(" + str(n) + ")"
        return str(n)
    pr = {'+': 1, '-': 1, '×': 2, '÷': 2}
    if pr[o2] > pr[o1]:
        q = "(" + f(v1, True) + o1 + f(v2) + ")" + o2 + f(v3)
    else:
        q = f(v1, True) + o1 + f(v2) + o2 + f(v3)
    return {
        'question_text': q,
        'answer': '',
        'correct_answer': str(int(res)),
        'mode': 1
    }

def check(user_answer, correct_answer):
    try:
        status = int(user_answer) == int(correct_answer)
    except:
        status = False
    return {
        'correct': status,
        'result': '正確' if status else '錯誤'
    }