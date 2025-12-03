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
                return None # 代表全選
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("❌ 輸入無效，請重試。")
        except ValueError:
            print("❌ 請輸入數字。")

def generate_prompts(model, skill, examples):
    """
    針對技能生成符合「功文數學 (Kumon)」理念的引導提問 (繁體中文)。
    """
    
    example_text = ""
    if examples:
        example_text = "\n\n【參考例題】:\n"
        for i, ex in enumerate(examples, 1):
            example_text += f"例題 {i}:\n{ex.problem_text}\n詳解: {ex.detailed_solution}\n\n"
            
    # [Prompt 優化] 加入 JSON 轉義特別指示
    prompt = f"""
    # Role
    你是一位資深的「功文數學 (Kumon)」輔導員。你的學生是數學基礎較弱的高中職生。
    你的任務是針對技能單元「{skill.skill_ch_name}」撰寫 3 句固定的「引導提示詞」。

    # Context
    技能描述: {skill.description}
    {example_text}

    # Constraints (關鍵限制)
    1. **簡潔有力**: 每一句提示必須控制在 **30 個字以內**。
    2. **通用性**: 這些提示會用於該單元的所有題目，**不可提及特定題目中的數字**，必須講述通用的解題邏輯。
    3. **LaTeX 格式**: 所有數學符號必須用 $ 包覆 (例如: $x^2$)。
    4. **JSON 格式注意**: 輸出 JSON 字串時，若包含 LaTeX 反斜線 (\\)，請務必使用雙反斜線 (\\\\) 進行轉義 (例如: 將 \\frac 寫成 \\\\frac)。

    # Levels
    - **Prompt 1 (觀察與回憶)**: 提醒學生觀察特徵或回想公式。
    - **Prompt 2 (關鍵第一步)**: 指出第一步該做什麼動作。
    - **Prompt 3 (核心操作)**: 指出運算邏輯，但不直接給答案。

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
        
        # [Critical Fix] 使用 Regex 修復常見的 LaTeX JSON 轉義錯誤
        # 尋找單獨的反斜線，且後面接的不是標準 JSON 轉義符 (u, ", \, /, b, f, n, r, t)
        # 將其替換為雙反斜線
        text = re.sub(r'\\(?![u"\\/bfnrt])', r'\\\\', text)

        return json.loads(text)
    except Exception as e:
        # print(f"Error generating prompt for {skill.skill_id}: {e}") # 暫時註解以免洗版
        # 若失敗，印出原始文字以供除錯
        print(f"   ⚠️ JSON Parse Error. Raw Text snippet: {text[:50]}...")
        return None

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("🚀 開始為技能補充 AI 提示詞 (Enrich Skills)...")
        
        try:
            model = get_model()
        except Exception as e:
            print(f"❌ 無法初始化 AI 模型: {e}")
            sys.exit(1)
        
        # --- 互動式篩選 ---
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

        # --- 最終查詢 ---
        final_query = db.session.query(SkillInfo).join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id).filter(SkillInfo.is_active == True)
        if selected_curr: final_query = final_query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: final_query = final_query.filter(SkillCurriculum.grade == selected_grade)
        if selected_volume: final_query = final_query.filter(SkillCurriculum.volume == selected_volume)
        if selected_chapter: final_query = final_query.filter(SkillCurriculum.chapter == selected_chapter)

        skills_to_process = final_query.distinct().all()
        
        total = len(skills_to_process)
        print(f"\n📊 根據您的篩選，共找到 {total} 個技能需要處理。\n")
        
        if total == 0:
            print("✅ 無需處理。")
            sys.exit(0)

        # 使用 tqdm 顯示進度
        for skill in tqdm(skills_to_process, desc="處理進度"):
            # 取得例題上下文
            examples = db.session.query(TextbookExample).filter_by(skill_id=skill.skill_id).limit(2).all()
            
            # 生成提示詞
            prompts = generate_prompts(model, skill, examples)
            
            if prompts:
                try:
                    # 強制覆蓋，不再檢查是否為 None
                    skill.suggested_prompt_1 = prompts.get('prompt_1')
                    skill.suggested_prompt_2 = prompts.get('prompt_2')
                    skill.suggested_prompt_3 = prompts.get('prompt_3')
                    
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"寫入 DB 失敗: {e}")
            
            # 避免 API Rate Limit
            time.sleep(1)

        print("\n✅ 作業完成！")