"""此模組負責與 Google Gemini AI 模型進行互動，提供圖片分析、手寫辨識、題目技能識別以及從圖片生成測驗等功能。"""

# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json
import tempfile
import os
import re
from flask import current_app
import PIL.Image
import io

# 初始化 gemini_model 為 None，避免 NameError
gemini_model = None

def configure_gemini(api_key, model_name):
    global gemini_model
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)  # 動態設定！

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def get_ai_prompt():
    """
    從資料庫讀取 AI Prompt，若不存在則使用預設值並寫入資料庫
    """
    from models import SystemSetting, db
    
    # 預設 Prompt（保留原始內容）
    DEFAULT_PROMPT = """你是一位功文數學數學助教，正在批改學生手寫的計算紙。請你扮演一個非常有耐心、擅長鼓勵的數學家教老師。我的學生對數學比較沒信心
題目：{context}
此單元的前置基礎技能有：{prereq_text}

請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字、格式條列清楚。
如果學生計算錯誤或觀念不熟，你可以根據提供的前置技能列表，建議他回到哪個基礎技能練習。

{
  "reply": "用 Markdown 格式寫出具體建議(步驟對錯、遺漏、改進點)。如果計算過程完全正確,reply 內容應為「答對了,計算過程很正確!」。",
  "is_process_correct": true 或 false,
  "correct": true 或 false,
  "next_question": true 或 false,
  "error_type": "如果答錯,請從以下選擇一個:'計算錯誤'、'觀念錯誤'、'粗心'、'其他'。如果答對則為 null",
  "error_description": "如果答錯,簡短描述錯誤原因(例如:正負號弄反、公式背錯),30字以內。如果答對則為 null",
  "improvement_suggestion": "如果答錯,給學生的具體改進建議,30字以內。如果答對則為 null"
}

直接輸出 JSON 內容，不要包在 ```json 標記內。"""
    
    try:
        # 嘗試從資料庫讀取
        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        
        if setting:
            return setting.value
        else:
            # 資料庫中沒有，寫入預設值
            new_setting = SystemSetting(
                key='ai_analyzer_prompt',
                value=DEFAULT_PROMPT,
                description='AI 分析學生手寫答案時使用的 Prompt 模板。必須保留 {context} 和 {prereq_text} 變數。'
            )
            db.session.add(new_setting)
            db.session.commit()
            return DEFAULT_PROMPT
    except Exception as e:
        # 如果資料庫操作失敗，使用預設值
        print(f"Warning: Failed to read AI prompt from database: {e}")
        return DEFAULT_PROMPT

