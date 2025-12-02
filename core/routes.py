# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import traceback
import os
import re
import importlib
import pandas as pd
import google.generativeai as genai
import random
import string
from sqlalchemy.orm import aliased
from flask import session
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum, Progress, Class, ClassStudent, User, ExamAnalysis
from sqlalchemy.exc import IntegrityError
from core.utils import get_skill_info
from core.session import get_current, set_current
from core.ai_analyzer import get_model, analyze
from core.exam_analyzer import analyze_exam_image, save_analysis_result, get_flattened_unit_paths
from werkzeug.utils import secure_filename
import uuid


core_bp = Blueprint('core', __name__, template_folder='../templates')
practice_bp = Blueprint('practice', __name__) # 新增：練習專用的 Blueprint


@core_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

# 練習相關的路由也需要登入
@practice_bp.before_request
@login_required
def practice_require_login():
    pass

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

@core_bp.route('/batch_import_skills', methods=['POST'])
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
@core_bp.route('/batch_import_curriculum', methods=['POST'])
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


@practice_bp.route('/practice/<skill_id>')
@login_required
def practice(skill_id):
    # 查詢當前技能的資訊
    skill_info = db.session.get(SkillInfo, skill_id)
    skill_ch_name = skill_info.skill_ch_name if skill_info else "未知技能"

    # 查詢與此技能相關的前置基礎技能
    # 我們 JOIN SkillPrerequisites 和 SkillInfo 來找到所有 prerequisite_id 對應的技能名稱
    prerequisites = db.session.query(SkillInfo).join(
        SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
    ).filter(
        SkillPrerequisites.skill_id == skill_id,
        SkillInfo.is_active == True  # 只顯示啟用的技能
    ).order_by(SkillInfo.skill_ch_name).all()

    # 將查詢結果轉換為字典列表，方便模板使用
    prereq_skills = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in prerequisites]

    return render_template('index.html', 
                           skill_id=skill_id,
                           skill_ch_name=skill_ch_name,
                           prereq_skills=prereq_skills) # 將前置技能列表傳遞給模板

@practice_bp.route('/get_next_question')
def next_question():
    skill_id = request.args.get('skill', 'remainder')
    requested_level = request.args.get('level', type=int) # 新增：從前端獲取請求的難度等級
    
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
        if requested_level: # 如果前端有明確指定等級，則優先使用
            difficulty_level = requested_level
        elif curriculum_entry and curriculum_entry.difficulty_level: # 否則，使用課綱設定的等級
            difficulty_level = curriculum_entry.difficulty_level
        else:
            difficulty_level = 1 # 如果在課綱中找不到特定設定，預設為等級 1

        # 讀取使用者進度，僅用於顯示，不再用於決定題目難度
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, skill_id=skill_id).first()
        consecutive = progress.consecutive_correct if progress else 0

        # 新增：查詢前置技能，並準備給 AI 的資訊
        prereq_query = db.session.query(SkillInfo).join(
            SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
        ).filter(
            SkillPrerequisites.skill_id == skill_id,
            SkillInfo.is_active == True
        ).order_by(SkillInfo.skill_ch_name).all()
        
        prereq_info_for_ai = [{'id': p.skill_id, 'name': p.skill_ch_name} for p in prereq_query]

        data = mod.generate(level=difficulty_level) # 將從課綱查到的 difficulty_level 傳入 generate 函數
        
        # 加入 context_string 給 AI
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        # 修正：在 data 產生後，才加入前置技能資訊
        data['prereq_skills'] = prereq_info_for_ai
        set_current(skill_id, data) # set_current 會將整個 data 存入 session
        
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

@practice_bp.route('/check_answer', methods=['POST'])
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

