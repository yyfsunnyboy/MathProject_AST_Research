import random
import math
import io
import base64
import re
import json
import matplotlib.pyplot as plt
from fractions import Fraction

# ==========================================
# 核心工具：格式化與繪圖
# ==========================================

def to_latex(num):
    """
    將數字轉換為 LaTeX 格式
    """
    if isinstance(num, int): return str(num)
    val = Fraction(num).limit_denominator(100)
    if val.denominator == 1: return str(val.numerator)
    
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    whole = abs_val.numerator // abs_val.denominator
    rem_num = abs_val.numerator % abs_val.denominator
    
    if whole == 0:
        return r"{}\frac{{{}}}{{{}}}".format(sign, rem_num, abs_val.denominator)
    return r"{}{}\frac{{{}}}{{{}}}".format(sign, whole, rem_num, abs_val.denominator)

def draw_number_line(draw_points, arrows=[]):
    """
    繪製數線圖形
    """
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False 

    fig, ax = plt.subplots(figsize=(10, 2.5))
    
    all_vals = [p[1] for p in draw_points] + [0]
    for start, end, _ in arrows:
        all_vals.extend([start, end])
        
    min_val = math.floor(min(all_vals)) - 1
    max_val = math.ceil(max(all_vals)) + 1
    
    if max_val - min_val < 8:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 4)
        max_val = int(mid + 4)
        
    ax.set_xlim(min_val - 0.5, max_val + 0.5)
    ax.set_ylim(-0.5, 0.8)
    
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axis('off')
    
    ticks = range(min_val, max_val + 1)
    for t in ticks:
        ax.plot([t, t], [-0.05, 0.05], 'k-', lw=1)
        ax.text(t, -0.2, str(t), ha='center', va='top', fontsize=10)
        
    for label, val, color in draw_points:
        ax.plot(val, 0, 'o', color=color, markersize=8, zorder=5)
        y_pos = 0.25
        ax.text(val, y_pos, label, ha='center', va='bottom', color=color, fontsize=12, fontweight='bold')

    for start, end, color in arrows:
        ax.annotate('', xy=(end, 0.15), xytext=(start, 0.15),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# ==========================================
# 主程式：題目生成
# ==========================================

def generate(level=1, **kwargs):
    prob_type = random.choice(['identify', 'distance', 'movement'])
    
    denom_choices = [2, 3, 4] if str(level) == '1' else [2, 3, 4, 5, 6, 8]
    range_limit = 5 if str(level) == '1' else 8
    
    img_b64 = ""
    state = {}
    
    if prob_type == 'identify':
        count = random.randint(2, 3)
        labels = random.sample(['A', 'B', 'C', 'D', 'E'], count)
        points_data = []
        
        used_vals = set()
        for label in labels:
            for _ in range(10):
                den = random.choice(denom_choices)
                val = Fraction(random.randint(-range_limit*den, range_limit*den), den)
                if val not in used_vals:
                    used_vals.add(val)
                    points_data.append((label, val))
                    break
        
        points_data.sort(key=lambda x: x[1])
        label_str = ", ".join([p[0] for p in points_data])
        question_text = f"請觀察數線，寫出 {label_str} 各點的座標。<br>(答案格式範例：A(2), B(-1 1/2))"
        
        ans_parts = [f"{l}({to_latex(v)})" for l, v in points_data]
        correct_answer = ", ".join(ans_parts)
        
        draw_points = [(l, float(v), 'blue') for l, v in points_data]
        img_b64 = draw_number_line(draw_points)
        
        state = {
            "type": "identify",
            "targets": {l: float(v) for l, v in points_data},
            "display_ans": correct_answer
        }

    elif prob_type == 'distance':
        den = random.choice([1, 2])
        v1 = Fraction(random.randint(-range_limit, range_limit), den)
        v2 = Fraction(random.randint(-range_limit, range_limit), den)
        while v1 == v2: v2 = Fraction(random.randint(-range_limit, range_limit), den)
        
        dist = abs(v1 - v2)
        question_text = f"數線上兩點 A(${to_latex(v1)}$)、B(${to_latex(v2)}$)，求 A、B 兩點的距離。"
        correct_answer = to_latex(dist)
        
        draw_points = [('A', float(v1), 'black'), ('B', float(v2), 'black')]
        img_b64 = draw_number_line(draw_points)
        
        state = {
            "type": "value",
            "ans": float(dist),
            "display_ans": str(dist)
        }

    elif prob_type == 'movement':
        start_val = random.randint(-5, 2)
        move = random.randint(2, 6)
        direction = random.choice(['right', 'left'])
        
        if direction == 'right':
            end_val = start_val + move
            dir_text = "向右"
            color = 'red'
        else:
            end_val = start_val - move
            dir_text = "向左"
            color = 'blue'
            
        question_text = f"數線上有一點 P，座標為 {start_val}。若將 P 點{dir_text}移動 {move} 個單位長到達 Q 點，則 Q 點座標為何？"
        correct_answer = str(end_val)
        
        draw_points = [('P', start_val, 'black'), ('Q', end_val, color)]
        arrows = [(start_val, end_val, color)]
        img_b64 = draw_number_line(draw_points, arrows)
        
        state = {
            "type": "value",
            "ans": float(end_val),
            "display_ans": str(end_val)
        }

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": img_b64,
        "state": state
    }

