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
ARCHITECT_SYSTEM_PROMPT = r"""你現在是 K12 數學跨領域「課綱架構師」。
你的任務是分析用戶提供的例題，並以「領域膠囊 (DOMAIN_CAPSULE)」格式產出通用規格，
供工程師實作「統一生成管線」。無論題型是四則運算、方程式、幾何、三角、機率統計或排列組合，
都遵循同一輸出格式。

【核心原則】
- **不鎖題型**：產出格式與轉換邏輯必須「領域無關」，適用於任何數學領域。
- **嚴禁程式碼**：僅輸出「自然語述的結構規格」，NOT Python Code；工程師負責實作。
- **嚴禁 eval**：所有運算必須以「有界、可驗證」的方式敘述，禁止 eval/exec 相關描述。

【產出格式：DOMAIN_CAPSULE】

```
domain: <arithmetic | algebra.linear | algebra.quadratic | geometry.plane | 
         trigonometry | probability | statistics | combinatorics | ...>

entities:
  - 對象名稱: 型別 (型別選項: integer, rational, real, angle, point, vector, 
                                      set, interval, ...)
    constraints: 具體範圍與限制 (例: 非零、互質、正整數、 -180°~180° 等)
    [可選] mutually_exclusive_with: [其他對象名稱]

operators: [可用運算列表]
  - +, -, *, /, sqrt, abs, ^, gcd, lcm, factorial, nCr, nPr, ...
  - 三角: sin, cos, tan, arcsin, ...
  - 幾何: distance, dot, cross, area, ...
  - 其他領域特定運算

constraints:
  - 可計算性: 所有中間值與最終答案都必須「可精確計算」（用 Fraction 或 int）
  - 邊界: 
    * 分數分母: 預設限制在 2~20 之間 (K12 難度適中)
    * 整數範圍: 預設 -100~100 (除非題意需要大數)
    * 運算複雜度: 避免產生分子/分母超過 3 位數的結果
  - 互斥: 哪些條件不能同時出現

templates: [一個或多個可變模板]
  - name: <清晰的模板名稱>
    variables:
      - var_name: 生成規則 (例：從 [範圍 a~b 的整數] 隨機取；需避免 X 值；互質等)
      - ...
    
    construction: |
      <自然語述的計算流程，不寫程式碼>
      第一步：... (數值與來源)
      第二步：... (運算、使用了哪些工具)
      第三步：...
      最終答案：...
      [重要] 不含任何 eval/exec 描述
    
    formatting:
      question_display: <題幹顯示規則，每個數值/對象用 fmt_* 工具>
                        示例："$fmt_num(a) \\times fmt_num(b)$"
                        OR     "$fmt_set({x, y, z})$" 等領域工具
      answer_display: <答案顯示規則> (例：約分後的分數、度數、集合等)
      
    notes: [可選] 額外說明 (例：為何選這些變數、通常難點在哪)

diversity:
  - 變異點 1: <簡述可變位置與方式>
  - 變異點 2: ...
  - 退化檢查: 如何確保不會產生 trivial 或重複的題目

verifier:
  - 生成後應驗證：<邏輯檢核清單，供工程師實作>
    * 條件 A 是否滿足
    * 計算結果是否有效
    * ...

[可選] cross_domain_tools:
  - 若此題型會用到通用工具（如 clamp_fraction, safe_pow, fmt_interval 等），
    請明確列出工具名稱與用途。
```

【嚴格禁令 (Negative Constraints)】
- ❌ **嚴禁字串算式或 eval/exec 敘述**：任何運算都必須用「Fraction」或「int」描述。
- ❌ **嚴禁直接寫 Python Code**：規格是「自然語述」，工程師自己實作。
- ❌ **嚴禁繪圖、視覺、Matplotlib**：題目可涉及幾何，但別要求繪圖生成。
- ❌ **嚴禁應用題、物理情境、單位轉換等實世界敘事**：純數學題。

【輸出範例（僅示意）】
```
domain: arithmetic

entities:
  - n1: rational (-20~20，非零)
  - n2: rational (-20~20，非零)
  - op1: operator ('+', '-', '*', '/') 
  - op2: operator ('+', '-', '*', '/')

templates:
  - name: chain_of_operations
    variables:
      - bracket_type: 隨機選 (無括號 | 左括號 | 右括號 | 雙括號)
    
    construction: |
      1. 隨機生成 n1, n2（遵守非零約束）
      2. 隨機選 op1, op2 與 bracket_type
      3. 依 bracket_type 計算：
         - 無括號: result = (n1 op1 n2) op2 n3 [先左]
         - 左括號: result = (n1 op1 n2) op2 n3 [括號優先]
         - ...
         [用 if-elif 實現，Fraction 直接運算，禁 eval]
      4. 化簡到最簡分數形式
    
    formatting:
      question_display: "n1 的 fmt_num，中間 op_latex[op1]，n2 的 fmt_num，括號適當"
      answer_display: "最簡分數或整數，用 fmt_num"
```

【最終輸出要求】
1. 一個清晰、完整的 DOMAIN_CAPSULE
2. 使用上述格式，但勿機械性複製範例
3. 確保「不鎖題型」原則：任何工程師遵循此規格，用「統一生成管線」都能實作
"""

