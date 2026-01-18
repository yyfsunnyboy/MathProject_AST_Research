# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): skills/Example_Program_Research.py
功能說明 (Description): 科研標準化出題模板，支援 3x2 模式矩陣 (正向/反向題型)。
                       專為 14B 模型優化，整合 V14.0 視覺規範與 AST 自癒對接。
版本資訊 (Version): V1.0 (Research Branch)
更新日期 (Date): 2026-01-17
維護團隊 (Maintainer): Shih-Wei Research Lab & Gemini
=============================================================================
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# ==============================================================================
# 1. 核心進入點：generate (支援 3x2 實驗矩陣)
# ==============================================================================
def generate(level=1, **kwargs):
    """
    [Research Matrix 3x2]
    Mode 1, 3, 5: 正向出題 (Forward) - 鏡射課本例題 1, 2, 3
    Mode 2, 4, 6: 反向出題 (Reverse) - 對應例題 1, 2, 3 的逆向推理
    """
    # 接收實驗編排器傳入的強制模式
    mode = kwargs.get('force_mode', random.choice([1, 2, 3, 4, 5, 6]))
    
    result = {
        "mode": int(mode),
        "question_text": "",
        "correct_answer": "",
        "answer": "",
        "image_base64": "",
        "metadata": {
            "ablation_id": kwargs.get('ablation_id'),
            "model_size": "14B"
        }
    }

    try:
        # 模式分流邏輯
        if mode in [1, 2]:
            data = _logic_variant_1(is_reverse=(mode == 2))
        elif mode in [3, 4]:
            data = _logic_variant_2(is_reverse=(mode == 4))
        else:
            data = _logic_variant_3(is_reverse=(mode == 6))
        
        result.update(data)

    except Exception as e:
        result["question_text"] = f"Generation Error in Mode {mode}: {str(e)}"
    
    return result

# ==============================================================================
# 2. 模式邏輯實作 (以多項式不等式為例)
# ==============================================================================

def _logic_variant_1(is_reverse=False):
    """
    對應 RAG 例題 1 的變體邏輯
    """
    # 定解：座標鎖定為整數，確保 14B 運算穩定
    r1, r2 = random.randint(-4, 1), random.randint(2, 6)
    
    if not is_reverse:
        # 正向：解方程式
        # 【強制】使用 .replace() 避免 f-string LaTeX 衝突
        tpl = r"解一元二次不等式 $(x - {r1})(x - {r2}) < 0$。"
        q_text = tpl.replace("{r1}", str(r1)).replace("{r2}", str(r2))
        ans = r"{r1} < x < {r2}".replace("{r1}", str(r1)).replace("{r2}", str(r2))
    else:
        # 反向：由解回推
        tpl = r"已知一元二次不等式 $x^2 + ax + b < 0$ 的解為 ${r1} < x < {r2}$，求 $a+b$ 的值。"
        q_text = tpl.replace("{r1}", str(r1)).replace("{r2}", str(r2))
        ans = str(-(r1 + r2) + (r1 * r2))

    return {
        "question_text": q_text + r"\n(答案格式：請填寫數值)",
        "correct_answer": ans,
        "answer": ans
    }

# ==============================================================================
# 3. 視覺化渲染規範 (V14.0 Pure Style)
# ==============================================================================
def _render_research_plot(plot_data):
    """
    [V14.0] 物理比例鎖死與資源管理
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # 座標軸硬化規約
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_aspect('equal') # 鎖定正方形網格
    ax.grid(True, linestyle=':', alpha=0.6)

    # 繪圖數據處理...
    
    # [16GB VRAM 保護] 強制釋放 Figure 物件
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig) 
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# ==============================================================================
# 4. 閱卷引擎 (V11.0 Standard)
# ==============================================================================
def check(user_answer, correct_answer):
    """
    [V11.0] 強化型字串比對
    """
    u = str(user_answer).strip().replace(" ", "")
    c = str(correct_answer).strip().replace(" ", "")
    is_correct = (u == c)
    return {"correct": is_correct, "result": "正確！" if is_correct else "答案錯誤"}