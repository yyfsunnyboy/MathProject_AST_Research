# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json
import tempfile
import os
from flask import current_app

gemini_model = None

def configure_gemini(api_key, model_name):
    global gemini_model
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)  # 動態設定！

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def analyze(image_data_url, context, api_key):
    try:
        # 解碼 base64
        _, b64 = image_data_url.split(',', 1)
        img_data = base64.b64decode(b64)

        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(img_data)
            temp_file_path = temp_file.name

        # 上傳檔案
        file = genai.upload_file(path=temp_file_path)

        # 改用新模型（Gemini 2.5 Flash）
        model = genai.GenerativeModel("gemini-2.5-flash")  # 關鍵修改！

        prompt = f"""
        題目：{context}
        分析學生手寫計算紙：
        - 步驟是否正確？
        - 是否遺漏？
        - 給出具體建議（Markdown）
        回傳 JSON：
        {{
          "reply": "建議",
          "is_graph_correct": true/false,
          "correct": true/false,
          "next_question": true/false
        }}
        """

        # 生成內容
        resp = model.generate_content([prompt, file])
        text = resp.text.strip().replace('```json', '').replace('```', '')
        result = json.loads(text)

        # 刪除臨時檔案
        os.unlink(temp_file_path)

        return result
    except Exception as e:
        return {
            "reply": f"AI 分析失敗：{str(e)}",
            "is_graph_correct": False,
            "correct": False,
            "next_question": False
        }
    
def ask_ai_text(user_question):
    try:
        model = get_model()
        prompt = f"你是功文數學 AI 助教，用繁體中文親切回答：{user_question}"
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI 錯誤：{str(e)}"