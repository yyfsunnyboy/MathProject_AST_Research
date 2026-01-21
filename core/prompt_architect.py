# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/prompt_architect.py
功能說明 (Description): 
    V15 Architect (Hardening Edition)
    負責產出具備 6 種模式、LaTeX 規約與邏輯矩陣的數學技能規格 (Spec)。
    此模組是 "Prompt Engineering" 的核心，負責指揮 Coder 如何撰寫程式碼。
    
版本資訊 (Version): V15.0
更新日期 (Date): 2026-01-18
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import os
import json
import re
import time
from datetime import datetime
from flask import current_app
from models import db, SkillInfo, SkillGenCodePrompt, TextbookExample
from core.ai_wrapper import get_ai_client

# ==============================================================================
# V15 SYSTEM PROMPT (The "Blueprints")
# ==============================================================================
# ==============================================================================
# V15.1 HYBRID SYSTEM PROMPT
# ==============================================================================
# [prompt_architect.py] V31.0 - 通用型元架構師
ARCHITECT_SYSTEM_PROMPT = r"""你現在是 K12 數學科研架構師。
【通用邏輯提取任務】：
1. **[單一精確分析]**：僅分析用戶提供的「第一個例題」，識別其數學結構、運算子與數值特徵。
2. **[演算法抽象化]**：
   - 產出一整段 Python 邏輯區塊，用於生成該題型的隨機變體。
   - 若例題包含多個子題，請將其規律抽象化為「一個具備內部分支或隨機結構的單一邏輯塊」。
   - **必須**處理數學嚴謹性（如：除法需整除且分母不為零、根號內不為負等）。
   - **必須**使用 fmt_num(n) 處理所有數值的顯示格式。
3. **[輸出規範]**：
   - 題目字串賦值給 q，答案字串賦值給 a。
   - 僅輸出 Python 邏輯行，嚴禁輸出 Markdown 標籤、定義函式或引用外部資料庫。
"""

def generate_v15_spec(skill_id, model_tag="local_14b", architect_model=None):
    """
    [V31.0 Meta-Architect] 
    技能無關 (Skill-Agnostic) 策略：自動分析單一範例並轉譯為演算法規格。
    """
    try:
        # 1. 只抓取 1 個範例，避免 Context 過載
        skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
        example = TextbookExample.query.filter_by(skill_id=skill_id).limit(1).first()
        
        if not example:
            return {'success': False, 'message': "No example found for this skill."}

        example_text = f"{example.problem_text} (Sol: {example.detailed_solution})"

        # 2. 構建純淨的 User Prompt
        user_prompt = f"""Skill Name: {skill.skill_ch_name}
### RAG EXAMPLE (Analyze this ONLY):
{example_text}

### TASK:
請將上方例題的數學邏輯轉化為一段具備隨機性的 Python 程式碼規格 (MASTER_SPEC)。
"""
        
        full_prompt = ARCHITECT_SYSTEM_PROMPT + "\n\n" + user_prompt

        # 3. 呼叫架構師 (建議使用 Gemini Pro 1.5 進行高精度分析)
        client = get_ai_client(role='architect') 
        response = client.generate_content(full_prompt)
        spec_content = response.text

        # 4. 存檔 (永遠覆蓋 MASTER_SPEC，確保 Coder 讀到最新指令)
        new_prompt_entry = SkillGenCodePrompt(
            skill_id=skill_id,
            prompt_content=spec_content,
            prompt_type="MASTER_SPEC",
            system_prompt=ARCHITECT_SYSTEM_PROMPT, 
            user_prompt_template=user_prompt,
            model_tag=model_tag,
            created_at=datetime.now()
        )
        db.session.add(new_prompt_entry)
        db.session.commit()

        return {'success': True, 'spec': spec_content}
    except Exception as e:
        return {'success': False, 'message': str(e)}
# Alias for backward compatibility if needed (though we updated callers)
# generate_v9_spec = generate_v15_spec 