# -*- coding: utf-8 -*-
# ==============================================================================
# ID: sync_skills_files.py
# Version: V9.2.0 (Scientific Standard Edition)
# Last Updated: 2026-01-27
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   本程式是科展實驗的核心執行控制台 (Experiment Runner)，負責驅動「自動出題與修復流水線」。
#   它主要用於執行 3x3 矩陣實驗 (3 Model Sizes x 3 Ablation Levels)，
#   藉此量化 AST/Regex 自癒機制如何提升小模型 (Local 14B/7B) 的代碼生成能力。
#
#   [Scientific Control Strategy]:
#   為了確保實驗數據具備統計學意義與可比性，本程式在執行「專家分工模式 (Mode 4)」時，
#   採取「單一黃金標準 (Unified Golden Standard)」策略：
#   無論當前測試的模型大小為何，架構師 (Architect) 階段強制生成並鎖定 'standard_14b' 規格書。
#   這確保了所有實驗組別 (Experimental Groups) 面對的都是同一份標準難度的題目規格 (Control Variable)。
#
# [Database Schema Usage]:
#   1. Read:  SkillInfo, SkillCurriculum (篩選目標技能範圍)
#   2. Read:  SkillGenCodePrompt (讀取 MASTER_SPEC 供 Coder 實作)
#   3. Write: SkillInfo.gemini_prompt (清理舊有 Prompt 標記)
#   4. Write: experiment_log (關鍵！記錄 Token 消耗、AST 修復次數、成功率等實驗數據)
#   5. Write: Local File System (寫入最終通過驗證的 .py 技能檔或失敗樣本)
#
# [Logic Flow]:
#   1. Range Selection    -> 使用者篩選課綱/年級/章節，鎖定測試範圍。
#   2. Gap Analysis       -> 比對資料庫與本地檔案，找出缺失或需更新的技能。
#   3. Experiment Config  -> 設定 Ablation ID (1:Bare, 2:Engineered, 3:Full-Healing) 與 Model Class。
#   4. Phase 1 Architect  -> (若選 Mode 4) 強制生成標準規格書 (Tag: standard_14b)。
#   5. Phase 2 Coder      -> 呼叫 code_generator 進行生成、AST/Regex 修復與沙盒驗證。
#   6. Data Logging       -> 將完整實驗過程寫入 experiment_log 以供後續分析。
# ==============================================================================

import sys
import os
import glob
import time
import logging
import ast # [Research] Import AST for robust parsing
from datetime import datetime
from tqdm import tqdm
from sqlalchemy import distinct

# ==============================================================================
# 1. 智慧路徑設定 (自動偵測專案根目錄)
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while not os.path.exists(os.path.join(project_root, 'app.py')):
    parent = os.path.dirname(project_root)
    if parent == project_root:
        print("❌ 錯誤：無法定位專案根目錄 (找不到 app.py)")
        sys.exit(1)
    project_root = parent

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models import db, SkillInfo, SkillCurriculum, TextbookExample, SkillGenCodePrompt
# [Research] Import requested functions
from core.code_generator import auto_generate_skill_code
from core.prompt_architect import generate_v15_spec
from config import Config

PROTECTED_FILES = {
    "Example_Program.py",
    "__init__.py", 
    "base_skill.py"
}

def get_user_selection(options, prompt_text):
    if not options: return None
    # [Fix] 移除 sorted()，保留外部傳入的正確順序 (display_order)
    options = [o for o in options if o is not None]
    
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

