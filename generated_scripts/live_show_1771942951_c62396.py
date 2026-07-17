
# ==============================================================================
# [AUTO-INJECTED RESOURCE] IntegerOps
# ==============================================================================
class IntegerOps:
    """整數運算模組 - 支援格式化、絕對值等"""
    
    @staticmethod
    def fmt_num(n):
        """格式化數字，為負數自動加括號"""
        if n < 0:
            return f"({n})"
        return str(n)
    
    @staticmethod
    def random_nonzero(min_val, max_val):
        """生成非零隨機整數"""
        available = [x for x in range(min_val, max_val + 1) if x != 0]
        if not available:
            raise ValueError(f"No non-zero integers in range [{min_val}, {max_val}]")
        return random.choice(available)
    
    @staticmethod
    def is_divisible(a, b):
        """檢查 a 是否能被 b 整除"""
        if b == 0:
            return False
        return a % b == 0
    
    @staticmethod
    def safe_eval(expr):
        """安全評估算式，支援：abs()、基本四則運算、括號"""
        safe_dict = {
            '__builtins__': {},
            'abs': abs,
            'sum': sum,
            'max': max,
            'min': min,
        }
        expr = expr.replace('[', '(').replace(']', ')')
        expr = expr.replace('\\times', '*').replace('\\div', '/')
        expr = expr.replace('{', '').replace('}', '')
        expr = expr.replace(' ', '')
        try:
            return eval(expr, safe_dict)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expr}. Error: {e}")

    @staticmethod
    def format_latex(val):
        """格式化為 LaTeX 輸出，為了與 PolynomialOps/RadicalOps 介面一致"""
        return str(val)
        
    @staticmethod
    def format_plain(val):
        """格式化為純文字輸出，為了與 PolynomialOps/RadicalOps 介面一致"""
        return str(val)

def generate(level=1, **kwargs):
    question_text = ''
    if level == 1:
        a = random.randint(-20, 20)
        b = random.randint(-10, 10)
        if random.choice([True, False]):
            question_text = format_latex(f'{IntegerOps.fmt_num(a)} \\times {IntegerOps.fmt_num(b)}')
            correct_answer = a * b
        else:
            b = random.randint(-10, 10)
            a = b * random.randint(-10, 10)
            question_text = format_latex(f'{IntegerOps.fmt_num(a)} \\div {IntegerOps.fmt_num(b)}')
            correct_answer = a // b
    elif level == 2:
        b = random.randint(-15, 15)
        temp_ans = random.randint(-15, 15)
        a = b * temp_ans
        c = random.randint(-10, 10)
        if random.choice([True, False]):
            question_text = format_latex(f'{IntegerOps.fmt_num(a)} \\div {IntegerOps.fmt_num(b)} \\times {IntegerOps.fmt_num(c)}')
            correct_answer = a // b * c
        else:
            c2 = random.randint(-15, 15)
            temp_ans2 = random.randint(-10, 10)
            prod = c2 * temp_ans2
            a2 = random.randint(-10, 10)
            b2 = c2 * random.randint(-5, 5)
            question_text = format_latex(f'{IntegerOps.fmt_num(a2)} \\times {IntegerOps.fmt_num(b2)} \\div {IntegerOps.fmt_num(c2)}')
            correct_answer = a2 * (b2 // c2)
    elif random.choice([True, False]):
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        d = random.randint(-15, 15)
        q = random.randint(-10, 10)
        c = d * q
        question_text = format_latex(f'{IntegerOps.fmt_num(a)} \\times {IntegerOps.fmt_num(b)} + {IntegerOps.fmt_num(c)} \\div {IntegerOps.fmt_num(d)}')
        correct_answer = a * b + c // d
    else:
        a = random.randint(-20, 20)
        c = random.randint(-15, 15)
        q = random.randint(-10, 10)
        b = c * q
        d = random.randint(-10, 10)
        question_text = format_latex(f'{IntegerOps.fmt_num(a)} - {IntegerOps.fmt_num(b)} \\div {IntegerOps.fmt_num(c)} \\times {IntegerOps.fmt_num(d)}')
        correct_answer = a - b // c * d
    if random.choice([True, False]):
        question_text = format_shuffled_latex(question_text)
    return {'question_text': question_text, 'answer': '', 'correct_answer': format_plain(correct_answer), 'mode': 1}

def check(user_answer, correct_answer):
    try:
        if str(user_answer).strip() == str(correct_answer).strip():
            return {'correct': True, 'result': '正確'}
        if abs(float(user_answer) - float(correct_answer)) < 1e-06:
            return {'correct': True, 'result': '正確'}
    except:
        pass
    return {'correct': False, 'result': '錯誤'}