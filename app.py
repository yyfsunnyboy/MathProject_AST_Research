# app.py
import pandas as pd
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import inspect, Table, MetaData
from sqlalchemy.exc import IntegrityError
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
from models import init_db, User, db, Progress, SkillInfo, SkillCurriculum
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

# 1. 先初始化 SQLAlchemy，讓它與 Flask App 關聯
db.init_app(app)

# 2. 在 App 上下文中使用 SQLAlchemy 的 engine 來建立表格
with app.app_context():
    init_db(db.engine)

# Flask-Login 設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # 使用 SQLAlchemy ORM 的方式讀取使用者，更簡潔安全
    return User.query.get(int(user_id))

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
        
        # 使用 ORM 查詢使用者
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
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
            return redirect(url_for('register'))

        # 檢查使用者是否已存在
        if User.query.filter_by(username=username).first():
            flash('帳號已存在', 'warning')
            return redirect(url_for('register'))

        # 使用 ORM 建立新使用者
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('註冊成功！請登入', 'success')
        return redirect(url_for('login'))
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
    view_mode = request.args.get('view', 'curriculum')
    # 預設為 'curriculum' 視圖，並預設選擇 'junior_high' (國中)
    curriculum = request.args.get('curriculum', 'junior_high')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    
    # 使用 SQLAlchemy ORM 讀取使用者進度
    progress_records = Progress.query.filter_by(user_id=current_user.id).all()
    progress_dict = {
        p.skill_id: (p.skill_id, p.consecutive_correct, p.questions_solved, p.current_level)
        for p in progress_records
    }
    
    if view_mode == 'curriculum':
        from core.utils import get_volumes_by_curriculum, get_chapters_by_curriculum_volume, get_skills_by_volume_chapter
        
        if curriculum and volume and chapter:
            # 第四層：顯示技能
            skills_raw = get_skills_by_volume_chapter(volume, chapter)

            # 組裝帶有進度的技能資料
            all_skills_with_progress = []
            for s in skills_raw:
                prog = progress_dict.get(s['skill_id'], (s['skill_id'], 0, 0, 1))
                all_skills_with_progress.append({
                    **s,
                    'consecutive_correct': prog[1],
                    'questions_solved': prog[2],
                    'current_level': prog[3],
                })

            # 修正後的分組邏輯：使用字典來確保每個 section 只有一個群組
            sections_map = {}
            for skill in all_skills_with_progress:
                section_name = skill['section']
                if section_name not in sections_map:
                    # 如果是第一次遇到這個 section，建立一個新的群組
                    sections_map[section_name] = {'section': section_name, 'skills': []}
                # 將技能加入到對應的群組中
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
            # 第三層：顯示章節
            chapters = get_chapters_by_curriculum_volume(curriculum, volume)
            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='chapters',
                                 curriculum=curriculum,
                                 volume=volume,
                                 chapters=chapters,
                                 username=current_user.username)
        elif curriculum:
            # 預設層級：根據課綱顯示冊別
            volumes = get_volumes_by_curriculum(curriculum)

            # === 客製化排序邏輯：僅針對二年級 ===
            # 檢查是否存在二年級 (grade 11) 的資料
            if 11 in volumes:
                # 定義期望的排序順序
                desired_order_g11 = {
                    '數學3A': 0, '數學4A': 1,
                    '數學3B': 2, '數學4B': 3
                }
                # 使用自訂的 key 來排序，找不到的項目排在後面
                volumes[11].sort(key=lambda vol: desired_order_g11.get(vol, 99))

            # === 客製化排序邏輯：僅針對三年級 ===
            # 檢查是否存在三年級 (grade 12) 的資料
            if 12 in volumes:
                # 定義期望的排序順序
                desired_order = {
                    '數學甲(上)': 0, '數學甲(下)': 1,
                    '數學乙(上)': 2, '數學乙(下)': 3
                }
                # 使用自訂的 key 來排序，找不到的項目排在後面
                volumes[12].sort(key=lambda vol: desired_order.get(vol, 99))

            # 根據課綱決定年級的顯示名稱
            if curriculum == 'junior_high':
                grade_map = {
                    7: '七年級', 8: '八年級', 9: '九年級'
                }
            else: # 預設為普高/技高
                grade_map = {
                    10: '一年級', 11: '二年級', 12: '三年級'
                }

            return render_template('dashboard.html',
                                 view_mode='curriculum',
                                 level='volumes', # 直接顯示冊別
                                 curriculum=curriculum,
                                 volumes=volumes,
                                 grade_map=grade_map,
                                 username=current_user.username)
    else:
        # === 顯示所有 (分類檢視) ===
        selected_category = request.args.get('category')

        if selected_category:
            # 第二層：顯示特定分類下的所有技能
            skills = SkillInfo.query.filter_by(is_active=True, category=selected_category).order_by(SkillInfo.order_index).all()
            
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
            # 第一層：顯示所有技能分類
            
            # 1. 建立理想的排序順序：從「普高」課程中查詢類別的出現順序
            ordered_categories_query = db.session.query(SkillInfo.category)\
                .join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id)\
                .filter(SkillCurriculum.curriculum == 'general', SkillInfo.is_active == True)\
                .order_by(SkillCurriculum.grade, SkillCurriculum.display_order)\
                .all()
            
            # 建立一個帶有順序的唯一類別列表
            desired_order_list = []
            seen_categories = set()
            for row in ordered_categories_query:
                category = row[0]
                if category and category not in seen_categories:
                    desired_order_list.append(category)
                    seen_categories.add(category)
            
            # 2. 獲取所有可用的類別
            all_category_rows = db.session.query(SkillInfo.category).filter(SkillInfo.is_active == True).distinct().all()
            categories = [row[0] for row in all_category_rows if row[0]]
            
            # 3. 根據理想順序進行排序
            order_map = {category: index for index, category in enumerate(desired_order_list)}
            categories.sort(key=lambda cat: order_map.get(cat, 999)) # 找不到順序的排在後面
            
            return render_template('dashboard.html',
                                 view_mode='all',
                                 level='categories',
                                 categories=categories,
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
    # 使用 ORM 獲取所有技能列表，用於下拉選單
    skills = SkillInfo.query.order_by(SkillInfo.order_index, SkillInfo.skill_id).all()

    # 使用 ORM 讀取現有的課程分類資料，並預先載入關聯的技能資訊以提高效率
    curriculum_items = SkillCurriculum.query.join(SkillInfo).order_by(
        SkillCurriculum.curriculum,
        SkillCurriculum.grade,
        SkillCurriculum.volume,
        SkillCurriculum.chapter,
        SkillCurriculum.section,
        SkillCurriculum.paragraph,
        SkillCurriculum.display_order
    ).all()
    
    return render_template('admin_curriculum.html', 
                           username=current_user.username,
                           skills=skills,
                           curriculum_items=curriculum_items) # 變數名改為 curriculum_items 避免與迴圈變數衝突

# === 新增課程分類 ===
@app.route('/admin/curriculum/add', methods=['POST'])
@login_required
def admin_add_curriculum():
    data = request.form
    try:
        new_item = SkillCurriculum(
            curriculum=data['curriculum'],
            grade=int(data['grade']),
            volume=data['volume'],
            chapter=data['chapter'],
            section=data['section'],
            paragraph=data.get('paragraph').strip() or None,
            skill_id=data['skill_id'],
            display_order=int(data.get('display_order', 0)),
            difficulty_level=int(data.get('difficulty_level', 1))
        )
        db.session.add(new_item)
        db.session.commit()
        flash('課程分類新增成功！', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('新增失敗：該課程分類項目已存在（唯一性約束衝突）。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('admin_curriculum'))

# === 編輯課程分類 ===
@app.route('/admin/curriculum/edit/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_edit_curriculum(curriculum_id):
    item = SkillCurriculum.query.get_or_404(curriculum_id)
    data = request.form
    try:
        item.curriculum = data['curriculum']
        item.grade = int(data['grade'])
        item.volume = data['volume']
        item.chapter = data['chapter']
        item.section = data['section']
        item.paragraph = data.get('paragraph').strip() or None
        item.skill_id = data['skill_id']
        item.display_order = int(data.get('display_order', 0))
        item.difficulty_level = int(data.get('difficulty_level', 1))
        
        db.session.commit()
        flash('課程分類更新成功！', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('更新失敗：該課程分類項目已存在（唯一性約束衝突）。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗：{str(e)}', 'danger')
    return redirect(url_for('admin_curriculum'))

# === 刪除課程分類 ===
@app.route('/admin/curriculum/delete/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_delete_curriculum(curriculum_id):
    item = SkillCurriculum.query.get_or_404(curriculum_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('課程分類刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('admin_curriculum'))

# === 技能管理頁面 ===
@app.route('/admin/skills')
@login_required
def admin_skills():
    # 使用 ORM 查詢所有技能，並排序
    skills = SkillInfo.query.order_by(SkillInfo.order_index, SkillInfo.skill_id).all()
    return render_template('admin_skills.html', skills=skills, username=current_user.username)

# === 新增技能 ===
@app.route('/admin/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    
    # 檢查技能 ID 是否已存在
    if SkillInfo.query.get(data['skill_id']):
        flash('技能 ID 已存在！', 'danger')
        return redirect(url_for('admin_skills'))

    try:
        # 建立新的 SkillInfo 物件
        new_skill = SkillInfo(
            skill_id=data['skill_id'],
            skill_en_name=data['skill_en_name'],
            skill_ch_name=data['skill_ch_name'],
            category=data['category'],
            description=data['description'],
            input_type=data.get('input_type', 'text'),
            gemini_prompt=data['gemini_prompt'],
            consecutive_correct_required=int(data['consecutive_correct_required']),
            is_active=data.get('is_active') == 'on', # 直接轉換為布林值
            order_index=int(data.get('order_index', 999))
        )
        db.session.add(new_skill)
        db.session.commit()
        flash('技能新增成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')

    return redirect(url_for('admin_skills'))

# === 編輯技能 ===
@app.route('/admin/skills/edit/<skill_id>', methods=['POST'])
@login_required
def admin_edit_skill(skill_id):
    skill = SkillInfo.query.get_or_404(skill_id)
    data = request.form
    
    try:
        skill.skill_en_name = data['skill_en_name']
        skill.skill_ch_name = data['skill_ch_name']
        skill.category = data['category']
        skill.description = data['description']
        skill.input_type = data.get('input_type', 'text')
        skill.gemini_prompt = data['gemini_prompt']
        skill.consecutive_correct_required = int(data['consecutive_correct_required'])
        skill.is_active = data.get('is_active') == 'on'
        skill.order_index = int(data.get('order_index', 999))
        
        db.session.commit()
        flash('技能更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗：{str(e)}', 'danger')

    return redirect(url_for('admin_skills'))

# === 刪除技能 ===
@app.route('/admin/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = SkillInfo.query.get_or_404(skill_id)
    
    try:
        # 使用 ORM 檢查是否有使用者正在使用此技能
        count = Progress.query.filter_by(skill_id=skill_id).count()
        
        if count > 0:
            flash(f'無法刪除：目前有 {count} 位使用者正在練習此技能！建議改為「停用」', 'warning')
        else:
            # 因為我們在 SkillCurriculum 模型中設定了 ondelete='CASCADE'
            # 所以刪除 SkillInfo 時，相關的課程綱要也會自動刪除
            db.session.delete(skill)
            db.session.commit()
            flash('技能刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')

    return redirect(url_for('admin_skills'))

# === 切換啟用狀態 ===
@app.route('/admin/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    skill = SkillInfo.query.get_or_404(skill_id)
    try:
        skill.is_active = not skill.is_active
        db.session.commit()
        flash(f'技能已{"啟用" if skill.is_active else "停用"}！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'操作失敗：{str(e)}', 'danger')

    return redirect(url_for('admin_skills'))

# === 資料庫管理頁面 ===
@app.route('/admin/db_maintenance', methods=['GET', 'POST'])
@login_required
def db_maintenance():
    # 建議加上管理員權限檢查
    # if not current_user.is_admin:
    #     flash('您沒有權限存取此頁面。', 'danger')
    #     return redirect(url_for('dashboard'))

    inspector = inspect(db.engine)
    table_names = sorted(inspector.get_table_names())

    if request.method == 'POST':
        action = request.form.get('action')
        
        # 如果是針對特定表格的操作，才需要檢查 table_name
        if action in ['drop_table', 'clear_data', 'upload_excel']:
            table_name = request.form.get('table_name')
            if not table_name or table_name not in table_names:
                flash(f'表格 "{table_name}" 不存在。', 'danger')
                return redirect(url_for('db_maintenance'))
        else:
            # 對於 replace_curriculum_data 等操作，table_name 不是必需的
            table_name = None

        conn = None # 初始化 conn
        try:
            if action == 'drop_table':
                # 使用 SQLAlchemy 的 MetaData 來安全地處理 drop
                meta = MetaData()
                meta.reflect(bind=db.engine)
                table_to_drop = meta.tables.get(table_name)
                if table_to_drop is not None:
                    table_to_drop.drop(db.engine)
                    flash(f'表格 "{table_name}" 已成功刪除。', 'success')
                else:
                    flash(f'找不到要刪除的表格 "{table_name}"。', 'warning')

            elif action == 'clear_data':
                conn = db.engine.raw_connection()
                cursor = conn.cursor()
                cursor.execute(f'DELETE FROM {table_name}')
                conn.commit()
                flash(f'表格 "{table_name}" 的所有資料已清除。', 'success')

            elif action == 'upload_excel':
                file = request.files.get('file')
                if not file or file.filename == '':
                    flash('沒有選擇檔案。', 'warning')
                    return redirect(url_for('db_maintenance'))

                df = pd.read_excel(file)
                # 將 NaN 替換為 None 以符合資料庫要求
                df = df.where(pd.notnull(df), None)
                
                # 使用 pandas 的 to_sql 功能寫入資料庫
                df.to_sql(table_name, db.engine, if_exists='append', index=False)
                flash(f'已成功從 Excel 將 {len(df)} 筆記錄新增至表格 "{table_name}"。', 'success')

            elif action == 'replace_curriculum_data':
                volume_name = request.form.get('volume_name')
                file = request.files.get('file')

                if not volume_name or not file or file.filename == '':
                    flash('冊別名稱和檔案皆為必填項目。', 'warning')
                    return redirect(url_for('db_maintenance'))

                # 在 Flask-SQLAlchemy 自動管理的交易中執行操作
                # 1. 刪除該冊別的舊資料
                deleted_count = SkillCurriculum.query.filter_by(volume=volume_name).delete(synchronize_session=False)
                
                # 2. 讀取新檔案並準備插入
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                df.columns = [str(col).lower().strip() for col in df.columns]
                if 'diffcult_level' in df.columns:
                    df.rename(columns={'diffcult_level': 'difficulty_level'}, inplace=True)
                df['paragraph'] = df['paragraph'].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None)
                
                # 3. 使用 ORM 進行批次插入
                records_to_insert = df.to_dict(orient='records')
                db.session.bulk_insert_mappings(SkillCurriculum, records_to_insert)
                db.session.commit() # 手動提交交易
                flash(f'成功替換資料！冊別「{volume_name}」的 {deleted_count} 筆舊資料已被刪除，並從檔案新增了 {len(records_to_insert)} 筆新資料。', 'success')

            elif action == 'upsert_skills_info':
                file = request.files.get('file')
                if not file or file.filename == '':
                    flash('沒有選擇檔案。', 'warning')
                    return redirect(url_for('db_maintenance'))

                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                df.columns = [str(col).lower().strip() for col in df.columns]
                
                # 1. 從上傳的檔案中獲取所有 skill_id
                incoming_skill_ids = {str(sid).strip() for sid in df['skill_id'].unique()}

                # 2. 一次性查詢資料庫中已存在的技能
                existing_skills = SkillInfo.query.filter(SkillInfo.skill_id.in_(incoming_skill_ids)).all()
                existing_skills_map = {skill.skill_id: skill for skill in existing_skills}

                records_to_update = []
                records_to_insert = []

                # 3. 遍歷上傳的資料，分類為「待更新」或「待新增」
                for record in df.to_dict(orient='records'):
                    skill_id = str(record['skill_id']).strip()
                    skill_data = {
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
                    if skill_id in existing_skills_map:
                        records_to_update.append(skill_data)
                    else:
                        records_to_insert.append(skill_data)
                
                # 4. 批次執行更新和新增
                if records_to_update:
                    db.session.bulk_update_mappings(SkillInfo, records_to_update)
                if records_to_insert:
                    db.session.bulk_insert_mappings(SkillInfo, records_to_insert)
                
                db.session.commit()
                flash(f'技能單元資料處理完成！新增 {len(records_to_insert)} 筆，更新 {len(records_to_update)} 筆。', 'success')

        except Exception as e:
            # 使用 SQLAlchemy 的 session 來回滾，而不是舊的 conn 物件
            db.session.rollback()
            flash(f'操作失敗：{e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('db_maintenance'))

    return render_template('db_maintenance.html', tables=table_names)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
