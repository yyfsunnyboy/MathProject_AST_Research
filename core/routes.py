# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user  # 必須匯入！
from .session import set_current, get_current
from .ai_analyzer import analyze
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
    mod = get_skill(skill)
    if not mod:
        return jsonify({"error": "單元不存在"}), 404
    data = mod.generate()
    set_current(skill, data)  # 會儲存 data["answer"]
    return jsonify({
        "new_question_text": data["question_text"],
        "inequality_string": data.get("inequality_string", "")
    })

@core_bp.route('/check_answer', methods=['POST'])
def check_answer():
    ans = request.json.get('answer')
    state = get_current()
    mod = get_skill(state['skill'])
    result = mod.check(ans, state['answer'])

    # 進度記錄
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if result['correct']:
        c.execute('''
            INSERT INTO progress (user_id, skill_id, consecutive_correct, total_attempted)
            VALUES (?, ?, 1, 1)
            ON CONFLICT(user_id, skill_id) DO UPDATE SET
                consecutive_correct = consecutive_correct + 1,
                total_attempted = total_attempted + 1
        ''', (current_user.id, state['skill']))
    else:
        c.execute('''
            INSERT INTO progress (user_id, skill_id, consecutive_correct, total_attempted)
            VALUES (?, ?, 0, 1)
            ON CONFLICT(user_id, skill_id) DO UPDATE SET
                consecutive_correct = 0,
                total_attempted = total_attempted + 1
        ''', (current_user.id, state['skill']))
    conn.commit()
    conn.close()

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

