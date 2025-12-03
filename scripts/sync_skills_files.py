import sys
import os
import glob
from tqdm import tqdm
from sqlalchemy import distinct

# 1. 設定專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, SkillInfo, SkillCurriculum
from core.code_generator import auto_generate_skill_code

# [安全設定] 絕對不能刪除的檔案白名單
PROTECTED_FILES = {
    "Example_Program.py",
    "__init__.py", 
    "base_skill.py"
}

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

if __name__ == "__main__":
    app = create_app()
    
    # 設定 skills 資料夾路徑
    SKILLS_DIR = os.path.join(app.root_path, 'skills')
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ 找不到技能目錄: {SKILLS_DIR}")
        sys.exit(1)

    with app.app_context():
        print("🚀 開始同步資料庫與實體檔案 (互動模式)...")
        
        # --- 1. 互動篩選 (Curriculum -> Grade -> Volume -> Chapter) ---

        # Level 1: Curriculum
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇課綱:")

        # Level 2: Grade
        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if selected_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == selected_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")

        # Level 3: Volume
        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if selected_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_vol = q_vol.filter(SkillCurriculum.grade == selected_grade)
        volumes = [r[0] for r in q_vol.all()]
        selected_vol = get_user_selection(volumes, "請選擇冊別:")

        # Level 4: Chapter
        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if selected_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_chap = q_chap.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: q_chap = q_chap.filter(SkillCurriculum.volume == selected_vol)
        chapters = [r[0] for r in q_chap.all()]
        selected_chap = get_user_selection(chapters, "請選擇章節:")

        # 判斷是否全域掃描 (如果全部都選 0/None)
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
        # A. 缺失檔案 (在範圍內, 但沒檔案) -> Need Create
        to_create = target_skill_ids - file_skill_ids
        
        # B. 現有檔案 (在範圍內, 且有檔案) -> Can Regenerate
        existing_in_scope = target_skill_ids.intersection(file_skill_ids)

        # C. 孤兒檔案 (只有 Full Scan 才計算)
        to_delete = set()
        if is_full_scan:
            all_active_ids = set(r[0] for r in db.session.query(SkillInfo.skill_id).filter_by(is_active=True).all())
            to_delete = file_skill_ids - all_active_ids

        # --- 5. 顯示狀態與詢問 ---
        print(f" [範圍分析結果]")
        print(f"   - 範圍內技能總數: {len(target_skill_ids)}")
        print(f"   - 缺失檔案 (需新增): {len(to_create)}")
        print(f"   - 現有檔案 (可更新): {len(existing_in_scope)}")
        if is_full_scan:
            print(f"   - 孤兒檔案 (需刪除): {len(to_delete)}")
        else:
            print(f"   - 孤兒檔案: (略過，非全域掃描)")

        if not target_skill_ids and not to_delete:
            print("✅ 範圍內無技能或無需操作，結束。")
            sys.exit(0)

        print("\n請選擇操作模式:")
        print("   [1] 僅生成缺失檔案 (Safe Mode)")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All)")
        if to_delete:
            print("   [3] 清理孤兒檔案 (Delete Orphans)")
        
        mode = input("👉 請輸入選項: ").strip()
        
        list_to_process = set()
        is_regenerate = False

        if mode == '1':
            list_to_process = to_create
            print(f"\n⚙️  模式 1: 將生成 {len(list_to_process)} 個新檔案...")
        elif mode == '2':
            list_to_process = to_create.union(existing_in_scope)
            is_regenerate = True
            print(f"\n⚙️  模式 2: 將強制重新生成 {len(list_to_process)} 個檔案...")
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

        # --- 6. 執行生成 (這裡是重點，縮排必須正確) ---
        success_count = 0
        fail_count = 0
        
        # 使用 tqdm 顯示進度
        for skill_id in tqdm(list_to_process, desc="Generating"):
            try:
                # 呼叫核心生成函式
                # 注意：queue=None 表示同步執行
                result = auto_generate_skill_code(skill_id, queue=None)
                
                # auto_generate_skill_code 可能回傳 (bool, msg) 或 bool，視實作而定
                # 這裡做個相容性檢查
                if isinstance(result, tuple):
                    is_ok = result[0]
                else:
                    is_ok = result

                if is_ok:
                    success_count += 1
                else:
                    fail_count += 1
                    print(f"   ❌ 失敗: {skill_id}")

            except Exception as e:
                fail_count += 1
                print(f"   ❌ 異常 {skill_id}: {e}")
        
        print("-" * 50)
        print(f"🎉 作業完成！ 成功: {success_count} / 失敗: {fail_count}")