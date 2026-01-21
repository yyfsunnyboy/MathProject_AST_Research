# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/prompt_architect.py
功能說明 (Description): 
    V42.0 Architect (Pure Math Edition)
    專注於分析「純符號計算題」的數學結構，產出 MASTER_SPEC。
    此版本已移除圖形 (Geometry) 與情境 (Scenario) 的干擾，
    指導 Coder 生成精準的數論與運算邏輯。
    
版本資訊 (Version): V42.0
更新日期 (Date): 2026-01-21
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
# V42.0 SYSTEM PROMPT (Pure Symbolic Math)
# ==============================================================================
ARCHITECT_SYSTEM_PROMPT = r"""你現在是 K12 數學「純符號運算」架構師。
你的任務是分析用戶提供的例題，並設計出能生成無限變體的「演算法規格書 (MASTER_SPEC)」。

【核心任務】
1. **[結構分析]**：識別例題中的運算子 (+, -, *, /, ^, sqrt)、括號結構與數值類型（整數、分數、小數）。
2. **[數值約束]**：
   - 若涉及除法，必須設計邏輯確保「整除」或「分數簡化」（除非題目特意要求餘數）。
   - 若涉及根號，必須確保開根號後為有理數（除非題目要求無理數）。
   - 若涉及減法，需考慮結果是否允許為負數。
3. **[多樣性設計]**：
   - 不要只生成一種固定的算式。
   - 請要求使用隨機邏輯（Random Choice）來變化運算子組合（例如：有時是 A+B*C，有時是 (A+B)*C）。
   - 定義變數的隨機範圍（例如：-10 到 10，且不為 0）。

【輸出規範 (MASTER_SPEC)】
請輸出一段清晰的「演算法描述」(不要寫 Python Code)，包含：
- **變數定義**：定義 n1, n2, n3等變數的生成範圍與限制。
- **運算邏輯**：描述如何組合這些變數。
- **格式要求**：
  - 題目 `q`：使用 LaTeX 格式（例如 `$(-5) \times 3$`）。
  - 答案 `a`：僅輸出最終數值，不含計算過程。

【嚴格禁令 (Negative Constraints)】
- **嚴禁**要求繪圖、坐標系、幾何圖形或 Matplotlib。
- **嚴禁**設計應用題、文字情境或物理問題。
- **嚴禁**直接輸出 Python 程式碼，只輸出邏輯規格。
"""

# ==============================================================================
# Core Generation Logic
# ==============================================================================

def generate_v15_spec(skill_id, model_tag="local_14b", architect_model=None):
    """
    [V42.0 Spec Generator]
    讀取例題 -> 呼叫 AI 架構師 -> 存入資料庫 (MASTER_SPEC)
    """
    try:
        # 1. 抓取 1 個範例 (避免過多 Context 干擾)
        skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
        example = TextbookExample.query.filter_by(skill_id=skill_id).limit(1).first()
        
        if not example:
            return {'success': False, 'message': "No example found for this skill."}

        # 簡單清理例題文字，移除不必要的 HTML 或雜訊
        problem_clean = example.problem_text.strip()
        solution_clean = example.detailed_solution.strip()
        example_text = f"Question: {problem_clean}\nSolution: {solution_clean}"

        # 2. 構建 User Prompt
        user_prompt = f"""
當前技能 ID: {skill_id}
技能名稱: {skill.skill_ch_name}

參考例題：
{example_text}

任務：
請根據上述例題，撰寫一份 MASTER_SPEC，指導工程師生成同類型的「純計算題」。
重點：確保數值隨機但邏輯嚴謹（如整除、正負號處理）。
"""
        
        full_prompt = ARCHITECT_SYSTEM_PROMPT + "\n\n" + user_prompt

        # 3. 呼叫架構師 
        # (這裡建議使用邏輯能力較強的模型，如 Gemini Pro 或 Flash)
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
        print(f"❌ Architect Error: {str(e)}")
        # 回傳錯誤訊息但不中斷程式，讓上層處理
        return {'success': False, 'message': str(e)}

def infer_model_tag(model_name):
    """
    [Legacy Support] 根據模型名稱自動判斷分級。
    """
    name = model_name.lower()
    if any(x in name for x in ['gemini', 'gpt', 'claude']): return 'cloud_pro'
    if '70b' in name or '32b' in name or '14b' in name: return 'local_14b'
    if 'phi' in name or '7b' in name or '8b' in name: return 'edge_7b'
    return 'local_14b'

# Alias for backward compatibility
generate_v9_spec = generate_v15_spec