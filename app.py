# ==============================================================================
# 1. Imports
# ==============================================================================
import random
import os
import base64
import io
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import google.generativeai as genai
from PIL import Image
import time
import re
import math
from google.api_core.exceptions import ResourceExhausted

# ==============================================================================
# 2. App Initialization and Configuration
# ==============================================================================
app = Flask(__name__)
app.secret_key = 'your_api_key'  # ★ 請務必更換成您自己的密鑰 ★
#app.secret_key = 'your_api_key' # ★ 備用的密鑰 ★


# --- Database Configuration ---
# 取得 instance 資料夾的絕對路徑
instance_path = app.instance_path
print(f"資料庫將會被儲存在: {instance_path}") # 加上這行方便您確認

# 確保 instance 資料夾存在
try:
    os.makedirs(instance_path)
except OSError:
    pass # 資料夾已存在

# 明確指定資料庫的完整路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'kumon_math.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# --- Gemini API Configuration ---
try:
    genai.configure(api_key="AIzaSyCCvlrh5-3Y_Ck15cZDJ-R0C3yYN9WTBpw")
    model = genai.GenerativeModel('models/gemini-pro-latest')
except Exception as e:
    print(f"Gemini API 尚未設定或金鑰錯誤: {e}")
    model = None

# ==============================================================================
# 3. Database Models
# ==============================================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    progress = db.relationship('UserProgress', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    main_unit = db.Column(db.String(100), nullable=True) # <-- 新增這行
    # vvvv 確保您已經加上這兩行 vvvv
    school_type = db.Column(db.String(20), nullable=True, default='共同')
    grade_level = db.Column(db.String(20), nullable=True, default='國中')
    generator_key = db.Column(db.String(100), nullable=True, index=True)
    # ^^^^ 確保您已經加上這兩行 ^^^^

    # ... (Skill 模型裡的其他欄位) ...

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    consecutive_correct = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    total_attempted = db.Column(db.Integer, default=0)
    consecutive_incorrect = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc'),)

class SkillDependency(db.Model):
    """ 用來儲存技能依賴關係 (知識圖譜) 的模型 """
    id = db.Column(db.Integer, primary_key=True)

    # '先備知識' 的 ID
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    # '目標技能' 的 ID
    target_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)

    # 建立關係，讓我們可以方便地查詢
    prerequisite = db.relationship('Skill', foreign_keys=[prerequisite_id], backref='leading_to')
    target = db.relationship('Skill', foreign_keys=[target_id], backref='requires')

    # 確保同一個依賴關係不會重複
    db.UniqueConstraint('prerequisite_id', 'target_id', name='unique_dependency')

    def __repr__(self):
        return f'<Dependency: {self.prerequisite.display_name} -> {self.target.display_name}>'

# ^^^^ 程式碼加到這裡為止 ^^^^

# ==============================================================================
# 4. Helper Functions (Formatting, Checking)
# ==============================================================================

# --- Validation Functions (Referenced by name) ---
def validate_remainder(user_answer, correct_answer):
    # 簡單的字串比較
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def validate_factor(user_answer, correct_answer):
    # 判斷 '是' 或 '否'
    return str(user_answer).strip() == str(correct_answer)

def validate_linear_equation(user_answer, correct_answer):
    # 判斷 x=... 或 y=...
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def validate_check_point(user_answer, correct_answer):
    # 判斷 '是' 或 '否'
    return str(user_answer).strip() == str(correct_answer)

def validate_multiple_choice(user_answer, correct_answer):
    """Validates multiple choice questions by comparing the selected option (e.g., 'A') with the correct answer."""
    return str(user_answer).strip().upper() == str(correct_answer).strip().upper()

# --- Formatting Functions ---
def format_polynomial(coeffs):
    """將係數列表轉換成漂亮的多項式字串"""
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        if coeff == 0:
            continue
        term = ""
        if coeff > 0:
            if i > 0:
                term += " + "
        else:
            term += " - "
        abs_coeff = abs(coeff)
        if abs_coeff != 1 or power == 0:
            term += str(abs_coeff)
        if power == 1:
            term += "x"
        elif power > 1:
            term += f"x^{power}"
        terms.append(term)
    if not terms:
        return "0"
    return "".join(terms)

def format_linear_equation_lhs(a, b):
    """將係數 (a, b) 轉換成 "ax + by" 的漂亮字串"""
    terms = []
    if a == 1:
        terms.append("x")
    elif a == -1:
        terms.append("-x")
    elif a != 0:
        terms.append(f"{a}x")
    if b > 0:
        if a != 0:
            terms.append(" + ")
        if b == 1:
            terms.append("y")
        else:
            terms.append(f"{b}y")
    elif b < 0:
        if a != 0:
            terms.append(" - ")
        else:
            terms.append("-")
        if b == -1:
            terms.append("y")
        else:
            terms.append(f"{abs(b)}y")
    if not terms:
        return "0"
    return "".join(terms)

def check_inequality(a, b, c, sign, x, y):
    """檢查點 (x, y) 是否滿足 ax + by [sign] c"""
    lhs = (a * x) + (b * y)
    if sign == '>':
        return lhs > c
    if sign == '>=':
        return lhs >= c
    if sign == '<':
        return lhs < c
    if sign == '<=':
        return lhs <= c
    return False

def format_inequality(a, b, c, sign):
    """將係數 (a, b, c) 和符號轉換成 "ax + by [sign] c" 的字串"""
    lhs_str = format_linear_equation_lhs(a, b)
    return f"{lhs_str} {sign} {c}"

# ==============================================================================
# 5. Question Generators
# ==============================================================================
def generate_remainder_theorem_question():
    """動態生成一道「餘式定理」的題目 (二次式或三次式)"""
    degree = random.choice([2, 3])
    k = random.randint(-3, 3)
    coeffs = []
    correct_answer = 0
    if degree == 2:
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        c = random.randint(-9, 9)
        coeffs = [a, b, c]
        correct_answer = (a * (k**2)) + (b * k) + c
    elif degree == 3:
        a = random.randint(-2, 2)
        while a == 0:
            a = random.randint(-2, 2)
        b = random.randint(-3, 3)
        c = random.randint(-5, 5)
        d = random.randint(-9, 9)
        coeffs = [a, b, c, d]
        correct_answer = (a * (k**3)) + (b * (k**2)) + (c * k) + d
    poly_text = format_polynomial(coeffs)
    k_sign = "-" if k >= 0 else "+"
    k_abs = abs(k)
    divisor_text = "(x)" if k == 0 else f"(x {k_sign} {k_abs})"
    question_text = f"求 f(x) = {poly_text} 除以 {divisor_text} 的餘式。"
    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": validate_remainder.__name__
    }

def generate_factor_theorem_question():
    """動態生成一道「因式定理」的題目 (是/否)"""
    degree = random.choice([2, 3])
    k = random.randint(-3, 3)
    coeffs = []
    is_factor = random.choice([True, False])
    if degree == 2:
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        if is_factor:
            c = -((a * (k**2)) + (b * k))
        else:
            c = random.randint(-9, 9)
            remainder = (a * (k**2)) + (b * k) + c
            while remainder == 0:
                c = random.randint(-9, 9)
                remainder = (a * (k**2)) + (b * k) + c
        coeffs = [a, b, c]
    elif degree == 3:
        a = random.randint(-2, 2)
        while a == 0:
            a = random.randint(-2, 2)
        b = random.randint(-3, 3)
        c = random.randint(-5, 5)
        if is_factor:
            d = -((a * (k**3)) + (b * (k**2)) + (c * k))
        else:
            d = random.randint(-9, 9)
            remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
            while remainder == 0:
                d = random.randint(-9, 9)
                remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
        coeffs = [a, b, c, d]
    poly_text = format_polynomial(coeffs)
    k_sign = "-" if k >= 0 else "+"
    k_abs = abs(k)
    divisor_text = "(x)" if k == 0 else f"(x {k_sign} {k_abs})"
    question_text = f"請問 {divisor_text} 是否為 f(x) = {poly_text} 的因式？ (請回答 '是' 或 '否')"
    correct_answer = "是" if is_factor else "否"
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": validate_factor.__name__
    }

def generate_substitution_question():
    """動態生成一道「帶入消去法」的題目 (確保唯一解)。"""
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    while x_sol == 0 or y_sol == 0:
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)
    if random.choice([True, False]):  # 產生 y = mx + k
        m = random.randint(-3, 3)
        while m == 0:
            m = random.randint(-3, 3)
        k = y_sol - (m * x_sol)
        eq1_lhs = "y"
        eq1_rhs = f"{m}x"
        if k > 0:
            eq1_rhs += f" + {k}"
        elif k < 0:
            eq1_rhs += f" - {abs(k)}"
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 or b == 0 or a == -m * b:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        c = (a * x_sol) + (b * y_sol)
        eq2_lhs = format_linear_equation_lhs(a, b)
        eq2_rhs = str(c)
    else:  # 產生 x = my + k
        m = random.randint(-3, 3)
        while m == 0:
            m = random.randint(-3, 3)
        k = x_sol - (m * y_sol)
        eq1_lhs = "x"
        eq1_rhs = f"{m}y"
        if k > 0:
            eq1_rhs += f" + {k}"
        elif k < 0:
            eq1_rhs += f" - {abs(k)}"
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 or b == 0 or b == -m * a:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        c = (a * x_sol) + (b * y_sol)
        eq2_lhs = format_linear_equation_lhs(a, b)
        eq2_rhs = str(c)
    ask_for = random.choice(["x", "y"])
    answer = str(x_sol) if ask_for == "x" else str(y_sol)
    question_text = (f"請用帶入消去法解下列聯立方程式：\n"
                    f"  {eq1_lhs:<15} = {eq1_rhs:<10} ...... (1)\n"
                    f"  {eq2_lhs:<15} = {eq2_rhs:<10} ...... (2)\n\n"
                    f"請問 {ask_for} = ?")
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": validate_linear_equation.__name__
    }

def generate_addition_subtraction_question():
    """動態生成一道「加減消去法」的題目 (加入倍數變化)。"""
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    while x_sol == 0 or y_sol == 0:
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)
    a1 = random.randint(-5, 5)
    b1 = random.randint(-5, 5)
    while a1 == 0 or b1 == 0:
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
    multiplier = random.choice([-3, -2, 2, 3])
    b2 = b1 * multiplier
    a2 = random.randint(-5, 5)
    while a2 == 0 or a2 == a1 * multiplier:
        a2 = random.randint(-5, 5)
    c1 = (a1 * x_sol) + (b1 * y_sol)
    c2 = (a2 * x_sol) + (b2 * y_sol)
    eq1_lhs = format_linear_equation_lhs(a1, b1)
    eq2_lhs = format_linear_equation_lhs(a2, b2)
    ask_for = random.choice(["x", "y"])
    answer = str(x_sol) if ask_for == "x" else str(y_sol)
    question_text = (f"請用加減消去法解下列聯立方程式：\n"
                    f"  {eq1_lhs:<15} = {c1:<10} ...... (1)\n"
                    f"  {eq2_lhs:<15} = {c2:<10} ...... (2)\n\n"
                    f"請問 {ask_for} = ?")
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": validate_linear_equation.__name__
    }

def generate_check_point_in_system_question():
    """動態生成一道「判斷點是否為不等式系統解」的題目。"""
    num_inequalities = random.choice([2, 3])
    inequalities = []
    inequality_strs = []
    for _ in range(num_inequalities):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while a == 0 and b == 0:
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
        temp_x = random.randint(-3, 3)
        temp_y = random.randint(-3, 3)
        c = (a * temp_x) + (b * temp_y)
        sign = random.choice(['>', '>=', '<', '<='])
        inequalities.append({'a': a, 'b': b, 'c': c, 'sign': sign})
        inequality_strs.append(format_inequality(a, b, c, sign))
    test_x = random.randint(-5, 5)
    test_y = random.randint(-5, 5)
    is_solution = True
    for ieq in inequalities:
        if not check_inequality(ieq['a'], ieq['b'], ieq['c'], ieq['sign'], test_x, test_y):
            is_solution = False
            break
    correct_answer = "是" if is_solution else "否"
    system_str = "\n".join([f"  {s}" for s in inequality_strs])
    question_text = f"請問點 ({test_x}, {test_y}) 是否為下列不等式系統的解？ (請回答 '是' 或 '否')\n{system_str}"
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": validate_check_point.__name__
    }

