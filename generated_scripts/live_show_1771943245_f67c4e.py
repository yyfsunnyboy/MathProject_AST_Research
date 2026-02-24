import random

def generate(level=1, **kwargs):
    ops = ['+', '-', '*', '/']
    sym = {'+': '+', '-': '-', '*': '×', '/': '÷'}
    while True:
        n = [random.randint(-20, 20) for _ in range(3)]
        n = [x if x != 0 else random.randint(1, 10) for x in n]
        o = [random.choice(ops) for _ in range(2)]
        try:
            if o[1] in ['*', '/'] and o[0] in ['+', '-']:
                if o[1] == '/' and n[1] % n[2] != 0: continue
                ans = eval(f"{n[0]}{o[0]}({n[1]}{o[1]}{n[2]})")
            else:
                if o[0] == '/' and n[0] % n[1] != 0: continue
                mid = eval(f"{n[0]}{o[0]}{n[1]}")
                if o[1] == '/' and mid % n[2] != 0: continue
                ans = eval(f"({n[0]}{o[0]}{n[1]}){o[1]}{n[2]}")
            
            def f(v, p):
                return str(v) if (v >= 0 or p) else f"({v})"
            
            txt = f"{f(n[0], True)} {sym[o[0]]} {f(n[1], False)} {sym[o[1]]} {f(n[2], False)}"
            return {
                'question_text': txt,
                'answer': '',
                'correct_answer': str(int(ans)),
                'mode': 1
            }
        except:
            continue

def check(user_answer, correct_answer):
    c = str(user_answer).strip() == str(correct_answer).strip()
    return {
        'correct': c,
        'result': '正確' if c else '錯誤'
    }