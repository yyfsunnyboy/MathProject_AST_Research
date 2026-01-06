# -*- coding: utf-8 -*-
# ==============================================================================
# ID: sync_skills_files.py
# Version: v7.7.7 (Hierarchical Selection + Batch Hybrid Mode)
# Description:
#   負責同步資料庫中的技能清單與本地實體檔案。
#   支援「階層式篩選」與「專家分工批次生成」。
#   Mode 4: 兩階段批次處理 (Batch Phase 1 -> Batch Phase 2) 以優化資源。
# ==============================================================================

import sys
import os
import glob
import time
import logging
from datetime import datetime
from tqdm import tqdm
from sqlalchemy import distinct

# ==============================================================================
# 1. 智慧路徑設定 (自動偵測專案根目錄)
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
# 嘗試往上找，直到找到 app.py，確保能正確 import
project_root = current_dir
while not os.path.exists(os.path.join(project_root, 'app.py')):
    parent = os.path.dirname(project_root)
    if parent == project_root: # 已經到頂層了還找不到
        print("❌ 錯誤：無法定位專案根目錄 (找不到 app.py)")
        sys.exit(1)
    project_root = parent

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import 必須在路徑設定之後
from app import create_app
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.code_generator import auto_generate_skill_code
# 引入架構師功能
from core.prompt_architect import generate_design_prompt
from config import Config

# [安全設定] 絕對不能刪除的檔案白名單
PROTECTED_FILES = {
    "Example_Program.py",
    "__init__.py", 
    "base_skill.py"
}

def get_user_selection(options, prompt_text):
    """通用互動函式"""
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

