# ==============================================================================
# ID: jh_數學1下_PerpendicularBisectorsAndLineSymmetricFigures
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 111.23s | RAG: 5 examples
# Created At: 2026-01-11 22:51:31
# Fix Status: [Repaired]
#==============================================================================


import random
import math
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
# --- 4. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization (LaTeX spaces).
    """
    if user_answer is None: return {"correct": False, "result": "No answer provided."}
    
    # 1. Normalize strings (remove spaces, LaTeX commas, etc.)
    def normalize(s):
        return str(s).strip().replace(" ", "").replace("\\,", "").replace("\\;", "")
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy
    if user_norm == correct_norm:
        return {"correct": True, "result": "Correct!"}
        
    # 3. Float Match Strategy (for numerical answers)
    try:
        # If both can be parsed as floats and are close enough
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except ValueError:
        pass # If parsing to float fails, it's not a simple numerical answer.
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}    
    return result

import matplotlib.pyplot as plt
import numpy as np

import io
import base64
import matplotlib.patches as patches


# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# Helper function for plotting and labeling points
def plot_point(ax, point, label, color='blue', marker='o', text_offset=(0.5, 0.5)):
    ax.plot(point[0], point[1], marker, color=color, markersize=8, zorder=5)
    ax.text(point[0] + text_offset[0], point[1] + text_offset[1], label, fontsize=12, ha='center', va='center', zorder=6)

# Helper function for drawing lines
def draw_line(ax, p1, p2, linestyle='-', color='black', label=None, linewidth=1.5, zorder=1):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linestyle=linestyle, color=color, label=label, linewidth=linewidth, zorder=zorder)

# Helper function for calculating distance
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Helper function for calculating midpoint
def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

# Helper function to rotate a point around an origin
def rotate_point(point, angle_rad, origin=(0, 0)):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
    qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
    return (qx, qy)

# Helper function to get the centroid of a polygon
def polygon_centroid(vertices):
    x_coords = [p[0] for p in vertices]
    y_coords = [p[1] for p in vertices]
    _len = len(vertices)
    centroid_x = sum(x_coords) / _len
    centroid_y = sum(y_coords) / _len
    return (centroid_x, centroid_y)

# Helper function to generate base64 image
def get_image_base64(fig):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image_base64

def generate_problem():
    problem_types = [
        "point_to_line_distance",
        "segment_division_midpoint",
        "line_symmetry_properties",
        "identify_symmetric_figures",
        "paper_folding_symmetry"
    ]
    selected_type = random.choice(problem_types)

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    problem_type_label = ""

    fig, ax = plt.subplots(figsize=(7, 7)) # Increased size for better clarity
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_xticks(np.arange(-10, 11, 2))
    ax.set_yticks(np.arange(-10, 11, 2))
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel('x', loc='right')
    ax.set_ylabel('y', loc='top', rotation=0)

    # Manually add '0' label to avoid overlap with 'x'/'y' or removal by ticklabel filtering
    ax.text(0.5, -1.5, '0', color='black', ha='center', va='top', fontsize=10) 
    ax.set_xticklabels(['' if x == 0 else str(int(x)) for x in ax.get_xticks()])
    ax.set_yticklabels(['' if y == 0 else str(int(y)) for y in ax.get_yticks()])


    if selected_type == "point_to_line_distance":
        problem_type_label = "點到直線距離"
        
        # Randomly choose line type (horizontal or vertical)
        is_horizontal = random.choice([True, False])
        
        if is_horizontal:
            line_val = random.randint(-5, 5) # y-value for horizontal line
            x_B = random.randint(-8, 8)
            distance = random.randint(3, 7)
            
            # Ensure B is not on the line
            y_B_options = [line_val + distance, line_val - distance]
            y_B = random.choice(y_B_options)
            
            B = (x_B, y_B)
            D = (x_B, line_val) # Perpendicular foot
            
            # Line L points for drawing (extended beyond view limits for visual clarity)
            line_p1 = (-15, line_val)
            line_p2 = (15, line_val)
            
            question_text = f"如圖所示，直線 L 為通過點 ({int(line_p1[0])}, {line_val}) 和 ({int(line_p2[0])}, {line_val}) 的水平線，點 B 的座標為 ({B[0]}, {B[1]})。"
            question_text += "\n請問點 B 到直線 L 的距離是圖中哪條線段的長度？"
            
            # Generate other points on L
            other_points = []
            x_coords_used = {x_B}
            while len(other_points) < 3:
                x_c = random.randint(-9, 9)
                if x_c not in x_coords_used:
                    other_points.append((x_c, line_val))
                    x_coords_used.add(x_c)
            
            C, E, F = other_points[0], other_points[1], other_points[2]
            
            # Plotting
            draw_line(ax, line_p1, line_p2, color='k', label='L')
            plot_point(ax, B, 'B', color='red', text_offset=(0.5, 0.8))
            plot_point(ax, D, 'D', color='green', text_offset=(0.5, 0.8))
            plot_point(ax, C, 'C', color='purple', text_offset=(0.5, 0.8))
            plot_point(ax, E, 'E', color='orange', text_offset=(0.5, 0.8))
            plot_point(ax, F, 'F', color='brown', text_offset=(0.5, 0.8))
            
            # Draw perpendicular line segment
            draw_line(ax, B, D, linestyle='--', color='blue')
            
            # Add right angle symbol
            if y_B > line_val: # B is above the line
                ax.plot([D[0], D[0]+0.5, D[0]+0.5], [D[1], D[1], D[1]+0.5], 'k-', linewidth=1)
            else: # B is below the line
                ax.plot([D[0], D[0]+0.5, D[0]+0.5], [D[1], D[1], D[1]-0.5], 'k-', linewidth=1)


        else: # Vertical line
            line_val = random.randint(-5, 5) # x-value for vertical line
            y_B = random.randint(-8, 8)
            distance = random.randint(3, 7)
            
            # Ensure B is not on the line
            x_B_options = [line_val + distance, line_val - distance]
            x_B = random.choice(x_B_options)
            
            B = (x_B, y_B)
            D = (line_val, y_B) # Perpendicular foot
            
            # Line L points for drawing (extended beyond view limits for visual clarity)
            line_p1 = (line_val, -15)
            line_p2 = (line_val, 15)
            
            question_text = f"如圖所示，直線 L 為通過點 ({line_val}, {int(line_p1[1])}) 和 ({line_val}, {int(line_p2[1])}) 的垂直線，點 B 的座標為 ({B[0]}, {B[1]})。"
            question_text += "\n請問點 B 到直線 L 的距離是圖中哪條線段的長度？"
            
            # Generate other points on L
            other_points = []
            y_coords_used = {y_B}
            while len(other_points) < 3:
                y_c = random.randint(-9, 9)
                if y_c not in y_coords_used:
                    other_points.append((line_val, y_c))
                    y_coords_used.add(y_c)
            
            C, E, F = other_points[0], other_points[1], other_points[2]

            # Plotting
            draw_line(ax, line_p1, line_p2, color='k', label='L')
            plot_point(ax, B, 'B', color='red', text_offset=(0.5, 0.8))
            plot_point(ax, D, 'D', color='green', text_offset=(0.5, 0.8))
            plot_point(ax, C, 'C', color='purple', text_offset=(0.5, 0.8))
            plot_point(ax, E, 'E', color='orange', text_offset=(0.5, 0.8))
            plot_point(ax, F, 'F', color='brown', text_offset=(0.5, 0.8))
            
            # Draw perpendicular line segment
            draw_line(ax, B, D, linestyle='--', color='blue')
            
            # Add right angle symbol
            if x_B > line_val: # B is to the right of the line
                ax.plot([D[0], D[0], D[0]-0.5], [D[1], D[1]+0.5, D[1]+0.5], 'k-', linewidth=1)
            else: # B is to the left of the line
                ax.plot([D[0], D[0], D[0]+0.5], [D[1], D[1]+0.5, D[1]+0.5], 'k-', linewidth=1)

        # Options for multiple choice
        option_labels = ['BA', 'BC', 'BD', 'BE', 'BF']
        random.shuffle(option_labels)
        
        question_text += "\n選項："
        for i, label in enumerate(option_labels):
            question_text += f"\n{chr(65+i)}. 線段 {label}"

        correct_answer = f"線段 BD" # The label, not the length
        question_text += "\n(答案格式：選A/B/C/D/E)"

    elif selected_type == "segment_division_midpoint":
        problem_type_label = "線段中點與比例"

        total_length_options = [8, 12, 16, 20] # Lengths divisible by 4 for clean midpoints
        L_AB = random.choice(total_length_options)

        # Generate A, B on a horizontal or vertical line
        orientation = random.choice(['horizontal', 'vertical'])
        # Ensure points are within reasonable bounds after translation
        x_start = random.randint(-8, 8 - L_AB) if orientation == 'horizontal' else random.randint(-5, 5)
        y_start = random.randint(-5, 5) if orientation == 'horizontal' else random.randint(-8, 8 - L_AB)

        if orientation == 'horizontal':
            A = (x_start, y_start)
            B = (x_start + L_AB, y_start)
        else: # vertical
            A = (x_start, y_start)
            B = (x_start, y_start + L_AB)

        M = midpoint(A, B)
        
        # Randomly choose N to be midpoint of AM or BM
        if random.choice([True, False]): # N is midpoint of AM
            N = midpoint(A, M)
            question_segment_options = ["AN", "NM", "MB", "NB", "AB"]
            question_segment = random.choice(question_segment_options)
            
            if question_segment == "AN": ans_val = L_AB / 4
            elif question_segment == "NM": ans_val = L_AB / 4
            elif question_segment == "MB": ans_val = L_AB / 2
            elif question_segment == "NB": ans_val = L_AB * 3 / 4
            elif question_segment == "AB": ans_val = L_AB
            
            question_text = f"如圖所示，線段 AB 長度為 {L_AB}。點 M 是線段 AB 的中點，點 N 是線段 AM 的中點。"
            question_text += f"\n請問線段 {question_segment} 的長度為何？"
        else: # N is midpoint of BM
            N = midpoint(M, B)
            question_segment_options = ["AN", "AM", "MN", "NB", "AB"]
            question_segment = random.choice(question_segment_options)
            
            if question_segment == "AN": ans_val = L_AB * 3 / 4
            elif question_segment == "AM": ans_val = L_AB / 2
            elif question_segment == "MN": ans_val = L_AB / 4
            elif question_segment == "NB": ans_val = L_AB / 4
            elif question_segment == "AB": ans_val = L_AB

            question_text = f"如圖所示，線段 AB 長度為 {L_AB}。點 M 是線段 AB 的中點，點 N 是線段 BM 的中點。"
            question_text += f"\n請問線段 {question_segment} 的長度為何？"

        # Plotting
        draw_line(ax, A, B, color='black', linewidth=2)
        plot_point(ax, A, 'A', text_offset=(0, 0.8))
        plot_point(ax, B, 'B', text_offset=(0, 0.8))
        plot_point(ax, M, 'M', color='red', text_offset=(0, 0.8))
        plot_point(ax, N, 'N', color='green', text_offset=(0, 0.8))

        # Add tick marks to indicate midpoints
        tick_len = 0.5
        if orientation == 'horizontal':
            ax.plot([M[0], M[0]], [M[1]-tick_len, M[1]+tick_len], 'k-', linewidth=1)
            # Add another tick mark for N
            ax.plot([N[0], N[0]], [N[1]-tick_len, N[1]+tick_len], 'k-', linewidth=1)
        else: # vertical
            ax.plot([M[0]-tick_len, M[0]+tick_len], [M[1], M[1]], 'k-', linewidth=1)
            # Add another tick mark for N
            ax.plot([N[0]-tick_len, N[0]+tick_len], [N[1], N[1]], 'k-', linewidth=1)

        correct_answer = f"{int(ans_val) if ans_val == int(ans_val) else ans_val}"
        question_text += "\n(答案格式：長度=_)"

    elif selected_type == "line_symmetry_properties":
        problem_type_label = "線對稱圖形性質"

        # Subtype: identify symmetric element or perpendicular bisector
        subtype = random.choice(["symmetric_element", "perpendicular_bisector"])

        if subtype == "symmetric_element":
            # Generate an isosceles triangle
            base_length = random.randint(3, 5) * 2 # Even for integer midpoints
            height = random.randint(4, 8)

            # Center the base on x-axis, apex on y-axis
            A_orig = (0, height)
            B_orig = (-base_length / 2, 0)
            C_orig = (base_length / 2, 0)
            
            # Rotate and translate for diversity
            angle = random.uniform(0, 2 * math.pi)
            center_x, center_y = random.randint(-3, 3), random.randint(-3, 3)
            
            A = rotate_point(A_orig, angle)
            B = rotate_point(B_orig, angle)
            C = rotate_point(C_orig, angle)
            
            A = (A[0] + center_x, A[1] + center_y)
            B = (B[0] + center_x, B[1] + center_y)
            C = (C[0] + center_x, C[1] + center_y)

            # Symmetry axis L: passes through A and midpoint of BC
            M_BC = midpoint(B, C)
            
            # To draw L, extend beyond the triangle. Find two points on L.
            # Use A and M_BC to define the line.
            # Extend from (M_BC[0] - 10*(A[0]-M_BC[0]), M_BC[1] - 10*(A[1]-M_BC[1]))
            # to (M_BC[0] + 10*(A[0]-M_BC[0]), M_BC[1] + 10*(A[1]-M_BC[1]))
            
            # Calculate direction vector
            dx_L = A[0] - M_BC[0]
            dy_L = A[1] - M_BC[1]
            
            # Normalize vector (if not zero)
            if dx_L == 0 and dy_L == 0: # A and M_BC are the same point, unlikely but handle
                L_p1 = (A[0], -15)
                L_p2 = (A[0], 15)
            else:
                length_vec = math.sqrt(dx_L**2 + dy_L**2)
                dx_L_norm = dx_L / length_vec
                dy_L_norm = dy_L / length_vec
                
                # Extend line for drawing
                L_p1 = (M_BC[0] - 15 * dx_L_norm, M_BC[1] - 15 * dy_L_norm)
                L_p2 = (M_BC[0] + 15 * dx_L_norm, M_BC[1] + 15 * dy_L_norm)
            
            # Plotting
            triangle_patch = patches.Polygon([A, B, C], closed=True, edgecolor='black', facecolor='lightblue', alpha=0.7)
            ax.add_patch(triangle_patch)
            
            draw_line(ax, L_p1, L_p2, linestyle='--', color='red', label='對稱軸 L')
            
            plot_point(ax, A, 'A', text_offset=(0, 0.8))
            plot_point(ax, B, 'B', text_offset=(-0.8, -0.8))
            plot_point(ax, C, 'C', text_offset=(0.8, -0.8))

            # Question options
            question_choices = [
                ("點 B 的對稱點是哪個點？", "點 C"),
                ("線段 AB 的對稱線段是哪條？", "線段 AC"),
                ("∠ABC 的對稱角是哪個角？", "∠ACB")
            ]
            question_choice, correct_ans = random.choice(question_choices)
            question_text = f"如圖所示為一個等腰三角形，直線 L 是其對稱軸。\n{question_choice}"
            correct_answer = correct_ans
            question_text += "\n(答案格式：點 X 或 線段 XY 或 ∠XYZ)"

        else: # perpendicular_bisector
            # Generate two pairs of symmetric points and one non-symmetric pair
            # Start with a simple axis, e.g., y=x, then rotate and translate
            
            # Generate points symmetric w.r.t y=x
            x1_base = random.randint(2, 6)
            y1_base = random.randint(-8, 8)
            P_base = (x1_base, y1_base)
            P_prime_base = (y1_base, x1_base) # Reflection across y=x

            x2_base = random.randint(2, 6)
            y2_base = random.randint(-8, 8)
            # Ensure Q, Q' are distinct from P, P'
            while (x2_base, y2_base) == P_base or (x2_base, y2_base) == P_prime_base:
                x2_base = random.randint(2, 6)
                y2_base = random.randint(-8, 8)
            Q_base = (x2_base, y2_base)
            Q_prime_base = (y2_base, x2_base)

            # Non-symmetric pair (e.g., not reflected correctly or not perpendicular)
            R_base = (random.randint(-6, 6), random.randint(-8, 8))
            S_base = (random.randint(-6, 6), random.randint(-8, 8))
            # Ensure R and S are not symmetric to each other wrt L (y=x)
            # And ensure R and S are not on L, and R != S
            while (R_base[0] == S_base[1] and R_base[1] == S_base[0]) or \
                  (R_base[0] == R_base[1] or S_base[0] == S_base[1]) or \
                  (R_base == S_base) or \
                  (R_base in [P_base, P_prime_base, Q_base, Q_prime_base]) or \
                  (S_base in [P_base, P_prime_base, Q_base, Q_prime_base]):
                 R_base = (random.randint(-6, 6), random.randint(-8, 8))
                 S_base = (random.randint(-6, 6), random.randint(-8, 8))

            # Rotate all points and the axis
            angle = random.uniform(0, 2 * math.pi)
            center_x, center_y = random.randint(-3, 3), random.randint(-3, 3)

            # Axis L: y=x line
            L_p1_base = (-10, -10)
            L_p2_base = (10, 10)

            # Apply rotation and translation to all points
            points_to_transform = [P_base, P_prime_base, Q_base, Q_prime_base, R_base, S_base, L_p1_base, L_p2_base]
            transformed_points = [rotate_point(p, angle, (0,0)) for p in points_to_transform]
            transformed_points = [(p[0] + center_x, p[1] + center_y) for p in transformed_points]
            
            P, P_prime, Q, Q_prime, R, S, L_p1, L_p2 = transformed_points

            # Plotting
            draw_line(ax, L_p1, L_p2, linestyle='--', color='red', label='對稱軸 L')
            
            plot_point(ax, P, 'P', text_offset=(0.5, 0.8))
            plot_point(ax, P_prime, "P'", text_offset=(0.5, 0.8))
            draw_line(ax, P, P_prime, linestyle='-', color='blue')
            
            plot_point(ax, Q, 'Q', text_offset=(0.5, 0.8))
            plot_point(ax, Q_prime, "Q'", text_offset=(0.5, 0.8))
            draw_line(ax, Q, Q_prime, linestyle='-', color='green')
            
            plot_point(ax, R, 'R', text_offset=(0.5, 0.8))
            plot_point(ax, S, 'S', text_offset=(0.5, 0.8))
            draw_line(ax, R, S, linestyle='-', color='purple')
            
            question_text = "如圖所示，直線 L 是一條對稱軸。"
            question_text += "\n下列哪條線段**不被**直線 L 垂直平分？"

            options = ["PP'", "QQ'", "RS"]
            random.shuffle(options)
            
            question_text += "\n選項："
            for i, option in enumerate(options):
                question_text += f"\n{chr(65+i)}. 線段 {option}"
            
            correct_answer = "線段 RS"
            question_text += "\n(答案格式：選A/B/C)"

    elif selected_type == "identify_symmetric_figures":
        problem_type_label = "判斷線對稱圖形與對稱軸數量"

        figure_data = {
            "長方形": {"type": "rectangle", "axes": 2, "is_symmetric": True},
            "正方形": {"type": "square", "axes": 4, "is_symmetric": True},
            "等腰梯形": {"type": "isosceles_trapezoid", "axes": 1, "is_symmetric": True},
            "等腰三角形": {"type": "isosceles_triangle", "axes": 1, "is_symmetric": True},
            "正五邊形": {"type": "regular_pentagon", "axes": 5, "is_symmetric": True},
            "正六邊形": {"type": "regular_hexagon", "axes": 6, "is_symmetric": True},
            "圓形": {"type": "circle", "axes": "無限多條", "is_symmetric": True},
            "一般三角形": {"type": "general_triangle", "axes": 0, "is_symmetric": False},
            "平行四邊形": {"type": "parallelogram", "axes": 0, "is_symmetric": False},
        }
        
        selected_figure_name = random.choice(list(figure_data.keys()))
        fig_info = figure_data[selected_figure_name]
        
        # Random rotation and translation
        angle = random.uniform(0, 2 * math.pi)
        dx, dy = random.randint(-3, 3), random.randint(-3, 3)

        if fig_info["type"] == "rectangle":
            width = random.randint(4, 8)
            height = random.randint(3, 7)
            while width == height: # Ensure it's not a square
                height = random.randint(3, 7)
            
            vertices = [
                (0, 0), (width, 0), (width, height), (0, height)
            ]
            
            center = (width/2, height/2)
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)

        elif fig_info["type"] == "square":
            side = random.randint(4, 8)
            vertices = [
                (0, 0), (side, 0), (side, side), (0, side)
            ]
            center = (side/2, side/2)
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)

        elif fig_info["type"] == "isosceles_trapezoid":
            # Base width, top width, height
            base1 = random.randint(6, 10)
            base2 = random.randint(2, base1 - 2) # Top base must be smaller than bottom base
            h = random.randint(3, 7)
            
            x_offset = (base1 - base2) / 2
            vertices = [
                (0, 0), (base1, 0),
                (base1 - x_offset, h), (x_offset, h)
            ]
            
            center = polygon_centroid(vertices)
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)

        elif fig_info["type"] == "isosceles_triangle":
            base = random.randint(4, 10)
            h = random.randint(4, 10)
            
            vertices = [
                (0, 0), (base, 0), (base/2, h)
            ]
            
            center = polygon_centroid(vertices)
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)
            
        elif fig_info["type"] == "general_triangle":
            # Generate 3 points, ensure it's not isosceles or equilateral
            p1 = (random.randint(-5, -2), random.randint(-5, -2))
            p2 = (random.randint(2, 5), random.randint(-5, -2))
            p3 = (random.randint(-2, 2), random.randint(2, 5))
            
            # Re-generate if it's too close to isosceles or equilateral
            sides = sorted([dist(p1,p2), dist(p2,p3), dist(p3,p1)])
            while abs(sides[0] - sides[1]) < 0.5 or abs(sides[1] - sides[2]) < 0.5: # 0.5 is a tolerance
                p1 = (random.randint(-5, -2), random.randint(-5, -2))
                p2 = (random.randint(2, 5), random.randint(-5, -2))
                p3 = (random.randint(-2, 2), random.randint(2, 5))
                sides = sorted([dist(p1,p2), dist(p2,p3), dist(p3,p1)])
            
            center = polygon_centroid([p1,p2,p3])
            rotated_vertices = [rotate_point(v, angle, center) for v in [p1,p2,p3]]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)

        elif fig_info["type"] == "parallelogram":
            base = random.randint(5, 9)
            height = random.randint(3, 6)
            shear_x = random.randint(1, 3) # horizontal shift for top base
            
            vertices = [
                (0, 0), (base, 0), (base + shear_x, height), (shear_x, height)
            ]
            # Ensure it's not a rectangle or rhombus (sides are not equal)
            d1 = dist(vertices[0], vertices[1])
            d2 = dist(vertices[1], vertices[2])
            while shear_x == 0 or abs(d1 - d2) < 0.5: # check for rhombus
                shear_x = random.randint(1, 3)
                vertices = [(0, 0), (base, 0), (base + shear_x, height), (shear_x, height)]
                d1 = dist(vertices[0], vertices[1])
                d2 = dist(vertices[1], vertices[2])

            center = polygon_centroid(vertices)
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)
            
        elif fig_info["type"] == "circle":
            radius = random.randint(3, 6)
            center = (dx, dy)
            patch = patches.Circle(center, radius, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)
            
        elif fig_info["type"] in ["regular_pentagon", "regular_hexagon"]:
            num_sides = 5 if fig_info["type"] == "regular_pentagon" else 6
            radius = random.randint(4, 7)
            
            vertices = []
            for i in range(num_sides):
                x = radius * math.cos(2 * math.pi * i / num_sides)
                y = radius * math.sin(2 * math.pi * i / num_sides)
                vertices.append((x,y))
            
            center = (0,0) # Already centered for regular polygons
            rotated_vertices = [rotate_point(v, angle, center) for v in vertices]
            translated_vertices = [(v[0]+dx, v[1]+dy) for v in rotated_vertices]
            patch = patches.Polygon(translated_vertices, closed=True, edgecolor='black', facecolor='lightgreen', alpha=0.7)
            ax.add_patch(patch)
            

        question_text = f"請判斷以下圖形是否為線對稱圖形。若是，請寫出其對稱軸的數量。 (若為無限多條，請填寫'無限多條')"
        
        if fig_info["is_symmetric"]:
            correct_answer = f"是, 數量={fig_info['axes']}"
        else:
            correct_answer = "否, 數量=0"
        
        question_text += "\n(答案格式：是, 數量=_ 或 否, 數量=0)"

    elif selected_type == "paper_folding_symmetry":
        problem_type_label = "紙張摺疊與剪裁"

        # Fixed scenario: square paper, fold twice, cut a triangle from the outer corner
        side_length = 10
        
        # Original square (for context)
        square_vertices = [(0,0), (side_length,0), (side_length,side_length), (0,side_length)]
        square_patch = patches.Polygon(square_vertices, closed=True, edgecolor='gray', facecolor='lightyellow', alpha=0.5, zorder=0)
        ax.add_patch(square_patch)
        ax.text(side_length/2, side_length/2, "原始紙張", ha='center', va='center', fontsize=10, color='gray', zorder=0)

        # Fold lines (dashed)
        draw_line(ax, (side_length/2, 0), (side_length/2, side_length), linestyle=':', color='blue', linewidth=1, zorder=1)
        draw_line(ax, (0, side_length/2), (side_length, side_length/2), linestyle=':', color='blue', linewidth=1, zorder=1)
        
        # Depict the folded paper (one quadrant)
        # Let's say the folded paper ends up as the bottom-left quadrant
        folded_side = side_length / 2
        folded_vertices = [(0,0), (folded_side,0), (folded_side,folded_side), (0,folded_side)]
        folded_patch = patches.Polygon(folded_vertices, closed=True, edgecolor='black', facecolor='lightyellow', alpha=0.9, zorder=2)
        ax.add_patch(folded_patch)
        
        # Cut a small right triangle from the outer corner (0,0) of the folded paper
        cut_size = random.randint(1, 2)
        cut_vertices = [(0,0), (cut_size,0), (0,cut_size)]
        cut_patch = patches.Polygon(cut_vertices, closed=True, edgecolor='red', facecolor='red', alpha=0.8, zorder=3)
        ax.add_patch(cut_patch)
        ax.text(cut_size/2, cut_size/2, "剪裁處", ha='center', va='center', fontsize=10, color='white', zorder=4)

        ax.set_xlim(-2, side_length + 2)
        ax.set_ylim(-2, side_length + 2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['left'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.set_title("紙張摺疊與剪裁示意圖", fontsize=14)

        question_text = "一張正方形紙張，先沿水平中線對摺一次，再沿垂直中線對摺一次。"
        question_text += "\n接著，在最外側的角剪下一個直角三角形（如圖所示）。"
        question_text += "\n請問完全展開後，紙張的形狀為何？"
        
        correct_answer = "一個中心有菱形孔洞的正方形"
        question_text += "\n(答案格式：一個中心有菱形孔洞的正方形)"

    # Final image processing
    # Check if any patches or lines were added to the axes to determine if an image was generated
    if ax.patches or ax.lines or ax.texts: # Check if anything was drawn
        image_base64 = get_image_base64(fig)
    else:
        plt.close(fig) # Close the figure if nothing was drawn
        image_base64 = ""

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": image_base64,
        "problem_type": problem_type_label
    }


# [Auto-Injected Smart Dispatcher v8.7]
def generate(level=1):
    if level == 1:
        types = ['generate_problem']
        selected = random.choice(types)
    else:
        types = ['generate_problem']
        selected = random.choice(types)
    if selected == 'generate_problem': return generate_problem()
    return generate_problem()

# [Auto-Injected Patch v9.2] Universal Return Fixer
# 1. Ensures 'answer' key exists (copies from 'correct_answer')
# 2. Ensures 'image_base64' key exists (extracts from 'visuals')
def _patch_return_dict(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            # Fix 1: Answer Key
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            
            # Fix 2: Image Key (Flatten visuals for legacy frontend)
            if 'image_base64' not in res and 'visuals' in res:
                try:
                    # Extract first image value from visuals list
                    for item in res['visuals']:
                        if item.get('type') == 'image/png':
                            res['image_base64'] = item.get('value')
                            break
                except: pass
        return res
    return wrapper

# Apply patch to ALL generator functions in scope
import sys
# Iterate over a copy of globals keys to avoid modification issues
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'generate'):
        globals()[_name] = _patch_return_dict(_func)
