# 系統分析文件 (System Analysis Document)

**專案名稱**：Textbook Processor & AI Analyzer  
**文件代號**：SA-DOC-2025-TB-PROCESSOR  
**文件版本**：v1.0  
**撰寫日期**：2025/12/06  
**負責角色**：System Analyst

---

## 1. 系統模組概述 (System Overview)

### 1.1 模組描述
本模組 **Textbook Processor & AI Analyzer** 旨在解決傳統教材數位化過程中，人工拆解結構耗時且難以標準化的痛點。系統採用「OCR 混合文件解析」技術搭配「Generative AI (Google Gemini)」進行語意理解，自動將非結構化的教科書檔案轉換為結構化的關聯式資料。

### 1.2 核心功能
1.  **自動化內容提取**：支援 PDF 與 Word (.docx) 格式，自動識別章節、圖片與數學公式。
2.  **AI 語意分析**：利用 Google Gemini LLM 分析文本，提取「核心觀念 (Concepts)」與「課程結構」。
3.  **資料結構化存儲**：將非結構化文本轉換為關聯式資料 (Relational Data)，存入資料庫以支援後續出題系統。

---

## 2. 詳細處理流程 (Process Flow)

### 2.1 系統流程圖 (System Flowchart)

```mermaid
graph TD
    %% 定義樣式
    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef ai fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef storage fill:#e0f2f1,stroke:#00695c,stroke-width:2px;

    Start([開始: 接收檔案路徑]) --> CheckTemp{檢查檔名<br/>是否以 ~$ 開頭?}
    CheckTemp -- 是 (暫存檔) --> EndSkip([結束: 跳過檔案])
    CheckTemp -- 否 --> ExtCheck{判斷副檔名}

    %% PDF 處理分支
    subgraph PDF_Process [PDF 處理流程]
        ExtCheck -- .pdf --> PyMuPDF[PyMuPDF (fitz) 提取文字]
        PyMuPDF --> DetectHeader[偵測大字體標題]
        DetectHeader --> OCR_PDF[pytesseract OCR 辨識圖片內容]
    end

    %% Word 處理分支
    subgraph Word_Process [Word (.docx) 處理流程]
        ExtCheck -- .docx --> Pypandoc[pypandoc 轉 Markdown]
        Pypandoc --> CheckMedia{檢查 media 資料夾<br/>圖片格式}
        CheckMedia -- .wmf / .emf --> WandConvert[Wand: 向量圖轉 .png]
        CheckMedia -- 其他格式 --> OCR_Word[pytesseract OCR 辨識圖片]
        WandConvert --> OCR_Word
        OCR_Word --> CleanPandoc[clean_pandoc_output<br/>清洗特殊標記/修正 sqrt]
    end

    PDF_Process --> AI_Phase
    Word_Process --> AI_Phase

    %% AI 分析分支
    subgraph AI_Analysis [AI 智能分析階段]
        AI_Phase[選擇 Prompt: 康軒/龍騰/通用]:::ai --> CallGemini[呼叫 Google Gemini API]:::ai
        CallGemini --> GetJSON[取得 JSON 回傳]:::ai
    end

    %% 資料清洗與存儲分支
    subgraph Data_Parsing [資料解析與清洗]
        GetJSON --> Sanitize[_sanitize_and_parse_json<br/>修復 JSON 格式錯誤]
        Sanitize --> FixLatex[fix_common_latex_errors<br/>正則表達式修復 LaTeX]
    end

    subgraph Data_Persistence [資料庫寫入]
        FixLatex --> SaveSkill[寫入 SkillInfo]:::storage
        SaveSkill --> SaveCurr[寫入 SkillCurriculum]:::storage
        SaveSkill --> SaveEx[寫入 TextbookExample]:::storage
    end

    Data_Persistence --> CheckGen{是否有新技能?}:::decision
    CheckGen -- 是 --> AutoGen[呼叫 auto_generate_skill_code<br/>生成出題腳本]:::process
    CheckGen -- 否 --> End([結束])
    AutoGen --> End

    class PyMuPDF,DetectHeader,OCR_PDF,Pypandoc,WandConvert,OCR_Word,CleanPandoc,Sanitize,FixLatex,AutoGen process;
    class CheckTemp,ExtCheck,CheckMedia,CheckGen decision;
```

---

## 3. 資料庫設計 (Database Schema)

根據 `models.py` 定義，系統主要由三個核心 Table 組成。

### 3.1 實體關聯圖 (ER Diagram 概念)
* **SkillInfo** (1) <---> (N) **SkillCurriculum**
* **SkillInfo** (1) <---> (N) **TextbookExample**

### 3.2 資料字典 (Data Dictionary)

#### A. Table: `SkillInfo` (技能資訊表)
**描述**：儲存最小顆粒度的知識點 (Knowledge Point)，為系統核心。

| 欄位名稱 (Field) | 資料型態 | 屬性 | 用途說明 |
| :--- | :--- | :--- | :--- |
| `skill_id` | VARCHAR | **PK**, Not Null | 技能唯一英文代碼 (例: `quadratic_formula`)。 |
| `skill_ch_name` | VARCHAR | Not Null | 技能中文名稱 (例: `公式解`)。 |
| `gemini_prompt` | TEXT | Nullable | 該技能專屬的 AI 出題提示詞模板。 |
| `category` | VARCHAR | Nullable | 學科分類 (如: 代數, 幾何)。 |

