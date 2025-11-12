# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json
import tempfile
import os
import re
from flask import current_app

# 初始化 gemini_model 為 None，避免 NameError
gemini_model = None

def configure_gemini(api_key, model_name):
    global gemini_model
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)  # 動態設定！

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def analyze(image_data_url, context, api_key, prerequisite_skills=None):
    """
    強制 Gemini 回傳純 JSON，失敗時自動重試一次
    """
    def _call_gemini():
        # 將前置技能列表轉換為文字描述
        prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prerequisite_skills]) if prerequisite_skills else "無"

        # 解碼 Base64 圖片
        _, b64 = image_data_url.split(',', 1)
        img_data = base64.b64decode(b64)

        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name

        try:
            # 上傳到 Gemini
            file = genai.upload_file(path=temp_path)

            # 強制 JSON 輸出 Prompt
            prompt = f"""你是一位功文數學數學助教，正在批改學生手寫的計算紙。請你扮演一個非常有耐心、擅長鼓勵的數學家教老師。我的學生對數學比較沒信心
題目：{context}
此單元的前置基礎技能有：{prereq_text}

請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字、格式條列清楚。
如果學生計算錯誤或觀念不熟，你可以根據提供的前置技能列表，建議他回到哪個基礎技能練習。

{{
  "reply": "用 Markdown 格式寫出具體建議（步驟對錯、遺漏、改進點）。如果計算過程完全正確，reply 內容應為「答對了，計算過程很正確！」。",
  "is_process_correct": true 或 false,
  "correct": true 或 false,
  "next_question": true 或 false
}}

直接輸出 JSON 內容，不要包在 ```json 標記內。"""

            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content([prompt, file])
            raw_text = resp.text.strip()

            # 清理可能的 ```json 標記
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
            return json.loads(cleaned)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # 最多嘗試 2 次
    for attempt in range(2):
        try:
            return _call_gemini()
        except json.JSONDecodeError as e:
            if attempt == 1:
                return {
                    "reply": f"AI 回應格式錯誤（第 {attempt+1} 次）：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)  # 重試前延遲
        except Exception as e:
            if attempt == 1:
                return {
                    "reply": f"AI 分析失敗：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False
                }
            import time; time.sleep(1)

    return {
        "reply": "AI 分析失敗，請稍後再試",
        "is_process_correct": False,
        "correct": False,
        "next_question": False
    }
    
def ask_ai_text(user_question):
    try:
        model = get_model()
        prompt = f"""
        你是功文數學 AI 助教，用繁體中文親切回答。
        要求：
        1. 多項式用這種格式：f(x) = x³ - 8x² + 9x + 5
        2. 不要用 $...$ 或 LaTeX
        3. 例題用「範例：」開頭
        4. 步驟用數字 1. 2. 3.
        5. 結尾加鼓勵話，如「加油～」
        
        學生問題：{user_question}
        """
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI 錯誤：{str(e)}"
    
# core/ai_analyzer.py
def ask_ai_text_with_context(user_question, context=""):
    """
    聊天專用 AI：帶入當前題目 context
    """
    model = get_model()
    
    system_prompt = f"""
    你是功文數學 AI 助教，用繁體中文親切回答。
    
    【當前題目】：
    {context or "（無題目資訊）"}
    
    【學生問題】：
    {user_question}
    
    要求：
    1. 如果有題目，必須參考題目內容
    2. 多項式用 x^3 格式（如 x^3 - 2x^2 + 1）
    3. 例題用「範例：」開頭
    4. 步驟用 1. 2. 3.
    5. 結尾加鼓勵話，如「加油～」
    """
    
    try:
        resp = model.generate_content(system_prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI 內部錯誤：{str(e)}"
    # ...existing code...

from datetime import datetime
from typing import List, Optional, Dict

def _build_analysis_prompt(answer_steps: List[str], student_answer: str, correct_answer: Optional[str]=None, skill_prompt: Optional[str]=None) -> str:
    """
    建構傳給 AI 的 prompt，要求回傳 JSON 格式：
    {"error_category": "...", "error_explanation": "...", "guidance": "..."}
    """
    prompt_lines = [
        "你是數學助教。請根據學生的作答過程判斷錯誤並生成簡短回饋（繁體中文）。",
        "輸出必須是 JSON，包含三個欄位：error_category, error_explanation, guidance。",
        "error_category: 一個簡短分類（例如: 計算錯誤、概念誤解、公式套用錯誤、粗心）。",
        "error_explanation: 一句話說明學生錯在哪裡（最多 30 字）。",
        "guidance: 一至兩句簡短指導，告訴學生下一步怎麼改進（最多 50 字）。",
        ""
    ]
    if skill_prompt:
        prompt_lines.append(f"技能提示: {skill_prompt}")
    if correct_answer:
        prompt_lines.append(f"正確答案或目標: {correct_answer}")
    prompt_lines.append("學生作答過程（步驟）：")
    for i, step in enumerate(answer_steps, start=1):
        prompt_lines.append(f"{i}. {step}")
    prompt_lines.append("")
    prompt_lines.append("學生最終作答：")
    prompt_lines.append(student_answer or "<無>")
    prompt_lines.append("")
    prompt_lines.append("請只輸出 JSON，並確保 keys 如上。")
    return "\n".join(prompt_lines)

def analyze_student_answer(answer_steps: List[str], student_answer: str, correct_answer: Optional[str]=None, skill_prompt: Optional[str]=None, timeout_sec: int=10) -> Dict:
    """
    以結構化格式回傳 AI 對學生作答的分析：
    回傳 dict 範例：
    {
      "error_category": "計算錯誤",
      "error_explanation": "在第三步乘法寫錯",
      "guidance": "重新檢查乘法並約簡分數",
      "raw_response": "...",
      "generated_at": "2025-11-11T12:34:56"
    }

    若無法呼叫外部 AI，會回傳 fallback 的簡短分析。
    """
    prompt = _build_analysis_prompt(answer_steps, student_answer, correct_answer, skill_prompt)

    # 嘗試呼叫已設定的 Gemini (genai) client；若未設定則使用 fallback
    try:
        model = get_model()
        resp = model.generate_content(prompt)
        text = getattr(resp, "text", str(resp)).strip()
        
        # 若有實際 text，嘗試解析為 JSON
        parsed = json.loads(text)
        return {
            "error_category": parsed.get("error_category", "").strip(),
            "error_explanation": parsed.get("error_explanation", "").strip(),
            "guidance": parsed.get("guidance", "").strip(),
            "raw_response": text,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Fallback logic in case of API error or JSON parsing failure
        # 若非 JSON，做最小化的回傳
        raw_text_fallback = f"fallback due to: {str(e)}"
        if 'text' in locals():
             raw_text_fallback = text
        return {
            "error_category": "分析失敗",
            "error_explanation": f"無法解析 AI 回應: {str(e)}",
            "guidance": "請檢查你的作答，或稍後再試。",
            "raw_response": raw_text_fallback,
            "generated_at": datetime.utcnow().isoformat()
        }
# ...existing code...
    