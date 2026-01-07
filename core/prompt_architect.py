# -*- coding: utf-8 -*-
# ==============================================================================
# Module: core/prompt_architect.py
# Project: AI-Driven Math Problem Generator (Taiwan Junior High School Curriculum)
# Version: v7.8 (Syntax Fixed & Dynamic Types)
# Last Updated: 2026-01-07
# Description:
#   [Science Fair Final Build]
#   此模組執行「專家分工模式」的第一階段：【教案設計 (The Architect)】。
#   利用高推理能力的模型 (Gemini) 深度分析教科書例題 (RAG)，
#   產出給工程師 (Qwen) 閱讀的「嚴格工程規格書 (Strict Implementation Spec)」。
#
#   Core Logic:
#   1. RAG Retrieval: 讀取 TextbookExample 中的數學例題 (Limit 12)。
#   2. Dynamic Mapping: 根據例題數量 N，動態生成 Type 1 ~ Type N 的規格。
#   3. Safety Guardrails: 強制定義變數範圍、數學防呆、LaTeX 語法規範。
#   4. Syntax Fix: 使用 replace() 取代 f-string，避免 Prompt 中的 LaTeX 符號導致 Python 報錯。
# ==============================================================================

import sys
import os
from flask import current_app
from models import db, SkillInfo, TextbookExample
from core.ai_wrapper import get_ai_client

def generate_design_prompt(skill_id):
    """
    使用架構師模型 (Gemini) 分析 RAG 例題，並將設計好的「動態且安全的規格書」存入資料庫。
    """
    print(f"--- [Architect] Starting analysis for {skill_id} ---")
    
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    if not skill:
        print(f"❌ Error: Skill {skill_id} not found.")
        return False

    # [Safety] 限制讀取最多 12 個例題，避免 Context Window 爆炸或 Qwen 寫到當機
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(12).all()
    if not examples:
        print(f"⚠️ Warning: No examples found for {skill_id}.")
        return False
    
    # 建構 RAG 上下文
    rag_text = ""
    for i, ex in enumerate(examples):
        q = getattr(ex, 'problem_text', 'N/A')
        a = getattr(ex, 'correct_answer', 'N/A')
        rag_text += f"Example {i+1}:\nQuestion: {q}\nAnswer: {a}\n\n"

    # ==============================================================================
    # 核心指令 (System Prompt)
    # 使用純字串 (無 f-prefix) + replace，避免 Python 解析 LaTeX 中的 {} 導致 SyntaxError
    # ==============================================================================
    system_instruction = """You are a **Senior Math Curriculum Architect** for Taiwan Junior High School Education.
Your task is to analyze the provided textbook examples and generate a **Strict Python Implementation Spec** for a Junior Engineer (Qwen-7B).

The Engineer will blindly follow your spec. If you are vague, the code will crash. You must be precise.

### 1. DYNAMIC MAPPING RULE (Crucial)
You must define a distinct `Problem Type` for **EACH** provided example.
- Total Examples Provided: **__TOTAL_COUNT__**
- You MUST define: **Type 1**, **Type 2**, ..., up to **Type __TOTAL_COUNT__**.
- **Naming Convention**: Use function names `generate_type_1_problem`, `generate_type_2_problem`, etc.

### 2. MATH & LOGIC SAFETY GUARDRAILS (Crucial)
For each type, you must define **Constraints** to prevent meaningless or impossible math:
- **Range Control**: Do NOT say "random number". Define specific ranges suitable for mental math (e.g., `random.randint(2, 12)`). Avoid huge numbers unless necessary.
- **Divisibility**: If division is involved, ensure the result is an integer (e.g., "numerator must be a multiple of denominator").
- **Geometry**: Ensure triangle inequality (a+b>c). Ensure positive lengths.
- **Quadratic**: Ensure discriminant >= 0 for real roots.

### 3. PYTHON & LATEX SYNTAX RULES (Crucial)
The Engineer uses Python f-strings. You MUST specify the template correctly:
- **LaTeX Escape**: Backslashes must be escaped (e.g., `\\frac` not `\frac`).
- **F-String Escape**: LaTeX curly braces `{}` must be DOUBLED `{{}}` inside f-strings.
  - WRONG: `f"\\frac{a}{b}"`
  - CORRECT: `f"\\frac{{a}}{{b}}"`
- **Variable Injection**: Python variables use single braces `{var}`.
  - EXAMPLE: `f"Calculate \\frac{{{num}}}{{{denom}}}"` (This renders as LaTeX fraction)

### OUTPUT FORMAT (Write this strictly):
For each Type (1 to __TOTAL_COUNT__), output a block like this:

---
**Type {N}** (Function: `generate_type_{N}_problem`):
- **Source**: Based on Example {N}
- **Mathematical Goal**: (Short summary)
- **Variables & Constraints**: 
  * `var1`: int (range 1-10).
  * `var2`: int (range 1-10, must be > var1).
  * Logic: Ensure (`var1` + `var2`) is even.
- **Step-by-Step Logic**:
  1. Generate `var1`, `var2`...
  2. Compute `answer`...
- **Question Template (Python f-string)**: 
  * "請計算 ${{ \\frac{{{var1}}}{{{var2}}} }}$ 的值。" (Note the double braces for LaTeX)
- **Answer Format**: (e.g., Integer, Fraction string)
---

Finally, list the required dispatcher logic:
**Dispatcher List**: [`generate_type_1_problem`, ..., `generate_type___TOTAL_COUNT___problem`]
"""

    # [Safe Variable Injection] 使用 replace 填入例題數量
    system_instruction = system_instruction.replace("__TOTAL_COUNT__", str(len(examples)))

    user_prompt = f"### TEXTBOOK EXAMPLES to Analyze:\n{rag_text}\n\n### YOUR IMPLEMENTATION SPEC:"

    try:
        # 呼叫架構師 (Gemini)
        client = get_ai_client(role='architect')
        response = client.generate_content(system_instruction + "\n" + user_prompt)
        design_plan = response.text.strip()

        # 簡單驗證輸出品質
        if "Type 1" not in design_plan:
            print(f"⚠️ Warning: Architect response might be malformed.\n{design_plan[:200]}")
        
        print(f"\n[Architect Output Preview]:\n{design_plan[:300]}...\n")

        # 寫入資料庫
        skill.gemini_prompt = design_plan
        db.session.commit()
        
        print(f"✅ Success! Design plan (v7.8) saved for {skill_id}.")
        return True

    except Exception as e:
        print(f"❌ Error during architect generation: {e}")
        return False