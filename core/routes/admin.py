# -*- coding: utf-8 -*-
"""
=============================================================================
Module Name: admin.py
Description: 後台管理核心模組 (V2.5 Final)
             包含：資料庫維護、教科書匯入、技能管理、課程綱要管理、
             例題管理、Prompt 管理、前置技能管理 (Prerequisites)
=============================================================================
"""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash, send_file, Response, stream_with_context
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import distinct, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from markupsafe import Markup
import os
import uuid
import queue
import threading
import traceback
import pandas as pd
import io
import re
import importlib

from . import core_bp
from core.globals import TASK_QUEUES
from core import textbook_processor

# [Fix] 只引用確定存在的函式，避免 ImportError
from core.data_importer import import_excel_to_db

from config import Config
# [Fix] 確保 SkillPrerequisites 被引用
from models import db, SkillInfo, SkillCurriculum, User, TextbookExample, Progress, SkillGenCodePrompt, SkillPrerequisites, init_db

# ==========================================
# Background Tasks (背景任務)
# ==========================================

def background_processing(file_paths, task_queue, app_context, curriculum_info, skip_code_gen):
    """背景處理教科書分析任務"""
    with app_context:
        try:
            total_files = len(file_paths)
            task_queue.put(f"INFO: 開始處理任務，共 {total_files} 個檔案...")

            for idx, file_path in enumerate(file_paths, 1):
                filename = os.path.basename(file_path)
                if filename.startswith('~$') or filename.startswith('.'):
                    continue

                task_queue.put(f"INFO: [{idx}/{total_files}] 正在分析: {filename} ...")
                try:
                    textbook_processor.process_textbook_file(
                        file_path, 
                        curriculum_info=curriculum_info, 
                        queue=task_queue, 
                        skip_code_gen=skip_code_gen
                    )
                except Exception as e:
                    task_queue.put(f"ERROR: 檔案 {filename} 處理失敗: {e}")
                
                if 'uploads' in file_path and os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass

            task_queue.put("SUCCESS: 所有作業完成！")
        except Exception as e:
            task_queue.put(f"ERROR: 任務執行發生例外: {str(e)}")
        finally:
            task_queue.put("END_OF_STREAM")

# ==========================================
# Textbook Importer (教科書匯入器)
# ==========================================

@core_bp.route('/textbook_importer', methods=['GET', 'POST'])
@login_required
def admin_textbook_importer():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        target_files = []
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        single_file = request.files.get('textbook_pdf')
        batch_files = request.files.getlist('textbook_folder')
        
        if single_file and single_file.filename != '':
            path = os.path.join(upload_dir, secure_filename(single_file.filename))
            single_file.save(path)
            target_files.append(path)
        elif batch_files and len(batch_files) > 0 and batch_files[0].filename != '':
            for f in batch_files:
                if f.filename != '' and (f.filename.endswith('.pdf') or f.filename.endswith('.docx')):
                    path = os.path.join(upload_dir, secure_filename(os.path.basename(f.filename)))
                    f.save(path)
                    target_files.append(path)

        if target_files:
            task_id = str(uuid.uuid4())
            q = queue.Queue()
            TASK_QUEUES[task_id] = q

            curriculum_info = {
                'curriculum': request.form.get('curriculum'),
                'publisher': request.form.get('publisher'),
                'grade': request.form.get('grade'),
                'volume': request.form.get('volume')
            }
            skip_code = request.form.get('skip_code_gen') == 'on'

            app = current_app._get_current_object()
            threading.Thread(
                target=background_processing,
                args=(target_files, q, app.app_context(), curriculum_info, skip_code)
            ).start()

            return redirect(url_for('core.importer_status', task_id=task_id))
        else:
            flash('請選擇有效檔案', 'warning')

    return render_template('textbook_importer.html')

