# skills/remainder.py
import random

# skills/remainder.py
def format_polynomial(coeffs):
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        if coeff == 0:
            continue

        # 符號處理
        if coeff > 0 and terms:
            sign = " + "
        elif coeff < 0:
            sign = " - "
            coeff = -coeff
        else:
            sign = ""

        # 係數為 1 或 -1 時省略
        if coeff == 1 and power > 0:
            coeff_str = ""
        elif coeff == -1 and power > 0:
            coeff_str = ""
        else:
            coeff_str = str(coeff)

        # x 變數 + 上標
        if power == 0:
            term = f"{sign}{coeff}"
        elif power == 1:
            term = f"{sign}{coeff_str}x"
        else:
            term = f"{sign}{coeff_str}x<sup>{power}</sup>"

        terms.append(term)

    return "".join(terms).lstrip(" + ").strip()

def generate():
    degree = 3
    coeffs = [0] * (degree + 1)
    coeffs[0] = random.randint(1, 3)  # 最高次係數
    for i in range(1, degree + 1):
        coeffs[i] = random.randint(-9, 9)

    k = random.randint(1, 4)
    remainder = sum(coeffs[i] * (k ** (degree - i)) for i in range(degree + 1))

    poly_html = format_polynomial(coeffs)

    return {
        "question_text": f"用餘式定理求 f(x) = {poly_html} 除以 (x - {k}) 的餘式",
        "answer": remainder
    }

def check(user, correct):
    user_str = str(user).strip()
    correct_str = str(correct).strip()
    return {
        "correct": user_str == correct_str,
        "result": "正確！" if user_str == correct_str else f"錯誤，正解 {correct}"
    }