#### B. Table: `SkillCurriculum` (課綱結構表)
**描述**：定義技能在不同教科書版本中的位置，採扁平化儲存。

| 欄位名稱 (Field) | 資料型態 | 屬性 | 用途說明 |
| :--- | :--- | :--- | :--- |
| `id` | INT | **PK**, Auto Inc | 流水號。 |
| `skill_id` | VARCHAR | **FK** (Ref: SkillInfo) | 關聯的技能 ID。 |
| `curriculum` | VARCHAR | Not Null | 課綱/版本 (例: `108課綱`, `康軒`)。 |
| `grade` | VARCHAR | Not Null | 年級 (例: `七年級`, `高一`)。 |
| `volume` | VARCHAR | Nullable | 冊次 (例: `第一冊`)。 |
| `chapter` | VARCHAR | Not Null | 章節 (例: `Ch2 一元一次方程式`)。 |
| `section` | VARCHAR | Nullable | 小節 (例: `2-1 未知數`)。 |
| `display_order` | INT | Default 0 | 前端顯示排序權重。 |

#### C. Table: `TextbookExample` (課本例題表)
**描述**：儲存從教材中提取的標準例題，用於 RAG 檢索或出題參考。

| 欄位名稱 (Field) | 資料型態 | 屬性 | 用途說明 |
| :--- | :--- | :--- | :--- |
| `id` | INT | **PK**, Auto Inc | 流水號。 |
| `skill_id` | VARCHAR | **FK** (Ref: SkillInfo) | 關聯的技能 ID。 |
| `problem_text` | TEXT | Not Null | 題目敘述，包含 LaTeX 語法。 |
| `detailed_solution`| TEXT | Nullable | 詳解步驟。 |
| `source_description`| VARCHAR | Nullable | 來源標記 (例: `P.15 例題 2`)。 |

---

## 4. 關鍵技術細節 (Technical Stack)

### 4.1 技術堆疊 (Tech Stack)

| 類別 | 元件/套件 | 說明 |
| :--- | :--- | :--- |
| **PDF 解析** | `PyMuPDF (fitz)` | 高速提取文字區塊與圖片座標。 |
| **Word 轉檔** | `pypandoc` | 將 .docx 轉為 Markdown，確保數學公式以 LaTeX 格式保留。 |
| **圖像處理** | `Wand (ImageMagick)` | 專門處理 Word 舊式向量圖 (`.wmf`, `.emf`) 轉 `.png`。 |
| **OCR 辨識** | `pytesseract` | 針對圖片中的中文與數學符號進行光學辨識。 |
| **AI 模型** | `Google Gemini API` | 負責語意理解、結構化輸出 (JSON) 與觀念歸納。 |
| **資料清洗** | `Regex (re)` | 使用 Python 正則表達式修復 LaTeX 與 JSON 格式。 |

### 4.2 核心演算法：LaTeX 標準化 (Code Snippet)
為解決 OCR 與 Pandoc 轉檔常見的數學符號錯誤，系統實作 `fix_common_latex_errors` 函式：

```python
import re

def fix_common_latex_errors(text: str) -> str:
    """
    針對 OCR 識別錯誤或 Pandoc 轉檔產生的非標準格式進行 Regex 修復。
    """
    # 1. 三角函數正體化 (sin -> \sin)
    math_funcs = r"(sin|cos|tan|csc|sec|cot|log|ln)"
    text = re.sub(fr"(?<!\\)\b{math_funcs}\b", r"\\\1", text, flags=re.IGNORECASE)

    # 2. 希臘字母補全反斜線 (alpha -> \alpha)
    greek_letters = r"alpha|beta|gamma|theta|pi|delta|sigma|omega"
    text = re.sub(fr"(?<!\\)\b({greek_letters})\b", r"\\\1", text, flags=re.IGNORECASE)

    # 3. 修正 Pandoc 根號格式 (\sqrt [3] {x} -> \sqrt[3]{x})
    text = re.sub(r"\\sqrt\s*\[\s*(\d+)\s*\]\s*\{", r"\\sqrt[\1]{", text)
    text = re.sub(r"\\sqrt\s+\{", r"\\sqrt{", text)

    # 4. 向量符號標準化
    text = re.sub(r"\\vec\s+\{", r"\\vec{", text)
    
    return text.strip()
```

### 4.3 核心演算法：JSON 容錯解析
針對 LLM 回傳內容的不穩定性，`_sanitize_and_parse_json` 採用以下策略：
* **Strip Fencing**：移除 Markdown 程式碼區塊標記 (```json ... ```)。
* **JSON5 Fallback**：若標準解析失敗，使用 `json5` 庫解析以允許尾隨逗號 (trailing commas)。
* **Schema Validation**：檢查必要欄位 (`topics`, `content`) 是否存在。

---

## 5. 待辦事項與建議 (Next Steps)

1.  **擴充向量資料庫**：建議將 `TextbookExample` 寫入 Vector DB (如 ChromaDB)，實現語意搜題。
2.  **人工介入介面 (Human-in-the-loop)**：開發簡易的前端介面，供老師在寫入資料庫前審核 AI 辨識的課綱結構。
3.  **效能優化**：針對大量圖片的 PDF，可考慮非同步 (Async) 處理 OCR 任務。