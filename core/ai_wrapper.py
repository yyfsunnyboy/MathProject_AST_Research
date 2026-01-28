# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/ai_wrapper.py
功能說明 (Description): AI 模型驅動層 (AI Driver Layer)，負責將業務邏輯與底層 AI 供應商 (Google/Ollama) 解耦，並根據角色 (Role) 自動調度合適的模型。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# ==============================================================================

import os
import requests
import json
import logging
# [Fix] Migrate from deprecated 'google.generativeai' to 'google.genai'
try:
    from google import genai
except ImportError:
    # Fallback to old package if new one is not installed (though warning suggests it's deprecated)
    import google.generativeai as genai # Compat
    print("[WARN] Using deprecated 'google.generativeai'. Please upgrade to 'google-genai'.")
from flask import current_app
from config import Config

# 設定 Logger
logger = logging.getLogger(__name__)

class LocalAIClient:
    """
    處理 Local Ollama API 的客戶端
    負責與本地運行的 Ollama 服務 (預設 Port 11434) 進行通訊。
    """
    def __init__(self, model_name, temperature=0.7, **kwargs):
        # [Config Adaption] 自動讀取 config.py 中的 LOCAL_API_URL，若無則使用預設值
        self.api_url = getattr(Config, 'LOCAL_API_URL', "http://localhost:11434/api/generate")
        self.model = model_name
        self.temperature = temperature
        
        # [V2.1 Refactor] 動態接收配置參數
        self.max_tokens = kwargs.get('max_tokens', 4096)
        self.extra_options = kwargs.get('extra_body', {})

    def generate_content(self, prompt):
        # 基礎 options
        options = {
            "temperature": self.temperature,
            "num_predict": self.max_tokens,
            "num_ctx": 8192  # Default fallback
        }
        
        # 合併 extra_body 中的參數 (如 num_ctx, num_gpu 等)
        # config.py 的設定優先權高於預設值
        if self.extra_options:
            options.update(self.extra_options)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json()
            
            # 取出 Ollama 回傳的真正內容與 token 計數
            generated_text = result.get("response", "")
            prompt_tokens = result.get("prompt_eval_count", 0)
            completion_tokens = result.get("eval_count", 0)
            
            # 建立一個帶 usage 的 MockResponse（模擬 OpenAI / Gemini 風格）
            class MockResponse:
                def __init__(self, text, prompt_t, comp_t):
                    self.text = text
                    self.usage = type('Usage', (), {})()   # 簡單的 namespace
                    self.usage.prompt_tokens = prompt_t
                    self.usage.completion_tokens = comp_t
                    self.usage.total_tokens = prompt_t + comp_t
            
            return MockResponse(generated_text, prompt_tokens, completion_tokens)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Local AI (Ollama) Error: {str(e)}\n請確認 Ollama 是否正在運行於 {self.api_url}"
            logger.error(error_msg)
            class MockResponse:
                def __init__(self, text): 
                    self.text = error_msg
                    self.usage = type('Usage', (), {})()
                    self.usage.prompt_tokens = 0
                    self.usage.completion_tokens = 0
            return MockResponse(error_msg)

class GoogleAIClient:
    """
    處理 Google Gemini API 的客戶端
    負責與 Google Generative AI 服務進行通訊 (需連網)。
    """
    def __init__(self, model_name, temperature=0.7):
        # [Config Adaption] 自動讀取 config.py 中的 GEMINI_API_KEY
        api_key = getattr(Config, 'GEMINI_API_KEY', None)
        
        # 雙重保險：如果 Config 物件沒抓到，嘗試從系統環境變數抓
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found! Please check your config.py or .env file.")
            raise ValueError("GEMINI_API_KEY is missing. 無法啟動 Google AI Client。")

        # [SDK Compat] Check if using new SDK (google.genai) or old SDK (google.generativeai)
        if hasattr(genai, 'Client'):
            # New SDK (google.genai)
            self.client = genai.Client(api_key=api_key)
            self.model_name = model_name
            self.is_new_sdk = True
        else:
            # Old SDK (google.generativeai)
            if hasattr(genai, 'configure'):
                genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.is_new_sdk = False
            
        self.temperature = temperature

    def generate_content(self, prompt):
        try:
            if getattr(self, 'is_new_sdk', False):
                # New SDK usage
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={"temperature": self.temperature}
                )
                return response
            else:
                # Old SDK usage
                config = genai.GenerationConfig(temperature=self.temperature)
                response = self.model.generate_content(prompt, generation_config=config)
                return response
        except Exception as e:
            error_msg = f"Google AI Error: {str(e)}"
            logger.error(error_msg)
            class MockResponse:
                def __init__(self, text): self.text = f"Error: {text}"
            return MockResponse(error_msg)

def get_ai_client(role='default'):
    """
    [Factory Method] AI 客戶端工廠
    根據 config.py 中 MODEL_ROLES 的設定，實例化對應的 Client (Local 或 Google)。
    
    Args:
        role (str): 角色名稱 (e.g., 'architect', 'coder', 'vision_analyzer')
    
    Returns:
        LocalAIClient or GoogleAIClient
    """
    # 1. 讀取角色設定
    role_config = Config.MODEL_ROLES.get(role, Config.MODEL_ROLES.get('default'))
    
    provider = role_config.get('provider', 'local').lower()
    model_name = role_config.get('model', 'qwen2.5-coder:7b')
    temperature = role_config.get('temperature', 0.7)
    
    # [V2.1 Refactor] 提取更多配置參數
    max_tokens = role_config.get('max_tokens', 4096)
    extra_body = role_config.get('extra_body', {})

    # 2. 智慧派發 (Smart Dispatch)
    # 同時支援 'google' 和 'gemini' 標籤，增加設定檔的容錯率
    if provider in ['google', 'gemini']:
        return GoogleAIClient(model_name, temperature)
    elif provider == 'local':
        return LocalAIClient(model_name, temperature, max_tokens=max_tokens, extra_body=extra_body)
    else:
        logger.warning(f"⚠️ 未知的 Provider: {provider}，強制切換至 Local 模式")
        return LocalAIClient(model_name, temperature, max_tokens=max_tokens, extra_body=extra_body)