@core_bp.route('/importer/status/<task_id>')
@login_required
def importer_status(task_id):
    if task_id not in TASK_QUEUES:
        flash('任務已過期或不存在', 'warning')
        return redirect(url_for('core.admin_textbook_importer'))
    return render_template('importer_status.html', task_id=task_id)

@core_bp.route('/importer/stream/<task_id>')
@login_required
def importer_stream(task_id):
    def event_stream():
        q = TASK_QUEUES.get(task_id)
        if not q:
            yield "data: END_OF_STREAM\n\n"
            return
        while True:
            msg = q.get()
            yield f"data: {msg}\n\n"
            if msg == "END_OF_STREAM":
                TASK_QUEUES.pop(task_id, None)
                break
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

# ==========================================
# Database Maintenance (資料庫維護)
# ==========================================

@core_bp.route('/db_maintenance', methods=['GET', 'POST'])
@login_required
def db_maintenance():
    if not (current_user.is_admin or current_user.role == "teacher"):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        table_name = request.form.get('table_name')

        if action == 'export_db':
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            inspector = db.inspect(db.engine)
            for table in inspector.get_table_names():
                try:
                    df = pd.read_sql_table(table, db.engine)
                    for col in df.columns:
                        df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[\x00-\x1f\x7f-\x9f]', '', x) if x != 'None' else "")
                    df.to_excel(writer, sheet_name=table[:31], index=False)
                except: pass
            writer.close()
            output.seek(0)
            return send_file(output, download_name=f"backup_{datetime.now().strftime('%Y%m%d')}.xlsx", as_attachment=True)

        elif action == 'clear_all_data':
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                if table.name == 'users':
                    db.session.query(User).filter(User.username != 'admin').delete(synchronize_session=False)
                else:
                    db.session.execute(text(f"DELETE FROM {table.name}"))
                db.session.commit()
            flash('資料庫已清空 (保留 Admin)', 'success')

        elif action == 'batch_import_folder':
            files = request.files.getlist('files')
            success_count, error_count = 0, 0
            for file in files:
                if file and file.filename.endswith(('.csv', '.xlsx', '.xls')):
                    try:
                        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
                        df.columns = [str(c).lower().strip() for c in df.columns]
                        for _, row in df.iterrows():
                            if pd.isna(row.get('skill_id')): continue
                            item = SkillCurriculum(
                                curriculum=row.get('curriculum', 'general'),
                                grade=int(row.get('grade', 10)),
                                volume=row.get('volume', ''),
                                chapter=row.get('chapter', ''),
                                section=row.get('section', ''),
                                skill_id=str(row['skill_id']).strip(),
                                display_order=int(row.get('display_order', 0)) if 'display_order' in row else 0,
                                difficulty_level=int(row.get('difficulty_level', 1)) if 'difficulty_level' in row else 1
                            )
                            db.session.add(item)
                        success_count += 1
                    except: error_count += 1
            db.session.commit()
            flash(f'匯入完成：成功 {success_count}，失敗 {error_count}。', 'success')
        
        elif table_name and action == 'clear_data':
             try:
                 db.session.execute(text(f"DELETE FROM {table_name}"))
                 db.session.commit()
                 flash(f'表格 {table_name} 已清空', 'success')
             except Exception as e:
                 db.session.rollback()
                 flash(f'錯誤: {e}', 'danger')

        return redirect(url_for('core.db_maintenance'))

    inspector = db.inspect(db.engine)
    tables = sorted(inspector.get_table_names())
    return render_template('db_maintenance.html', tables=tables)

