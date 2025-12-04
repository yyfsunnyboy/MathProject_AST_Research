import sys
import os
import json
import time
from tqdm import tqdm  # 如果沒安裝 tqdm，請執行 pip install tqdm
import re
from sqlalchemy import distinct

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

def generate_prompts(model, skill, examples):
    """
    針對技能生成符合「功文數學 (Kumon)」理念的引導提問。
    """
    
    example_text = ""
    if examples:
        example_text = "\n\n【參考例題】:\n"
        for i, ex in enumerate(examples, 1):
            example_text += f"例題 {i}:\n{ex.problem_text}\n詳解: {ex.detailed_solution}\n\n"
            
    # [Prompt 優化] Kumon 風格 + LaTeX/JSON 防護
    prompt = f"""
    # Role
    你是一位資深的「功文數學 (Kumon)」輔導員。你的學生是正在進行自學自習的學生。
    技能單元: {skill.skill_ch_name} ({skill.skill_en_name})
    單元描述: {skill.description}
    {example_text}

    # Task
    請設計 3 個「精簡短促」的引導式提問 (Suggested Prompts)，協助學生自學。
    學生看到的例題跟你看到的不同，請綜合所有狀況，設計通用的引導提問。
    每個提問請聚焦在「引導學生思考下一步該做什麼」，而非直接給出解答。
    
    # Guidelines (功文式哲學)
    1. **極度精簡**: 每個提問盡量控制在 **30 個字以內**。
    2. **例題導向**: 遇到不懂，先叫學生「觀察例題」找規律。
    3. **專注運算**: 少講大道理，多提示「下一步要做什麼動作」。
    4. **不直接給答案**: 只提示路徑，讓學生自己完成最後一步。
    5. **繁體中文**: 使用台灣用語。
    
    # Constraints (技術限制)
    1. **LaTeX 格式**: 所有數學符號必須用 $ 包覆 (例如: $x^2$)。
    2. **JSON 轉義**: 輸出 JSON 字串時，若包含 LaTeX 反斜線 (\\)，必須使用雙反斜線 (\\\\) 轉義。
    3. **純淨輸出**: 只回傳 JSON，不要有 Markdown 標記或其他廢話。

    # Levels
    - **prompt_1 (觀察例題)**: 引導學生觀察例題的特徵或規律。(例如：「請觀察例題，指數的位置發生了什麼變化？」)
    - **prompt_2 (關鍵步驟)**: 提示解題的「第一個小動作」。(例如：「先將分母通分，再進行加減。」)
    - **prompt_3 (自我檢查)**: 引導學生檢查計算細節。(例如：「檢查一下，正負號有沒有變對？」)

    # Output Format (JSON Only)
    {{
        "prompt_1": "...",
        "prompt_2": "...",
        "prompt_3": "..."
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        
        # [修復] 使用 Regex 修復常見的 LaTeX JSON 轉義錯誤
        # 保護標準 JSON 轉義符 (u, ", \, /, b, f, n, r, t)，其餘單反斜線轉為雙反斜線
        text = re.sub(r'\\(?![u"\\/bfnrt])', r'\\\\', text)

        return json.loads(text)
    except Exception as e:
        print(f"   ⚠️ 生成失敗 (JSON Parse Error). Raw snippet: {text[:50]}...")
        return None

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
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