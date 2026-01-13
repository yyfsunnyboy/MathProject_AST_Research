# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): skills/Example_Program.py
功能說明 (Description): 黃金標準範例程式 (Gold Standard Template)。
    作為所有 AI 生成技能程式碼的參考模板，展示了標準的結構、
    LaTeX 處理規範、分級邏輯 (Level 1/2) 以及回應格式要求。
執行語法 (Usage): 作為 RAG (Retrieval-Augmented Generation) 的參考文件
版本資訊 (Version): V8.7 (Universal)
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
import random
import math
from fractions import Fraction

# ==============================================================================
# GOLD STANDARD TEMPLATE v8.7 (Universal)
# ==============================================================================
# Rules for AI Coder:
# 1. LATEX: Use f-string with DOUBLE BRACES for LaTeX commands. 
#    Ex: f"\\frac{{{a}}}{{{b}}}" -> \frac{a}{b}
#    Ex: f"\\begin{{bmatrix}} {a} & {b} \\\\ {c} & {d} \\end{{bmatrix}}"
# 2. NEGATIVES: Use fmt_num(val) to handle negative numbers like (-5).
# 3. LEVEL: Level 1 = Basic Concept/Direct Calc. Level 2 = Application/Mixed.
# 4. RETURN: Must return dict with 'question_text', 'answer', 'correct_answer'.
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher:
    - Level 1: Basic concepts, direct calculations, simple definitions.
    - Level 2: Advanced applications, multi-step problems, word problems.
    """
    if level == 1:
        # 基礎題型池：概念定義、單步驟運算
        problem_type = random.choice([
            'type_basic_calc', 
            'type_concept_check'
        ])
    else:
        # 進階題型池：應用題、混合運算、逆向思考
        problem_type = random.choice([
            'type_advanced_app', 
            'type_reverse_logic'
        ])
    
    # Dynamic Dispatch
    if problem_type == 'type_basic_calc': return generate_basic_calculation()
    if problem_type == 'type_concept_check': return generate_concept_check()
    if problem_type == 'type_advanced_app': return generate_advanced_application()
    if problem_type == 'type_reverse_logic': return generate_reverse_logic()
    
    # Fallback
    return generate_basic_calculation()

def fmt_num(num):
    """Helper: Format negative numbers with parentheses for display."""
    if num < 0:
        return f"({num})"
    return str(num)

def generate_basic_calculation():
    """
    Level 1 Example: Basic Integer/Fraction Operation
    Demonstrates: Simple f-string LaTeX.
    """
    a = random.randint(-10, 10)
    b = random.randint(2, 9)
    # Ensure no division by zero logic inside generation
    
    ans_val = a * b
    
    # LaTeX Rule: Use double braces for LaTeX syntax inside f-strings
    # Example: exponents x^{2} should be x^{{2}}
    question_text = f"計算下列各式的值： $ {fmt_num(a)} \\times {b} $"
    
    return {
        "question_text": question_text,
        "answer": str(ans_val),
        "correct_answer": str(ans_val),
        "difficulty": 1
    }

def generate_concept_check():
    """
    Level 1 Example: Concept Definition (Matrices/Sets/Logic)
    Demonstrates: Complex LaTeX structures (Matrices).
    """
    # Example: Matrix determinant concept
    a, b, c, d = random.sample(range(1, 10), 4)
    
    # High Risk LaTeX Area: Matrix
    # Use \\begin{{bmatrix}} ... \\end{{bmatrix}}
    matrix_latex = f"\\begin{{bmatrix}} {a} & {b} \\\\ {c} & {d} \\end{{bmatrix}}"
    
    det = a*d - b*c
    
    question_text = f"求二階行列式的值： $ {matrix_latex} $"
    
    return {
        "question_text": question_text,
        "answer": str(det),
        "correct_answer": str(det),
        "difficulty": 1
    }

def generate_advanced_application():
    """
    Level 2 Example: Word Problem / Geometry
    Demonstrates: Text processing and multi-variable logic.
    """
    # Context: Scientific Notation or Geometry Application
    base = random.randint(100, 999)
    exp = random.randint(5, 9)
    
    # Generating a story context
    question_text = (
        f"已知某星球距離地球約 ${base} \\times 10^{{{exp}}}$ 公里。"
        f"若太空船以每小時 $10^{4}$ 公里的速度飛行，"
        f"大約需要多少小時才能到達？(以科學記號表示，係數保留整數)"
    )
    
    # Logic
    time_val = base * (10**(exp - 4))
    # Formatting result back to sci-notation manually for the answer key
    # (In Phase 4, we will use SymPy here)
    ans_str = f"{base} \\times 10^{{{exp-4}}}"
    
    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str,
        "difficulty": 2
    }

def generate_reverse_logic():
    """
    Level 2 Example: Reverse Engineering (Find x given y)
    Demonstrates: Algebra and Equation solving.
    """
    x = random.randint(1, 10)
    # Equation: 2x + b = c
    b = random.randint(1, 20)
    c = 2 * x + b
    
    question_text = f"已知方程式 $2x + {b} = {c}$，求 $x$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(x),
        "correct_answer": str(x),
        "difficulty": 2
    }

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    Handles float tolerance and string normalization.
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    if user == correct:
        return {"correct": True, "result": "Correct!"}
        
    try:
        if abs(float(user) - float(correct)) < 1e-6:
            return {"correct": True, "result": "Correct!"}
    except:
        pass
        
    return {"correct": False, "result": f"Incorrect. The answer is {correct_answer}."}