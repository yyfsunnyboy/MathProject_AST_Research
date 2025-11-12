# core/pdf.py
import os
import pdfplumber
import google.generativeai as genai
import json # ✅ 1. 導入 json 模組
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, jsonify # ✅ 2. 導入 jsonify
)
from flask_login import login_required
from werkzeug.utils import secure_filename

pdf_bp = Blueprint('pdf', __name__, template_folder='templates')

# ==============================
# ✅ 設定 Gemini API
# ==============================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("請先設定環境變數 GEMINI_API_KEY，否則無法使用 Gemini API。")

genai.configure(api_key=api_key)

# ✅ 3. 設定 JSON 輸出配置
# 我們可以共用这个設定，強制模型回傳 JSON
json_generation_config = genai.GenerationConfig(
    response_mime_type="application/json"
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """檢查檔案格式"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================
# 上傳 PDF 並擷取文字 (此部分與您原始碼相同)
# ==============================
@pdf_bp.route('/generate_from_pdf', methods=['POST'])
@login_required
def generate_from_pdf():
    if 'pdf_file' not in request.files:
        flash('沒有檔案部分', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['pdf_file']
    if file.filename == '':
        flash('未選擇檔案', 'danger')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        question_type = request.form.get('question_type', 'short_answer')

        try:
            with pdfplumber.open(filepath) as pdf:
                text = "".join([page.extract_text() or "" for page in pdf.pages])

            if not text.strip():
                flash('無法從 PDF 中提取文字內容。', 'warning')
                return redirect(url_for('dashboard'))

            session['pdf_text'] = text
            session['question_type'] = question_type
            return redirect(url_for('pdf.practice_pdf'))

        except Exception as e:
            flash(f'處理 PDF 時發生錯誤: {e}', 'danger')
            return redirect(url_for('dashboard'))
    else:
        flash('只允許上傳 PDF 檔案', 'danger')
        return redirect(url_for('dashboard'))


# ==============================
# 顯示練習頁面 (此部分與您原始碼相同)
# ==============================
@pdf_bp.route('/practice_pdf')
@login_required
def practice_pdf():
    pdf_text = session.get('pdf_text')
    question_type = session.get('question_type')

    if not pdf_text:
        flash('沒有找到學習材料，請重新上傳 PDF。', 'warning')
        return redirect(url_for('dashboard'))

    return render_template('practice_pdf.html', question_type=question_type)


# ==============================
# 生成題目 (✅ 已修復)
# ==============================
@pdf_bp.route('/generate_pdf_question', methods=['POST'])
@login_required
def generate_pdf_question():
    pdf_text = session.get('pdf_text')
    question_type = session.get('question_type', 'short_answer')

    if not pdf_text:
        # ✅ 4. API 路由應該回傳 JSON 錯誤
        return jsonify({"error": "學習材料遺失，請重新上傳 PDF。"}), 400

    try:
        # ✅ 5. 應用 JSON 輸出設定
        model = genai.GenerativeModel(
            "gemini-pro-latest",
            generation_config=json_generation_config
        )

        if question_type == 'multiple_choice':
            prompt = f"""
            根據以下內容，生成一個選擇題。
            請以 JSON 格式返回，包含：
            "question"（題目文字）、
            "options"（4 個選項的列表）、
            "answer"（正確答案文字）。

            內容：
            ---
            {pdf_text[:4000]}
            ---
            """
        else:
            prompt = f"""
            根據以下內容，生成一個簡答題。
            請以 JSON 格式返回，包含：
            "question" 和 "answer"（一個參考答案）。

            內容：
            ---
            {pdf_text[:4000]}
            ---
            """

        response = model.generate_content(prompt)

        # ✅ 6. 【重要】檢查 API 是否因為安全或其他原因阻擋了回應
        if not response.parts:
            print(f"DEBUG (generate): AI request was blocked. Feedback: {response.prompt_feedback}")
            return jsonify({"error": f"AI 請求被阻擋。原因: {response.prompt_feedback.block_reason}"}), 400

        # ✅ 7. 【重要】檢查 'text' 屬性是否存在
        if not hasattr(response, 'text') or not response.text:
            print(f"DEBUG (generate): AI response has no 'text' attribute or text is empty. Parts: {response.parts}")
            return jsonify({"error": "AI 未回傳任何文字內容，可能因為內容過濾。"}), 500
            
        # ✅ 8. 嘗試解析 JSON
        try:
            # 不再需要 .replace('```json', ...)
            json_data = json.loads(response.text)
        except json.JSONDecodeError:
            # 如果 AI 沒有回傳標準 JSON
            print(f"DEBUG (generate): AI response was not valid JSON: {response.text[:200]}...") 
            return jsonify({"error": "無法解析 AI 回應 (非JSON)，請重試。"}), 500

        # ✅ 9. 使用 jsonify 回傳一個真正的 JSON 響應
        return jsonify(json_data)

    except Exception as e:
        # ✅ 10. 捕捉所有其他錯誤 (例如 API 金鑰錯誤、網路問題)
        print(f"ERROR in generate_pdf_question: {e}") 
        return jsonify({"error": f"生成題目時發生未預期錯誤: {e}"}), 500


# ==============================
# 批改答案 (✅ 已修復)
# ==============================
@pdf_bp.route('/check_pdf_answer', methods=['POST'])
@login_required
def check_pdf_answer():
    data = request.get_json()
    question = data.get('question')
    user_answer = data.get('user_answer')
    original_answer = data.get('original_answer')

    if not all([question, user_answer, original_answer]):
        return jsonify({"error": "缺少必要的批改資訊。"}), 400

    try:
        # ✅ 11. 同樣應用 JSON 輸出設定
        model = genai.GenerativeModel(
            "gemini-pro-latest",
            generation_config=json_generation_config
        )

        prompt = f"""
        這是一個簡答題的批改任務。請判斷學生的答案是否正確。

        問題：{question}
        標準答案：{original_answer}
        學生的答案：{user_answer}

        請以 JSON 格式返回結果，包含：
        1. "is_correct": 布林值 (true/false)
        2. "feedback": 字串，提供對學生答案的簡短回饋。
        """

        response = model.generate_content(prompt)
        
        # ✅ 12. 同樣的錯誤處理邏輯
        if not response.parts:
            print(f"DEBUG (check): AI request was blocked. Feedback: {response.prompt_feedback}")
            return jsonify({"error": f"AI 批改請求被阻擋。原因: {response.prompt_feedback.block_reason}"}), 400
            
        if not hasattr(response, 'text') or not response.text:
            print(f"DEBUG (check): AI response has no 'text' or text is empty. Parts: {response.parts}")
            return jsonify({"error": "AI 批改未回傳任何文字內容。"}), 500

        # ✅ 13. 解析模型的 JSON 字串
        try:
            evaluation_data = json.loads(response.text)
        except json.JSONDecodeError:
            print(f"DEBUG (check): AI check_answer response was not valid JSON: {response.text[:200]}...")
            return jsonify({"error": "無法解析 AI 批改回應 (非JSON)，請重試。"}), 500

        # ✅ 14. 將解析後的 *物件* 放入回傳的 JSON 中
        return jsonify({
            "evaluation": evaluation_data,
            "final_answer": original_answer
        })

    except Exception as e:
        print(f"ERROR in check_pdf_answer: {e}")
        return jsonify({"error": f"批改答案時發生未預期錯誤: {e}"}), 500