@practice_bp.route('/analyze_handwriting', methods=['POST'])
@login_required
def analyze_handwriting():
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: 
        return jsonify({"reply": "缺少圖片"}), 400
    
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    # 新增：從 session 讀取前置技能資訊並傳遞給 analyze 函式
    prereq_skills = state.get('prereq_skills', [])
    result = analyze(image_data_url=img, context=state['question'], 
                     api_key=api_key, 
                     prerequisite_skills=prereq_skills)
    
    # 更新進度
    if result.get('correct') or result.get('is_process_correct'):
        update_progress(current_user.id, state['skill'], True)
    else:
        update_progress(current_user.id, state['skill'], False)

        # 記錄錯誤到資料庫
        try:
            from models import MistakeLog
            
            mistake_log = MistakeLog(
                user_id=current_user.id,
                skill_id=state['skill'],
                question_content=state['question'],
                user_answer="手寫作答(圖片)",
                correct_answer=state.get('correct_answer', '未知'),
                error_type=result.get('error_type'),
                error_description=result.get('error_description'),
                improvement_suggestion=result.get('improvement_suggestion')
            )
            db.session.add(mistake_log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"記錄錯誤失敗: {e}")
            db.session.rollback()
            # 不影響主流程,繼續執行
    
    return jsonify(result)

@practice_bp.route('/chat_ai', methods=['POST'])
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
    prereq_skills = current.get('prereq_skills', []) # 新增：從 session 讀取前置技能資訊
    
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

        # 新增：將前置技能資訊加入 prompt
        prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prereq_skills]) if prereq_skills else "無"
        enhanced_context += f"\n\n此單元的前置基礎技能有：{prereq_text}。"

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

        # 新增：移除 AI 回覆中用於標記 LaTeX 數學式子的 '$' 符號
        reply = reply.replace('$', '')
        
        # 強制加鼓勵話（避免 AI 太冷）
        if not any(word in reply for word in ['加油', '試試', '可以的', '棒']):
            reply += "\n\n試試看，你一定可以的！加油～"
            
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[CHAT_AI ERROR] {e}")
        return jsonify({"reply": "AI 暫時無法回應，請稍後再試！"}), 500

