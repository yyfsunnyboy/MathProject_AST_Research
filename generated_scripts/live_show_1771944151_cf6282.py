import random

def generate(level=1, **kwargs):
    ops_map = {'+': '+', '-': '-', '*': '×', '/': '÷'}
    while True:
        n1 = random.randint(-15, 15)
        n2 = random.randint(-15, 15)
        n3 = random.randint(-15, 15)
        o1 = random.choice(['+', '-', '*', '/'])
        o2 = random.choice(['+', '-', '*', '/'])
        t = random.randint(1, 3)
        def f(n):
            return f"({n})" if n < 0 else str(n)
        try:
            if t == 1:
                e = f"({n1}){o1}({n2}){o2}({n3})"
                q = f"{f(n1)}{ops_map[o1]}{f(n2)}{ops_map[o2]}{f(n3)}"
            elif t == 2:
                e = f"({n1}){o1}(({n2}){o2}({n3}))"
                q = f"{f(n1)}{ops_map[o1]}({f(n2)}{ops_map[o2]}{f(n3)})"
            else:
                e = f"(({n1}){o1}({n2})){o2}({n3})"
                q = f"({f(n1)}{ops_map[o1]}{f(n2)}){ops_map[o2]}{f(n3)}"
            r = eval(e)
            if isinstance(r, (int, float)) and r == int(r):
                return {
                    'question_text': q,
                    'answer': '',
                    'correct_answer': str(int(r)),
                    'mode': 1
                }
        except ZeroDivisionError:
            continue

def check(user_answer, correct_answer):
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    return {
        'correct': is_correct,
        'result': '正確' if is_correct else '錯誤'
    }