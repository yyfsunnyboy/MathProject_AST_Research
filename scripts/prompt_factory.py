# -*- coding: utf-8 -*-
# ==============================================================================
# ID: prompt_factory.py
# Version: V9.2.0 (Scientific Standard Edition)
# Last Updated: 2026-01-27
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   本程式是「自動出題系統」的上游工廠，負責生產「MASTER_SPEC (主規格書)」。
#   為了在科展實驗中建立嚴謹的對照組 (Control Group)，本版本移除了所有針對
#   不同模型大小 (7B/Cloud) 的差異化 Prompt。
#
#   我們採用「單一黃金標準 (Unified Golden Standard)」策略：
#   所有題目均根據 14B 模型的理解能力生成最完整、標準的規格書。
#   這確保了後續實驗中，不同模型的表現差異純粹來自於「模型本身能力」
#   與「AST+Regex 自癒系統」的效能，而非 Prompt 的難易度差別。
#
# [Database Schema Usage]:
#   1. Read:  SkillInfo, SkillCurriculum (篩選目標技能範圍)
#   2. Read:  TextbookExample (讀取課本例題作為 RAG 來源)
#   3. Write: SkillGenCodePrompt (寫入生成的 MASTER_SPEC)
#
# [Logic Flow]:
#   1. User Selects Range -> 選擇課綱/年級/章節
#   2. Factory Execution  -> 呼叫 Architect (Gemini) 分析課本例題
#   3. Standardization    -> 強制標記為 'standard_14b' 並寫入資料庫
#   4. Downstream         -> code_generator.py 讀取此唯一標準規格進行實作
# ==============================================================================

import sys
import os
import time
from tqdm import tqdm
from sqlalchemy import distinct

# --- 1. 路徑修正 (確保能找到根目錄的 models 與 app) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models import db, SkillInfo, SkillCurriculum, SkillGenCodePrompt
from core.prompt_architect import generate_v15_spec

def get_user_selection(options, prompt_text):
    """移植自 v8.6.2 的選單功能"""
    if not options: return None
    options = sorted([o for o in options if o is not None])
    
    print(f"\n{prompt_text}")
    print("   [0] ALL (全部/跳過)")
    for i, opt in enumerate(options, 1):
        print(f"   [{i}] {opt}")
        
    while True:
        try:
            choice = input("👉 請選擇 (輸入數字): ").strip()
            if choice == '0': return None
            idx = int(choice) - 1
            if 0 <= idx < len(options): return options[idx]
            print("❌ 輸入無效，請重試。")
        except ValueError:
            print("❌ 請輸入數字。")

def run_architect_factory(skill_ids):
    """
    執行 Prompt 生成任務 (Standardized Pipeline)
    強制使用 'standard_14b' 標籤，不接受分級參數。
    """
    # [Scientific Control] 強制統一標籤
    target_tag = 'standard_14b'

    print("\n" + "="*60)
    print(f"🧠 [Prompt Factory] 啟動標準化規格生成程序")
    print(f"   - 技能數量: {len(skill_ids)}")
    print(f"   - 生成標準: Unified Golden Spec (Targeting 14B)")
    print(f"   - 寫入標籤: {target_tag}")
    print("="*60)

    success_count = 0
    fail_count = 0

    # 開始批次處理
    for skill_id in tqdm(skill_ids, desc="Generating Standard Specs", unit="skill"):
        try:
            # 呼叫核心架構師 (Prompt Architect)
            # 注意: 這裡的 model_tag 僅作為 DB 標記，Architect 內部已統一 Prompt 邏輯
            result = generate_v15_spec(skill_id, model_tag=target_tag)
            
            if result.get('success'):
                # 簡單顯示成功版本，不刷頻
                tqdm.write(f"✅ {skill_id}: Success")
                success_count += 1
            else:
                tqdm.write(f"❌ {skill_id} Failed: {result.get('message')}")
                fail_count += 1
        except Exception as e:
            tqdm.write(f"💥 {skill_id} Critical Error: {e}")
            fail_count += 1

    print("\n" + "="*60)
    print(f"🎉 標準化備料完成！")
    print(f"   成功生成: {success_count} 筆 MASTER_SPEC")
    print(f"   失敗數量: {fail_count} 筆")
    print(f"   說明: 下游 code_generator 將讀取最新的 'MASTER_SPEC' 進行實作。")
    print("="*60)

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        print("\n============================================================")
        print("🚀 Math-Master Prompt Factory (Scientific Standard Edition)")
        print("   目標: 為 AST 自癒實驗建立統一的 14B 基準規格書")
        print("============================================================")
        
        # --- 1. 階層式選取 (嚴格參考 sync_skills_files.py) ---
        
        # 1.1 選擇課綱
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        sel_curr = get_user_selection(curriculums, "請選擇課綱:")

        # 1.2 選擇年級
        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if sel_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == sel_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        sel_grade = get_user_selection(grades, "請選擇年級:")

        # 1.3 選擇冊別
        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if sel_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: q_vol = q_vol.filter(SkillCurriculum.grade == sel_grade)
        volumes = [r[0] for r in q_vol.all()]
        sel_vol = get_user_selection(volumes, "請選擇冊別:")

        # 1.4 選擇章節
        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if sel_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: q_chap = q_chap.filter(SkillCurriculum.grade == sel_grade)
        if sel_vol: q_chap = q_chap.filter(SkillCurriculum.volume == sel_vol)
        chapters = [r[0] for r in q_chap.all()]
        sel_chap = get_user_selection(chapters, "請選擇章節:")

        # 1.5 單一技能挑選
        sel_skill_id = None
        if any([sel_curr, sel_grade, sel_vol, sel_chap]):
            q_skill = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).join(SkillCurriculum).filter(SkillInfo.is_active == True)
            if sel_curr: q_skill = q_skill.filter(SkillCurriculum.curriculum == sel_curr)
            if sel_grade: q_skill = q_skill.filter(SkillCurriculum.grade == sel_grade)
            if sel_vol: q_skill = q_skill.filter(SkillCurriculum.volume == sel_vol)
            if sel_chap: q_skill = q_skill.filter(SkillCurriculum.chapter == sel_chap)
            
            skills_raw = q_skill.order_by(SkillCurriculum.display_order).all()
            skill_opts = [f"{s.skill_id} | {s.skill_ch_name}" for s in skills_raw]
            
            if skill_opts:
                sel_skill_str = get_user_selection(skill_opts, "請選擇單一技能 (Optional):")
                if sel_skill_str:
                    sel_skill_id = sel_skill_str.split(' | ')[0].strip()

        # --- 2. 鎖定最終清單 ---
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: query = query.filter(SkillCurriculum.grade == sel_grade)
        if sel_vol: query = query.filter(SkillCurriculum.volume == sel_vol)
        if sel_chap: query = query.filter(SkillCurriculum.chapter == sel_chap)
        if sel_skill_id: query = query.filter(SkillInfo.skill_id == sel_skill_id)
        
        target_ids = list(set([r[0] for r in query.all()]))
        target_ids.sort()

        if not target_ids:
            print("❌ 找不到符合條件的技能。")
            sys.exit(0)

        # --- 3. 執行確認 (移除分級選單) ---
        print(f"\n⚠️  準備為 {len(target_ids)} 個技能生成 'Standard 14B' 規格書。")
        print("   (這將覆蓋先前的規格，確保實驗基準一致)")
        
        if input("👉 確認執行？ (y/n): ").lower() == 'y':
            run_architect_factory(target_ids)
        else:
            print("操作已取消。")