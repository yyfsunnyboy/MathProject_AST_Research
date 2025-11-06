# 功文數學 AI 助教 (Kumon Math AI Tutor)

這是一個基於 Flask 框架開發的個人化數學學習平台。專案的核心精神源自「功文式教育」，旨在提供一個自適應的學習環境，讓學生能夠在感到舒適的難度下進行大量練習，並在遇到困難時適時獲得 AI 輔助，從而鞏固基礎、建立信心。

## 主要功能 (Main Features)

1.  **自適應學習系統 (Adaptive Learning)**
    *   **功文式進退階**：系統會根據學生的連續答對/答錯次數，自動調整練習題的難度等級。連續答對可晉級，連續答錯則會退回一個等級以鞏固基礎。
    *   **個人化進度追蹤**：每位使用者擁有獨立的學習進度，系統會記錄每個技能單元的練習次數、等級和連續答對情況。

2.  **AI 整合 (AI Integration)**
    *   **Gemini AI 助教**：整合 Google Gemini AI 模型，提供即時的文字問答和解題輔助。
    *   **手寫辨識與分析**：使用者可以上傳手寫的計算過程圖片，AI 會進行分析並給出批改建議。

3.  **使用者與課程管理 (User & Curriculum Management)**
    *   **使用者認證**：提供使用者註冊、登入、登出功能。
    *   **雙軌課程系統**：儀表板支援「普通高中」與「技術型高中」兩種課程綱要的切換與瀏覽。
    *   **階層式課程瀏覽**：使用者可以從「課綱 -> 冊別 -> 章 -> 節」的層級結構中選擇要練習的技能。

4.  **強大的管理後台 (Admin Panel)**
    *   **單元管理 (`/admin/skills`)**：新增、編輯、刪除和啟用/停用數學技能單元，並可為每個技能設定專屬的 AI 提示 (Prompt)。
    *   **課程分類管理 (`/admin/curriculum`)**：將技能單元精確地對應到不同課綱的特定章節段落中。
    *   **資料庫維護 (`/admin/db_maintenance`)**：一個強大的後台工具，允許管理員：
        *   檢視所有資料庫表格。
        *   清空指定表格的所有資料。
        *   從 Excel 檔案上傳資料到指定表格。
        *   永久刪除整個資料庫表格（請謹慎使用）。

## 技術棧 (Tech Stack)

-   **後端 (Backend)**: Python, Flask
-   **資料庫 (Database)**: SQLite
-   **ORM**: Flask-SQLAlchemy
-   **前端 (Frontend)**: HTML, CSS, JavaScript
-   **AI 模型 (AI Model)**: Google Gemini
-   **Python 套件 (Libraries)**: `pandas`, `Flask-Login`, `python-dotenv`

---

## 安裝與執行 (Installation and Setup)

請依照以下步驟在您的本機環境中設定並執行此專案。

### 步驟一：環境準備 (Prerequisites)

1.  確認您已安裝 Python 3.8 或更高版本。
2.  將專案檔案放置在您選擇的目錄下（例如 `d:\Python\math-master`）。
3.  打開終端機 (Terminal) 或命令提示字元 (Command Prompt)，進入專案根目錄。
4.  建立並啟用 Python 虛擬環境：

    ```bash
    # 建立虛擬環境
    python -m venv venv

    # 啟用虛擬環境 (Windows)
    .\venv\Scripts\activate

    # 啟用虛擬環境 (macOS/Linux)
    # source venv/bin/activate
    ```
    啟用成功後，您應該會在終端機提示符前看到 `(venv)` 字樣。

### 步驟二：安裝依賴套件 (Install Dependencies)

專案所需的所有 Python 套件都已列在 `requirements.txt` 檔案中。執行以下指令進行安裝：

```bash
pip install -r requirements.txt
```

### 步驟三：設定環境變數 (Configure Environment Variables)

1.  在專案根目錄下，手動建立一個名為 `.env` 的檔案。
2.  打開 `.env` 檔案，並填入您的 Google Gemini API 金鑰。您也可以在此設定 Flask 的密鑰。

    ```
    # .env
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    SECRET_KEY="a-strong-and-random-secret-key-for-flask-session"
    ```
    > **重要**：請將 `YOUR_GEMINI_API_KEY_HERE` 替換為您自己的有效金鑰。

### 步驟四：初始化資料庫 (Initialize Database)

在第一次執行應用程式之前，您需要初始化資料庫並匯入課程資料。這個步驟會建立 `math_master.db` 資料庫檔案，並將 `document/` 目錄下的 CSV 檔案內容寫入資料庫。

在終端機中執行以下指令：

```bash
python import_data.py
```

您應該會看到資料庫初始化成功以及資料匯入完成的訊息。

### 步驟五：執行應用程式 (Run the Application)

一切準備就緒後，執行以下指令來啟動 Flask 網站伺服器：

```bash
python app.py
```

伺服器啟動後，您會在終端機看到類似以下的訊息：

```
 * Running on http://127.0.0.1:5000
```

現在，打開您的網頁瀏覽器，訪問 **http://127.0.0.1:5000** 即可開始使用本應用程式。

---

## 系統架構與檔案說明

-   `app.py`: Flask 主應用程式，包含所有路由和核心邏輯。
-   `models.py`: 定義所有資料庫表格的 SQLAlchemy ORM 模型。
-   `import_data.py`: 用於初始化資料庫並從 CSV 匯入資料的腳本。
-   `config.py`: 應用程式的設定檔。
-   `requirements.txt`: 專案的 Python 依賴套件列表。
-   `.env`: (需手動建立) 用於存放敏感資訊，如 API 金鑰。
-   `templates/`: 存放所有 HTML 樣板檔案。
-   `static/`: 存放 CSS、JavaScript 等靜態檔案。
-   `skills/`: 存放各個數學技能單元的題目生成與批改邏輯模組。
-   `core/`: 存放 AI 分析、Session 管理等核心輔助功能。
-   `document/`: 存放 `skills_info.csv` 和 `skill_curriculum.csv`，用於資料庫初始化。

## 預設帳號

您可以使用以下帳號登入，或自行註冊新帳號：
-   **帳號**: `admin`
-   **密碼**: `admin`

> **注意**: 預設帳號需要在執行 `import_data.py` 後手動註冊一次，或直接修改 `import_data.py` 以自動建立。