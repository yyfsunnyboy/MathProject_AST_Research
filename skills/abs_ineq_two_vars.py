import random

def generate(level=1):
    """
    生成一道「含絕對值之二元一次不等式圖形」的題目。
    此為觀念題，要求學生辨識圖形區域。
    level 1: |x| + |y| <= k
    level 2: |ax+by| <= k
    """
    k = random.randint(2, 8)
    op = random.choice(['<=', '>='])

    if level == 1:
        question_text = (
            f"請問二元一次不等式 |x| + |y| {op} {k} 的圖形是「正方形」的內部還是外部區域？\n\n"
            "A) 內部（含邊界）\n"
            "B) 外部（含邊界）"
        )
        correct_answer = "A" if op == '<=' else "B"
    else: # level 2
        a = random.randint(1, 3)
        b = random.randint(1, 3)
        question_text = (
            f"請問二元一次不等式 |{a}x + {b}y| {op} {k} 的圖形是「兩平行線」的內部還是外部區域？\n\n"
            "A) 內部（含邊界）\n"
            "B) 外部（含邊界）"
        )
        correct_answer = "A" if op == '<=' else "B"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}