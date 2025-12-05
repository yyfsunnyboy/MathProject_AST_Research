import sys
import os
import json
import time
import re
from tqdm import tqdm
from sqlalchemy import distinct

# ==========================================
# 1. 設定路徑以匯入專案模組
# script/ -> root/
# ==========================================
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.ai_analyzer import get_model

# ==========================================
# 互動選單函式
# ==========================================
def get_user_selection(options, prompt_text):
    if not options:
        return None
    
    # 過濾 None 並排序
    options = sorted([o for o in options if o is not None])
    
    print(f"\n{prompt_text}")
    print("   [0] ALL (全部處理)")
    for i, opt in enumerate(options, 1):
        print(f"   [{i}] {opt}")
        
    while True:
        try:
            choice = input("👉 請選擇 (輸入數字): ").strip()
            if choice == '0':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("⚠️ 輸入無效，請重試。")
        except ValueError:
            print("⚠️ 請輸入數字。")

# ==========================================
# 核心邏輯：準備候選技能池
# ==========================================
def get_candidate_skills(target_skill, all_skills_cache):
    """
    為目標技能篩選出「可能的」前置技能候選池。
    邏輯：
    1. 排除自己。
    2. 跨階段：目標是高中 (gh_)，則所有國中 (jh_) 都是候選。
    3. 同階段：必須排序 (order_index) 在目標之前。
    """
    candidates = []
    
    target_id = target_skill.skill_id
    target_is_gh = target_id.startswith('gh_')
    target_order = target_skill.order_index or 99999

    for s in all_skills_cache:
        candidate_id = s['id']
        
        # 排除自己
        if candidate_id == target_id:
            continue
            
        candidate_order = s['order'] or 99999
        candidate_is_jh = candidate_id.startswith('jh_')
        candidate_is_gh = candidate_id.startswith('gh_')

        is_valid = False

        # [規則 A] 跨階段：目標是高中，候選是國中 -> 必定納入
        if target_is_gh and candidate_is_jh:
            is_valid = True
        
        # [規則 B] 同階段：依照順序判斷 (高中找高中、國中找國中)
        elif (target_is_gh and candidate_is_gh) or (not target_is_gh and candidate_is_jh):
            if candidate_order < target_order:
                is_valid = True

        if is_valid:
            # 格式: "ID (中文名稱)"
            candidates.append(f"{s['id']} ({s['name']})")

    return candidates

