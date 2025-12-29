import random

def generate(level=1):
    # 1. Define Variables (Logic Layer)
    a = random.randint(-10, 10)
    dist = random.randint(1, 10)
    direction = random.choice(['right', 'left'])
    
    # 2. Calculate Answer
    if direction == 'right':
        target_val = a + dist
        dir_text = "右"
    else:
        target_val = a - dist
        dir_text = "左"
    
    # 3. Question Text
    question_text = f"""數線上 A 點座標為 ${a}$，B 點在 A 點的{dir_text}邊 ${dist}$ 單位處，求 B 點座標？"""
    
    # 4. Return Data
    return {
        "question_text": question_text,
        "answer": str(target_val),
        "correct_answer": str(target_val)
    }

def check(user_ans, correct_ans):
    return {"correct": user_ans.strip() == correct_ans.strip(), "result": f"答案是 ${correct_ans}$", "next_question": True}