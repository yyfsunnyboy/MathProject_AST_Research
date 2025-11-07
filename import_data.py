import pandas as pd
import os
from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, init_db, SkillInfo, SkillCurriculum

SKILLS_INFO_CSV = "document/skills_info.csv"
SKILL_CURRICULUM_CSV = "document/skill_curriculum.csv"

def setup_database():
    """使用與主應用程式相同的方式初始化資料庫，確保所有表格都存在。"""
    # 建立一個臨時的 Flask app 來提供資料庫操作的上下文
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
    
    # 在 app 上下文內執行資料庫初始化
    with app.app_context():
        init_db(db.engine)
    return app # 回傳 app 以便後續使用其上下文

def import_data_to_db(skills_csv, curriculum_csv):
    if not os.path.exists(skills_csv):
        print(f"錯誤：找不到 CSV 檔案 '{skills_csv}'")
        return
    if not os.path.exists(curriculum_csv):
        print(f"錯誤：找不到 CSV 檔案 '{curriculum_csv}'")
        return

    try:
        # --- 使用 ORM 清空資料 ---
        # 1. 先清空子表 (SkillCurriculum)，因為它有指向 SkillInfo 的外鍵
        print("...清空舊的 skill_curriculum 資料...")
        db.session.query(SkillCurriculum).delete()
        
        # 2. 再清空主表 (SkillInfo)
        print("...清空舊的 skills_info 資料...")
        db.session.query(SkillInfo).delete()
        
        # 提交清空操作
        db.session.commit()

        # --- 匯入 skills_info 資料 ---
        print("正在匯入 skills_info 資料...")
        df_skills = pd.read_csv(skills_csv)
        df_skills.columns = [str(col).lower().strip() for col in df_skills.columns]
        df_skills['is_active'] = df_skills['is_active'].apply(lambda x: str(x).lower() == 'true')
        
        # 將 DataFrame 轉換為字典列表，以便進行批次插入
        skills_records = df_skills.to_dict(orient='records')
        
        # 使用 ORM 進行批次插入
        db.session.bulk_insert_mappings(SkillInfo, skills_records)
        print(f"skills_info 資料匯入完成，共處理 {len(skills_records)} 筆。")

        # --- 匯入 skill_curriculum 資料 ---
        print("正在匯入 skill_curriculum 資料...")
        df_curriculum = pd.read_csv(curriculum_csv)
        df_curriculum.columns = [str(col).lower().strip() for col in df_curriculum.columns]
        
        # 處理欄位名稱不一致的問題 (diffcult_level -> difficulty_level)
        if 'diffcult_level' in df_curriculum.columns:
            df_curriculum.rename(columns={'diffcult_level': 'difficulty_level'}, inplace=True)
        
        # 處理空值
        df_curriculum['paragraph'] = df_curriculum['paragraph'].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None)
        
        curriculum_records = df_curriculum.to_dict(orient='records')
        
        # 使用 ORM 進行批次插入
        db.session.bulk_insert_mappings(SkillCurriculum, curriculum_records)
        print(f"skill_curriculum 資料匯入完成，共處理 {len(curriculum_records)} 筆。")
        
        # 在所有操作成功後，一次性提交
        db.session.commit()

    except Exception as e:
        db.session.rollback() # 如果發生錯誤，回滾所有操作
        print(f"匯入過程中發生錯誤: {e}")

if __name__ == "__main__":
    print("正在初始化資料庫結構...")
    app = setup_database() # 建立 app 並初始化資料庫結構
    
    # 在 app 上下文內執行資料匯入
    with app.app_context():
        print(f"開始從 CSV 檔案匯入資料到資料庫 (路徑: {SQLALCHEMY_DATABASE_URI})...")
        import_data_to_db(SKILLS_INFO_CSV, SKILL_CURRICULUM_CSV)
        print("資料匯入腳本執行完畢。")