@core_bp.route('/upload_db', methods=['POST'])
@login_required
def upload_db():
    if not current_user.is_admin:
        flash('權限不足', 'danger')
        return redirect(url_for('core.db_maintenance'))

    if 'file' not in request.files:
        flash('沒有檔案', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    file = request.files['file']
    if file.filename == '':
        flash('未選擇檔案', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if file and (file.filename.endswith('.xlsx')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            success, message = import_excel_to_db(filepath)
            if success:
                flash(Markup(message.replace('\n', '<br>')), 'success')
            else:
                flash(message, 'danger')
        except Exception as e:
            flash(f'處理錯誤: {str(e)}', 'danger')
            
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return redirect(url_for('core.db_maintenance'))
    else:
        flash('格式錯誤，請上傳 .xlsx', 'danger')
        return redirect(url_for('core.db_maintenance'))

@core_bp.route('/admin/import_textbook_examples', methods=['POST'])
@login_required
def import_textbook_examples():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('權限不足', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if 'file' not in request.files: return redirect(url_for('core.db_maintenance'))
    file = request.files['file']
    if file.filename == '': return redirect(url_for('core.db_maintenance'))
        
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_dir): os.makedirs(upload_dir)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            success, message = import_excel_to_db(filepath)
            if os.path.exists(filepath): os.remove(filepath)
            
            if success: flash(Markup(message.replace('\n', '<br>')), 'success')
            else: flash(message, 'danger')
        except Exception as e:
            flash(f'匯入失敗: {str(e)}', 'error')
            
    return redirect(url_for('core.db_maintenance'))

# ==========================================
# Curriculum Management (課程綱要管理)
# ==========================================

@core_bp.route('/curriculum', methods=['GET', 'POST'])
@login_required
def admin_curriculum():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            new_curr = SkillCurriculum(
                skill_id=request.form.get('skill_id'),
                curriculum=request.form.get('curriculum'),
                grade=int(request.form.get('grade')) if request.form.get('grade') else 0,
                volume=request.form.get('volume'),
                chapter=request.form.get('chapter'),
                section=request.form.get('section'),
                paragraph=request.form.get('paragraph'),
                difficulty_level=int(request.form.get('difficulty_level', 1)),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(new_curr)
            db.session.commit()
            flash('新增成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'新增失敗: {str(e)}', 'error')
        return redirect(url_for('core.admin_curriculum'))

    sel_curr = request.args.get('curriculum')
    sel_grade = request.args.get('grade')
    sel_vol = request.args.get('volume')
    sel_chap = request.args.get('chapter')
    sel_sec = request.args.get('section')

    query = SkillCurriculum.query.join(SkillInfo)
    if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
    if sel_grade: query = query.filter(SkillCurriculum.grade == int(sel_grade))
    if sel_vol: query = query.filter(SkillCurriculum.volume == sel_vol)
    if sel_chap: query = query.filter(SkillCurriculum.chapter == sel_chap)
    if sel_sec: query = query.filter(SkillCurriculum.section == sel_sec)
    
    items = query.order_by(SkillCurriculum.grade, SkillCurriculum.volume, SkillCurriculum.display_order).limit(200).all()

    curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).all()]
    grades = sorted([r[0] for r in db.session.query(distinct(SkillCurriculum.grade)).filter(SkillCurriculum.grade != None).all()])
    volumes = [r[0] for r in db.session.query(distinct(SkillCurriculum.volume)).all()]
    chapters = [r[0] for r in db.session.query(distinct(SkillCurriculum.chapter)).all()]
    sections = [r[0] for r in db.session.query(distinct(SkillCurriculum.section)).all()]
    
    curriculum_map = {'junior_high': '國中', 'general': '普高', 'technical': '技高', 'elementary': '國小'}
    grade_map = {str(g): str(g) for g in grades}

    return render_template('admin_curriculum.html', 
                           items=items,
                           filters={'curriculums': curriculums, 'grades': grades, 'volumes': volumes, 'chapters': chapters, 'sections': sections},
                           selected_filters={'f_curriculum': sel_curr, 'f_grade': sel_grade, 'f_volume': sel_vol, 'f_chapter': sel_chap, 'f_section': sel_sec},
                           curriculum_map=curriculum_map,
                           grade_map=grade_map,
                           skills=SkillInfo.query.all())

@core_bp.route('/curriculum/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_curriculum(id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False}), 403
    try:
        curr = SkillCurriculum.query.get_or_404(id)
        curr.curriculum = request.form.get('curriculum')
        curr.grade = request.form.get('grade')
        curr.volume = request.form.get('volume')
        curr.chapter = request.form.get('chapter')
        curr.section = request.form.get('section')
        curr.skill_id = request.form.get('skill_id')
        curr.display_order = request.form.get('display_order')
        curr.difficulty_level = request.form.get('difficulty_level')
        db.session.commit()
        flash('更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗: {e}', 'error')
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_curriculum(id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False}), 403
    try:
        curr = SkillCurriculum.query.get_or_404(id)
        db.session.delete(curr)
        db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500

# ==========================================
# Skills Management (技能管理)
# ==========================================

@core_bp.route('/skills')
@login_required
def admin_skills():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    sel_curr = request.args.get('f_curriculum')
    sel_grade = request.args.get('f_grade')
    
    if sel_curr or sel_grade:
        query = db.session.query(SkillInfo).join(SkillCurriculum)
        if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: query = query.filter(SkillCurriculum.grade == int(sel_grade))
        skills = query.distinct().order_by(SkillInfo.skill_id).all()
    else:
        skills = SkillInfo.query.order_by(SkillInfo.skill_id).all()

    curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).all()]
    grades = sorted([r[0] for r in db.session.query(distinct(SkillCurriculum.grade)).filter(SkillCurriculum.grade != None).all()])

    return render_template('admin_skills.html', 
                           skills=skills,
                           filters={'curriculums': curriculums, 'grades': grades},
                           selected_filters={'f_curriculum': sel_curr, 'f_grade': sel_grade},
                           grade_map={str(g):str(g) for g in grades},
                           curriculum_map={'junior_high': '國中', 'general': '普高'},
                           username=current_user.username)

@core_bp.route('/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    if db.session.get(SkillInfo, data['skill_id']):
        flash('技能 ID 已存在', 'danger')
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
        flash('新增成功', 'success')
    except Exception as e:
        flash(f'錯誤: {e}', 'danger')
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
        skill.suggested_prompt_1 = data.get('suggested_prompt_1', '')
        skill.suggested_prompt_2 = data.get('suggested_prompt_2', '')
        skill.suggested_prompt_3 = data.get('suggested_prompt_3', '')
        db.session.commit()
        flash('更新成功', 'success')
    except Exception as e:
        flash(f'錯誤: {e}', 'danger')
    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    try:
        db.session.delete(skill)
        db.session.commit()
        flash('刪除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗 (可能有關聯資料): {e}', 'danger')
    return redirect(url_for('core.admin_skills'))


@core_bp.route('/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    skill.is_active = not skill.is_active
    db.session.commit()
    flash(f'技能已{"啟用" if skill.is_active else "停用"}', 'success')
    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/<skill_id>/regenerate', methods=['POST'])
@login_required
def admin_regenerate_skill_code(skill_id):
    try:
        from core.code_generator import auto_generate_skill_code
        result = auto_generate_skill_code(skill_id, queue=None)
        success = result[0] if isinstance(result, tuple) else result
        return jsonify({"success": success, "message": "生成成功" if success else "失敗"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/skills/<skill_id>/details', methods=['GET'])
@login_required
def admin_get_skill_details(skill_id):
    skill = db.session.get(SkillInfo, skill_id)
    if not skill: return jsonify({'success': False}), 404
    return jsonify({
        'success': True,
        'data': {
            'skill_id': skill.skill_id,
            'skill_ch_name': skill.skill_ch_name,
            'skill_en_name': skill.skill_en_name,
            'category': skill.category,
            'description': skill.description,
            'input_type': skill.input_type,
            'consecutive_correct_required': skill.consecutive_correct_required,
            'gemini_prompt': skill.gemini_prompt,
            'suggested_prompt_1': skill.suggested_prompt_1,
            'suggested_prompt_2': skill.suggested_prompt_2,
            'suggested_prompt_3': skill.suggested_prompt_3
        }
    })

# ==========================================
# Examples Management (例題管理)
# ==========================================

@core_bp.route('/examples', methods=['GET'])
@login_required
def admin_examples():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    query = db.session.query(TextbookExample).join(SkillInfo, TextbookExample.skill_id == SkillInfo.skill_id)
    pagination = query.order_by(TextbookExample.id.desc()).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin_examples.html', 
                           pagination=pagination, 
                           filters={}, selected_filters={}, curriculum_map={}, grade_map={}, 
                           skills=SkillInfo.query.all(), username=current_user.username)

@core_bp.route('/examples/add', methods=['POST'])
@login_required
def admin_add_example():
    try:
        new_ex = TextbookExample(
            skill_id=request.form.get('skill_id'),
            problem_text=request.form.get('problem_text'),
            correct_answer=request.form.get('correct_answer', ''),
            detailed_solution=request.form.get('detailed_solution', ''),
            difficulty_level=int(request.form.get('difficulty_level', 1))
        )
        db.session.add(new_ex)
        db.session.commit()
        flash('例題新增成功', 'success')
    except Exception as e:
        flash(f'新增失敗: {e}', 'danger')
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/delete/<int:example_id>', methods=['POST'])
@login_required
def admin_delete_example(example_id):
    ex = db.session.get(TextbookExample, example_id)
    if ex:
        db.session.delete(ex)
        db.session.commit()
        flash('刪除成功', 'success')
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/<int:example_id>/details', methods=['GET'])
@login_required
def admin_get_example_details(example_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    try:
        ex = db.session.get(TextbookExample, example_id)
        if not ex: return jsonify({'success': False, 'message': '找不到'}), 404
        return jsonify({
            'success': True,
            'data': {
                'id': ex.id,
                'skill_id': ex.skill_id,
                'problem_text': ex.problem_text or '',
                'correct_answer': ex.correct_answer or '',
                'detailed_solution': ex.detailed_solution or '',
                'difficulty_level': ex.difficulty_level or 1
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/examples/edit/<int:example_id>', methods=['POST'])
@login_required
def admin_edit_example(example_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('core.admin_examples'))
    try:
        ex = db.session.get(TextbookExample, example_id)
        if ex:
            ex.skill_id = request.form.get('skill_id')
            ex.problem_text = request.form.get('problem_text')
            ex.correct_answer = request.form.get('correct_answer', '')
            ex.detailed_solution = request.form.get('detailed_solution', '')
            ex.difficulty_level = int(request.form.get('difficulty_level', 1))
            db.session.commit()
            flash('更新成功', 'success')
    except Exception as e:
        flash(f'更新失敗: {e}', 'danger')
    return redirect(url_for('core.admin_examples'))

# ==========================================
# Prompt Management (Prompt 設定)
# ==========================================

@core_bp.route('/api/skills/<skill_id>/prompts', methods=['GET'])
@login_required
def api_get_skill_prompts(skill_id):
    prompts = SkillGenCodePrompt.query.filter_by(skill_id=skill_id).all()
    data = [{'id': p.id, 'model_tag': p.model_tag, 'system_prompt': p.system_prompt, 'user_prompt_template': p.user_prompt_template} for p in prompts]
    return jsonify({'success': True, 'data': data})

@core_bp.route('/api/skills/<skill_id>/prompts/save', methods=['POST'])
@login_required
def api_save_skill_prompt(skill_id):
    try:
        data = request.get_json()
        model_tag = data.get('model_tag')
        prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=model_tag).first()
        
        if prompt:
            prompt.user_prompt_template = data.get('user_prompt_template')
            prompt.system_prompt = data.get('system_prompt')
            prompt.version += 1
        else:
            prompt = SkillGenCodePrompt(
                skill_id=skill_id, model_tag=model_tag,
                user_prompt_template=data.get('user_prompt_template'),
                system_prompt=data.get('system_prompt'), version=1
            )
            db.session.add(prompt)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Prompt saved'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
@login_required
def api_delete_skill_prompt(prompt_id):
    try:
        prompt = db.session.get(SkillGenCodePrompt, prompt_id)
        if prompt:
            db.session.delete(prompt)
            db.session.commit()
        return jsonify({'success': True, 'message': '刪除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --------------------------------------------------------
# 請將以下程式碼接在 api_delete_skill_prompt 之後
# --------------------------------------------------------

# ==========================================
# Prerequisites Management (前置技能管理)
# ==========================================

@core_bp.route('/admin/prerequisites')
@login_required
def admin_prerequisites():
    """前置技能管理頁面"""
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))
    
    f_curriculum = request.args.get('f_curriculum', 'all')
    f_grade = request.args.get('f_grade', 'all')
    f_volume = request.args.get('f_volume', 'all')
    f_chapter = request.args.get('f_chapter', 'all')
    
    query = db.session.query(SkillInfo, SkillCurriculum).join(
        SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id
    ).filter(SkillInfo.is_active.is_(True))
    
    if f_curriculum != 'all': query = query.filter(SkillCurriculum.curriculum == f_curriculum)
    if f_grade != 'all': query = query.filter(SkillCurriculum.grade == int(f_grade))
    if f_volume != 'all': query = query.filter(SkillCurriculum.volume == f_volume)
    if f_chapter != 'all': query = query.filter(SkillCurriculum.chapter == f_chapter)
    
    results = query.order_by(SkillCurriculum.display_order).all()
    
    skills_list = []
    seen_skill_ids = set()
    for skill_info, skill_curriculum in results:
        if skill_info.skill_id in seen_skill_ids: continue
        seen_skill_ids.add(skill_info.skill_id)
        
        skill_info.grade = skill_curriculum.grade
        skill_info.volume = skill_curriculum.volume
        skill_info.chapter = skill_curriculum.chapter
        skill_info.prereq_count = len(skill_info.prerequisites)
        skills_list.append(skill_info)
    
    base_query = db.session.query(SkillCurriculum)
    curriculums = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.curriculum)).all()]
    grades = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.grade)).order_by(SkillCurriculum.grade).all()]
    volumes = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.volume)).all()]
    chapters = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.chapter)).all()]

    return render_template('admin_prerequisites.html',
                           skills=skills_list,
                           filters={'curriculums': curriculums, 'grades': grades, 'volumes': volumes, 'chapters': chapters},
                           selected={'f_curriculum': f_curriculum, 'f_grade': f_grade, 'f_volume': f_volume, 'f_chapter': f_chapter},
                           username=current_user.username)

