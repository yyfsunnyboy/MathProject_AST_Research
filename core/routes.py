# core/routes.py
from flask import Blueprint, request, jsonify, current_app
from .session import set_current, get_current
from .ai_analyzer import analyze
import importlib

core_bp = Blueprint('core', __name__)

def get_skill(skill_id):
    try:
        return importlib.import_module(f"skills.{skill_id}")
    except:
        return None

@core_bp.route('/get_next_question')
def next_question():
    skill = request.args.get('skill', 'remainder')
    mod = get_skill(skill)
    if not mod: return jsonify({"error": "單元不存在"}), 404
    data = mod.generate()
    set_current(skill, data)
    return jsonify({
        "new_question_text": data["question_text"],
        "inequality_string": data.get("inequality_string", "")
    })

@core_bp.route('/check_answer', methods=['POST'])
def check():
    ans = request.json.get('answer')
    state = get_current()
    mod = get_skill(state['skill'])
    result = mod.check(ans, state['answer'])
    return jsonify(result)

@core_bp.route('/analyze_handwriting', methods=['POST'])
def analyze_handwriting():
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: return jsonify({"reply": "缺少圖片"}), 400
    state = get_current()
    result = analyze(img, state['question'], current_app)
    return jsonify(result)