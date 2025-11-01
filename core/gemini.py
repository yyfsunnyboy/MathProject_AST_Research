# core/gemini.py
import google.generativeai as genai

gemini_model = None

def configure_gemini(api_key, model_name='gemini-1.5-flash'):
    global gemini_model
    if gemini_model is not None:
        return
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)
    print(f"[Gemini] 初始化成功：{model_name}")

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！請先呼叫 configure_gemini()")
    return gemini_model