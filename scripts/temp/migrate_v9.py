# scripts/migrate_v9.py
# Version: v9.0 Migration Tool
import sys
import os
import pandas as pd
from datetime import datetime

# 設定路徑以匯入主程式
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
from app import app, db
# 注意：這裡匯入的是新版 models.py 定義的類別
from models import SkillInfo, SkillGenCodePrompt, ExperimentLog, TextbookExample, init_db

def migrate_from_excel(backup_file="backup_v8_before_upgrade.xlsx"):
    print(f"🚀 [v9.0 Upgrade] 開始執行資料庫升級與遷移...")
    print(f"📂 來源備份檔: {backup_file}")
    
    if not os.path.exists(backup_file):
        print(f"❌ 錯誤：找不到備份檔案 {backup_file}，請確認檔案名稱或路徑。")
        return

    with app.app_context():
        # 1. 初始化全新的 v9.0 資料庫
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"⚠️  警告：偵測到現有資料庫 {db_path}，將會被覆蓋！")
        
        print("🔨 正在建立 v9.0 資料庫結構 (Tables)...")
        # 使用我們剛更新的 init_db 函式
        init_db(db.engine)
        print("✅ 資料庫結構建立完成！")

        # 2. 讀取 Excel
        try:
            xls = pd.ExcelFile(backup_file)
        except Exception as e:
            print(f"❌ Excel 讀取失敗: {e}")
            return

        # --- A. 遷移 SkillInfo & 自動拆分 Prompt ---
        if 'SkillInfo' in xls.sheet_names:
            print("📦 正在遷移 SkillInfo 並拆分 Prompt 到 SkillGenCodePrompt...")
            df_skills = pd.read_excel(xls, 'SkillInfo')
            df_skills = df_skills.where(pd.notnull(df_skills), None)
            
            count_skills = 0
            count_prompts = 0
            
            for _, row in df_skills.iterrows():
                skill_id = row.get('skill_id')
                if not skill_id: continue

                # A-1. 建立 SkillInfo (新版模型已無 gemini_prompt 欄位，或我們選擇忽略它)
                # 這裡我們只填入 SkillInfo 真正需要的欄位
                skill = SkillInfo(
                    skill_id=skill_id,
                    skill_ch_name=row.get('skill_ch_name', '未命名'),
                    skill_en_name=row.get('skill_en_name', 'Unnamed'),
                    category=row.get('category'),
                    description=row.get('description', ''),
                    input_type=row.get('input_type', 'text'),
                    # gemini_prompt 欄位在 v9.0 models.py 裡如果還在，就留空或填入；
                    # 如果 models.py 裡移除了，這裡就不要填。
                    # 假設您 models.py 裡還保留該欄位當 legacy backup，我們填入空字串或原值皆可
                    gemini_prompt="", # v9.0 政策：SkillInfo 不再持有 Prompt，清空它
                    consecutive_correct_required=int(row.get('consecutive_correct_required', 10) or 10),
                    is_active=bool(row.get('is_active', True)),
                    order_index=int(row.get('order_index', 999) or 999)
                )
                db.session.add(skill)
                count_skills += 1
                
                # A-2. [關鍵] 搬移舊 Prompt 到新表格
                old_prompt = row.get('gemini_prompt')
                if old_prompt and len(str(old_prompt)) > 10:
                    new_prompt_entry = SkillGenCodePrompt(
                        skill_id=skill_id,
                        model_tag='default', # 預設標籤
                        prompt_strategy='Legacy_v8', # 標記這是舊版搬過來的
                        system_prompt="You are a Senior Python Engineer...", # 給個預設值
                        user_prompt_template=old_prompt, # 這裡塞入原本的 prompt
                        creation_prompt_tokens=0,     # 舊資料無法考據，設為 0
                        creation_completion_tokens=0,
                        creation_total_tokens=0,
                        version=1,
                        is_active=True
                    )
                    db.session.add(new_prompt_entry)
                    count_prompts += 1
            
            print(f"   - SkillInfo: {count_skills} 筆")
            print(f"   - SkillGenCodePrompt: {count_prompts} 筆 (已完成搬家)")

        # --- B. 遷移 ExperimentLog ---
        if 'ExperimentLog' in xls.sheet_names:
            print("📊 正在遷移 ExperimentLog (補零新欄位)...")
            df_logs = pd.read_excel(xls, 'ExperimentLog')
            df_logs = df_logs.where(pd.notnull(df_logs), None)
            
            count_logs = 0
            for _, row in df_logs.iterrows():
                log = ExperimentLog(
                    timestamp=row.get('timestamp') if row.get('timestamp') else datetime.utcnow(),
                    skill_id=row.get('skill_id'),
                    ai_provider=row.get('ai_provider'),
                    model_name=row.get('model_name'),
                    duration_seconds=row.get('duration_seconds'),
                    input_length=row.get('input_length'),
                    output_length=row.get('output_length'),
                    is_success=bool(row.get('is_success')),
                    syntax_error_initial=row.get('syntax_error_initial'),
                    ast_repair_triggered=bool(row.get('ast_repair_triggered')),
                    
                    # 新欄位全部補預設值
                    experiment_batch='Legacy_Data_v8',
                    prompt_strategy='Unknown',
                    regex_fix_count=0,
                    logic_fix_count=0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    code_complexity=0
                )
                db.session.add(log)
                count_logs += 1
            print(f"   - ExperimentLog: {count_logs} 筆")

        # --- C. 遷移 TextbookExample ---
        if 'TextbookExample' in xls.sheet_names:
            print("📖 正在遷移 TextbookExample...")
            df_ex = pd.read_excel(xls, 'TextbookExample')
            df_ex = df_ex.where(pd.notnull(df_ex), None)
            
            count_ex = 0
            for _, row in df_ex.iterrows():
                ex = TextbookExample(
                    skill_id=row.get('skill_id'),
                    problem_text=row.get('problem_text'),
                    correct_answer=row.get('correct_answer'),
                    source_curriculum=row.get('source_curriculum', 'general'),
                    source_volume=row.get('source_volume', 'unknown'),
                    source_chapter=row.get('source_chapter', 'unknown'),
                    source_section=row.get('source_section', 'unknown'),
                    source_description=row.get('source_description', ''),
                    difficulty_level=int(row.get('difficulty_level', 1) or 1)
                )
                db.session.add(ex)
                count_ex += 1
            print(f"   - TextbookExample: {count_ex} 筆")

        # 3. 提交變更
        try:
            db.session.commit()
            print("\n🎉 v9.0 資料庫升級與遷移大成功！")
            print("請重新啟動 Flask 伺服器，現在系統已具備完整科展數據追蹤能力。")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 資料庫寫入失敗: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 這裡請填入您剛剛匯出的 Excel 檔名
    backup_filename = "kumon_math_20260110_1810.xlsx" 
    
    if len(sys.argv) > 1:
        backup_filename = sys.argv[1]

    print(f"準備從 {backup_filename} 還原並升級資料庫...")
    confirm = input("⚠️  確定要執行嗎？這將建立新的資料庫內容 (y/n): ")
    if confirm.lower() == 'y':
        migrate_from_excel(backup_filename)
    else:
        print("已取消。")