@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['GET'])
@login_required
def api_get_prerequisites(skill_id):
    try:
        skill = db.session.get(SkillInfo, skill_id)
        if not skill: return jsonify({"success": False, "message": "技能不存在"}), 404
        data = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in skill.prerequisites]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['POST'])
@login_required
def api_add_prerequisite(skill_id):
    if not (current_user.is_admin or current_user.role == "teacher"): return jsonify({"success": False}), 403
    try:
        data = request.get_json()
        prereq_id = data.get('prereq_id')
        target = db.session.get(SkillInfo, skill_id)
        prereq = db.session.get(SkillInfo, prereq_id)
        
        if not target or not prereq: return jsonify({"success": False, "message": "技能不存在"}), 404
        if skill_id == prereq_id: return jsonify({"success": False, "message": "不能相依自己"}), 400
        
        if prereq not in target.prerequisites:
            target.prerequisites.append(prereq)
            db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/<string:skill_id>/prerequisites/<string:prereq_id>', methods=['DELETE'])
@login_required
def api_remove_prerequisite(skill_id, prereq_id):
    if not (current_user.is_admin or current_user.role == "teacher"): return jsonify({"success": False}), 403
    try:
        target = db.session.get(SkillInfo, skill_id)
        prereq = db.session.get(SkillInfo, prereq_id)
        
        if target and prereq and prereq in target.prerequisites:
            target.prerequisites.remove(prereq)
            db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/search', methods=['GET'])
