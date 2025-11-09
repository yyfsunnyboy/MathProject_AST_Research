# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .session import set_current, get_current
from .ai_analyzer import analyze, ask_ai_text_with_context, get_model
from flask import session # 導入 session
import importlib, os
from core.utils import get_skill_info
from models import db, Progress, SkillInfo, SkillCurriculum, SkillPrerequisites # 導入 SkillPrerequisites
from sqlalchemy.orm import aliased
import traceback

core_bp = Blueprint('core', __name__)

# 所有 core 路由都需要登入
@core_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

def get_skill(skill_id):
    try:
        return importlib.import_module(f"skills.{skill_id}")
    except:
        return None

def update_progress(user_id, skill_id, is_correct):
    """
    更新用戶進度（功文式教育理論）
    核心精神：在學生感到舒適的難度下進行大量練習，達到精熟後才晉級。若遇到困難，則退回一個等級鞏固基礎，避免挫折感。
    **新邏輯**：由於題目難度已由課綱靜態決定，此函式不再處理升降級，僅記錄練習次數與連續答對/錯次數。
    """
    # 使用 ORM 查詢進度記錄
    progress = db.session.query(Progress).filter_by(user_id=user_id, skill_id=skill_id).first()

    if not progress:
        # 如果沒有記錄，建立新的 Progress 物件
        progress = Progress(
            user_id=user_id,
            skill_id=skill_id,
            consecutive_correct=1 if is_correct else 0,
            consecutive_wrong=0 if is_correct else 1,
            questions_solved=1,
            current_level=1 # 此欄位已不再用於決定題目難度，僅為保留欄位
        )
        db.session.add(progress)
    else:
        # 如果有記錄，更新現有物件
        progress.questions_solved += 1
        
        # 讀取技能的晉級/降級門檻
        skill_info = db.session.get(SkillInfo, skill_id)
        required = skill_info.consecutive_correct_required if skill_info else 10
        
        # 更新連續答對/錯次數
        if is_correct:
            progress.consecutive_correct += 1
            progress.consecutive_wrong = 0 # 答對，連續錯誤歸零
        else:
            progress.consecutive_correct = 0 # 只要錯了，連續答對就中斷
            progress.consecutive_wrong += 1
    
    # 提交變更到資料庫
    db.session.commit()

@core_bp.route('/admin/batch_import_skills', methods=['POST'])
@login_required
def batch_import_skills():
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "Permission denied."}), 403
    
    try:
        # This is where your actual import logic is called.
        # I am assuming it's in a module named 'data_importer'.
        # Please adjust this to match your code.
        from . import data_importer 
        count = data_importer.import_skills_from_json()
        
        # If successful, return a success message
        return jsonify({"success": True, "message": f"成功匯入 {count} 個技能單元！"})

    except Exception as e:
        # This block will catch ANY error that occurs during the import
        
        # 1. Log the full, detailed error to your server console for debugging
        error_details = traceback.format_exc()
        current_app.logger.error(f"Batch import skills failed: {e}\n{error_details}")
        
        # 2. Return a clear error message to the frontend page
        return jsonify({
            "success": False, 
            "message": f"批次匯入技能失敗！\n\n錯誤原因：\n{str(e)}\n\n請檢查伺服器日誌以獲取詳細資訊。"
        }), 500

# Find your existing function for importing the curriculum and modify it similarly
@core_bp.route('/admin/batch_import_curriculum', methods=['POST'])
@login_required
def batch_import_curriculum():
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "Permission denied."}), 403

    try:
        # Adjust this to match your code
        from . import data_importer
        count = data_importer.import_curriculum_from_json()
        
        return jsonify({"success": True, "message": f"成功匯入 {count} 個課程綱要項目！"})

    except Exception as e:
        # Catch and report any errors
        error_details = traceback.format_exc()
        current_app.logger.error(f"Batch import curriculum failed: {e}\n{error_details}")
        
        return jsonify({
            "success": False, 
            "message": f"批次匯入課程綱要失敗！\n\n錯誤原因：\n{str(e)}\n\n請檢查伺服器日誌以獲取詳細資訊。"
        }), 500


