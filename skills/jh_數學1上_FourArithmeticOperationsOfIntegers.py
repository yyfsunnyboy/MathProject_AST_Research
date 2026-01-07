# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (v7.9.3)
# Duration: 45.05s | RAG: 10 examples
# Created At: 2026-01-07 16:03:55
# Fix Status: [Repaired]
# ==============================================================================

import random

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{{num.numerator}}}{{{num.denominator}}}"
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
    # Generate a simple addition problem with integers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    return f"{num1} + {num2} =", answer

def generate_type_2_problem():
    # Generate a simple subtraction problem with integers between 1 and 20
    num1 = random.randint(1, 20)
    num2 = random.randint(1, num1)  # Ensure the result is non-negative
    answer = num1 - num2
    return f"{num1} - {num2} =", answer

def generate_type_3_problem():
    # Generate a simple multiplication problem with integers between 1 and 5
    num1 = random.randint(1, 5)
    num2 = random.randint(1, 5)
    answer = num1 * num2
    return f"{num1} x {num2} =", answer

def generate_type_4_problem():
    # Generate a simple division problem with integers between 1 and 10
    num1 = random.randint(1, 10) * random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 // num2
    return f"{num1} ÷ {num2} =", answer

def generate_type_5_problem():
    # Generate a problem involving parentheses and basic arithmetic
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    num3 = random.randint(1, 10)
    operator1 = random.choice(['+', '-'])
    operator2 = random.choice(['+', '-'])
    answer = eval(f"{num1}{operator1}{num2}{operator2}{num3}")
    return f"({num1} {operator1} {num2}) {operator2} {num3} =", answer

def generate_type_6_problem():
    # Generate a problem involving fractions and basic arithmetic
    num1 = random.randint(1, 5)
    num2 = random.randint(1, 5)
    operator = random.choice(['+', '-'])
    fraction1 = f"{num1}/{num2}"
    fraction2 = f"{num2}/{num1}"
    answer = eval(f"float({fraction1}) {operator} float({fraction2})"
    return f"{fraction1} {operator} {fraction2} =", answer

def generate_type_7_problem():
    # Generate a problem involving negative numbers and basic arithmetic
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-'])
    answer = eval(f"{num1}{operator}-{num2}")
    return f"{num1} {operator} -{num2} =", answer

def generate_type_8_problem():
    # Generate a problem involving order of operations
    num1 = random.randint(1, 5)
    num2 = random.randint(1, 5)
    num3 = random.randint(1, 5)
    operator1 = random.choice(['+', '-'])
    operator2 = random.choice(['*', '/'])
    answer = eval(f"{num1}{operator1}{num2}{operator2}{num3}")
    return f"({num1} {operator1} {num2}) {operator2} {num3} =", answer

def generate_type_9_problem():
    # Generate a problem involving exponents
    base = random.randint(1, 5)
    exponent = random.randint(1, 3)
    answer = base ** exponent
    return f"{base} ^ {exponent} =", answer

def generate_type_10_problem():
    # Generate a problem involving square roots
    num = random.randint(1, 25)
    answer = int(num ** 0.5)
    return f"√{num} =", answer

def generate_type_11_problem():
    # Generate a word problem involving integer addition and multiplication
    start_position = random.randint(-5, 5)
    total_rolls = random.randint(8, 15)
    even_move = random.randint(3, 7)
    odd_move = random.randint(-7, -3)
    even_count = random.randint(1, total_rolls - 1)
    odd_count = total_rolls - even_count
    abs_odd_move = abs(odd_move)
    final_position = start_position + (even_count * even_move) + (odd_count * odd_move)
    return f"已知小翊一開始將棋子放在坐標 {start_position}，共投擲了 {total_rolls} 次，其中出現 {even_count} 次偶數點，則棋子最後的位置在哪個坐標上？", final_position

def generate_type_12_problem():
    # Generate a word problem involving integer arithmetic for scoring
    total_games = random.randint(7, 12)
    win_points = random.randint(2, 4)
    lose_points = random.randint(1, 3)
    draw_points = random.randint(0, 2)
    draws = random.randint(1, total_games - 2)
    remaining_games = total_games - draws
    player1_wins = random.randint(1, remaining_games - 1)
    player2_wins = remaining_games - player1_wins
    player1_losses = player2_wins
    player2_losses = player1_wins
    player1_score = (player1_wins * win_points) - (player1_losses * lose_points) + (draws * draw_points)
    player2_score = (player2_wins * win_points) - (player2_losses * lose_points) + (draws * draw_points)
    return f"小妍與小美玩猜拳遊戲，遊戲規則為贏的人得 {win_points} 分，輸的人扣 {lose_points} 分，平手則各得 {draw_points} 分。已知兩人共猜了 {total_games} 次拳，其中小妍贏 {player1_wins} 次，小美贏 {player2_wins} 次，平手 {draws} 次，分別求出兩人最後的分數為何？", f"小妍{player1_score}分，小美{player2_score}分"

# Dispatcher list
dispatcher_list = [
    generate_type_1_problem,
    generate_type_2_problem,
    generate_type_3_problem,
    generate_type_4_problem,
    generate_type_5_problem,
    generate_type_6_problem,
    generate_type_7_problem,
    generate_type_8_problem,
    generate_type_9_problem,
    generate_type_10_problem,
    generate_type_11_problem,
    generate_type_12_problem
]

# Example usage:
problem, answer = dispatcher_list[0]()

# [Auto-Injected Robust Dispatcher by v7.9.3]
def generate(level=1):
    available_types = ['generate_type_10_problem', 'generate_type_11_problem', 'generate_type_12_problem', 'generate_type_1_problem', 'generate_type_2_problem', 'generate_type_3_problem', 'generate_type_4_problem', 'generate_type_5_problem', 'generate_type_6_problem', 'generate_type_7_problem', 'generate_type_8_problem', 'generate_type_9_problem']
    selected_type = random.choice(available_types)
    try:
        if selected_type == 'generate_type_10_problem': return generate_type_10_problem()
        elif selected_type == 'generate_type_11_problem': return generate_type_11_problem()
        elif selected_type == 'generate_type_12_problem': return generate_type_12_problem()
        elif selected_type == 'generate_type_1_problem': return generate_type_1_problem()
        elif selected_type == 'generate_type_2_problem': return generate_type_2_problem()
        elif selected_type == 'generate_type_3_problem': return generate_type_3_problem()
        elif selected_type == 'generate_type_4_problem': return generate_type_4_problem()
        elif selected_type == 'generate_type_5_problem': return generate_type_5_problem()
        elif selected_type == 'generate_type_6_problem': return generate_type_6_problem()
        elif selected_type == 'generate_type_7_problem': return generate_type_7_problem()
        elif selected_type == 'generate_type_8_problem': return generate_type_8_problem()
        elif selected_type == 'generate_type_9_problem': return generate_type_9_problem()
        else: return generate_type_10_problem()
    except TypeError:
        # Fallback for functions requiring arguments
        return generate_type_10_problem()
