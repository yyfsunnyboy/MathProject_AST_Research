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
    [名師引導版 - 最終修訂]
    
    修正重點：
    1. [新增] 強制禁止 Markdown 粗體/斜體格式，確保前端顯示乾淨。
    2. 保持解題三部曲邏輯 (啟動 -> 策略 -> 檢查)。
    """
    
    # 1. 讀取 Context
    skill_code_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills', f'{skill.skill_id}.py')
    code_content = None
    
    if os.path.exists(skill_code_path):
        try:
            with open(skill_code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception:
            pass 

    if code_content:
        context_source = "Python 題目生成程式碼"
        context_content = f"```python\n{code_content}\n```"
    else:
        context_source = "課本例題"
        context_content = "\n---\n".join([
            f"例題 {i+1}:\n題目：{ex.problem_text}\n詳解：{ex.detailed_solution}"
            for i, ex in enumerate(examples)
        ])

    JSON_SCHEMA = 'system_instruction, prompt_1, prompt_2, prompt_3' 

    # 設定 System Prompt
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    # 設定 System Prompt
    SYSTEM_PROMPT = f"""
請針對技能『{skill.skill_ch_name}』與例題『{context_content}』生成一個 JSON。

【核心任務：教學指令 (system_instruction)】
你是啟發式助教。請在指令中要求自己：
1. **極簡回答**：每則回話限 50 字內，不給答案。
2. **邏輯鏈追問**：回傳的 `follow_up_prompts` 必須嚴格遵守以下三步：
   - 第一問【觀察】：引導學生看題目資訊（例：底數一樣嗎？）。
   - 第二問【聯想】：聯想公式（例：底數相同相乘，指數要怎麼算？）。
   - 第三問【執行】：引導寫出第一步（例：你可以試著先把式子列出來嗎？）。

【輔助任務：生成初始引導詞】
請提供 3 個精簡的破冰問題。

【輸出 JSON 格式】：
{{
  "system_instruction": "...",
  "prompt_1": "這題第一步做什麼？",
  "prompt_2": "公式怎麼帶？",
  "prompt_3": "要注意什麼陷阱？"
}}
"""

    try:
        response = model.generate_content(SYSTEM_PROMPT)
        text = response.text.strip()
        
        # 清理 Markdown Code Block 標記
        if text.startswith("```"):
            text = re.sub(r"^```json\s*|^```\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 嘗試修復 LaTeX 跳脫字元問題
            fixed_text = re.sub(r'(?<!\\)\\(?![u"\\/bfnrt])', r'\\\\', text)
            try:
                return json.loads(fixed_text)
            except json.JSONDecodeError:
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
                connection.execute(text("PRAGMA busy_timeout=10000"))
                connection.execute(text("PRAGMA synchronous=NORMAL"))
            print("✅ 穩定模式已啟動 (WAL + Busy Timeout + Normal Sync)")
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
                    
                    # ✨ 更新為邏輯鏈教學指令
                    system_inst = prompts.get('system_instruction')
                    if system_inst:
                        skill.gemini_prompt = system_inst
                        print(f"   [OK] 已更新 {skill.skill_ch_name} 為邏輯鏈模式")

                    db.session.commit()
                    count_processed += 1
                except Exception as e:
                    db.session.rollback()
                    db.session.expunge_all() # 重要：清理快取，避免壞掉的物件影響下一輪
                    print(f"❌ 寫入 DB 失敗: {e}")
                    
                    if "malformed" in str(e).lower():
                        print("🚨 CRITICAL ERROR: 資料庫檔案毀損 (Disk image is malformed)！")
                        print("   請立即停止程式，並從備份還原資料庫。")
                        sys.exit(1)
            
            # 避免 API Rate Limit (延長緩衝時間)
            time.sleep(1.5)

        print(f"\n✨ 全部作業完成！")
        print(f"   - 實際處理/更新: {count_processed} 個")
        print(f"   - 跳過 (原本已有內容): {count_skipped} 個")