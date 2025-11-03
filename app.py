# ==============================================================================
# 1. Imports
# ==============================================================================
import random
import os
import base64
import io
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import google.generativeai as genai
from PIL import Image
import time
import re
import math
from google.api_core.exceptions import ResourceExhausted

# ==============================================================================
# Custom Modules Imports
# ==============================================================================
from core.helpers import *
from skills.remainder import generate_remainder_theorem_question
from skills.factor import generate_factor_theorem_question
from skills.linear_sub import generate_substitution_question
from skills.linear_add import generate_addition_subtraction_question
from skills.inequality_judge import generate_check_point_in_system_question
from skills.inequality_graph import generate_inequality_region_question
from skills.common_logarithm import generate_common_logarithm_question
from skills.linear_equation import generate_linear_equation_question
from skills.circle_equation import generate_circle_equation_question
from skills.circle_line import generate_circle_line_question
from skills.polynomial_division import generate_polynomial_division_question
from skills.quadratic_function import generate_quadratic_function_question
from skills.cubic_function import generate_cubic_function_question
from skills.polynomial_inequality import generate_polynomial_inequality_question
from skills.sequence import generate_sequence_question
from skills.series import generate_series_question
from skills.exponential import generate_exponential_question
from skills.counting_principles import generate_counting_principles_question
from skills.permutations import generate_permutations_question
from skills.combinations import generate_combinations_question
from skills.classical_probability import generate_classical_probability_question
from skills.expected_value import generate_expected_value_question
from skills.data_analysis_1d import generate_data_analysis_1d_question
from skills.data_analysis_2d import generate_data_analysis_2d_question
from skills.trig_ratios_right_triangle import generate_trig_ratios_right_triangle_question
from skills.trig_ratios_general_angle import generate_trig_ratios_general_angle_question
from skills.trig_properties_laws import generate_trig_properties_laws_question
from skills.radian_measure import generate_radian_measure_question
from skills.trig_graphs_periodicity import generate_trig_graphs_periodicity_question
from skills.trig_sum_difference import generate_trig_sum_difference_question
from skills.polar_coordinates import generate_polar_coordinates_question
from skills.trig_sine_cosine_combination import generate_trig_sine_cosine_combination_question
from skills.real_number_system import generate_real_number_system_question
from skills.absolute_value import generate_absolute_value_question
from skills.exponential_functions import generate_exponential_functions_question
from skills.logarithmic_properties import generate_logarithmic_properties_question
from skills.logarithmic_functions import generate_logarithmic_functions_question
from skills.vectors_2d import generate_vectors_2d_question
from skills.vectors_2d_operations import generate_vectors_2d_operations_question
from skills.space_concepts import generate_space_concepts_question
from skills.vectors_3d_coordinates import generate_vectors_3d_coordinates_question
from skills.determinant_3x3 import generate_determinant_3x3_question
from skills.planes_in_space import generate_planes_in_space_question
from skills.vectors_3d_operations import generate_vectors_3d_operations_question
from skills.lines_in_space import generate_lines_in_space_question
from skills.function_properties import generate_function_properties_question
from skills.matrix_applications import generate_matrix_applications_question
from skills.simultaneous_equations_3var import generate_simultaneous_equations_3var_question
from skills.matrix_operations import generate_matrix_operations_question
from skills.ratio_in_plane import generate_ratio_in_plane_question
from skills.coordinate_systems import generate_coordinate_systems_question
from skills.conic_sections import generate_conic_sections_question
from skills.parabola import generate_parabola_question
from skills.ellipse import generate_ellipse_question
from skills.hyperbola import generate_hyperbola_question
from skills.quadratic_curves import generate_quadratic_curves_question
from skills.linear_programming import generate_linear_programming_question
from skills.conditional_probability import generate_conditional_probability_question
from skills.bayes_theorem import generate_bayes_theorem_question
from skills.discrete_random_variables import generate_discrete_random_variables_question
from skills.binomial_geometric_distributions import generate_binomial_geometric_distributions_question
from skills.binomial_distribution import generate_binomial_distribution_question
from skills.complex_roots_polynomials import generate_complex_roots_polynomials_question
from skills.complex_numbers_geometry import generate_complex_numbers_geometry_question
from skills.complex_plane import generate_complex_plane_question
from skills.polynomials_intro import generate_polynomials_intro_question
from skills.sequence_limits_infinite_series import generate_sequence_limits_infinite_series_question
from skills.functions_limits import generate_functions_limits_question
from skills.differentiation import generate_differentiation_question

# ==============================================================================
# 2. App Initialization and Configuration
# ==============================================================================
app = Flask(__name__)
app.secret_key = 'your_api_key'  # ★ 請務必更換成您自己的密鑰 ★
#app.secret_key = 'your_api_key' # ★ 備用的密鑰 ★


# --- Database Configuration ---
# 取得 instance 資料夾的絕對路徑
instance_path = app.instance_path
print(f"資料庫將會被儲存在: {instance_path}") # 加上這行方便您確認

# 確保 instance 資料夾存在
try:
    os.makedirs(instance_path)
except OSError:
    pass # 資料夾已存在

# 明確指定資料庫的完整路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'kumon_math.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# --- Gemini API Configuration ---
try:
    genai.configure(api_key="AIzaSyCCvlrh5-3Y_Ck15cZDJ-R0C3yYN9WTBpw")
    model = genai.GenerativeModel('models/gemini-pro-latest')
except Exception as e:
    print(f"Gemini API 尚未設定或金鑰錯誤: {e}")
    model = None

