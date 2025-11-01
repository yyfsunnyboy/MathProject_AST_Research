# core/utils.py （新建檔案）
import sqlite3

def get_skill_info(skill_id):
    """從 skills_info 表讀取單一技能資訊"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, skill_en_name, skill_ch_name, description, 
               gemini_prompt, consecutive_correct_required, is_active, order_index
        FROM skills_info 
        WHERE skill_id = ? AND is_active = TRUE
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
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT skill_id, skill_en_name, skill_ch_name, description, 
               consecutive_correct_required, order_index
        FROM skills_info 
        WHERE is_active = TRUE 
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