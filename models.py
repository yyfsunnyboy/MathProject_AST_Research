# models.py
import sqlite3
from flask_login import UserMixin

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. 建立 users 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            streak INTEGER DEFAULT 0
        )
    ''')

    # 2. 建立 progress 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            skill_id TEXT,
            consecutive_correct INTEGER DEFAULT 0,
            total_correct INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            questions_solved INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, skill_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 3. 安全新增欄位（如果不存在才加）
    def add_column_if_not_exists(table, column, definition):
        c.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in c.fetchall()]
        if column not in columns:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # 為 progress 表新增欄位（安全）
    add_column_if_not_exists('progress', 'current_level', 'INTEGER DEFAULT 1')
    add_column_if_not_exists('progress', 'questions_solved', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('progress', 'consecutive_correct', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('progress', 'total_correct', 'INTEGER DEFAULT 0')

    # 4. 建立 skills_info 表（您的功文式設計）
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills_info (
            skill_id TEXT PRIMARY KEY,
            skill_en_name TEXT NOT NULL,
            skill_ch_name TEXT NOT NULL,
            description TEXT NOT NULL,
            gemini_prompt TEXT NOT NULL,
            consecutive_correct_required INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INTEGER DEFAULT 0
        )
    ''')

    # 5. 建立 skill_curriculum 表（課程分類表）
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volume INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            section INTEGER NOT NULL,
            paragraph INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            UNIQUE(volume, chapter, section, paragraph, skill_id)
        )
    ''')

    # 6. 初始技能資料
    skills = [
        ('remainder', 'Remainder Theorem', '餘式定理',
         '學習用餘式定理快速求多項式餘數',
         '分析學生答案：{user_answer}，正確答案：{correct_answer}，如果錯誤，教導餘式定理代入法。', 8, True, 1),
        ('factor_theorem', 'Factor Theorem', '因式定理',
         '判斷 (x-k) 是否為多項式的因式',
         '分析學生答案：{user_answer}，正確答案：{correct_answer}，如果錯誤，教導因式定理用法。', 10, True, 2),
        ('inequality_graph', 'Inequality Graph', '不等式圖解',
         '畫出二元一次不等式的可行域區域',
         '分析學生手寫圖形：題目 {context}，檢查直線位置、陰影區域是否正確，給出具體建議。', 12, True, 3),
        ('abs_val_ineq_lt', 'Abs. Value Inequality (Less Than)', '絕對值不等式 (<)',
         '解形如 |ax + b| < c 的不等式，並在數線上標示其解的範圍',
         '分析學生手寫圖形：題目 {context}，檢查學生是否正確標示出解的區間 {inequality_string}，包含端點是否為空心點。', 10, True, 4),
        ('abs_val_ineq_gt', 'Abs. Value Inequality (Greater Than)', '絕對值不等式 (≥)',
         '解形如 |ax + b| ≥ c 的不等式，並在數線上標示其解的範圍',
         '分析學生手寫圖形：題目 {context}，檢查學生是否正確標示出解的區間 {inequality_string}，包含端點是否為實心點。', 10, True, 5),
        ('quadrant_points', 'Quadrants and Coordinates', '象限與點坐標',
         '識別直角坐標平面上的四個象限，並判斷點 (a,b) 所在的象限。',
         '分析學生答案：{user_answer}，正確答案：{correct_answer}，如果錯誤，解釋如何根據坐標的正負號判斷象限。', 8, True, 6),
        ('dist_formula_2d', '2D Distance Formula', '平面上的距離公式', '熟練計算平面上兩點間距離 AB=sqrt((x2-x1)^2 + (y2-y1)^2)。', 'You are a math teacher. Your student is learning the distance formula in a 2D Cartesian coordinate system. Ask them to calculate the distance between two given points A(x1, y1) and B(x2, y2). The question must be in Chinese.', 3, True, 110),
        ('midpoint_formula', 'Midpoint Formula', '中點坐標公式', '熟練使用中點坐標公式 P((x1+x2)/2, (y1+y2)/2)。', 'You are a math teacher. Your student is learning the midpoint formula. Ask them to find the midpoint of the line segment connecting two points A(x1, y1) and B(x2, y2). The question must be in Chinese and the answer should be an integer coordinate.', 3, True, 120),
        ('section_formula', 'Section Formula', '內分點坐標公式', '熟練使用內分點坐標公式 P((nx1+mx2)/(m+n), (ny1+my2)/(m+n))。', 'You are a math teacher. Your student is learning the section formula. Given two points A(x1, y1) and B(x2, y2), and a ratio m:n, ask the student to find the coordinates of the point P that divides the line segment AB in the ratio m:n. The question must be in Chinese and the answer should be an integer coordinate.', 3, True, 130),
        ('centroid_formula', 'Triangle Centroid Formula', '三角形重心坐標', '熟練計算三角形重心坐標 G((x1+x2+x3)/3, (y1+y2+y3)/3)。', 'You are a math teacher. Your student is learning to find the centroid of a triangle. Given the coordinates of the three vertices A(x1, y1), B(x2, y2), and C(x3, y3), ask the student to calculate the coordinates of the centroid. The question must be in Chinese and the answer should be an integer coordinate.', 3, True, 140),
        ('function_def', 'Function Definition', '函數的定義', '理解函數的定義：「對於每一個 x 值，都恰有一個 y 值與之對應」，並認識自變數 x 和應變數 y。', 'You are a math teacher. Your student is learning the definition of a function. Present a set of ordered pairs and ask if the relation represents a function. The question should be in Chinese.', 5, True, 150),
        ('linear_func_type', 'Linear Function Types', '線型函數分類與圖形', '區分常數函數 y=b (a=0) 和一次函數 y=ax+b (a!=0)，並判斷其圖形為水平線或斜直線。', 'You are a math teacher. Your student is learning to classify linear functions. Provide a linear function in the form y = ax + b and ask them to identify whether it is a "constant function" (常數函數) or a "linear function" (一次函數), and whether its graph is a "horizontal line" (水平線) or a "slope line" (斜直線). The question must be in Chinese.', 5, True, 160)
    ]
    c.executemany("INSERT OR IGNORE INTO skills_info VALUES (?, ?, ?, ?, ?, ?, ?, ?)", skills)

    conn.commit()
    conn.close()
    print("資料庫初始化成功！")

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username