def reset_skill_prompts(skill_ids):
    """
    [Fix] 使用空字串 "" 而非 None 來清空 Prompt。
    解決 sqlite3.IntegrityError: NOT NULL constraint failed
    """
    if not skill_ids: return
    try:
        # 注意: 這裡是清空 gemini_prompt 欄位 (舊欄位)，雖然現在主要用 SkillGenCodePrompt 表
        # 但為了保持相容性，我們還是清一下
        SkillInfo.query.filter(SkillInfo.skill_id.in_(skill_ids)).update({SkillInfo.gemini_prompt: ""}, synchronize_session=False)
        db.session.commit()
        # 同時也可以考慮清空 SkillGenCodePrompt 表中對應的 standard_14b 記錄，強制重新生成
        # 但 generate_v15_spec 會自動覆蓋，所以不強制 delete 也可以
        tqdm.write(f"🧹 已清空 {len(skill_ids)} 筆舊資料標記。")
    except Exception as e:
        tqdm.write(f"⚠️ 清空舊規格失敗: {e}")
        db.session.rollback()

def auto_patch_missing_functions(code_content, skill_id):
    """
    [Research Edition] 使用 AST 進行結構化偵測與修復
    """
    patches = []
    tree = None
    
    try:
        tree = ast.parse(code_content)
    except Exception as e:
        tqdm.write(f"⚠️ AST Parse Error for {skill_id}: {e}")
        pass # Continue to try raw string check if AST fails initially

    has_generate = False
    has_check = False
    generate_args = []
    
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'generate':
                    has_generate = True
                    generate_args = [a.arg for a in node.args.args]
                elif node.name == 'check':
                    has_check = True

    # 1. 檢查 generate 進入點
    if not has_generate:
        # Fallback raw check
        if "def generate" not in code_content:
            # 尋找是否有類似 generate_number_line 這樣的變體
            import re
            alt_gen = re.findall(r'def (generate_[a-zA-Z0-9_]+)\(', code_content)
            if alt_gen:
                patches.append(f"\n# [Auto-Fix] Alias {alt_gen[0]} to generate")
                patches.append(f"generate = {alt_gen[0]}")
            else:
                # 注入強力調度器
                patches.append("\n# [Auto-Fix] Injected Robust Dispatcher")
                patches.append("def generate(level=1, **kwargs): return {'question_text': '題目生成失敗(Dispatcher Missing)', 'correct_answer': 'N/A'}")
    
    elif not any(arg in ['level', 'kwargs'] for arg in generate_args):
        # 如果有 generate 但沒有參數，這會導致 crash
        code_content = code_content.replace("def generate():", "def generate(level=1, **kwargs):")

    # 2. 檢查 check 函式
    if not has_check and "def check" not in code_content:
        patches.append("\n# [Auto-Fix] Emergency Fallback Check")
        patches.append("def check(u, c): return {'correct': False, 'result': '評分系統異常(Check Missing)'}")

    if patches:
        tqdm.write(f"🔧 {skill_id}: Detected missing functions via AST. Applying patches.")
        return code_content + "\n" + "\n".join(patches)
    
    return code_content

def run_expert_pipeline(skill_ids, arch_model, current_model, ablation_id, model_size_class, prompt_level):
    """
    執行完整的專家分工流程 (Phase 1 + Phase 2)
    [Research]: Supports Ablation Logic
    [V9.2 Update]: 強制統一使用 'standard_14b' 規格，確保與 Factory 標準一致。
    """
    if not skill_ids: return
    
    # Step 0: 清空舊 Spec
    print("\n" + "="*50)
    print(f"🧹 [Step 0] 清空舊規格書...")
    print("="*50)
    reset_skill_prompts(skill_ids)

    # Step 1: Architect
    # =========================================================================
    # [Scientific Standard Fix] 關鍵修正！
    # 無論 current_model 是 7B/14B/Cloud，這裡永遠鎖定 'standard_14b'。
    # 這保證了所有模型使用的是同一份「標準難度」的規格書 (Control Variable)。
    # =========================================================================
    target_tag = 'standard_14b' 
    
    print("\n" + "="*60)
    print(f"🧠 [Phase 1] Architect Analysis (Model: {arch_model})")
    print(f"   🎯 Experiment Control: Using Unified Prompt Tag '{target_tag}'")
    print(f"   🤖 Coder Identity: {current_model} (Will be logged in Experiment Log)")
    print("="*60)
    
    arch_success_count = 0
    pbar_arch = tqdm(skill_ids, desc="Phase 1 (Architect)", unit="file", ncols=100)
    
    for skill_id in pbar_arch:
        pbar_arch.set_description(f"Planning: {skill_id}")
        try:
            # 呼叫 Architect，傳入強制統一的 tag
            result = generate_v15_spec(skill_id, model_tag=target_tag, architect_model=arch_model)
            success = result.get('success', False)
        except Exception as e:
            tqdm.write(f"   ❌ {skill_id} Architect Error: {e}")
            success = False

        if success:
            arch_success_count += 1
    
    print(f"\n✅ Phase 1 完成: {arch_success_count}/{len(skill_ids)} 份標準教案已生成。\n")
    
    # Step 2: Coder
    # 這裡才把真正負責寫 code 的模型身分傳下去，記錄在 experiment_log
    execute_coder_phase(skill_ids, current_model, ablation_id, model_size_class, prompt_level)