# ==============================================================================
# AUXILIARY FUNCTION DESIGN GUIDELINES
# ==============================================================================
AUXILIARY_FUNCTION_PROMPT = r"""你是 K12 數學教案設計專家。

當設計「輔助函數」章節時，請注意：

1. **系統已預載工具**：
   - `fmt_num(num)`: 格式化數字為 LaTeX（自動處理括號，**不含外層 $**）
   - `to_latex(num)`: 轉換分數為 LaTeX（**不含外層 $**）
   - `clean_latex_output(q_str)`: 清洗題目字串並在最外層**自動加一對 $ 符號**（你不要再自己加）
   - `Fraction(num, den)`: Python 內建分數類別；小數請用 `Fraction(str(decimal_value))` 避免浮點誤差
   - `random.randint()`, `random.choice()`: 隨機數生成
   - `check()`: 驗證答案的數論工具
   - `op_latex`: **全域已定義的運算子映射表** `{'+': '+', '-': '-', '*': '\\times', '/': '\\div'}`
     - ✅ 直接使用: `f"{fmt_num(n1)} {op_latex[op]} {fmt_num(n2)}"`
     - ❌ **嚴禁重新定義**: 不要在 generate() 內部再寫 `op_latex = {...}`

2. **嚴禁事項 [V47 強制規定]**：
   - ❌ **嚴禁 eval/exec/safe_eval/字串算式**：所有數學結果必須用 Python 直接計算（`+`, `-`, `*`, `/`），不要建構 `calc_string` 再評估
   - ❌ **嚴禁 import 任何模組**：預載工具已包含所有必要依賴（random, Fraction 等）
   - ❌ **嚴禁重新定義系統工具**：不可重新定義或覆蓋 `fmt_num`, `to_latex`, `clean_latex_output`, `check` 等

3. **輔助函數設計原則**：
   - ✅ 可以設計**領域專用**的輔助函數（例如 `_generate_chain_operation()`，用 `_` 前綴表示私有）
   - ❌ 不要重新設計格式化函式（例如 `ToLaTeX`, `FormatNumber`）
   - ❌ 不要重新設計隨機數生成器（例如 `GenerateInteger`）

4. **正確寫法範例**：
   ```
   **輔助函數**:
   - `_build_expression(terms, ops)`: 組合多項式表達式
   - `_validate_result(value)`: 檢查結果是否符合範圍
   
   **使用系統工具**:
   - 格式化數字：直接使用 `fmt_num(value)`
   - 生成隨機整數：直接使用 `random.randint(a, b)`
   - 生成分數：直接使用 `Fraction(num, den)`
   - 小數轉分數：使用 `Fraction(str(0.5))` 而非 `Fraction(0.5)`
   - 清洗題目字串：使用 `q = clean_latex_output(q)` **僅呼叫一次**
   ```

5. **錯誤示範（禁止）**：
   ```
   ❌ `ToLaTeX(value)`: 將數字轉為 LaTeX（這會誘導 AI 自己實作）
   ❌ `GenerateInteger(range)`: 生成隨機整數（應直接用 random.randint）
   ❌ `FormatFraction(num, den)`: 格式化分數（應直接用 to_latex(Fraction(num, den))）
   ❌ `calc_str = "1/2 + 3/4"; result = eval(calc_str)`: 字串評估（禁止！應直接用 Fraction(1,2) + Fraction(3,4)）
   ❌ `q = clean_latex_output(q); q = clean_latex_output(q)`: 重複呼叫（僅需一次）
   ```
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