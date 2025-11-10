# 功文數學 — 智慧數學學習平台 (math-master)

簡短說明
---------
本專案為以「功文數學」教學理論為核心的智慧數學學習平台，結合手寫辨識、生成式 AI（Gemini / LLM）分析與自適應題目推送，目標幫助「考不及格、數學較弱」的高中職學生打好基礎運算與解題能力，達到及格門檻並建立學習信心。此專案同時為參加育秀盃 AI 應用競賽之作品。

專案重點
---------
- 教學理論：採用功文數學（基礎概念精熟、漸進式學習、重複練習、即時回饋）。
- 主要目的：把未達標學生提升到及格（60分）為優先目標，透過診斷與針對性練習強化基本運算能力。
- 適用場域：智慧校園 — 學習與教學優化、校園生活輔助、永續教育等。

架構總覽
---------
- 後端：Python + Flask（輕量 Web 框架）
- 資料庫：SQLite（單檔式，本地測試與部署）
- 前端：原生 HTML / CSS / JavaScript（templates/ 與 static/）
- 技能模組：skills/ 下各技能以獨立模組管理（題目生成、答案檢核）
- AI 整合：以生成式模型 (Gemini/LLM) 做手寫/文字答案分析與教學提示（透過可配置的 prompt）
- 部署測試：本地 Flask run（開發時使用）

主要目錄
---------
- app.py — Flask 主應用與路由
- requirements.txt — Python 套件依賴
- templates/ — Jinja2 HTML 模板（含 admin 與練習頁面）
- static/ — CSS / JS / 圖片等靜態檔
- skills/ — 各類技能題型模組（generate/check 等函式）
- core/ 或 routes.py — 共用邏輯、學習路徑、診斷系統（視實作）
- schema.sql 或 instance/ — 資料庫 Schema（若有）
- README.md — 專案說明（本檔）

重要資料表（範例）
------------------
- skills_info — 技能定義（skill_id、名稱、gemini_prompt、input_type、order_index、is_active 等）
- skill_curriculum — 課程映射（id, skill_id, curriculum, grade, volume, chapter, section, paragraph, display_order, diffcult_level, last_practiced）
（請確認 schema 與模板欄位完全對應）

快速啟動（Windows）
-------------------
1. 建立虛擬環境並啟用
   .venv 建議放在專案目錄：
