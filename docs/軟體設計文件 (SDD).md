功文數學 AI 助教 - 軟體設計文件 (SDD)

1. 系統架構

1.1 整體架構 (檔案結構)

math-master/
├── app.py               # Flask 應用程式主體、路由
├── models.py           # SQLAlchemy 資料庫模型
├── import_data.py      # 初始資料匯入腳本
├── config.py           # 應用程式設定
├── requirements.txt    # Python 依賴套件
├── .env                # (需手動建立) 儲存 API 金鑰與密鑰
├── templates/            # Jinja2 前端 HTML 樣板
│   └── ...
├── static/               # CSS, JavaScript, 圖片等靜態檔案
│   └── ...
├── skills/               # 數學技能模組 (題目生成、批改邏輯)
│   └── ...
├── core/                 # 核心輔助功能 (如 AI 串接)
│   └── gemini_analysis.py
└── document/             # 原始資料 (CSV 檔案)
    ├── skills_info.csv
    └── skill_curriculum.csv


1.2 技術堆疊 (Tech Stack)

後端框架: Flask

ORM: Flask-SQLAlchemy

資料庫: SQLite (開發/生產)

前端: HTML, CSS, JavaScript

模板引擎: Jinja2

AI 服務: Google Gemini API

認證: Flask-Login (Session-based)

資料處理: pandas (用於 import_data.py)

2. 資料庫設計

2.1 概念 ER 圖 (Mermaid)

