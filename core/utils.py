"""此模組提供與資料庫互動的通用工具函式，包含查詢技能資訊、課綱結構（年級、冊別、章節）以及管理技能與課綱關聯的 CRUD 操作。"""

# core/utils.py （新建檔案）
from sqlalchemy import func
import re
from models import db, SkillInfo, SkillCurriculum

def get_skill_info(skill_id):
    """從 skills_info 表讀取單一技能資訊"""
    # 使用 ORM 查詢
    skill = SkillInfo.query.filter_by(skill_id=skill_id, is_active=True).first()

    if not skill:
        return None
    
    return {
        'skill_id': skill.skill_id,
        'skill_en_name': skill.skill_en_name,
        'skill_ch_name': skill.skill_ch_name,
        'category': skill.category,
        'description': skill.description,
        'input_type': skill.input_type,
        'gemini_prompt': skill.gemini_prompt,
        'consecutive_correct_required': skill.consecutive_correct_required,
        'is_active': skill.is_active,
        'order_index': skill.order_index
    }

def get_all_active_skills():
    """讀取所有啟用技能，用於 dashboard"""
    # 使用 ORM 查詢
    skills = SkillInfo.query.filter_by(is_active=True).order_by(SkillInfo.order_index).all()
    
    return [{
        'skill_id': s.skill_id,
        'skill_en_name': s.skill_en_name,
        'skill_ch_name': s.skill_ch_name,
        'category': s.category,
        'description': s.description,
        'input_type': s.input_type,
        'consecutive_correct_required': s.consecutive_correct_required,
        'order_index': s.order_index
    } for s in skills]

def get_curriculums():
    """取得所有課綱 (例如: 'general', 'vocational')"""
    # 使用 ORM 查詢，.distinct() 確保唯一性，.all() 取得所有結果
    results = db.session.query(SkillCurriculum.curriculum).distinct().all()
    return [r[0] for r in results]

def get_volumes_by_curriculum(curriculum):
    """根據課綱取得所有冊別，並按年級分組"""
    # 使用 ORM 查詢
    rows = db.session.query(SkillCurriculum.grade, SkillCurriculum.volume)\
                     .filter_by(curriculum=curriculum)\
                     .distinct()\
                     .order_by(SkillCurriculum.grade, SkillCurriculum.display_order)\
                     .all()
    
    grouped_volumes = {}
    for grade, volume in rows:
        if grade not in grouped_volumes:
            grouped_volumes[grade] = []
        if volume not in grouped_volumes[grade]:
            grouped_volumes[grade].append(volume)
    return grouped_volumes

def get_chapters_by_curriculum_volume(curriculum, volume):
    """根據課綱和冊別取得所有章節"""
    # 使用 ORM 查詢
    results = db.session.query(SkillCurriculum.chapter)\
                        .filter_by(curriculum=curriculum, volume=volume)\
                        .distinct()\
                        .all()
    
    chapters = [r[0] for r in results]

    # 定義一個函式來從章節名稱中提取數字
    def extract_chapter_number(chapter_name):
        # 使用正規表示式尋找 "第" 和 "章" 之間的數字
        match = re.search(r'第(\d+)', chapter_name)
        if match:
            return int(match.group(1))
        return float('inf') # 如果找不到數字，排在最後

    # 使用自訂的排序鍵進行排序
    # [Fix] Natural Sorting
    def natural_keys(text):
        if not text: return []
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]

    chapters.sort(key=natural_keys)
    
    return chapters

def get_skills_by_volume_chapter(volume, chapter):
    """取得指定冊、章的所有技能（包含進度）"""
    # 使用 ORM 進行 JOIN 查詢
    # .join() 會根據我們在模型中定義的 ForeignKey 自動關聯
    results = db.session.query(SkillCurriculum, SkillInfo)\
                        .join(SkillInfo)\
                        .filter(SkillCurriculum.volume == volume,
                                SkillCurriculum.chapter == chapter,
                                SkillInfo.is_active == True)\
                        .order_by(SkillCurriculum.display_order)\
                        .all()
    
    return [{
        'curriculum': sc.curriculum,
        'grade': sc.grade,
        'volume': sc.volume,
        'chapter': sc.chapter,
        'section': sc.section,
        'paragraph': sc.paragraph,
        'skill_id': sc.skill_id,
        'display_order': sc.display_order,
        'skill_ch_name': si.skill_ch_name,
        'skill_en_name': si.skill_en_name,
        'description': si.description,
        'consecutive_correct_required': si.consecutive_correct_required
    } for sc, si in results]

def get_all_skill_curriculums():
    """
    取得 SkillCurriculum 表中的所有條目，並 JOIN SkillInfo 以獲取技能名稱。
    這是給 /admin/curriculum 管理頁面使用的。
    """
    results = db.session.query(SkillCurriculum, SkillInfo.skill_ch_name, SkillInfo.difficulty)\
                        .outerjoin(SkillInfo, SkillCurriculum.skill_id == SkillInfo.skill_id)\
                        .order_by(SkillCurriculum.curriculum, SkillCurriculum.grade, SkillCurriculum.display_order)\
                        .all()

    return [{
        'id': sc.id,
        'curriculum': sc.curriculum,
        'grade': sc.grade,
        'volume': sc.volume,
        'chapter': sc.chapter,
        'section': sc.section,
        'paragraph': sc.paragraph,
        'skill_id': sc.skill_id,
        'display_order': sc.display_order,
        'skill_ch_name': skill_ch_name,
        'difficulty': difficulty # 移除此行末尾的逗號
    } for sc, skill_ch_name, difficulty in results] # 修正：將 for 迴圈與 return 對齊

def create_skill_curriculum(data):
    """
    新增一筆 SkillCurriculum 記錄。
    'data' 是一個包含所有必要欄位資訊的字典。
    """
    try:
        new_entry = SkillCurriculum(**data)
        db.session.add(new_entry)
        db.session.commit()
        return {'success': True, 'message': '記錄新增成功。', 'id': new_entry.id}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤，但只回傳通用訊息給前端
        print(f"Create Error: {e}")
        return {'success': False, 'message': '新增失敗，請檢查資料格式或聯繫管理員。'}

def update_skill_curriculum(entry_id, data):
    """
    更新一筆指定 id 的 SkillCurriculum 記錄。
    'data' 是一個包含要更新欄位資訊的字典。
    """
    try:
        entry = SkillCurriculum.query.get(entry_id)
        if not entry:
            return {'success': False, 'message': '找不到指定的記錄。'}
        
        for key, value in data.items():
            setattr(entry, key, value)
            
        db.session.commit()
        return {'success': True, 'message': '記錄更新成功。'}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤
        print(f"Update Error: {e}")
        return {'success': False, 'message': '更新失敗，請檢查資料或聯繫管理員。'}

def delete_skill_curriculum(entry_id):
    """
    刪除一筆指定 id 的 SkillCurriculum 記錄。
    """
    try:
        entry = SkillCurriculum.query.get(entry_id)
        if not entry:
            return {'success': False, 'message': '找不到指定的記錄。'}
        
        db.session.delete(entry)
        db.session.commit()
        return {'success': True, 'message': '記錄刪除成功。'}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤
        print(f"Delete Error: {e}")
        return {'success': False, 'message': '刪除失敗，可能有關聯資料，請聯繫管理員。'}

def to_superscript(n):
    """將整數轉換為上標字串。"""
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻"
    }
    return "".join(superscript_map.get(char, char) for char in str(n))