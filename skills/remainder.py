import random
from core.helpers import format_polynomial, validate_remainder

def generate_remainder_theorem_question():
    """動態生成一道「餘式定理」的題目 (二次式或三次式)"""
    degree = random.choice([2, 3])
    k = random.randint(-3, 3)
    coeffs = []
    correct_answer = 0
    if degree == 2:
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        c = random.randint(-9, 9)
        coeffs = [a, b, c]
        correct_answer = (a * (k**2)) + (b * k) + c
    elif degree == 3:
        a = random.randint(-2, 2)
        while a == 0:
            a = random.randint(-2, 2)
        b = random.randint(-3, 3)
        c = random.randint(-5, 5)
        d = random.randint(-9, 9)
        coeffs = [a, b, c, d]
        correct_answer = (a * (k**3)) + (b * (k**2)) + (c * k) + d
    poly_text = format_polynomial(coeffs)
    k_sign = "-" if k >= 0 else "+"
    k_abs = abs(k)
    divisor_text = "(x)" if k == 0 else f"(x {k_sign} {k_abs})"
    question_text = f"求 f(x) = {poly_text} 除以 {divisor_text} 的餘式。"
    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": validate_remainder.__name__
    }
