# \積分\面積 (上和/下和)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「面積 (上和/下和)」的觀念題。
    """
    if level == 1:
        question_text = (
            "對於一個遞增函數 f(x)，在區間 [a, b] 上使用 n 個子區間計算黎曼和時，使用「右端點」會得到什麼？\n\n"
            "A) 上和 (Upper Sum)\nB) 下和 (Lower Sum)\nC) 正確面積"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "當我們將區間 [a, b] 的分割數 n 趨近於無限大時，上和與下和會發生什麼事？\n\n" \
                        "A) 都趨近於無限大\nB) 都趨近於 0\nC) 都會收斂到同一個值（定積分）"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')