@login_required
def api_search_skills():
    term = request.args.get('term', '').strip()
    if not term: return jsonify({"results": []})
    
    query = db.session.query(SkillInfo).filter(
        SkillInfo.is_active.is_(True),
        db.or_(
            SkillInfo.skill_id.like(f'%{term}%'),
            SkillInfo.skill_ch_name.like(f'%{term}%')
        )
    ).limit(20)
    
    results = [{'id': s.skill_id, 'text': f"{s.skill_ch_name} ({s.skill_id})"} for s in query.all()]
    return jsonify({"results": results})

@core_bp.route('/admin/init_db', methods=['POST'])
@login_required
def init_db_route():
    try:
        # 使用 models 內的 init_db
        init_db(db.engine)
        flash('資料庫初始化成功', 'success')
    except Exception as e:
        flash(f'初始化失敗: {e}', 'error')
    return redirect(url_for('core.db_maintenance'))

@core_bp.route('/admin/import_skills', methods=['POST'])
@login_required
def import_skills():
    if not current_user.is_admin: return jsonify({"success": False}), 403
    try:
        from core.data_importer import import_skills_from_json
        count = import_skills_from_json()
        return jsonify({"success": True, "message": f"成功匯入 {count} 個技能"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/admin/import_curriculum', methods=['POST'])
@login_required
def import_curriculum():
    if not current_user.is_admin: return jsonify({"success": False}), 403
    try:
        from core.data_importer import import_curriculum_from_json
        count = import_curriculum_from_json()
        return jsonify({"success": True, "message": f"成功匯入 {count} 個課綱"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==========================================
# Dropdown APIs (下拉選單連動)
# ==========================================

@core_bp.route('/api/get_grades')
@login_required
def api_get_grades():
    curriculum = request.args.get('curriculum')
    query = db.session.query(distinct(SkillCurriculum.grade)).filter_by(curriculum=curriculum)
    grades = sorted([row[0] for row in query.filter(SkillCurriculum.grade != None).all()])
    return jsonify(grades)

@core_bp.route('/api/get_volumes')
@login_required
def api_get_volumes():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    query = db.session.query(distinct(SkillCurriculum.volume)).filter_by(curriculum=curriculum, grade=grade)
    volumes = [row[0] for row in query.all()]
    return jsonify(volumes)

@core_bp.route('/api/get_chapters')
@login_required
def api_get_chapters():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    query = db.session.query(distinct(SkillCurriculum.chapter)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume
    )
    chapters = [row[0] for row in query.all()]
    return jsonify(chapters)

@core_bp.route('/api/get_sections')
@login_required
def api_get_sections():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    query = db.session.query(distinct(SkillCurriculum.section)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume, chapter=chapter
    )
    sections = [row[0] for row in query.all()]
    return jsonify(sections)

# API: 檢查幽靈技能檔案
@core_bp.route('/api/check_ghost_skills', methods=['GET'])
@login_required
def api_check_ghost_skills():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    try:
        skills_dir = os.path.join(current_app.root_path, 'skills')
        if not os.path.exists(skills_dir): return jsonify([])
        py_files = [f[:-3] for f in os.listdir(skills_dir) if f.endswith('.py') and f != '__init__.py']
        db_skills = [s.skill_id for s in SkillInfo.query.all()]
        ghost_skills = [f for f in py_files if f not in db_skills]
        return jsonify(ghost_skills)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
