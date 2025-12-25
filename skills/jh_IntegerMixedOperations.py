import random
from fractions import Fraction

def safe_eval(expression_string):
    """Safely evaluates a mathematical expression string for integers and basic ops and abs()."""
    # Restrict the global and local namespaces for safety
    # Only 'abs' function is allowed besides basic arithmetic operations.
    allowed_builtins = {"abs": abs}
    try:
        # Using eval with restricted namespaces to prevent arbitrary code execution
        return eval(expression_string, {"__builtins__": None}, allowed_builtins)
    except Exception as e:
        # In a production environment, this error should be logged.
        # For problem generation, it indicates an issue in the generated expression.
        print(f"Error evaluating expression '{expression_string}': {e}")
        return None

def generate_basic_mixed_operations():
    """
    生成基本整數加減混合運算題目。
    例如: (-60) - (-42) + 18
    """
    num_count = random.choice([3, 4]) # 3 or 4 numbers
    # Ensure numbers are not always positive to test negative arithmetic
    numbers = [random.randint(-100, 100) for _ in range(num_count)]
    operators = [random.choice(['+', '-']) for _ in range(num_count - 1)]

    problem_parts_latex = [] # For display in LaTeX, e.g., (-5)
    problem_parts_eval = []  # For eval() function, e.g., (-5) or -5

    # Handle the first number
    problem_parts_latex.append(f"({numbers[0]})" if numbers[0] < 0 else str(numbers[0]))
    problem_parts_eval.append(str(numbers[0]))

    for i in range(num_count - 1):
        op = operators[i]
        num = numbers[i+1]
        problem_parts_latex.append(op)
        problem_parts_eval.append(op)

        # Wrap negative numbers in parentheses for clarity in display and robustness in eval
        if num < 0:
            problem_parts_latex.append(f"({num})")
            problem_parts_eval.append(f"({num})")
        else:
            problem_parts_latex.append(str(num))
            problem_parts_eval.append(str(num))

    question_text = f"計算下列各式的值。<br>${' '.join(problem_parts_latex)}$"
    
    eval_string = ' '.join(problem_parts_eval)
    correct_answer = str(safe_eval(eval_string))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_absolute_value_operations():
    """
    生成包含絕對值的整數運算題目。
    例如: |-25| - |-75| - 18 或 30 + |(-64) + 14| - 25
    """
    # Structure options:
    # 1. |N1| op N2 op |N3| 
    # 2. N1 op |N2 op N3| op N4
    
    choice = random.choice([1, 2])
    
    problem_parts_latex = []
    problem_parts_eval = []
    
    if choice == 1: # |N1| op N2 op |N3|
        n1 = random.randint(-50, 50)
        op1 = random.choice(['+', '-'])
        n2 = random.randint(-50, 50)
        op2 = random.choice(['+', '-'])
        n3 = random.randint(-50, 50)
        
        problem_parts_latex.append(f"|{n1}|")
        problem_parts_eval.append(f"abs({n1})")

        problem_parts_latex.append(op1)
        problem_parts_eval.append(op1)

        problem_parts_latex.append(f"({n2})" if n2 < 0 else str(n2))
        problem_parts_eval.append(str(n2))

        problem_parts_latex.append(op2)
        problem_parts_eval.append(op2)

        problem_parts_latex.append(f"|{n3}|")
        problem_parts_eval.append(f"abs({n3})")

    else: # N1 op |N2 op N3| op N4
        n1 = random.randint(-50, 50)
        op1 = random.choice(['+', '-'])
        n2 = random.randint(-50, 50)
        op_internal = random.choice(['+', '-'])
        n3 = random.randint(-50, 50)
        op2 = random.choice(['+', '-'])
        n4 = random.randint(-50, 50)

        problem_parts_latex.append(f"({n1})" if n1 < 0 else str(n1))
        problem_parts_eval.append(str(n1))
        
        problem_parts_latex.append(op1)
        problem_parts_eval.append(op1)

        # Build internal expression for absolute value
        internal_expr_latex = []
        internal_expr_eval = []
        internal_expr_latex.append(f"({n2})" if n2 < 0 else str(n2))
        internal_expr_eval.append(str(n2))
        internal_expr_latex.append(op_internal)
        internal_expr_eval.append(op_internal)
        internal_expr_latex.append(f"({n3})" if n3 < 0 else str(n3))
        internal_expr_eval.append(str(n3))
        
        joined_internal_latex = ' '.join(internal_expr_latex)
        joined_internal_eval = ' '.join(internal_expr_eval)
        
        problem_parts_latex.append(f"|{joined_internal_latex}|")
        problem_parts_eval.append(f"abs({joined_internal_eval})")

        problem_parts_latex.append(op2)
        problem_parts_eval.append(op2)

        problem_parts_latex.append(f"({n4})" if n4 < 0 else str(n4))
        problem_parts_eval.append(str(n4))

    question_text = f"計算下列各式的值。<br>${' '.join(problem_parts_latex)}$"
    eval_string = ' '.join(problem_parts_eval)
    correct_answer = str(safe_eval(eval_string))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parentheses_operations():
    """
    生成包含括號的整數運算題目，練習去括號規則。
    例如: -(6+3) - 5 或 (-4) - (-7+2) + 1
    """
    # Structure options:
    # 1. -(A op B) op C (emphasizes leading negative before parenthesis)
    # 2. X + (A op B) + Y (emphasizes positive before parenthesis)
    # 3. X - (A op B) + Y (emphasizes negative before parenthesis)
    
    choice = random.choice([1, 2, 3])
    
    problem_parts_latex = []
    problem_parts_eval = []
    
    if choice == 1: # -(A op B) op C
        # A, B are usually positive here to clearly show -(A+B) = -A-B or -(A-B) = -A+B
        a = random.randint(1, 20) 
        b = random.randint(1, 20)
        op_internal = random.choice(['+', '-'])
        c = random.randint(-50, 50)
        op_outside = random.choice(['+', '-'])
        
        internal_expr_latex = [str(a), op_internal, str(b)]
        internal_expr_eval = [str(a), op_internal, str(b)]
        
        joined_internal_latex = ' '.join(internal_expr_latex)
        joined_internal_eval = ' '.join(internal_expr_eval)
        
        problem_parts_latex.append(f"- ( {joined_internal_latex} )")
        problem_parts_eval.append(f"-({joined_internal_eval})")

        problem_parts_latex.append(op_outside)
        problem_parts_eval.append(op_outside)
        
        problem_parts_latex.append(f"({c})" if c < 0 else str(c))
        problem_parts_eval.append(str(c))
        
    elif choice == 2: # X + (A op B) + Y
        x = random.randint(-50, 50)
        op1 = '+' # Force + before parenthesis to show it can be removed directly
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        op_internal = random.choice(['+', '-'])
        op2 = random.choice(['+', '-'])
        y = random.randint(-50, 50)

        problem_parts_latex.append(f"({x})" if x < 0 else str(x))
        problem_parts_eval.append(str(x))
        
        problem_parts_latex.append(op1)
        problem_parts_eval.append(op1)

        internal_expr_latex = []
        internal_expr_eval = []
        internal_expr_latex.append(f"({a})" if a < 0 else str(a))
        internal_expr_eval.append(str(a))
        internal_expr_latex.append(op_internal)
        internal_expr_eval.append(op_internal)
        internal_expr_latex.append(f"({b})" if b < 0 else str(b))
        internal_expr_eval.append(str(b))

        joined_internal_latex = ' '.join(internal_expr_latex)
        joined_internal_eval = ' '.join(internal_expr_eval)

        problem_parts_latex.append(f"( {joined_internal_latex} )")
        problem_parts_eval.append(f"({joined_internal_eval})")

        problem_parts_latex.append(op2)
        problem_parts_eval.append(op2)

        problem_parts_latex.append(f"({y})" if y < 0 else str(y))
        problem_parts_eval.append(str(y))
        
    else: # X - (A op B) + Y
        x = random.randint(-50, 50)
        op1 = '-' # Force - before parenthesis
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        op_internal = random.choice(['+', '-'])
        op2 = random.choice(['+', '-'])
        y = random.randint(-50, 50)

        problem_parts_latex.append(f"({x})" if x < 0 else str(x))
        problem_parts_eval.append(str(x))
        
        problem_parts_latex.append(op1)
        problem_parts_eval.append(op1)

        internal_expr_latex = []
        internal_expr_eval = []
        internal_expr_latex.append(f"({a})" if a < 0 else str(a))
        internal_expr_eval.append(str(a))
        internal_expr_latex.append(op_internal)
        internal_expr_eval.append(op_internal)
        internal_expr_latex.append(f"({b})" if b < 0 else str(b))
        internal_expr_eval.append(str(b))

        joined_internal_latex = ' '.join(internal_expr_latex)
        joined_internal_eval = ' '.join(internal_expr_eval)

        problem_parts_latex.append(f"( {joined_internal_latex} )")
        problem_parts_eval.append(f"({joined_internal_eval})")

        problem_parts_latex.append(op2)
        problem_parts_eval.append(op2)

        problem_parts_latex.append(f"({y})" if y < 0 else str(y))
        problem_parts_eval.append(str(y))
        
    question_text = f"計算下列各式的值。<br>${' '.join(problem_parts_latex)}$"
    eval_string = ' '.join(problem_parts_eval)
    correct_answer = str(safe_eval(eval_string))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「整數加減混合運算」相關題目。
    根據難度選擇不同類型的問題。
    """
    problem_type = random.choice([
        'basic_mixed_operations', 
        'absolute_value_operations', 
        'parentheses_operations'
    ])
    
    if problem_type == 'basic_mixed_operations':
        return generate_basic_mixed_operations()
    elif problem_type == 'absolute_value_operations':
        return generate_absolute_value_operations()
    else: # 'parentheses_operations'
        return generate_parentheses_operations()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    接受使用者答案和正確答案，進行比較。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False

    try:
        if int(user_answer) == int(correct_answer):
            is_correct = True
    except ValueError:
        pass 

    # Fallback to float comparison for robustness (e.g., user enters '5.0' for '5')
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # User input is not a valid number at all

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}