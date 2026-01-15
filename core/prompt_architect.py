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

    # 3. 系統指令 (V11.8 鏡射增強版)
    system_instruction = """【任務】：擔任 K12 數學 AI 首席系統架構師 (V11.8 鏡射增強版)

    你的 Spec 產出必須遵循：
    1. [禁絕原創]：不要設計新的題目。請指示 Coder 如何隨機化 RAG 中的現有題目。
    2. [座標鎖死]：針對幾何題，指示 Coder 必須根據 RAG 圖形（如長方形 ACEF）定義正確的頂點座標。

    3. 程式結構 (Structure Hardening)
    - [頂層函式]：嚴禁使用 class 封裝。必須直接定義 generate(level=1) 與 check(user_answer, correct_answer) 於模組最外層。
    - [自動重載]：確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

    4. 題型鏡射 (Problem Mirroring)
    - [隨機分流]：generate() 內部必須使用 random.choice 或 if/elif 邏輯，明確對應到 RAG 中的例題 (Type 1 -> Ex 1)。
    - [範例]：Spec 必須描述如何將 RAG 例題中的數據「動態化」(Dynamize)，而不是創造新題型。

    5. 排版與 LaTeX 安全 (Elite Guardrails)
    - 【強制】語法零修復 (Regex=0)：
      凡字串包含 LaTeX 指令 (如 \\frac, \\sqrt, \\pm)，嚴禁使用 f-string 或 % 格式化。
      必須嚴格執行以下模板：
      ans_val = 5
      expr = r"x = {a}".replace("{a}", str(ans_val))
      
    - 【嚴禁】不可使用 f"x = {ans_val}"，因為這會導致 LaTeX 的大括號與 Python 衝突。
    - 【排版】嚴禁使用 \\par 或 \\[...\\]。所有數學式一律使用 $...$。


    6. 視覺化與輔助函式通用規範 (Generic Helper Rules)
    - [必須回傳]：所有定義的輔助函式（如 draw_ 開頭或自定義運算函式），最後一行必須明確使用 'return' 語句回傳結果。
    - [類型一致]：若該函式結果會用於拼接 question_text，則回傳值必須強制轉為字串 (str)。
    - [防洩漏原則]：視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式，確保學生無法從圖形中直接看到答案。

    7. 數據與欄位 (Standard Fields)
    - [欄位鎖死]：返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    - [時間戳記]：更新時必須將 created_at 設為 datetime.now() 並遞增 version。

    8. 特殊領域保護 (Domain Specific Rules)
    - [矩陣與行列式]：若技能涉及 Matrix 或 Determinant：
      - correct_answer 必須為字串化的二維列表 (e.g., "[[1,2],[3,4]]")。
      - 必須強制觸發手寫模式 (在 question_text 包含 "^" 或 "[" 等手寫特徵符號)。

    9. 題目對應 (Problem Type Mapping)
    - [對應機制]：在 Spec 中定義每個 Problem Type 時，必須明確指出其對應的資料庫例題編號。
    - [格式]：例如 "Type 1 (Maps to Example 1, 3): Description..."。確保設計的邏輯緊密跟隨教科書範例。

    10. 數據禁絕常數 (Data Prohibition) [CRITICAL]
    - [隨機生成]：Spec 必須明確要求 Coder 使用 random.randint 生成所有幾何長度、角度與面積。
    - [公式計算]：嚴禁硬編碼 (Hardcode) 答案或座標。所有目標答案與圖形座標必須根據隨機生成的數據，透過幾何公式反向計算得出。


    11. [V10.2 座標平面專用硬化規格 (Coordinate Hardening Spec)]

    #### A. 資料結構鎖死 (Prevent Unpacking Error):
    - 必須指示 Coder 定義 `_generate_coordinate_value()` 並統一回傳固定格式：`(float_val, (int_part, num, den, is_neg))`。
    - 格式化函式必須嚴格執行 `int_part, num, den, is_neg = data[1]` 的解包方式。
    - 若為整數，`num` 與 `den` 設為 0；若為分數，則 `int_part` 為帶分數整數部。

    #### B. 標點題防洩漏協定 (Anti-Leak Protocol):
    - 針對「在平面上標出點」的題型 (Plotting Type)，Spec 必須明確指示 Coder：
      - 在呼叫繪圖函式時，`points` 參數必須傳入 **空列表 `[]`**。
      - 圖形僅能顯示網格與坐標軸，學生需根據題目文字自行判斷位置。
    - 針對「讀取坐標」題型 (Reading Type)，則需顯示點與標籤。

    #### C. LaTeX 模板規範 (No Double Braces):
    - 嚴禁指示 Coder 使用 `f"{{...}}"` 這種寫法。
    - 必須規範 LaTeX 模板使用單層大括號（如 `{n}`, `{d}`），並搭配 `.replace("{n}", str(num))` 進行代換，以確保輸出的 LaTeX 不會出現 `{{1}}` 冗餘。

    #### D. 視覺一致性 (V10.2 Pure Style):
    - 必須鎖定 `ax.set_aspect('equal')` 確保網格為正方形。 
    - 坐標軸標註：僅顯示原點 `0` (18號加粗)，點標籤須加白色光暈 (bbox)。



    12. [V12.6 邏輯驗證硬化規約]:
    - 【禁絕映射】：嚴禁指示 Coder 使用字典映射答案（如 "Q1" -> "第一象限"）。
    - 【強制運算】：必須指示 Coder 先產生隨機數 a, b，計算新的座標 (x', y')，最後透過 if/elif 判斷 x', y' 正負號來回傳象限名稱。
    - 【結構鎖死】：指示 check() 必須實作「數值序列比對」，只要用戶輸入的數字順序與正確座標一致，即回傳 True。

    13. [V13.0 座標教學邏輯硬化規約]:
    - 【座標選取控制】：必須指示 Coder 生成座標時使用 `random.randint(-8, 8)` 或 `random.randint(-8, 8) + 0.5`。
    - 【標註權限隔離】：
      - 指示 Coder：`ax.text` 標註的 string 只能是點的名稱（Label），絕對不能包含座標值。座標值只能出現在 `correct_answer` 欄位中。
    - 【格式精確要求】：指示 Coder 必須使用 `str(int(val))` 處理整數，確保回饋給學生的答案是 "(5, 4)" 而非 "(5.0, 4.0)"。
    - 【格線對齊】：座標軸範圍必須是對稱整數（如 -10 到 10），且 `xticks` 間隔必須固定為 1。

    14. [V13.1 教學正確性補正]:
    - 【禁絕假分數】：指示 Coder 在生成座標時，若有分數部，必須檢查 `numerator < denominator` 且 `denominator > 1`。
    - 【答案格式標準化】：
      - 座標題：正確答案格式為 A(3, 5)。
      - 屬性題：正確答案格式為純數字列表，如 2, -1, 1, 2（不要括號）。
    - 【標籤純淨化】：明確要求 Coder 在繪圖時 `ax.text` 的內容只能是標籤文字（Label），座標值（Values）只能存在於文字敘述與 correct_answer 中。

    15. [V13.5 最終硬化規約]:
    - 【標籤隔離】：強制要求 Coder 在繪圖時將「標籤文字」與「座標數值」完全隔離。ax.text 只能標註點名稱。
    - 【整數優先】：指示 Coder 生成座標後必須判斷 `if val.is_integer(): val = int(val)`，確保輸出的答案如 (5, 4) 而非 (5.0, 4.0)。
    - 【禁絕複雜比對】：嚴禁指示 Coder 在 check() 內寫 if/else 字串拆解，統一要求使用數字序列比對。
    - 【座標範圍】：座標範圍必須對稱且寬裕（如 -8 到 8），確保點與標籤不會被邊框切掉。

    16. [V13.6 API Hardened Spec]:
    - 【Arrow Ban】：嚴禁在 axhline/axvline 使用 arrowprops（會導致 API 錯誤）。必須指示使用 `ax.plot(limit, 0, ">k", clip_on=False)` 繪製箭頭。
    - 【Strict Labeling】：強制檢查點名稱是否在白名單內。
    - 【Exact Check Logic】：指示 Coder 必須逐字複製 4-line check logic，不得自行發揮。

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