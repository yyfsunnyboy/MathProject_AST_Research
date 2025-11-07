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
    chapters.sort(key=extract_chapter_number)
    
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