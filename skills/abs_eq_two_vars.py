import random

def generate(level=1):
    """
    生成一道「含絕對值之二元一次方程式圖形」的題目。
    此為觀念題，要求學生辨識圖形。
    level 1: |x| + |y| = k
    level 2: |ax+by| = k
    """
    if level == 1:
        k = random.randint(2, 8)
        question_text = (
            f"請問二元一次方程式 |x| + |y| = {k} 的圖形在直角坐標平面上是什麼形狀？\n\n"
            "A) 一條直線\n"
            "B) 兩條平行線\n"
            "C) 一個正方形\n"
            "D) 一個圓形"
        )
        correct_answer = "C"
    else: # level 2
        a = random.randint(1, 3)
        b = random.randint(1, 3)
        k = random.randint(2, 8)
        question_text = (
            f"請問二元一次方程式 |{a}x + {b}y| = {k} 的圖形在直角坐標平面上是什麼形狀？\n\n"
            "A) 一條直線\n"
            "B) 兩條平行線\n"
            "C) 兩條相交直線\n"
            "D) 一個圓形"
        )
        correct_answer = "B"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}