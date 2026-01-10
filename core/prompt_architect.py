# -*- coding: utf-8 -*-
# ==============================================================================
# ID: prompt_architect.py
# Version: v8.7.3 (Level-Aware & Clean Answers Edition)
# Last Updated: 2026-01-09
# Author: Math-Master AI Dev Team
# 
# Description: 
#   The "Brain" of the operation. This module analyzes raw textbook examples
#   and generates a precise "Architect's Specification" for the Coder model.
#
#   [v8.7.2 Upgrade]:
#   1. Clean Answer Enforcement: Explicitly forbids '$' in answer keys.
#   2. Universal Math Syntax: Added Matrix, Calculus, Probability rules.
#   3. Tool Awareness: Tells Coder to use built-in helpers.
# ==============================================================================

import sys
import os
from flask import current_app
from models import db, SkillInfo, TextbookExample
from core.ai_wrapper import get_ai_client

def generate_design_prompt(skill_id):
    """
    Retrieves examples for a skill and generates a structured design spec (Prompt).
    The output is stored in `SkillInfo.gemini_prompt` and used by the Coder.
    """
    print(f"--- [Architect v8.7.2] Starting analysis for {skill_id} ---")
    
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    if not skill:
        print(f"❌ Error: Skill {skill_id} not found.")
        return False

    # Retrieve RAG examples (Up to 12 to ensure variety)
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(12).all()
    if not examples:
        print(f"⚠️ Warning: No examples found for {skill_id}.")
        return False
    
    # Construct RAG Context
    rag_text = ""
    for i, ex in enumerate(examples):
        q = getattr(ex, 'problem_text', 'N/A')
        a = getattr(ex, 'correct_answer', 'N/A')
        rag_text += f"Example {i+1}:\nQuestion: {q}\nAnswer: {a}\n\n"

    # ==========================================================================
    # --- The Architect's System Instruction (v8.7.2) ---
    # ==========================================================================
    system_instruction = """You are a **Senior Math Curriculum Architect**.
Your goal is to design a Python implementation plan for a specific math skill.

### 1. ANALYSIS & LEVELING (CRITICAL)
Analyze the provided examples and group them by difficulty:
- **Level 1 (Basic)**: Direct calculations, definitions, simple properties, single-step logic.
- **Level 2 (Advanced)**: Word problems, multi-step logic, inverse problems, mixed operations.

### 2. PYTHON MAPPING RULE
- Create a distinct function `generate_type_N_problem` for **EACH** example.
- **Total Functions**: Must match the number of provided examples.
- **Dispatcher**: You MUST instruct the Coder to implement `def generate(level=1):` that routes to the correct types based on your Level 1/2 classification.

### 3. UNIVERSAL MATH SYNTAX & TOOLS (STRICT)
- **Built-in Helpers (DO NOT RE-IMPLEMENT):**
  - `to_latex(val)`: Converts int/float/fraction to LaTeX string.
  - `fmt_num(val)`: Formats negative numbers with `()`.
  - `get_positive_factors(n)`: Returns sorted list of factors (e.g., `[1, 2, 4]`).
  - `is_prime(n)`: Returns True/False.
  - `get_prime_factorization(n)`: Returns dict `{prime: exp}`.
  - `gcd(a, b)` and `lcm(a, b)`: Math helpers.
  - `get_random_fraction(min, max)`: Returns `Fraction`.

- **Syntax Rules**:
  - **General**: Use `fmt_num(n)` for negative numbers.
  - **Fractions**: Use `\\frac{{a}}{{b}}` (Double braces for f-strings).
  - **Matrices**: Use `\\begin{{bmatrix}} ... \\end{{bmatrix}}`.
  - **Question Text**: MUST use `$` for math expressions (e.g., f"Calculate ${a} + {b}$").
  - **Answer Format**: **DO NOT** use `$` for `answer` or `correct_answer`. Keep it clean (e.g., "5", "\\frac{1}{2}").

### 4. OUTPUT FORMAT (The Spec)
Produce a structured plan for the Coder. Do NOT write the full code, but write the **Logic & Template** for each type.

#### Format Template:
--------------------------------------------------------------------------------
**[Level 1: Basic Types]**
- **Type 1** (Based on Ex 1):
  - **Concept**: ...
  - **Variables**: `a = random(-10, 10)`, ...
  - **Question**: f"Calculate ${a} + {b}$"
  - **Answer**: str(a+b)

... (More Level 1 Types) ...

**[Level 2: Advanced Types]**
- **Type X** (Based on Ex X):
  - **Concept**: Word problem involving ...
  - **Variables**: ...
  - **Question**: f"If John has {x} apples..."
  - **Answer**: ...

**[Dispatcher Logic]**
- `if level == 1`: random.choice([Type 1, Type 2, ...])
- `if level == 2`: random.choice([Type X, Type Y, ...])
--------------------------------------------------------------------------------
"""
    
    # Inject Total Count to ensure coverage
    total_count = len(examples)
    system_instruction += f"\n**Total Examples to Map: {total_count}**\n"

    # User Prompt combining RAG data
    user_prompt = f"### SKILL ID: {skill_id}\n\n### TEXTBOOK EXAMPLES:\n{rag_text}\n\n### YOUR ARCHITECT SPEC:"

    try:
        # Call AI (Gemini 2.5 Flash Recommended for speed/logic balance)
        client = get_ai_client(role='architect')
        response = client.generate_content(system_instruction + "\n" + user_prompt)
        design_plan = response.text.strip()

        # Save the plan to DB
        skill.gemini_prompt = design_plan
        db.session.commit()
        print(f"✅ [v8.7.2] Architect Spec generated for {skill_id}. (Length: {len(design_plan)})")
        return True

    except Exception as e:
        print(f"❌ Architect Error: {e}")
        return False