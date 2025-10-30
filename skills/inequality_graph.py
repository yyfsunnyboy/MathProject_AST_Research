# skills/inequality_graph.py
import random

def generate():
    a1, b1, c1 = random.randint(1, 3), random.randint(1, 3), random.randint(1, 5)
    a2, b2, c2 = random.randint(1, 3), random.randint(1, 3), random.randint(1, 5)
    return {
        "question_text": f"畫出可行域：\n{a1}x + {b1}y ≤ {c1}\n{a2}x + {b2}y ≥ {c2}",
        "inequality_string": f"{a1},{b1},{c1},{a2},{b2},{c2}",
        "correct_answer": "graph"  # 標記為圖形題
    }

def check(user, correct):
    # 圖形題不走文字批改，由前端觸發 AI 分析
    return {
        "correct": False,
        "result": "請使用畫筆繪製可行域，然後點選「AI檢查」",
        "next_question": False
    }