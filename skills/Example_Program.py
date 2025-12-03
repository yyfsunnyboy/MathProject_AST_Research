import random
from fractions import Fraction

def generate(level=1):
    """
    生成「數線」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 相對位置
    2. 座標大小比較
    3. 中點座標
    4. 數線讀值
    """
    problem_type = random.choice(['relative_pos', 'comparison', 'midpoint', 'ascii_read'])
    
    if problem_type == 'relative_pos':
        return generate_relative_pos_problem()
    elif problem_type == 'comparison':
        return generate_comparison_problem()
    elif problem_type == 'midpoint':
        return generate_midpoint_problem()
    else:
        return generate_ascii_read_problem()

def generate_relative_pos_problem():
    # 題型：數線上 A 點座標為 val_a，B 點在 A 點的 [方向] val_diff 單位處
    val_a = random.randint(-10, 10)
    val_diff = random.randint(1, 10)
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b = val_a + val_diff
        op_str = "+"
    else:
        val_b = val_a - val_diff
        op_str = "-"
        
    # [教學示範] 注意：數學符號與數字都用 $ 包裹
    # 這裡示範了如何正確嵌入變數： ${val_a}$
    question_text = f"數線上 $A$ 點座標為 ${val_a}$，$B$ 點在 $A$ 點的{direction}邊 ${val_diff}$ 單位處，請問 $B$ 點座標為何？"
    correct_answer = str(val_b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    # 題型：已知 A(a), B(b), C(c)...
    points = {}
    labels = ['A', 'B', 'C', 'D']
    num_points = random.choice([3, 4])
    used_labels = labels[:num_points]
    
    coords = random.sample(range(-20, 21), num_points)
    
    points_desc = []
    for i, label in enumerate(used_labels):
        points[label] = coords[i]
        # [教學示範] 座標表示法：$A(-5)$
        # 同時示範下標正確寫法 (雖然這裡沒用到，但給 AI 看)：$P_{i}$ (必須有大括號)
        points_desc.append(f"${label}({coords[i]})$")
        
    target = random.choice(['左', '右'])
    
    if target == '右':
        correct_label = max(points, key=points.get)
    else:
        correct_label = min(points, key=points.get)
        
    # [教學示範] 列表串接
    question_text = f"已知數線上 {', '.join(points_desc)}，請問哪一點在最{target}邊？(請填代號)"
    correct_answer = correct_label
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    val_a = random.randint(-15, 15)
    diff = random.randint(1, 10) * 2 
    
    if random.random() < 0.3:
        diff = random.randint(1, 10) * 2 + 1
        
    val_b = val_a + diff
    midpoint = (val_a + val_b) / 2
    
    if midpoint.is_integer():
        midpoint_str = str(int(midpoint))
    else:
        midpoint_str = str(midpoint)
        
    # [教學示範] 兩點座標與中點公式暗示
    question_text = f"數線上兩點 $A({val_a})$、$B({val_b})$，請問 $A$、$B$ 兩點的中點座標為何？"
    correct_answer = midpoint_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ascii_read_problem():
    # ASCII 圖形通常保持原樣，不需要加 $，但在描述文字中可以使用 LaTeX
    start = random.randint(-10, 5)
    step = random.randint(1, 3)
    length = 5
    
    sequence = [start + i*step for i in range(length)]
    missing_idx = random.randint(1, length-2)
    missing_val = sequence[missing_idx]
    
    display_seq = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_seq.append("( ? )")
        else:
            display_seq.append(str(val))
            
    ascii_art = " -- ".join(display_seq)
    
    question_text = f"請觀察下列數線上的刻度變化，填入括號中的數字：\n{ascii_art}"
    correct_answer = str(missing_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    # [教學示範] 回傳結果中也可以包含 LaTeX
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}