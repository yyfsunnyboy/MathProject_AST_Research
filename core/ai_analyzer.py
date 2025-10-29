# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json

# 移除 current_app，改用傳入 app
def configure_gemini(app):
    genai.configure(api_key=app.config['GEMINI_API_KEY'])

def analyze(image_data_url, context, app):
    try:
        _, b64 = image_data_url.split(',', 1)
        img_data = base64.b64decode(b64)
        file = genai.upload_file(file_bytes=img_data, mime_type="image/png")
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"題目：{context}\n分析學生手寫計算紙，回傳 JSON：{{'reply': '...', 'is_graph_correct': true/false, 'correct': true/false}}"
        resp = model.generate_content([prompt, file])
        text = resp.text.strip().replace('```json', '').replace('```', '')
        return json.loads(text)
    except Exception as e:
        return {"reply": f"AI 錯誤：{e}", "is_graph_correct": False, "correct": False}