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
    [終極強化版] 
    1. 讀取 Python 代碼 (Genotype) 或 課本例題 (Phenotype)。
    2. [Fix] 強制 LaTeX 符號內容完整 (防止 \\overline{} 亂碼)。
    3. [Fix] 禁止是非題 (禁止問 Is this...?)。
    4. [Fix] 變數語意化 (強制解釋 a,b 的數學角色)。
    5. 內建 JSON 容錯解析。
    """
    
    # 1. 嘗試讀取技能對應的 Python 程式碼
    skill_code_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills', f'{skill.skill_id}.py')
    code_content = None
    
    if os.path.exists(skill_code_path):
        try:
            with open(skill_code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            print(f"   ⚠️ 讀取程式碼失敗: {e}")

    # 2. 決定 Context 來源
    if code_content:
        context_source = "Python 題目生成程式碼 (Source Code)"
        context_content = f"```python\n{code_content}\n```"
        strategy_instruction = """
        【分析模式：程式碼邏輯分析】
        1. **識別分支**：分析 `generate` 函式是否包含多種題型分支。
        2. **角色解讀**：觀察程式碼中的變數（如 numer, denom, a, b），理解它們在數學上的意義，不要直接用英文變數名。
        """
    else:
        context_source = "課本例題 (Textbook Examples)"
        context_content = "\n---\n".join([
            f"例題 {i+1}:\n題目：{ex.problem_text}\n詳解：{ex.detailed_solution}"
            for i, ex in enumerate(examples)
        ])
        strategy_instruction = """
        【分析模式：例題歸納】
        請歸納例題的共通解法。將題目中的數字或符號轉化為通用的「數學角色」描述。
        """

    JSON_SCHEMA = 'prompt_1, prompt_2, prompt_3' 

    # 設定 System Prompt (包含 7 大黃金規則)
    SYSTEM_PROMPT = f"""
你是一位精通數學教育與程式邏輯的 AI 內容生成引擎。
你的任務是根據「目標技能描述」和「{context_source}」，為學生生成 3 個最精準、最具引導性的**點擊式問句**。

{strategy_instruction}

---
【強制輸出要求】
1. 輸出格式：純 JSON 物件 (keys: {JSON_SCHEMA})。
2. 語氣：**學生語氣**（以「我」開頭）。
3. 長度限制：25 字以內。
4. **LaTeX 要求**：數學符號用單個 `$` 包覆，**嚴禁空指令** (如 `$\\overline{{}}$` 必錯，要有內容 `$0.\\overline{{x}}$`)。
5. **❌ 禁止是非題**：嚴禁問「這題是不是要算...？」。
6. **✅ 強制特徵引導**：Prompt 1 必須引導觀察「視覺特徵」。
7. **✅ 強制角色定義 (關鍵)**：
   - **嚴禁**直接使用無意義的變數名稱 (如 "解 $a, b$"、"求 $x$")，除非該變數是題目中的標準未知數。
   - **必須**加上中文描述。
   - ❌ 爛問句：「這題是要解 $a, b$ 嗎？」(學生看不懂)
   - ✅ 好問句：「這題的 $a, b$ 是不是分別代表**『整數部分』**和**『根號前的係數』**？」
   - ✅ 好問句：「我要找出的 $x$，是不是代表**『原本的分數』**？」

---
目標技能描述: {skill.description}

[分析對象: {context_source}]
{context_content}

---
請根據以下三個階段，生成學生最想點擊的問題：

1. **prompt_1 (特徵與聯想)**: 
   - 觀察題目的**視覺特徵**，並用**中文角色名稱**稱呼變數。
   - 【框架】**「看到算式中有『[特徵]』，題目要求的『[中文角色/變數]』是指什麼？」**

2. **prompt_2 (策略與工具)**: 
   - 引導選擇工具。
   - 【框架】**「針對這種題型，我第一步該用『[方法A]』還是『[方法B]』？」**

3. **prompt_3 (驗算與反思)**: 
   - 引導逆向檢查。
   - 【框架】**「算出來的答案，如果『[逆向操作]』回去，會吻合嗎？」**
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
            # 3. [策略 B] 啟動 Regex 修復
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