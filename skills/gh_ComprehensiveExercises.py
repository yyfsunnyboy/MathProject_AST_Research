import random
import math
from fractions import Fraction

# Helper functions for combinations and permutations
def nCr(n, r):
    # n choose r
    if r < 0 or r > n:
        return 0
    if r == 0 or r == n:
        return 1
    if r > n // 2:
        r = n - r
    
    # Use math.comb for efficiency and correctness (available from Python 3.8)
    return math.comb(n, r)

def nPr(n, r):
    # n permute r
    if r < 0 or r > n:
        return 0
    
    # Use math.perm for efficiency and correctness (available from Python 3.8)
    return math.perm(n, r)

def generate(level=1):
    problem_type = random.choice([
        'true_false_property',
        'simple_combination_permutation',
        'conditional_combination',
        'binomial_coefficient',
        'sum_of_binomials',
        'geometric_combinations'
    ])

    if problem_type == 'true_false_property':
        return generate_true_false_property_problem(level)
    elif problem_type == 'simple_combination_permutation':
        return generate_simple_combination_permutation_problem(level)
    elif problem_type == 'conditional_combination':
        return generate_conditional_combination_problem(level)
    elif problem_type == 'binomial_coefficient':
        return generate_binomial_coefficient_problem(level)
    elif problem_type == 'sum_of_binomials':
        return generate_sum_of_binomials_problem(level)
    elif problem_type == 'geometric_combinations':
        return generate_geometric_combinations_problem(level)