@core_bp.route('/get_next_question')
def next_question():
    skill_id = request.args.get('skill', 'remainder')
    
    # 從 DB 驗證 skill 是否存在
    skill_info = get_skill_info(skill_id)
    if not skill_info:
        return jsonify({"error": f"技能 {skill_id} 不存在或未啟用"}), 404
    
    try:
        mod = importlib.import_module(f"skills.{skill_id}")
        
        # === 核心邏輯修改：根據課綱決定題目難度 ===
        # 1. 從 session 讀取使用者當前的課綱情境
        current_curriculum_context = session.get('current_curriculum', 'general') # 若無情境，預設為 'general'

        # 2. 查詢 skill_curriculum 表以取得指定的 difficulty_level
        curriculum_entry = db.session.query(SkillCurriculum).filter_by(
            skill_id=skill_id,
            curriculum=current_curriculum_context
        ).first()

        # 3. 決定要使用的難度等級
        if curriculum_entry and curriculum_entry.difficulty_level:
            difficulty_level = curriculum_entry.difficulty_level
        else:
            difficulty_level = 1 # 如果在課綱中找不到特定設定，預設為等級 1

        # 讀取使用者進度，僅用於顯示，不再用於決定題目難度
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, skill_id=skill_id).first()
        consecutive = progress.consecutive_correct if progress else 0

        data = mod.generate(level=difficulty_level) # 將從課綱查到的 difficulty_level 傳入 generate 函數
        
        # 加入 context_string 給 AI
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        set_current(skill_id, data)
        
        return jsonify({
            "new_question_text": data["question_text"],
            "context_string": data.get("context_string", ""),
            "inequality_string": data.get("inequality_string", ""),
            "consecutive_correct": consecutive, # 連續答對
            "current_level": difficulty_level, # 顯示的等級應為當前題目的等級
            "answer_type": skill_info.get("input_type", "text") # 從 DB 讀取作答類型
        })
    except Exception as e:
        return jsonify({"error": f"生成題目失敗: {str(e)}"}), 500

@core_bp.route('/check_answer', methods=['POST'])
def check_answer():
    user = request.json.get('answer', '').strip()
    current = get_current()
    skill = current['skill']
    correct_answer = current['correct_answer']

    mod = get_skill(skill)
    if not mod:
        return jsonify({"correct": False, "result": "單元錯誤"})

    # 圖形題：不批改，直接提示用 AI
    if correct_answer == "graph":
        return jsonify({
            "correct": False,
            "result": "請畫完可行域後，點「AI 檢查」",
            "next_question": False
        })

    # 文字題：正常批改
    result = mod.check(user, current['answer'])
    
    # 安全地獲取批改結果，避免 KeyError
    is_correct = result.get('correct', False)
    if not isinstance(is_correct, bool):
        is_correct = False

    # 更新進度
    update_progress(current_user.id, skill, is_correct)
    
    return jsonify(result)

@core_bp.route('/analyze_handwriting', methods=['POST'])
def analyze_handwriting():
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: 
        return jsonify({"reply": "缺少圖片"}), 400
    
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    result = analyze(img, state['question'], api_key)
    
    # 更新進度
    if result.get('correct') or result.get('is_process_correct'):
        update_progress(current_user.id, state['skill'], True)
    else:
        update_progress(current_user.id, state['skill'], False)
    
    return jsonify(result)