def execute_coder_phase(skill_ids, current_model, ablation_id, model_size_class, prompt_level):
    print("="*50)
    print(f"💻 [Step 2] 啟動工程師批次實作 ({current_model})")
    print(f"   🧬 Experiment Config: Ablation={ablation_id} | Size={model_size_class} | Prompt={prompt_level}")
    print("="*50)
    
    success_count = 0
    fail_count = 0
    
    pbar_code = tqdm(skill_ids, desc="Phase 2 (Coder)", unit="file", ncols=100)
    
    for skill_id in pbar_code:
        pbar_code.set_description(f"Coding: {skill_id}")
        
        # [Research] Pass experiment params and unpack 3 return values
        try:
            is_ok, msg, metrics = auto_generate_skill_code(
                skill_id, 
                queue=None, 
                ablation_id=ablation_id, 
                model_size_class=model_size_class,
                prompt_level=prompt_level
            )

            if is_ok:
                # [Research] Check Syntax Score
                is_valid = metrics.get('is_valid', False)
                is_failed = not is_valid
                
                if is_failed:
                    fail_count += 1
                    tqdm.write(f"   ⚠️ {skill_id}: Validation Failed | Score=0")
                else:
                    success_count += 1
                    fixes = metrics.get('fixes', 0)
                    repair_info = f"Fixes={fixes}" if fixes > 0 else "Clean Pass"
                    tqdm.write(f"   ✅ {skill_id}: Success | Score=100 | {repair_info}")
                
                # Post-Validation Patching
                try:
                    skill_path = os.path.join(project_root, 'skills', f"{skill_id}.py")
                    if os.path.exists(skill_path):
                        with open(skill_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # --- 確保實驗純淨度：只有 Ab3 能享受最後的 AST 補丁 ---
                        if ablation_id == 3:
                            patched_content = auto_patch_missing_functions(content, skill_id)
                        else:
                            patched_content = content # Ab1, Ab2 保持「原始慘狀」以利數據對比
                        
                        
                        if patched_content != content:
                            with open(skill_path, 'w', encoding='utf-8') as f:
                                f.write(patched_content)
                            tqdm.write(f"   🔧 {skill_id}: Patched missing functions.")
                        
                        # 2. [Versioned Storage Strategy] (Research Last Will)
                        
                        if is_failed:
                            # 💥 [科研遺書機制]: 失敗也要存
                            file_name = f"{skill_id}_{model_size_class}_Ab{ablation_id}_FAILED.py"
                            tqdm.write(f"   💾 保存壞標本: {file_name}")
                        else:
                            file_name = f"{skill_id}_{model_size_class}_Ab{ablation_id}.py"

                        file_path = os.path.join(SKILLS_DIR, file_name)
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(patched_content)
                            
                        if not is_failed:
                            tqdm.write(f"   📦 Isolated Save: {file_name}")

                except Exception as e:
                     tqdm.write(f"   ❌ {skill_id} Patching/Saving Error: {e}")

            else:
                fail_count += 1
                tqdm.write(f"   ❌ {skill_id}: Failed ({msg})")

        except Exception as e:
            fail_count += 1
            tqdm.write(f"   ❌ {skill_id} Critical Error: {e}")

    print("\n" + "=" * 50)
    print(f"🎉 作業完成！")
    print(f"   成功: {success_count} | 失敗: {fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    app = create_app()
    
    SKILLS_DIR = os.path.join(project_root, 'skills')
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ 找不到技能目錄: {SKILLS_DIR}")
        sys.exit(1)

    with app.app_context():
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
        current_model = role_config.get('model', 'Unknown')
        
        arch_config = Config.MODEL_ROLES.get('architect', {})
        arch_model = arch_config.get('model', 'Unknown')

        print(f"🚀 開始同步資料庫與實體檔案 (V9.2.0 Scientific Standard Edition)")
        print(f"🧠 架構師模型 (Architect): \033[1;35m{arch_model}\033[0m")        
        print(f"🤖 工程師模型 (Coder): \033[1;36m{current_model}\033[0m")         
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

        selected_skill_id = None
        if any([selected_curr, selected_grade, selected_vol, selected_chap]):
            q_skill = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).join(SkillCurriculum).filter(SkillInfo.is_active == True)
            if selected_curr: q_skill = q_skill.filter(SkillCurriculum.curriculum == selected_curr)
            if selected_grade: q_skill = q_skill.filter(SkillCurriculum.grade == selected_grade)
            if selected_vol: q_skill = q_skill.filter(SkillCurriculum.volume == selected_vol)
            if selected_chap: q_skill = q_skill.filter(SkillCurriculum.chapter == selected_chap)
            
            skills_raw = q_skill.order_by(SkillCurriculum.display_order).all()
            skill_options = [f"{s.skill_id} | {s.skill_ch_name}" for s in skills_raw]
            
            if skill_options:
                selected_skill_str = get_user_selection(skill_options, "請選擇單一技能 (Optional):")
                if selected_skill_str:
                    selected_skill_id = selected_skill_str.split(' | ')[0].strip()

        is_full_scan = all(x is None for x in [selected_curr, selected_grade, selected_vol, selected_chap, selected_skill_id])

        # --- 2. 查詢目標技能 ---
        print("\n🔍 正在查詢目標技能...")
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        
        if selected_curr: query = query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: query = query.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: query = query.filter(SkillCurriculum.volume == selected_vol)
        if selected_chap: query = query.filter(SkillCurriculum.chapter == selected_chap)
        if selected_skill_id: query = query.filter(SkillInfo.skill_id == selected_skill_id)
        
        target_skill_ids = set(r[0] for r in query.all())

        # --- 3. 掃描實體檔案 by glob ---
        files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
        file_skill_ids = set()
        for f in files:
            fname = os.path.basename(f)
            if fname not in PROTECTED_FILES:
                file_skill_ids.add(fname.replace('.py', ''))
        
        to_create = target_skill_ids - file_skill_ids
        existing_in_scope = target_skill_ids.intersection(file_skill_ids)
        to_delete = set()
        if is_full_scan:
            all_active_ids = set(r[0] for r in db.session.query(SkillInfo.skill_id).filter_by(is_active=True).all())
            to_delete = file_skill_ids - all_active_ids

        print(f"\n📊 [範圍分析結果]")
        print(f"   - 範圍內技能總數: {len(target_skill_ids)}")
        print(f"   - 缺失檔案 (需新增): {len(to_create)}")
        print(f"   - 現有檔案 (可更新): {len(existing_in_scope)}")
        if is_full_scan:
            print(f"   - 孤兒檔案 (需刪除): {len(to_delete)}")

        if not target_skill_ids and not to_delete:
            print("✅ 範圍內無技能或無需操作，結束。")
            sys.exit(0)

        # [Research Edition] 整合模式 3 與參數提升
        print("\n請選擇操作模式:")
        print("   [1] 僅生成缺失檔案 (Safe Mode)")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All)")
        print("   [3] 僅生成選定範圍內尚未生成的檔案 (Incremental Scope)") 
        print("   [4] 專家分工模式：全部重跑 (Full Pipeline + AST Healing)") 
        if to_delete:
            print("   [5] 清理孤兒檔案 (Delete Orphans)")
        
        mode = input("👉 請輸入選項: ").strip()
        
        list_to_process = []
        run_full_pipeline = False
        
        # 判斷處理清單
        if mode == '1':
            list_to_process = sorted(list(to_create))
        elif mode == '2':
            list_to_process = sorted(list(target_skill_ids)) # 強制範圍內全跑
        elif mode == '3':
            list_to_process = sorted(list(target_skill_ids.intersection(to_create))) # 範圍內且缺失
        elif mode == '4':
            list_to_process = sorted(list(target_skill_ids))
            run_full_pipeline = True
        elif mode == '5' and to_delete:
            print("\n🗑️  正在清理孤兒檔案...")
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

        # --- [Research] 實驗參數設定 ---
        if mode in ['1', '2', '3', '4']:
            print("\n" + "="*60)
            print("🧪 [實驗變因控制] 請選擇本次生成的 Ablation 層級:")
            print("   1: Bare (Baseline)    -> 簡單 Prompt + 無修復 (測試原生能力)")
            print("   2: Engineered (Prompt) -> V15.1 Spec + 無修復 (測試提示工程貢獻)")
            print("   3: Full Healing (Sys)  -> V15.1 Spec + Regex/AST 修復 (測試系統全能力)")
            print("="*60)
            
            ab_input = input("   👉 輸入 Ablation ID (1/2/3, 預設 3): ").strip()
            ablation_id = int(ab_input) if ab_input in ['1', '2', '3'] else 3
            
            # 對應實驗描述，方便日誌紀錄
            ab_desc = {1: "Bare", 2: "Engineered-Only", 3: "Full-Healing"}
            print(f"✅ 已設定實驗組別：{ab_desc[ablation_id]}")

            # --- [UI Improvement] Model Size Class Selection ---
            print("\n" + "="*60)
            print("📏 [實驗變因控制] 請選擇 Model Size Class:")
            print("   1: Cloud     -> 大型模型 (如 Gemini, GPT-4)")
            print("   2: Local 14B -> 中型模型 (如 Qwen 2.5-14B)")
            print("   3: Edge 7B   -> 小型模型 (如 Llama 3-8B, Phi-3)")
            print("="*60)
            
            size_map = {'1': 'Cloud', '2': '14B', '3': '7B'}
            ms_input = input("   👉 輸入選項 (1/2/3, 預設 1): ").strip()
            # 預設為 'Cloud'
            model_size_class = size_map.get(ms_input, 'Cloud')
            print(f"✅ 已設定模型量級：{model_size_class}")
            
            prompt_level = ab_desc[ablation_id] # Update prompt_level to match description

        if not list_to_process:
            print("✅ 沒有需要處理的檔案。")
            sys.exit(0)

        # Confirm
        count = len(list_to_process)
        print(f"\n⚠️  [注意] 準備開始")
        print(f"   數量: {count} 題")
        confirm = input("   確定要繼續嗎? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(0)

        # Execution
        if run_full_pipeline:
            run_expert_pipeline(
                list_to_process, 
                arch_model, 
                current_model,
                ablation_id,
                model_size_class,
                prompt_level
            )
        else:
            # Code Gen Only (Phase 2)
            execute_coder_phase(
                list_to_process, 
                current_model, 
                ablation_id, 
                model_size_class, 
                prompt_level
            )