def generate_common_logarithm_question():
    power = random.randint(1, 3)
    base = 10
    number = base ** power
    question_text = f"計算 log({number}) = ?"
    return {
        "text": question_text,
        "answer": str(power),
        "validation_function_name": None
    }

def generate_linear_equation_question():
    # Generate two points (x1, y1) and (x2, y2)
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    while x1 == x2: # Ensure distinct x-coordinates for a non-vertical line
        x2 = random.randint(-5, 5)

    # Calculate slope (m) and y-intercept (b)
    m_num = y2 - y1
    m_den = x2 - x1

    # Simplify the slope if possible
    from math import gcd
    common_divisor = gcd(m_num, m_den)
    m_num //= common_divisor
    m_den //= common_divisor

    # Equation: y - y1 = m(x - x1)
    # y = (m_num/m_den) * x - (m_num/m_den) * x1 + y1
    # To avoid fractions in the answer, we'll ask for the slope and y-intercept
    
    question_text = f"已知兩點 ({x1}, {y1}) 和 ({x2}, {y2})，求通過這兩點的直線斜率。"
    
    # Answer is the simplified slope
    if m_den == 1:
        answer = str(m_num)
    else:
        answer = f"{m_num}/{m_den}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_circle_equation_question():
    center_x = random.randint(-3, 3)
    center_y = random.randint(-3, 3)
    radius = random.randint(2, 5)
    
    # Equation: (x - h)^2 + (y - k)^2 = r^2
    # Ask for the equation given center and radius
    question_text = f"已知圓心為 ({center_x}, {center_y})，半徑為 {radius}，求此圓的方程式。"
    
    # Answer format: (x-h)^2+(y-k)^2=r^2
    h_str = f"x - {abs(center_x)}" if center_x > 0 else f"x + {abs(center_x)}" if center_x < 0 else "x"
    k_str = f"y - {abs(center_y)}" if center_y > 0 else f"y + {abs(center_y)}" if center_y < 0 else "y"
    
    if center_x == 0 and center_y == 0:
        answer = f"x^2+y^2={radius**2}"
    elif center_x == 0:
        answer = f"x^2+({k_str})^2={radius**2}"
    elif center_y == 0:
        answer = f"({h_str})^2+y^2={radius**2}"
    else:
        answer = f"({h_str})^2+({k_str})^2={radius**2}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_circle_line_question():
    # Simple question: determine if a point is on a circle
    center_x = random.randint(-3, 3)
    center_y = random.randint(-3, 3)
    radius = random.randint(2, 4)
    
    # Generate a point (px, py)
    px = random.randint(center_x - radius - 1, center_x + radius + 1)
    py = random.randint(center_y - radius - 1, center_y + radius + 1)
    
    # Check if the point is on the circle
    distance_sq = (px - center_x)**2 + (py - center_y)**2
    is_on_circle = (distance_sq == radius**2)
    
    question_text = f"已知圓方程式為 (x - {center_x})^2 + (y - {center_y})^2 = {radius**2}，請問點 ({px}, {py}) 是否在此圓上？ (請回答 '是' 或 '否')"
    correct_answer = "是" if is_on_circle else "否"

    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": None # Simple string comparison
    }

def generate_polynomial_division_question():
    # Generate a simple quadratic polynomial and a linear divisor
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    divisor_root = random.randint(-3, 3) # x - divisor_root
    
    # Polynomial: ax^2 + bx + c
    # Divisor: x - divisor_root
    
    # Using synthetic division or direct calculation
    # (ax^2 + bx + c) / (x - r) = (ax + (b+ar)) with remainder (c+r(b+ar))
    
    quotient_coeff_x = a
    quotient_constant = b + a * divisor_root
    remainder = c + divisor_root * (b + a * divisor_root)
    
    poly_text = f"{a}x^2 + {b}x + {c}" if b >= 0 and c >= 0 else f"{a}x^2 {b}x {c}" if b < 0 and c < 0 else f"{a}x^2 {b}x + {c}" if b < 0 else f"{a}x^2 + {b}x {c}"
    divisor_text = f"x - {abs(divisor_root)}" if divisor_root > 0 else f"x + {abs(divisor_root)}"
    
    question_text = f"求多項式 {poly_text} 除以 {divisor_text} 的餘式。"
    
    return {
        "text": question_text,
        "answer": str(remainder),
        "validation_function_name": None
    }

def generate_quadratic_function_question():
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)

    # Find vertex (-b/2a)
    vertex_x_num = -b
    vertex_x_den = 2 * a
    
    # Simplify fraction
    from math import gcd
    common_divisor = gcd(vertex_x_num, vertex_x_den)
    vertex_x_num //= common_divisor
    vertex_x_den //= common_divisor

    question_text = f"已知二次函數 f(x) = {a}x^2 + {b}x + {c}，求其頂點的 x 座標。"
    
    if vertex_x_den == 1:
        answer = str(vertex_x_num)
    else:
        answer = f"{vertex_x_num}/{vertex_x_den}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_cubic_function_question():
    a = random.randint(1, 2)
    b = random.randint(-3, 3)
    c = random.randint(-5, 5)
    d = random.randint(-9, 9)
    x_val = random.randint(-2, 2)

    # Function: f(x) = ax^3 + bx^2 + cx + d
    correct_answer = a * (x_val**3) + b * (x_val**2) + c * x_val + d

    question_text = f"已知三次函數 f(x) = {a}x^3 + {b}x^2 + {c}x + {d}，求 f({x_val}) 的值。"

    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }

def generate_polynomial_inequality_question():
    # Simple linear inequality for now
    a = random.randint(-5, 5)
    while a == 0:
        a = random.randint(-5, 5)
    b = random.randint(-10, 10)
    
    sign = random.choice(['>', '<', '>=', '<='])

    question_text = f"解不等式 {a}x {sign} {b}。"
    
    # Solve for x
    if a > 0:
        if sign == '>': answer_sign = '>'
        elif sign == '<': answer_sign = '<'
        elif sign == '>=': answer_sign = '>='
        else: answer_sign = '<='
        answer_val = b / a
    else: # a < 0, reverse inequality sign
        if sign == '>': answer_sign = '<'
        elif sign == '<': answer_sign = '>'
        elif sign == '>=': answer_sign = '<='
        else: answer_sign = '>='
        answer_val = b / a
    
    # Format answer to one decimal place if not integer
    if answer_val == int(answer_val):
        answer = f"x {answer_sign} {int(answer_val)}"
    else:
        answer = f"x {answer_sign} {answer_val:.1f}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_sequence_question():
    # Arithmetic sequence
    a1 = random.randint(1, 10) # First term
    d = random.randint(-3, 3) # Common difference
    while d == 0: d = random.randint(-3, 3)
    n = random.randint(4, 7) # Term to find

    # Generate first few terms
    terms = [a1 + (i * d) for i in range(n-1)]
    terms_str = ", ".join(map(str, terms))

    correct_answer = a1 + (n-1) * d

    question_text = f"已知一個等差數列的前 {n-1} 項為 {terms_str}，求第 {n} 項。"

    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }

def generate_series_question():
    # Sum of arithmetic series
    a1 = random.randint(1, 10) # First term
    d = random.randint(-3, 3) # Common difference
    while d == 0: d = random.randint(-3, 3)
    n = random.randint(3, 6) # Number of terms

    # Sum = n/2 * (2*a1 + (n-1)*d)
    correct_answer = (n / 2) * (2 * a1 + (n - 1) * d)

    question_text = f"已知一個等差數列的首項為 {a1}，公差為 {d}，求前 {n} 項的和。"

    return {
        "text": question_text,
        "answer": str(int(correct_answer)), # Ensure integer answer
        "validation_function_name": None
    }

def generate_exponential_question():
    base = random.randint(2, 5)
    exponent = random.randint(2, 4)
    correct_answer = base ** exponent
    question_text = f"計算 {base}^{exponent} = ?"
    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }

def generate_inequality_region_question():
    """動態生成一道「圖示不等式解區域」的題目。"""
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 and b == 0:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    while c == 0:
        c = random.randint(-9, 9)
    sign = random.choice(['>', '<', '>=', '<='])
    inequality_lhs = format_linear_equation_lhs(a, b)
    c_str = ""
    if c > 0:
        c_str = f" + {c}"
    elif c < 0:
        c_str = f" - {abs(c)}"
    inequality_expression = f"{inequality_lhs}{c_str}"
    full_inequality_string = f"{inequality_expression} {sign} 0"
    question_text = (
        f"請在下方的「數位計算紙」上，圖示二元一次不等式：\n\n"
        f"    {full_inequality_string}\n\n"
        f"畫完後，請點擊「AI 檢查計算」按鈕。"
    )
    return {
        "text": question_text,
        "answer": None,
        "validation_function_name": None,
        "inequality_string": full_inequality_string
    }

def generate_counting_principles_question():
    """動態生成一道「計數原理」的題目 (乘法原理)"""
    items1_count = random.randint(2, 5)
    items1_name = random.choice(["種上衣", "種帽子", "種麵包"])
    items2_count = random.randint(2, 5)
    items2_name = random.choice(["種褲子", "種圍巾", "種飲料"])
    answer = items1_count * items2_count
    question_text = f"小明有 {items1_count} {items1_name}和 {items2_count} {items2_name}，請問他總共可以搭配出幾種不同的組合？"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }

def generate_permutations_question():
    """動態生成一道「排列」的題目 (P(n,k))"""
    n = random.randint(4, 7)
    k = random.randint(2, n - 1)
    answer = math.perm(n, k)
    question_text = f"從 {n} 個相異物中取出 {k} 個進行排列，請問有幾種排法？ (即 P({n}, {k}))"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }

def generate_combinations_question():
    """動態生成一道「組合」的題目 (C(n,k))"""
    n = random.randint(5, 9)
    k = random.randint(2, n - 2)
    answer = math.comb(n, k)
    question_text = f"從 {n} 個相異物中取出 {k} 個，請問有幾種取法？ (即 C({n}, {k}))"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }

def generate_classical_probability_question():
    """動態生成一道「古典機率」的題目"""
    total_outcomes = 6
    event_type = random.choice(['even', 'odd', 'greater_than'])
    if event_type == 'even':
        fav_outcomes = 3 # 2, 4, 6
        question_text = "擲一顆公正的骰子，出現偶數點的機率是多少？（請以 a/b 的形式表示）"
        answer = "3/6"
    elif event_type == 'odd':
        fav_outcomes = 3 # 1, 3, 5
        question_text = "擲一顆公正的骰子，出現奇數點的機率是多少？（請以 a/b 的形式表示）"
        answer = "3/6"
    else: # greater_than
        num = random.randint(1, 4)
        fav_outcomes = 6 - num
        question_text = f"擲一顆公正的骰子，出現比 {num} 大的點數的機率是多少？（請以 a/b 的形式表示）"
        answer = f"{fav_outcomes}/6"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_expected_value_question():
    """動態生成一道「數學期望值」的題目"""
    outcomes = [1, 2, 3, 4, 5, 6]
    probabilities = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6]
    expected_value = sum(o * p for o, p in zip(outcomes, probabilities))
    question_text = "擲一顆公正的骰子，其出現點數的數學期望值是多少？"
    answer = str(expected_value)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_data_analysis_1d_question():
    """動態生成一道「一維數據分析」的題目 (平均數、中位數或眾數)"""
    data = sorted([random.randint(1, 20) for _ in range(random.choice([5, 7]))])
    stat_type = random.choice(['mean', 'median', 'mode'])
    if stat_type == 'mean':
        mean = sum(data) / len(data)
        answer = f"{mean:.1f}" if mean != int(mean) else str(int(mean))
        question_text = f"給定一組數據：{data}，請問這組數據的算術平均數是多少？"
    elif stat_type == 'median':
        median = data[len(data) // 2]
        answer = str(median)
        question_text = f"給定一組數據：{data}，請問這組數據的中位數是多少？"
    else: # mode
        mode_val = random.choice(data)
        data.insert(random.randint(0, len(data)), mode_val)
        data.sort()
        answer = str(mode_val)
        question_text = f"給定一組數據：{data}，請問這組數據的眾數是多少？"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_data_analysis_2d_question():
    """動態生成一道「二維數據分析」的題目 (求中心點)"""
    data_points = []
    x_sum = 0
    y_sum = 0
    n = 5
    for _ in range(n):
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        data_points.append(f"({x}, {y})")
        x_sum += x
        y_sum += y
    mean_x = x_sum / n
    mean_y = y_sum / n
    mean_x_str = f"{mean_x:.1f}" if mean_x != int(mean_x) else str(int(mean_x))
    mean_y_str = f"{mean_y:.1f}" if mean_y != int(mean_y) else str(int(mean_y))
    points_str = ", ".join(data_points)
    question_text = f"給定 {n} 組二維數據 (X, Y): {points_str}，請問此數據的中心點 (X的平均數, Y的平均數) 是什麼？(請以 (x,y) 的格式回答，無須空格)"
    answer = f"({mean_x_str},{mean_y_str})"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_ratios_right_triangle_question():
    """動態生成一道「直角三角形的三角比」的題目"""
    if random.choice([True, False]):
        a, b, c = 3, 4, 5
    else:
        a, b, c = 5, 12, 13
    leg1, leg2 = random.sample([a, b], 2)
    hypotenuse = c
    angle_choice = random.choice(['A', 'B'])
    trig_func = random.choice(['sin', 'cos', 'tan'])
    if angle_choice == 'A':
        angle_desc = f"對邊為 {leg1} 的那個銳角"
        if trig_func == 'sin':
            answer = f"{leg1}/{hypotenuse}"
        elif trig_func == 'cos':
            answer = f"{leg2}/{hypotenuse}"
        else:
            answer = f"{leg1}/{leg2}"
    else:
        angle_desc = f"對邊為 {leg2} 的那個銳角"
        if trig_func == 'sin':
            answer = f"{leg2}/{hypotenuse}"
        elif trig_func == 'cos':
            answer = f"{leg1}/{hypotenuse}"
        else:
            answer = f"{leg2}/{leg1}"
    question_text = f"在一個直角三角形中，兩股長分別為 {leg1} 和 {leg2}。請問 {angle_desc} 的 {trig_func} 值是多少？(請以 a/b 的形式表示)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_ratios_general_angle_question():
    """動態生成一道「廣義角三角比」的題目 (有理數答案)"""
    options = [
        (150, 'sin', '1/2'), (210, 'sin', '-1/2'), (330, 'sin', '-1/2'),
        (120, 'cos', '-1/2'), (240, 'cos', '-1/2'),
        (135, 'tan', '-1'), (225, 'tan', '1'), (315, 'tan', '-1')
    ]
    angle_deg, trig_func, answer = random.choice(options)
    question_text = f"請問 {trig_func}({angle_deg}°) 的值是多少？(請以數字或 a/b 的形式表示)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_properties_laws_question():
    """動態生成一道「三角比的性質」的題目 (餘弦定理)"""
    a, b, angle_C, c = random.choice([(8, 3, 60, 7), (8, 5, 60, 7)])
    question_text = f"在三角形 ABC 中，若邊 a = {a}，邊 b = {b}，且兩邊的夾角 C = {angle_C}°，請問對邊 c 的長度是多少？"
    answer = str(c)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_radian_measure_question():
    """動態生成一道「弧度量」的題目 (角度與弧度互換)"""
    deg_to_rad = {
        30: "pi/6", 60: "pi/3", 90: "pi/2", 120: "2*pi/3",
        180: "pi", 270: "3*pi/2", 360: "2*pi"
    }
    deg = random.choice(list(deg_to_rad.keys()))
    answer = deg_to_rad[deg]
    question_text = f"請問 {deg}° 等於多少弧度 (radian)？ (請用 pi 表示，例如: pi/2)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_graphs_periodicity_question():
    """動態生成一道「三角函數的圖形/週期性」的題目"""
    func = random.choice(['sin', 'cos'])
    b = random.choice([1, 2, 4])
    func_str = f"{func}({b}x)" if b != 1 else f"{func}(x)"
    if b == 1:
        answer = "2*pi"
    elif b == 2:
        answer = "pi"
    elif b == 4:
        answer = "pi/2"
    question_text = f"請問函數 f(x) = {func_str} 的最小正週期是多少？(答案請用 pi 表示，例如: 2*pi)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_sum_difference_question():
    """動態生成一道「三角的和差角公式」的題目 (概念)"""
    formulas = {
        "sin(A+B)": "sin(A)cos(B)+cos(A)sin(B)",
        "sin(A-B)": "sin(A)cos(B)-cos(A)sin(B)",
        "cos(A+B)": "cos(A)cos(B)-sin(A)sin(B)",
        "cos(A-B)": "cos(A)cos(B)+sin(A)sin(B)"
    }
    func = random.choice(list(formulas.keys()))
    answer = formulas[func]
    question_text = f"請問 {func} 的展開式是什麼？(請用 sin(A), cos(B) 等方式作答)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_polar_coordinates_question():
    """動態生成一道「極坐標」的題目 (極座標轉直角座標)"""
    r = random.randint(2, 10)
    angle_deg = random.choice([0, 90, 180, 270])
    
    cos_val = 0
    sin_val = 0
    if angle_deg == 0:
        cos_val = 1
    elif angle_deg == 90:
        sin_val = 1
    elif angle_deg == 180:
        cos_val = -1
    elif angle_deg == 270:
        sin_val = -1

    x = r * cos_val
    y = r * sin_val

    if random.choice([True, False]):
         question_text = f"將極坐標點 [{r}, {angle_deg}°] 轉換為直角坐標 (x, y)，請問 x 坐標是多少？"
         answer = str(int(x))
    else:
         question_text = f"將極坐標點 [{r}, {angle_deg}°] 轉換為直角坐標 (x, y)，請問 y 坐標是多少？"
         answer = str(int(y))

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_trig_sine_cosine_combination_question():
    """動態生成一道「正餘弦的疊合」的題目 (求最大/最小值)"""
    a, b, r = random.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17)])
    a, b = random.sample([a, b], 2)
    max_or_min = random.choice(['max', 'min'])
    if max_or_min == 'max':
        question_text = f"請問函數 f(x) = {a}*sin(x) + {b}*cos(x) 的最大值是多少？"
        answer = str(r)
    else:
        question_text = f"請問函數 f(x) = {a}*sin(x) + {b}*cos(x) 的最小值是多少？"
        answer = str(-r)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_real_number_system_question():
    """動態生成一道「數」的題目 (有理數/無理數)"""
    rational_examples = ["5", "-3", "1/2", "0.75"]
    irrational_examples = [("pi", "無理數"), ("sqrt(2)", "無理數")]
    if random.choice([True, False]):
        num_str = random.choice(rational_examples)
        answer = "有理數"
    else:
        num_str, answer = random.choice(irrational_examples)
    question_text = f"請問 {num_str} 是有理數還是無理數？"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_absolute_value_question():
    """動態生成一道「絕對值」的題目 (基本運算)"""
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = abs(a) + abs(b)
    else:
        answer = abs(a) - abs(b)
    question_text = f"計算 |{a}| {op} |{b}| = ?"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }

def generate_exponential_functions_question():
    """動態生成一道「指數函數」的題目 (解方程式)"""
    base = random.randint(2, 5)
    exponent = random.randint(2, 4)
    result = base ** exponent
    question_text = f"解指數方程式 {base}^x = {result}，請問 x = ?"
    answer = str(exponent)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_logarithmic_properties_question():
    """
    Generates a fill-in-the-blank question about the properties of logarithms.
    Covers conceptual links to exponents, basic operations, and algebraic application.
    """
    questions = [
        {
            'question': '指數律 a^m * a^n = a^(m+n) 啟發了對數的運算性質 log_a(XY) = ? (答案請勿包含空格)',
            'answer': 'log_a(X)+log_a(Y)'
        },
        {
            'question': '請計算 log_2(4) + log_2(8) 的值。',
            'answer': '5'
        },
        {
            'question': '3 * log_10(5) + log_10(8) 的值是多少？',
            'answer': '3'
        },
        {
            'question': '已知 log_a(x) = 5 且 log_a(y) = 2，請問 log_a(x^2 / y) 的值是多少？',
            'answer': '8'
        }
    ]
    
    q = random.choice(questions)
    
    # Return format for fill-in-the-blank
    return {
        "text": q['question'],
        "answer": q['answer'],
        "validation_function_name": None # Use default string comparison
    }

def generate_logarithmic_functions_question():
    """動態生成一道「對數函數」的題目 (解方程式)"""
    base = random.choice([2, 3, 5])
    result_exp = random.randint(2, 4)
    x = base ** result_exp
    question_text = f"解對數方程式 log{base}(x) = {result_exp}，請問 x = ?"
    answer = str(x)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_vectors_2d_question():
    """動態生成一道「平面向量」的題目 (分量或長度)"""
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    vec_x = x2 - x1
    vec_y = y2 - y1
    if random.choice([True, False]):
        question_text = f"已知點 A({x1}, {y1}) 和點 B({x2}, {y2})，請問向量 AB 的 x 分量是多少？"
        answer = str(vec_x)
    else:
        question_text = f"已知點 A({x1}, {y1}) 和點 B({x2}, {y2})，請問向量 AB 的 y 分量是多少？"
        answer = str(vec_y)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_vectors_2d_operations_question():
    """動態生成一道「平面向量的運算」的題目 (加減法)"""
    ux, uy = random.randint(-5, 5), random.randint(-5, 5)
    vx, vy = random.randint(-5, 5), random.randint(-5, 5)
    op = random.choice(['+', '-'])
    if op == '+':
        res_x = ux + vx
        res_y = uy + vy
    else:
        res_x = ux - vx
        res_y = uy - vy
    if random.choice([True, False]):
        question_text = f"已知向量 u = ({ux}, {uy}) 和向量 v = ({vx}, {vy})，請問向量 u {op} v 的 x 分量是多少？"
        answer = str(res_x)
    else:
        question_text = f"已知向量 u = ({ux}, {uy}) 和向量 v = ({vx}, {vy})，請問向量 u {op} v 的 y 分量是多少？"
        answer = str(res_y)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_space_concepts_question():
    """動態生成一道「空間概念」的題目 (點到平面距離)"""
    x, y, z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    plane_choice = random.choice(['xy', 'yz', 'xz'])
    if plane_choice == 'xy':
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 xy 平面的距離是多少？"
        answer = str(abs(z))
    elif plane_choice == 'yz':
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 yz 平面的距離是多少？"
        answer = str(abs(x))
    else: # xz
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 xz 平面的距離是多少？"
        answer = str(abs(y))
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_vectors_3d_coordinates_question():
    """動態生成一道「空間向量的坐標表示法」的題目 (向量分量)"""
    x1, y1, z1 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    x2, y2, z2 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    
    vec_x = x2 - x1
    vec_y = y2 - y1
    vec_z = z2 - z1
    
    component_choice = random.choice(['x', 'y', 'z'])
    
    if component_choice == 'x':
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 x 分量是多少？"
        answer = str(vec_x)
    elif component_choice == 'y':
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 y 分量是多少？"
        answer = str(vec_y)
    else: # 'z'
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 z 分量是多少？"
        answer = str(vec_z)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_determinant_3x3_question():
    """動態生成一道「三階行列式」的題目"""
    matrix = []
    for _ in range(3):
        matrix.append([random.randint(-3, 3) for _ in range(3)])
    
    # Calculate determinant for a 3x3 matrix
    # | a b c |
    # | d e f |
    # | g h i |
    # det = a(ei - fh) - b(di - fg) + c(dh - eg)
    
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    
    determinant = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    
    matrix_str = "\n".join([f"| {row[0]:>2} {row[1]:>2} {row[2]:>2} |" for row in matrix])
    
    question_text = f"計算下列三階行列式的值：\n{matrix_str}"
    
    return {
        "text": question_text,
        "answer": str(determinant),
        "validation_function_name": None
    }

