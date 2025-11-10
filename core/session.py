# core/session.py
from flask import session

def set_current(skill, data):
    """
    安全儲存當前題目資料，支援圖形題（answer=None）
    """
    session['current_skill'] = skill
    session['current_question'] = data["question_text"]
    
    # 安全取值：圖形題沒有 answer，用 None
    session['current_answer'] = data.get("answer")

    # 新增：儲存前置技能資訊
    session['current_prereq_skills'] = data.get('prereq_skills', [])
    
    # 安全取 inequality_string
    session['current_inequality'] = data.get("inequality_string", "")
    
    # 額外儲存 correct_answer（供 check_answer 判斷題型）
    session['current_correct_answer'] = data.get("correct_answer", "text")

def get_current():
    """
    安全取得當前題目資料
    """
    return {
        "skill": session.get('current_skill'),
        "question": session.get('current_question'),
        "answer": session.get('current_answer'),
        "prereq_skills": session.get('current_prereq_skills', []), # 新增：讀取前置技能
        "inequality": session.get('current_inequality'),
        "correct_answer": session.get('current_correct_answer', "text")
    }

def clear():
    """
    清除所有 current 資料
    """
    keys = ['current_skill', 'current_question', 'current_answer', 'current_prereq_skills',
            'current_inequality', 'current_correct_answer']
    for k in keys:
        session.pop(k, None)