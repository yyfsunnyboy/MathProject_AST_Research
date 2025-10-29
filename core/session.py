# core/session.py
from flask import session

def set_current(skill, data):
    session['skill'] = skill
    session['answer'] = data.get('correct_answer')
    session['question'] = data.get('question_text')
    session['inequality'] = data.get('inequality_string', '')

def get_current():
    return {
        'skill': session.get('skill'),
        'answer': session.get('answer'),
        'question': session.get('question'),
        'inequality': session.get('inequality', '')
    }

def clear():
    for k in ['skill', 'answer', 'question', 'inequality']:
        session.pop(k, None)