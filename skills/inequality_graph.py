# skills/inequality_graph.py
import random

def generate():
    a1, b1, c1 = random.randint(1,3), random.randint(1,3), random.randint(1,5)
    a2, b2, c2 = random.randint(1,3), random.randint(1,3), random.randint(1,5)
    return {
        "question_text": f"畫出可行域：\n{a1}x + {b1}y ≤ {c1}\n{a2}x + {b2}y ≥ {c2}",
        "inequality_string": f"{a1},{b1},{c1},{a2},{b2},{c2}",
        "correct_answer": "graph"
    }

def check(user, correct):
    return {"correct": False, "result": "請用畫筆繪圖", "next_question": False}