def analyze(image_data_url, context, api_key, prerequisite_skills=None):
    """
    強制 Gemini 回傳純 JSON，失敗時自動重試一次
    """
    def _call_gemini():
        # 將前置技能列表轉換為文字描述
        prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prerequisite_skills]) if prerequisite_skills else "無"

        # 解碼 Base64 圖片
        _, b64 = image_data_url.split(',', 1)
        img_data = base64.b64decode(b64)

        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name

        try:
            # 上傳到 Gemini
            file = genai.upload_file(path=temp_path)

            # 從資料庫讀取 Prompt 模板
            prompt_template = get_ai_prompt()
            
            # 使用 str.replace() 替換變數（避免 JSON 大括號衝突）
            prompt = prompt_template.replace("{context}", context).replace("{prereq_text}", prereq_text)

            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content([prompt, file])
            raw_text = resp.text.strip()

            # 清理可能的 ```json 標記
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
            return json.loads(cleaned)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # 最多嘗試 2 次
    for attempt in range(2):
        try:
            return _call_gemini()
        except json.JSONDecodeError as e:
            if attempt == 1:
                return {
                    "reply": f"AI 回應格式錯誤（第 {attempt+1} 次）：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)  # 重試前延遲
        except Exception as e:
            if attempt == 1:
                return {
                    "reply": f"AI 分析失敗：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)

    return {
        "reply": "AI 分析失敗，請稍後再試",
        "is_process_correct": False,
        "correct": False,
        "next_question": False
    }
    
def identify_skills_from_problem(problem_text):
    """
    Analyzes a math problem's text to identify relevant skills.
    """
    try:
        model = get_model()
        
        # Get the list of available skills from the skills directory
        skills_dir = os.path.join(os.path.dirname(__file__), '..', 'skills')
        skill_files = [f.replace('.py', '') for f in os.listdir(skills_dir) if f.endswith('.py') and f != '__init__.py']
        
        prompt = f"""
        You are an expert math teacher. Your task is to analyze a math problem and identify the key concepts or skills required to solve it.
        I will provide you with a math problem and a list of available skill IDs.

        **Math Problem:**
        "{problem_text}"

        **Available Skills:**
        {', '.join(skill_files)}

        Please identify up to 3 of the most relevant skills from the list that are directly applicable to solving this problem.

        **Instructions:**
        1.  Carefully read the problem to understand what is being asked.
        2.  Review the list of available skills.
        3.  Choose the skill IDs that best match the problem's requirements.
        4.  Return your answer in a JSON format with a single key "skill_ids" containing a list of the chosen skill ID strings.

        **Example Response:**
        {{
          "skill_ids": ["quadratic_equation", "factoring"]
        }}

        Do not include any other text or explanations. Just the JSON object.
        """
        
        resp = model.generate_content(prompt)
        raw_text = resp.text.strip()
        
        # Clean up potential markdown formatting
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
        
        data = json.loads(cleaned)
        
        # Basic validation
        if "skill_ids" in data and isinstance(data["skill_ids"], list):
            return data["skill_ids"]
        else:
            # Log or handle the case where the response is not in the expected format
            return []
            
    except json.JSONDecodeError as e:
        # Log or handle JSON parsing errors
        print(f"AI response JSON decode error: {e}")
        return []
    except Exception as e:
        # Log or handle other exceptions
        print(f"An error occurred in identify_skills_from_problem: {e}")
        return []

def ask_ai_text(user_question):
    try:
        model = get_model()
        prompt = f"""
        你是功文數學 AI 助教，用繁體中文親切回答。
        要求：
        1. 多項式用這種格式：f(x) = x³ - 8x² + 9x + 5
        2. 不要用 $...$ 或 LaTeX
        3. 例題用「範例：」開頭
        4. 步驟用數字 1. 2. 3.
        5. 結尾加鼓勵話，如「加油～」
        
        學生問題：{user_question}
        """
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI 錯誤：{str(e)}"
    
# core/ai_analyzer.py
def ask_ai_text_with_context(user_question, context=""):
    """
    聊天專用 AI：帶入當前題目 context
    """
    model = get_model()
    
    system_prompt = f"""
    你是功文數學 AI 助教，用繁體中文親切回答。
    
    【當前題目】：
    {context or "（無題目資訊）"}
    
    【學生問題】：
    {user_question}
    
    要求：
    1. 如果有題目，必須參考題目內容
    2. 多項式用 x^3 格式（如 x^3 - 2x^2 + 1）
    3. 例題用「範例：」開頭
    4. 步驟用 1. 2. 3.
    5. 結尾加鼓勵話，如「加油～」
    """
    
    try:
        resp = model.generate_content(system_prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI 內部錯誤：{str(e)}"


def generate_quiz_from_image(image_file, description):
    """
    Generates a quiz from an image and a text description using a multimodal AI model.
    """
    try:
        model = get_model()

        # Prepare the image for the API
        img = PIL.Image.open(image_file.stream)

        prompt = f"""
        You are an expert math quiz generator. Your task is to create a quiz based on the provided image and description.

        **Description:**
        "{description}"

        **Instructions:**
        1.  Analyze the image, which contains a math problem or concept.
        2.  Use the user's description to understand what kind of quiz to generate (e.g., number of questions, question type).
        3.  Generate a list of questions. Each question should have a question text, a list of options (if applicable), and the correct answer.
        4.  Return your answer in a JSON format with a single key "questions" containing a list of the question objects.
        5.  The structure for each question object should be: {{"question_text": "...", "options": ["...", "...", "..."], "correct_answer": "..."}}. For free-response questions, the "options" key can be omitted.

        **Example Response:**
        {{
          "questions": [
            {{
              "question_text": "What is the first step to solve the equation in the image?",
              "options": ["Add 5 to both sides", "Subtract 5 from both sides", "Multiply by 2"],
              "correct_answer": "Subtract 5 from both sides"
            }},
            {{
              "question_text": "What is the final value of x?",
              "correct_answer": "x = 3"
            }}
          ]
        }}

        Do not include any other text or explanations. Just the JSON object.
        """

        # Generate content with both the prompt and the image
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()

        # Clean up potential markdown formatting
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)

        data = json.loads(cleaned)

        # Basic validation
        if "questions" in data and isinstance(data["questions"], list):
            return data.get("questions", [])
        else:
            current_app.logger.error("AI response for quiz generation was not in the expected format.")
            return []

    except json.JSONDecodeError as e:
        current_app.logger.error(f"AI response JSON decode error in quiz generation: {e}")
        return []
    except Exception as e:
        current_app.logger.error(f"An error occurred in generate_quiz_from_image: {e}")
        return []

    