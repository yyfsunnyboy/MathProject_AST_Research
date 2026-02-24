import random
import math

def generate(level=1, **kwargs):
    if level == 1:
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        c = random.randint(-20, 20)
        d = random.randint(-20, 20)
        e = random.randint(-20, 20)
        f = random.randint(-20, 20)
        question_text = f"計算({a})×{b}+|({c})×{d}-{e}|的值。"
        correct_answer = str(eval(question_text.replace('×', '*').replace('|', '').replace('(', '').replace(')', '')))
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
        user_answer = user_answer.strip()
        correct_answer = correct_answer.strip()
        if user_answer == correct_answer:
            return {'correct': True, 'result': '正確'}
        else:
            return {'correct': False, 'result': '錯誤'}
    except:
        return {'correct': False, 'result': '錯誤'}