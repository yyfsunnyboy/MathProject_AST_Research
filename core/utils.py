# core/utils.py （新建檔案）
import sqlite3

def get_skill_info(skill_id):
    """從 skills_info 表讀取單一技能資訊"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, skill_en_name, skill_ch_name, description, 
               gemini_prompt, consecutive_correct_required, is_active, order_index
        FROM skills_info 
        WHERE skill_id = ? AND is_active = 1
    ''', (skill_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'skill_id': row[0],
        'skill_en_name': row[1],
        'skill_ch_name': row[2],
        'description': row[3],
        'gemini_prompt': row[4],
        'consecutive_correct_required': row[5],
        'is_active': row[6] == 1,
        'order_index': row[7]
    }

def get_all_active_skills():
    """讀取所有啟用技能，用於 dashboard"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, skill_en_name, skill_ch_name, description, 
               consecutive_correct_required, order_index
        FROM skills_info 
        WHERE is_active = 1 
        ORDER BY order_index
    ''')
    rows = c.fetchall()
    conn.close()
    
    return [{
        'skill_id': r[0],
        'skill_en_name': r[1],
        'skill_ch_name': r[2],
        'description': r[3],
        'consecutive_correct_required': r[4],
        'order_index': r[5]
    } for r in rows]

def get_curriculums():
    """取得所有課綱 (例如: 'general', 'vocational')"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT DISTINCT curriculum FROM skill_curriculum
    ''')
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_volumes_by_curriculum(curriculum):
    """根據課綱取得所有冊別，並按年級分組"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT DISTINCT grade, volume FROM skill_curriculum
        WHERE curriculum = ?
        ORDER BY grade, display_order
    ''', (curriculum,))
    rows = c.fetchall()
    conn.close()
    
    grouped_volumes = {}
    for grade, volume in rows:
        if grade not in grouped_volumes:
            grouped_volumes[grade] = []
        if volume not in grouped_volumes[grade]:
            grouped_volumes[grade].append(volume)
    return grouped_volumes

def get_chapters_by_curriculum_volume(curriculum, volume):
    """根據課綱和冊別取得所有章節"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT DISTINCT chapter
        FROM skill_curriculum
        WHERE curriculum = ? AND volume = ?
        ORDER BY display_order
    ''', (curriculum, volume))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_skills_by_volume_chapter(volume, chapter):
    """取得指定冊、章的所有技能（包含進度）"""
    conn = sqlite3.connect('math_master.db')
    c = conn.cursor()
    c.execute('''
        SELECT sc.curriculum, sc.grade, sc.volume, sc.chapter, sc.section, sc.paragraph, 
               sc.skill_id, sc.display_order,
               si.skill_ch_name, si.skill_en_name, si.description, 
               si.consecutive_correct_required
        FROM skill_curriculum sc
        JOIN skills_info si ON sc.skill_id = si.skill_id
        WHERE sc.volume = ? AND sc.chapter = ? AND si.is_active = 1
        ORDER BY sc.display_order
    ''', (volume, chapter))
    rows = c.fetchall()
    conn.close()
    
    return [{
        'curriculum': r[0],
        'grade': r[1],
        'volume': r[2],
        'chapter': r[3],
        'section': r[4],
        'paragraph': r[5],
        'skill_id': r[6],
        'display_order': r[7],
        'skill_ch_name': r[8],
        'skill_en_name': r[9],
        'description': r[10],
        'consecutive_correct_required': r[11]
    } for r in rows]