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
gemini_chat = None

def clean_and_parse_json(text):
    """
    強力清洗並解析 Gemini 回傳的 JSON 字串。
    能夠自動移除 Markdown (```json) 與多餘雜訊，只提取有效的 JSON 物件。
    """
    try:
        # 1. 移除常見的 Markdown code block 標記
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)
        
        # 2. 使用 Regex 尋找最外層的 { } 結構
        # dotall 模式讓 . 可以匹配換行符號
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            
        # 3. 嘗試解析
        return json.loads(text)
    except Exception as e:
        print(f"JSON 解析失敗: {e}, 原始文字: {text}")
        return None

# 預設批改 Prompt
DEFAULT_PROMPT = """你是一位功文數學數學助教，正在批改學生手寫的計算紙。請你扮演一個非常有耐心、擅長鼓勵的數學家教老師。我的學生對數學比較沒信心
題目：{context}
此單元的前置基礎技能有：{prereq_text}

請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字、格式條列清楚。
如果學生計算錯誤或觀念不熟，你可以根據提供的前置技能列表，建議他回到哪個基礎技能練習。

【⚠️ 絕對嚴格的數學輸出規範 ⚠️】：
為了讓網頁能正確顯示數學公式，你必須遵守以下規則，否則學生會看到亂碼：

1. **所有的數學符號與算式**，無論多短，都**必須**用單個錢字號 $ 包裹。
   - ❌ 錯誤：x^3 + \\frac{1}{x^3}
   - ✅ 正確：$x^3 + \\frac{1}{x^3}$
   
2. **變數與數字**：
   - ❌ 錯誤：令 a = x
   - ✅ 正確：令 $a = x$
   - ❌ 錯誤：答案是 198
   - ✅ 正確：答案是 $198$

3. **禁止巢狀 $**：
   - ❌ 錯誤：$\\sqrt{ $3$ \\times $5$ }$
   - ✅ 正確：$\\sqrt{3 \\times 5}$  (整個算式用一組 $ 包起來即可)

4. **常用符號對照表**：
   - 分數：$\\frac{a}{b}$
   - 次方：$x^2$
   - 根號：$\\sqrt{x}$
   - 乘號：\\times 或 \\cdot

請檢查你的 JSON 輸出中的 "reply" 欄位，確保所有數學部分都已經加上了 $。
{
  "reply": "用 Markdown 格式寫出具體建議(步驟對錯、遺漏、改進點)。如果計算過程完全正確,reply 內容應為「答對了,計算過程很正確!」。",
  "is_process_correct": true 或 false,
  "correct": true 或 false,
  "next_question": true 或 false,
  "error_type": "如果答錯,請從以下選擇一個:'計算錯誤'、'觀念錯誤'、'粗心'、'其他'。如果答對則為 null",
  "error_description": "如果答錯,簡短描述錯誤原因(例如:正負號弄反、公式背錯),30字以內。如果答對則為 null",
  "improvement_suggestion": "如果答錯,給學生的具體改進建議,30字以內。如果答對則為 null",
  "follow_up_prompts": [
      "Prompt 1 (觀察/發現)",
      "Prompt 2 (修正/行動)",
      "Prompt 3 (延伸/驗證)"
  ]
}

直接輸出 JSON 內容，不要包在 ```json 標記內。"""

# 預設聊天 Prompt
# 預設聊天 Prompt
# ======================================================
# 請將這段程式碼「完全覆蓋」原本的 DEFAULT_CHAT_PROMPT 設定
# ======================================================

DEFAULT_CHAT_PROMPT = """
你是一個「蘇格拉底式引導機器人」。
你的工作**絕對不是解題**，而是**指出下一個思考點**。

【嚴格規則】：
1. **只能回傳「一個問句」**：你的 reply 必須是一個引導學生思考下一步的問題。
2. **禁止給答案**：嚴禁出現數字結果或完整算式。
3. **禁止解釋**：不要解釋原理，直接問學生「這裡該怎麼做」。

【思考邏輯】：
- 看到 $2x+5=15$，不要解 $x=5$。
- 而是問：「為了讓左邊只剩下 $2x$，那個 $+5$ 應該怎麼處理？」

- 看到 $\\sqrt{12}$，不要說 $2\\sqrt{3}$。
- 而是問：「$12$ 可以分解成哪兩個數相乘，其中一個是完全平方數？」

【JSON 輸出格式】：
你必須輸出符合此 JSON schema 的內容：
{
  "reply": "你的引導問句 (必須包含 LaTeX 格式的數學符號，如 $x$)",
  "follow_up_prompts": [
    "選項1 (例如：移項)",
    "選項2 (例如：同除)",
    "選項3 (例如：看不懂)"
  ]
}
"""

