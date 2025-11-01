    # app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # 必須匯入 login_required！
from werkzeug.security import generate_password_hash, check_password_hash
from core.routes import core_bp
from core.ai_analyzer import configure_gemini
from config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME  # 一定要 import！
)
from core.ai_analyzer import configure_gemini
from models import init_db, User
import sqlite3
from core.utils import get_all_active_skills
from config import SECRET_KEY, GEMINI_API_KEY, GEMINI_MODEL_NAME

app = Flask(__name__, template_folder='templates', static_folder='static')

# 載入設定
app.config.update(
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY=SECRET_KEY,
    GEMINI_API_KEY=GEMINI_API_KEY,
    GEMINI_MODEL_NAME=GEMINI_MODEL_NAME
)

# 驗證
if not app.config['GEMINI_API_KEY']:
    raise ValueError("請設定 GEMINI_API_KEY 環境變數！")

# 正確呼叫：兩個參數！（只呼叫一次！）
configure_gemini(
    api_key=app.config['GEMINI_API_KEY'],
    model_name=app.config['GEMINI_MODEL_NAME']
)

# 初始化資料庫
init_db()


# Flask-Login 設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 執行一次即可（加在 app.py 頂部或手動執行）
def init_skills():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills_info (
            skill_id TEXT PRIMARY KEY,
            skill_en_name TEXT NOT NULL,
            skill_ch_name TEXT NOT NULL,
            description TEXT NOT NULL,
            gemini_prompt TEXT NOT NULL,
            consecutive_correct_required INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INTEGER DEFAULT 0
        )
    ''')
    
    # 功文式技能資料（連續答對題數）
    skills = [
        # 餘式定理：連續答對 8 題晉級
        ('remainder', 'Remainder Theorem', '餘式定理', 
         '學習用餘式定理快速求多項式餘數', 
         '分析學生答案：{user_answer}，正確答案：{correct_answer}，如果錯誤，教導餘式定理代入法。', 
         8, True, 1),
        
        # 因式定理：連續答對 10 題晉級
        ('factor_theorem', 'Factor Theorem', '因式定理', 
         '判斷 (x-k) 是否為多項式的因式', 
         '分析學生答案：{user_answer}，正確答案：{correct_answer}，如果錯誤，教導因式定理用法。', 
         10, True, 2),
        
        # 不等式圖解：連續答對 12 題晉級
        ('inequality_graph', 'Inequality Graph', '不等式圖解', 
         '畫出二元一次不等式的可行域區域', 
         '分析學生手寫圖形：題目 {context}，檢查直線位置、陰影區域是否正確，給出具體建議。', 
         12, True, 3)
    ]
    
    c.executemany("INSERT OR IGNORE INTO skills_info VALUES (?, ?, ?, ?, ?, ?, ?, ?)", skills)
    conn.commit()
    conn.close()
    
# 呼叫一次
init_skills()


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1])
    return None

# 註冊 Blueprint    
app.register_blueprint(core_bp)
    
# === 首頁跳轉到 dashboard ===
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# === 登入 ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1]))
            return redirect(url_for('dashboard'))
        flash('帳號或密碼錯誤', 'danger')
    return render_template('login.html')

# === 註冊 ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 4:
            flash('密碼至少 4 個字', 'warning')
            return render_template('register.html')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, generate_password_hash(password)))
            conn.commit()
            flash('註冊成功！請登入', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('帳號已存在', 'warning')
        finally:
            conn.close()
    return render_template('register.html')

# 定義一個裝飾器，專門用在 Blueprint 路由上
def login_required_bp(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated



# === 登出 ===
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('login'))

# === 個人儀表板 ===


@app.route('/dashboard')
@login_required
def dashboard():
    # 直接從 DB 讀取所有技能
    skills = get_all_active_skills()
    
    # 讀取使用者進度
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, consecutive_correct, questions_solved, current_level
        FROM progress 
        WHERE user_id = ?
    ''', (current_user.id,))
    progress_rows = c.fetchall()
    conn.close()
    
    progress_dict = {row[0]: row for row in progress_rows}
    
    dashboard_data = []
    for skill in skills:
        prog = progress_dict.get(skill['skill_id'], (skill['skill_id'], 0, 0, 1))
        dashboard_data.append({
            'skill': skill,
            'consecutive_correct': prog[1],
            'questions_solved': prog[2],
            'current_level': prog[3]
        })
    
    return render_template('dashboard.html', 
                         dashboard_data=dashboard_data, 
                         username=current_user.username)

# === 練習頁面（需登入）===
@app.route('/practice/<skill_id>')
@login_required
def practice(skill_id):
    return render_template('index.html', skill_id=skill_id)  # 傳 skill_id 進去！

if __name__ == '__main__':
    app.run(debug=True, port=5000)