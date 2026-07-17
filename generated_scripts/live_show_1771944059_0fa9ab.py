import random

def generate(level=1, **kwargs):
    if level == 1:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        d = random.randint(-10, 10)
        e = random.randint(-10, 10)
        f = random.randint(-10, 10)
        g = random.randint(-10, 10)
        h = random.randint(-10, 10)
        i = random.randint(-10, 10)
        j = random.randint(-10, 10)
        k = random.randint(-10, 10)
        l = random.randint(-10, 10)
        m = random.randint(-10, 10)
        n = random.randint(-10, 10)
        o = random.randint(-10, 10)
        p = random.randint(-10, 10)
        q = random.randint(-10, 10)
        r = random.randint(-10, 10)
        s = random.randint(-10, 10)
        t = random.randint(-10, 10)
        u = random.randint(-10, 10)
        v = random.randint(-10, 10)
        w = random.randint(-10, 10)
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        z = random.randint(-10, 10)
        question_text = f"計算({a})×{b}+|({c})×{d}-{e}|+{f}×{g}-{h}÷{i}+{j}×{k}-{l}÷{m}+{n}×{o}-{p}÷{q}+{r}×{s}-{t}÷{u}+{v}×{w}-{x}÷{y}+{z}的值。"
        correct_answer = str(eval(question_text.replace("×", "*").replace("÷", "/").replace("|", "").replace(")", "").replace("(", "").replace("+", "+").replace("-", "-")))
        return {
            'question_text': question_text,
            'answer': '',
            'correct_answer': correct_answer,
            'mode': 1
        }
    else:
        return {
            'question_text': '',
            'answer': '',
            'correct_answer': '',
            'mode': 1
        }

def check(user_answer, correct_answer):
    try:
        user_answer = int(user_answer)
        correct_answer = int(correct_answer)
        return {
            'correct': user_answer == correct_answer,
            'result': '正確' if user_answer == correct_answer else '錯誤'
        }
    except:
        return {
            'correct': False,
            'result': '錯誤'
        }