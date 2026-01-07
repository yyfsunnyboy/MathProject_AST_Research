# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: deepseek-coder-v2:lite | Strategy: Architect-Engineer Pipeline (v8.0)
# Duration: 432.11s | RAG: 10 examples
# Created At: 2026-01-07 22:12:40
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
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    result = num1 + num2
    return f"What is the sum of {num1} and {num2}?"

def generate_type_2_problem():
    operand1 = random.randint(10, 99)
    operand2 = random.randint(10, 99)
    operation = random.choice(['+', '-', '*', '/'])
    if operation == '+':
        result = operand1 + operand2
    elif operation == '-':
        result = operand1 - operand2
    elif operation == '*':
        result = operand1 * operand2
    else:
        result = operand1 / operand2
    return f"What is the result of {operand1} {operation} {operand2}?"

def generate_type_3_problem():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    operation = random.choice(['+', '-', '*', '/'])
    if operation == '+':
        result = num1 + num2
    elif operation == '-':
        result = num1 - num2
    elif operation == '*':
        result = num1 * num2
    else:
        result = num1 / num2
    return f"Calculate the result of {num1} {operation} {num2}"

def generate_type_4_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    equation = f"{a}x^2 + {b}x + {c}"
    discriminant = b**2 - 4*a*c
    if discriminant > 0:
        roots = "real and different"
    elif discriminant == 0:
        roots = "real and equal"
    else:
        roots = "imaginary"
    return f"Determine the nature of the roots for the quadratic equation {equation}."

def generate_type_5_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Find the roots of the quadratic equation {a}x^2 + {b}x + {c} = 0."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 has no real roots."

def generate_type_6_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Solve the quadratic equation {a}x^2 + {b}x + {c} = 0 using the quadratic formula."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 has no real roots, so it cannot be solved using the quadratic formula."

def generate_type_7_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Solve the quadratic equation {a}x^2 + {b}x + {c} = 0 by factoring."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 cannot be solved by factoring because it has no real roots."

def generate_type_8_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Solve the quadratic equation {a}x^2 + {b}x + {c} = 0 by completing the square."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 cannot be solved by completing the square because it has no real roots."

def generate_type_9_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Solve the quadratic equation {a}x^2 + {b}x + {c} = 0 using any method of your choice."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 has no real roots, so it cannot be solved by any method provided here."

def generate_type_10_problem():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + (discriminant ** 0.5)) / (2*a)
        x2 = (-b - (discriminant ** 0.5)) / (2*a)
        return f"Solve the quadratic equation {a}x^2 + {b}x + {c} = 0 using any method of your choice."
    else:
        return f"The quadratic equation {a}x^2 + {b}x + {c} = 0 has no real roots, so it cannot be solved by any method provided here."

def generate_type_11_problem():
    initial_position = random.randint(-3, 3)
    even_move_units = random.randint(4, 8)
    odd_move_units = -random.randint(4, 8)
    total_rolls = random.randint(10, 15)
    num_even_rolls = random.randint(2, total_rolls - 2)
    num_odd_rolls = total_rolls - num_even_rolls
    final_position = initial_position + (num_even_rolls * even_move_units) + (num_odd_rolls * odd_move_units)
    return f"Starting at position {initial_position}, move right by {even_move_units} for each even roll and left by {abs(odd_move_units)} for each odd roll. If you rolled the dice {total_rolls} times with {num_even_rolls} even rolls and {num_odd_rolls} odd rolls, what is your final position?"

def generate_type_12_problem():
    total_games = random.randint(9, 15)
    player_win_score = random.randint(2, 4)
    player_lose_score = -random.randint(2, 4)
    num_wins = random.randint(0, total_games)
    score = num_wins * player_win_score + (total_games - num_wins) * player_lose_score
    return f"In a series of {total_games} games, you win {player_win_score} points and lose {abs(player_lose_score)} points for each loss. If you won {num_wins} games, what is your total score?"

# Example usage:

# [Auto-Injected Robust Dispatcher by v8.0]
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
        return generate_type_10_problem()
