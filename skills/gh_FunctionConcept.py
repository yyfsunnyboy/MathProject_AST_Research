import random
import math # For sqrt, if used
import uuid # For unique filenames if graph output were needed, but it's text.
from fractions import Fraction # For displaying rational numbers

def generate(level=1):
    """
    生成「函數概念」相關題目。
    包含：
    1. 函數值計算 (線性、二次、絕對值、分段函數)
    2. 定義域判斷 (分式、根式)
    3. 函數定義判斷 (判斷給定關係是否為函數)
    4. 自變數/應變數識別 (情境題)
    """
    problem_types = ['function_evaluation', 'domain_range_concept', 'variable_identification']
    problem_type = random.choice(problem_types)

    if problem_type == 'function_evaluation':
        return generate_function_evaluation_problem(level)
    elif problem_type == 'domain_range_concept':
        return generate_domain_range_concept_problem(level)
    elif problem_type == 'variable_identification':
        return generate_variable_identification_problem(level)

def generate_function_evaluation_problem(level):
    func_type = random.choice(['linear', 'quadratic', 'absolute_value', 'piecewise'])
    
    if func_type == 'linear':
        a = random.randint(2, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])
        val = random.randint(-5, 5)

        func_expr = f"{a}x + {b}" if b >= 0 else f"{a}x - {-b}"
        if a == 1: func_expr = func_expr[1:]
        if a == -1: func_expr = "-x" + func_expr[2:]
        if func_expr.startswith("1x"): func_expr = func_expr[1:]
        if func_expr.startswith("-1x"): func_expr = "-x" + func_expr[3:]
        
        correct_answer_val = a * val + b
        question_text = f"已知函數 $f(x) = {func_expr}$，求 $f({val})$ 的值。"
        correct_answer = str(correct_answer_val)

    elif func_type == 'quadratic':
        a = random.randint(1, 3) * random.choice([-1, 1])
        b = random.randint(0, 5) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        val = random.randint(-3, 3)

        terms = []
        if a != 0:
            if a == 1: terms.append(r"x^{{2}}")
            elif a == -1: terms.append(r"-x^{{2}}")
            else: terms.append(f"{a}x^{{2}}")
        if b != 0:
            if b == 1: terms.append("x")
            elif b == -1: terms.append("-x")
            elif b > 0: terms.append(f"+{b}x")
            else: terms.append(f"{b}x")
        if c != 0:
            if c > 0: terms.append(f"+{c}")
            else: terms.append(f"{c}")
        
        func_expr = "".join(terms).lstrip('+')
        if not func_expr: func_expr = "0"
        
        correct_answer_val = a * (val**2) + b * val + c
        question_text = f"已知函數 $f(x) = {func_expr}$，求 $f({val})$ 的值。"
        correct_answer = str(correct_answer_val)
        
    elif func_type == 'absolute_value':
        a = random.randint(1, 3) * random.choice([-1, 1])
        b = random.randint(1, 5) * random.choice([-1, 1])
        val = random.randint(-5, 5)

        inside_abs = f"{a}x + {b}" if b >= 0 else f"{a}x - {-b}"
        if a == 1: inside_abs = inside_abs[1:]
        if a == -1: inside_abs = "-x" + inside_abs[2:]
        if inside_abs.startswith("1x"): inside_abs = inside_abs[1:]
        if inside_abs.startswith("-1x"): inside_abs = "-x" + inside_abs[3:]
        
        func_expr = f"|{inside_abs}|"
        
        correct_answer_val = abs(a * val + b)
        question_text = f"已知函數 $f(x) = {func_expr}$，求 $f({val})$ 的值。"
        correct_answer = str(correct_answer_val)

    elif func_type == 'piecewise':
        k = random.randint(-2, 2)
        val = random.randint(-5, 5)
        
        condition_type = random.choice(['le', 'gt'])
        if condition_type == 'le':
            if val > k: 
                k = val + random.randint(0, 3) 
        else: # condition_type == 'gt'
            if val <= k: 
                k = val - random.randint(1, 4) 

        if val == k:
            val += 1

        a1 = random.randint(1, 4) * random.choice([-1, 1])
        b1 = random.randint(1, 7) * random.choice([-1, 1])
        a2 = random.randint(1, 4) * random.choice([-1, 1])
        b2 = random.randint(1, 7) * random.choice([-1, 1])

        expr1_str = f"{a1}x + {b1}" if b1 >= 0 else f"{a1}x - {-b1}"
        expr2_str = f"{a2}x + {b2}" if b2 >= 0 else f"{a2}x - {-b2}"
        
        for expr_name in ['expr1_str', 'expr2_str']:
            expr_val = locals()[expr_name]
            if expr_val.startswith("1x"):
                expr_val = expr_val[1:]
            elif expr_val.startswith("-1x"):
                expr_val = "-x" + expr_val[3:]
            locals()[expr_name] = expr_val
        
        func_expr = r"\\begin{{cases}} " \
                    f"{expr1_str}, & \\text{{當 }} x \\le {k} \\\\ " \
                    f"{expr2_str}, & \\text{{當 }} x > {k} " \
                    r"\\end{{cases}}"

        if val <= k:
            correct_answer_val = a1 * val + b1
        else:
            correct_answer_val = a2 * val + b2
        
        question_text = f"已知函數 $f(x) = {func_expr}$，求 $f({val})$ 的值。"
        correct_answer = str(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_domain_range_concept_problem(level):
    sub_type = random.choice(['domain_fraction', 'domain_sqrt', 'function_definition'])
    
    if sub_type == 'domain_fraction':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])
        
        if a == 0: a = random.choice([1, -1])
        
        denominator_str = f"{a}x + {b}" if b >= 0 else f"{a}x - {-b}"
        if a == 1: denominator_str = denominator_str[1:]
        if a == -1: denominator_str = "-x" + denominator_str[2:]
        if denominator_str.startswith("1x"): denominator_str = denominator_str[1:]
        if denominator_str.startswith("-1x"): denominator_str = "-x" + denominator_str[3:]

        func_expr = r"\\frac{{1}}{{{denominator_str}}}"
        
        excluded_val = -b / a
        
        if excluded_val.is_integer():
            correct_answer = f"$x \\neq {int(excluded_val)}$"
        else:
            frac_val = Fraction(-b, a)
            if frac_val.denominator == 1:
                correct_answer = f"$x \\neq {frac_val.numerator}$"
            else:
                correct_answer = f"$x \\neq \\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}$"

        question_text = f"求函數 $f(x) = {func_expr}$ 的定義域。"
        
    elif sub_type == 'domain_sqrt':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])

        if a == 0: a = random.choice([1, -1])
        
        sqrt_expr_str = f"{a}x + {b}" if b >= 0 else f"{a}x - {-b}"
        if a == 1: sqrt_expr_str = sqrt_expr_str[1:]
        if a == -1: sqrt_expr_str = "-x" + sqrt_expr_str[2:]
        if sqrt_expr_str.startswith("1x"): sqrt_expr_str = sqrt_expr_str[1:]
        if sqrt_expr_str.startswith("-1x"): sqrt_expr_str = "-x" + sqrt_expr_str[3:]

        func_expr = r"\\sqrt{{{sqrt_expr_str}}}"
        
        threshold = -b / a
        
        if threshold.is_integer():
            threshold_str = str(int(threshold))
        else:
            frac_val = Fraction(-b, a)
            if frac_val.denominator == 1:
                threshold_str = str(frac_val.numerator)
            else:
                threshold_str = r"\\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}"

        if a > 0:
            correct_answer = f"$x \\ge {threshold_str}$"
        else:
            correct_answer = f"$x \\le {threshold_str}$"
            
        question_text = f"求函數 $f(x) = {func_expr}$ 的定義域。"

    elif sub_type == 'function_definition':
        options = []
        correct_option_idx = -1
        
        potential_options = [
            (r"y = 2x + 1", True),
            (r"y = x^{{2}}", True),
            (r"y = |x|", True),
            (r"x = y^{{2}}", False),
            (r"x^{{2}} + y^{{2}} = 9", False),
            (r"y^{{3}} = x", True)
        ]
        
        random.shuffle(potential_options)
        
        num_options = 3
        chosen_options = potential_options[:num_options]
        
        has_correct = any(opt[1] for opt in chosen_options)
        if not has_correct:
            func_options = [opt for opt in potential_options if opt[1]]
            chosen_options[0] = random.choice(func_options)
            
        random.shuffle(chosen_options)
        
        label_map = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        
        for i, (expr, is_func) in enumerate(chosen_options):
            options.append(f"({label_map[i]}) ${expr}$")
            if is_func:
                if correct_option_idx == -1:
                    correct_option_idx = i
            
        if correct_option_idx == -1:
            return generate_domain_range_concept_problem(level)
            
        question_text = "下列哪個關係式中，$y$ 是 $x$ 的函數？(請填寫選項代號)<br>" + "<br>".join(options)
        correct_answer = label_map[correct_option_idx]

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_variable_identification_problem(level):
    scenarios = [
        {"scenario": "某物品的售價與其生產成本。", "indep": "生產成本", "dep": "售價"},
        {"scenario": "計程車的車資與行駛距離。", "indep": "行駛距離", "dep": "車資"},
        {"scenario": "正方形的面積與其邊長。", "indep": "邊長", "dep": "面積"},
        {"scenario": "水被加熱時的溫度與加熱時間。", "indep": "加熱時間", "dep": "溫度"},
        {"scenario": "銀行存款的利息與存款金額。", "indep": "存款金額", "dep": "利息"},
        {"scenario": "學生考試的成績與其學習時間。", "indep": "學習時間", "dep": "成績"},
    ]
    
    chosen_scenario = random.choice(scenarios)
    
    question_type = random.choice(['indep', 'dep'])
    
    if question_type == 'indep':
        question_text = f"在「{chosen_scenario['scenario']}」中，哪個是自變數？"
        correct_answer = chosen_scenario['indep']
    else:
        question_text = f"在「{chosen_scenario['scenario']}」中，哪個是應變數？"
        correct_answer = chosen_scenario['dep']
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = str(user_answer).strip().replace(' ', '').lower()
    correct_answer = str(correct_answer).strip().replace(' ', '').lower()

    is_correct = False

    try:
        if float(user_answer) == float(correct_answer):
            is_correct = True
    except ValueError:
        pass

    if not is_correct:
        # For string answers (like variable names, inequalities, option letters)
        is_correct = (user_answer == correct_answer)
        
        # More robust check for inequalities and domain descriptions
        if not is_correct and ('x' in user_answer or 'x' in correct_answer):
            # Normalize LaTeX symbols for comparison
            user_normalized = user_answer.replace(r"\\neq", "!=").replace(r"\\le", "<=").replace(r"\\ge", ">=")
            correct_normalized = correct_answer.replace(r"\\neq", "!=").replace(r"\\le", "<=").replace(r"\\ge", ">=")

            # Attempt to parse and compare parts for inequalities
            try:
                # Example: x!=3 vs x!=3.0, x>=1/2 vs x>=0.5
                if 'x' in user_normalized and 'x' in correct_normalized:
                    # Simple split by operator
                    for op in ['!=', '>=', '<=', '>', '<', '=']:
                        if op in user_normalized and op in correct_normalized:
                            user_parts = user_normalized.split(op)
                            correct_parts = correct_normalized.split(op)
                            if len(user_parts) == 2 and len(correct_parts) == 2:
                                val1_user = user_parts[1].replace(r"\\frac{{","").replace("}}{{"," / ").replace("}}","").strip()
                                val1_correct = correct_parts[1].replace(r"\\frac{{","").replace("}}{{"," / ").replace("}}","").strip()
                                
                                # Try evaluating fractions and floats
                                try:
                                    if '/' in val1_user: val1_user_float = float(eval(val1_user))
                                    else: val1_user_float = float(val1_user)
                                    if '/' in val1_correct: val1_correct_float = float(eval(val1_correct))
                                    else: val1_correct_float = float(val1_correct)
                                    
                                    if user_parts[0].strip() == correct_parts[0].strip() and \
                                       op == correct_parts[0].strip() and \
                                       abs(val1_user_float - val1_correct_float) < 1e-9: # Compare floats with tolerance
                                        is_correct = True
                                        break
                                except (ValueError, NameError, SyntaxError):
                                    pass # Not a number or fraction, continue to string compare
                                
            except Exception:
                pass # General error during parsing, fall back to simple string comparison

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}