def generate_planes_in_space_question():
    """動態生成一道「空間中的平面」的題目 (求法向量)"""
    a, b, c = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    d = random.randint(-10, 10)
    
    # Ensure at least one coefficient is non-zero
    while a == 0 and b == 0 and c == 0:
        a, b, c = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
        
    equation_parts = []
    if a != 0:
        equation_parts.append(f"{a}x")
    if b != 0:
        if b > 0 and equation_parts:
            equation_parts.append(f" + {b}y")
        elif b < 0 and equation_parts:
            equation_parts.append(f" - {abs(b)}y")
        else:
            equation_parts.append(f"{b}y")
    if c != 0:
        if c > 0 and equation_parts:
            equation_parts.append(f" + {c}z")
        elif c < 0 and equation_parts:
            equation_parts.append(f" - {abs(c)}z")
        else:
            equation_parts.append(f"{c}z")
            
    equation_str = "".join(equation_parts)
    if not equation_str: # Should not happen if a,b,c are not all zero
        equation_str = "0"
        
    question_text = f"已知平面方程式為 {equation_str} = {d}，請問此平面的法向量為何？ (請以 (a,b,c) 的格式回答，無須空格)"
    answer = f"({a},{b},{c})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_vectors_3d_operations_question():
    """動態生成一道「空間向量的運算」的題目 (加減法)"""
    u_x, u_y, u_z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    v_x, v_y, v_z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    op = random.choice(['+', '-'])
    
    if op == '+':
        res_x = u_x + v_x
        res_y = u_y + v_y
        res_z = u_z + v_z
    else: # op == '-'
        res_x = u_x - v_x
        res_y = u_y - v_y
        res_z = u_z - v_z
        
    component_choice = random.choice(['x', 'y', 'z'])
    
    if component_choice == 'x':
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 x 分量是多少？"
        answer = str(res_x)
    elif component_choice == 'y':
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 y 分量是多少？"
        answer = str(res_y)
    else: # 'z'
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 z 分量是多少？"
        answer = str(res_z)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_lines_in_space_question():
    """動態生成一道「空間中的直線」的題目 (求方向向量)"""
    # 點 (x0, y0, z0) 和方向向量 (a, b, c)
    x0, y0, z0 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    a, b, c = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
    
    # 確保方向向量不是零向量
    while a == 0 and b == 0 and c == 0:
        a, b, c = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
        
    # 參數式: x = x0 + at, y = y0 + bt, z = z0 + ct
    question_text = f"已知空間中一條直線的參數式為 x = {x0}{'+' if a >= 0 else ''}{a}t, y = {y0}{'+' if b >= 0 else ''}{b}t, z = {z0}{'+' if c >= 0 else ''}{c}t，請問此直線的一個方向向量為何？ (請以 (a,b,c) 的格式回答，無須空格)"
    answer = f"({a},{b},{c})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_function_properties_question():
    """動態生成一道「函數性質的判定」的題目 (判斷奇偶函數)"""
    # 偶函數: f(x) = f(-x) (只有偶次項)
    # 奇函數: f(x) = -f(-x) (只有奇次項)
    # 兩者皆非: 混合奇偶次項
    
    func_type = random.choice(['even', 'odd', 'neither'])
    coeffs = [0, 0, 0, 0] # x^3, x^2, x^1, x^0
    
    if func_type == 'even':
        coeffs[1] = random.randint(1, 5) # x^2
        coeffs[3] = random.randint(1, 5) # constant
        question_text = f"請問函數 f(x) = {coeffs[1]}x^2 + {coeffs[3]} 是奇函數、偶函數還是兩者皆非？"
        answer = "偶函數"
    elif func_type == 'odd':
        coeffs[0] = random.randint(1, 5) # x^3
        coeffs[2] = random.randint(1, 5) # x^1
        question_text = f"請問函數 f(x) = {coeffs[0]}x^3 + {coeffs[2]}x 是奇函數、偶函數還是兩者皆非？"
        answer = "奇函數"
    else: # neither
        coeffs[0] = random.randint(1, 5) # x^3
        coeffs[1] = random.randint(1, 5) # x^2
        coeffs[3] = random.randint(1, 5) # constant
        question_text = f"請問函數 f(x) = {coeffs[0]}x^3 + {coeffs[1]}x^2 + {coeffs[3]} 是奇函數、偶函數還是兩者皆非？"
        answer = "兩者皆非"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_matrix_applications_question():
    """動態生成一道「矩陣的應用」的題目 (矩陣乘法)"""
    # 生成兩個 2x2 矩陣
    matrix_a = [[random.randint(-3, 3) for _ in range(2)] for _ in range(2)]
    matrix_b = [[random.randint(-3, 3) for _ in range(2)] for _ in range(2)]
    
    # 計算乘積矩陣 C = A * B
    matrix_c = [[0, 0], [0, 0]]
    matrix_c[0][0] = matrix_a[0][0] * matrix_b[0][0] + matrix_a[0][1] * matrix_b[1][0]
    matrix_c[0][1] = matrix_a[0][0] * matrix_b[0][1] + matrix_a[0][1] * matrix_b[1][1]
    matrix_c[1][0] = matrix_a[1][0] * matrix_b[0][0] + matrix_a[1][1] * matrix_b[1][0]
    matrix_c[1][1] = matrix_a[1][0] * matrix_b[0][1] + matrix_a[1][1] * matrix_b[1][1]
    
    # 隨機選擇詢問的元素位置
    row_idx = random.choice([0, 1])
    col_idx = random.choice([0, 1])
    
    question_text = (
        f"已知矩陣 A = [[{matrix_a[0][0]}, {matrix_a[0][1]}], [{matrix_a[1][0]}, {matrix_a[1][1]}]] "
        f"和矩陣 B = [[{matrix_b[0][0]}, {matrix_b[0][1]}], [{matrix_b[1][0]}, {matrix_b[1][1]}]]. "
        f"請問矩陣 C = A * B 中，位於第 {row_idx + 1} 列第 {col_idx + 1} 行的元素是多少？"
    )
    answer = str(matrix_c[row_idx][col_idx])
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_simultaneous_equations_3var_question():
    """動態生成一道「三元一次聯立方程式」的題目 (簡化版)"""
    # 確保有整數解，且題目不會太複雜
    x_sol = random.randint(-3, 3)
    y_sol = random.randint(-3, 3)
    z_sol = random.randint(-3, 3)
    
    # 方程式 1: 簡單的 x + y + z = C1
    c1 = x_sol + y_sol + z_sol
    eq1_str = f"x + y + z = {c1}"
    
    # 方程式 2: 2x + y - z = C2
    c2 = 2 * x_sol + y_sol - z_sol
    eq2_str = f"2x + y - z = {c2}"
    
    # 方程式 3: x - 2y + 3z = C3
    c3 = x_sol - 2 * y_sol + 3 * z_sol
    eq3_str = f"x - 2y + 3z = {c3}"
    
    ask_for = random.choice(['x', 'y', 'z'])
    if ask_for == 'x':
        answer = str(x_sol)
    elif ask_for == 'y':
        answer = str(y_sol)
    else:
        answer = str(z_sol)
        
    question_text = (
        f"請解下列聯立方程式：\n"
        f"  {eq1_str} ...... (1)\n"
        f"  {eq2_str} ...... (2)\n"
        f"  {eq3_str} ...... (3)\n\n"
        f"請問 {ask_for} = ?"
    )
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_matrix_operations_question():
    """動態生成一道「矩陣的運算」的題目 (矩陣加法)"""
    # 生成兩個 2x2 矩陣
    matrix_a = [[random.randint(-5, 5) for _ in range(2)] for _ in range(2)]
    matrix_b = [[random.randint(-5, 5) for _ in range(2)] for _ in range(2)]
    
    # 計算和矩陣 C = A + B
    matrix_c = [[0, 0], [0, 0]]
    matrix_c[0][0] = matrix_a[0][0] + matrix_b[0][0]
    matrix_c[0][1] = matrix_a[0][1] + matrix_b[0][1]
    matrix_c[1][0] = matrix_a[1][0] + matrix_b[1][0]
    matrix_c[1][1] = matrix_a[1][1] + matrix_b[1][1]
    
    # 隨機選擇詢問的元素位置
    row_idx = random.choice([0, 1])
    col_idx = random.choice([0, 1])
    
    question_text = (
        f"已知矩陣 A = [[{matrix_a[0][0]}, {matrix_a[0][1]}], [{matrix_a[1][0]}, {matrix_a[1][1]}]] "
        f"和矩陣 B = [[{matrix_b[0][0]}, {matrix_b[0][1]}], [{matrix_b[1][0]}, {matrix_b[1][1]}]]. "
        f"請問矩陣 C = A + B 中，位於第 {row_idx + 1} 列第 {col_idx + 1} 行的元素是多少？"
    )
    answer = str(matrix_c[row_idx][col_idx])
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_ratio_in_plane_question():
    """動態生成一道「平面上的比例」的題目 (分點公式)"""
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    
    m = random.randint(1, 3)
    n = random.randint(1, 3)
    
    # 內部一點 P 將 AB 線段分成 m:n
    # Px = (n*x1 + m*x2) / (m+n)
    # Py = (n*y1 + m*y2) / (m+n)
    
    px_num = n * x1 + m * x2
    py_num = n * y1 + m * y2
    den = m + n
    
    # 確保答案是整數，或者至少是簡單分數
    if px_num % den != 0 or py_num % den != 0:
        # 重新生成，直到得到整數解
        return generate_ratio_in_plane_question()
        
    px = px_num // den
    py = py_num // den
    
    question_text = (
        f"已知平面上兩點 A({x1}, {y1}) 和 B({x2}, {y2})。"
        f"若點 P 在線段 AB 上，且 AP:PB = {m}:{n}，請問點 P 的坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    )
    answer = f"({px},{py})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_coordinate_systems_question():
    """動態生成一道「坐標系」的題目 (直角坐標轉極坐標)"""
    # 選擇一個容易轉換的點，例如在軸上或特殊角度
    choice = random.choice([1, 2, 3, 4])
    if choice == 1: # (r, 0)
        x = random.randint(1, 5)
        y = 0
        r = x
        theta_deg = 0
    elif choice == 2: # (0, r)
        x = 0
        y = random.randint(1, 5)
        r = y
        theta_deg = 90
    elif choice == 3: # (-r, 0)
        x = random.randint(-5, -1)
        y = 0
        r = abs(x)
        theta_deg = 180
    else: # (0, -r)
        x = 0
        y = random.randint(-5, -1)
        r = abs(y)
        theta_deg = 270
        
    question_text = f"將直角坐標點 ({x}, {y}) 轉換為極坐標 (r, θ)，請問 r 的值是多少？"
    answer = str(r)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_conic_sections_question():
    """動態生成一道「圓錐曲線」的題目 (判斷類型)"""
    # Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    # 判斷類型主要看 A, B, C
    # B^2 - 4AC
    # < 0: 橢圓或圓
    # = 0: 拋物線
    # > 0: 雙曲線
    
    conic_type = random.choice(['ellipse', 'parabola', 'hyperbola'])
    
    if conic_type == 'ellipse':
        # A, C 同號，B=0
        A = random.randint(1, 5)
        C = random.randint(1, 5)
        while A == C: # 避免是圓
            C = random.randint(1, 5)
        B = 0
        equation_str = f"{A}x^2 + {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "橢圓"
    elif conic_type == 'parabola':
        # A=0 或 C=0 (但不同時為0), B=0
        if random.choice([True, False]):
            A = random.randint(1, 5)
            C = 0
        else:
            A = 0
            C = random.randint(1, 5)
        B = 0
        if A == 0:
            equation_str = f"{C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        else:
            equation_str = f"{A}x^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "拋物線"
    else: # hyperbola
        # A, C 異號，B=0
        A = random.randint(1, 5)
        C = random.randint(-5, -1)
        B = 0
        equation_str = f"{A}x^2 {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "雙曲線"
        
    question_text = f"請問下列方程式代表哪一種圓錐曲線？\n{equation_str}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_parabola_question():
    """動態生成一道「拋物線」的題目 (求頂點)"""
    # 考慮兩種基本形式: y = a(x-h)^2 + k 或 x = a(y-k)^2 + h
    # 這裡我們生成 y = ax^2 + bx + c 形式，求頂點 (-b/2a, f(-b/2a))
    
    a = random.randint(-3, 3)
    while a == 0: # 確保是二次項
        a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    # 頂點 x 座標: -b / (2a)
    vertex_x_num = -b
    vertex_x_den = 2 * a
    
    # 簡化分數
    from math import gcd
    common_divisor = gcd(vertex_x_num, vertex_x_den)
    vertex_x_num //= common_divisor
    vertex_x_den //= common_divisor
    
    question_text = f"已知拋物線方程式為 y = {a}x^2 + {b}x + {c}，請問其頂點的 x 坐標是多少？"
    
    if vertex_x_den == 1:
        answer = str(vertex_x_num)
    else:
        answer = f"{vertex_x_num}/{vertex_x_den}"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_ellipse_question():
    """動態生成一道「橢圓」的題目 (求中心點)"""
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    a_sq = random.randint(4, 9) # a^2
    b_sq = random.randint(1, 3) # b^2
    
    # (x-h)^2/a^2 + (y-k)^2/b^2 = 1
    # 為了簡化，我們只問中心點
    
    question_text = f"已知橢圓方程式為 (x - {h})^2/{a_sq} + (y - {k})^2/{b_sq} = 1，請問此橢圓的中心點坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    answer = f"({h},{k})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_hyperbola_question():
    """動態生成一道「雙曲線」的題目 (求中心點)"""
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    a_sq = random.randint(4, 9) # a^2
    b_sq = random.randint(1, 3) # b^2
    
    # (x-h)^2/a^2 - (y-k)^2/b^2 = 1 或 (y-k)^2/b^2 - (x-h)^2/a^2 = 1
    # 為了簡化，我們只問中心點
    
    if random.choice([True, False]):
        equation_str = f"(x - {h})^2/{a_sq} - (y - {k})^2/{b_sq} = 1"
    else:
        equation_str = f"(y - {k})^2/{b_sq} - (x - {h})^2/{a_sq} = 1"
        
    question_text = f"已知雙曲線方程式為 {equation_str}，請問此雙曲線的中心點坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    answer = f"({h},{k})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_quadratic_curves_question():
    """動態生成一道「二次曲線」的題目 (判斷類型)"""
    # Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    # 判斷類型主要看 B^2 - 4AC
    # < 0: 橢圓或圓
    # = 0: 拋物線
    # = 0: 拋物線
    # > 0: 雙曲線
    
    conic_type = random.choice(['ellipse', 'parabola', 'hyperbola'])
    
    if conic_type == 'ellipse':
        # A, C 同號，B=0
        A = random.randint(1, 5)
        C = random.randint(1, 5)
        while A == C: # 避免是圓
            C = random.randint(1, 5)
        B = 0
        equation_str = f"{A}x^2 + {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "橢圓"
    elif conic_type == 'parabola':
        # A=0 或 C=0 (但不同時為0), B=0
        if random.choice([True, False]):
            A = random.randint(1, 5)
            C = 0
        else:
            A = 0
            C = random.randint(1, 5)
        B = 0
        if A == 0:
            equation_str = f"{C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        else:
            equation_str = f"{A}x^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "拋物線"
    else: # hyperbola
        # A, C 異號，B=0
        A = random.randint(1, 5)
        C = random.randint(-5, -1)
        B = 0
        equation_str = f"{A}x^2 {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "雙曲線"
        
    question_text = f"請問下列方程式代表哪一種二次曲線？\n{equation_str}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_linear_programming_question():
    """動態生成一道「線性規劃」的題目 (判斷點是否滿足不等式組)"""
    num_inequalities = random.choice([2, 3])
    inequalities = []
    inequality_strs = []
    
    # 生成不等式組
    for _ in range(num_inequalities):
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 and b == 0:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        
        # 確保不等式有意義
        x_test = random.randint(-5, 5)
        y_test = random.randint(-5, 5)
        c = (a * x_test) + (b * y_test) + random.randint(-2, 2) # 讓點有機會滿足或不滿足
        
        sign = random.choice(['>', '>=', '<', '<='])
        inequalities.append({'a': a, 'b': b, 'c': c, 'sign': sign})
        inequality_strs.append(format_inequality(a, b, c, sign))
        
    # 生成一個測試點
    test_x = random.randint(-5, 5)
    test_y = random.randint(-5, 5)
    
    # 檢查測試點是否滿足所有不等式
    is_solution = True
    for ieq in inequalities:
        if not check_inequality(ieq['a'], ieq['b'], ieq['c'], ieq['sign'], test_x, test_y):
            is_solution = False
            break
            
    correct_answer = "是" if is_solution else "否"
    system_str = "\n".join([f"  {s}" for s in inequality_strs])
    
    question_text = f"請問點 ({test_x}, {test_y}) 是否為下列不等式組的解？ (請回答 '是' 或 '否')\n{system_str}"
    
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": None # 可以考慮使用 validate_check_point
    }

