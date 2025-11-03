import pandas as pd
import sqlite3
import os

DB_NAME = "users.db"
EXCEL_FILE = "document/數B第一冊單元分類.xlsx"

def import_excel_to_db(excel_file, db_name):
    if not os.path.exists(excel_file):
        print(f"錯誤：找不到 Excel 檔案 '{excel_file}'")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # --- 匯入 skills_info 資料 ---
        print("正在匯入 skills_info 資料...")
        df_skills = pd.read_excel(excel_file, sheet_name='skills_info')
        
        # 處理 is_active 欄位，將 'true'/'false' 轉換為 1/0
        df_skills['is_active'] = df_skills['is_active'].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

        for index, row in df_skills.iterrows():
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO skills_info (
                        skill_id, skill_en_name, skill_ch_name, description, 
                        gemini_prompt, consecutive_correct_required, is_active, order_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['skill_id'],
                    row['skill_en_name'],
                    row['skill_ch_name'],
                    row['description'],
                    row['gemini_prompt'],
                    int(row['consecutive_correct_required']),
                    row['is_active'],
                    int(row['order_index'])
                ))
            except Exception as e:
                print(f"匯入 skills_info 失敗 (skill_id: {row['skill_id']}): {e}")
        conn.commit()
        print("skills_info 資料匯入完成。")

        # --- 匯入 skill_curriculum 資料 ---
        print("正在匯入 skill_curriculum 資料...")
        df_curriculum = pd.read_excel(excel_file, sheet_name='skill_curriculum')

        for index, row in df_curriculum.iterrows():
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO skill_curriculum (
                        volume, chapter, section, paragraph, skill_id, display_order
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    int(row['volume']),
                    int(row['chapter']),
                    int(row['section']),
                    int(row['paragraph']),
                    row['skill_id'],
                    int(row['display_order'])
                ))
            except Exception as e:
                print(f"匯入 skill_curriculum 失敗 (volume: {row['volume']}, chapter: {row['chapter']}, skill_id: {row['skill_id']}): {e}")
        conn.commit()
        print("skill_curriculum 資料匯入完成。")

    except Exception as e:
        print(f"匯入過程中發生錯誤: {e}")
    finally:
        if conn:
            conn.close()
            print("資料庫連接已關閉。")

if __name__ == "__main__":
    print(f"開始從 '{EXCEL_FILE}' 匯入資料到 '{DB_NAME}'...")
    import_excel_to_db(EXCEL_FILE, DB_NAME)
    print("資料匯入腳本執行完畢。")
