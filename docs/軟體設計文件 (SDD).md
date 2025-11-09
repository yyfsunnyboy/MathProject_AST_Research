# 功文數學學習平台 - 軟體設計文件 (SDD)

## 1. 系統架構

### 1.1 整體架構 (檔案結構)

```

math-master/
├── app.py               \# Flask 應用程式主體、路由
├── models.py           \# SQLAlchemy 資料庫模型
├── import\_data.py      \# 初始資料匯入腳本
├── config.py           \# 應用程式設定
├── requirements.txt    \# Python 依賴套件
├── .env                \# (需手動建立) 儲存 API 金鑰與密鑰
├── templates/            \# Jinja2 前端 HTML 樣板
│   └── ...
├── static/               \# CSS, JavaScript, 圖片等靜態檔案
│   └── ...
├── skills/               \# 數學技能模組 (題目生成、批改邏輯)
│   └── ...
├── core/                 \# 核心輔助功能 (如 AI 串接)
│   └── gemini\_analysis.py
└── document/             \# 原始資料 (CSV 檔案)
├── skills\_info.csv
└── skill\_curriculum.csv

````

### 1.2 技術堆疊 (Tech Stack)

* **後端框架**: Flask
* **ORM**: Flask-SQLAlchemy
* **資料庫**: SQLite (開發/生產)
* **前端**: HTML, CSS, JavaScript
* **模板引擎**: Jinja2
* **AI 服務**: Google Gemini API
* **認證**: Flask-Login (Session-based)
* **資料處理**: pandas (用於 `import_data.py`)

---

## 2. 資料庫設計

### 2.1 概念 ER 圖 (Mermaid)

```mermaid
erDiagram
    users ||--o{ progress : "記錄 (FK: user_id)"
    skills_info ||--o{ progress : "的進度 (FK: skill_id)"
    skills_info ||--o{ skill_curriculum : "對應到 (FK: skill_id)"

    users {
        INTEGER id PK "主鍵"
        TEXT username
        TEXT password_hash
        TEXT email
        DATETIME created_at
    }

    skills_info {
        TEXT skill_id PK "技能唯一ID"
        TEXT skill_ch_name
        TEXT category
        TEXT gemini_prompt
        INTEGER consecutive_correct_required
        BOOLEAN is_active
    }

    progress {
        INTEGER user_id FK
        TEXT skill_id FK
        INTEGER current_level
        INTEGER consecutive_correct
        INTEGER consecutive_wrong
        INTEGER questions_solved
        DATETIME last_practiced
        PRIMARY KEY (user_id, skill_id)
    }

    skill_curriculum {
        INTEGER id PK
        TEXT skill_id FK
        TEXT curriculum
        TEXT grade
        TEXT volume "冊別"
        TEXT chapter
        TEXT section
        TEXT paragraph "段落 (可選)"
        INTEGER display_order
        INTEGER difficulty_level "難易度"
    }
````

### 2.2 資料表設計 (Table Schema)

#### `users` (使用者帳號資訊)

  * 儲存使用者的登入帳號與密碼等基本資料。這是 flask-login 擴充套件運作的基礎。
  * **`id`**: INTEGER, 主鍵 (PK) - 使用者的唯一識別碼。
  * **`username`**: TEXT - 用於登入的使用者名稱。
  * **`password_hash`**: TEXT - 經過雜湊 (hashing) 處理的密碼。
  * **`email`**: TEXT - 使用者信箱，可用於找回密碼。
  * **`created_at`**: DATETIME - 帳號建立時間。

#### `skills_info` (技能目錄表)

  * 技能的「總目錄」。定義了系統中有哪些練習單元、它們的名稱、描述、以及晉級門檻等靜態資訊。
  * **`skill_id`**: TEXT, 主鍵 (PK) - 技能的唯一英文 ID，對應到程式碼檔案名稱。
  * **`skill_en_name`**: TEXT - 技能的英文名稱。
  * **`skill_ch_name`**: TEXT - 技能的中文顯示名稱 (例如：「餘式定理」)。
  * **`category`**: TEXT - 技能類別 (如三角函數、向量等)。
  * **`description`**: TEXT - 對此技能的簡短描述。
  * **`input_type`**: TEXT - 題目類型 (例如: text 或 handwriting)。
  * **`gemini_prompt`**: TEXT - 針對此技能，給予 AI 助教的特定提示詞 (Prompt) 模板。
  * **`consecutive_correct_required`**: INTEGER - 需要連續答對幾題才能提升等級。
  * **`is_active`**: BOOLEAN - 此技能是否啟用 (1 為啟用，0 為停用)。
  * **`order_index`**: INTEGER - 用於在儀表板上對技能進行排序。

#### `progress` (學習進度動態記錄)

  * 學習進度的「動態記錄本」。記錄了哪位使用者在哪個技能上的詳細學習狀況。
  * **`id`**: INTEGER, 主鍵 (PK) - 記錄的唯一識別碼。
  * **`user_id`**: INTEGER, 外鍵 (FK) - 對應到 `users` 表的 `id`。
  * **`skill_id`**: TEXT, 外鍵 (FK) - 對應到 `skills_info` 表的 `skill_id`。
  * **`current_level`**: INTEGER - 使用者在此技能的目前等級 (例如：1-10級)。
  * **`consecutive_correct`**: INTEGER - 連續答對次數 (答錯時會歸零)。
  * **`consecutive_wrong`**: INTEGER - 連續答錯次數 (用於判斷是否降級)。
  * **`questions_solved`**: INTEGER - 在此技能總共完成的題數。
  * **`last_practiced`**: DATETIME - 上次練習此技能的時間。

#### `skill_curriculum` (課程結構地圖)

  * 課程的「地圖」。用來定義普高、技高的課程結構，將 `skills_info` 中的技能組織成有層次的冊、章、節。
  * **`id`**: INTEGER, 主鍵 (PK) - 記錄的唯一識別碼。
  * **`skill_id`**: TEXT, 外鍵 (FK) - 對應到 `skills_info` 表的 `skill_id`。
  * **`curriculum`**: TEXT - 課綱 (例如: general, vocational)。
  * **`grade`**: TEXT - 年級 (例如: 1, 2, 3)。
  * **`volume`**: TEXT - 所屬冊別 (例如: B1, B2, C1, C2)。
  * **`chapter`**: TEXT - 所屬章節 (例如：「第一章 多項式」)。
  * **`section`**: TEXT - 所屬小節 (例如：「1-2 餘式定理」)。
  * **`paragraph`**: TEXT - (可選) 更細的段落劃分。
  * **`display_order`**: INTEGER - 在同一章節內的顯示順序。
  * **`diffcult_level`**: INTEGER - 難易度 (例如: 1, 2)。
  * **`last_practiced`**: DATETIME - (建議欄位) 上次練習此技能的時間。

-----

## 3\. 模組設計

### 3.1 技能模組介面 (skills/ Concept)

`skills/` 目錄下的每個檔案代表一個技能，需提供至少兩個方法：

```python
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
```

### 3.2 AI 服務介面 (core/gemini\_analysis.py)

封裝對 Google Gemini API 的呼叫：

```python
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
```

-----

## 4\. API 設計 (Web 路由)

本系統主要為網頁應用，API 多為內部 AJAX 呼叫。

### 4.1 頁面路由 (Page Routes)

  * `GET /`: 儀表板 (Dashboard)，顯示課綱
  * `GET /login`: 登入頁面
  * `POST /login`: 處理登入請求
  * `GET /register`: 註冊頁面
  * `POST /register`: 處理註冊請求
  * `GET /logout`: 處理登出
  * `GET /practice/<skill_id>`: 練習作答頁面

### 4.2 核心 API (AJAX Endpoints)

  * `POST /submit_answer`: (需登入)
      - **Request**: `{'skill_id': '...', 'answer': '...', 'question_data': {...}}`
      - **Response**: `{'is_correct': true/false, 'new_level': 5, 'consecutive_correct': 3}`
  * `POST /tutor_chat`: (需登入)
      - **Request**: `{'message': '...', 'skill_id': '...'}`
      - **Response**: `{'reply': '...'}`
  * `POST /tutor_image_analysis`: (需登入)
      - **Request**: `{'image': 'data:image/png;base64,...', 'skill_id': '...'}`
      - **Response**: `{'analysis': '...'}`

### 4.3 管理介面路由 (Admin Routes)

  * `GET /admin/skills`: 技能單元管理頁面
  * `POST /admin/skills/add`: 新增技能
  * `POST /admin/skills/edit/<id>`: 編輯技能
  * `GET /admin/skills/delete/<id>`\_ : 刪除技能
  * `GET /admin/curriculum`: 課程分類管理頁面
  * `POST /admin/curriculum/map`: 對應技能與課綱
  * `GET /admin/db_maintenance`: 資料庫維護頁面
  * `POST /admin/db_maintenance/action`: 執行維護操作 (清空/上傳/刪除)

-----

## 5\. 安全設計

### 5.1 認證機制

  * 使用 **Flask-Login** 管理使用者 Session。
  * 登入與註冊時，密碼使用 `werkzeug.security` (Flask 內建) 進行 `generate_password_hash` 雜湊儲存，並使用 `check_password_hash` 進行驗證。

### 5.2 權限控制

  * 核心 API (AJAX) 路由使用 `@login_required` 裝飾器保護，確保只有登入使用者能存取。
  * 管理介面 (`/admin/*`) 路由應增加額外的管理員身分檢查 (例如 `if current_user.is_admin:` )。

### 5.3 敏感資訊

  * `GEMINI_API_KEY` 和 `SECRET_KEY` 必須儲存在 `.env` 檔案中，並使用 `python-dotenv` 載入。
  * `.env` 檔案必須被加入 `.gitignore`，嚴禁上傳至版本控制。

-----

## 6\. 測試策略 (建議)

### 6.1 單元測試

  * **Skills**: 測試 `skills/` 目錄下各模組的 `generate_question` 和 `check_answer` 邏輯是否正確。
  * **Models**: 測試 `models.py` 中 User 模型的密碼設定/檢查功能。

### 6.2 整合測試

  * **Auth Flow**: 測試 註冊 -\> 登入 -\> 登出 流程是否正常。
  * **Learn Flow**: 測試 選擇單元 -\> 答題 (答對/答錯) -\> `progress` 資料庫是否正確更新 (進階/退階)。
  * **AI Flow**: 測試 `/tutor_chat` 和 `/tutor_image_analysis` 路由是否能正確串接 AI 服務並返回結果。

-----

## 7\. 部署架構

### 7.1 開發環境

  * **建立虛擬環境**
  * python -m venv venv
  * **啟用虛擬環境 (Windows)**
  * .\venv\Scripts\activate
  * **安裝依賴**
  * pip install -r requirements.txt
  * **(手動設定 .env 檔案)**
  * $env:GEMINI_API_KEY = "你的金鑰"
  * **執行應用程式**
  * python app.py

### 7.2 生產環境 (建議)

使用更強健的 WSGI 伺服器，並使用反向代理。

```
[Nginx (反向代理)] -> [Gunicorn (WSGI 伺服器)] -> [Flask App] -> [SQLite 檔案]
```

*註：若未來流量增大，`SQLite` 可替換為 `PostgreSQL` 或 `MySQL`，僅需修改 `config.py` 中的 `SQLALCHEMY_DATABASE_URI` 並安裝對應驅動。*

```
```