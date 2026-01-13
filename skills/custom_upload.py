# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): skills/custom_upload.py
功能說明 (Description): 自定義上傳題目的處理模組。
    本模組作為前端圖片上傳與 AI 解析的佔位介面，回傳預設的空模板，
    確保系統在處理 "Custom Upload" 類型題目時有一致的介面。
執行語法 (Usage): 由系統自動調用 (core/code_generator.py 或 routes)
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# skills/custom_upload.py
import random

def generate(level=1):
    """
    此函數主要用於保持介面一致性。
    Custom Upload 的題目通常是從前端上傳圖片後，由 AI 解析並直接注入 session。
    因此這裡只回傳一個預設的空模板或提示。
    """
    return {
        "question_text": "請上傳題目圖片以開始練習。",
        "answer": "",
        "answer_type": "text"
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    採用更寬鬆的檢測方式：
    1. 去除空白、括號、LaTeX 符號後比對字串。
    2. 嘗試數值比對。
    """
    if not user_answer or not correct_answer:
        return {"correct": False, "result": "無法驗證答案 (缺少題目或作答)"}

    # 輔助函式：標準化字串 (去除干擾字元)
    def normalize(s):
        return str(s).strip().lower()\
            .replace(" ", "")\
            .replace("(", "").replace(")", "")\
            .replace("[", "").replace("]", "")\
            .replace("{", "").replace("}", "")\
            .replace("$", "").replace("\\", "")

    u_norm = normalize(user_answer)
    c_norm = normalize(correct_answer)

    # 1. 直接字串比對 (標準化後)
    if u_norm == c_norm:
        return {"correct": True, "result": "答對了！"}

    # 2. 嘗試數值比對 (針對單一數值)
    try:
        u_val = float(u_norm)
        c_val = float(c_norm)
        if abs(u_val - c_val) < 1e-6:
             return {"correct": True, "result": "答對了！"}
    except ValueError:
        pass
        
    # 3. 嘗試以逗號分隔的數值/字串比對 (處理座標或多重答案)
    if ',' in u_norm and ',' in c_norm:
        u_parts = u_norm.split(',')
        c_parts = c_norm.split(',')
        if len(u_parts) == len(c_parts):
            all_match = True
            for u, c in zip(u_parts, c_parts):
                # 每個部分都嘗試數值或字串比對
                try:
                    if abs(float(u) - float(c)) > 1e-6:
                        all_match = False
                        break
                except ValueError:
                    if u != c:
                        all_match = False
                        break
            if all_match:
                return {"correct": True, "result": "答對了！"}

    return {"correct": False, "result": f"答錯了。正確答案應為：{correct_answer}"}
