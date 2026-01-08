# -*- coding: utf-8 -*-
# ==============================================================================
# Module: core/prompt_architect.py
# Project: AI-Driven Math Problem Generator
# Version: v8.6 (Strict Spec Engine - Safety First)
# Last Updated: 2026-01-08
# Description:
#   [Architect Engine]
#   負責分析教科書例題並產出「工程規格書 (Implementation Spec)」。
#   v8.6 重點更新：
#   1. One-to-One Mapping: 讀取 N 個例題 -> 產出 N 個對應的 Type 函式。
#   2. Safety First: 強制要求定義參數範圍 (Ranges) 與防止無窮迴圈 (Loop Limits)。
#   3. Logic Validation: 確保數學式有意義 (避免分母為0、負數長度等)。
# ==============================================================================

import sys
import os
from flask import current_app
from models import db, SkillInfo, TextbookExample
from core.ai_wrapper import get_ai_client

def generate_design_prompt(skill_id):
    """
    [v8.6 Architect]
    讀取該技能的所有例題，並要求 Gemini 2.5 Flash 為「每一題」設計一個專屬的生成函式。
    重點在於產出包含邊界檢查與安全機制的規格書。
    """
    print(f"--- [Architect v8.6] Starting analysis for {skill_id} ---")
    
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    if not skill:
        print(f"❌ Error: Skill {skill_id} not found.")
        return False

    # 1. 讀取所有例題 (1-to-1 Mapping)
    examples = TextbookExample.query.filter_by(skill_id=skill_id).all()
    
    if not examples:
        print(f"⚠️ Warning: No examples found for {skill_id}.")
        return False
    
    total_count = len(examples)
    print(f"📊 Found {total_count} examples. Generating v8.6 Safety Spec...")

    # 2. 建構 RAG 上下文
    rag_text = ""
    for i, ex in enumerate(examples):
        q = getattr(ex, 'problem_text', 'N/A').strip()
        a = getattr(ex, 'correct_answer', 'N/A').strip()
        rag_text += f"### Reference Example {i+1}:\n- Question: {q}\n- Answer: {a}\n\n"

    # ==============================================================================
    # 核心指令 (System Prompt v8.6)
    # ==============================================================================
    system_instruction = f"""You are the **Lead Math Architect** for an AI Education System.
Your goal is to design a **Strict Python Implementation Spec** for the "Coder" (Gemini 2.5 Flash).

### 1. CORE TASK: ONE-TO-ONE MAPPING
You have received **{total_count}** reference examples.
You MUST design exactly **{total_count}** separate Python functions.
- **Example 1** -> `def generate_type_1_problem():`
- ...
- **Example {total_count}** -> `def generate_type_{total_count}_problem():`

### 2. SAFETY & LOGIC GUARDRAILS (Non-Negotiable)
For every function, you must define constraints to prevent runtime errors:
- **Parameter Ranges**: Explicitly define ranges (e.g., `random.randint(2, 12)`). DO NOT allow "any random number".
- **Prevent Infinite Loops**: If using `while` loops to generate distinct numbers, **YOU MUST** instruct the Coder to use a `retry_count` (max 100 attempts).
- **Avoid Meaningless Math**:
  - Denominators MUST NOT be 0.
  - Lengths/Areas MUST be positive.
  - Triangle inequality (a+b>c) MUST hold.
  - If subtraction results in negative numbers, ensure the question allows it (or swap values).

### 3. PYTHON & LATEX SYNTAX RULES
- **F-String Escape**: 
  - LaTeX commands need double backslashes: `\\\\frac`
  - LaTeX braces need double curly braces: `{{ }}`
  - Python variables need single braces: `{{var}}`
  - **Correct Template**: `f"Calculate ${{ \\\\frac{{{{a}}}}{{{{b}}}} }}$"`

### 4. OUTPUT FORMAT (Markdown):

# Implementation Plan for {skill_id}

## Type 1 (Based on Example 1)
- **Concept**: [Short Description]
- **Variables & Constraints**:
  - `v1`: int (range 2-9)
  - `v2`: int (range 10-20), ensure `v2 % v1 == 0` (Divisibility check)
- **Step-by-Step Logic**:
  1. Generate `v1`.
  2. Generate `v2`. Loop max 100 times to ensure `v2 != v1`.
  3. Calculate `ans`.
- **Question Template**: `f"Question with LaTeX: ${{ \\\\frac{{{{v2}}}}{{{{v1}}}} }}$"`
- **Answer**: `str(ans)`

... (Repeat for all {total_count} types) ...

## Main Dispatcher
- Implement `def generate(level=1):` that randomly calls one of the {total_count} types.
"""

    user_prompt = f"### REFERENCE EXAMPLES:\n{rag_text}\n\n### ARCHITECT, PLEASE GENERATE THE SPEC:"

    try:
        # 呼叫架構師 (Gemini)
        client = get_ai_client(role='architect')
        response = client.generate_content(system_instruction + "\n" + user_prompt)
        design_plan = response.text.strip()

        # 簡單驗證
        if "Type 1" not in design_plan:
            print(f"⚠️ Warning: Architect response might be malformed.\n{design_plan[:200]}")
        
        print(f"\n[Architect Output Preview]:\n{design_plan[:300]}...\n")

        # 寫入資料庫
        skill.gemini_prompt = design_plan
        db.session.commit()
        
        print(f"✅ Success! Design plan (v8.6) saved for {skill_id}.")
        return True

    except Exception as e:
        print(f"❌ Error during architect generation: {e}")
        return False