def generate_conditional_probability_question():
    """動態生成一道「條件機率」的題目"""
    # 簡單情境：從袋中取球
    red_balls = random.randint(2, 5)
    blue_balls = random.randint(2, 5)
    total_balls = red_balls + blue_balls
    
    # 假設第一次取出紅球，第二次再取球是藍球的機率
    # P(B|R) = P(B and R) / P(R)
    # P(R) = red_balls / total_balls
    # P(B and R) = (red_balls / total_balls) * (blue_balls / (total_balls - 1))
    # P(B|R) = blue_balls / (total_balls - 1)
    
    question_text = (
        f"一個袋中有 {red_balls} 顆紅球和 {blue_balls} 顆藍球。"
        f"如果第一次取出紅球後不放回，請問第二次取出藍球的機率是多少？ (請以 a/b 的形式表示)"
    )
    
    answer_num = blue_balls
    answer_den = total_balls - 1
    
    from math import gcd
    common = gcd(answer_num, answer_den)
    answer = f"{answer_num // common}/{answer_den // common}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_bayes_theorem_question():
    """動態生成一道「貝氏定理」的題目 (簡化版)"""
    # 假設情境：某疾病的盛行率和檢測的準確性
    # P(D) = 疾病盛行率
    # P(pos|D) = 檢測結果為陽性，且確實有病 (真陽性率)
    # P(pos|not D) = 檢測結果為陽性，但沒有病 (偽陽性率)
    # 求 P(D|pos) = P(pos|D) * P(D) / P(pos)
    # P(pos) = P(pos|D) * P(D) + P(pos|not D) * P(not D)
    
    # 為了簡化，我們使用容易計算的數字
    p_d = 0.01 # 疾病盛行率 1%
    p_pos_given_d = 0.95 # 真陽性率 95%
    p_pos_given_not_d = 0.10 # 偽陽性率 10%
    
    p_not_d = 1 - p_d
    p_pos = (p_pos_given_d * p_d) + (p_pos_given_not_d * p_not_d)
    p_d_given_pos = (p_pos_given_d * p_d) / p_pos
    
    question_text = (
        f"某種疾病的盛行率為 {p_d*100:.0f}%。"
        f"一種檢測方法對有病的人有 {p_pos_given_d*100:.0f}% 的機率呈現陽性，"
        f"對沒病的人有 {p_pos_given_not_d*100:.0f}% 的機率呈現陽性。"
        f"如果一個人的檢測結果為陽性，請問他確實有病的機率是多少？ (請四捨五入到小數點後兩位)"
    )
    answer = f"{p_d_given_pos:.2f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_discrete_random_variables_question():
    """動態生成一道「離散型隨機變數」的題目 (求期望值)"""
    # 簡單的機率分佈
    values = [random.randint(1, 5) for _ in range(3)]
    probabilities = [0.2, 0.3, 0.5] # 固定機率，確保和為 1
    
    # 計算期望值 E(X) = sum(x * P(x))
    expected_value = sum(v * p for v, p in zip(values, probabilities))
    
    question_text = (
        f"已知離散型隨機變數 X 的機率分佈如下：\n"
        f"  P(X={values[0]}) = {probabilities[0]:.1f}\n"
        f"  P(X={values[1]}) = {probabilities[1]:.1f}\n"
        f"  P(X={values[2]}) = {probabilities[2]:.1f}\n"
        f"請問 X 的期望值是多少？"
    )
    answer = str(expected_value)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_binomial_geometric_distributions_question():
    """動態生成一道「二項分布與幾何分布」的題目 (判斷類型)"""
    scenario_type = random.choice(['binomial', 'geometric'])
    
    if scenario_type == 'binomial':
        n = random.randint(5, 10)
        p = random.choice([0.2, 0.5, 0.8])
        question_text = (
            f"小明投籃命中率為 {p*100:.0f}%。他投籃 {n} 次，請問他投進 3 球的機率，"
            f"適合用哪種機率分布來計算？ (請回答 '二項分布' 或 '幾何分布')"
        )
        answer = "二項分布"
    else: # geometric
        p = random.choice([0.2, 0.5, 0.8])
        question_text = (
            f"小華每次射擊命中靶心的機率為 {p*100:.0f}%。"
            f"請問他第一次命中靶心需要射擊幾次的機率，適合用哪種機率分布來計算？ (請回答 '二項分布' 或 '幾何分布')"
        )
        answer = "幾何分布"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_binomial_distribution_question():
    """動態生成一道「二項分布」的題目 (求特定成功次數的機率)"""
    n = random.randint(3, 5) # 試驗次數
    k = random.randint(1, n) # 成功次數
    p_val = random.choice([0.2, 0.5, 0.8]) # 成功機率
    
    # 計算二項分布機率 P(X=k) = C(n, k) * p^k * (1-p)^(n-k)
    probability = math.comb(n, k) * (p_val ** k) * ((1 - p_val) ** (n - k))
    
    question_text = (
        f"某次實驗成功機率為 {p_val:.1f}。若進行 {n} 次獨立實驗，"
        f"請問恰好成功 {k} 次的機率是多少？ (請四捨五入到小數點後三位)"
    )
    answer = f"{probability:.3f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_complex_roots_polynomials_question():
    """動態生成一道「複數與多項式方程式的根」的題目 (共軛複數根)"""
    # 根據共軛複數根定理，如果一個實係數多項式有一個複數根 a+bi，那麼它的共軛複數 a-bi 也是一個根。
    
    # 生成一個複數根
    a = random.randint(-3, 3)
    b = random.randint(1, 3) # 確保 b 不為 0，是純虛數部分
    
    complex_root_str = f"{a}{'+' if b > 0 else ''}{b}i"
    conjugate_root_str = f"{a}{'-' if b > 0 else '+'}{abs(b)}i"
    
    question_text = (
        f"已知一個實係數多項式方程式有一個根為 {complex_root_str}。"
        f"請問此多項式方程式的另一個根為何？"
    )
    answer = conjugate_root_str
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_complex_numbers_geometry_question():
    """動態生成一道「複數的幾何意涵」的題目 (求模數)"""
    real_part = random.randint(-5, 5)
    imag_part = random.randint(-5, 5)
    
    # 確保不是 0+0i
    while real_part == 0 and imag_part == 0:
        real_part = random.randint(-5, 5)
        imag_part = random.randint(-5, 5)
        
    modulus = math.sqrt(real_part**2 + imag_part**2)
    
    complex_num_str = f"{real_part}{'+' if imag_part >= 0 else ''}{imag_part}i"
    
    question_text = f"請問複數 {complex_num_str} 的模數 (絕對值) 是多少？ (請四捨五入到小數點後一位)"
    answer = f"{modulus:.1f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_complex_plane_question():
    """動態生成一道「複數與複數平面」的題目 (從坐標判斷複數)"""
    real_part = random.randint(-5, 5)
    imag_part = random.randint(-5, 5)
    
    complex_num_str = f"{real_part}{'+' if imag_part >= 0 else ''}{imag_part}i"
    
    question_text = f"在複數平面上，點 ({real_part}, {imag_part}) 代表哪一個複數？ (請以 a+bi 的形式回答)"
    answer = complex_num_str
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_polynomials_intro_question():
    """動態生成一道「多項式」的題目 (求次數)"""
    degree = random.randint(1, 4)
    coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
    
    # 確保最高次項係數不為零
    while coeffs[0] == 0:
        coeffs[0] = random.randint(-5, 5)
        
    poly_text = format_polynomial(coeffs)
    
    question_text = f"請問多項式 f(x) = {poly_text} 的次數是多少？"
    answer = str(degree)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_sequence_limits_infinite_series_question():
    """動態生成一道「數列的極限與無窮等比級數」的題目 (求無窮等比級數和)"""
    a = random.randint(1, 10) # 首項
    r_num = random.randint(1, 4) # 公比分子
    r_den = random.randint(5, 9) # 公比分母，確保 |r| < 1
    r = r_num / r_den
    
    # 無窮等比級數和 S = a / (1 - r)
    sum_val = a / (1 - r)
    
    question_text = (
        f"已知一個無窮等比級數的首項為 {a}，公比為 {r_num}/{r_den}。"
        f"請問此無窮等比級數的和是多少？ (請四捨五入到小數點後兩位)"
    )
    answer = f"{sum_val:.2f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_functions_limits_question():
    """動態生成一道「函數與函數的極限」的題目 (求多項式函數的極限)"""
    # 簡單的多項式函數，直接代入即可
    a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    x_val = random.randint(-2, 2)
    
    # f(x) = ax^2 + bx + c
    limit_val = a * (x_val**2) + b * x_val + c
    
    question_text = f"請問函數 f(x) = {a}x^2 + {b}x + {c} 在 x 趨近於 {x_val} 時的極限值是多少？"
    answer = str(limit_val)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