@core_bp.route('/chat_ai', methods=['POST'])
def chat_ai():
    data = request.get_json()
    user_question = data.get('question', '').strip()
    context = data.get('context', '')
    question_text = data.get('question_text', '')  # 接收完整題目文字

    if not user_question:
        return jsonify({"reply": "請輸入問題！"}), 400

    # 安全取得當前題目
    current = get_current()
    skill_id = current.get("skill")
    
    # 優先使用傳入的題目文字，否則使用 session 中的，最後使用 context
    if question_text:
        full_question_context = question_text
    elif current.get("question"):
        full_question_context = current.get("question")
    else:
        full_question_context = context or "（無題目資訊）"
    
    # 如果 session 沒資料，從 context 猜測 skill
    if not skill_id:
        if any(kw in context for kw in ['餘式', 'remainder', 'f(x)', '除']):
            skill_id = 'remainder'
        elif any(kw in context for kw in ['因式', 'factor', '(x -', '是否為']):
            skill_id = 'factor_theorem'
        elif any(kw in context for kw in ['不等式', 'inequality', '可行域', '≥', '≤']):
            skill_id = 'inequality_graph'
        else:
            skill_id = 'remainder'

    # 從 DB 讀取 prompt 模板
    skill_info = get_skill_info(skill_id)
    if not skill_info:
        return jsonify({"reply": "技能未找到"}), 404

    # 動態替換 prompt，加入完整題目資訊
    prompt_template = skill_info['gemini_prompt']
    try:
        # 構建包含完整題目的提示
        enhanced_context = f"當前題目：{full_question_context}"
        if context and context != full_question_context:
            enhanced_context += f"\n詳細資訊：{context}"
        
        full_prompt = prompt_template.format(
            user_answer=user_question,
            correct_answer="（待批改）",
            context=enhanced_context
        )
        
        # 在提示開頭明確加入題目資訊，讓 AI 知道學生正在問哪一題
        full_prompt = f"【學生當前正在練習的題目】\n{full_question_context}\n\n" + full_prompt
        
    except KeyError as e:
        full_prompt = f"【學生當前正在練習的題目】\n{full_question_context}\n\n學生問：{user_question}\n（提示模板有誤：{e}）"

    try:
        model = get_model()
        resp = model.generate_content(full_prompt)
        reply = resp.text.strip()
        
        # 強制加鼓勵話（避免 AI 太冷）
        if not any(word in reply for word in ['加油', '試試', '可以的', '棒']):
            reply += "\n\n試試看，你一定可以的！加油～"
            
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[CHAT_AI ERROR] {e}")
        return jsonify({"reply": "AI 暫時無法回應，請稍後再試！"}), 500

# === API 路由：用於連動式下拉選單 ===
# 這些路由註冊在 core_bp 上，會自動受到 before_request 的登入保護
@core_bp.route('/api/curriculum/grades')
def api_get_grades():
    curriculum = request.args.get('curriculum')
    if not curriculum:
        return jsonify([])
    grades = db.session.query(SkillCurriculum.grade).filter_by(curriculum=curriculum).distinct().order_by(SkillCurriculum.grade).all()
    return jsonify([g[0] for g in grades])

@core_bp.route('/api/curriculum/volumes')
def api_get_volumes():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    if not curriculum or not grade:
        return jsonify([])
    volumes = db.session.query(SkillCurriculum.volume).filter_by(curriculum=curriculum, grade=int(grade)).distinct().order_by(SkillCurriculum.volume).all()
    return jsonify([v[0] for v in volumes])

@core_bp.route('/api/curriculum/chapters')
def api_get_chapters():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    if not curriculum or not grade or not volume:
        return jsonify([])
    chapters = db.session.query(SkillCurriculum.chapter).filter_by(
        curriculum=curriculum, 
        grade=int(grade),
        volume=volume
    ).distinct().order_by(SkillCurriculum.chapter).all()
    return jsonify([c[0] for c in chapters])

@core_bp.route('/api/curriculum/sections')
def api_get_sections():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    if not all([curriculum, grade, volume, chapter]):
        return jsonify([])
    sections = db.session.query(SkillCurriculum.section).filter_by(
        curriculum=curriculum, 
        grade=int(grade),
        volume=volume,
        chapter=chapter
    ).distinct().order_by(SkillCurriculum.section).all()
    return jsonify([s[0] for s in sections])