# ==============================================================================
# 3. Database Models
# ==============================================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    progress = db.relationship('UserProgress', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    main_unit = db.Column(db.String(100), nullable=True) # <-- 新增這行
    # vvvv 確保您已經加上這兩行 vvvv
    school_type = db.Column(db.String(20), nullable=True, default='共同')
    grade_level = db.Column(db.String(20), nullable=True, default='國中')
    generator_key = db.Column(db.String(100), nullable=True, index=True)
    # ^^^^ 確保您已經加上這兩行 ^^^^

    # ... (Skill 模型裡的其他欄位) ...

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    consecutive_correct = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    total_attempted = db.Column(db.Integer, default=0)
    consecutive_incorrect = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc'),)

class SkillDependency(db.Model):
    """ 用來儲存技能依賴關係 (知識圖譜) 的模型 """
    id = db.Column(db.Integer, primary_key=True)

    # '先備知識' 的 ID
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    # '目標技能' 的 ID
    target_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)

    # 建立關係，讓我們可以方便地查詢
    prerequisite = db.relationship('Skill', foreign_keys=[prerequisite_id], backref='leading_to')
    target = db.relationship('Skill', foreign_keys=[target_id], backref='requires')

    # 確保同一個依賴關係不會重複
    db.UniqueConstraint('prerequisite_id', 'target_id', name='unique_dependency')

    def __repr__(self):
        return f'<Dependency: {self.prerequisite.display_name} -> {self.target.display_name}>'

# ^^^^ 程式碼加到這裡為止 ^^^^



