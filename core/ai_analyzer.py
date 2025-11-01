# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json
import tempfile
import os
import re
from flask import current_app

def configure_gemini(api_key, model_name):
    global gemini_model
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)  # 動態設定！

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def analyze(image_data_url, context, api_key):
    """
    強制 Gemini 回傳純 JSON，失敗時自動重試一次
    """
    def _call_gemini():
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

            # 強制 JSON 輸出 Prompt
            prompt = f"""你是一位數學助教，正在批改學生手寫的計算紙。
題目：{context}

請**嚴格按照以下 JSON 格式回覆**，不要加入任何多餘文字、問候或解釋：

{{
  "reply": "用 Markdown 格式寫出具體建議（步驟對錯、遺漏、改進點）",
  "is_graph_correct": true 或 false,
  "correct": true 或 false,
  "next_question": true 或 false
}}

直接輸出 JSON 內容，不要包在 ```json 標記內。"""

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
                    "is_graph_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)  # 重試前延遲
        except Exception as e:
            if attempt == 1:
                return {
                    "reply": f"AI 分析失敗：{str(e)}",
                    "is_graph_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)

    return {
        "reply": "AI 分析失敗，請稍後再試",
        "is_graph_correct": False,
        "correct": False,
        "next_question": False
    }
    
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
    