def configure_gemini(api_key, model_name):
    global gemini_model, gemini_chat
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)
    gemini_chat = gemini_model.start_chat(history=[])  # 動態設定！

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def get_ai_prompt():
    """
    從資料庫讀取 AI Prompt，若不存在則使用預設值並寫入資料庫
    """
    from models import SystemSetting, db
    
    """
    從資料庫讀取 AI Prompt，若不存在則使用預設值並寫入資料庫
    """
    from models import SystemSetting, db
    
    # DEFAULT_PROMPT 已定義在全域
    
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
                description='AI 分析學生手寫答案時使用的 Prompt 模板。必須保留 {context} 和 {prereq_text} 變數。回傳 JSON 須包含 follow_up_prompts。'
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

            model = get_model()
            resp = model.generate_content(
                [prompt, file],
                generation_config={"max_output_tokens": 4096, "temperature": 0.5}
            )
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
                    "next_question": False,
                    "follow_up_prompts": []
                }
            import time; time.sleep(1)  # 重試前延遲
        except Exception as e:
            if attempt == 1:
                return {
                    "reply": f"AI 分析失敗：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False,
                    "follow_up_prompts": []
                }
            import time; time.sleep(1)

    return {
        "reply": "AI 分析失敗，請稍後再試",
        "is_process_correct": False,
        "correct": False,
        "next_question": False,
        "follow_up_prompts": []
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
        
        resp = chat.send_message(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
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
        resp = chat.send_message(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
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
        resp = model.generate_content(
            system_prompt,
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
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


def build_chat_prompt(skill_id, user_question, full_question_context, context, prereq_skills):
    """
    Constructs the full system prompt for the chat AI.
    1. Tries to load specific prompt from SkillInfo.
    2. Falls back to SystemSetting or DEFAULT_CHAT_PROMPT.
    3. Handles variable replacement and strict JSON instruction appending.
    """
    from models import SkillInfo, SystemSetting
    
    from models import SkillInfo, SystemSetting
    
    # DEFAULT_CHAT_PROMPT 已定義在全域

    prompt_template = None

    # 1. Try to get skill-specific specific prompt
    if skill_id:
        try:
            skill = SkillInfo.query.get(skill_id)
            if skill and skill.gemini_prompt:
                prompt_template = skill.gemini_prompt
        except Exception as e:
            print(f"Error fetching skill info: {e}")

    # 2. If no skill prompt, try SystemSetting
    if not prompt_template:
        try:
            setting = SystemSetting.query.filter_by(key='chat_ai_prompt').first()
            if setting:
                prompt_template = setting.value
        except Exception:
            pass

    # 3. Use Default if still None
    if not prompt_template:
        prompt_template = DEFAULT_CHAT_PROMPT

    # 4. Construct Context Strings
    prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prereq_skills]) if prereq_skills else "無"
    
    enhanced_context = f"當前題目：{full_question_context}"
    if context and context != full_question_context:
        enhanced_context += f"\n詳細資訊：{context}"
    enhanced_context += f"\n\n此單元的前置基礎技能有：{prereq_text}。"

    # 5. Format the template
    try:
        # Check if template expects 'context' or strict format
        # For safety, we try to inject values if placeholders exist, 
        # or just append if it's a simple string.
        # But assuming our templates use {context} and {user_answer}
        full_prompt = prompt_template.format(
            user_answer=user_question,
            correct_answer="（待批改）",
            context=enhanced_context,
            prereq_text=prereq_text
        )
    except Exception:
        # Fallback formatting if template keys mismatch
        full_prompt = f"{prompt_template}\n\n[系統補完]\n題目：{enhanced_context}\n學生問題：{user_question}"

    # 6. Prepend Title (Optional, specific to requirement)
    if "【學生當前正在練習的題目】" not in full_prompt:
        full_prompt = f"【學生當前正在練習的題目】\n{full_question_context}\n\n" + full_prompt

    # 7. Append Rigid JSON Instructions
    full_prompt += """
    
    # We need to guide the student further.
    請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字。
    
    {
      "reply": "用繁體中文回答學生的問題。如果學生答錯，給予引導；如果答對，給予鼓勵。步驟用 1. 2. 3. 表示。多項式用 x^3 格式。結尾加一句鼓勵的話。注意：這裡**只要**包含回答內容，**絕對不要**包含建議的追問選項。",
      "follow_up_prompts": [
          "選項1 (觀察：針對具體錯誤點，引導觀察，15字內)",
          "選項2 (行動：提示具體修正動作，15字內)",
          "選項3 (思考：如果答對則出類似題或反問概念；如果答錯則引導驗算，15字內)"
      ]
    }
    
    直接輸出 JSON，不要 Markdown。
    請確保 `reply` 欄位只包含對學生的直接回應，而 `follow_up_prompts` 欄位包含下一步的建議選項。
    """
    
    return full_prompt

def get_chat_response(prompt):
    global gemini_chat
    if gemini_chat is None and gemini_model is not None:
        gemini_chat = gemini_model.start_chat(history=[])

    """
    取得 Gemini 的回應，並確保回傳格式為 JSON。
    """
    if not gemini_model:
        return {
            "reply": "系統尚未初始化 (API Key 可能無效)。",
            "follow_up_prompts": []
        }

    try:
        # 呼叫 Gemini
        response = gemini_chat.send_message(prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config=genai.types.GenerationConfig(
                response_mime_type='application/json', # 強制 JSON
                temperature=0.5,
                max_output_tokens=2048, # 稍微調高一點，避免 AI 加上"Here is JSON"後導致真正的 JSON 被截斷
            )
        )
        
        raw_text = response.text
        
        # 嘗試解析 (優先使用官方 JSON 模式，失敗則用強力清洗)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            cleaned_data = clean_and_parse_json(raw_text)
            
            # [關鍵修復]：如果清洗後還是 None，回傳一個安全預設值，絕對不要回傳 None！
            if cleaned_data is None:
                print(f"解析失敗，原始回傳: {raw_text}")
                return {
                    "reply": "運算發生錯誤，請試著換個方式問問看。", 
                    "follow_up_prompts": ["重試"]
                }
            return cleaned_data

    except Exception as e:
        print(f"AI 生成錯誤: {e}")
        return {
            "reply": "連線忙碌中，請稍後再試。", 
            "follow_up_prompts": ["重試"]
        }

# 預設弱點分析 Prompt
DEFAULT_WEAKNESS_ANALYSIS_PROMPT = """
你是一位專業的數學教學診斷專家。請根據以下學生的錯題記錄，使用「質性分析」方式推估各單元的熟練度。

{prompt_data}

**分析規則**：
1. **概念錯誤**：代表學生對該單元的核心概念不熟練，應大幅降低熟練度分數 (建議扣 30-50 分)
2. **計算錯誤/粗心**：代表學生概念理解但執行細節有誤，應輕微扣分 (建議扣 5-15 分)
3. **考卷資料權重**：請特別重視「考卷診斷」的結果，若考卷答錯，代表真實考試情境下的弱點，權重應高於平時練習。
4. **信心度與評語**：若 AI 評語包含正向詞彙 (如「掌握良好」、「理解正確」)，或是考卷信心度高且正確，可適度提高熟練度
5. **基準分數**：假設學生初始熟練度為 80 分，根據錯誤情況與考卷表現進行調整

請以 JSON 格式回傳分析結果：
{{
  "mastery_scores": {{
    "單元名稱1": 85,
    "單元名稱2": 60
  }},
  "overall_comment": "整體學習評語 (100 字以內)",
  "recommended_unit": "建議優先加強的單元名稱"
}}

注意：
- 熟練度分數範圍 0-100，分數越高代表越熟練
- 請務必回傳有效的 JSON 格式
- mastery_scores 的 key 必須是上述提供的單元名稱
"""

def analyze_student_weakness(prompt_data):
    """
    Calls Gemini to analyze student weakness based on mistake logs.
    """
    try:
        model = get_model() # Use shared model instance
        
        prompt = DEFAULT_WEAKNESS_ANALYSIS_PROMPT.format(prompt_data=prompt_data)
        
        response = chat.send_message(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
        ai_response_text = response.text.strip()
        
        # Clean JSON
        cleaned = re.sub(r'^```json\s*|\s*```$', '', ai_response_text, flags=re.MULTILINE)
        return json.loads(cleaned)
        
    except Exception as e:
        print(f"Weakness Analysis Error: {e}")
        return {
            "mastery_scores": {},
            "overall_comment": "分析失敗",
            "recommended_unit": ""
        }