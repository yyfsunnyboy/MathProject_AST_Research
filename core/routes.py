# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .session import set_current, get_current
from .ai_analyzer import analyze, get_model, analyze_student_answer # 修正：匯入 analyze_student_answer
from flask import session # 導入 session
import importlib, os
from core.utils import get_skill_info
from models import db, Progress, SkillInfo, SkillCurriculum, SkillPrerequisites, StudentErrorRecord # 導入 StudentErrorRecord
import traceback
import re
from sqlalchemy.orm import aliased
import pandas as pd
import google.generativeai as genai
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt


core_bp = Blueprint('core', __name__, template_folder='../templates')
practice_bp = Blueprint('practice', __name__) # 新增：練習專用的 Blueprint

# 所有 core 路由都需要登入
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

    # === 新增：如果答錯，呼叫 AI 分析並記錄錯誤 ===
    if not is_correct:
        ai_guidance = None # 初始化 AI 指導為 None
        try:
            # 1. 準備給 AI 的資料
            #    - question_id: 使用題目文字的 hash 作為唯一識別
            #    - answer_steps: 目前先用用戶的單一答案作為步驟
            import hashlib
            question_id = hashlib.md5(current.get("question", "").encode()).hexdigest()
            answer_steps = [user] # 暫時將用戶答案當作單一步驟

            # 2. 呼叫 AI 分析
            ai_analysis = analyze_student_answer(
                answer_steps=answer_steps,
                student_answer=user,
                correct_answer=str(correct_answer)
            )
            ai_guidance = ai_analysis.get('guidance') # 取得 AI 的指導

            # 3. 建立並儲存錯誤記錄
            new_error_record = StudentErrorRecord(
                user_id=current_user.id,
                skill_id=skill,
                question_id=question_id,
                is_correct=False,
                error_category=ai_analysis.get('error_category'),
                error_explanation=ai_analysis.get('error_explanation'),
                guidance=ai_guidance
            )
            db.session.add(new_error_record)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"寫入錯誤記錄失敗: {e}\n{traceback.format_exc()}")
        
        result['guidance'] = ai_guidance # 將 AI 指導加入回傳給前端的 JSON
    
    return jsonify(result)

@practice_bp.route('/analyze_handwriting', methods=['POST'])
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
    
    # 判斷 AI 批改結果
    is_correct_by_ai = result.get('correct', False) or result.get('is_process_correct', False)

    # 更新進度
    update_progress(current_user.id, state['skill'], is_correct_by_ai)
    
    # === 新增：如果 AI 判斷過程錯誤，記錄到資料庫 ===
    if not is_correct_by_ai:
        try:
            import hashlib
            question_id = hashlib.md5(state.get("question", "").encode()).hexdigest()

            # 建立並儲存錯誤記錄
            new_error_record = StudentErrorRecord(
                user_id=current_user.id,
                skill_id=state['skill'],
                question_id=question_id,
                is_correct=False,
                error_category="手寫過程錯誤", # 給定一個分類
                error_explanation=result.get('reply', 'AI 未提供詳細說明'), # 使用 AI 的 reply 作為說明
                guidance=result.get('reply', '請根據 AI 建議修正') # 同上
            )
            db.session.add(new_error_record)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"寫入 AI 手寫分析錯誤記錄失敗: {e}\n{traceback.format_exc()}")

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
    if not current_user.is_admin:
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
    if not current_user.is_admin:
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
                    df = pd.read_excel(file)
                    df = df.where(pd.notnull(df), None) # 將 NaN 轉為 None
                    df.to_sql(table_name, db.engine, if_exists='append', index=False)
                    flash(f'成功將資料從 Excel 匯入到表格 "{table_name}"。', 'success')
                else:
                    flash('沒有選擇檔案或檔案無效。', 'warning')
            
            return redirect(url_for('core.db_maintenance'))

        # GET request
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
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
