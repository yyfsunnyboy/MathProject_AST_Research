# skills/remainder.py
import random

def generate():
    x = random.randint(2, 5)
    c = [random.randint(1, 9) for _ in range(3)]
    poly = " + ".join(f"{v}x^{i}" if i > 0 else str(v) for i, v in enumerate(c))
    ans = sum(v * (x ** i) for i, v in enumerate(c))
    return {
        "question_text": f"用餘式定理求 f(x) = {poly} 除以 (x - {x}) 的餘式",  # 改這裡！
        "correct_answer": ans,
        "inequality_string": ""
    }

def check(user, correct):
    ok = str(user).strip() == str(correct)
    return {"correct": ok, "result": "正確！" if ok else f"錯誤，正解 {correct}"}