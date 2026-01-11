# -*- coding: utf-8 -*-
# ==============================================================================
# ID: prompt_architect.py
# Version: v9.2.2 (Traditional Chinese Enforcement)
# Last Updated: 2026-01-11
# Description:
#   Upgrade from v9.2.1:
#   1. Enforce "Traditional Chinese (Taiwan)" for ALL output content.
#   2. Architect MUST write the `tutor_guide` in Chinese.
#   3. Architect MUST instruct Coder to generate Chinese question text.
# ==============================================================================

import json, re, ast
from models import db, SkillInfo, TextbookExample, SkillGenCodePrompt
from core.ai_wrapper import get_ai_client

def generate_v9_spec(skill_id, model_tag='cloud_pro', prompt_strategy='standard', architect_model='human'):
    print(f"--- [Architect v9.2.2] Analyzing {skill_id} for '{model_tag}' (Chinese Mode) ---")
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
    if not skill: return {'success': False, 'message': 'Skill not found'}

    # 1. 抓取全量例題
    all_examples = TextbookExample.query.filter_by(skill_id=skill_id).order_by(TextbookExample.id).all()
    if not all_examples: return {'success': False, 'message': 'No examples found'}
    selected_examples = all_examples[:12]
    rag_text = "".join([f"Example {i+1}:\nQ: {getattr(ex, 'problem_text', 'N/A')}\nA: {getattr(ex, 'correct_answer', 'N/A')}\n\n" for i, ex in enumerate(selected_examples)])

    # 2. 定義分級策略
    if model_tag == 'edge_7b':
        tier_scope = "Consolidate all examples into ONE single, highly representative function. Keep logic flat and simple."
    elif model_tag == 'local_14b':
        tier_scope = "Consolidate examples into MAX 3 distinct problem types (e.g., Calculation, Concept, Application)."
    else: # cloud_pro
        tier_scope = "Create a rich variety of problem types covering all nuances of the examples."

    # 3. 系統指令 (升級版：加入語言衛兵)
    system_instruction = f"""You are an **Elite Math Architect & Engineering Lead**.
Your goal is to design a Python implementation plan (`coder_spec`) for a Junior Coder AI.

### 🌐 GOAL 0: LANGUAGE ENFORCEMENT (CRITICAL)
1.  **Output Language**: All generated content (Questions, Stories, Explanations, Tutor Guides) MUST be in **Traditional Chinese (Taiwan)** (繁體中文).
2.  **Terminology**: Use standard Taiwan math terminology (e.g., use "座標" not "坐標", "矩陣" not "行列式" context dependent).
3.  **Coder Instructions**: You MUST explicitly tell the Coder AI: "Generate the `question_text` and `correct_answer` in Traditional Chinese."

### 🎯 GOAL 1: ADAPTIVE SCENARIO (Context vs. Pure Math)
Analyze the INPUT DATA (Textbook Examples) first.
1.  **If examples are Word Problems**: You MUST wrap math in **Real-world Scenarios** (e.g., Shopping, Temperature, Geometry Design).
2.  **If examples are Pure Calculations** (e.g., "Solve x+y=5"):
    - **DO NOT** force a story. Keep it abstract and clean.
    - Focus on **Structural Diversity** (e.g., vary equation forms, use fractions/integers mix).
    - Visuals should be technical plots (e.g., "Geometric Solution").

*Instruction to Coder*: Explicitly tell the Coder to match the *style* of the reference examples (Story vs. Pure Math).

### 🛠️ GOAL 2: ENGINEERING ROBUSTNESS (Strict Rules)
1.  **NO File I/O**: NEVER use `savefig`. Use `io.BytesIO` and return **Base64** string.
2.  **Return Format**: MUST return a Dictionary:
    {{
        "question_text": "Story (in Chinese)...", 
        "correct_answer": "Solution (in Chinese)...", 
        "image_base64": "...", 
        "problem_type": "..."
    }}
3.  **Visuals**: Use `matplotlib`. **CRITICAL**: Set Chinese font: `plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']`.
4.  **Randomization**: Never hardcode numbers. Use `random`.

### 🛡️ GOAL 3: NUMERICAL GUARDRAILS (Feasibility & Logic)
You MUST instruct the Coder to enforce these mathematical constraints:
1.  **Reasonable Ranges**: Lengths > 0, Angles sum to 180, etc.
2.  **Clean Answers (Reverse Engineering)**:
    - **DO NOT** generate random operands first.
    - **DO** generate the *Answer* first (integers), then calculate operands.
3.  **Logic Checks**: No division by zero, etc.

### 📝 INPUT DATA (Textbook Examples)
{rag_text}

### 📦 OUTPUT FORMAT (JSON ONLY)
Return a valid JSON object with:
1. `coder_spec`: A detailed MARKDOWN prompt for the Coder AI. **Ensure the prompt instructions explicitly demand Traditional Chinese output.**
2. `tutor_guide`: A concise cheat sheet in **Traditional Chinese**.

### ⛔ SYSTEM SAFETY
- Escape all double quotes in JSON.
- NO conversational text. START WITH `{{`.
"""

    user_prompt = f"### SKILL: {skill.skill_ch_name} ({skill.skill_id})\n### STRATEGY: {tier_scope}\n### EXECUTE:"

    try:
        client = get_ai_client(role='architect')
        try:
            response = client.generate_content(
                system_instruction + "\n" + user_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
        except:
            response = client.generate_content(system_instruction + "\n" + user_prompt)
            
        response_text = response.text.strip()
        
        # --- JSON 解析與容錯 ---
        clean_json = re.sub(r'^```json\s*|```$', '', response_text, flags=re.MULTILINE).strip()
        data = {}
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            print(f"   ⚠️ JSON Standard Parse Failed. Trying AST...")
            try:
                data = ast.literal_eval(clean_json)
            except:
                print(f"   🚨 Parsing FAILED. Fallback to Raw.")
                data = {"coder_spec": clean_json, "tutor_guide": "Parsing Failed."}

        # Stringify
        coder_spec = data.get('coder_spec', '')
        if isinstance(coder_spec, (dict, list)): coder_spec = json.dumps(coder_spec, indent=2, ensure_ascii=False)
        else: coder_spec = str(coder_spec)

        tutor_guide = data.get('tutor_guide', '')
        if isinstance(tutor_guide, (dict, list)): tutor_guide = json.dumps(tutor_guide, indent=2, ensure_ascii=False)
        else: tutor_guide = str(tutor_guide)

        # 4. Upsert DB
        existing_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=model_tag).first()
        
        final_version = 1
        if existing_prompt:
            existing_prompt.user_prompt_template = coder_spec
            existing_prompt.system_prompt = system_instruction
            existing_prompt.version += 1
            final_version = existing_prompt.version
            print(f"   🔄 [Upsert] Updated existing prompt (Ver: {final_version})")
        else:
            new_prompt = SkillGenCodePrompt(
                skill_id=skill_id, model_tag=model_tag, user_prompt_template=coder_spec, 
                system_prompt=system_instruction, version=1, is_active=True, 
                architect_model=architect_model
            )
            db.session.add(new_prompt)
            print(f"   🆕 [Upsert] Inserted new prompt entry.")

        if model_tag == 'cloud_pro':
            skill.gemini_prompt = tutor_guide
            print("   📢 [Tutor Guide] Updated (TC).")
        else:
            print(f"   🔒 [Tutor Guide] Locked.")
        
        db.session.commit()
        return {'success': True, 'version': final_version}

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in generate_v9_spec: {str(e)}")
        return {'success': False, 'message': str(e)}