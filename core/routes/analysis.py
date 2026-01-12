# -*- coding: utf-8 -*-
"""
=============================================================================
Module Name: analysis.py
Description: AI 分析與診斷模組
             包含：AI 聊天助手 (Chat AI)、手寫辨識分析 (Handwriting)、
             考卷上傳與診斷 (Exam Analysis)、錯題本 (Mistake Notebook)、弱點分析
Version: V2.0 (Refactored)
Maintainer: Math AI Team
=============================================================================
"""

from flask import request, jsonify, render_template, current_app, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import uuid
import traceback

from . import core_bp, practice_bp
from core.session import get_current
from core.ai_analyzer import build_chat_prompt, get_chat_response, analyze
from core.exam_analyzer import analyze_exam_image, save_analysis_result
from core.diagnosis_analyzer import perform_weakness_analysis
from models import db, MistakeNotebookEntry, ExamAnalysis, SkillInfo

ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_exam_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS

# ==========================================
# AI Chat & Handwriting (AI 互動)
# ==========================================

@practice_bp.route('/chat_ai', methods=['POST'])
def chat_ai():
    """AI 助教對話 API"""
    data = request.get_json()
    user_question = data.get('question', '').strip()
    context = data.get('context', '')
    question_text = data.get('question_text', '')

    if not user_question:
        return jsonify({"reply": "請輸入問題！"}), 400

    current = get_current()
    skill_id = current.get("skill")
    prereq_skills = current.get('prereq_skills', [])
    
    full_question_context = question_text if question_text else (current.get("question") or context)
    
    if not skill_id and context:
        # 簡單推測 skill_id (Fallback)
        if '餘式' in context: skill_id = 'remainder'
        elif '因式' in context: skill_id = 'factor_theorem'

    full_prompt = build_chat_prompt(
        skill_id=skill_id,
        user_question=user_question,
        full_question_context=full_question_context,
        context=context,
        prereq_skills=prereq_skills
    )
    
    result = get_chat_response(full_prompt)
    return jsonify(result)

@practice_bp.route('/analyze_handwriting', methods=['POST'])
@login_required
def analyze_handwriting():
    """手寫數學算式辨識與分析"""
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: return jsonify({"reply": "缺少圖片"}), 400
    
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    prereq_skills = state.get('prereq_skills', [])
    
    result = analyze(image_data_url=img, context=state['question'], 
                     api_key=api_key, 
                     prerequisite_skills=prereq_skills)
    
    # 這裡的 update_progress 邏輯若有需要可在此處呼叫 helper
    
    return jsonify(result)



# ==========================================
# Mistake Notebook & Diagnosis (錯題本與診斷)
# ==========================================

@core_bp.route('/mistake-notebook')
@login_required
def mistake_notebook():
    return render_template('mistake_notebook.html', username=current_user.username)

@core_bp.route('/api/mistake-notebook', methods=['GET'])
@login_required
def api_mistake_notebook():
    entries = db.session.query(MistakeNotebookEntry).filter_by(student_id=current_user.id).order_by(MistakeNotebookEntry.created_at.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])

@core_bp.route('/mistake-notebook/add', methods=['POST'])
@login_required
def add_mistake_entry():
    try:
        data = request.get_json()
        db.session.add(MistakeNotebookEntry(
            student_id=current_user.id,
            exam_image_path=data.get('exam_image_path'),
            question_data=data.get('question_data'),
            notes=data.get('notes'),
            skill_id=data.get('skill_id')
        ))
        db.session.commit()
        return jsonify({'success': True, 'message': '已記錄'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/student/analyze_weakness', methods=['POST'])
@login_required
def analyze_weakness():
    """學生學習弱點分析 (Radar Chart Data)"""
    try:
        force_refresh = request.json.get('force_refresh', False) if request.json else False
        result = perform_weakness_analysis(current_user.id, force_refresh)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"弱點分析錯誤: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# [遺漏補齊] Mistake Notebook Helpers
# ==========================================

@core_bp.route('/add_mistake_page')
@login_required
def add_mistake_page():
    """顯示手動新增錯題的頁面"""
    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()
    return render_template('add_mistake.html', skills=skills, username=current_user.username)

@core_bp.route('/mistake-notebook/upload-image', methods=['POST'])
@login_required
def upload_mistake_image():
    """處理錯題圖片上傳"""
    if 'file' not in request.files: return jsonify({'success': False, 'message': '沒有檔案'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_exam_file(file.filename):
        return jsonify({'success': False, 'message': '檔案無效'}), 400

    try:
        upload_dir = os.path.join(current_app.static_folder, 'mistake_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(upload_dir, unique_filename)
        file.save(path)
        
        rel_path = os.path.join('mistake_uploads', str(current_user.id), unique_filename).replace('\\', '/')
        return jsonify({'success': True, 'path': rel_path})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Student Diagnosis (學生學習診斷頁面)
# ==========================================

@core_bp.route('/student/diagnosis')
@login_required
def student_diagnosis():
    """
    顯示學生學習診斷頁面
    """
    return render_template('student_diagnosis.html', username=current_user.username)