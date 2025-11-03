# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from core.routes import core_bp
from core.ai_analyzer import configure_gemini
from config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME
)
from models import init_db, User
import sqlite3
from core.utils import get_all_active_skills

app = Flask(__name__, template_folder='templates', static_folder='static')

# 載入設定
app.config.update(
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY=SECRET_KEY,
    GEMINI_API_KEY=GEMINI_API_KEY,
    GEMINI_MODEL_NAME=GEMINI_MODEL_NAME
)

# 驗證 API Key
if not app.config['GEMINI_API_KEY']:
    raise ValueError("請設定 GEMINI_API_KEY 環境變數！")

# 配置 Gemini（只呼叫一次）
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

# 初始化技能資料
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
    view_mode = request.args.get('view', 'all')  # 'all' 或 'curriculum'
    volume = request.args.get('volume', type=int)
    chapter = request.args.get('chapter', type=int)
    
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
    
    if view_mode == 'curriculum':
        from core.utils import get_volumes, get_chapters_by_volume, get_skills_by_volume_chapter
        
        if volume and chapter:
            # 第三層：顯示該冊該章的所有技能
            skills = get_skills_by_volume_chapter(volume, chapter)

            # 後端分組：按 (section, paragraph)
            section_groups = {}
            for s in skills:
                key = (s['section'], s['paragraph'])
                section_groups.setdefault(key, []).append(s)

            # 組裝帶進度的分組資料
            grouped_skills = []
            for (section, paragraph), skill_list in sorted(section_groups.items()):
                grouped_item = {
                    'section': section,
                    'paragraph': paragraph,
                    'skills': []
                }
                for s in skill_list:
                    prog = progress_dict.get(s['skill_id'], (s['skill_id'], 0, 0, 1))
                    grouped_item['skills'].append({
                        **s,
                        'consecutive_correct': prog[1],
                        'questions_solved': prog[2],
                        'current_level': prog[3],
                    })
                grouped_skills.append(grouped_item)

            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='skills',  # 第三層
                                 volume=volume,
                                 chapter=chapter,
                                 grouped_skills=grouped_skills,
                                 username=current_user.username)
        elif volume:
            # 第二層：顯示該冊的所有章
            chapters = get_chapters_by_volume(volume)
            
            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='chapters',  # 第二層
                                 volume=volume,
                                 chapters=chapters,
                                 username=current_user.username)
        else:
            # 第一層：顯示所有冊
            volumes = get_volumes()
            
            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='volumes',  # 第一層
                                 volumes=volumes,
                                 username=current_user.username)
    else:
        # 顯示所有
        skills = get_all_active_skills()
        
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
                             view_mode='all',
                             username=current_user.username)

# === 練習頁面（需登入）===
@app.route('/practice/<skill_id>')
@login_required
def practice(skill_id):
    return render_template('index.html', skill_id=skill_id)

# === 技能管理頁面 ===
@app.route('/admin/skills')
@login_required
def admin_skills():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, skill_en_name, skill_ch_name, description, 
               gemini_prompt, consecutive_correct_required, is_active, order_index
        FROM skills_info 
        ORDER BY order_index, skill_id
    ''')
    skills = c.fetchall()
    conn.close()
    
    skills_list = [{
        'skill_id': row[0],
        'skill_en_name': row[1],
        'skill_ch_name': row[2],
        'description': row[3],
        'gemini_prompt': row[4],
        'consecutive_correct_required': row[5],
        'is_active': row[6],
        'order_index': row[7]
    } for row in skills]
    
    return render_template('admin_skills.html', skills=skills_list, username=current_user.username)

# === 新增技能 ===
@app.route('/admin/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name, description, 
                                    gemini_prompt, consecutive_correct_required, is_active, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['skill_id'],
            data['skill_en_name'],
            data['skill_ch_name'],
            data['description'],
            data['gemini_prompt'],
            int(data['consecutive_correct_required']),
            1 if data.get('is_active') == 'on' else 0,
            int(data.get('order_index', 999))
        ))
        conn.commit()
        flash('技能新增成功！', 'success')
    except sqlite3.IntegrityError:
        flash('技能 ID 已存在！', 'danger')
    except Exception as e:
        flash(f'新增失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_skills'))

# === 編輯技能 ===
@app.route('/admin/skills/edit/<skill_id>', methods=['POST'])
@login_required
def admin_edit_skill(skill_id):
    data = request.form
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE skills_info 
            SET skill_en_name = ?, skill_ch_name = ?, description = ?, 
                gemini_prompt = ?, consecutive_correct_required = ?, 
                is_active = ?, order_index = ?
            WHERE skill_id = ?
        ''', (
            data['skill_en_name'],
            data['skill_ch_name'],
            data['description'],
            data['gemini_prompt'],
            int(data['consecutive_correct_required']),
            1 if data.get('is_active') == 'on' else 0,
            int(data.get('order_index', 999)),
            skill_id
        ))
        conn.commit()
        flash('技能更新成功！', 'success')
    except Exception as e:
        flash(f'更新失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_skills'))

# === 刪除技能 ===
@app.route('/admin/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        # 檢查是否有使用者正在使用此技能
        c.execute('SELECT COUNT(*) FROM progress WHERE skill_id = ?', (skill_id,))
        count = c.fetchone()[0]
        
        if count > 0:
            flash(f'無法刪除：目前有 {count} 位使用者正在練習此技能！建議改為「停用」', 'warning')
        else:
            c.execute('DELETE FROM skills_info WHERE skill_id = ?', (skill_id,))
            conn.commit()
            flash('技能刪除成功！', 'success')
    except Exception as e:
        flash(f'刪除失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_skills'))

# === 切換啟用狀態 ===
@app.route('/admin/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('SELECT is_active FROM skills_info WHERE skill_id = ?', (skill_id,))
        current = c.fetchone()[0]
        new_status = 0 if current == 1 else 1
        
        c.execute('UPDATE skills_info SET is_active = ? WHERE skill_id = ?', (new_status, skill_id))
        conn.commit()
        flash(f'技能已{"啟用" if new_status == 1 else "停用"}！', 'success')
    except Exception as e:
        flash(f'操作失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_skills'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)