# ==============================================================================
# 6. Skill Engine Definition
# ==============================================================================
SKILL_ENGINE = {
    # Logarithms & Exponents
    'logarithms': {
        'generator': generate_common_logarithm_question,
        'display_name': '常用對數',
        'description': '計算常用對數。'
    },
    'exponents': {
        'generator': generate_exponential_question,
        'display_name': '指數',
        'description': '計算指數運算。'
    },
    'common_logarithms': {
        'generator': generate_common_logarithm_question,
        'display_name': '常用對數',
        'description': '計算常用對數。'
    },
    'exponential_functions': { 'generator': generate_exponential_functions_question, 'display_name': '指數函數', 'description': '練習解指數方程式。' },
    'logarithmic_properties': {
        'generator': generate_logarithmic_properties_question,
        'display_name': '對數與對數律 / 對數',
        'description': '練習對數律的應用。'
    },
    'logarithmic_functions': { 'generator': generate_logarithmic_functions_question, 'display_name': '對數函數', 'description': '練習解對數方程式。' },

    # Linear Algebra & Equations
    'linear_equations': {
        'generator': generate_linear_equation_question,
        'display_name': '直線方程式',
        'description': '練習直線方程式。'
    },
    'simultaneous_equations_1or2var': {
        'generator': generate_addition_subtraction_question,
        'display_name': '一/二元一次聯立方程式',
        'description': '練習二元一次聯立方程式的加減消去法。'
    },
    'simultaneous_equations_3var': {
        'generator': generate_addition_subtraction_question,
        'display_name': '三元一次聯立方程式',
        'description': '練習二元一次聯立方程式(暫代)。'
    },
    'linear_programming': {
        'generator': generate_inequality_region_question,
        'display_name': '線性規劃',
        'description': '練習二元一次不等式圖解區域。'
    },

    # Geometry
    'circle_equations': {
        'generator': generate_circle_equation_question,
        'display_name': '圓方程式',
        'description': '練習圓的方程式。'
    },
    'circle_line_relations': {
        'generator': generate_circle_line_question,
        'display_name': '圓與直線',
        'description': '練習圓與直線的關係。'
    },

    # Polynomials
    'polynomial_division': {
        'generator': generate_polynomial_division_question,
        'display_name': '多項式的除法原理',
        'description': '練習多項式除法、餘式與因式定理。'
    },
    'quadratic_functions': {
        'generator': generate_factor_theorem_question,
        'display_name': '一次與二次函數',
        'description': '練習判斷因式。'
    },
    'cubic_functions_graph': {
        'generator': generate_factor_theorem_question,
        'display_name': '三次函數的圖形特徵',
        'description': '練習判斷因式。'
    },
    'polynomial_inequalities': {
        'generator': generate_inequality_region_question,
        'display_name': '多項式不等式',
        'description': '練習不等式相關問題。'
    },
    

    # Placeholder Mappings (using default generators)
    'sequences_recursion': { 'generator': generate_sequence_question, 'display_name': '數列與遞迴關係', 'description': '練習等差數列。' },
    'series': { 'generator': generate_series_question, 'display_name': '級數', 'description': '練習等差級數求和。' },
    'counting_principles': { 'generator': generate_counting_principles_question, 'display_name': '計數原理', 'description': '練習計數的乘法原理。' },
    'permutations': { 'generator': generate_permutations_question, 'display_name': '排列', 'description': '練習排列 P(n,k)。' },
    'combinations': { 'generator': generate_combinations_question, 'display_name': '組合', 'description': '練習組合 C(n,k)。' },
    'classical_probability': { 'generator': generate_classical_probability_question, 'display_name': '古典機率', 'description': '練習基本的機率問題。' },
    'expected_value': { 'generator': generate_expected_value_question, 'display_name': '數學期望值', 'description': '練習計算期望值。' },
    'data_analysis_1d': { 'generator': generate_data_analysis_1d_question, 'display_name': '一維數據分析', 'description': '練習計算平均數、中位數或眾數。' },
    'data_analysis_2d': { 'generator': generate_data_analysis_2d_question, 'display_name': '二維數據分析', 'description': '練習計算二維數據的中心點。' },
    'trig_ratios_right_triangle': { 'generator': generate_trig_ratios_right_triangle_question, 'display_name': '直角三角形的三角比', 'description': '練習計算三角比。' },
    'trig_ratios_general_angle': { 'generator': generate_trig_ratios_general_angle_question, 'display_name': '廣義角三角比', 'description': '練習計算廣義角的三角比。' },
    'polar_coordinates': { 'generator': generate_polar_coordinates_question, 'display_name': '與極坐標', 'description': '練習極座標與直角座標的轉換。' },
    'trig_properties_laws': { 'generator': generate_trig_properties_laws_question, 'display_name': '三角比的性質', 'description': '練習正弦與餘弦定理。' },
    'radian_measure': { 'generator': generate_radian_measure_question, 'display_name': '弧度量', 'description': '練習角度與弧度的換算。' },
    'trig_graphs_periodicity': { 'generator': generate_trig_graphs_periodicity_question, 'display_name': '三角函數的圖形 / 週期性', 'description': '練習三角函數的週期。' },
    'trig_sum_difference': { 'generator': generate_trig_sum_difference_question, 'display_name': '三角的和差角公式', 'description': '練習和差角公式的觀念。' },
    'trig_sine_cosine_combination': { 'generator': generate_trig_sine_cosine_combination_question, 'display_name': '正餘弦的疊合', 'description': '練習疊合後求最大最小值。' },
    'real_number_system': { 'generator': generate_real_number_system_question, 'display_name': '數', 'description': '練習判斷有理數與無理數。' },
    'absolute_value': { 'generator': generate_absolute_value_question, 'display_name': '絕對值', 'description': '練習絕對值的基本運算。' },
    'vectors_2d': { 'generator': generate_vectors_2d_question, 'display_name': '平面向量', 'description': '練習向量的分量。' },
    'vectors_2d_operations': { 'generator': generate_vectors_2d_operations_question, 'display_name': '平面向量的運算', 'description': '練習向量的加減法。' },
    'space_concepts': { 'generator': generate_space_concepts_question, 'display_name': '空間概念', 'description': '練習點到平面的距離。' },
    'vectors_3d_coordinates': { 'generator': generate_vectors_3d_coordinates_question, 'display_name': '空間向量的坐標表示法', 'description': '練習空間向量的分量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'vectors_3d_operations': { 'generator': generate_vectors_3d_operations_question, 'display_name': '空間向量的運算', 'description': '練習空間向量的加減法。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'determinant_3x3': { 'generator': generate_determinant_3x3_question, 'display_name': '三階行列式', 'description': '練習計算三階行列式的值。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'planes_in_space': { 'generator': generate_planes_in_space_question, 'display_name': '空間中的平面', 'description': '練習求平面的法向量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'lines_in_space': { 'generator': generate_lines_in_space_question, 'display_name': '空間中的直線', 'description': '練習求直線的方向向量。', 'grade_level': '十一年級', 'main_unit': '向量與空間' },
    'function_properties': { 'generator': generate_function_properties_question, 'display_name': '函數性質的判定', 'description': '練習判斷函數的奇偶性。', 'grade_level': '十一年級', 'main_unit': '(微積分/極限)' },
    'matrix_applications': { 'generator': generate_matrix_applications_question, 'display_name': '矩陣的應用', 'description': '練習矩陣乘法。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'matrix_operations': { 'generator': generate_matrix_operations_question, 'display_name': '矩陣的運算', 'description': '練習矩陣加法。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'simultaneous_equations_3var': { 'generator': generate_simultaneous_equations_3var_question, 'display_name': '三元一次聯立方程式', 'description': '練習解三元一次聯立方程式。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    
    'function_properties': { 'generator': generate_remainder_theorem_question, 'display_name': '函數性質的判定', 'description': 'Placeholder' },
    
    
    'ratio_in_plane': { 'generator': generate_ratio_in_plane_question, 'display_name': '平面上的比例', 'description': '練習分點公式。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'coordinate_systems': { 'generator': generate_coordinate_systems_question, 'display_name': '坐標系', 'description': '練習直角坐標與極坐標轉換。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'conic_sections': { 'generator': generate_conic_sections_question, 'display_name': '圓錐曲線', 'description': '練習判斷圓錐曲線類型。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'parabola': { 'generator': generate_parabola_question, 'display_name': '拋物線', 'description': '練習求拋物線頂點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'ellipse': { 'generator': generate_ellipse_question, 'display_name': '橢圓', 'description': '練習求橢圓中心點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'hyperbola': { 'generator': generate_hyperbola_question, 'display_name': '雙曲線', 'description': '練習求雙曲線中心點。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'quadratic_curves': { 'generator': generate_quadratic_curves_question, 'display_name': '二次曲線', 'description': '練習判斷二次曲線類型。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'linear_programming': { 'generator': generate_linear_programming_question, 'display_name': '線性規劃', 'description': '練習判斷點是否滿足不等式組。', 'grade_level': '十二年級', 'main_unit': '向量與空間' },
    'conditional_probability': { 'generator': generate_conditional_probability_question, 'display_name': '條件機率', 'description': '練習計算條件機率。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'bayes_theorem': { 'generator': generate_bayes_theorem_question, 'display_name': '貝氏定理', 'description': '練習貝氏定理的應用。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'discrete_random_variables': { 'generator': generate_discrete_random_variables_question, 'display_name': '離散型隨機變數', 'description': '練習計算離散型隨機變數的期望值。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'binomial_geometric_distributions': { 'generator': generate_binomial_geometric_distributions_question, 'display_name': '二項分布與幾何分布', 'description': '練習判斷二項分布與幾何分布。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'binomial_distribution': { 'generator': generate_binomial_distribution_question, 'display_name': '二項分布', 'description': '練習計算二項分布機率。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    'complex_roots_polynomials': { 'generator': generate_complex_roots_polynomials_question, 'display_name': '複數與多項式方程式的根', 'description': '練習共軛複數根定理。', 'grade_level': '十二年級', 'main_unit': '排組機統' },
    
    
    
    
    
    'integration': { 'generator': generate_remainder_theorem_question, 'display_name': '積分', 'description': 'Placeholder' },
    'integration_applications': { 'generator': generate_remainder_theorem_question, 'display_name': '積分的應用', 'description': 'Placeholder' },

    # Original 6 skills (now mapped to user's keys)
    'remainder-theorem': { 'generator': generate_remainder_theorem_question, 'display_name': '餘式定理', 'description': '練習 f(x) 除以 (x-k) 的餘式。' },
    'factor-theorem': { 'generator': generate_factor_theorem_question, 'display_name': '因式定理', 'description': '判斷 (x-k) 是否為 f(x) 的因式。' },
    'linear-eq-substitution': { 'generator': generate_substitution_question, 'display_name': '二元一次 (帶入消去法)', 'description': '練習 y=ax+b 形式的帶入消去。' },
    'linear-eq-addition': { 'generator': generate_addition_subtraction_question, 'display_name': '二元一次 (加減消去法)', 'description': '練習係數需乘以倍數的加減消去。' },
    'linear-ineq-region': { 'generator': generate_inequality_region_question, 'display_name': '二元一次不等式 (圖解區域)', 'description': '在數位計算紙上畫出不等式的解區域。' },
    'linear-ineq-check-point': { 'generator': generate_check_point_in_system_question, 'display_name': '二元一次不等式 (判斷解)', 'description': '判斷一個點是否為不等式系統的解。' }
}

DEMOTION_THRESHOLD = 3  # 連續答錯 3 題就降級

def initialize_skills():
    """同步 SKILL_ENGINE 到資料庫 (包含先備知識)"""
    print("正在同步技能到資料庫...")
    for skill_id, skill_data_in_code in SKILL_ENGINE.items():
        skill_in_db = Skill.query.filter_by(name=skill_id).first()
        needs_update = False
        if skill_in_db:
            # 比較並更新現有技能
            if skill_in_db.display_name != skill_data_in_code['display_name']:
                skill_in_db.display_name = skill_data_in_code['display_name']
                needs_update = True
            if 'description' in skill_data_in_code and skill_in_db.description != skill_data_in_code['description']:
                skill_in_db.description = skill_data_in_code['description']
                needs_update = True
            if 'grade_level' in skill_data_in_code and skill_in_db.grade_level != skill_data_in_code['grade_level']:
                skill_in_db.grade_level = skill_data_in_code['grade_level']
                needs_update = True
            if 'main_unit' in skill_data_in_code and skill_in_db.main_unit != skill_data_in_code['main_unit']:
                skill_in_db.main_unit = skill_data_in_code['main_unit']
                needs_update = True
            # if skill_in_db.prerequisite_skill_id != skill_data_in_code.get('prerequisite_skill_id'):
            #     skill_in_db.prerequisite_skill_id = skill_data_in_code.get('prerequisite_skill_id')
            #     needs_update = True
            if needs_update:
                db.session.commit()
                print(f"更新技能 {skill_id} 到資料庫")
        else:
            # 創建新技能
            new_skill = Skill(
                name=skill_id,
                display_name=skill_data_in_code['display_name'],
                description=skill_data_in_code.get('description', '無描述'),
                grade_level=skill_data_in_code.get('grade_level'),
                main_unit=skill_data_in_code.get('main_unit')
            )
            db.session.add(new_skill)
            db.session.commit()
            print(f"添加新技能 {skill_id} 到資料庫")

DEMOTION_THRESHOLD = 3  # 連續答錯 3 題就降級

def initialize_skills():
    """同步 SKILL_ENGINE 到資料庫 (包含先備知識)"""
    print("正在同步技能到資料庫...")
    for skill_id, skill_data_in_code in SKILL_ENGINE.items():
        skill_in_db = Skill.query.filter_by(name=skill_id).first()
        needs_update = False
        if skill_in_db:
            # 比較並更新現有技能
            if skill_in_db.display_name != skill_data_in_code['display_name']:
                skill_in_db.display_name = skill_data_in_code['display_name']
                needs_update = True
            if 'description' in skill_data_in_code and skill_in_db.description != skill_data_in_code['description']:
                skill_in_db.description = skill_data_in_code['description']
                needs_update = True
            if 'grade_level' in skill_data_in_code and skill_in_db.grade_level != skill_data_in_code['grade_level']:
                skill_in_db.grade_level = skill_data_in_code['grade_level']
                needs_update = True
            if 'main_unit' in skill_data_in_code and skill_in_db.main_unit != skill_data_in_code['main_unit']:
                skill_in_db.main_unit = skill_data_in_code['main_unit']
                needs_update = True
            # if skill_in_db.prerequisite_skill_id != skill_data_in_code.get('prerequisite_skill_id'):
            #     skill_in_db.prerequisite_skill_id = skill_data_in_code.get('prerequisite_skill_id')
            #     needs_update = True
            if needs_update:
                db.session.commit()
                print(f"更新技能 {skill_id} 到資料庫")
        else:
            # 創建新技能
            new_skill = Skill(
                name=skill_id,
                display_name=skill_data_in_code['display_name'],
                description=skill_data_in_code.get('description', '無描述'),
                grade_level=skill_data_in_code.get('grade_level'),
                main_unit=skill_data_in_code.get('main_unit')
            )
            db.session.add(new_skill)
            db.session.commit()
            print(f"添加新技能 {skill_id} 到資料庫")

# ==============================================================================
# 7. Routes (View Functions)
# ==============================================================================

# --- Authentication Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("帳號或密碼不可為空", "warning")
            return redirect(url_for('register'))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("這個帳號名稱已經有人用了！", "warning")
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("註冊成功！請登入。", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("帳號或密碼不可為空", "danger")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"歡迎回來，{user.username}！", "success")
            return redirect(url_for('home'))
        else:
            flash("帳號或密碼錯誤。", "danger")
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("您已成功登出。", "info")
    return redirect(url_for('login'))

@app.route('/upload_image_problem', methods=['POST'])
def upload_image_problem():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first.'}), 401
    if not model: # Changed from vision_model
        return jsonify({'error': 'Model is not configured.'}), 500

    if 'problem_image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    image_file = request.files['problem_image']
    question_number = request.form.get('question_number') # Get the question number
    
    if image_file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    try:
        img = Image.open(image_file.stream)
        
        # Modify prompt based on whether a question number was provided
        if question_number:
            prompt = f"這是一張數學題目的圖片。請只專注於題號為 '{question_number}' 的題目，並僅辨識其文字內容。如果圖片中找不到該題號，請辨識圖片中的所有文字。"
        else:
            prompt = "辨識這張圖片中的數學題目文字。"

        prompt_parts = [prompt, img]
        
        response = model.generate_content(prompt_parts) # Changed from vision_model
        recognized_text = response.text

        session['custom_question_text'] = recognized_text
        
        redirect_url = url_for('practice', skill_id='custom')

        return jsonify({'redirect_url': redirect_url})

    except Exception as e:
        print(f"Error during image recognition: {e}")
        return jsonify({'error': f'An error occurred during recognition: {str(e)}'}), 500

# --- Core Application Routes ---
@app.route("/")
def home():
    if 'user_id' not in session:
        flash("請先登入！", "warning")
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# ( ... dashboard 函式的正下方 ... )

@app.route('/grade/<grade_name>')
def show_grade(grade_name):
    """ 
    [新頁面] 顯示特定年級的所有「大單元」 
    例如： /grade/十年級
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 查詢該年級下所有不重複的「大單元」
    try:
        units_query = db.session.query(Skill.main_unit).filter(Skill.grade_level == grade_name).distinct().all()
        main_units = [u[0] for u in units_query if u[0] is not None]
    except Exception as e:
        print(f"查詢 {grade_name} 的大單元時出錯: {e}")
        main_units = []
        flash("讀取單元時發生錯誤。", "warning")

    # 我們會建立一個新的 HTML 模板來顯示
    return render_template('grade_view.html', 
                           grade_name=grade_name, 
                           main_units=main_units)

# (請找到您 app.py 中現有的 dashboard 函式...)
@app.route('/dashboard')
def dashboard():
    """ 儀表板 - 現在改為顯示所有「年級」 """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        flash("找不到用戶資料，請重新登入。", "warning")
        return redirect(url_for('login'))

    # 從 Skill 表中查詢所有不重複的「年級」
    try:
        # 查詢所有不重複的 grade_level
        grades_query = db.session.query(Skill.grade_level).distinct().all()
        
        # 將 [( '十年級',), ('十一年級',)] 轉成 ['十年級', '十一年級']
        grades = [g[0] for g in grades_query if g[0] is not None]
        
        # 這裡可以手動排序 (如果您的年級不是照順序)
        # 例如： grades.sort(key=lambda g: 10 if '十' in g else (11 if '十一' in g else 12))
        
    except Exception as e:
        print(f"查詢年級時出錯: {e}")
        grades = []
        flash("讀取課綱時發生錯誤，請稍後再試。", "warning")

    # 注意：我們傳送的變數改為 grades
    return render_template('dashboard.html', 
                           username=user.username, 
                           grades=grades) 
# ( ... 取代到這裡為止 ... )
# ( ... dashboard 函式的正下方 ... )

# ( ... 找到您 app.py 中的 show_unit ... )
@app.route('/unit/<grade_name>/<path:main_unit_name>')
def show_unit(grade_name, main_unit_name):
    """ 
    [新頁面] 顯示特定大單元的所有「小單元」 (包含使用者進度)
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # 查詢該大單元下所有的「小單元」(即 Skills)
    try:
        sub_units_query = Skill.query.filter(Skill.main_unit == main_unit_name).order_by(Skill.id).all()
        
        # --- vvv 這就是我們加回來的「進度查詢」邏輯 vvv ---
        
        # 1. 取得這個用戶的所有進度
        user_progresses = UserProgress.query.filter_by(user_id=user_id).all()
        # 2. 轉成字典方便查詢 { skill_id: progress_object }
        progress_map = {p.skill_id: p for p in user_progresses}
        
        # 3. 建立要傳到前端的資料包
        sub_units_data = []
        for skill in sub_units_query:
            progress = progress_map.get(skill.id)
            sub_units_data.append({
                'skill': skill,
                'consecutive_correct': progress.consecutive_correct if progress else 0,
                'total_attempted': progress.total_attempted if progress else 0
            })
        # --- ^^^ 進度查詢邏輯結束 ^^^ ---

    except Exception as e:
        print(f"查詢 {main_unit_name} 的小單元時出錯: {e}")
        sub_units_data = []
        flash("讀取小單元時發生錯誤。", "warning")
        
    # 從第一個小單元反查年級，用來顯示麵包屑導覽
    # current_grade = sub_units_query[0].grade_level if sub_units_query else "..."

    # 我們會建立第二個新的 HTML 模板來顯示
    return render_template('unit_view.html',
                           grade_name=grade_name,
                           main_unit_name=main_unit_name,
                           sub_units_data=sub_units_data) # <--- 注意，變數名稱改了
# ( ... 取代到這裡為止 ... )

@app.route("/practice/<string:skill_id>")
def practice(skill_id):
    if 'user_id' not in session:
        flash("請先登入！", "warning")
        return redirect(url_for('login'))

    question_data = {}
    skill_display_name = ""

    if skill_id == 'custom':
        question_text = session.get('custom_question_text')
        if not question_text:
            flash("找不到自訂題目，請重新上傳。", "warning")
            return redirect(url_for('dashboard'))
        
        question_data = {
            'text': question_text,
            'answer': None,
            'inequality_string': None,
            'validation_function_name': None
        }
        skill_display_name = "自訂題目"
        print(f"(custom) 新題目: {question_text}")

    else:
        skill = Skill.query.filter_by(name=skill_id).first()
        if not skill or skill_id not in SKILL_ENGINE:
            flash("找不到指定的練習單元。", "danger")
            return redirect(url_for('dashboard'))
        
        question_data = SKILL_ENGINE[skill_id]['generator']()
        skill_display_name = skill.display_name
        print(f"({skill_id}) 新題目: {question_data.get('text')} (答案: {question_data.get('answer')})")

    session['current_skill_id'] = skill_id
    session['current_question_text'] = question_data.get('text')
    session['current_answer'] = question_data.get('answer')
    session['current_inequality_string'] = question_data.get('inequality_string')
    session['validation_function_name'] = question_data.get('validation_function_name')
    
    return render_template('index.html',
                           question_text=question_data.get('text'),
                           inequality_string=question_data.get('inequality_string') or '',
                           username=session.get('username'),
                           skill_display_name=skill_display_name)

# --- API Endpoints ---
@app.route("/get_next_question", methods=["GET"])
def get_next_question():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    skill_id = session.get('current_skill_id')
    if not skill_id or skill_id not in SKILL_ENGINE:
        return jsonify({"error": "Skill error"}), 400
        
    generator_func = SKILL_ENGINE[skill_id]['generator']
    question_data = generator_func()
    
    session['current_answer'] = question_data.get('answer')
    session['current_question_text'] = question_data.get('text')
    session['current_inequality_string'] = question_data.get('inequality_string')
    session['validation_function_name'] = question_data.get('validation_function_name')
    
    print(f"({skill_id}) 下一題: {question_data.get('text')} (答案: {question_data.get('answer')})")

    return jsonify({
        "new_question_text": question_data.get('text'),
        "inequality_string": question_data.get('inequality_string')
    })

@app.route("/check_answer", methods=["POST"])
def check_answer():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    if not data or 'answer' not in data:
        return jsonify({"error": "Missing JSON data or 'answer'"}), 400
        
    user_answer = data.get('answer')
    skill_id_str = session.get('current_skill_id')
    correct_answer = session.get('current_answer')
    validation_func_name = session.get('validation_function_name')
    if not skill_id_str:
        return jsonify({"error": "Session missing skill_id"}), 400
    
    is_correct = False
    result_message = ""
    validation_func = globals().get(validation_func_name) if validation_func_name else None
    
    if validation_func:
        try:
            is_correct = validation_func(user_answer, correct_answer)
            result_message = "答對了！" if is_correct else "答錯了..."
        except Exception as e:
            print(f"Validation function error: {e}")
            is_correct = False
            result_message = "答案格式錯誤"
    else:
        is_correct = (str(user_answer).strip().lower() == str(correct_answer).strip().lower())
        result_message = "答對了！" if is_correct else "答錯了..."
    
    demote_to_skill_id = None
    promote_to_skill_id = None # [新功能] 初始化晉級變數

    try:
        user_id = session['user_id']
        skill = Skill.query.filter_by(name=skill_id_str).first()
        if skill:
            progress = UserProgress.query.filter_by(user_id=user_id, skill_id=skill.id).first()
            if not progress:
                progress = UserProgress(user_id=user_id, skill_id=skill.id)
                db.session.add(progress)

            # [修復] 處理資料庫中可能存在的 NULL 值，確保計數器為整數
            if progress.total_attempted is None:
                progress.total_attempted = 0
            if progress.consecutive_correct is None:
                progress.consecutive_correct = 0
            if progress.total_correct is None:
                progress.total_correct = 0
            if progress.consecutive_incorrect is None:
                progress.consecutive_incorrect = 0
            
            progress.total_attempted += 1
            if is_correct:
                progress.consecutive_correct += 1
                progress.total_correct += 1
                progress.consecutive_incorrect = 0

                # [新功能] 檢查是否達到晉級門檻
                PROMOTION_THRESHOLD = 5
                if progress.consecutive_correct >= PROMOTION_THRESHOLD:
                    # 查詢下一個技能 (以當前技能為先備的目標技能)
                    dependency = SkillDependency.query.filter_by(prerequisite_id=skill.id).first()
                    if dependency and dependency.target:
                        promote_to_skill_id = dependency.target.name
                        result_message = f"恭喜！您已掌握「{skill.display_name}」，即將前進到下一個單元！"
                        # 重置當前技能的連續答對次數，以便下次重新計算
                        progress.consecutive_correct = 0
            else:
                progress.consecutive_correct = 0
                progress.consecutive_incorrect += 1
                # [新邏輯] 當達到連續答錯門檻時，查詢 SkillDependency 表
                if progress.consecutive_incorrect >= DEMOTION_THRESHOLD:
                    dependency = SkillDependency.query.filter_by(target_id=skill.id).first()
                    
                    # 如果在依賴關係表中找到了先備技能
                    if dependency and dependency.prerequisite:
                        # 取得先備技能的資訊
                        prereq_skill = dependency.prerequisite
                        demote_to_skill_id = prereq_skill.name  # 前端需要 skill 的 name/id
                        prereq_name = prereq_skill.display_name
                        
                        # 準備要顯示給使用者的訊息
                        result_message = f"您在「{skill.display_name}」單元連續答錯 {progress.consecutive_incorrect} 題了.\n系統建議您先回去複習「{prereq_name}」！"
                        
                        # 重置連續答錯計數器
                        progress.consecutive_incorrect = 0
                    # 如果沒有找到依賴關係，則不會觸發降級，只會顯示標準的答錯訊息
            db.session.commit()
            # [DEBUG] Print progress after commit
            print(f"[DEBUG] Skill: {skill.name}, Correct: {is_correct}, New Consecutive Correct: {progress.consecutive_correct}")
        else:
            print(f"Warning: Skill '{skill_id_str}' not found.")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating progress: {e}")
    
    return jsonify({
        "result": result_message,
        "correct": is_correct,
        "demote_to_skill_id": demote_to_skill_id,
        "promote_to_skill_id": promote_to_skill_id
    })

@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    if 'user_id' not in session:
        return jsonify({"reply": "Not logged in"}), 401
    if model is None:
        return jsonify({"reply": "AI 助教尚未設定。"}), 500
    data = request.get_json()
    if not data or not data.get('prompt') or not data.get('current_question'):
        return jsonify({"reply": "錯誤：缺少提示或題目內容。"}), 400
         
    user_prompt = data.get('prompt')
    current_question = data.get('current_question')
    current_skill_id = session.get('current_skill_id', 'unknown')
    current_skill_display_name = SKILL_ENGINE.get(current_skill_id, {}).get('display_name', '數學')
    
    system_instruction = f"""
        你是一位專業且有耐心的高中數學家教，專門輔導資源班的學生。
        學生的目標是段考及格。請用繁體中文回答。
        
        你的任務：
        1.  **角色扮演**：你是一位友善的 AI 助教。
        2.  **教學重點**：學生目前正在練習「{current_skill_display_name}」。
        3.  **當前題目**：學生正在看的題目是「{current_question}」。
        4.  **回答限制**：
            * **不要直接給答案！** 這是最重要的規則。
            * 如果學生問「這題答案是什麼？」，你應該反問他：「你覺得第一步該怎麼做呢？」或「你記得{current_skill_display_name}的定義嗎？」。
            * 如果學生問「詳解」，請提供「解題步驟」和「思路引導」，而不是只給計算過程。
            * 如果學生問觀念（例如「什麼是{current_skill_display_name}？」），請用最簡單、最白話的方式解釋。
    
        學生的問題是：「{user_prompt}」
        請根據上述規則，提供你的回答：
        """
    try:
        response = model.generate_content(system_instruction)
        ai_reply = response.text
    except Exception as e:
        print(f"Gemini API 呼叫失敗: {e}")
        ai_reply = "抱歉，助教現在有點忙... 請稍後再試。"
    return jsonify({"reply": ai_reply})

@app.route("/analyze_handwriting", methods=["POST"])
def analyze_handwriting():
    if 'user_id' not in session:
        return jsonify({"reply": "Not logged in"}), 401
    if model is None:
        return jsonify({"reply": "AI 助教尚未設定。"}), 500

    # --- 獲取 Session 中的情境 ---
    user_id = session.get('user_id')
    current_skill_id_str = session.get('current_skill_id', 'unknown')
    current_question = session.get('current_question_text', '未知題目')
    current_answer = session.get('current_answer')  # 可能是 None
    current_inequality_string = session.get('current_inequality_string')  # 可能是 None
    current_skill_display_name = SKILL_ENGINE.get(current_skill_id_str, {}).get('display_name', '數學')
    
    # --- 獲取前端傳來的資料 ---
    data = request.get_json()
    if not data:
        return jsonify({"reply": "錯誤：未收到 JSON 資料。"}), 400
    image_data_url = data.get('image_data_url')
    
    if not image_data_url:
        print("錯誤: 前端未發送 image_data_url")
        return jsonify({"reply": "錯誤：缺少圖片資料。"}), 400

    try:
        # 2. 轉換圖片
        header, encoded = image_data_url.split(",", 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data))

        # 3. 根據 current_inequality_string 是否存在，決定提示詞
        prompt_parts = []
        is_graph_question = bool(current_inequality_string)

        if is_graph_question:
            # --- 提示詞：畫圖題 (二元一次不等式) ---
            print(f"收到畫圖題分析請求: {current_inequality_string}")
            prompt_parts = [
                f"""你是一位專業且有耐心的數學家教，專門輔導高中資源班學生，目標是讓學生段考及格。
                請用繁體中文回答。學生正在練習「{current_skill_display_name}」單元，題目是：
                「{current_question}」
                學生提交了一張手繪圖片（已提供），請根據以下要求分析：
                - 題目要求學生在數位計算紙上畫出二元一次不等式 {current_inequality_string} 的解區域。
                - 檢查學生繪製的直線和陰影區域是否正確。
                - 如果正確，回覆格式為：「CORRECT: 畫得很好！解區域完全正確。」
                - 如果錯誤，回覆格式為：「INCORRECT: 錯誤的地方在...（具體說明，例如直線位置或陰影方向錯誤）」
                - 避免使用「請」或「請問」，直接給出結論。
                - 回覆中，如果是「INCORRECT」，請確保第一行是「INCORRECT: 錯誤的地方在...」，後續提供詳細解釋。
                以下是學生的手繪圖片：""",
                image
            ]
        else:
            # --- 提示詞：計算題 (通用) ---
            prompt_parts = [
                f"""你是一位專業且有耐心的數學家教，專門輔導高中資源班學生，目標是讓學生段考及格。
                請用繁體中文回答。學生正在練習「{current_skill_display_name}」單元，題目是：
                「{current_question}」
                學生提交了一張手寫計算過程的圖片（已提供），請根據以下要求分析：
                - 檢查計算過程是否正確。
                - 如果正確，回覆格式為：「CORRECT: 計算正確！」
                - 如果錯誤，回覆格式為：「INCORRECT: 錯誤的地方在...（具體說明，例如某一步計算錯誤）」
                - 避免使用「請」或「請問」，直接給出結論。
                以下是學生的手寫計算過程：""",
                image
            ]

        # 4. 呼叫 Gemini API (加入重試機制處理配額限制)
        ai_reply = ""
        max_retries = 3
        for i in range(max_retries):
            try:
                response = model.generate_content(prompt_parts)
                ai_reply = response.text.strip()
                break # 成功則跳出迴圈
            except ResourceExhausted as e:
                print(f"Gemini API 配額超出，正在重試 ({i+1}/{max_retries})...")
                retry_seconds = 60 # Default retry time
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                if match:
                    retry_seconds = float(match.group(1))
                print(f"等待 {retry_seconds + 1} 秒後重試。")
                time.sleep(retry_seconds + 1) # 等待建議時間 + 1 秒
            except Exception as e:
                raise e # 其他錯誤直接拋出

        if not ai_reply:
            raise Exception("Gemini API 呼叫失敗，即使重試也未能成功。")

        # 5. 解讀 AI 回覆並判斷對錯 (只對畫圖題更新進度)
        is_graph_correct = False
        demote_to_skill_id = None  # 初始化 demote_to_skill_id
        short_feedback = ai_reply.split('\n')[0] if ai_reply else "分析錯誤"
        detailed_feedback = ai_reply if ai_reply else "分析失敗，請重試。"

        if is_graph_question:
            if ai_reply.startswith("CORRECT:"):
                is_graph_correct = True
            elif ai_reply.startswith("INCORRECT:"):
                is_graph_correct = False
                # 確保 detailed_feedback 包含完整回覆
                detailed_feedback = ai_reply
            else:
                is_graph_correct = False
                short_feedback = f"AI 回覆格式錯誤...\n({ai_reply})"
                detailed_feedback = short_feedback

            # --- 更新資料庫進度 (只針對畫圖題) ---
            try:
                skill = Skill.query.filter_by(name=current_skill_id_str).first()
                if skill and user_id:
                    progress = UserProgress.query.filter_by(user_id=user_id, skill_id=skill.id).first()
                    if not progress:
                        progress = UserProgress(user_id=user_id, skill_id=skill.id)
                        db.session.add(progress)
                    progress.total_attempted += 1
                    if is_graph_correct:
                        progress.consecutive_correct += 1
                        progress.total_correct += 1
                        progress.consecutive_incorrect = 0
                    else:
                        progress.consecutive_correct = 0
                        progress.consecutive_incorrect += 1
                        if progress.consecutive_incorrect >= DEMOTION_THRESHOLD and skill.prerequisite_skill_id:
                            demote_to_skill_id = skill.prerequisite_skill_id
                            prereq_skill = Skill.query.filter_by(name=demote_to_skill_id).first()
                            prereq_name = prereq_skill.display_name if prereq_skill else "基礎單元"
                            detailed_feedback += f"\n\n錯誤次數較多，建議您先複習「{prereq_name}」。"
                    db.session.commit()
                    print(f"畫圖題進度已更新: correct={is_graph_correct}, demote={demote_to_skill_id}")
                else:
                    print("警告: 找不到技能或用戶，無法更新畫圖題進度")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating progress: {e}")

    except Exception as e:
        print(f"Gemini API 或圖片處理失敗: {e}")
        is_graph_correct = False
        demote_to_skill_id = None  # 確保在異常情況下也有預設值
        short_feedback = f"分析失敗：{str(e)[:100]}... 請檢查圖片或稍後再試。"
        detailed_feedback = short_feedback

    # 7. 回傳結果給前端
    print(f"回傳給前端: short_feedback='{short_feedback}', detailed_feedback='{detailed_feedback}', is_graph_correct={is_graph_correct}, demote={demote_to_skill_id}")
    return jsonify({
        "short_feedback": short_feedback,  # 左邊紅色區塊顯示
        "reply": detailed_feedback,        # 右邊對話框顯示
        "is_graph_correct": is_graph_correct,
        "demote_to_skill_id": demote_to_skill_id
    })

# ==============================================================================
# 8. Application Runner
# ==============================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 確保所有資料表都建立
        initialize_skills()  # 同步技能列表
    print("Starting Flask app...")
    app.run(debug=True)