erDiagram
    User ||--|{ UserProgress : "有"
    Skill ||--|{ UserProgress : "的進度"
    Skill ||--|{ SkillCurriculumMapping : "對應到"
    Curriculum ||--|{ SkillCurriculumMapping : "的課綱"

    User {
        int id PK
        string username
        string password_hash
    }
    Skill {
        string id PK
        string name
        string ai_prompt
        bool is_active
    }
    Curriculum {
        int id PK
        string type
        string book
        string chapter
        string section
    }
    UserProgress {
        int user_id FK
        string skill_id FK
        int current_level
        int consecutive_correct
    }
    SkillCurriculumMapping {
        string skill_id FK
        int curriculum_id FK
    }


2.2 資料表設計

User (使用者)

id: INTEGER PRIMARY KEY

username: TEXT UNIQUE NOT NULL

password_hash: TEXT NOT NULL

Skill (技能單元)

id: TEXT PRIMARY KEY (例如 "SKILL_001")

name: TEXT NOT NULL

description: TEXT

ai_prompt: TEXT (此單元專屬的 AI 提示)

is_active: BOOLEAN

Curriculum (課綱結構)

id: INTEGER PRIMARY KEY

type: TEXT NOT NULL (例如 "普通高中")

book: TEXT NOT NULL (例如 "第一冊")

chapter: TEXT NOT NULL (例如 "第一章")

section: TEXT NOT NULL (例如 "1-1")

SkillCurriculumMapping (技能課綱對應)

skill_id: TEXT (Foreign Key -> Skill.id)

curriculum_id: INTEGER (Foreign Key -> Curriculum.id)

UserProgress (使用者進度)

user_id: INTEGER (Foreign Key -> User.id)

skill_id: TEXT (Foreign Key -> Skill.id)

current_level: INTEGER (目前難度等級)

consecutive_correct: INTEGER (連續答對次數)

3. 模組設計

3.1 技能模組介面 (skills/ Concept)

skills/ 目錄下的每個檔案代表一個技能，需提供至少兩個方法：

# 概念性介面 (非-真實-繼承)
class BaseSkillModule:
    def generate_question(self, level: int) -> dict:
        """
        依據等級生成題目
        @return: {'question_text': '...', 'correct_answer': '...'}
        """
        pass
        
    def check_answer(self, question_data: dict, user_answer: str) -> bool:
        """
        批改使用者答案
        """
        pass


3.2 AI 服務介面 (core/gemini_analysis.py)

封裝對 Google Gemini API 的呼叫：

class AIService:
    def __init__(self, api_key: str):
        """初始化 Gemini Client"""
        pass

    def get_text_response(self, prompt: str) -> str:
        """
        傳送純文字提示，取得 AI 回覆
        """
        pass
        
    def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """
        傳送圖片與提示，分析手寫內容
        """
        pass


4. API 設計 (Web 路由)

本系統主要為網頁應用，API 多為內部 AJAX 呼叫。

4.1 頁面路由 (Page Routes)

GET /: 儀表板 (Dashboard)，顯示課綱

GET /login: 登入頁面

POST /login: 處理登入請求

GET /register: 註冊頁面

POST /register: 處理註冊請求

GET /logout: 處理登出

GET /practice/<skill_id>: 練習作答頁面

4.2 核心 API (AJAX Endpoints)

POST /submit_answer: (需登入)

Request: {'skill_id': '...', 'answer': '...', 'question_data': {...}}

Response: {'is_correct': true/false, 'new_level': 5, 'consecutive_correct': 3}

POST /tutor_chat: (需登入)

Request: {'message': '...', 'skill_id': '...'}

Response: {'reply': '...'}

POST /tutor_image_analysis: (需登入)

Request: {'image': 'data:image/png;base64,...', 'skill_id': '...'}

Response: {'analysis': '...'}

4.3 管理介面路由 (Admin Routes)

GET /admin/skills: 技能單元管理頁面

POST /admin/skills/add: 新增技能

POST /admin/skills/edit/<id>: 編輯技能

GET /admin/skills/delete/<id>: 刪除技能

GET /admin/curriculum: 課程分類管理頁面

POST /admin/curriculum/map: 對應技能與課綱

GET /admin/db_maintenance: 資料庫維護頁面

POST /admin/db_maintenance/action: 執行維護操作 (清空/上傳/刪除)

5. 安全設計

5.1 認證機制

使用 Flask-Login 管理使用者 Session。

登入與註冊時，密碼使用 werkzeug.security (Flask 內建) 進行 generate_password_hash 雜湊儲存，並使用 check_password_hash 進行驗證。

5.2 權限控制

核心 API (AJAX) 路由使用 @login_required 裝飾器保護，確保只有登入使用者能存取。

管理介面 (/admin/*) 路由應增加額外的管理員身分檢查 (例如 if current_user.is_admin: )。

5.3 敏感資訊

GEMINI_API_KEY 和 SECRET_KEY 必須儲存在 .env 檔案中，並使用 python-dotenv 載入。

.env 檔案必須被加入 .gitignore，嚴禁上傳至版本控制。

6. 測試策略 (建議)

6.1 單元測試

Skills: 測試 skills/ 目錄下各模組的 generate_question 和 check_answer 邏輯是否正確。

Models: 測試 models.py 中 User 模型的密碼設定/檢查功能。

6.2 整合測試

Auth Flow: 測試 註冊 -> 登入 -> 登出 流程是否正常。

Learn Flow: 測試 選擇單元 -> 答題 (答對/答錯) -> UserProgress 資料庫是否正確更新 (進階/退階)。

AI Flow: 測試 /tutor_chat 和 /tutor_image_analysis 路由是否能正確串接 AI 服務並返回結果。

7. 部署架構

7.1 開發環境

# 1. 建立虛擬環境
python -m venv venv
# 2. 啟用虛擬環境 (Windows)
.\venv\Scripts\activate
# 3. 安裝依賴
pip install -r requirements.txt
# 4. (手動建立 .env 檔案)
# 5. 初始化資料庫
python import_data.py
# 6. 執行應用程式
python app.py


7.2 生產環境 (建議)

使用更強健的 WSGI 伺服器，並使用反向代理。

[Nginx (反向代理)] -> [Gunicorn (WSGI 伺服器)] -> [Flask App] -> [SQLite 檔案]


註：若未來流量增大，SQLite 可替換為 PostgreSQL 或 MySQL，僅需修改 config.py 中的 SQLALCHEMY_DATABASE_URI 並安裝對應驅動。