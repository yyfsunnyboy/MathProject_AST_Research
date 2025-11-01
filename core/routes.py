# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user  # 必須匯入！
from .session import set_current, get_current
from .ai_analyzer import analyze, ask_ai_text_with_context
import importlib
import sqlite3

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

@core_bp.route('/get_next_question')
def next_question():
    skill = request.args.get('skill', 'remainder')
    try:
        mod = get_skill(skill)
        if not mod:
            return jsonify({"error": f"單元 {skill} 不存在"}), 404
        
        data = mod.generate()
        # 確保必要鍵存在
        data.setdefault('answer', None)
        data.setdefault('correct_answer', 'text')
        
        set_current(skill, data)
        return jsonify({
            "new_question_text": data["question_text"],
            "inequality_string": data.get("inequality_string", ""),
            "context_string": data.get("context_string", "")  # 必須有！
        })
    except Exception as e:
        print(f"[ERROR] 生成題目失敗: {e}")
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
    return jsonify(result)

# core/routes.py
@core_bp.route('/analyze_handwriting', methods=['POST'])
def analyze_handwriting():
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: return jsonify({"reply": "缺少圖片"}), 400
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    result = analyze(img, state['question'], api_key)  # 傳 api_key
    return jsonify(result)

@core_bp.route('/chat_ai', methods=['POST'])
def chat_ai():
    data = request.get_json()
    user_question = data.get('question', '').strip()
    context = data.get('context', '')  # 接收前端傳的題目！

    if not user_question:
        return jsonify({"reply": "請輸入問題！"}), 400

    try:
        # 傳給 AI 分析器（支援 context）
        reply = ask_ai_text_with_context(user_question, context)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[CHAT_AI ERROR] {e}")  # 除錯用
        return jsonify({"reply": f"AI 錯誤：{str(e)}"}), 500