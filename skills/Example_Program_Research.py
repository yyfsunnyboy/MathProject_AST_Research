# -*- coding: utf-8 -*-
"""
=============================================================================
ID: skills/Example_Program_Research.py
Description: 
    科研專用標準樣板 (V2.1 - Single Logic Edition)
    專供 14B 模型進行 RAG 模仿實驗，支援自動語法修復與 AST 結構補強。
=============================================================================
"""
import random
import math
from fractions import Fraction

def generate(level=1, **kwargs):
    """
    [Research Target] 
    Coder 應根據 MASTER_SPEC 在下方 [RAG_LOGIC] 區塊實作。
    """
    # 預設變數初始化 (防止 UnboundLocalError)
    q = "題目生成中..."
    a = "N/A"
    
    # ========================== [RAG_LOGIC_START] ==========================
    # 指導：請在此處根據課本例題的數學結構，實作數值隨機化與題目字串生成。
    # 提醒：請務必使用 fmt_num() 處理所有 LaTeX 輸出的數值。
    
    
    # [請在此處填入邏輯，例如：]
    # n1 = random.randint(-100, 100)
    # q = f"計算 ${fmt_num(n1)} + 5$ 的值"
    # a = str(n1 + 5)
    
    
    # =========================== [RAG_LOGIC_END] ===========================

    return {
        'question_text': q, 
        'correct_answer': a, 
        'answer': a,
        'mode': 1
    }

def check(user_answer, correct_answer):
    """
    標準評分邏輯 (由 code_generator 自動注入強力版本)
    """
    u = str(user_answer).strip()
    c = str(correct_answer).strip()
    return {"correct": u == c, "result": "正確" if u == c else "錯誤"}