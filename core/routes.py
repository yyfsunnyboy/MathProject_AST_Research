# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from .session import set_current, get_current
from .ai_analyzer import analyze, ask_ai_text_with_context, get_model
import importlib
from core.utils import get_skill_info
from models import db, Progress, SkillInfo

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
            current_level=1
        )
        db.session.add(progress)
    else:
        # 如果有記錄，更新現有物件
        progress.questions_solved += 1
        
        # 讀取技能的晉級/降級門檻
        skill_info = db.session.get(SkillInfo, skill_id)
        required = skill_info.consecutive_correct_required if skill_info else 10
        demotion_threshold = 3 # 連續答錯 3 次就降級
        
        # 功文式進退階邏輯
        if is_correct:
            progress.consecutive_correct += 1
            progress.consecutive_wrong = 0 # 答對，連續錯誤歸零
            # 1. 晉級：連續答對達到門檻，等級提升，連續答對數歸零。
            if progress.consecutive_correct >= required and progress.current_level < 10: # 假設最高 10 級
                progress.current_level += 1
                progress.consecutive_correct = 0
        else:
            # 2. 降級：連續答錯達到門檻，等級降低（但不低於1），連續答對數也歸零。
            # 這能幫助基礎不穩的學生回到更簡單的題目，建立信心。
            progress.consecutive_correct = 0 # 只要錯了，連續答對就中斷
            progress.consecutive_wrong += 1
            if progress.consecutive_wrong >= demotion_threshold and progress.current_level > 1:
                progress.current_level -= 1
    
    # 提交變更到資料庫
    db.session.commit()


@core_bp.route('/get_next_question')
def next_question():
    skill_id = request.args.get('skill', 'remainder')
    
    # 從 DB 驗證 skill 是否存在
    skill_info = get_skill_info(skill_id)
    if not skill_info:
        return jsonify({"error": f"技能 {skill_id} 不存在或未啟用"}), 404
    
    try:
        mod = importlib.import_module(f"skills.{skill_id}")
        
        # 根據用戶當前等級，生成對應難度的題目
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, skill_id=skill_id).first()
        current_level = progress.current_level if progress else 1
        consecutive = progress.consecutive_correct if progress else 0

        data = mod.generate(level=current_level) # 將等級傳入 generate 函數
        
        # 加入 context_string 給 AI
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        set_current(skill_id, data)
        
        return jsonify({
            "new_question_text": data["question_text"],
            "context_string": data.get("context_string", ""),
            "inequality_string": data.get("inequality_string", ""),
            "consecutive_correct": consecutive, # 連續答對
            "current_level": current_level, # 目前等級,
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
    
    # 更新進度
    update_progress(current_user.id, skill, result['correct'])
    
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
    if result.get('correct') or result.get('is_graph_correct'):
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