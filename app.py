# app.py
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

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
            skills_raw = get_skills_by_volume_chapter(volume, chapter)

            # 組裝帶進度的扁平化技能資料
            all_skills_with_progress = []
            for s in skills_raw:
                prog = progress_dict.get(s['skill_id'], (s['skill_id'], 0, 0, 1))
                all_skills_with_progress.append({
                    **s,
                    'consecutive_correct': prog[1],
                    'questions_solved': prog[2],
                    'current_level': prog[3],
                })

            # 重新分組：按節分組技能，同一節的所有段的技能都放在一起
            grouped_sections = []
            current_section = None
            current_skills = []
            section_paragraphs = set()  # 記錄該節包含的所有段

            for skill in all_skills_with_progress:
                if skill['section'] != current_section:
                    # 保存前一個section的數據
                    if current_section is not None:
                        sorted_paras = sorted(section_paragraphs)
                        para_str = '、'.join(map(str, sorted_paras)) if len(sorted_paras) > 1 else str(sorted_paras[0]) if sorted_paras else ''
                        grouped_sections.append({
                            'section': current_section,
                            'paragraphs': sorted_paras,  # 該節包含的所有段
                            'paragraphs_str': para_str,  # 段落字符串，用於顯示
                            'skills': current_skills.copy()
                        })
                    # 開始新的section
                    current_section = skill['section']
                    current_skills = []
                    section_paragraphs = set()
                
                current_skills.append(skill)
                section_paragraphs.add(skill['paragraph'])
            
            # 添加最後一個section
            if current_section is not None:
                sorted_paras = sorted(section_paragraphs)
                para_str = '、'.join(map(str, sorted_paras)) if len(sorted_paras) > 1 else str(sorted_paras[0]) if sorted_paras else ''
                grouped_sections.append({
                    'section': current_section,
                    'paragraphs': sorted_paras,  # 該節包含的所有段
                    'paragraphs_str': para_str,  # 段落字符串，用於顯示
                    'skills': current_skills.copy()
                })

            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='skills',  # 第三層
                                 volume=volume,
                                 chapter=chapter,
                                 grouped_sections=grouped_sections, # 傳遞按節/段分組的數據
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

# === 課程分類管理頁面 ===
@app.route('/admin/curriculum')
@login_required
def admin_curriculum():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # 獲取所有技能列表，用於下拉選單
    c.execute('''
        SELECT skill_id, skill_ch_name, skill_en_name FROM skills_info ORDER BY order_index, skill_id
    ''')
    skills = [{'skill_id': row[0], 'skill_ch_name': row[1], 'skill_en_name': row[2]} for row in c.fetchall()]

    # 讀取現有的課程分類資料
    c.execute('''
        SELECT sc.id, sc.volume, sc.chapter, sc.section, sc.paragraph, 
               sc.skill_id, sc.display_order, si.skill_ch_name, si.skill_en_name
        FROM skill_curriculum sc
        JOIN skills_info si ON sc.skill_id = si.skill_id
        ORDER BY sc.volume, sc.chapter, sc.section, sc.paragraph, sc.display_order
    ''')
    curriculum_items = [{
        'id': row[0],
        'volume': row[1],
        'chapter': row[2],
        'section': row[3],
        'paragraph': row[4],
        'skill_id': row[5],
        'display_order': row[6],
        'skill_ch_name': row[7],
        'skill_en_name': row[8]
    } for row in c.fetchall()]
    
    conn.close()
    
    return render_template('admin_curriculum.html', 
                           username=current_user.username,
                           skills=skills,
                           curriculum=curriculum_items)

# === 新增課程分類 ===
@app.route('/admin/curriculum/add', methods=['POST'])
@login_required
def admin_add_curriculum():
    data = request.form
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO skill_curriculum (volume, chapter, section, paragraph, skill_id, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            int(data['volume']),
            int(data['chapter']),
            int(data['section']),
            int(data['paragraph']),
            data['skill_id'],
            int(data.get('display_order', 0))
        ))
        conn.commit()
        flash('課程分類新增成功！', 'success')
    except sqlite3.IntegrityError:
        flash('課程分類已存在！', 'danger')
    except Exception as e:
        flash(f'新增失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_curriculum'))

# === 編輯課程分類 ===
@app.route('/admin/curriculum/edit/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_edit_curriculum(curriculum_id):
    data = request.form
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE skill_curriculum 
            SET volume = ?, chapter = ?, section = ?, paragraph = ?, 
                skill_id = ?, display_order = ?
            WHERE id = ?
        ''', (
            int(data['volume']),
            int(data['chapter']),
            int(data['section']),
            int(data['paragraph']),
            data['skill_id'],
            int(data.get('display_order', 0)),
            curriculum_id
        ))
        conn.commit()
        flash('課程分類更新成功！', 'success')
    except Exception as e:
        flash(f'更新失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_curriculum'))

# === 刪除課程分類 ===
@app.route('/admin/curriculum/delete/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_delete_curriculum(curriculum_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM skill_curriculum WHERE id = ?', (curriculum_id,))
        conn.commit()
        flash('課程分類刪除成功！', 'success')
    except Exception as e:
        flash(f'刪除失敗：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_curriculum'))

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
