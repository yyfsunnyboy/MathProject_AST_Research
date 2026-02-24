
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
        b = random.randint(-20, 20)
        c = random.randint(-20, 20)
        d = random.randint(-20, 20)
        e = random.randint(-20, 20)
        f = random.randint(-20, 20)
        g = random.randint(-20, 20)
        h = random.randint(-20, 20)
        i = random.randint(-20, 20)
        j = random.randint(-20, 20)
        k = random.randint(-20, 20)
        l = random.randint(-20, 20)
        m = random.randint(-20, 20)
        n = random.randint(-20, 20)
        o = random.randint(-20, 20)
        p = random.randint(-20, 20)
        q = random.randint(-20, 20)
        r = random.randint(-20, 20)
        s = random.randint(-20, 20)
        t = random.randint(-20, 20)
        u = random.randint(-20, 20)
        v = random.randint(-20, 20)
        w = random.randint(-20, 20)
        x = random.randint(-20, 20)
        y = random.randint(-20, 20)
        z = random.randint(-20, 20)
        question_text = IntegerOps.format_latex(f'({IntegerOps.fmt_num(a)} \\times {IntegerOps.fmt_num(b)} + {IntegerOps.fmt_num(c)}) \\div {IntegerOps.fmt_num(d)} \\times {IntegerOps.fmt_num(e)} - {IntegerOps.fmt_num(f)} \\times {IntegerOps.fmt_num(g)} + {IntegerOps.fmt_num(h)} \\times {IntegerOps.fmt_num(i)} - {IntegerOps.fmt_num(j)} \\times {IntegerOps.fmt_num(k)} + {IntegerOps.fmt_num(l)} \\times {IntegerOps.fmt_num(m)} - {IntegerOps.fmt_num(n)} \\times {IntegerOps.fmt_num(o)} + {IntegerOps.fmt_num(p)} \\times {IntegerOps.fmt_num(q)} - {IntegerOps.fmt_num(r)} \\times {IntegerOps.fmt_num(s)} + {IntegerOps.fmt_num(t)} \\times {IntegerOps.fmt_num(u)} - {IntegerOps.fmt_num(v)} \\times {IntegerOps.fmt_num(w)} + {IntegerOps.fmt_num(x)} \\times {IntegerOps.fmt_num(y)} - {IntegerOps.fmt_num(z)}')
        answer = IntegerOps.safe_eval(question_text.replace('\\times', '*').replace('\\div', '/').replace('\\times', '*').replace('\\div', '/'))
        correct_answer = IntegerOps.format_plain(answer)
    return {'question_text': question_text, 'answer': '', 'correct_answer': correct_answer, 'mode': 1}

def check(user_answer, correct_answer):
    try:
        if str(user_answer).strip() == str(correct_answer).strip():
            return {'correct': True, 'result': '正確'}
        if abs(float(user_answer) - float(correct_answer)) < 1e-06:
            return {'correct': True, 'result': '正確'}
    except:
        pass
    return {'correct': False, 'result': '錯誤'}