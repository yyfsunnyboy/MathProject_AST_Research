import os

# 取得目前檔案所在的目錄 (絕對路徑)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    全域設定檔 (Global Configuration)
    包含：資料庫、檔案上傳、以及科展專用的 AI 雙模組設定
    """

    # ==========================================
    # 1. 資料庫設定 (SQLite)
    # ==========================================
    # 建立 instance 資料夾 (如果不存在)
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # 構建資料庫檔案的絕對路徑
    db_path = os.path.join(instance_path, 'kumon_math.db')
    
    # 設定連線 URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # 2. 檔案系統設定
    # ==========================================
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 確保上傳目錄存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ==========================================
    # 3. 安全設定
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

    # ==========================================
    # 4. ★★★ AI 雙模組設定 (科展實驗核心) ★★★
    # ==========================================
    
    # 策略開關：'local' (本地端) 或 'gemini' (雲端)
    # 從環境變數讀取，若無則預設為 'local' (直接使用 DeepSeek R1)
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'local')

    # --- [Cloud] Google Gemini 設定 ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    # 標準名稱 gemini-2.5-flash 
    GEMINI_MODEL_NAME = "gemini-2.5-flash" 
    
    CHAT_PROMPT_TEMPLATE = "你是功文數學 AI 助教，用繁體中文親切回答高職學生：{question}。解釋要簡單、步驟清楚，適合數學弱勢學生。"

    # --- [Local] Ollama / DeepSeek 設定 ---
    # 這是 Ollama 的標準 API 接口
    LOCAL_API_URL = "http://localhost:11434/api/generate"
    # 使用我們剛剛下載的 DeepSeek R1 (8B)
    #LOCAL_MODEL_NAME = "deepseek-r1:8b"
    # ★★★ 修改這裡：換成剛下載的極速版 ★★★
    LOCAL_MODEL_NAME = "qwen2.5-coder:1.5b"