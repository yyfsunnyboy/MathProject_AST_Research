# -*- coding: utf-8 -*-
# [core/prompt_architect.py] V15.2 Research Edition

import os
import json
import re
import time
from datetime import datetime
from flask import current_app
from models import db, SkillInfo, SkillGenCodePrompt, TextbookExample
from core.ai_wrapper import get_ai_client

# ==============================================================================
# V15.2 HYBRID SYSTEM PROMPT (廣義建模架構師)
# ==============================================================================
V15_1_SYSTEM_PROMPT = """【任務】：K12 數學科研架構師 (Dynamic Logic Architect)

### ⛔ 核心規則：
1. 目標：將 RAG 母題轉化為「廣義數學建模」邏輯。
2. 廢除樣板化思考：嚴禁直接複製母題數值。
3. 輸出格式：僅輸出 Python 程式碼邏輯（定義 q 與 a），嚴禁輸出 Markdown 標籤。
4. 針對「純計算題」：專注於運算結構的隨機化，嚴禁自創無關情境。
5. **[全量參數化強制]：規格書必須要求 Coder 將算式中的「每一個」數字都定義為獨立變數（如 n1, n2, n3...），嚴禁在 q 字串中出現任何硬編碼（Hardcoded）的常數。**
"""

def generate_v15_spec(skill_id, model_tag="cloud_pro", architect_model=None):
    """
    [V15.2 Hybrid Architect] 
    1. 捕捉 Token 數據。
    2. 依照最新 Table Schema 存入 prompt_content 與 user_prompt_template。
    """
    try:
        # 1. 抓取技能與 RAG 母題
        skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
        if not skill:
            return {'success': False, 'message': f"Skill {skill_id} not found."}

        # 僅取第 1 筆母題作為 RAG 參考
        examples = TextbookExample.query.filter_by(skill_id=skill_id).order_by(TextbookExample.id.asc()).limit(1).all()
        rag_block = ""
        if examples:
            rag_block = "\n".join([f"Example: {e.problem_text} (Sol: {e.detailed_solution})" for e in examples])
        else:
            rag_block = "(No textbook examples found. Base design on skill name.)"

        # 2. 構建使用者指令 (這將存入 user_prompt_template)
        user_prompt = f"""Skill ID: {skill_id}
Skill Name: {skill.skill_ch_name}

### RAG EXAMPLE (Mother Problem):
{rag_block}

### TASK:
1. 分析母題數學結構並實作隨機化。
2. 僅提供 '# [RAG_LOGIC_HERE]' 區塊所需的 Python 代碼。
"""
        
        full_prompt = V15_1_SYSTEM_PROMPT + "\n\n" + user_prompt

        # 3. 呼叫 AI 並捕捉 Token
        client = get_ai_client(role='architect') 
        print(f"   🧠 V15.2 Architect is thinking... (Skill: {skill.skill_ch_name})")
        
        response = client.generate_content(full_prompt)
        spec_content = response.text
        
        # --- [科研數據捕捉] ---
        p_tokens = 0
        c_tokens = 0
        if hasattr(response, 'usage_metadata'):
            p_tokens = response.usage_metadata.prompt_token_count
            c_tokens = response.usage_metadata.candidates_token_count

        if not spec_content:
            return {'success': False, 'message': "Empty response from AI."}

        # 4. 依照最新 Schema 存入資料庫
        # 更新 SkillInfo 作為備份 (Legacy access)
        skill.gemini_prompt = spec_content
        
        # 建立新的 Prompt 紀錄
        new_prompt_entry = SkillGenCodePrompt(
            skill_id=skill_id,
            architect_model=architect_model or "gemini-2.5-flash",
            model_tag=model_tag,
            prompt_type='standard',
            prompt_strategy='single_logic_rag',
            system_prompt=V15_1_SYSTEM_PROMPT, 
            user_prompt_template=user_prompt,      # 原始請求指令
            prompt_content=spec_content,           # [MASTER_SPEC] 最終產出
            creation_prompt_tokens=p_tokens,
            creation_completion_tokens=c_tokens,
            creation_total_tokens=p_tokens + c_tokens,
            version=1,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.session.add(new_prompt_entry)
        db.session.commit()

        return {
            'success': True,
            'version': 15.2,
            'spec': spec_content, 
            'tokens': {'in': p_tokens, 'out': c_tokens},
            'message': "V15.2 Spec generated and logged successfully."
        }

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}