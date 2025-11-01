import random

def generate_common_logarithm_question():
    power = random.randint(1, 3)
    base = 10
    number = base ** power
    question_text = f"計算 log({number}) = ?"
    return {
        "text": question_text,
        "answer": str(power),
        "validation_function_name": None
    }
