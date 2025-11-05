import pandas as pd
import sqlite3
import os
from models import init_db # 導入 init_db 函式

DB_NAME = "math_master.db"
SKILLS_INFO_CSV = "document/skills_info.csv"
SKILL_CURRICULUM_CSV = "document/skill_curriculum.csv"

def setup_database():
    """初始化資料庫，確保所有表格都存在。"""
    init_db()

def import_data_to_db(skills_csv, curriculum_csv, db_name):
    if not os.path.exists(skills_csv):
        print(f"錯誤：找不到 CSV 檔案 '{skills_csv}'")
        return
    if not os.path.exists(curriculum_csv):
        print(f"錯誤：找不到 CSV 檔案 '{curriculum_csv}'")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # --- 調整清空順序 ---
        # 1. 先清空子表 (skill_curriculum)，避免級聯刪除問題
        print("...清空舊的 skill_curriculum 資料...")
        cursor.execute('DELETE FROM skill_curriculum')
        # 2. 再清空主表 (skills_info)
        print("...清空舊的 skills_info 資料...")
        cursor.execute('DELETE FROM skills_info')

        # --- 匯入 skills_info 資料 ---
        print("正在匯入 skills_info 資料...")
        df_skills = pd.read_csv(skills_csv)
        num_skills = len(df_skills)

        # 標準化欄位名稱：將所有欄位名稱轉為小寫
        df_skills.columns = [str(col).lower().strip() for col in df_skills.columns]
        
        # 處理 is_active 欄位，將 'true'/'false' 轉換為 1/0
        df_skills['is_active'] = df_skills['is_active'].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

        for index, row in df_skills.iterrows():
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO skills_info (
                        skill_id, skill_en_name, skill_ch_name, category, description, input_type,
                        gemini_prompt, consecutive_correct_required, is_active, order_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['skill_id']).strip(), # 強制轉為字串並移除前後空格
                    row['skill_en_name'],
                    row['skill_ch_name'],
                    row.get('category', '未分類'), # 新增 category 欄位
                    row['description'],
                    row.get('input_type', 'text'), # 新增 input_type 欄位
                    row['gemini_prompt'],
                    int(row['consecutive_correct_required']),
                    row['is_active'],
                    int(row['order_index'])
                ))
            except Exception as e:
                print(f"匯入 skills_info 失敗 (skill_id: {row['skill_id']}): {e}")
        print(f"skills_info 資料匯入完成，共處理 {num_skills} 筆。")

        # --- 匯入 skill_curriculum 資料 ---
        print("正在匯入 skill_curriculum 資料...")
        df_curriculum = pd.read_csv(curriculum_csv)
        num_curriculum = len(df_curriculum)

        # --- 關鍵修正：將所有欄位名稱轉為小寫，以避免大小寫問題 ---
        df_curriculum.columns = [str(col).lower().strip() for col in df_curriculum.columns]


        for index, row in df_curriculum.iterrows():
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO skill_curriculum (
                        curriculum, grade, volume, chapter, section, paragraph, 
                        skill_id, display_order, difficulty_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['curriculum']).strip(),
                    int(row['grade']),
                    str(row['volume']).strip(),
                    str(row['chapter']).strip(),
                    str(row['section']).strip(),
                    str(row.get('paragraph', '') or '').strip() or None, # 處理空值和 None
                    str(row['skill_id']).strip(), # 強制轉為字串並移除前後空格
                    int(row['display_order']),
                    int(row.get('difficulty_level', 1)) # 新增：讀取難易度，若無則預設為 1
                ))
            except KeyError as e:
                print(f"匯入 skill_curriculum 失敗：欄位缺失 {e}。錯誤行資料：\n{row}\n")
        print(f"skill_curriculum 資料匯入完成，共處理 {num_curriculum} 筆。")

        conn.commit() # 在所有操作成功後，一次性提交

    except Exception as e:
        print(f"匯入過程中發生錯誤: {e}")
    finally:
        if conn:
            conn.close()
            print("資料庫連接已關閉。")

if __name__ == "__main__":
    print("正在初始化資料庫結構...")
    setup_database() # 匯入前先確保資料庫和表格都已建立
    print(f"開始從 CSV 檔案匯入資料到 '{DB_NAME}'...")
    import_data_to_db(SKILLS_INFO_CSV, SKILL_CURRICULUM_CSV, DB_NAME)
    print("資料匯入腳本執行完畢。")
