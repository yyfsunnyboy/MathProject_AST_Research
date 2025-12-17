# 學生端學習診斷修改分析 (Student Learning Diagnosis Modification Analysis)

## 1. 需求概述
修改學生端學習診斷功能，使其能整合現有的錯題資料庫 (`MistakeLog`) 與考卷分析結果 (`ExamAnalysis`)，並結合知識圖譜 (`SkillPrerequisites`) 提供 AI 建議。

## 2. 資料來源分析
### 2.1 錯題資料庫 (`MistakeLog`)
- **欄位**: `question_content`, `user_answer`, `correct_answer`, `error_type`, `error_description`.
- **用途**: 統計學生在練習模式下的錯誤類型頻率。

### 2.2 考卷分析結果 (`ExamAnalysis`)
- **欄位**: `error_type`, `is_correct`, `confidence`, `feedback`.
- **用途**: 統計學生在考卷測試中的錯誤類型頻率。

### 2.3 知識圖譜 (`SkillPrerequisites`)
- **結構**: `SkillInfo` (節點) + `SkillPrerequisites` (邊)。
- **用途**: 提供 AI 分析時的上下文，找出錯誤單元的前置弱點技能。

## 3. 功能設計
### 3.1 錯誤類型分析 (Bar Chart)
- **邏輯**: 
    1. 撈取該學生最近 N 筆 (或全部) `MistakeLog`。
    2. 撈取該學生最近 N 筆 `ExamAnalysis` (只取 `is_correct=False` 或有 `error_type` 的記錄)。
    3. 統計各 `error_type` (如: 計算錯誤, 觀念不清, 審題錯誤等) 的出現次數。
    4. 輸出數據供前端繪製長條圖。

### 3.2 AI 學習建議
- **Prompt 設計**:
    - **Input**: 
        - 錯誤類型統計數據。
        - 具體錯題內容 (抽樣幾題代表性的)。
        - 相關單元及其前置技能 (知識圖譜)。
    - **Output**:
        - 綜合分析評語。
        - 推薦加強單元 (`recommended_unit`)。
        - 具體學習建議。
- **儲存**: 將 AI 回應存入 `LearningDiagnosis` 表格，避免重複生成。

### 3.3 推薦單元
- 根據 AI 分析結果，明確給出需要練習的單元名稱，並提供連結。

## 4. 資料庫變更
- **LearningDiagnosis**: 
    - 利用現有的 `radar_chart_data` (Text) 欄位儲存複合 JSON 資料。
    - **JSON 結構**:
      ```json
      {
        "radar": { "單元A": 80, "單元B": 60 },
        "bar": { "觀念錯誤": 5, "計算錯誤": 3, "審題不清": 2 }
      }
      ```
    - `ai_comment`: 儲存 AI 總結評語。
    - `recommended_unit`: 儲存推薦單元。

## 5. 實作步驟
1.  建立/更新 `/student/diagnosis` 路由。
2.  實作資料彙整邏輯。
3.  呼叫 Gemini API 生成建議。
4.  前端頁面展示。
