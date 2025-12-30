import requests
import google.generativeai as genai
from flask import current_app
# 從我們剛剛改好的 config.py 匯入設定
from config import Config 

class AIResponse:
    """
    標準化回應物件：
    無論是 Gemini 還是 Local AI，回傳給主程式的結果
    都會被包裝成這個物件，統一透過 .text 屬性取得內容。
    """
    def __init__(self, text):
        self.text = text

class GeminiClient:
    """
    雲端適配器：負責跟 Google Gemini 溝通
    """
    def __init__(self, model_name=None):
        if not Config.GEMINI_API_KEY:
            error_msg = "❌ 錯誤：Gemini 模式需要設定 GEMINI_API_KEY"
            if current_app: current_app.logger.error(error_msg)
            raise ValueError(error_msg)
            
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Use provided model_name or fallback to default
        self.model_name = model_name if model_name else "gemini-1.5-flash"
        self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt):
        try:
            # Google SDK 的標準呼叫方式
            response = self.model.generate_content(prompt)
            return AIResponse(response.text)
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            if current_app: current_app.logger.error(error_msg)
            return AIResponse(error_msg)

class LocalLLMClient:
    """
    本地適配器：負責跟 Ollama (DeepSeek) 溝通
    這就是我們科展實驗的核心！
    """
    def __init__(self, model_name=None):
        self.api_url = Config.LOCAL_API_URL
        # Use provided model_name or fallback to default
        self.model_name = model_name if model_name else "qwen2.5-coder:3b"

    def generate_content(self, prompt):
        # Ollama API 的標準格式
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False, # 不使用串流，一次拿回完整結果
            "options": {
                "temperature": 0.2, # 低溫模式，讓寫程式更精確、邏輯更嚴謹
                "num_ctx": 4096     # 確保它能讀完我們長長的 13 點 Prompt
            }
        }
        try:
            # 發送請求給本機的 Ollama
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # 從 Ollama 的回傳 JSON 中提取文字
            result_text = response.json().get("response", "")
            return AIResponse(result_text)
            
        except Exception as e:
            error_msg = f"Local AI (Ollama) Error: {str(e)}\n請確認 Ollama 應用程式是否已啟動？"
            if current_app: current_app.logger.error(error_msg)
            return AIResponse(error_msg)

def get_ai_client(role='default'):
    """
    工廠函式 (Factory Function)：
    根據 role 參數從 Config.MODEL_ROLES 取得對應的 provider 與 model。
    """
    # 1. 取得角色設定，若找不到則回退到 default
    role_config = Config.MODEL_ROLES.get(role, Config.MODEL_ROLES.get('default'))
    
    # 2. 解析設定
    provider = role_config.get('provider', 'local').lower()
    model_name = role_config.get('model')
    
    # 3. 分派客戶端
    if provider == 'gemini':
        if current_app: 
            current_app.logger.info(f"✨ [AI Mode] Role: {role} -> Google Gemini ({model_name})")
        return GeminiClient(model_name)
        
    elif provider == 'local':
        if current_app: 
            current_app.logger.info(f"💻 [AI Mode] Role: {role} -> Local Ollama ({model_name})")
        return LocalLLMClient(model_name)
        
    else:
        if current_app:
            current_app.logger.warning(f"⚠️ 未知的 Provider: {provider}，強制切換至 Local 模式")
        return LocalLLMClient(model_name)