def generate_true_false_property_problem(level):
    problem_sub_type = random.choice([
        'C_n_k_C_n_n_minus_k', # C_n^k = C_n^(n-k)
        'P_n_k_C_n_k_k_factorial', # P_n^k = C_n^k * k!
        'binomial_coefficient_symmetry', # (x+y)^n x^a y^b coeff == x^b y^a coeff
        'sum_of_Cnk_power_of_2', # sum C_n^k = 2^n (can be false)
        'C_n_k_plus_C_n_k_plus_1_C_n_plus_1_k_plus_1' # Pascal's identity (can be false)
    ])

    n = random.randint(5, 12 + level)
    k = random.randint(1, n - 1 if n > 1 else 1) # Ensure k is valid, 1 <= k <= n-1

    question_text = ""
    correct_answer = ""
    
    if problem_sub_type == 'C_n_k_C_n_n_minus_k':
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$C_{{{{ {n} }}}}^{{{{ {k} }}}} = C_{{{{ {n} }}}}^{{{{ {n-k} }}}}$"
        correct_answer = "○"
    elif problem_sub_type == 'P_n_k_C_n_k_k_factorial':
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$P_{{{{ {n} }}}}^{{{{ {k} }}}} = C_{{{{ {n} }}}}^{{{{ {k} }}}} \\times {k}!$"
        correct_answer = "○"
    elif problem_sub_type == 'binomial_coefficient_symmetry':
        a = random.randint(1, n - 1)
        b = n - a
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>在 $(x+y)^{{{{ {n} }}}}$ 的展開式中，$x^{{{{ {a} }}}} y^{{{{ {b} }}}}$ 項的係數與 $x^{{{{ {b} }}}} y^{{{{ {a} }}}}$ 項的係數相等。"
        correct_answer = "○"
    elif problem_sub_type == 'sum_of_Cnk_power_of_2':
        is_true_statement = random.random() < 0.7 # Most likely true
        if is_true_statement:
            question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$C_{{{{ {n} }}}}^{{0}} + C_{{{{ {n} }}}}^{{1}} + \\dots + C_{{{{ {n} }}}}^{{{{ {n} }}}} = 2^{{{{ {n} }}}}$"
            correct_answer = "○"
        else: # False case: sum of subset of terms or wrong exponent
            false_type = random.choice(['missing_term', 'wrong_exponent'])
            if false_type == 'missing_term':
                if n < 1: # Regenerate if n is too small for meaningful 'missing_term'
                    return generate_true_false_property_problem(level)
                
                missing_term_idx = random.randint(0, n)
                terms_list = []
                actual_sum_val = 0
                for i in range(n + 1):
                    if i == missing_term_idx:
                        pass # Skip this term
                    else:
                        terms_list.append(f"C_{{{{ {n} }}}}^{{{{ {i} }}}}")
                        actual_sum_val += nCr(n, i)
                
                sum_str = " + ".join(terms_list)
                question_text = f"下列敘述對的打「○」，錯的打「×」。<br>${sum_str} = 2^{{{{ {n} }}}}$"
                correct_answer = "○" if actual_sum_val == (1 << n) else "×"
                
            elif false_type == 'wrong_exponent':
                wrong_exp = n + random.choice([-1, 1, 2])
                while wrong_exp <= 0 or wrong_exp == n: # Ensure exponent is positive and different from n
                    wrong_exp = n + random.choice([-1, 1, 2])
                question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$C_{{{{ {n} }}}}^{{0}} + C_{{{{ {n} }}}}^{{1}} + \\dots + C_{{{{ {n} }}}}^{{{{ {n} }}}} = 2^{{{{ {wrong_exp} }}}}$"
                correct_answer = "×" 

    elif problem_sub_type == 'C_n_k_plus_C_n_k_plus_1_C_n_plus_1_k_plus_1':
        is_true_statement = random.random() < 0.7 # Most likely true
        if is_true_statement:
            question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$C_{{{{ {n} }}}}^{{{{ {k} }}}} + C_{{{{ {n} }}}}^{{{{ {k+1} }}}} = C_{{{{ {n+1} }}}}^{{{{ {k+1} }}}}$"
            correct_answer = "○"
        else: # False case: use wrong index for C_(n+1)
            wrong_idx = k + random.choice([-1, 0, 2])
            while wrong_idx < 0 or wrong_idx > n + 1 or wrong_idx == k+1: # Ensure index is valid and different
                wrong_idx = k + random.choice([-1, 0, 2])
            
            question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$C_{{{{ {n} }}}}^{{{{ {k} }}}} + C_{{{{ {n} }}}}^{{{{ {k+1} }}}} = C_{{{{ {n+1} }}}}^{{{{ {wrong_idx} }}}}$"
            actual_sum = nCr(n, k) + nCr(n, k + 1)
            stated_C = nCr(n + 1, wrong_idx)
            correct_answer = "○" if actual_sum == stated_C else "×"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_simple_combination_permutation_problem(level):
    n = random.randint(5, 12 + level*2)
    k = random.randint(2, min(n, 7 + level)) # k is generally smaller

    problem_sub_type = random.choice([
        'combination_select', # Choose k items from n (order doesn't matter)
        'permutation_arrange', # Arrange k items from n (order matters)
        'permutation_all_arrange', # Arrange all n items
        'handshakes_inverse' # C_n^2 type problem, asking for n given total
    ])

    question_text = ""
    correct_answer = ""

    if problem_sub_type == 'combination_select':
        item = random.choice(['人', '書', '球', '花'])
        verb = random.choice(['選出', '取出', '抽出'])
        question_text = f"從 ${n}$ {item}中{verb} ${k}$ {item}，共有多少種選法？"
        correct_answer = str(nCr(n, k))
    elif problem_sub_type == 'permutation_arrange':
        item = random.choice(['人', '字母'])
        verb = random.choice(['排成一列', '安排'])
        question_text = f"從 ${n}$ {item}中選出 ${k}$ {item} {verb}，共有多少種排法？"
        correct_answer = str(nPr(n, k))
    elif problem_sub_type == 'permutation_all_arrange':
        item = random.choice(['人', '書', '字母'])
        question_text = f"將 ${n}$ 個不同的{item}排成一列，共有多少種排法？"
        correct_answer = str(math.factorial(n))
    elif problem_sub_type == 'handshakes_inverse':
        num_players = random.randint(5, 15) # Keep n smaller for this problem type for easier inverse calculation
        total_games = nCr(num_players, 2)
        question_text = f"在一場桌球比賽中，每位選手都必須和其他選手各比賽一場。若賽程總計為 ${total_games}$ 場，則選手共有多少人？"
        correct_answer = str(num_players)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conditional_combination_problem(level):
    num_men = random.randint(4, 8 + level)
    num_women = random.randint(3, 7 + level)
    total_select = random.randint(3, min(num_men + num_women, 9 + level))

    # Adjust total_select if it's too small for some types
    if total_select < 2:
        total_select = 2

    problem_sub_type = random.choice([
        'exactly', # Exactly k men and (total-k) women
        'at_least_one_type', # At least 1 woman
        'at_least_both_types' # At least 1 man AND at least 1 woman
    ])

    # Pre-checks for impossible scenarios
    if problem_sub_type == 'at_least_one_type': # e.g. at least 1 woman
        if num_women == 0 or total_select == 0:
            return generate_conditional_combination_problem(level) # Regenerate if impossible
    elif problem_sub_type == 'at_least_both_types': # at least 1 man AND at least 1 woman
        if num_men == 0 or num_women == 0 or total_select < 2:
            return generate_conditional_combination_problem(level) # Regenerate
        if total_select > num_men + num_women:
            return generate_conditional_combination_problem(level) # Regenerate

    question_text = f"從 ${num_men}$ 位男生、${num_women}$ 位女生中選派 ${total_select}$ 人參加社區服務，共有多少種選派方法，若："
    correct_answer = ""

    if problem_sub_type == 'exactly':
        lower_r = max(0, total_select - num_women)
        upper_r = min(total_select, num_men)
        
        if lower_r > upper_r: # No valid combination possible, regenerate
            return generate_conditional_combination_problem(level)
        
        men_to_select = random.randint(lower_r, upper_r)
        women_to_select = total_select - men_to_select
        
        question_text += f"<br>(1) 恰為 ${men_to_select}$ 男生與 ${women_to_select}$ 女生。"
        correct_answer = str(nCr(num_men, men_to_select) * nCr(num_women, women_to_select))

    elif problem_sub_type == 'at_least_one_type':
        # At least one female
        question_text += "<br>(1) 至少有 $1$ 名女生。"
        total_ways = nCr(num_men + num_women, total_select)
        ways_no_women = nCr(num_men, total_select)
        correct_answer = str(total_ways - ways_no_women)
        
    elif problem_sub_type == 'at_least_both_types':
        # At least 1 man and at least 1 woman
        question_text += "<br>(1) 男生、女生至少各 $1$ 名。"
        total_ways = nCr(num_men + num_women, total_select)
        ways_no_men = nCr(num_women, total_select)
        ways_no_women = nCr(num_men, total_select)
        correct_answer = str(total_ways - ways_no_men - ways_no_women)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_binomial_coefficient_problem(level):
    # (ax^p + by^q)^n, find coefficient of x^X y^Y
    
    n = random.randint(4, 7 + level)
    
    # Generate coefficients
    coeff1 = random.randint(1, 3) * random.choice([-1, 1])
    coeff2 = random.randint(1, 3) * random.choice([-1, 1])
    
    # Generate powers for x and y terms inside the binomial
    x_power_inner = random.randint(1, 2) # E.g., x^1 or x^2
    y_power_inner = random.randint(1, 3) # E.g., y^1, y^2, y^3
    
    # The general term is C_n^r * (coeff1*x^x_power_inner)^(n-r) * (coeff2*y^y_power_inner)^r
    # So the power of x in a term is (n-r) * x_power_inner
    # And the power of y in a term is r * y_power_inner
    
    # We need to find an 'r' (from 0 to n) that generates the target powers.
    # To simplify, let's fix 'r' first, then derive the target x and y powers.
    r = random.randint(0, n)
    
    x_target_power = (n - r) * x_power_inner
    y_target_power = r * y_power_inner
    
    # Construct the terms for the binomial
    term1 = f"{coeff1}x"
    if x_power_inner > 1:
        term1 = f"{coeff1}x^{{{{ {x_power_inner} }}}}"
    
    term2 = f"{coeff2}y"
    if y_power_inner > 1:
        term2 = f"{coeff2}y^{{{{ {y_power_inner} }}}}"
    
    question_text = f"求 $({term1} + {term2})^{{{{ {n} }}}}$ 展開式中 $x^{{{{ {x_target_power} }}}} y^{{{{ {y_target_power} }}}}$ 項的係數。"

    # Calculate the coefficient: C_n^r * (coeff1)^(n-r) * (coeff2)^r
    binom_coeff = nCr(n, r)
    numerical_coeff = binom_coeff * (coeff1 ** (n - r)) * (coeff2 ** r)
    
    correct_answer = str(numerical_coeff)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sum_of_binomials_problem(level):
    question_type = random.choice(['sum_Cnk_0_to_n', 'sum_Cnk_1_to_n'])
    
    target_n = random.randint(7, 12) # A common range for n for these sums
    
    if question_type == 'sum_Cnk_0_to_n':
        target_sum = (1 << target_n) # 2^n
        sum_latex_expr_for_question = r"C_{n}^{0} + C_{n}^{1} + \dots + C_{n}^{n}"
    else: # sum_Cnk_1_to_n
        target_sum = (1 << target_n) - 1 # 2^n - 1
        sum_latex_expr_for_question = r"C_{n}^{1} + C_{n}^{2} + \dots + C_{n}^{n}"

    # Create bounds around target_sum
    lower_bound = target_sum - random.randint(10, 50)
    upper_bound = target_sum + random.randint(10, 50)
    
    # Ensure bounds make sense (lower_bound is positive)
    lower_bound = max(1, lower_bound)
    
    question_text = f"求滿足不等式 ${lower_bound} < {sum_latex_expr_for_question} < {upper_bound}$ 的正整數 $n$。"
    correct_answer = str(target_n)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_combinations_problem(level):
    num_total_points = random.randint(7, 12 + level)
    # Ensure num_collinear_points is meaningful (at least 3 and less than total)
    num_collinear_points_upper_bound = min(num_total_points - 1, 6 + level // 2)
    
    if num_collinear_points_upper_bound < 3: # If not enough points to form meaningful collinear set, regenerate
        return generate_geometric_combinations_problem(level)
        
    num_collinear_points = random.randint(3, num_collinear_points_upper_bound)

    problem_sub_type = random.choice(['lines', 'triangles'])

    question_text = f"平面上有 ${num_total_points}$ 個點，其中恰有 ${num_collinear_points}$ 個點共線，其餘點皆不共線（任意三點皆不共線）。"
    correct_answer = ""

    if problem_sub_type == 'lines':
        question_text += "<br>(1) 這些點共可決定多少條直線？"
        # Total pairs - pairs from collinear points + 1 (for the single line formed by collinear points)
        num_lines = nCr(num_total_points, 2) - nCr(num_collinear_points, 2) + 1
        correct_answer = str(num_lines)
    elif problem_sub_type == 'triangles':
        question_text += "<br>(1) 以這些點中的 $3$ 個點為頂點，共可決定多少個三角形？"
        # Total triplets - triplets from collinear points (cannot form a triangle)
        num_triangles = nCr(num_total_points, 3) - nCr(num_collinear_points, 3)
        correct_answer = str(num_triangles)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    user_answer = str(user_answer).strip().upper()
    correct_answer = str(correct_answer).strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # For numerical answers, try converting to float for comparison
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}