# -*- coding: utf-8 -*-
# ==============================================================================
# Module: core/prompt_architect.py
# Project: AI-Driven Math Problem Generator (Taiwan Junior High School Curriculum)
# Version: v7.7.4 (Strict Spec Mode)
# Last Updated: 2026-01-06
# Author: Senior Python Architect & R&D Team
#
# Description:
#   此模組執行「專家分工模式」的第一階段：【教案設計 (The Architect)】。
#   利用高推理能力的模型 (Phi-4-mini 或 Gemini) 深度分析教科書例題 (RAG)，
#   產出給工程師 (Qwen) 閱讀的「嚴格工程規格書 (Strict Implementation Spec)」。
#
# Core Logic:
#   1. RAG Retrieval: 讀取 TextbookExample 中的數學例題。
#   2. Deep Analysis: 要求 AI 針對「每一個」例題定義出一種獨立的題型 (One-to-One Mapping)。
#   3. Strict Constraints: 強制定義變數範圍 (e.g., "int 1-50" 而非 "random number") 與難度係數。
#   4. Template Enforcement: 要求定義 f-string 模板，防止工程師漏用變數。
#   5. DB Sync: 將生成的規格書寫入 SkillInfo.gemini_prompt。
#
# Change Log (v7.7.4):
#   - [Enhancement] 導入 "One-to-One Mapping" 策略，確保覆蓋所有例題變體。
#   - [Safety] 強制要求明確的數值範圍 (Explicit Ranges)，防止 7B 模型數值幻覺。
#   - [Format] 要求輸出 Required Question Template，解決變數未使用的 Bug。
# ==============================================================================

import sys
import os
from flask import current_app
from models import db, SkillInfo, TextbookExample
from core.ai_wrapper import get_ai_client

def generate_design_prompt(skill_id):
    """
    使用架構師模型 (Gemini/Phi-4) 分析 RAG 例題，並將設計好的「嚴格規格書」存入資料庫。
    """
    print(f"--- [Architect] Starting analysis for {skill_id} ---")
    
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    if not skill: return False

    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(10).all()
    if not examples: return False
    
    rag_text = ""
    for i, ex in enumerate(examples):
        q = getattr(ex, 'problem_text', 'N/A')
        a = getattr(ex, 'correct_answer', 'N/A')
        rag_text += f"Example {i+1}:\nQuestion: {q}\nAnswer: {a}\n\n"

    # [Fix v7.7.5] 強制對齊 code_generator.py 的骨架 (Type A, B, C)
    system_instruction = """You are a Senior Math Curriculum Architect.
Your task is to analyze the provided textbook examples and generate a **Strict Python Implementation Spec**.

### CRITICAL MAPPING RULES (Must Follow):
1. **Naming Convention**: You must map examples to **Type A**, **Type B**, and **Type C**.
   - Example 1 -> **Type A** (corresponds to `generate_type_A_problem`)
   - Example 2 -> **Type B** (corresponds to `generate_type_B_problem`)
   - Example 3 -> **Type C** (corresponds to `generate_type_C_problem`)
   (If fewer examples, define at least 3 variations. If more, group them.)

2. **Define Ranges Explicitly**: e.g., "random integer between 1 and 50".

### OUTPUT FORMAT (Write this into the database):
For each Type (A, B, C), output a block like this:

**Type A** (Function: `generate_type_A_problem`):
- **Difficulty**: (Level 1-5)
- **Goal**: (One sentence summary)
- **Variables**: 
  * Define exact range (e.g., `num1: int (10-99)`).
- **Logic**:
  1. Generate `num1`...
  2. Calculate `result`...
- **Template**: (Required f-string, e.g., "Calculate {num1} + {num2}")

(Repeat for Type B and Type C...)
"""

    user_prompt = f"### TEXTBOOK EXAMPLES to Analyze:\n{rag_text}\n\n### YOUR IMPLEMENTATION SPEC:"

    try:
        client = get_ai_client(role='architect')
        response = client.generate_content(system_instruction + "\n" + user_prompt)
        design_plan = response.text.strip()

        print(f"\n[Architect Output Preview]:\n{design_plan[:300]}...\n")

        skill.gemini_prompt = design_plan
        db.session.commit()
        
        print(f"✅ Success! Aligned design plan (v7.7.5) saved for {skill_id}.")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False