# core/data_importer.py
"""
Data importer module for batch importing data from Excel/CSV files
"""
import pandas as pd
from models import db, SkillCurriculum, SkillInfo, TextbookExample


def import_textbook_examples_from_file(file_path):
    """
    從 Excel 檔案匯入課本例題到 TextbookExample 資料表
    """
    try:
        # 讀取 Excel
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 標準化欄位名稱 (轉小寫)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        count = 0
        for _, row in df.iterrows():
            # 必填欄位檢查
            if 'skill_id' not in row or pd.isna(row['skill_id']):
                continue
            
            # 準備寫入資料
            example = TextbookExample(
                skill_id=str(row['skill_id']).strip(),
                source_curriculum=row.get('curriculum', ''),
                source_volume=row.get('volume', ''),
                source_chapter=row.get('chapter', ''),
                source_section=row.get('section', ''),
                source_description=row.get('description', ''),
                source_paragraph=row.get('paragraph', '') if 'paragraph' in row and not pd.isna(row['paragraph']) else None,
                problem_text=row.get('problem_text', ''),
                problem_type=row.get('problem_type', 'calculation'),
                correct_answer=str(row.get('correct_answer', '')),
                detailed_solution=row.get('detailed_solution', ''),
                difficulty_level=int(row.get('difficulty', 1)) if 'difficulty' in row and not pd.isna(row['difficulty']) else 1
            )
            
            db.session.add(example)
            count += 1
            
        db.session.commit()
        return count
        
    except Exception as e:
        db.session.rollback()
        print(f"Import Textbook Examples Error: {e}")
        raise e


def import_curriculum_from_json():
    """
    從 JSON 匯入課程綱要 (Placeholder for existing route)
    TODO: Implement this function based on your data source
    """
    # This is a placeholder function referenced by batch_import_curriculum route
    # You'll need to implement this based on your actual data source
    raise NotImplementedError("import_curriculum_from_json needs to be implemented")


def import_skills_from_json():
    """
    從 JSON 匯入技能資訊 (Placeholder for existing route)
    TODO: Implement this function based on your data source
    """
    # This is a placeholder function referenced by batch_import_skills route
    # You'll need to implement this based on your actual data source
    raise NotImplementedError("import_skills_from_json needs to be implemented")
