import pandas as pd
import os
from sqlalchemy import text
from models import (
    db, User, Class, ClassStudent, SkillInfo, 
    SkillPrerequisites, TextbookExample, Progress, 
    MistakeLog, ExamAnalysis, SystemSetting, ExperimentLog,
    LearningDiagnosis, MistakeNotebookEntry, SkillCurriculum,
    Question, QuizAttempt  # <--- 新增這兩個
)

# 建立 Sheet 名稱到 Model 的對照表 (Map Sheet Name -> DB Model)
# 這樣就算 Excel Sheet 名稱跟 Table 名稱不完全一樣也能對應
# 如果你的 Sheet 名稱已經跟 Table 名稱一樣 (例如 Sheet 'users' -> Table 'users')，這個表可以用來過濾
def get_model_mapping():
    return {
        'users': User,
        'classes': Class,
        'class_students': ClassStudent,
        'skills_info': SkillInfo,
        'skill_prerequisites': SkillPrerequisites,
        'textbook_examples': TextbookExample,
        'progress': Progress,
        'mistake_logs': MistakeLog,
        'exam_analysis': ExamAnalysis,
        'system_settings': SystemSetting,
        'experiment_logs': ExperimentLog,
        'experiment_log': ExperimentLog,
        'learning_diagnosis': LearningDiagnosis,
        'mistake_notebook_entries': MistakeNotebookEntry,
        'skill_curriculum': SkillCurriculum,
        
        # 👇 新增這兩行，讓匯入程式認得它們
        'questions': Question,
        'quiz_attempts': QuizAttempt
    }

def import_excel_to_db(filepath):
    """
    讀取 Excel 檔案，將每個 Sheet 的資料匯入對應的資料庫 Table
    """
    if not os.path.exists(filepath):
        return False, "❌ 檔案不存在"

    try:
        # 1. 讀取 Excel 檔案 (取得所有 Sheet 的資料)
        # sheet_name=None 代表讀取所有 Sheets，回傳一個 Dict
        xls = pd.read_excel(filepath, sheet_name=None, engine='openpyxl')
        
        mapping = get_model_mapping()
        results = []
        
        # 2. 遍歷每一個 Sheet
        for sheet_name, df in xls.items():
            # 去除 Sheet 名稱前後空白
            sheet_name_clean = sheet_name.strip()
            
            # 檢查這個 Sheet 是否有對應的資料庫模型
            if sheet_name_clean not in mapping:
                results.append(f"⚠️ 跳過 Sheet '{sheet_name}': 資料庫中無此 Table 或未設定對應。")
                continue
                
            model = mapping[sheet_name_clean]
            table_name = model.__tablename__
            
            # 3. 資料處理 (Data Cleaning)
            # 將 pandas 的 NaN (空值) 轉為 Python 的 None，否則寫入 DB 會報錯
            df = df.where(pd.notnull(df), None)
            
            # 取得該 Model 的所有欄位名稱
            model_columns = model.__table__.columns.keys()
            excel_columns = df.columns.tolist()
            
            # [除錯建議] 檢查欄位是否匹配
            common_columns = set(model_columns) & set(excel_columns)
            if not common_columns:
                results.append(f"❌ Sheet '{sheet_name}' 欄位名稱與 Table '{table_name}' 完全不符！\n   Excel: {excel_columns}\n   DB: {model_columns}")
                continue
            
            imported_count = 0
            
            # 4. 逐列寫入資料庫
            for index, row in df.iterrows():
                try:
                    data = {}
                    # 只讀取 Model 裡有的欄位，忽略 Excel 裡多餘的欄位
                    for col in model_columns:
                        if col in row:
                            val = row[col]
                            # 特殊處理：布林值轉換
                            if isinstance(val, str):
                                if val.lower() == 'true': val = True
                                elif val.lower() == 'false': val = False
                            data[col] = val
                    
                    if not data:
                        continue

                    # 使用 merge (UPSERT): 有 ID 就更新，沒 ID 就新增
                    instance = model(**data)
                    db.session.merge(instance)
                    imported_count += 1
                    
                except Exception as e:
                    print(f"❌ Error inserting row {index} in {sheet_name}: {e}")
                    continue
            
            results.append(f"✅ Sheet '{sheet_name}' -> Table '{table_name}': 成功匯入 {imported_count} 筆。")

        # 5. 提交變更
        db.session.commit()
        return True, "\n".join(results)

    except Exception as e:
        db.session.rollback()
        return False, f"❌ 匯入失敗: {str(e)}"
