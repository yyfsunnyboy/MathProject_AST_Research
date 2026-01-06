# -*- coding: utf-8 -*-
# ==============================================================================
# Module: core/ai_wrapper.py
# Project: AI-Driven Math Problem Generator (Taiwan Junior High School Curriculum)
# Version: v7.7.5 (Universal Adapter)
# Last Updated: 2026-01-06
# Author: Senior Python Architect & R&D Team
#
# Description:
#   本模組擔任「AI 模型驅動層 (AI Driver Layer)」的角色。
#   它負責將上層業務邏輯 (Architect/Coder) 與底層 AI 供應商 (Google/Ollama) 解耦。
#   無論 Config 如何設定，上層只需呼叫 get_ai_client()，無需關心底層實作。
#
# Key Features:
#   1. **Factory Pattern**: 透過 get_ai_client() 自動派發 GoogleAIClient 或 LocalAIClient。
#   2. **Config Adaptive**: 自動適配 config.py 中的 GEMINI_API_KEY 與 LOCAL_API_URL 變數名。
#   3. **Provider Agnostic**: 同時支援 'google', 'gemini' (雲端) 與 'local' (本地) 關鍵字。
#   4. **Error Handling**: 封裝 API 連線錯誤，回傳 MockResponse 避免主程式崩潰。
#
# Change Log (v7.7.5):
#   - [Fix] 修正 Config 變數對接問題 (支援 GEMINI_API_KEY, LOCAL_API_URL)。
#   - [Refactor] 統一 Google/Gemini Provider 的判斷邏輯。
# ==============================================================================

import os
import requests
import json
import logging
import google.generativeai as genai
from flask import current_app
from config import Config

# 設定 Logger
logger = logging.getLogger(__name__)

class LocalAIClient:
    """
    處理 Local Ollama API 的客戶端
    負責與本地運行的 Ollama 服務 (預設 Port 11434) 進行通訊。
    """
    def __init__(self, model_name, temperature=0.7):
        # [Config Adaption] 自動讀取 config.py 中的 LOCAL_API_URL，若無則使用預設值
        self.api_url = getattr(Config, 'LOCAL_API_URL', "http://localhost:11434/api/generate")
        self.model = model_name
        self.temperature = temperature

    def generate_content(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096  # 確保上下文足夠長，避免程式碼被截斷
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=600) # 延長 Timeout 防止 8B 模型回應過慢
            response.raise_for_status()
            result = response.json()
            
            # 模擬 Google Response 物件介面
            class MockResponse:
                def __init__(self, text): self.text = text
            return MockResponse(result.get("response", ""))
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Local AI (Ollama) Error: {str(e)}\n請確認 Ollama 應用程式是否已啟動？"
            logger.error(error_msg)
            # 回傳錯誤訊息，確保主流程不中斷
            class MockResponse:
                def __init__(self, text): self.text = error_msg
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

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature

    def generate_content(self, prompt):
        try:
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

    # 2. 智慧派發 (Smart Dispatch)
    # 同時支援 'google' 和 'gemini' 標籤，增加設定檔的容錯率
    if provider in ['google', 'gemini']:
        return GoogleAIClient(model_name, temperature)
    elif provider == 'local':
        return LocalAIClient(model_name, temperature)
    else:
        logger.warning(f"⚠️ 未知的 Provider: {provider}，強制切換至 Local 模式")
        return LocalAIClient(model_name, temperature)