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
V15_1_SYSTEM_PROMPT = """Role: Senior Mathematics Curriculum Architect (Taiwan).

### ⛔ MISSION:
Analyze the RAG examples and design a "Master Coding Spec" for random question generation.

### 🌍 LANGUAGE RULES:
1. ALL output text MUST be in Traditional Chinese (繁體中文, 台灣用語).
2. USE local terms: e.g., "計算下列各式的值", "最簡分數", "分配律".

### 🧩 LOGIC MATRIX (3x2 Strategy):
- Extract the core math logic (integers, fractions, brackets).
- Mode 1-2: Basic arithmetic.
- Mode 3-4: Intermediate (Nested brackets or absolute values).
- Mode 5-6: Advanced (Distributive law or multi-step logic).

### 🧪 OUTPUT FORMAT:
- Variable naming: You MUST instruct the Coder to use 'q' for question text and 'a' for the answer string.
- No Context: If the examples are pure math, do NOT force scenarios like "deposits" or "temperature".
"""

def generate_v15_spec(skill_id, model_tag="cloud_pro", architect_model=None):
    """
    [V15.1 Hybrid Architect] 
    使用混合語言策略：英文定義邏輯結構，中文定義情境內容。
    Adaption: Uses core.ai_wrapper for compatibility.
    """
    try:
        # 1. Fetch Data
        skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
        if not skill:
            return {'success': False, 'message': f"Skill {skill_id} not found."}

        # RAG: Get textbook examples
        examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(3).all()
        examples_text = []
        if examples:
            examples_text = [f"{e.problem_text} (Sol: {e.detailed_solution})" for e in examples]
        else:
            examples_text = ["(No textbook examples found. Base design on skill name.)"]

        # 2. Build Prompt (Hybrid Strategy)
        # Using concatenation since ai_wrapper supports single prompt argument
        rag_block = chr(10).join([f"Example {i+1}: {ex}" for i, ex in enumerate(examples_text)])
        
        user_prompt = f"""Skill ID: {skill_id}
Skill Name: {skill.skill_ch_name}

### RAG EXAMPLES (Reference Material):
{rag_block}

### TASK:
Analyze the 3 examples above. 
1. Extract their scenarios into `SCENARIO_DB`. 
2. Define the 3x2 Mirror Logic Matrix. 
3. Generate the final coding specification in a rigorous, logical format.
"""
        
        full_prompt = V15_1_SYSTEM_PROMPT + "\n\n" + user_prompt

        # 3. Call AI
        client = get_ai_client(role='architect') 
        
        print(f"   🧠 V15.1 Architect is thinking... (Skill: {skill.skill_ch_name})")
        # Note: ai_wrapper handles api keys and model selection based on config
        response = client.generate_content(full_prompt)
        spec_content = response.text
        
        if not spec_content:
            return {'success': False, 'message': "Empty response from AI."}

        # 4. Save to Database (MASTER_SPEC Strategy)
        skill.gemini_prompt = spec_content
        
        # 永遠以 MASTER_SPEC 標籤存檔，覆蓋或新增都不影響讀取
        new_prompt_entry = SkillGenCodePrompt(
            skill_id=skill_id,
            prompt_content=spec_content, # 統一使用 prompt_content
            prompt_type="MASTER_SPEC",    # 固定標籤，不再更動版本號
            system_prompt=V15_1_SYSTEM_PROMPT, 
            user_prompt_template=user_prompt,
            model_tag=model_tag,          # Keep tag mostly for debugging/logging origin
            architect_model=architect_model or "default_architect",
            created_at=datetime.now()
        )
        db.session.add(new_prompt_entry)
        db.session.commit()

        return {
            'success': True,
            'version': 15.1,
            'spec': spec_content, 
            'message': "V15.1 Spec generated successfully."
        }

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}

# Alias for backward compatibility if needed (though we updated callers)
# generate_v9_spec = generate_v15_spec 