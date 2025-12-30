import random
def to_latex(number):
    if isinstance(number, int) or isinstance(number, float):
        return f"${number}$"
    else:
        return number

def sub_problem_midpoint(A, B):
    midpoint = (A + B) / 2
    question_text = f"數線示意： <---|---|---|--->\n      {to_latex(A)}   0   {to_latex(B)}\n"
    question_text += f"若 A 為 {to_latex(A)}，B 為 {to_latex(B)}，則 A 和 B 的中點是多少？"
    answer = to_latex(midpoint)
    correct_answer = midpoint
    return {"question_text": question_text, "answer": answer, "correct_answer": correct_answer}

def sub_problem_distance(A, B):
    distance = abs(A - B)
    question_text = f"數線示意： <---|---|---|--->\n      {to_latex(A)}   0   {to_latex(B)}\n"
    question_text += f"若 A 為 {to_latex(A)}，B 為 {to_latex(B)}，則 A 和 B 間的距離是多少？"
    answer = to_latex(distance)
    correct_answer = distance
    return {"question_text": question_text, "answer": answer, "correct_answer": correct_answer}

def generate(level=1):
    problem_type = random.choice(["midpoint", "distance"])
    if problem_type == "midpoint":
        A = random.randint(-10, 10)
        B = random.randint(-10, 10)
        while A == B:
            B = random.randint(-10, 10)
        return sub_problem_midpoint(A, B)
    else:
        A = random.randint(-10, 10)
        B = random.randint(-10, 10)
        while A == B:
            B = random.randint(-10, 10)
        return sub_problem_distance(A, B)