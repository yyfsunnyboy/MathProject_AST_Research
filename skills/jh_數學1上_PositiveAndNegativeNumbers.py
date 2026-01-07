# ==============================================================================
# ID: jh_數學1上_PositiveAndNegativeNumbers
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 228.62s | RAG: 3 examples
# Created At: 2026-01-07 22:48:10
# Fix Status: [Repaired]
# ==============================================================================

from fractions import Fraction
import random

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")

def generate_type_1_problem():
    pos_value_magnitude = random.randint(3, 15)
    neg_value_magnitude = random.randint(3, 15)
    unit = "公里"
    positive_direction_description = "東邊"
    negative_direction_description = "西邊"
    reference_point = "學校的位置"
    positive_example_item = "超市"
    negative_target_item = "醫院"
    
    question_text = f"以{reference_point}為基準，{positive_direction_description}當作正向，{negative_direction_description}為負向。若{positive_example_item}位在{reference_point}的{positive_direction_description}{pos_value_magnitude}{unit}處，記為「＋{pos_value_magnitude}」{unit}，則{negative_target_item}位在{reference_point}的{negative_direction_description}{neg_value_magnitude}{unit}處，應該怎麼記錄？"
    answer = f"-{neg_value_magnitude} {unit}"
    
    return {"question_text": question_text, "answer": answer, "correct_answer": answer}

def generate_type_2_problem():
    direct_loss_amount = random.randint(50, 290) * 10
    cost = random.randint(250, 950) * 50
    loss_diff = random.randint(10, 150) * 10
    while loss_diff >= cost:
        loss_diff = random.randint(10, 150) * 10
    sell_price = cost - loss_diff
    
    question_text = f"商店老闆每賣出一件商品，就會記錄這筆交易的賺賠情形，他以「＋」表示賺錢，以「-」表示賠錢，例如：賺了 100 {unit}，就記為＋100 {unit}。試回答下列問題：\n⑴ 若賠了 {direct_loss_amount} {unit}，應該怎麼記錄？\n⑵ 若一件商品的成本是 {cost} {unit}，以 {sell_price} {unit} 售出，則老闆應該怎麼記錄？"
    answer1 = f"-{direct_loss_amount} {unit}"
    answer2 = f"-{loss_diff} {unit}"
    
    return {"question_text": question_text, "answer": (answer1, answer2), "correct_answer": (answer1, answer2)}

def generate_type_3_problem():
    numbers_data = []
    while len(numbers_data) < 6:
        value = random.uniform(-9.9, 9.9)
        if abs(value) > 0 and abs(value) <= 9.9 and not any(abs(num - abs(int(num))) < 1e-9 for num in numbers_data):
            latex_str = str(value).replace(".", " \\frac{{}}")
            if value < 0:
                latex_str = "-" + latex_str.strip()
            numbers_data.append((value, latex_str))
    
    random.shuffle(numbers_data)
    display_numbers_str = " ".join([num[1] for num in numbers_data])
    
    reference_number_value = random.choice([num for num in [random.uniform(-9.9, 9.9) for _ in range(5)] if abs(num) > 0 and abs(num) <= 9.9])
    reference_number_str = str(reference_number_value).replace(".", " \\frac{{}}")
    if reference_number_value < 0:
        reference_number_str = "-" + reference_number_str.strip()
    
    negative_numbers_list = [num[1] for num in numbers_data if num[0] < 0]
    integers_list = [num[1] for num in numbers_data if abs(int(num[0])) == abs(num[0])]
    same_sign_numbers_list = [num[1] for num in numbers_data if (num[0] > 0 and reference_number_value > 0) or (num[0] < 0 and reference_number_value < 0)]
    
    answer = {
        "負數": negative_numbers_list,
        "整數": integers_list,
        "同號數": same_sign_numbers_list
    }
    
    question_text = f"下列各數中，哪些是負數？哪些是整數？哪些與${{{reference_number_str}}}$是同號數？\n{display_numbers_str}"
    
    return {"question_text": question_text, "answer": answer, "correct_answer": answer}

# [Auto-Injected Robust Dispatcher by v8.0]
def generate(level=1):
    available_types = ['generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        else: return generate_type_1_problem()
    except TypeError:
        return generate_type_1_problem()
