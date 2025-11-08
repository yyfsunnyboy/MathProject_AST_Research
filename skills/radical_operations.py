import random
import math

def simplify_radical(n):
    """輔助函式：化簡根式 sqrt(n)"""
    if n < 0: n = -n # 處理負數
    if n == 0: return 0, 1
    i = 2
    limit = int(math.sqrt(n))
    a = 1
    b = n
    while i <= limit:
        if b % (i*i) == 0:
            b = b // (i*i)
            a = a * i
            limit = int(math.sqrt(b))
            continue
        i += 1
    return a, b

def generate(level=1):
    """
    生成一道「根式四則運算」的題目。
    level 1: 同類方根加減或簡單乘除，答案為整數。
    level 2: 不同類方根運算，需要化簡。
    """
    op = random.choice(['+', '-', '*', '/'])

    if level == 1:
        # Level 1: 同類方根加減或簡單乘除
        rad = random.choice([2, 3, 5, 7])
        c1 = random.randint(2, 10)
        c2 = random.randint(1, c1 - 1)
        if op == '+':
            question_text = f"請計算：{c1}√{rad} + {c2}√{rad}"
            ans_coeff = c1 + c2
            correct_answer = f"{ans_coeff}√{rad}"
        elif op == '-':
            question_text = f"請計算：{c1}√{rad} - {c2}√{rad}"
            ans_coeff = c1 - c2
            correct_answer = f"{ans_coeff}√{rad}"
        elif op == '*':
            question_text = f"請計算：√{rad} * √{rad}"
            correct_answer = str(rad)
        else: # '/'
            num = rad * random.randint(2,5)**2
            question_text = f"請計算：√{num} / √{rad}"
            correct_answer = str(int(math.sqrt(num/rad)))
    else:
        # Level 2: 不同類方根運算
        a1, b1 = random.randint(2, 5), random.choice([2, 3, 5])
        a2, b2 = random.randint(2, 5), random.choice([2, 3, 5])
        n1 = a1**2 * b1
        n2 = a2**2 * b2
        if op == '+':
            question_text = f"請計算並化簡：√{n1} + √{n2}"
            s1_a, s1_b = simplify_radical(n1)
            s2_a, s2_b = simplify_radical(n2)
            if s1_b == s2_b:
                correct_answer = f"{s1_a + s2_a}√{s1_b}"
            else: # 無法合併
                correct_answer = f"{s1_a}√{s1_b}+{s2_a}√{s2_b}"
        elif op == '-':
            # 確保答案不為0
            while n1 == n2: n2 = random.randint(2, 5)**2 * random.choice([2, 3, 5])
            question_text = f"請計算並化簡：√{n1} - √{n2}"
            s1_a, s1_b = simplify_radical(n1)
            s2_a, s2_b = simplify_radical(n2)
            if s1_b == s2_b:
                correct_answer = f"{s1_a - s2_a}√{s1_b}"
            else:
                correct_answer = f"{s1_a}√{s1_b}-{s2_a}√{s2_b}"
        else: # '*' or '/'
            question_text = f"請計算並化簡：√{n1} * √{n2}"
            prod = n1 * n2
            s_a, s_b = simplify_radical(prod)
            correct_answer = f"{s_a}√{s_b}" if s_b != 1 else str(s_a)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}