# ==========================================
# 驗證函數 (Ver 10.3 終極防呆版)
# ==========================================

def check(user_answer, state):
    # [Robust Check]
    # 1. 如果 state 是字串，嘗試解碼
    if isinstance(state, str):
        try:
            state = json.loads(state)
        except:
            pass # 解碼失敗先不管，往下檢查是否為 dict
    
    # 2. [關鍵修正] 檢查 state 是否真的為字典
    # 這行能擋下 'int', 'NoneType', 'list' 等所有怪異輸入
    if not isinstance(state, dict):
        return {"correct": False, "result": "系統狀態異常 (State Lost)，請重新整理頁面試試。"}

    # 3. 檢查使用者輸入
    if user_answer is None:
        return {"correct": False, "result": "請輸入答案"}
    
    u_str = str(user_answer).strip()
    if not u_str:
        return {"correct": False, "result": "請輸入答案"}

    try:
        if state.get('type') == 'identify': # 使用 .get 防止 key 不存在
            u_clean = u_str.replace(" ", "").replace("，", ",").replace("（", "(").replace("）", ")")
            targets = state.get('targets', {})
            
            for label, true_val in targets.items():
                pattern = f"{label}[=(]([-0-9./ ]+)[)]?"
                match = re.search(pattern, u_clean, re.IGNORECASE)
                
                if not match:
                    return {"correct": False, "result": f"找不到點 {label} 的答案"}
                
                user_val_str = match.group(1)
                try:
                    if "/" in user_val_str:
                        parts = user_val_str.split()
                        if len(parts) == 2:
                            val = float(Fraction(parts[1]))
                            val = float(parts[0]) + val if float(parts[0]) > 0 else float(parts[0]) - val
                        else:
                            val = float(Fraction(user_val_str))
                    else:
                        val = float(user_val_str)
                        
                    if abs(val - true_val) > 0.01:
                        return {"correct": False, "result": f"點 {label} 的座標不正確"}
                except:
                    return {"correct": False, "result": f"無法辨識點 {label} 的數值格式"}

            return {"correct": True, "result": "完全正確！"}

        elif state.get('type') == 'value':
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[ ]\d+/\d+)?(?:/\d+)?", u_str)
            if not nums:
                return {"correct": False, "result": "無法辨識數字"}
            
            ans_val = state.get('ans', 0)
            correct_display = state.get('display_ans', str(ans_val))

            for n_str in nums:
                try:
                    if "/" in n_str:
                        parts = n_str.split()
                        if len(parts) == 2:
                             val = float(Fraction(parts[1]))
                             val = float(parts[0]) + val if float(parts[0]) > 0 else float(parts[0]) - val
                        else:
                             val = float(Fraction(n_str))
                    else:
                        val = float(n_str)
                        
                    if abs(val - ans_val) < 0.01:
                        return {"correct": True, "result": "答對了！"}
                except:
                    pass
            
            return {"correct": False, "result": f"答案錯誤。正確答案是 {correct_display}"}

    except Exception as e:
        return {"correct": False, "result": f"批改錯誤：{str(e)}"}

    return {"correct": False, "result": f"答案錯誤。"}