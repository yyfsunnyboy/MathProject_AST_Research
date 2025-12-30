import random

def sub_problem_reading():
    # 随机选择两个点的位置
    A = random.randint(-10, 10)
    B = random.randint(-10, 10)
    
    # 确保A和B不重合
    while A == B:
        B = random.randint(-10, 10)
    
    # 计算中点C的位置
    C = (A + B) / 2
    
    # 生成题目描述
    question = f"1. 畫一條數線，並標記 A ({A})、B ({B}) 的位置。\n"
    question += f"2. 寫出中點 C 的坐標。"
    
    # 生成答案
    answer = f"1. 圖示標示 A 點在 {A}，B 點在 {B}\n"
    answer += f"2. C({C})"
    
    return {
        "question": question,
        "answer": answer
    }

def sub_problem_distance():
    # 随机选择两个点的位置
    A = random.randint(-10, 10)
    B = random.randint(-10, 10)
    
    # 确保A和B不重合
    while A == B:
        B = random.randint(-10, 10)
    
    # 计算两点之间的距离
    distance = abs(A - B)
    
    # 生成题目描述
    question = f"1. 畫一條數線，並標記 A ({A})、B ({B}) 的位置。\n"
    question += f"2. 寫出 A 和 B 間的距離。"
    
    # 生成答案
    answer = f"1. 圖示標示 A 點在 {A}，B 點在 {B}\n"
    answer += f"2. 距離為 {distance}"
    
    return {
        "question": question,
        "answer": answer
    }

def generate(level=1):
    if level == 1:
        return sub_problem_reading()
    elif level == 2:
        return sub_problem_distance()
    else:
        raise ValueError("Invalid level. Please choose 1 or 2.")

def check(user_ans, correct_ans):
    # 忽略空白进行比对
    user_ans = user_ans.replace(" ", "")
    correct_ans = correct_ans.replace(" ", "")
    
    return user_ans == correct_ans