def generate_differentiation_question():
    """動態生成一道「微分」的題目 (求多項式函數的導數)"""
    # f(x) = ax^2 + bx + c
    # f'(x) = 2ax + b
    
    a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    # 確保不是常數函數
    while a == 0 and b == 0:
        a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        
    question_text = f"請問函數 f(x) = {a}x^2 + {b}x + {c} 的導數 f'(x) 是多少？ (請以 ax+b 的形式回答)"
    
    # 格式化答案
    terms = []
    if 2*a != 0:
        terms.append(f"{2*a}x")
    if b != 0:
        if b > 0 and terms:
            terms.append(f" + {b}")
        elif b < 0 and terms:
            terms.append(f" - {abs(b)}")
        else:
            terms.append(str(b))
            
    if not terms:
        answer = "0"
    else:
        answer = "".join(terms)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }




# ==============================================================================
# 6. Skill Engine Definition
# ==============================================================================
SKILL_ENGINE = {
    # Logarithms & Exponents
    'logarithms': {
        'generator': generate_common_logarithm_question,
        'display_name': '常用對數',
        'description': '計算常用對數。'
    },
    'exponents': {
        'generator': generate_exponential_question,
        'display_name': '指數',
        'description': '計算指數運算。'
    },
    'common_logarithms': {
        'generator': generate_common_logarithm_question,
        'display_name': '常用對數',
        'description': '計算常用對數。'
    },
    'exponential_functions': { 'generator': generate_exponential_functions_question, 'display_name': '指數函數', 'description': '練習解指數方程式。' },
    'logarithmic_properties': {
        'generator': generate_logarithmic_properties_question,
        'display_name': '對數與對數律 / 對數',
        'description': '練習對數律的應用。'
    },
    'logarithmic_functions': { 'generator': generate_logarithmic_functions_question, 'display_name': '對數函數', 'description': '練習解對數方程式。' },

    # Linear Algebra & Equations
    'linear_equations': {
        'generator': generate_linear_equation_question,
        'display_name': '直線方程式',
        'description': '練習直線方程式。'
    },
    'simultaneous_equations_1or2var': {
        'generator': generate_addition_subtraction_question,
        'display_name': '一/二元一次聯立方程式',
        'description': '練習二元一次聯立方程式的加減消去法。'
    },
    'simultaneous_equations_3var': {
        'generator': generate_addition_subtraction_question,
        'display_name': '三元一次聯立方程式',
        'description': '練習二元一次聯立方程式(暫代)。'
    },
    'linear_programming': {
        'generator': generate_inequality_region_question,
        'display_name': '線性規劃',
        'description': '練習二元一次不等式圖解區域。'
    },

    # Geometry
    'circle_equations': {
        'generator': generate_circle_equation_question,
        'display_name': '圓方程式',
        'description': '練習圓的方程式。'
    },
    'circle_line_relations': {
        'generator': generate_circle_line_question,
        'display_name': '圓與直線',
        'description': '練習圓與直線的關係。'
    },

    # Polynomials
    'polynomial_division': {
        'generator': generate_polynomial_division_question,
        'display_name': '多項式的除法原理',
        'description': '練習多項式除法、餘式與因式定理。'
    },
    'quadratic_functions': {
        'generator': generate_factor_theorem_question,
        'display_name': '一次與二次函數',
        'description': '練習判斷因式。'
    },
    'cubic_functions_graph': {
        'generator': generate_factor_theorem_question,
        'display_name': '三次函數的圖形特徵',
        'description': '練習判斷因式。'
    },
    'polynomial_inequalities': {
        'generator': generate_inequality_region_question,
        'display_name': '多項式不等式',
        'description': '練習不等式相關問題。'
    },
    

    # Placeholder Mappings (using default generators)
    'sequences_recursion': { 'generator': generate_sequence_question, 'display_name': '數列與遞迴關係', 'description': '練習等差數列。' },
    'series': { 'generator': generate_series_question, 'display_name': '級數', 'description': '練習等差級數求和。' },
    'counting_principles': { 'generator': generate_counting_principles_question, 'display_name': '計數原理', 'description': '練習計數的乘法原理。' },
    'permutations': { 'generator': generate_permutations_question, 'display_name': '排列', 'description': '練習排列 P(n,k)。' },
    'combinations': { 'generator': generate_combinations_question, 'display_name': '組合', 'description': '練習組合 C(n,k)。' },
    'classical_probability': { 'generator': generate_classical_probability_question, 'display_name': '古典機率', 'description': '練習基本的機率問題。' },
    'expected_value': { 'generator': generate_expected_value_question, 'display_name': '數學期望值', 'description': '練習計算期望值。' },
    'data_analysis_1d': { 'generator': generate_data_analysis_1d_question, 'display_name': '一維數據分析', 'description': '練習計算平均數、中位數或眾數。' },
    'data_analysis_2d': { 'generator': generate_data_analysis_2d_question, 'display_name': '二維數據分析', 'description': '練習計算二維數據的中心點。' },
    'trig_ratios_right_triangle': { 'generator': generate_trig_ratios_right_triangle_question, 'display_name': '直角三角形的三角比', 'description': '練習計算三角比。' },
    'trig_ratios_general_angle': { 'generator': generate_trig_ratios_general_angle_question, 'display_name': '廣義角三角比', 'description': '練習計算廣義角的三角比。' },
    'polar_coordinates': { 'generator': generate_polar_coordinates_question, 'display_name': '與極坐標', 'description': '練習極座標與直角座標的轉換。' },
    'trig_properties_laws': { 'generator': generate_trig_properties_laws_question, 'display_name': '三角比的性質', 'description': '練習正弦與餘弦定理。' },
    'radian_measure': { 'generator': generate_radian_measure_question, 'display_name': '弧度量', 'description': '練習角度與弧度的換算。' },
    'trig_graphs_periodicity': { 'generator': generate_trig_graphs_periodicity_question, 'display_name': '三角函數的圖形 / 週期性', 'description': '練習三角函數的週期。' },
    'trig_sum_difference': { 'generator': generate_trig_sum_difference_question, 'display_name': '三角的和差角公式', 'description': '練習和差角公式的觀念。' },
    'trig_sine_cosine_combination': { 'generator': generate_trig_sine_cosine_combination_question, 'display_name': '正餘弦的疊合', 'description': '練習疊合後求最大最小值。' },
    'real_number_system': { 'generator': generate_real_number_system_question, 'display_name': '數', 'description': '練習判斷有理數與無理數。' },
    'absolute_value': { 'generator': generate_absolute_value_question, 'display_name': '絕對值', 'description': '練習絕對值的基本運算。' },
    'vectors_2d': { 'generator': generate_vectors_2d_question, 'display_name': '平面向量', 'description': '練習向量的分量。' },
    'vectors_2d_operations': { 'generator': generate_vectors_2d_operations_question, 'display_name': '平面向量的運算', 'description': '練習向量的加減法。' },
    'space_concepts': { 'generator': generate_space_concepts_question, 'display_name': '空間概念', 'description': '練習點到平面的距離。' },
    'vectors_3d_coordinates': { 'generator': generate_vectors_3d_coordinates_question, 'display_name': '空間向量的坐標表示法', 'description': '練習空間向量的分量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'vectors_3d_operations': { 'generator': generate_vectors_3d_operations_question, 'display_name': '空間向量的運算', 'description': '練習空間向量的加減法。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'determinant_3x3': { 'generator': generate_determinant_3x3_question, 'display_name': '三階行列式', 'description': '練習計算三階行列式的值。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'planes_in_space': { 'generator': generate_planes_in_space_question, 'display_name': '空間中的平面', 'description': '練習求平面的法向量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'lines_in_space': { 'generator': generate_lines_in_space_question, 'display_name': '空間中的直線', 'description': '練習求直線的方向向量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'function_properties': { 'generator': generate_function_properties_question, 'display_name': '函數性質的判定', 'description': '練習判斷函數的奇偶性。', 'grade_level': '十一年級', 'main_unit': '(微積分/極限)' },
    'matrix_applications': { 'generator': generate_matrix_applications_question, 'display_name': '矩陣的應用', 'description': '練習矩陣乘法。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'matrix_operations': { 'generator': generate_matrix_operations_question, 'display_name': '矩陣的運算', 'description': '練習矩陣加法。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'simultaneous_equations_3var': { 'generator': generate_simultaneous_equations_3var_question, 'display_name': '三元一次聯立方程式', 'description': '練習解三元一次聯立方程式。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    
    'function_properties': { 'generator': generate_remainder_theorem_question, 'display_name': '函數性質的判定', 'description': 'Placeholder' },
    
    
    'ratio_in_plane': { 'generator': generate_ratio_in_plane_question, 'display_name': '平面上的比例', 'description': '練習分點公式。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'coordinate_systems': { 'generator': generate_coordinate_systems_question, 'display_name': '坐標系', 'description': '練習直角坐標與極坐標轉換。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'conic_sections': { 'generator': generate_conic_sections_question, 'display_name': '圓錐曲線', 'description': '練習判斷圓錐曲線類型。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'parabola': { 'generator': generate_parabola_question, 'display_name': '拋物線', 'description': '練習求拋物線頂點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'ellipse': { 'generator': generate_ellipse_question, 'display_name': '橢圓', 'description': '練習求橢圓中心點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'hyperbola': { 'generator': generate_hyperbola_question, 'display_name': '雙曲線', 'description': '練習求雙曲線中心點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'quadratic_curves': { 'generator': generate_quadratic_curves_question, 'display_name': '二次曲線', 'description': '練習判斷二次曲線類型。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'linear_programming': { 'generator': generate_linear_programming_question, 'display_name': '線性規劃', 'description': '練習判斷點是否滿足不等式組。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'conditional_probability': { 'generator': generate_conditional_probability_question, 'display_name': '條件機率', 'description': '練習計算條件機率。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'bayes_theorem': { 'generator': generate_bayes_theorem_question, 'display_name': '貝氏定理', 'description': '練習貝氏定理的應用。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'discrete_random_variables': { 'generator': generate_discrete_random_variables_question, 'display_name': '離散型隨機變數', 'description': '練習計算離散型隨機變數的期望值。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'binomial_geometric_distributions': { 'generator': generate_binomial_geometric_distributions_question, 'display_name': '二項分布與幾何分布', 'description': '練習判斷二項分布與幾何分布。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'binomial_distribution': { 'generator': generate_binomial_distribution_question, 'display_name': '二項分布', 'description': '練習計算二項分布機率。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'complex_roots_polynomials': { 'generator': generate_complex_roots_polynomials_question, 'display_name': '複數與多項式方程式的根', 'description': '練習共軛複數根定理。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    
    
    
    
    
    'integration': { 'generator': generate_remainder_theorem_question, 'display_name': '積分', 'description': 'Placeholder' },
    'integration_applications': { 'generator': generate_remainder_theorem_question, 'display_name': '積分的應用', 'description': 'Placeholder' },

    # Original 6 skills (now mapped to user's keys)
    'remainder-theorem': { 'generator': generate_remainder_theorem_question, 'display_name': '餘式定理', 'description': '練習 f(x) 除以 (x-k) 的餘式。' },
    'factor-theorem': { 'generator': generate_factor_theorem_question, 'display_name': '因式定理', 'description': '判斷 (x-k) 是否為 f(x) 的因式。' },
    'linear-eq-substitution': { 'generator': generate_substitution_question, 'display_name': '二元一次 (帶入消去法)', 'description': '練習 y=ax+b 形式的帶入消去。' },
    'linear-eq-addition': { 'generator': generate_addition_subtraction_question, 'display_name': '二元一次 (加減消去法)', 'description': '練習係數需乘以倍數的加減消去。' },
    'linear-ineq-region': { 'generator': generate_inequality_region_question, 'display_name': '二元一次不等式 (圖解區域)', 'description': '在數位計算紙上畫出不等式的解區域。' },
    'linear-ineq-check-point': { 'generator': generate_check_point_in_system_question, 'display_name': '二元一次不等式 (判斷解)', 'description': '判斷一個點是否為不等式系統的解。' }
}

DEMOTION_THRESHOLD = 3  # 連續答錯 3 題就降級

def initialize_skills():
    """同步 SKILL_ENGINE 到資料庫 (包含先備知識)"""
    print("正在同步技能到資料庫...")
    for skill_id, skill_data_in_code in SKILL_ENGINE.items():
        skill_in_db = Skill.query.filter_by(name=skill_id).first()
        needs_update = False
        if skill_in_db:
            # 比較並更新現有技能
            if skill_in_db.display_name != skill_data_in_code['display_name']:
                skill_in_db.display_name = skill_data_in_code['display_name']
                needs_update = True
            if 'description' in skill_data_in_code and skill_in_db.description != skill_data_in_code['description']:
                skill_in_db.description = skill_data_in_code['description']
                needs_update = True
            if 'grade_level' in skill_data_in_code and skill_in_db.grade_level != skill_data_in_code['grade_level']:
                skill_in_db.grade_level = skill_data_in_code['grade_level']
                needs_update = True
            if 'main_unit' in skill_data_in_code and skill_in_db.main_unit != skill_data_in_code['main_unit']:
                skill_in_db.main_unit = skill_data_in_code['main_unit']
                needs_update = True
            # if skill_in_db.prerequisite_skill_id != skill_data_in_code.get('prerequisite_skill_id'):
            #     skill_in_db.prerequisite_skill_id = skill_data_in_code.get('prerequisite_skill_id')
            #     needs_update = True
            if needs_update:
                db.session.commit()
                print(f"更新技能 {skill_id} 到資料庫")
        else:
            # 創建新技能
            new_skill = Skill(
                name=skill_id,
                display_name=skill_data_in_code['display_name'],
                description=skill_data_in_code.get('description', '無描述'),
                grade_level=skill_data_in_code.get('grade_level'),
                main_unit=skill_data_in_code.get('main_unit')
            )
            db.session.add(new_skill)
            db.session.commit()
            print(f"添加新技能 {skill_id} 到資料庫")

DEMOTION_THRESHOLD = 3  # 連續答錯 3 題就降級

def initialize_skills():
    """同步 SKILL_ENGINE 到資料庫 (包含先備知識)"""
    print("正在同步技能到資料庫...")
    for skill_id, skill_data_in_code in SKILL_ENGINE.items():
        skill_in_db = Skill.query.filter_by(name=skill_id).first()
        needs_update = False
        if skill_in_db:
            # 比較並更新現有技能
            if skill_in_db.display_name != skill_data_in_code['display_name']:
                skill_in_db.display_name = skill_data_in_code['display_name']
                needs_update = True
            if 'description' in skill_data_in_code and skill_in_db.description != skill_data_in_code['description']:
                skill_in_db.description = skill_data_in_code['description']
                needs_update = True
            if 'grade_level' in skill_data_in_code and skill_in_db.grade_level != skill_data_in_code['grade_level']:
                skill_in_db.grade_level = skill_data_in_code['grade_level']
                needs_update = True
            if 'main_unit' in skill_data_in_code and skill_in_db.main_unit != skill_data_in_code['main_unit']:
                skill_in_db.main_unit = skill_data_in_code['main_unit']
                needs_update = True
            # if skill_in_db.prerequisite_skill_id != skill_data_in_code.get('prerequisite_skill_id'):
            #     skill_in_db.prerequisite_skill_id = skill_data_in_code.get('prerequisite_skill_id')
            #     needs_update = True
            if needs_update:
                db.session.commit()
                print(f"更新技能 {skill_id} 到資料庫")
        else:
            # 創建新技能
            new_skill = Skill(
                name=skill_id,
                display_name=skill_data_in_code['display_name'],
                description=skill_data_in_code.get('description', '無描述'),
                grade_level=skill_data_in_code.get('grade_level'),
                main_unit=skill_data_in_code.get('main_unit')
            )
            db.session.add(new_skill)
            db.session.commit()
            print(f"添加新技能 {skill_id} 到資料庫")

# ==============================================================================
# 7. Routes (View Functions)
# ==============================================================================

# --- Authentication Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("帳號或密碼不可為空", "warning")
            return redirect(url_for('register'))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("這個帳號名稱已經有人用了！", "warning")
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("註冊成功！請登入。", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("帳號或密碼不可為空", "danger")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"歡迎回來，{user.username}！", "success")
            return redirect(url_for('home'))
        else:
            flash("帳號或密碼錯誤。", "danger")
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("您已成功登出。", "info")
    return redirect(url_for('login'))

@app.route('/upload_image_problem', methods=['POST'])
def upload_image_problem():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first.'}), 401
    if not model: # Changed from vision_model
        return jsonify({'error': 'Model is not configured.'}), 500

    if 'problem_image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    image_file = request.files['problem_image']
    question_number = request.form.get('question_number') # Get the question number
    
    if image_file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    try:
        img = Image.open(image_file.stream)
        
        # Modify prompt based on whether a question number was provided
        if question_number:
            prompt = f"這是一張數學題目的圖片。請只專注於題號為 '{question_number}' 的題目，並僅辨識其文字內容。如果圖片中找不到該題號，請辨識圖片中的所有文字。"
        else:
            prompt = "辨識這張圖片中的數學題目文字。"

        prompt_parts = [prompt, img]
        
        response = model.generate_content(prompt_parts) # Changed from vision_model
        recognized_text = response.text

        session['custom_question_text'] = recognized_text
        
        redirect_url = url_for('practice', skill_id='custom')

        return jsonify({'redirect_url': redirect_url})

    except Exception as e:
        print(f"Error during image recognition: {e}")
        return jsonify({'error': f'An error occurred during recognition: {str(e)}'}), 500

# --- Core Application Routes ---
@app.route("/")
def home():
    if 'user_id' not in session:
        flash("請先登入！", "warning")
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# ( ... dashboard 函式的正下方 ... )

@app.route('/grade/<grade_name>')
def show_grade(grade_name):
    """ 
    [新頁面] 顯示特定年級的所有「大單元」 
    例如： /grade/十年級
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 查詢該年級下所有不重複的「大單元」
    try:
        units_query = db.session.query(Skill.main_unit).filter(Skill.grade_level == grade_name).distinct().all()
        main_units = [u[0] for u in units_query if u[0] is not None]
    except Exception as e:
        print(f"查詢 {grade_name} 的大單元時出錯: {e}")
        main_units = []
        flash("讀取單元時發生錯誤。", "warning")

    # 我們會建立一個新的 HTML 模板來顯示
    return render_template('grade_view.html', 
                           grade_name=grade_name, 
                           main_units=main_units)

# (請找到您 app.py 中現有的 dashboard 函式...)
@app.route('/dashboard')
def dashboard():
    """ 儀表板 - 現在改為顯示所有「年級」 """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        flash("找不到用戶資料，請重新登入。", "warning")
        return redirect(url_for('login'))

    # 從 Skill 表中查詢所有不重複的「年級」
    try:
        # 查詢所有不重複的 grade_level
        grades_query = db.session.query(Skill.grade_level).distinct().all()
        
        # 將 [( '十年級',), ('十一年級',)] 轉成 ['十年級', '十一年級']
        grades = [g[0] for g in grades_query if g[0] is not None]
        
        # 這裡可以手動排序 (如果您的年級不是照順序)
        # 例如： grades.sort(key=lambda g: 10 if '十' in g else (11 if '十一' in g else 12))
        
    except Exception as e:
        print(f"查詢年級時出錯: {e}")
        grades = []
        flash("讀取課綱時發生錯誤，請稍後再試。", "warning")

    # 注意：我們傳送的變數改為 grades
    return render_template('dashboard.html', 
                           username=user.username, 
                           grades=grades) 
# ( ... 取代到這裡為止 ... )
# ( ... dashboard 函式的正下方 ... )

# ( ... 找到您 app.py 中的 show_unit ... )
@app.route('/unit/<grade_name>/<path:main_unit_name>')
def show_unit(grade_name, main_unit_name):
    """ 
    [新頁面] 顯示特定大單元的所有「小單元」 (包含使用者進度)
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # 查詢該大單元下所有的「小單元」(即 Skills)
    try:
        sub_units_query = Skill.query.filter(Skill.main_unit == main_unit_name).order_by(Skill.id).all()
        
        # --- vvv 這就是我們加回來的「進度查詢」邏輯 vvv ---
        
        # 1. 取得這個用戶的所有進度
        user_progresses = UserProgress.query.filter_by(user_id=user_id).all()
        # 2. 轉成字典方便查詢 { skill_id: progress_object }
        progress_map = {p.skill_id: p for p in user_progresses}
        
        # 3. 建立要傳到前端的資料包
        sub_units_data = []
        for skill in sub_units_query:
            progress = progress_map.get(skill.id)
            sub_units_data.append({
                'skill': skill,
                'consecutive_correct': progress.consecutive_correct if progress else 0,
                'total_attempted': progress.total_attempted if progress else 0
            })
        # --- ^^^ 進度查詢邏輯結束 ^^^ ---

    except Exception as e:
        print(f"查詢 {main_unit_name} 的小單元時出錯: {e}")
        sub_units_data = []
        flash("讀取小單元時發生錯誤。", "warning")
        
    # 從第一個小單元反查年級，用來顯示麵包屑導覽
    # current_grade = sub_units_query[0].grade_level if sub_units_query else "..."

    # 我們會建立第二個新的 HTML 模板來顯示
    return render_template('unit_view.html',
                           grade_name=grade_name,
                           main_unit_name=main_unit_name,
                           sub_units_data=sub_units_data) # <--- 注意，變數名稱改了
# ( ... 取代到這裡為止 ... )

@app.route("/practice/<string:skill_id>")
def practice(skill_id):
    if 'user_id' not in session:
        flash("請先登入！", "warning")
        return redirect(url_for('login'))

    question_data = {}
    skill_display_name = ""

    if skill_id == 'custom':
        question_text = session.get('custom_question_text')
        if not question_text:
            flash("找不到自訂題目，請重新上傳。", "warning")
            return redirect(url_for('dashboard'))
        
        question_data = {
            'text': question_text,
            'answer': None,
            'inequality_string': None,
            'validation_function_name': None
        }
        skill_display_name = "自訂題目"
        print(f"(custom) 新題目: {question_text}")

    else:
        skill = Skill.query.filter_by(name=skill_id).first()
        if not skill or skill_id not in SKILL_ENGINE:
            flash("找不到指定的練習單元。", "danger")
            return redirect(url_for('dashboard'))
        
        question_data = SKILL_ENGINE[skill_id]['generator']()
        skill_display_name = skill.display_name
        print(f"({skill_id}) 新題目: {question_data.get('text')} (答案: {question_data.get('answer')})")

    session['current_skill_id'] = skill_id
    session['current_question_text'] = question_data.get('text')
    session['current_answer'] = question_data.get('answer')
    session['current_inequality_string'] = question_data.get('inequality_string')
    session['validation_function_name'] = question_data.get('validation_function_name')
    
    return render_template('index.html',
                           question_text=question_data.get('text'),
                           inequality_string=question_data.get('inequality_string') or '',
                           username=session.get('username'),
                           skill_display_name=skill_display_name)

# --- API Endpoints ---
@app.route("/get_next_question", methods=["GET"])
def get_next_question():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    skill_id = session.get('current_skill_id')
    if not skill_id or skill_id not in SKILL_ENGINE:
        return jsonify({"error": "Skill error"}), 400
        
    generator_func = SKILL_ENGINE[skill_id]['generator']
    question_data = generator_func()
    
    session['current_answer'] = question_data.get('answer')
    session['current_question_text'] = question_data.get('text')
    session['current_inequality_string'] = question_data.get('inequality_string')
    session['validation_function_name'] = question_data.get('validation_function_name')
    
    print(f"({skill_id}) 下一題: {question_data.get('text')} (答案: {question_data.get('answer')})")

    return jsonify({
        "new_question_text": question_data.get('text'),
        "inequality_string": question_data.get('inequality_string')
    })

@app.route("/check_answer", methods=["POST"])
def check_answer():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    if not data or 'answer' not in data:
        return jsonify({"error": "Missing JSON data or 'answer'"}), 400
        
    user_answer = data.get('answer')
    skill_id_str = session.get('current_skill_id')
    correct_answer = session.get('current_answer')
    validation_func_name = session.get('validation_function_name')
    if not skill_id_str:
        return jsonify({"error": "Session missing skill_id"}), 400
    
    is_correct = False
    result_message = ""
    validation_func = globals().get(validation_func_name) if validation_func_name else None
    
    if validation_func:
        try:
            is_correct = validation_func(user_answer, correct_answer)
            result_message = "答對了！" if is_correct else f"答錯了... (提示: {correct_answer})"
        except Exception as e:
            print(f"Validation function error: {e}")
            is_correct = False
            result_message = "答案格式錯誤"
    else:
        is_correct = (str(user_answer).strip().lower() == str(correct_answer).strip().lower())
        result_message = "答對了！" if is_correct else f"答錯了... (提示: {correct_answer})"
    
    demote_to_skill_id = None
    
    try:
        user_id = session['user_id']
        skill = Skill.query.filter_by(name=skill_id_str).first()
        if skill:
            progress = UserProgress.query.filter_by(user_id=user_id, skill_id=skill.id).first()
            if not progress:
                progress = UserProgress(user_id=user_id, skill_id=skill.id)
                db.session.add(progress)
            
            progress.total_attempted += 1
            if is_correct:
                progress.consecutive_correct += 1
                progress.total_correct += 1
                progress.consecutive_incorrect = 0
            else:
                progress.consecutive_correct = 0
                progress.consecutive_incorrect += 1
                if progress.consecutive_incorrect >= DEMOTION_THRESHOLD and skill.prerequisite_skill_id:
                    demote_to_skill_id = skill.prerequisite_skill_id
                    prereq_skill = Skill.query.filter_by(name=demote_to_skill_id).first()
                    prereq_name = prereq_skill.display_name if prereq_skill else "基礎單元"
                    result_message = f"您在「{skill.display_name}」單元連續答錯 {progress.consecutive_incorrect} 題了。\n系統建議您先回去複習「{prereq_name}」！"
                    progress.consecutive_incorrect = 0
            db.session.commit()
        else:
            print(f"Warning: Skill '{skill_id_str}' not found.")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating progress: {e}")
    
    return jsonify({
        "result": result_message,
        "correct": is_correct,
        "demote_to_skill_id": demote_to_skill_id
    })

@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    if 'user_id' not in session:
        return jsonify({"reply": "Not logged in"}), 401
    if model is None:
        return jsonify({"reply": "AI 助教尚未設定。"}), 500
    data = request.get_json()
    if not data or not data.get('prompt') or not data.get('current_question'):
        return jsonify({"reply": "錯誤：缺少提示或題目內容。"}), 400
         
    user_prompt = data.get('prompt')
    current_question = data.get('current_question')
    current_skill_id = session.get('current_skill_id', 'unknown')
    current_skill_display_name = SKILL_ENGINE.get(current_skill_id, {}).get('display_name', '數學')
    
    system_instruction = f"""
        你是一位專業且有耐心的高中數學家教，專門輔導資源班的學生。
        學生的目標是段考及格。請用繁體中文回答。
        
        你的任務：
        1.  **角色扮演**：你是一位友善的 AI 助教。
        2.  **教學重點**：學生目前正在練習「{current_skill_display_name}」。
        3.  **當前題目**：學生正在看的題目是「{current_question}」。
        4.  **回答限制**：
            * **不要直接給答案！** 這是最重要的規則。
            * 如果學生問「這題答案是什麼？」，你應該反問他：「你覺得第一步該怎麼做呢？」或「你記得{current_skill_display_name}的定義嗎？」。
            * 如果學生問「詳解」，請提供「解題步驟」和「思路引導」，而不是只給計算過程。
            * 如果學生問觀念（例如「什麼是{current_skill_display_name}？」），請用最簡單、最白話的方式解釋。
    
        學生的問題是：「{user_prompt}」
        請根據上述規則，提供你的回答：
        """
    try:
        response = model.generate_content(system_instruction)
        ai_reply = response.text
    except Exception as e:
        print(f"Gemini API 呼叫失敗: {e}")
        ai_reply = "抱歉，助教現在有點忙... 請稍後再試。"
    return jsonify({"reply": ai_reply})

@app.route("/analyze_handwriting", methods=["POST"])
def analyze_handwriting():
    if 'user_id' not in session:
        return jsonify({"reply": "Not logged in"}), 401
    if model is None:
        return jsonify({"reply": "AI 助教尚未設定。"}), 500

    # --- 獲取 Session 中的情境 ---
    user_id = session.get('user_id')
    current_skill_id_str = session.get('current_skill_id', 'unknown')
    current_question = session.get('current_question_text', '未知題目')
    current_answer = session.get('current_answer')  # 可能是 None
    current_inequality_string = session.get('current_inequality_string')  # 可能是 None
    current_skill_display_name = SKILL_ENGINE.get(current_skill_id_str, {}).get('display_name', '數學')
    
    # --- 獲取前端傳來的資料 ---
    data = request.get_json()
    if not data:
        return jsonify({"reply": "錯誤：未收到 JSON 資料。"}), 400
    image_data_url = data.get('image_data_url')
    
    if not image_data_url:
        print("錯誤: 前端未發送 image_data_url")
        return jsonify({"reply": "錯誤：缺少圖片資料。"}), 400

    try:
        # 2. 轉換圖片
        header, encoded = image_data_url.split(",", 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data))

        # 3. 根據 current_inequality_string 是否存在，決定提示詞
        prompt_parts = []
        is_graph_question = bool(current_inequality_string)

        if is_graph_question:
            # --- 提示詞：畫圖題 (二元一次不等式) ---
            print(f"收到畫圖題分析請求: {current_inequality_string}")
            prompt_parts = [
                f"""你是一位專業且有耐心的數學家教，專門輔導高中資源班學生，目標是讓學生段考及格。
                請用繁體中文回答。學生正在練習「{current_skill_display_name}」單元，題目是：
                「{current_question}」
                學生提交了一張手繪圖片（已提供），請根據以下要求分析：
                - 題目要求學生在數位計算紙上畫出二元一次不等式 {current_inequality_string} 的解區域。
                - 檢查學生繪製的直線和陰影區域是否正確。
                - 如果正確，回覆格式為：「CORRECT: 畫得很好！解區域完全正確。」
                - 如果錯誤，回覆格式為：「INCORRECT: 錯誤的地方在...（具體說明，例如直線位置或陰影方向錯誤）」
                - 避免使用「請」或「請問」，直接給出結論。
                - 回覆中，如果是「INCORRECT」，請確保第一行是「INCORRECT: 錯誤的地方在...」，後續提供詳細解釋。
                以下是學生的手繪圖片：""",
                image
            ]
        else:
            # --- 提示詞：計算題 (通用) ---
            prompt_parts = [
                f"""你是一位專業且有耐心的數學家教，專門輔導高中資源班學生，目標是讓學生段考及格。
                請用繁體中文回答。學生正在練習「{current_skill_display_name}」單元，題目是：
                「{current_question}」
                學生提交了一張手寫計算過程的圖片（已提供），請根據以下要求分析：
                - 檢查計算過程是否正確。
                - 如果正確，回覆格式為：「CORRECT: 計算正確！」
                - 如果錯誤，回覆格式為：「INCORRECT: 錯誤的地方在...（具體說明，例如某一步計算錯誤）」
                - 避免使用「請」或「請問」，直接給出結論。
                以下是學生的手寫計算過程：""",
                image
            ]

        # 4. 呼叫 Gemini API (加入重試機制處理配額限制)
        ai_reply = ""
        max_retries = 3
        for i in range(max_retries):
            try:
                response = model.generate_content(prompt_parts)
                ai_reply = response.text.strip()
                break # 成功則跳出迴圈
            except ResourceExhausted as e:
                print(f"Gemini API 配額超出，正在重試 ({i+1}/{max_retries})...")
                retry_seconds = 60 # Default retry time
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                if match:
                    retry_seconds = float(match.group(1))
                print(f"等待 {retry_seconds + 1} 秒後重試。")
                time.sleep(retry_seconds + 1) # 等待建議時間 + 1 秒
            except Exception as e:
                raise e # 其他錯誤直接拋出

        if not ai_reply:
            raise Exception("Gemini API 呼叫失敗，即使重試也未能成功。")

        # 5. 解讀 AI 回覆並判斷對錯 (只對畫圖題更新進度)
        is_graph_correct = False
        demote_to_skill_id = None  # 初始化 demote_to_skill_id
        short_feedback = ai_reply.split('\n')[0] if ai_reply else "分析錯誤"
        detailed_feedback = ai_reply if ai_reply else "分析失敗，請重試。"

        if is_graph_question:
            if ai_reply.startswith("CORRECT:"):
                is_graph_correct = True
            elif ai_reply.startswith("INCORRECT:"):
                is_graph_correct = False
                # 確保 detailed_feedback 包含完整回覆
                detailed_feedback = ai_reply
            else:
                is_graph_correct = False
                short_feedback = f"AI 回覆格式錯誤...\n({ai_reply})"
                detailed_feedback = short_feedback

            # --- 更新資料庫進度 (只針對畫圖題) ---
            try:
                skill = Skill.query.filter_by(name=current_skill_id_str).first()
                if skill and user_id:
                    progress = UserProgress.query.filter_by(user_id=user_id, skill_id=skill.id).first()
                    if not progress:
                        progress = UserProgress(user_id=user_id, skill_id=skill.id)
                        db.session.add(progress)
                    progress.total_attempted += 1
                    if is_graph_correct:
                        progress.consecutive_correct += 1
                        progress.total_correct += 1
                        progress.consecutive_incorrect = 0
                    else:
                        progress.consecutive_correct = 0
                        progress.consecutive_incorrect += 1
                        if progress.consecutive_incorrect >= DEMOTION_THRESHOLD and skill.prerequisite_skill_id:
                            demote_to_skill_id = skill.prerequisite_skill_id
                            prereq_skill = Skill.query.filter_by(name=demote_to_skill_id).first()
                            prereq_name = prereq_skill.display_name if prereq_skill else "基礎單元"
                            detailed_feedback += f"\n\n錯誤次數較多，建議您先複習「{prereq_name}」。"
                    db.session.commit()
                    print(f"畫圖題進度已更新: correct={is_graph_correct}, demote={demote_to_skill_id}")
                else:
                    print("警告: 找不到技能或用戶，無法更新畫圖題進度")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating progress: {e}")

    except Exception as e:
        print(f"Gemini API 或圖片處理失敗: {e}")
        is_graph_correct = False
        demote_to_skill_id = None  # 確保在異常情況下也有預設值
        short_feedback = f"分析失敗：{str(e)[:100]}... 請檢查圖片或稍後再試。"
        detailed_feedback = short_feedback

    # 7. 回傳結果給前端
    print(f"回傳給前端: short_feedback='{short_feedback}', detailed_feedback='{detailed_feedback}', is_graph_correct={is_graph_correct}, demote={demote_to_skill_id}")
    return jsonify({
        "short_feedback": short_feedback,  # 左邊紅色區塊顯示
        "reply": detailed_feedback,        # 右邊對話框顯示
        "is_graph_correct": is_graph_correct,
        "demote_to_skill_id": demote_to_skill_id
    })

# ==============================================================================
# 8. Application Runner
# ==============================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 確保所有資料表都建立
        initialize_skills()  # 同步技能列表
    print("Starting Flask app...")
    app.run(debug=True)
