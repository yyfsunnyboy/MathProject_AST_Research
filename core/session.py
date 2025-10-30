# core/session.py
from flask import session

def set_current(skill, data):
    session['current_skill'] = skill
    session['current_question'] = data["question_text"]
    session['current_answer'] = data["answer"]  # 必須儲存 answer！
    session['current_inequality'] = data.get("inequality_string", "")

def get_current():
    return {
        "skill": session.get('current_skill'),
        "question": session.get('current_question'),
        "answer": session.get('current_answer'),
        "inequality": session.get('current_inequality')
    }

def clear():
    for k in ['skill', 'answer', 'question', 'inequality']:
        session.pop(k, None)