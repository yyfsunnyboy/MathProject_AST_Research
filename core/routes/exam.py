# -*- coding: utf-8 -*-
"""
Module Name: exam.py
Description: 考卷診斷與分析路由 (Refactored)
             處理考卷上傳、分析、歷史紀錄查詢與顯示
"""

from flask import request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from models import db, ExamAnalysis
from . import core_bp
from core.exam_analyzer import analyze_exam_image, save_analysis_result
import os
import uuid
import traceback

# 允許的圖片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支援的檔案格式,請上傳 jpg, png 或 gif'}), 400
        
        # 2. 取得參數
        grade = request.form.get('grade', type=int)
        curriculum = request.form.get('curriculum', 'general')
        
        if not grade:
            return jsonify({'success': False, 'message': '請選擇年級'}), 400
        
        # 3. 儲存圖片
        # 建立目錄: static/exam_uploads/{user_id}/
        upload_dir = os.path.join(current_app.static_folder, 'exam_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 產生唯一檔名
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
        # 儲存相對路徑 (相對於 static 目錄)
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
        # 查詢該使用者的所有分析記錄
        analyses = db.session.query(ExamAnalysis).filter_by(
            user_id=current_user.id
        ).order_by(ExamAnalysis.created_at.desc()).all()
        
        # 轉換為字典列表
        history = [analysis.to_dict() for analysis in analyses]
        
        # 加入圖片 URL
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
