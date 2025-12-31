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
    print("   [0] ALL (全部處理)")
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
        
        print(f"🚀 開始同步資料庫與實體檔案")
        print(f"🤖 目前使用模型: \033[1;36m{current_model}\033[0m") # 青色高亮
        
        # --- 1. 互動篩選 ---
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇課綱:")

        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if selected_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == selected_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")

        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if selected_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_vol = q_vol.filter(SkillCurriculum.grade == selected_grade)
        volumes = [r[0] for r in q_vol.all()]
        selected_vol = get_user_selection(volumes, "請選擇冊別:")

        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if selected_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_chap = q_chap.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: q_chap = q_chap.filter(SkillCurriculum.volume == selected_vol)
        chapters = [r[0] for r in q_chap.all()]
        selected_chap = get_user_selection(chapters, "請選擇章節:")

        is_full_scan = all(x is None for x in [selected_curr, selected_grade, selected_vol, selected_chap])

        # --- 2. 查詢目標技能 ---
        print("\n🔍 正在查詢目標技能...")
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        
        if selected_curr: query = query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: query = query.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: query = query.filter(SkillCurriculum.volume == selected_vol)
        if selected_chap: query = query.filter(SkillCurriculum.chapter == selected_chap)
        
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
        else:
            print("❌ 無效選項或無操作。")
            sys.exit(0)

        if not list_to_process:
            print("✅ 沒有需要處理的檔案。")
            sys.exit(0)

        # --- [警示] 耗時提醒 ---
        count = len(list_to_process)
        # 如果是 7B 模型，估計 1 分鐘；如果是 14B，估計 3-5 分鐘
        est_time_per_file = 0.5 if "7b" in current_model.lower() else 3.5 
        total_est_min = count * est_time_per_file
        
        print(f"\n⚠️  [注意] 準備開始生成")
        print(f"   模型: {current_model}")
        print(f"   數量: {count} 題")
        print(f"   預估總耗時: {total_est_min:.1f} 分鐘")
        confirm = input("   確定要繼續嗎? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消。")
            sys.exit(0)

        # --- 6. 執行生成 (詳細資訊版) ---
        print(f"\n🚀 開始生成任務... (Log 將顯示於下方)\n")
        success_count = 0
        fail_count = 0
        
        pbar = tqdm(list_to_process, desc="Progress", unit="file", ncols=100)
        
        for skill_id in pbar:
            pbar.set_description(f"Processing: {skill_id}")
            
            # 1. 準備顯示資訊
            start_dt = datetime.now()
            start_str = start_dt.strftime("%H:%M:%S")
            
            # 查詢例題數量 (模擬 Generator 內部的查詢)
            rag_count = TextbookExample.query.filter_by(skill_id=skill_id).count()
            
            # 使用 tqdm.write 輸出，避免打斷進度條
            tqdm.write("─" * 50)
            tqdm.write(f"▶ 正在生成: \033[1;33m{skill_id}\033[0m") # 黃色
            tqdm.write(f"  ├─ 🤖 模型: {current_model}")
            tqdm.write(f"  ├─ 📚 RAG 例題數: {rag_count} (將取前 8-10 題)")
            tqdm.write(f"  └─ ⏰ 開始時間: {start_str}")
            
            try:
                # 2. 執行生成
                # auto_generate_skill_code 內部會寫入 experiment_log
                result = auto_generate_skill_code(skill_id, queue=None)
                
                if isinstance(result, tuple):
                    is_ok, msg = result
                else:
                    is_ok = result
                    msg = ""
                
                # 3. 結算時間
                end_dt = datetime.now()
                duration = (end_dt - start_dt).total_seconds()
                end_str = end_dt.strftime("%H:%M:%S")

                if is_ok:
                    success_count += 1
                    status_icon = "✅ 成功 [Clean Pass]"
                else:
                    fail_count += 1
                    status_icon = f"❌ 失敗: {msg}"
                
                tqdm.write(f"  └─ 🏁 結束時間: {end_str} (耗時 {duration:.2f}s) => {status_icon}")
                tqdm.write(f"  (📝 已寫入 experiment_log)")

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