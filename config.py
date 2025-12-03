# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# === 資料庫 (絕對路徑設定) ===
# 為了避免 "雙胞胎資料庫" 問題，我們強制使用絕對路徑。

# 1. 建立 instance 資料夾的路徑 (如果不存在)
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

# 2. 構建資料庫檔案的絕對路徑
db_path = os.path.join(instance_path, 'kumon_math.db')

# 3. 設定資料庫連線 URI
# 使用 f-string 和三個斜線開頭來表示本地檔案系統的絕對路徑
SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# === 檔案上傳 ===
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

# === 安全 ===
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

# === Gemini AI ===
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL_NAME = "gemini-2.5-flash"  # 或 gemini-1.5-flash-latest
CHAT_PROMPT_TEMPLATE = "你是功文數學 AI 助教，用繁體中文親切回答高職學生：{question}。解釋要簡單、步驟清楚，適合數學弱勢學生。"