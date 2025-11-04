import random
import math

def generate():
    """
    生成一個計算平面上兩點距離的題目。
    """
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)
    x2 = random.randint(-10, 10)
    y2 = random.randint(-10, 10)

    # 確保兩點不重合
    while x1 == x2 and y1 == y2:
        x2 = random.randint(-10, 10)
        y2 = random.randint(-10, 10)

    question_text = f"計算平面上兩點 A({x1}, {y1}) 和 B({x2}, {y2}) 之間的距離。"
    
    # 計算正確答案
    distance_squared = (x2 - x1)**2 + (y2 - y1)**2
    answer = f"sqrt({distance_squared})" # 答案可以是根號形式
    
    # 為了檢查，我們也計算數值
    correct_answer = math.sqrt(distance_squared)

    return {
        "question_text": question_text,
        "answer": str(correct_answer) # 儲存數值答案用於檢查
    }

def check(user_answer, correct_answer):
    """
    檢查使用者計算的距離是否正確。
    允許一定的誤差。
    """
    try:
        user_ans_float = float(user_answer)
        correct_ans_float = float(correct_answer)
        
        # 允許一定的浮點數誤差
        if math.isclose(user_ans_float, correct_ans_float, rel_tol=1e-9, abs_tol=0.0):
            return {"correct": True, "result": "完全正確！"}
        else:
            # 檢查是否答案是根號形式的平方
            if user_ans_float == correct_ans_float**2:
                 return {"correct": False, "result": f"您可能忘記開根號了喔！正確答案是 {correct_ans_float:.2f}。"}
            return {"correct": False, "result": f"答案不正確。正確答案是 {correct_ans_float:.2f}。"}
    except ValueError:
        # 處理使用者可能輸入根號表示法，例如 "sqrt(50)"
        import re
        match = re.match(r"sqrt\((\d+)\)", user_answer.replace(" ", ""))
        if match:
            num = int(match.group(1))
            correct_distance_squared = round(float(correct_answer)**2)
            if num == correct_distance_squared:
                return {"correct": True, "result": "完全正確！"}
        
        return {"correct": False, "result": "請輸入一個數字或 'sqrt(數字)' 的格式。"}