# === 檢查幽靈技能 API ===
@core_bp.route('/admin/skills/check_ghosts')
def check_ghost_skills():
    if not current_user.is_admin: # 確保只有管理員能執行
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 1. 獲取檔案系統中的所有技能檔案
        skills_dir = os.path.join(current_app.root_path, 'skills')
        skill_files = {f.replace('.py', '') for f in os.listdir(skills_dir) 
                       if f.endswith('.py') and f not in ['__init__.py', 'utils.py']}

        # 2. 獲取資料庫中所有已註冊的 skill_id
        registered_skills_query = db.session.query(SkillInfo.skill_id).all()
        registered_skill_ids = {row[0] for row in registered_skills_query}

        # 3. 找出差異：存在於檔案系統但不存在於資料庫中的檔案
        ghost_files = sorted(list(skill_files - registered_skill_ids))

        return jsonify({"success": True, "ghost_files": ghost_files})
    except Exception as e:
        # 使用 current_app.logger 記錄詳細錯誤
        current_app.logger.error(f"檢查幽靈技能時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": f"檢查時發生錯誤: {str(e)}"}), 500

# === 技能前置依賴管理 ===
@core_bp.route('/admin/prerequisites')
def admin_prerequisites():
    if not current_user.is_admin:
        flash('您沒有權限存取此頁面。', 'danger')
        return redirect(url_for('dashboard'))

    # 為了能同時顯示「目前技能」和「基礎技能」的中文名稱，需要進行 join 操作
    # 建立 SkillInfo 的兩個別名
    CurrentSkill = aliased(SkillInfo)
    PrereqSkill = aliased(SkillInfo)

    # 查詢所有依賴關係，並 join 兩次 SkillInfo 以取得名稱
    prerequisites = db.session.query(
        SkillPrerequisites.id,
        CurrentSkill.skill_ch_name.label('current_skill_name'),
        PrereqSkill.skill_ch_name.label('prereq_skill_name')
    ).join(
        CurrentSkill, SkillPrerequisites.skill_id == CurrentSkill.skill_id
    ).join(
        PrereqSkill, SkillPrerequisites.prerequisite_id == PrereqSkill.skill_id
    ).order_by(CurrentSkill.skill_ch_name, PrereqSkill.skill_ch_name).all()

    # 獲取所有技能列表，用於新增表單的下拉選單
    all_skills = db.session.query(SkillInfo).order_by(SkillInfo.skill_ch_name).all()

    return render_template('admin_prerequisites.html',
                           prerequisites=prerequisites,
                           all_skills=all_skills,
                           username=current_user.username)

@core_bp.route('/admin/prerequisites/add', methods=['POST'])
def admin_add_prerequisite():
    skill_id = request.form.get('skill_id')
    prerequisite_id = request.form.get('prerequisite_id')

    if not skill_id or not prerequisite_id:
        flash('必須同時選擇「目前技能」和「基礎技能」。', 'warning')
    elif skill_id == prerequisite_id:
        flash('技能不能將自己設為前置技能。', 'warning')
    else:
        new_prereq = SkillPrerequisites(skill_id=skill_id, prerequisite_id=prerequisite_id)
        db.session.add(new_prereq)
        db.session.commit()
        flash('前置技能關聯新增成功！', 'success')
    return redirect(url_for('core.admin_prerequisites'))

@core_bp.route('/admin/prerequisites/delete/<int:prereq_id>', methods=['POST'])
def admin_delete_prerequisite(prereq_id):
    prereq = db.get_or_404(SkillPrerequisites, prereq_id)
    db.session.delete(prereq)
    db.session.commit()
    flash('前置技能關聯已刪除。', 'success')
    return redirect(url_for('core.admin_prerequisites'))