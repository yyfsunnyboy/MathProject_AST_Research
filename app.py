# app.py
import pandas as pd
from sqlalchemy.orm import aliased
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import inspect, Table, MetaData, text
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
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
from models import init_db, User, db, Progress, SkillInfo, SkillCurriculum, SkillPrerequisites
from core.utils import get_all_active_skills

def _prepare_skill_data_from_record(record):
    """從字典記錄中準備並清理 SkillInfo 的資料。"""
    skill_id = str(record['skill_id']).strip()
    return {
        'skill_id': skill_id,
        'skill_en_name': record.get('skill_en_name'),
        'skill_ch_name': record.get('skill_ch_name'),
        'category': record.get('category'),
        'description': record.get('description'),
        'input_type': record.get('input_type', 'text'),
        'gemini_prompt': record.get('gemini_prompt'),
        'consecutive_correct_required': int(record.get('consecutive_correct_required', 10)),
        'is_active': str(record.get('is_active', 'true')).lower() == 'true',
        'order_index': int(record.get('order_index', 999))
    }

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # 載入設定
    app.config.update(
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=SQLALCHEMY_TRACK_MODIFICATIONS,
        SECRET_KEY=SECRET_KEY,
        GEMINI_API_KEY=GEMINI_API_KEY,
        GEMINI_MODEL_NAME=GEMINI_MODEL_NAME
        ,SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {"timeout": 30}  # 增加等待解鎖的時間到 30 秒
        }
    )    

    # 驗證 API Key
    if not app.config['GEMINI_API_KEY']:
        raise ValueError("請設定 GEMINI_API_KEY 環境變數！")

    # 初始化擴充套件
    db.init_app(app)
    login_manager.init_app(app)

    # 註冊藍圖
    from core.routes import practice_bp # 導入新的 blueprint
    app.register_blueprint(core_bp, url_prefix='/admin')
    app.register_blueprint(practice_bp) # 註冊練習用的 blueprint，沒有前綴

    # === 路由定義 ===
    # 將所有路由定義移至工廠函式內部

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'student') # 獲取身分，預設為學生
            
            user = db.session.query(User).filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                # 檢查身分是否相符
                if user.role != role:
                    flash(f'身分錯誤！此帳號為「{user.role}」帳號，請切換身分後再試。', 'warning')
                    return redirect(url_for('login'))

                login_user(user)
                
                # 根據身分導向不同頁面
                if user.role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            flash('帳號或密碼錯誤', 'danger')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'student') # 獲取身分

            if len(password) < 4:
                flash('密碼至少 4 個字', 'warning')
                return redirect(url_for('register'))

            if db.session.query(User).filter_by(username=username).first():
                flash('帳號已存在', 'warning')
                return redirect(url_for('register'))

            new_user = User(
                username=username,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                role=role # 儲存身分
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f'註冊成功！身分：{role}。請登入', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('已登出', 'info')
        return redirect(url_for('login'))

    @app.route('/teacher_dashboard')
    @login_required
    def teacher_dashboard():
        if current_user.role != 'teacher':
            flash('權限不足，無法存取教師頁面', 'warning')
            return redirect(url_for('dashboard'))
        return render_template('teacher_dashboard.html', username=current_user.username)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # --- 修改點：允許教師訪問學生儀表板 ---
        # 原本會將教師重導向，現在註解掉此邏輯，讓教師可以查看學生介面。
        # if current_user.role == 'teacher':
        #     return redirect(url_for('teacher_dashboard'))

        view_mode = request.args.get('view', 'curriculum')
        curriculum = request.args.get('curriculum', 'junior_high')
        volume = request.args.get('volume')
        chapter = request.args.get('chapter')
        
        progress_records = db.session.query(Progress).filter_by(user_id=current_user.id).all()
        progress_dict = {
            p.skill_id: (p.skill_id, p.consecutive_correct, p.questions_solved, p.current_level)
            for p in progress_records
        }
        
        if view_mode == 'curriculum':
            from core.utils import get_volumes_by_curriculum, get_chapters_by_curriculum_volume, get_skills_by_volume_chapter
            
            if curriculum:
                session['current_curriculum'] = curriculum

            if curriculum and volume and chapter:
                skills_raw = get_skills_by_volume_chapter(volume, chapter)

                all_skills_with_progress = []
                for s in skills_raw:
                    prog = progress_dict.get(s['skill_id'], (s['skill_id'], 0, 0, 1))
                    all_skills_with_progress.append({
                        **s,
                        'consecutive_correct': prog[1],
                        'questions_solved': prog[2],
                        'current_level': prog[3],
                    })

                sections_map = {}
                for skill in all_skills_with_progress:
                    section_name = skill['section']
                    if section_name not in sections_map:
                        sections_map[section_name] = {'section': section_name, 'skills': []}
                    sections_map[section_name]['skills'].append(skill)
                
                grouped_sections = list(sections_map.values())

                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='skills',
                                     curriculum=curriculum,
                                     volume=volume,
                                     chapter=chapter,
                                     grouped_sections=grouped_sections,
                                     username=current_user.username)
            elif curriculum and volume:
                chapters = get_chapters_by_curriculum_volume(curriculum, volume)
                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='chapters',
                                     curriculum=curriculum,
                                     volume=volume,
                                     chapters=chapters,
                                     username=current_user.username)
            elif curriculum:
                volumes = get_volumes_by_curriculum(curriculum)

                # 新增：針對國中冊別的排序邏輯
                if curriculum == 'junior_high':
                    desired_order_jh = {
                        '數學1上': 0, '數學1下': 1, '數學2上': 2, '數學2下': 3, '數學3上': 4, '數學3下': 5
                    }
                    for grade in volumes:
                        volumes[grade].sort(key=lambda vol: desired_order_jh.get(vol, 99))

                if 11 in volumes:
                    desired_order_g11 = {
                        '數學3A': 0, '數學4A': 1,
                        '數學3B': 2, '數學4B': 3
                    }
                    volumes[11].sort(key=lambda vol: desired_order_g11.get(vol, 99))

                if 12 in volumes:
                    desired_order = {
                        '數學甲(上)': 0, '數學甲(下)': 1,
                        '數學乙(上)': 2, '數學乙(下)': 3
                    }
                    volumes[12].sort(key=lambda vol: desired_order.get(vol, 99))

                if curriculum == 'junior_high':
                    grade_map = {
                        7: '七年級', 8: '八年級', 9: '九年級'
                    }
                else:
                    grade_map = {
                        10: '一年級', 11: '二年級', 12: '三年級'
                    }

                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='volumes',
                                     curriculum=curriculum,
                                     volumes=volumes,
                                     grade_map=grade_map,
                                     username=current_user.username)
        else:
            selected_category = request.args.get('category')

            if selected_category:
                skills = db.session.query(SkillInfo).filter_by(is_active=True, category=selected_category).order_by(SkillInfo.order_index).all()
                
                dashboard_data = []
                for skill in skills:
                    prog = progress_dict.get(skill.skill_id, (skill.skill_id, 0, 0, 1))
                    dashboard_data.append({
                        'skill': skill,
                        'consecutive_correct': prog[1],
                        'questions_solved': prog[2],
                        'current_level': prog[3]
                    })
                
                return render_template('dashboard.html', 
                                     dashboard_data=dashboard_data,
                                     view_mode='all',
                                     level='skills_in_category',
                                     category=selected_category,
                                     username=current_user.username)
            else:
                ordered_categories_query = db.session.query(SkillInfo.category)\
                    .join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id)\
                    .filter(SkillCurriculum.curriculum == 'general', SkillInfo.is_active == True)\
                    .order_by(SkillCurriculum.grade, SkillCurriculum.display_order)\
                    .all()
                
                desired_order_list = []
                seen_categories = set()
                for row in ordered_categories_query:
                    category = row[0]
                    if category and category not in seen_categories:
                        desired_order_list.append(category)
                        seen_categories.add(category)
                
                all_category_rows = db.session.query(SkillInfo.category).filter(SkillInfo.is_active == True).distinct().all()
                categories = [row[0] for row in all_category_rows if row[0]]
                
                order_map = {category: index for index, category in enumerate(desired_order_list)}
                categories.sort(key=lambda cat: order_map.get(cat, 999))
                
                return render_template('dashboard.html',
                                     view_mode='all',
                                     level='categories',
                                     categories=categories,
                                     username=current_user.username)

    with app.app_context():
        init_db(db.engine)
        # 啟用 WAL (Write-Ahead Logging) 模式以提高併發性並減少鎖定
        try:
            with db.engine.connect() as conn:
                # 啟用 WAL 模式，允許讀取和寫入並行
                conn.execute(text("PRAGMA journal_mode=WAL"))
                # 設定同步等級為 NORMAL，在 WAL 模式下是安全且高效的選擇
                conn.execute(text("PRAGMA synchronous=NORMAL"))
        except Exception as e:
            app.logger.error(f"Failed to set WAL mode for SQLite: {e}")

        configure_gemini(
            api_key=app.config['GEMINI_API_KEY'],
            model_name=app.config['GEMINI_MODEL_NAME']
        )

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
