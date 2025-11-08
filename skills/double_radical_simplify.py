import random
import math

def generate(level=1):
    """
    生成一道「化簡雙重根式」的題目。
    √(X ± 2√Y)，其中 X = a+b, Y = ab，化簡為 √a ± √b
    level 1: a, b 為整數
    level 2: a, b 其中一個可能不是完全平方數
    """
    if level == 1:
        a = random.randint(2, 10)
        b = random.randint(1, a - 1)
    else: # level 2
        a = random.randint(2, 10)
        b = random.randint(1, a - 1)
        # 增加複雜度，但保持可解
        if random.random() < 0.5:
            a *= random.choice([2,3])
        else:
            b *= random.choice([2,3])

    X = a + b
    Y = a * b
    op_symbol = random.choice(['+', '-'])
    
    question_text = f"請化簡雙重根式：√({X} {op_symbol} 2√{Y})"
    
    # 確保 a > b
    if a < b: a, b = b, a

    correct_answer = f"√{a} {op_symbol} √{b}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}