@practice_bp.route('/draw_diagram', methods=['POST'])
@login_required
def draw_diagram():
    try:
        data = request.get_json()
        question_text = data.get('question_text')

        if not question_text:
            return jsonify({"success": False, "message": "沒有收到題目文字。"}), 400

        # 1. Call Gemini API to get equations
        # IMPORTANT: The user provided a hardcoded key.
        api_key = "AIzaSyAHdn-IImFJwyVMqRt5TdqBFOdnw_bgbbY"
        genai.configure(api_key=api_key)
        
        # Use the model from app config for consistency
        model_name = current_app.config.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash')
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        從以下數學題目中提取出所有可以用來繪製2D圖形的方程式或不等式。
        - 請只回傳方程式/不等式，每個一行。
        - 例如，如果題目是 "y = 2x + 1 和 x^2 + y^2 = 9"，你就回傳：
          y = 2x + 1
          x**2 + y**2 = 9
        - 請將 '^' 符號轉換為 '**' 以利 Python 運算。
        - 如果找不到任何可繪製的方程式或不等式，請回傳 "No equation found"。

        題目：
        {question_text}
        """
        
        response = model.generate_content(prompt)
        equations_text = response.text.strip()

        if "No equation found" in equations_text or not equations_text:
            return jsonify({"success": False, "message": "AI 無法從題目中找到可繪製的方程式。"}), 400

        # 2. Use Matplotlib to plot
        plt.figure(figsize=(6, 6))
        x = np.linspace(-10, 10, 400)
        y = np.linspace(-10, 10, 400)
        x, y = np.meshgrid(x, y)

        has_plot = False
        for line in equations_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Sanitize equation string for safer evaluation
            # 1. Normalize operators like '+ -' to '-'
            line = line.replace('+ -', '-')
            # 2. Insert '*' for implicit multiplication, e.g., '2x' -> '2*x' or '-3y' -> '-3*y'
            #    This regex finds a number (potentially with a sign) followed immediately by 'x' or 'y'
            #    and inserts a '*' between them.
            line = re.sub(r'(-?\d+(?:\.\d+)?)([xy])', r'\1*\2', line)
            
            try:
                # This is a simplified and somewhat unsafe way to plot.
                # It assumes the AI returns valid Python boolean expressions.
                if '=' in line and '==' not in line and '>' not in line and '<' not in line:
                    # Likely an equation like y = 2*x + 1 or x**2 + y**2 = 9
                    parts = line.split('=')
                    expr = f"({parts[0].strip()}) - ({parts[1].strip()})"
                    # Plot contour where expression is zero
                    plt.contour(x, y, eval(expr, {'x': x, 'y': y, 'np': np}), levels=[0], colors='b')
                    has_plot = True
                elif '>' in line or '<' in line:
                    # Likely an inequality like y > 2*x or x + y <= 5
                    plt.contourf(x, y, eval(line, {'x': x, 'y': y, 'np': np}), levels=[0, np.inf], colors=['#3498db'], alpha=0.3)
                    has_plot = True

            except Exception as e:
                current_app.logger.error(f"無法繪製方程式 '{line}': {e}")
                # Don't stop, try to plot other equations
                continue
        
        if not has_plot:
            return jsonify({"success": False, "message": "成功提取方程式，但無法繪製任何有效的圖形。"}), 400

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.title("Equation Diagram")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.gca().set_aspect('equal', adjustable='box')

        # 3. Save the image
        # Ensure the static directory exists
        static_dir = os.path.join(current_app.static_folder)
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        image_path = os.path.join(static_dir, 'diagram.png')
        plt.savefig(image_path)
        plt.close() # Close the figure to free up memory

        # 4. Return the path
        return jsonify({
            "success": True,
            "image_path": url_for('static', filename='diagram.png')
        })

    except Exception as e:
        current_app.logger.error(f"繪製示意圖時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": f"伺服器內部錯誤: {e}"}), 500


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
@core_bp.route('/skills/check_ghosts')
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
@core_bp.route('/prerequisites')
def admin_prerequisites():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('您沒有權限存取此頁面。', 'danger')
        return redirect(url_for('dashboard'))
    
    selected_skill_id = request.args.get('skill_id')  # 獲取選擇的 skill_id 參數
    try:
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
        all_skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()

        # 新增：獲取所有唯一的技能類別，用於篩選器
        all_categories = sorted([c[0] for c in db.session.query(SkillInfo.category).distinct().all() if c[0]])

        return render_template('admin_prerequisites.html',
                               prerequisites=prerequisites,
                               all_skills=all_skills,
                               all_categories=all_categories,
                               selected_skill_id=selected_skill_id, # 將選擇的 skill_id 傳給模板
                               username=current_user.username
                               )
    except Exception as e:
        current_app.logger.error(f"Error in admin_prerequisites: {e}\n{traceback.format_exc()}")
        flash(f'載入技能關聯頁面時發生錯誤，請檢查伺服器日誌。錯誤：{e}', 'danger')
        return redirect(url_for('dashboard'))

@core_bp.route('/api/prerequisites/<string:skill_id>')
@login_required
def api_get_prerequisites_for_skill(skill_id):
    """根據指定的 skill_id，回傳其所有前置技能的詳細資訊"""
    if not current_user.is_admin:
        return jsonify({"error": "權限不足"}), 403

    # 使用 SQLAlchemy 的 relationship 來查詢
    skill = db.session.get(SkillInfo, skill_id)

    if not skill:
        return jsonify([]) # 如果技能不存在，回傳空列表

    # 為了獲取關聯本身的 ID，我們需要查詢關聯表
    prerequisite_records = db.session.query(SkillPrerequisites).filter_by(skill_id=skill_id).all()

    prerequisites_data = []
    for record in prerequisite_records:
        # 透過 record.prerequisite_id 找到對應的 SkillInfo
        prereq_skill = db.session.get(SkillInfo, record.prerequisite_id)
        if not prereq_skill: continue

        prerequisites_data.append({
            'prerequisite_record_id': record.id, # 加入關聯記錄的 ID
            'skill_id': skill.skill_id,
            'skill_ch_name': skill.skill_ch_name,
            'prerequisite_id': prereq_skill.skill_id,
            'prerequisite_ch_name': prereq_skill.skill_ch_name
        })
    return jsonify(prerequisites_data)

@core_bp.route('/api/skills_by_category')
@login_required
def api_get_skills_by_category():
    """根據指定的 category，回傳對應的技能列表"""
    category = request.args.get('category')
    query = db.session.query(SkillInfo).filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)
    
    skills = query.order_by(SkillInfo.skill_ch_name).all()
    
    return jsonify([{'id': s.skill_id, 'text': f"{s.skill_ch_name} ({s.skill_id})"} for s in skills])

@core_bp.route('/prerequisites/add', methods=['POST'])
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

    # 為了在重新導向後能恢復篩選器狀態，我們需要找到 skill_id 對應的 category
    selected_category = None
    if skill_id:
        skill_info = db.session.get(SkillInfo, skill_id)
        if skill_info:
            selected_category = skill_info.category

    # 修改：重新導向時，同時帶上 skill_id 和 category 參數以保持狀態
    return redirect(url_for('core.admin_prerequisites', skill_id=skill_id, category=selected_category))

@core_bp.route('/prerequisites/delete/<int:prereq_id>', methods=['POST'])
def admin_delete_prerequisite(prereq_id):
    prereq = db.get_or_404(SkillPrerequisites, prereq_id)
    # 在刪除前，先記下我們要返回的 skill_id
    skill_id_to_redirect = prereq.skill_id

    db.session.delete(prereq)
    db.session.commit()
    flash('前置技能關聯已刪除。', 'success')

    # 為了在重新導向後能恢復篩選器狀態，我們需要找到 skill_id 對應的 category
    selected_category = None
    if skill_id_to_redirect:
        skill_info = db.session.get(SkillInfo, skill_id_to_redirect)
        if skill_info:
            selected_category = skill_info.category

    # 修改：重新導向時，同時帶上 skill_id 和 category 參數以保持狀態
    return redirect(url_for('core.admin_prerequisites', skill_id=skill_id_to_redirect, category=selected_category))

# === 資料庫管理 (從主應用程式移入) ===
@core_bp.route('/db_maintenance', methods=['GET', 'POST'])
@login_required
def db_maintenance():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('您沒有權限存取此頁面。', 'danger')
        return redirect(url_for('dashboard'))

    try:
        if request.method == 'POST':
            action = request.form.get('action')
            table_name = request.form.get('table_name')

            # 這裡的 table 獲取邏輯保持不變，因為它是直接操作
            table = db.metadata.tables.get(table_name)
            if table is None and action in ['clear_data', 'drop_table', 'upload_excel']:
                flash(f'表格 "{table_name}" 不存在。', 'danger')
                return redirect(url_for('core.db_maintenance'))

            if action == 'clear_data':
                db.session.execute(table.delete())
                db.session.commit()
                flash(f'表格 "{table_name}" 的所有資料已成功清除。', 'success')
            elif action == 'drop_table':
                table.drop(db.engine)
                flash(f'表格 "{table_name}" 已成功刪除。', 'success')
            elif action == 'upload_excel':
                file = request.files.get('file')
                if file and file.filename != '':
                    # 1. 獲取目標表格的所有欄位名稱
                    inspector = db.inspect(db.engine)
                    table_columns = [c['name'] for c in inspector.get_columns(table_name)]
                    # 2. 讀取 Excel
                    df = pd.read_excel(file)
                    # 3. 過濾 DataFrame，只保留資料庫表格中存在的欄位
                    df_filtered = df[[col for col in df.columns if col in table_columns]]
                    # 4. 將 NaN 轉為 None，並使用過濾後的 DataFrame 寫入資料庫
                    df_filtered = df_filtered.where(pd.notnull(df_filtered), None)
                    df_filtered.to_sql(table_name, db.engine, if_exists='append', index=False)
                    flash(f'成功將資料從 Excel 匯入到表格 "{table_name}"。', 'success')
                else:
                    flash('沒有選擇檔案或檔案無效。', 'warning')
            
            return redirect(url_for('core.db_maintenance'))

        # GET request
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        # 只顯示這三個技能相關的表格
        allowed_tables = ['skills_info', 'skill_prerequisites', 'skill_curriculum']
        tables = [t for t in all_tables if t in allowed_tables]
        return render_template('db_maintenance.html', tables=tables)
    except Exception as e:
        current_app.logger.error(f"Error in db_maintenance: {e}\n{traceback.format_exc()}")
        flash(f'載入資料庫管理頁面時發生錯誤，請檢查伺服器日誌。錯誤：{e}', 'danger')
        return redirect(url_for('dashboard'))

# === 課程分類管理 (從 app.py 移入) ===
@core_bp.route('/curriculum')
@login_required
def admin_curriculum():
    f_curriculum = request.args.get('f_curriculum')
    f_grade = request.args.get('f_grade')
    f_volume = request.args.get('f_volume')
    f_chapter = request.args.get('f_chapter')

    skills = db.session.query(SkillInfo).order_by(SkillInfo.order_index, SkillInfo.skill_id).all()

    query = db.session.query(SkillCurriculum).options(db.joinedload(SkillCurriculum.skill_info))

    if f_curriculum:
        query = query.filter(SkillCurriculum.curriculum == f_curriculum)
    if f_grade:
        query = query.filter(SkillCurriculum.grade == int(f_grade))
    if f_volume:
        query = query.filter(SkillCurriculum.volume == f_volume)
    if f_chapter:
        query = query.filter(SkillCurriculum.chapter == f_chapter)

    curriculum_items = query.order_by(
        SkillCurriculum.curriculum,
        SkillCurriculum.grade,
        SkillCurriculum.volume,
        SkillCurriculum.chapter,
        SkillCurriculum.section,
        SkillCurriculum.display_order
    ).all()

    distinct_filters = {
        'curriculums': sorted([row[0] for row in db.session.query(SkillCurriculum.curriculum).distinct().all()])
    }

    curriculum_map = {
        'general': '普通高中',
        'vocational': '技術型高中',
        'junior_high': '國民中學'
    }
    grade_map = {
        7: '國一', 8: '國二', 9: '國三',
        10: '高一', 11: '高二', 12: '高三'
    }

    return render_template('admin_curriculum.html', 
                           username=current_user.username,
                           skills=skills,
                           curriculum=curriculum_items,
                           curriculum_map=curriculum_map,
                           grade_map=grade_map,
                           filters=distinct_filters,
                           selected_filters={
                               'f_curriculum': f_curriculum,
                               'f_grade': f_grade,
                               'f_volume': f_volume,
                               'f_chapter': f_chapter
                           })

@core_bp.route('/curriculum/add', methods=['POST'])
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
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/edit/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_edit_curriculum(curriculum_id):
    item = db.get_or_404(SkillCurriculum, curriculum_id)
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
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/delete/<int:curriculum_id>', methods=['POST'])
@login_required
def admin_delete_curriculum(curriculum_id):
    item = db.get_or_404(SkillCurriculum, curriculum_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('課程分類刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/skills')
@login_required
def admin_skills():
    selected_category = request.args.get('category')

    query = db.session.query(SkillInfo)

    if selected_category:
        query = query.filter(SkillInfo.category == selected_category)

    skills = query.order_by(SkillInfo.order_index, SkillInfo.skill_id).all()

    categories = sorted([row[0] for row in db.session.query(SkillInfo.category).distinct().all() if row[0]])

    return render_template('admin_skills.html', 
                           skills=skills, 
                           categories=categories,
                           selected_category=selected_category,
                           username=current_user.username)

@core_bp.route('/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    
    if db.session.get(SkillInfo, data['skill_id']):
        flash('技能 ID 已存在！', 'danger')
        return redirect(url_for('core.admin_skills'))

    try:
        new_skill = SkillInfo(
            skill_id=data['skill_id'],
            skill_en_name=data['skill_en_name'],
            skill_ch_name=data['skill_ch_name'],
            category=data['category'],
            description=data['description'],
            input_type=data.get('input_type', 'text'),
            gemini_prompt=data['gemini_prompt'],
            consecutive_correct_required=int(data['consecutive_correct_required']),
            is_active=data.get('is_active') == 'on',
            order_index=int(data.get('order_index', 999))
        )
        db.session.add(new_skill)
        db.session.commit()
        flash('技能新增成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/edit/<skill_id>', methods=['POST'])
@login_required
def admin_edit_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
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

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    
    try:
        count = db.session.query(Progress).filter_by(skill_id=skill_id).count()
        
        if count > 0:
            flash(f'無法刪除：目前有 {count} 位使用者正在練習此技能！建議改為「停用」', 'warning')
        else:
            db.session.delete(skill)
            db.session.commit()
            flash('技能刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    try:
        skill.is_active = not skill.is_active
        db.session.commit()
        flash(f'技能已{"啟用" if skill.is_active else "停用"}！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'操作失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@practice_bp.route('/similar-questions-page')
@login_required
def similar_questions_page():
    return render_template('similar_questions.html')

@practice_bp.route('/generate-similar-questions', methods=['POST'])
@login_required
def generate_similar_questions():
    data = request.get_json()
    problem_text = data.get('problem_text')

    if not problem_text:
        return jsonify({"error": "Missing problem_text"}), 400

    # Import the function from the analyzer
    from .ai_analyzer import identify_skills_from_problem
    
    # Get skill IDs from the AI
    skill_ids = identify_skills_from_problem(problem_text)

    if not skill_ids:
        return jsonify({"questions": [], "message": "AI 無法從您的問題中識別出相關的數學技能，請嘗試更具體地描述您的問題。"
})

    generated_questions = []
    for skill_id in skill_ids:
        try:
            # Dynamically import the skill module
            mod = importlib.import_module(f"skills.{skill_id}")
            
            # Check if the module has a 'generate' function
            if hasattr(mod, 'generate') and callable(mod.generate):
                # Generate a question with a default level (e.g., 1)
                new_question = mod.generate(level=1)
                
                # Add skill info for context
                skill_info = get_skill_info(skill_id)
                new_question['skill_id'] = skill_id
                new_question['skill_ch_name'] = skill_info.skill_ch_name if skill_info else "未知技能"
                
                generated_questions.append(new_question)
            else:
                current_app.logger.warning(f"Skill module {skill_id} does not have a 'generate' function.")

        except ImportError:
            current_app.logger.error(f"Could not import skill module: {skill_id}")
        except Exception as e:
            current_app.logger.error(f"Error generating question for skill {skill_id}: {e}")

    return jsonify({"questions": generated_questions})


@practice_bp.route('/image-quiz-generator')
@login_required
def image_quiz_generator():
    return render_template('image_quiz_generator.html')

@practice_bp.route('/generate-quiz-from-image', methods=['POST'])
@login_required
def generate_quiz_from_image():
    if 'image_file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image_file']
    description = request.form.get('description', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        questions = generate_quiz_from_image(filepath, description) # Pass filepath instead of file object
        return jsonify({"questions": questions})
    except Exception as e:
        current_app.logger.error(f"Error in generate_quiz_from_image route: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


# 預設的建議問題，當資料庫中沒有設定時使用
DEFAULT_PROMPTS = [
    "這題的解題思路是什麼？",
    "可以給我一個相關的例子嗎？",
    "這個概念在生活中有什麼應用？"
]

@practice_bp.route('/get_suggested_prompts/<skill_id>')
@login_required
def get_suggested_prompts(skill_id):
    skill_info = db.session.get(SkillInfo, skill_id)
    prompts = []
    if skill_info:
        # 假設您的 SkillInfo 模型中有 suggested_prompt_1, suggested_prompt_2, suggested_prompt_3 欄位
        # 請根據您 Excel 中 K, L, M 欄對應的實際欄位名稱修改
        prompts = [p for p in [getattr(skill_info, 'suggested_prompt_1', None), 
                               getattr(skill_info, 'suggested_prompt_2', None), 
                               getattr(skill_info, 'suggested_prompt_3', None)] if p]
    return jsonify(prompts)

# === 班級管理功能 ===

def generate_class_code():
    """產生 6 碼隨機班級代碼 (大寫字母 + 數字)"""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        # 確保代碼唯一
        if not db.session.query(Class).filter_by(class_code=code).first():
            return code

@core_bp.route('/classes/create', methods=['POST'])
@login_required
def create_class():
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        data = request.get_json()
        class_name = data.get('name')
        
        if not class_name:
            return jsonify({"success": False, "message": "請輸入班級名稱"}), 400
            
        new_class = Class(
            name=class_name,
            teacher_id=current_user.id,
            class_code=generate_class_code()
        )
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "班級建立成功",
            "class": new_class.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"建立班級失敗: {e}")
        return jsonify({"success": False, "message": "建立班級失敗"}), 500

@core_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        # 確保只能刪除自己的班級
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限刪除"}), 404
            
        db.session.delete(target_class)
        db.session.commit()
        
        return jsonify({"success": True, "message": "班級已刪除"})
    except Exception as e:
        current_app.logger.error(f"刪除班級失敗: {e}")
        return jsonify({"success": False, "message": "刪除班級失敗"}), 500

@core_bp.route('/api/teacher/classes')
@login_required
def get_teacher_classes():
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        classes = db.session.query(Class).filter_by(teacher_id=current_user.id).order_by(Class.created_at.desc()).all()
        return jsonify({
            "success": True,
            "classes": [c.to_dict() for c in classes]
        })
    except Exception as e:
        current_app.logger.error(f"獲取班級列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取班級列表失敗"}), 500

# === 學生帳號管理路由 ===

@core_bp.route('/api/classes/<int:class_id>/students', methods=['GET'])
@login_required
def get_class_students(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        # 查詢班級學生
        students = db.session.query(User).join(ClassStudent).filter(ClassStudent.class_id == class_id).all()
        
        return jsonify({
            "success": True,
            "students": [{
                "id": s.id,
                "username": s.username,
                "role": s.role,
                "created_at": s.created_at.strftime('%Y-%m-%d')
            } for s in students]
        })

    except Exception as e:
        current_app.logger.error(f"獲取學生列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取學生列表失敗"}), 500

@core_bp.route('/api/classes/<int:class_id>/students', methods=['POST'])
@login_required
def add_student_to_class(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "請輸入帳號與密碼"}), 400

        # 檢查帳號是否已存在
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"success": False, "message": "此帳號已存在,請更換使用者名稱"}), 400

        # 建立新學生帳號
        new_student = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='student'
        )
        db.session.add(new_student)
        db.session.flush() # 取得 new_student.id

        # 將學生加入班級
        class_student = ClassStudent(
            class_id=class_id,
            student_id=new_student.id
        )
        db.session.add(class_student)
        
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "學生帳號建立成功",
            "student": {
                "id": new_student.id,
                "username": new_student.username,
                "role": new_student.role,
                "created_at": new_student.created_at.strftime('%Y-%m-%d')
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"建立學生帳號失敗: {e}")
        return jsonify({"success": False, "message": "建立學生帳號失敗"}), 500

@core_bp.route('/api/classes/<int:class_id>/students/upload', methods=['POST'])
@login_required
def upload_students_excel(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        if 'file' not in request.files:
            return jsonify({"success": False, "message": "未上傳檔案"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "未選擇檔案"}), 400

        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({"success": False, "message": "請上傳 Excel 檔案 (.xlsx, .xls)"}), 400

        # 讀取 Excel，不預設標題，以便我們自己判斷
        df = pd.read_excel(file, header=None)
        
        if df.shape[1] < 2:
            return jsonify({"success": False, "message": "Excel 檔案格式錯誤：至少需要兩欄 (帳號, 密碼)"}), 400

        stats = {
            "total": 0,
            "added": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }

        # 開始處理每一列
        for index, row in df.iterrows():
            try:
                username = str(row[0]).strip()
                password = str(row[1]).strip()

                # 簡單判斷是否為標題列 (如果第一欄包含 'account' 或 'username' 或 '帳號')
                if index == 0 and any(x in username.lower() for x in ['account', 'username', '帳號']):
                    continue
                
                if not username or not password or pd.isna(row[0]) or pd.isna(row[1]):
                    continue

                stats["total"] += 1

                # 檢查帳號是否已存在
                existing_user = db.session.query(User).filter_by(username=username).first()
                
                if existing_user:
                    # 如果使用者已存在，檢查是否已在班級中
                    in_class = db.session.query(ClassStudent).filter_by(class_id=class_id, student_id=existing_user.id).first()
                    if not in_class:
                        # 加入班級
                        new_class_student = ClassStudent(class_id=class_id, student_id=existing_user.id)
                        db.session.add(new_class_student)
                        stats["added"] += 1
                    else:
                        stats["skipped"] += 1 # 已經在班級中
                else:
                    # 建立新使用者
                    new_student = User(
                        username=username,
                        password_hash=generate_password_hash(password),
                        role='student'
                    )
                    db.session.add(new_student)
                    db.session.flush() # 取得 ID

                    # 加入班級
                    new_class_student = ClassStudent(class_id=class_id, student_id=new_student.id)
                    db.session.add(new_class_student)
                    stats["added"] += 1

            except Exception as row_error:
                stats["failed"] += 1
                stats["errors"].append(f"Row {index+1}: {str(row_error)}")
                continue

        db.session.commit()
        
        message = f"處理完成。共 {stats['total']} 筆資料，新增 {stats['added']} 位學生，略過 {stats['skipped']} 位 (已存在)，失敗 {stats['failed']} 筆。"
        if stats['errors']:
            message += f" 錯誤詳情: {'; '.join(stats['errors'][:3])}..."

        return jsonify({
            "success": True, 
            "message": message,
            "stats": stats
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批次匯入學生失敗: {e}")
        return jsonify({"success": False, "message": f"匯入失敗: {str(e)}"}), 500

# === 考卷診斷與分析 API ===

# 允許的圖片格式
ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_exam_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS

@core_bp.route('/upload_exam', methods=['POST'])
@login_required
def upload_exam():
    """
    上傳考卷圖片並進行分析
    
    接收參數:
    - file: 圖片檔案
    - grade: 年級 (7, 10, 11, 12)
    - curriculum: 課程類型 ('general', 'vocational', 'junior_high')
    """
    try:
        # 1. 驗證檔案
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '沒有上傳檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '沒有選擇檔案'}), 400
        
        if not allowed_exam_file(file.filename):
            return jsonify({'success': False, 'message': '不支援的檔案格式,請上傳 jpg, png 或 gif'}), 400
        
        # 2. 取得參數
        grade = request.form.get('grade', type=int)
        curriculum = request.form.get('curriculum', 'general')
        
        if not grade:
            return jsonify({'success': False, 'message': '請選擇年級'}), 400
        
        # 3. 儲存圖片
        upload_dir = os.path.join(current_app.static_folder, 'exam_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        file.save(file_path)
        
        # 4. 分析圖片
        analysis_response = analyze_exam_image(file_path, grade, curriculum)
        
        if not analysis_response['success']:
            return jsonify({
                'success': False,
                'message': f"分析失敗: {analysis_response['error']}"
            }), 500
        
        # 5. 儲存結果
        relative_path = f"exam_uploads/{current_user.id}/{unique_filename}"
        
        save_response = save_analysis_result(
            user_id=current_user.id,
            analysis_result=analysis_response['result'],
            image_path=relative_path
        )
        
        if not save_response['success']:
            return jsonify({
                'success': False,
                'message': f"儲存結果失敗: {save_response['error']}"
            }), 500
        
        # 6. 回傳結果
        result = analysis_response['result'].get('analysis_result', {})
        
        return jsonify({
            'success': True,
            'message': '分析完成!',
            'data': {
                'exam_analysis_id': save_response['exam_analysis_id'],
                'is_correct': result.get('is_correct'),
                'matched_unit': result.get('matched_unit'),
                'error_analysis': result.get('error_analysis'),
                'image_url': url_for('static', filename=relative_path)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"上傳考卷時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'伺服器錯誤: {str(e)}'
        }), 500


@core_bp.route('/exam_history')
@login_required
def exam_history():
    """
    查詢當前使用者的考卷分析歷史記錄
    """
    try:
        analyses = db.session.query(ExamAnalysis).filter_by(
            user_id=current_user.id
        ).order_by(ExamAnalysis.created_at.desc()).all()
        
        history = [analysis.to_dict() for analysis in analyses]
        
        for item in history:
            item['image_url'] = url_for('static', filename=item['image_path'])
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        current_app.logger.error(f"查詢考卷歷史時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'查詢失敗: {str(e)}'
        }), 500


@core_bp.route('/exam_upload_page')
@login_required
def exam_upload_page():
    """
    顯示考卷上傳頁面
    """
    return render_template('exam_upload.html', username=current_user.username)