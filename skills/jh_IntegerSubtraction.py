import random

def generate(level=1):
    """
    生成整數減法運算題目。
    包含：
    1. 正數減正數 (可能小數減大數)
    2. 正數減負數
    3. 負數減正數
    4. 負數減負數
    """
    
    # Determine the range for operands based on level
    if level == 1:
        range_min = -20
        range_max = 20
    elif level == 2:
        range_min = -100
        range_max = 100
    else: # Default for level 3+ or invalid levels
        range_min = -500
        range_max = 500

    num1 = random.randint(range_min, range_max)
    num2 = random.randint(range_min, range_max)

    # Ensure num2 is not 0, making the problem more interesting.
    # It's fine for num1 to be 0.
    while num2 == 0:
        num2 = random.randint(range_min, range_max)

    # Calculate the correct answer
    correct_result = num1 - num2

    # Format num1 for display: enclose in parentheses if negative
    if num1 < 0:
        num1_display_str = f"({num1})"
    else:
        num1_display_str = str(num1)

    # Format num2 for display: enclose in parentheses if negative
    if num2 < 0:
        num2_display_str = f"({num2})"
    else:
        num2_display_str = str(num2)

    # Construct the question text
    # Examples:
    #   14 - 23         -> $14 - 23$
    #   125 - (-25)     -> $125 - (-25)$
    #   (-63) - 37      -> $(-63) - 37$
    #   (-133) - (-13)  -> $(-133) - (-13)$
    question_text = f"計算下列各式的值：<br>${num1_display_str} - {num2_display_str}$"

    # The `answer` and `correct_answer` fields should be the final numerical result as a string.
    correct_answer_str = str(correct_result)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    try:
        user_num = int(user_answer.strip())
        correct_num = int(correct_answer.strip())
        is_correct = (user_num == correct_num)
    except ValueError:
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}