if __name__ == "__main__":
    app = create_app()
    
    # 設定 skills 資料夾路徑
    SKILLS_DIR = os.path.join(app.root_path, 'skills')
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ 找不到技能目錄: {SKILLS_DIR}")
        sys.exit(1)

    with app.app_context():
        # 為了避免 Log 打亂 tqdm 進度條，我們暫時關閉 werkzeug 的 log
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        # 取得當前設定的模型名稱 (用於顯示)
        role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
        current_model = role_config.get('model', 'Unknown')
        
        # 取得架構師模型名稱
        arch_config = Config.MODEL_ROLES.get('architect', {})
        arch_model = arch_config.get('model', 'Unknown (Phi-4)')

        print(f"🚀 開始同步資料庫與實體檔案 (v7.7.7)")
        print(f"🤖 工程師模型 (Coder): \033[1;36m{current_model}\033[0m") 
        print(f"🧠 架構師模型 (Architect): \033[1;35m{arch_model}\033[0m")
        
        # --- 1. 互動篩選 (層層過濾) ---
        
        # Level 1: 課綱
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇課綱:")

        # Level 2: 年級
        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if selected_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == selected_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")

        # Level 3: 冊別
        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if selected_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_vol = q_vol.filter(SkillCurriculum.grade == selected_grade)
        volumes = [r[0] for r in q_vol.all()]
        selected_vol = get_user_selection(volumes, "請選擇冊別:")

        # Level 4: 章節
        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if selected_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_chap = q_chap.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: q_chap = q_chap.filter(SkillCurriculum.volume == selected_vol)
        chapters = [r[0] for r in q_chap.all()]
        selected_chap = get_user_selection(chapters, "請選擇章節:")

        # Level 5: 單一技能 (新增功能)
        selected_skill_id = None
        # 只有當前面的篩選條件至少有一個不是 None 時，才列出技能，避免一次列出數百個
        if any([selected_curr, selected_grade, selected_vol, selected_chap]):
            q_skill = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).join(SkillCurriculum).filter(SkillInfo.is_active == True)
            if selected_curr: q_skill = q_skill.filter(SkillCurriculum.curriculum == selected_curr)
            if selected_grade: q_skill = q_skill.filter(SkillCurriculum.grade == selected_grade)
            if selected_vol: q_skill = q_skill.filter(SkillCurriculum.volume == selected_vol)
            if selected_chap: q_skill = q_skill.filter(SkillCurriculum.chapter == selected_chap)
            
            # 格式化選項：ID | 中文名稱
            skills_raw = q_skill.order_by(SkillInfo.order_index).all()
            skill_options = [f"{s.skill_id} | {s.skill_ch_name}" for s in skills_raw]
            
            if skill_options:
                selected_skill_str = get_user_selection(skill_options, "請選擇單一技能 (Optional):")
                if selected_skill_str:
                    # 從字串中切分出 ID (例如 "jh_math_1 | 因數" -> "jh_math_1")
                    selected_skill_id = selected_skill_str.split(' | ')[0].strip()

        is_full_scan = all(x is None for x in [selected_curr, selected_grade, selected_vol, selected_chap, selected_skill_id])

        # --- 2. 查詢目標技能 (套用所有篩選) ---
        print("\n🔍 正在查詢目標技能...")
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        
        if selected_curr: query = query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: query = query.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: query = query.filter(SkillCurriculum.volume == selected_vol)
        if selected_chap: query = query.filter(SkillCurriculum.chapter == selected_chap)
        if selected_skill_id: query = query.filter(SkillInfo.skill_id == selected_skill_id)
        
        target_skill_ids = set(r[0] for r in query.all())

        # --- 3. 掃描實體檔案 ---
        files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
        file_skill_ids = set()
        for f in files:
            fname = os.path.basename(f)
            if fname not in PROTECTED_FILES:
                file_skill_ids.add(fname.replace('.py', ''))
        
        # --- 4. 計算差異 ---
        to_create = target_skill_ids - file_skill_ids
        existing_in_scope = target_skill_ids.intersection(file_skill_ids)
        to_delete = set()
        if is_full_scan:
            all_active_ids = set(r[0] for r in db.session.query(SkillInfo.skill_id).filter_by(is_active=True).all())
            to_delete = file_skill_ids - all_active_ids

        # --- 5. 顯示狀態與詢問 ---
        print(f"\n📊 [範圍分析結果]")
        print(f"   - 範圍內技能總數: {len(target_skill_ids)}")
        print(f"   - 缺失檔案 (需新增): {len(to_create)}")
        print(f"   - 現有檔案 (可更新): {len(existing_in_scope)}")
        if is_full_scan:
            print(f"   - 孤兒檔案 (需刪除): {len(to_delete)}")

        if not target_skill_ids and not to_delete:
            print("✅ 範圍內無技能或無需操作，結束。")
            sys.exit(0)

        print("\n請選擇操作模式:")
        print("   [1] 僅生成缺失檔案 (Safe Mode)")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All)")
        if to_delete:
            print("   [3] 清理孤兒檔案 (Delete Orphans)")
        # 模式 4: 專家分工 (兩階段批次)
        print("   [4] 專家分工模式 (Phase 1: Gemini 批次 Prompt -> Phase 2: Qwen 批次 Code)") 
        
        mode = input("👉 請輸入選項: ").strip()
        
        list_to_process = sorted(list(set()))
        
        if mode == '1':
            list_to_process = sorted(list(to_create))
        elif mode == '2':
            list_to_process = sorted(list(to_create.union(existing_in_scope)))
        elif mode == '3' and to_delete:
            print("\n🗑️  模式 3: 正在清理孤兒檔案...")
            for skill_id in tqdm(to_delete, desc="Deleting"):
                try:
                    os.remove(os.path.join(SKILLS_DIR, f"{skill_id}.py"))
                except Exception as e:
                    print(f"   ❌ 刪除失敗: {e}")
            print("✅ 清理完成。")
            sys.exit(0)
        elif mode == '4':
            list_to_process = sorted(list(to_create.union(existing_in_scope)))
        else:
            print("❌ 無效選項或無操作。")
            sys.exit(0)

        if not list_to_process:
            print("✅ 沒有需要處理的檔案。")
            sys.exit(0)

        # --- [警示] 耗時提醒 ---
        count = len(list_to_process)
        base_time = 0.5 
        if "14b" in current_model.lower(): base_time = 3.5
        
        if mode == '4':
            print(f"\n⚠️  [專家模式] 將執行兩階段批次處理：")
            print(f"   Phase 1: {arch_model} 產生所有教案")
            print(f"   Phase 2: {current_model} 產生所有程式碼")
        
        total_est_min = count * base_time
        
        print(f"\n⚠️  [注意] 準備開始生成")
        print(f"   數量: {count} 題")
        print(f"   預估總耗時: {total_est_min:.1f} 分鐘")
        confirm = input("   確定要繼續嗎? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消。")
            sys.exit(0)

        # --- 6. 執行生成 (分流處理) ---
        
        if mode == '4':
            # ==========================================
            # Mode 4: 兩階段批次處理 (Batch Architect -> Batch Coder)
            # ==========================================
            print("\n" + "="*50)
            print(f"🧠 [Phase 1] 啟動架構師批次分析 ({arch_model})...")
            print("="*50)
            
            arch_success_count = 0
            pbar_arch = tqdm(list_to_process, desc="Phase 1 (Architect)", unit="file", ncols=100)
            
            for skill_id in pbar_arch:
                pbar_arch.set_description(f"Planning: {skill_id}")
                # 呼叫架構師生成 Prompt 並存入 DB
                success = generate_design_prompt(skill_id)
                if success:
                    arch_success_count += 1
            
            print(f"\n✅ Phase 1 完成: {arch_success_count}/{len(list_to_process)} 份教案已生成。\n")
            
            print("="*50)
            print(f"💻 [Phase 2] 啟動工程師批次實作 ({current_model})...")
            print("="*50)
            
            success_count = 0
            fail_count = 0
            
            pbar_code = tqdm(list_to_process, desc="Phase 2 (Coder)", unit="file", ncols=100)
            
            for skill_id in pbar_code:
                pbar_code.set_description(f"Coding: {skill_id}")
                
                # 執行 Code 生成 (code_generator 會自動讀取 Phase 1 存好的教案)
                result = auto_generate_skill_code(skill_id, queue=None)
                
                is_ok = False
                msg = ""
                if isinstance(result, tuple):
                    is_ok, msg = result
                else:
                    is_ok = result
                
                if is_ok:
                    success_count += 1
                    tqdm.write(f"   ✅ {skill_id}: Success")
                else:
                    fail_count += 1
                    tqdm.write(f"   ❌ {skill_id}: Failed ({msg})")

            print("\n" + "=" * 50)
            print(f"🎉 專家模式作業完成！")
            print(f"   成功: {success_count}")
            print(f"   失敗: {fail_count}")
            print("=" * 50)

        else:
            # ==========================================
            # Mode 1 & 2: 標準單階段處理 (Standard)
            # ==========================================
            print(f"\n🚀 開始生成任務... (Log 將顯示於下方)\n")
            success_count = 0
            fail_count = 0
            
            pbar = tqdm(list_to_process, desc="Progress", unit="file", ncols=100)
            
            for skill_id in pbar:
                pbar.set_description(f"Processing: {skill_id}")
                
                start_dt = datetime.now()
                start_str = start_dt.strftime("%H:%M:%S")
                
                tqdm.write("─" * 50)
                tqdm.write(f"▶ 正在處理: \033[1;33m{skill_id}\033[0m")
                tqdm.write(f"   ⏰ 開始時間: {start_str}")
                
                try:
                    result = auto_generate_skill_code(skill_id, queue=None)
                    
                    if isinstance(result, tuple):
                        is_ok, msg = result
                    else:
                        is_ok = result
                        msg = ""
                    
                    end_dt = datetime.now()
                    duration = (end_dt - start_dt).total_seconds()
                    end_str = end_dt.strftime("%H:%M:%S")

                    if is_ok:
                        success_count += 1
                        status_icon = "✅ 成功 [Clean Pass]"
                    else:
                        fail_count += 1
                        status_icon = f"❌ 失敗: {msg}"
                    
                    tqdm.write(f"   └─ 🏁 結束時間: {end_str} (總耗時 {duration:.2f}s) => {status_icon}")

                except KeyboardInterrupt:
                    print("\n⚠️  使用者強制中斷！")
                    break
                except Exception as e:
                    fail_count += 1
                    tqdm.write(f"❌ 異常 {skill_id}: {e}")
            
            print("\n" + "=" * 50)
            print(f"🎉 作業完成！")
            print(f"   成功: {success_count}")
            print(f"   失敗: {fail_count}")
            print("=" * 50)