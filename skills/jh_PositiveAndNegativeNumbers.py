import random
from fractions import Fraction

def generate(level=1):
    """
    生成「正數與負數」相關題目。
    包含：
    1. 日常生活中利用正負號表示相對的量 (直接根據方向表示)
    2. 日常生活中利用正負號表示相對的量 (需計算差異後表示)
    3. 實際情境中判斷賺賠、升降等並記錄
    """
    problem_type = random.choice(['relative_direct', 'relative_calculate', 'real_world_scenario'])
    
    if problem_type == 'relative_direct':
        return generate_relative_direct_problem()
    elif problem_type == 'relative_calculate':
        return generate_relative_calculate_problem()
    else: # real_world_scenario
        return generate_real_world_scenario_problem()

def generate_relative_direct_problem():
    """
    生成直接表示相對量的問題，如：東邊為正，西邊為負，問西邊某距離如何表示。
    """
    scenarios = [
        {
            "reference": "學校的位置",
            "pos_dir": "東邊", "neg_dir": "西邊",
            "pos_verb": "位在", "neg_verb": "位在",
            "unit": "公里",
            "example_obj": "超市", "target_obj": "醫院"
        },
        {
            "reference": "基準點",
            "pos_dir": "上方", "neg_dir": "下方",
            "pos_verb": "距離", "neg_verb": "距離",
            "unit": "公尺",
            "example_obj": "山頂", "target_obj": "谷底"
        },
        {
            "reference": "出發點",
            "pos_dir": "向右", "neg_dir": "向左",
            "pos_verb": "移動", "neg_verb": "移動",
            "unit": "步",
            "example_obj": "小明", "target_obj": "小華"
        }
    ]
    
    scenario = random.choice(scenarios)
    
    pos_val = random.randint(3, 15)
    neg_val = random.randint(3, 15)
    
    question_text = (
        f"以{scenario['reference']}為基準，{scenario['reference']}的{scenario['pos_dir']}當作正向，"
        f"{scenario['reference']}的{scenario['neg_dir']}為負向。<br>"
        f"若{scenario['example_obj']}{scenario['pos_verb']}{scenario['reference']}的{scenario['pos_dir']} ${pos_val}$ {scenario['unit']}處，記為「$+{pos_val}$」{scenario['unit']}，<br>"
        f"則{scenario['target_obj']}{scenario['neg_verb']}{scenario['reference']}的{scenario['neg_dir']} ${neg_val}$ {scenario['unit']}處，應該怎麼記錄？"
    )
    correct_answer = f"$-{neg_val}$ {scenario['unit']}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_relative_calculate_problem():
    """
    生成需要計算差異後再表示相對量的問題，如：分數進步/退步。
    """
    scenarios = [
        {
            "context_ref": "第一次小考分數",
            "base_val_name": "分數",
            "pos_desc": "進步", "neg_desc": "退步",
            "unit": "分",
            "person1": "小妍", "person2": "小翊",
            "example_val_diff_range": (3, 10), # for example person's progress
            "target_val_diff_range": (2, 8),  # for target person's decline
            "base_val_range": (60, 80) # base score for both
        },
        {
            "context_ref": "基準體重",
            "base_val_name": "體重",
            "pos_desc": "增加", "neg_desc": "減少",
            "unit": "公斤",
            "person1": "爸爸", "person2": "媽媽",
            "example_val_diff_range": (1, 4), # weight increase
            "target_val_diff_range": (1, 5), # weight decrease
            "base_val_range": (50, 80)
        }
    ]
    
    scenario = random.choice(scenarios)
    
    base_val = random.randint(*scenario['base_val_range'])
    
    # Example person (positive change)
    pos_diff = random.randint(*scenario['example_val_diff_range'])
    person1_final_val = base_val + pos_diff
    
    # Target person (negative change)
    neg_diff = random.randint(*scenario['target_val_diff_range'])
    person2_final_val = base_val - neg_diff
    
    question_text = (
        f"{scenario['person1']}和{scenario['person2']}的{scenario['context_ref']}都是 ${base_val}$ {scenario['unit']}。<br>"
        f"以{scenario['context_ref']}為基準，{scenario['pos_desc']}為正向，{scenario['neg_desc']}為負向。<br>"
        f"若{scenario['person1']}第二次測量結果是 ${person1_final_val}$ {scenario['unit']}，{scenario['pos_desc']}了 ${pos_diff}$ {scenario['unit']}，記為「$+{pos_diff}$」{scenario['unit']}，<br>"
        f"則{scenario['person2']}第二次測量結果是 ${person2_final_val}$ {scenario['unit']}，應該怎麼記錄？"
    )
    
    # Correct answer calculation
    correct_diff = base_val - person2_final_val 
    correct_answer = f"$-{correct_diff}$ {scenario['unit']}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_real_world_scenario_problem():
    """
    生成實際情境問題，如：賺賠、溫度升降，需要判斷情況並用正負號記錄。
    此函數將只生成一個子問題，類似例題中的 (1) 或 (2)。
    """
    problem_choice = random.choice([1, 2]) # Choose between type (1) or type (2) from reference example
    
    if problem_choice == 1: # Type (1): Direct profit/loss or rise/fall
        scenarios = [
            {
                "context": "花店老闆每賣出一盆花，就會記錄這筆交易的賺賠情形",
                "pos_term": "賺錢", "neg_term": "賠錢",
                "unit": "元",
                "example_pos_val": random.randint(100, 500),
                "question_scenario_type": "neg", # Asking for negative case
                "target_val": random.randint(50, 300), # Amount lost/decreased
                "record_verb": "記錄"
            },
            {
                "context": "某城市每天的氣溫變化",
                "pos_term": "上升", "neg_term": "下降",
                "unit": "℃",
                "example_pos_val": random.randint(1, 5),
                "question_scenario_type": "neg",
                "target_val": random.randint(2, 7),
                "record_verb": "表示"
            },
            {
                "context": "科學家記錄潛水艇相對於海平面的深度",
                "pos_term": "上升", "neg_term": "下降",
                "unit": "公尺",
                "example_pos_val": random.randint(10, 50),
                "question_scenario_type": "neg",
                "target_val": random.randint(20, 100),
                "record_verb": "表示"
            }
        ]
        
        scenario = random.choice(scenarios)
        
        question_text = (
            f"{scenario['context']}，他以「$+$」表示{scenario['pos_term']}，以「$-$」表示{scenario['neg_term']}，"
            f"例如：{scenario['pos_term']}了 ${scenario['example_pos_val']}$ {scenario['unit']}，就記為 $+{scenario['example_pos_val']}$ {scenario['unit']}。<br>"
            f"試回答下列問題：<br>"
            f"若{scenario['neg_term']}了 ${scenario['target_val']}$ {scenario['unit']}，應該怎麼{scenario['record_verb']}？"
        )
        correct_answer = f"$-{scenario['target_val']}$ {scenario['unit']}"
        
    else: # Type (2): Calculate difference, then record (e.g., cost vs. selling price)
        scenarios = [
            {
                "context": "花店老闆每賣出一盆花，就會記錄這筆交易的賺賠情形",
                "pos_term": "賺錢", "neg_term": "賠錢",
                "unit": "元",
                "example_pos_val": random.randint(100, 500),
                "item_name": "一盆花",
                "initial_val_range": (300, 800), # cost or initial amount
                "change_range_profit": (50, 200), # selling price difference for profit
                "change_range_loss": (50, 200), # selling price difference for loss
                "record_verb": "記錄"
            },
            {
                "context": "運動員每次訓練都會記錄當天的體重變化",
                "pos_term": "增加", "neg_term": "減少",
                "unit": "公斤",
                "example_pos_val": random.randint(1, 3),
                "item_name": "運動員的體重",
                "initial_val_range": (50, 90), # initial weight
                "change_range_profit": (1, 4), # increase
                "change_range_loss": (1, 5), # decrease
                "record_verb": "表示"
            }
        ]
        
        scenario = random.choice(scenarios)
        
        initial_val = random.randint(*scenario['initial_val_range'])
        
        # Decide if it's a profit/increase or loss/decrease for the target question
        is_positive_change = random.random() < 0.5
        
        if is_positive_change: 
            change_val_abs = random.randint(scenario['change_range_profit'][0], scenario['change_range_profit'][1])
            final_val = initial_val + change_val_abs
            calculated_sign = "+"
            calculated_term = scenario['pos_term']
        else: 
            change_val_abs = random.randint(scenario['change_range_loss'][0], scenario['change_range_loss'][1])
            # Ensure final value is not negative for weight scenarios
            if scenario['unit'] == "公斤" and initial_val - change_val_abs <= 0:
                # If it would be negative, flip to a small increase instead
                is_positive_change = True
                change_val_abs = random.randint(1, min(initial_val - 1, scenario['change_range_profit'][1])) # ensure change is positive and not too large
                final_val = initial_val + change_val_abs
                calculated_sign = "+"
                calculated_term = scenario['pos_term']
            else:
                final_val = initial_val - change_val_abs
                calculated_sign = "-"
                calculated_term = scenario['neg_term']
        
        # Adjust for decimal if needed, e.g., for weight (more common to have decimals)
        if scenario['unit'] == "公斤" and random.random() < 0.5:
            decimal_part = random.choice([0.1, 0.2, 0.5, 0.8])
            initial_val = round(initial_val + decimal_part if random.random() < 0.5 else initial_val - decimal_part, 1)
            # Recalculate final_val with decimals
            change_val_abs = round(random.uniform(1.0, float(scenario['change_range_profit'][1] if is_positive_change else scenario['change_range_loss'][1])), 1)
            
            # Ensure final weight is positive
            if initial_val + change_val_abs <= 0:
                change_val_abs = round(random.uniform(0.1, initial_val - 0.1), 1) # Must decrease
                is_positive_change = False
                calculated_sign = "-"
                calculated_term = scenario['neg_term']
            elif initial_val - change_val_abs <= 0:
                 change_val_abs = round(random.uniform(0.1, initial_val - 0.1), 1) # Must decrease
                 is_positive_change = False
                 calculated_sign = "-"
                 calculated_term = scenario['neg_term']

            final_val = round(initial_val + change_val_abs if is_positive_change else initial_val - change_val_abs, 1)
            change_val_abs = abs(round(final_val - initial_val, 1))
            

        question_text = (
            f"{scenario['context']}，他以「$+$」表示{scenario['pos_term']}，以「$-$」表示{scenario['neg_term']}，"
            f"例如：{scenario['pos_term']}了 ${scenario['example_pos_val']}$ {scenario['unit']}，就記為 $+{scenario['example_pos_val']}$ {scenario['unit']}。<br>"
            f"試回答下列問題：<br>"
            f"若{scenario['item_name']}在初始為 ${initial_val}$ {scenario['unit']}的情況下，變為 ${final_val}$ {scenario['unit']}，"
            f"則應該怎麼{scenario['record_verb']}？"
        )
        
        actual_diff = abs(round(final_val - initial_val, 1)) # Recalculate actual diff in case of rounding
        correct_answer = f"${calculated_sign}{actual_diff}$ {scenario['unit']}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Clean and normalize user answer: remove spaces, '元', '公里', '分', etc., and convert to float/int
    # Also handle the '$' for LaTeX math mode
    def clean_answer(ans_str):
        ans_str = ans_str.strip().replace(" ", "").replace("公里", "").replace("公尺", "").replace("分", "").replace("元", "").replace("公斤", "").replace("℃", "")
        # Remove '$' signs if they are present for LaTeX
        ans_str = ans_str.replace("$", "")
        return ans_str
        
    user_answer_cleaned = clean_answer(user_answer)
    correct_answer_cleaned = clean_answer(correct_answer)
    
    is_correct = False
    
    # Try direct string comparison first
    if user_answer_cleaned.lower() == correct_answer_cleaned.lower():
        is_correct = True
    else:
        # Try numeric comparison if applicable
        try:
            user_num = float(user_answer_cleaned)
            correct_num = float(correct_answer_cleaned)
            # Use a small tolerance for float comparison
            if abs(user_num - correct_num) < 1e-9:
                is_correct = True
        except ValueError:
            pass # Not a number, so direct string comparison already failed.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}