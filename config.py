# config.py
import os

# === 資料庫 ===
# 使用相對路徑，Flask 會自動將其放在專案的 'instance' 資料夾中。
# 這是 Flask 推薦的最佳實踐，可以將執行時資料與原始碼分離。
SQLALCHEMY_DATABASE_URI = 'sqlite:///math_master.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# === 安全 ===
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

# === Gemini AI ===
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL_NAME = "gemini-2.5-flash"  # 或 gemini-1.5-flash-latest
CHAT_PROMPT_TEMPLATE = "你是功文數學 AI 助教，用繁體中文親切回答高職學生：{question}。解釋要簡單、步驟清楚，適合數學弱勢學生。"