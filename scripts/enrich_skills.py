import sys
import os
import json
import time
from tqdm import tqdm  # 如果沒安裝 tqdm，請執行 pip install tqdm
import re
from sqlalchemy import distinct, text

# 1. 設定路徑以匯入專案模組 (指回專案根目錄)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, SkillInfo, TextbookExample, SkillCurriculum
# 使用專案統一的 AI 介面
from core.ai_analyzer import get_model

def get_user_selection(options, prompt_text):
    """
    通用互動函式：讓使用者從選項中選擇，或輸入 0 全選
    """
    if not options:
        return None
    
    # 去除 None 值並排序
    options = sorted([o for o in options if o is not None])
    
    print(f"\n{prompt_text}")
    print("   [0] ALL (全部處理)")
    for i, opt in enumerate(options, 1):
        print(f"   [{i}] {opt}")
        
    while True:
        try:
            choice = input("👉 請選擇 (輸入數字): ").strip()
            if choice == '0':
                return None  # 代表全選
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("❌ 輸入無效，請重試。")
        except ValueError:
            print("❌ 請輸入數字。")

def generate_prompts(model, skill: SkillInfo, examples: list[TextbookExample]) -> dict:
    """
    呼叫 Gemini 生成 3 個學生視角的點擊式問句。
    [強化功能] 
    1. 啟用 SQLite WAL 防止壞檔 (由 main 函式控制)。
    2. 內建針對 LaTeX 的 JSON 容錯解析機制 (自動修復反斜線)。
    """
    
    # 準備例題上下文
    examples_context = "\n---\n".join([
        f"例題 {i+1}:\n題目：{ex.problem_text}\n詳解：{ex.detailed_solution}"
        for i, ex in enumerate(examples)
    ])

    JSON_SCHEMA = 'prompt_1, prompt_2, prompt_3' 

    # 設定 System Prompt (包含 LaTeX 強制 $ 包覆要求與學生問句風格)
    SYSTEM_PROMPT = f"""
你是一位精通數學教育的 AI 內容生成引擎，模擬**資深功文數學輔導員**的角色。
你的任務是根據「目標技能描述」和「實際例題 (Examples)」，為學生生成 3 個最精準、最具引導性的**點擊式問句 (Quick-Click Questions)**。

---
【強制輸出要求】
1. 輸出格式：必須為純 JSON 物件，包含三個鍵：{JSON_SCHEMA}。
2. 語氣：所有問題必須使用**學生語氣**，以「我」作為主詞開頭。
3. 長度限制：每個問句必須嚴格控制在**25 個字以內**。
4. **LaTeX 格式強制要求**：任何數學符號、變數、公式（如: \\frac, \\sqrt, x^2）**必須**使用單個美元符號 `$` 包覆，例如：`$x^2$`。
5. **絕對精準原則**：嚴禁使用例題中沒有出現的變數或符號 (例如：若沒出現 x，則不可提到 x 係數)。

---
目標技能描述: {skill.description}

[關鍵參考例題]
{examples_context}

---
請根據以下三個階段，生成學生最想點擊的問題：

1. **prompt_1 (概念與觀察)**: 詢問關鍵概念或與例題的關聯。
   【問句框架】: **「我該怎麼觀察例題，才能知道這題要用『[技能關鍵概念/公式]』？」**

2. **prompt_2 (實際操作與步驟)**: 詢問計算第一步或關鍵轉折點。
   【問句框架】: **「我第一步要先處理『[例題中具體計算對象/符號]』嗎？要怎麼做？」**

3. **prompt_3 (驗算與檢查)**: 詢問快速驗算或檢查細節的方法。
   【問句框架】: **「請問這題的答案『[例題中數值範圍/符號意義]』，我要如何檢查才合理？」**
"""

    try:
        # 呼叫 AI
        response = model.generate_content(SYSTEM_PROMPT)
        text = response.text.strip()
        
        # 1. 清理 Markdown 標記
        if text.startswith("```"):
            text = re.sub(r"^```json\s*|^```\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        
        # 2. [策略 A] 嘗試直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 3. [策略 B] 啟動 Regex 修復 (智慧容錯)
            # 說明：將所有「不是」標準 JSON 轉義符 (\n, \t, \u, \", \\) 的反斜線，強制轉為雙反斜線。
            # 這能救回 \int, \frac, \alpha 等所有 LaTeX 指令，防止 JSON Parse Error。
            fixed_text = re.sub(r'(?<!\\)\\(?![u"\\/bfnrt])', r'\\\\', text)
            
            try:
                return json.loads(fixed_text)
            except json.JSONDecodeError:
                print(f"   ⚠️ 生成失敗 (JSON Parse Error). Raw snippet: {text[:50]}...")
                return None
                
    except Exception as e:
        print(f"   ⚠️ API 呼叫錯誤: {e}")
        return None

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # [CRITICAL FIX] 啟用 WAL 模式以支援高併發寫入，防止資料庫壞檔
        try:
            with db.engine.connect() as connection:
                connection.execute(text("PRAGMA journal_mode=WAL"))
            print("✅ SQLite WAL 模式已啟用 (防止資料庫鎖死與損壞)")
        except Exception as e:
            print(f"⚠️ 無法啟用 WAL 模式: {e}")
        print("🚀 開始為技能補充 AI 提示詞 (Enrich Skills - Interactive Mode)...")
        
        try:
            model = get_model()
        except Exception as e:
            print(f"❌ 無法初始化 AI 模型: {e}")
            sys.exit(1)

        # ==========================================
        # 1. 階層篩選 (Hierarchical Filtering)
        # ==========================================
        base_query = db.session.query(SkillCurriculum)

        # Level 1: Curriculum
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇要處理的課綱:")
        if selected_curr:
            base_query = base_query.filter(SkillCurriculum.curriculum == selected_curr)

        # Level 2: Grade
        grades = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.grade)).order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")
        if selected_grade:
            base_query = base_query.filter(SkillCurriculum.grade == selected_grade)

        # Level 3: Volume
        volumes = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.volume)).order_by(SkillCurriculum.volume).all()]
        selected_volume = get_user_selection(volumes, "請選擇冊別:")
        if selected_volume:
            base_query = base_query.filter(SkillCurriculum.volume == selected_volume)

        # Level 4: Chapter
        chapters = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.chapter)).order_by(SkillCurriculum.chapter).all()]
        selected_chapter = get_user_selection(chapters, "請選擇章節:")
        if selected_chapter:
            base_query = base_query.filter(SkillCurriculum.chapter == selected_chapter)

        # ==========================================
        # 2. 準備處理清單
        # ==========================================
        final_query = db.session.query(SkillInfo).join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id).filter(SkillInfo.is_active == True)
        
        # 再次應用篩選條件以確保正確對應到 SkillInfo
        if selected_curr: final_query = final_query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: final_query = final_query.filter(SkillCurriculum.grade == selected_grade)
        if selected_volume: final_query = final_query.filter(SkillCurriculum.volume == selected_volume)
        if selected_chapter: final_query = final_query.filter(SkillCurriculum.chapter == selected_chapter)

        skills_to_process = final_query.distinct().all()
        total = len(skills_to_process)
        print(f"\n📊 根據您的篩選，共找到 {total} 個技能範圍。\n")
        
        if total == 0:
            print("✅ 無需處理。")
            sys.exit(0)

        # ==========================================
        # 3. 模式選擇 (Mode Selection)
        # ==========================================
        print("請選擇執行模式：")
        print("   [1] 僅生成缺失檔案 (Safe Mode) - 檢查 suggested_prompt_2 是否為空")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All)")
        
        mode = None
        while True:
            choice = input("👉 請選擇 (1 或 2): ").strip()
            if choice in ['1', '2']:
                mode = choice
                break
            print("❌ 輸入無效，請輸入 1 或 2。")

        # ==========================================
        # 4. 執行生成
        # ==========================================
        count_processed = 0
        count_skipped = 0

        for skill in tqdm(skills_to_process, desc="處理進度"):
            
            # [邏輯檢查] 根據模式決定是否跳過
            if mode == '1': # Safe Mode
                # 如果 suggested_prompt_2 已經有內容，則跳過
                if skill.suggested_prompt_2 and skill.suggested_prompt_2.strip():
                    count_skipped += 1
                    continue
            
            # 若為 Overwrite 模式，或 Safe Mode 且欄位為空，則繼續執行
            
            # 取得例題上下文
            examples = db.session.query(TextbookExample).filter_by(skill_id=skill.skill_id).limit(2).all()
            
            # 生成提示詞
            prompts = generate_prompts(model, skill, examples)
            
            if prompts:
                try:
                    skill.suggested_prompt_1 = prompts.get('prompt_1')
                    skill.suggested_prompt_2 = prompts.get('prompt_2')
                    skill.suggested_prompt_3 = prompts.get('prompt_3')
                    
                    db.session.commit()
                    count_processed += 1
                except Exception as e:
                    db.session.rollback()
                    print(f"寫入 DB 失敗: {e}")
            
            # 避免 API Rate Limit
            time.sleep(1)

        print(f"\n✨ 全部作業完成！")
        print(f"   - 實際處理/更新: {count_processed} 個")
        print(f"   - 跳過 (原本已有內容): {count_skipped} 個")