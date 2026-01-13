# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/prompt_architect.py
功能說明 (Description): AI 架構師模組 (Architect Mode)，負責分析教科書例題與技能需求，設計並生成給 Coder AI 使用的詳細 Python 實作規格書 (Spec)。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V9.3 (Elite Hardening + Timestamp Fix)
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# ==============================================================================

import json, re, ast
from datetime import datetime # [修正] 必須導入 datetime
from models import db, SkillInfo, TextbookExample, SkillGenCodePrompt
from core.ai_wrapper import get_ai_client
from config import Config

def generate_v9_spec(skill_id, model_tag='cloud_pro', prompt_strategy='standard', architect_model='human'):
    print(f"--- [Architect v9.3] Analyzing {skill_id} for '{model_tag}' (Elite Mode) ---")
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

    # 3. 系統指令 (V9.6 終極自動化版)
    system_instruction = """【任務】：擔任 K12 數學 AI 首席系統架構師 (V9.6 終極自動化版)

你必須產出符合以下規範的 Coder Spec，確保產出的 Python 程式碼能自動執行且排版完美：

1. 程式結構 (Structure Hardening)
- [頂層函式]：嚴禁使用 class 封裝。必須直接定義 generate(level=1) 與 check(user_answer, correct_answer) 於模組最外層。
- [自動重載]：確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

2. 題型多樣性 (Problem Variety)
- [隨機分流]：generate() 內部必須使用 random.choice 或 if/elif 邏輯，根據該技能的教科書例題，實作至少 3 種不同的題型變體。
- [範例]：題型應包含「直接計算」、「逆向求解（已知距離求座標）」、「情境應用（如移動點）」。

3. 排版與 LaTeX 安全 (Layout Guardrails)
- [禁止換行符]：嚴禁使用 \\par、\\\\ 或 \[...\]。所有數學式必須使用 $...$ (Inline Math)。
- [變數注入]：必須使用 r"模板".replace("{a}", str(a)) 語法，嚴禁直接使用 f-string 處理 LaTeX 區塊。

4. 視覺化工具規範 (Visuals)
- [數線工具]：若為數線題，必須實作 draw_number_line(points_map) 且該函式「最後必須有 return html_string」。
- [拼接要求]：question_text 必須由「文字題目 + <br> + 視覺化 HTML」組成。

5. 數據與欄位 (Standard Fields)
- [欄位鎖死]：返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
- [時間戳記]：更新時必須將 created_at 設為 datetime.now() 並遞增 version。
"""

    user_prompt = f"### SKILL: {skill.skill_ch_name} ({skill.skill_id})\n### STRATEGY: {tier_scope}\n### EXECUTE:"
    
    now = datetime.now() # [新增] 捕捉當前時間

    try:
        client = get_ai_client(role='architect')
        
        # [Fix] 強行覆蓋預設值 (User Request)
        if model_tag == 'cloud_pro':
            architect_model = Config.GEMINI_MODEL_NAME
        elif model_tag == 'local_14b':
            architect_model = Config.LOCAL_MODEL_NAME

        try:
            response = client.generate_content(
                system_instruction + "\n" + user_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
        except:
            response = client.generate_content(system_instruction + "\n" + user_prompt)
            
        response_text = response.text.strip()
        
        # --- JSON 解析與容錯 (V9.3 Reinforced) ---
        clean_json = response_text.strip()
        # 1. Try to extract strictly from ```json blocks
        block_match = re.search(r'```json\s*(.*?)\s*```', clean_json, re.DOTALL)
        if block_match:
            clean_json = block_match.group(1)
        else:
            # 2. Fallback: Strip Markdown tags if they frame the entire content
            clean_json = re.sub(r'^```json\s*|```$', '', clean_json, flags=re.MULTILINE).strip()
            
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

        # 4. Upsert DB 與時間更新
        existing_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=model_tag).first()
        
        final_version = 1
        if existing_prompt:
            existing_prompt.user_prompt_template = coder_spec
            existing_prompt.system_prompt = system_instruction
            existing_prompt.version += 1
            existing_prompt.created_at = now # [關鍵修正] 更新時間戳記，解決資料庫不跳動問題
            final_version = existing_prompt.version
            print(f"   🔄 [Upsert] Updated existing prompt (Ver: {final_version})")
        else:
            new_prompt = SkillGenCodePrompt(
                skill_id=skill_id, 
                model_tag=model_tag, 
                user_prompt_template=coder_spec, 
                system_prompt=system_instruction, 
                version=1, 
                is_active=True, 
                architect_model=architect_model,
                created_at=now # [新增] 初始時間
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