# ==========================================
# AI 分析函式 (加入例題上下文 + 數量限制)
# ==========================================
def identify_prerequisites(model, target_skill, candidate_list, example_text=None):
    """
    呼叫 AI 判斷前置技能
    """
    # 取順序最接近的 80 個技能作為候選 (節省 Token)
    candidates_str = "\n".join(candidate_list[-80:]) 

    # 構建例題區塊 (含詳解)
    example_block = ""
    if example_text:
        example_block = f"""
    --- TARGET SKILL EXAMPLE PROBLEM (For Analysis) ---
    Analyze the following problem to understand the step-by-step math operations required:
    {example_text}
    """

    prompt = f"""
    You are a Math Curriculum Expert responsible for building a Knowledge Graph.
    Your task is to identify the **Direct Prerequisite Skills** for the 'Target Skill' from the 'Candidate Pool'.

    Target Skill Info:
    - ID: {target_skill.skill_id}
    - Name: {target_skill.skill_ch_name}
    - Description: {target_skill.description}
    {example_block}

    Candidate Skills Pool (Sorted by curriculum order):
    {candidates_str}

    Analysis Logic:
    1. **Analyze Requirements**: Look at the Target Skill's description and the Example Problem. What underlying concepts are needed? (e.g., to solve quadratic equations, one needs factoring and square roots).
    2. **Map to Candidates**: Find skills in the 'Candidate Pool' that cover these concepts.
    3. **Hierarchy Rule**: 
       - If Target is High School (gh_), check Junior High (jh_) candidates first.
       - Select strictly necessary predecessors only.

    Output Format:
    - Return a JSON list of skill IDs ONLY.
    - **LIMIT**: Select at most **5** most critical prerequisite skills. Sort them by importance.
    - Example: ["jh_ID1", "gh_ID2"]
    - If no prerequisites found, return [].
    - DO NOT return markdown formatting like ```json ... ```. Just the raw JSON string.

    JSON Output:
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # 清理 Markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        result_ids = json.loads(text)
        
        # [修改] 硬性限制：只回傳前 5 個
        if isinstance(result_ids, list):
            return result_ids[:5]
        return []
        
    except Exception as e:
        print(f"   [AI Error] {e}")
        return []

# ==========================================
# 主程式
# ==========================================
def main():
    app = create_app()
    with app.app_context():
        print("🚀 啟動前置技能自動建構工具 (Auto-Build Prerequisites)")
        print("========================================================")
        
        # ==========================================
        # 1. 階層篩選 (Hierarchical Filtering)
        # ==========================================
        base_query = db.session.query(SkillCurriculum)

        # Level 1: Curriculum (課綱)
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇要處理的課綱 (Curriculum):")
        if selected_curr:
            base_query = base_query.filter(SkillCurriculum.curriculum == selected_curr)

        # Level 2: Grade (年級 - 基於上一層篩選結果)
        grades = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.grade)).order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級 (Grade):")
        if selected_grade:
            base_query = base_query.filter(SkillCurriculum.grade == selected_grade)

        # Level 3: Volume (冊別 - 基於上一層篩選結果)
        volumes = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.volume)).order_by(SkillCurriculum.volume).all()]
        selected_volume = get_user_selection(volumes, "請選擇冊別 (Volume):")
        if selected_volume:
            base_query = base_query.filter(SkillCurriculum.volume == selected_volume)

        # Level 4: Chapter (章節 - 基於上一層篩選結果)
        chapters = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.chapter)).order_by(SkillCurriculum.chapter).all()]
        selected_chapter = get_user_selection(chapters, "請選擇章節 (Chapter):")
        if selected_chapter:
            base_query = base_query.filter(SkillCurriculum.chapter == selected_chapter)

        # ==========================================
        # 2. 取得目標技能
        # ==========================================
        # Join SkillInfo 以便後續操作
        target_skills_query = base_query.with_entities(SkillCurriculum.skill_id).distinct()
        target_ids = [r[0] for r in target_skills_query.all()]
        
        # 查詢完整的 SkillInfo 物件
        target_skills = SkillInfo.query.filter(SkillInfo.skill_id.in_(target_ids)).order_by(SkillInfo.order_index).all()

        print(f"\n📋 共篩選出 {len(target_skills)} 個目標技能待處理。")
        if not target_skills:
            print("無資料，結束程式。")
            return

        # ==========================================
        # 3. 模式選擇與確認
        # ==========================================
        print("\n請選擇操作模式:")
        print("   [1] Safe Mode (安全模式): 僅處理目前「沒有」前置技能的項目")
        print("   [2] Power Mode (強制模式): 重新分析並「覆蓋」現有的前置技能")
        mode = input("👉 請輸入 (預設 1): ").strip() or "1"

        confirm = input("是否開始執行 AI 分析? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消。")
            return

        # ==========================================
        # 4. 準備全域快取 (Candidate Cache)
        # ==========================================
        print("📦 正在建立技能快取資料庫...")
        all_skills_query = SkillInfo.query.filter_by(is_active=True).order_by(SkillInfo.order_index).all()
        # 快取結構: 只存必要的比對資訊
        all_skills_cache = [
            {
                'id': s.skill_id, 
                'name': s.skill_ch_name, 
                'order': s.order_index
            } for s in all_skills_query
        ]
        # 建立 Map 方便寫入 DB
        skill_map = {s.skill_id: s for s in all_skills_query}

        # ==========================================
        # 5. 開始處理
        # ==========================================
        model = get_model()
        
        print("\n--- 開始分析 ---")
        for skill in tqdm(target_skills, desc="分析進度"):
            
            # SkillInfo.prerequisites 是一個 List (或 Query)
            current_prereqs = list(skill.prerequisites)
            if mode == '1' and len(current_prereqs) > 0:
                continue

            # A. 取得候選池
            candidates = get_candidate_skills(skill, all_skills_cache)
            if not candidates:
                continue 

            # B. 取得參考例題 (TextbookExample)
            example_data = None
            ex_obj = TextbookExample.query.filter_by(skill_id=skill.skill_id).first()
            if ex_obj:
                # 組合題目與詳解
                example_data = f"Problem: {ex_obj.problem_text}\nSolution: {ex_obj.detailed_solution or ex_obj.correct_answer}"

            # C. 呼叫 AI (限制最多 5 個)
            recommended_ids = identify_prerequisites(model, skill, candidates, example_data)
            
            # D. 寫入資料庫
            if recommended_ids:
                try:
                    # [Power Mode] 覆蓋前先清空
                    if mode == '2':
                        skill.prerequisites = []
                    
                    added_count = 0
                    for pre_id in recommended_ids:
                        if pre_id in skill_map:
                            prereq_skill = skill_map[pre_id]
                            # 避免重複添加
                            if prereq_skill not in skill.prerequisites:
                                skill.prerequisites.append(prereq_skill)
                                added_count += 1
                    
                    if added_count > 0:
                        db.session.commit()
                    
                    # 避免 Rate Limit
                    time.sleep(1) 
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ DB Write Error for {skill.skill_id}: {e}")

        print("\n✅ 處理完成！所有關聯已寫入資料庫。")

if __name__ == "__main__":
    main()