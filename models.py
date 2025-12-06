# models.py
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 建立 SQLAlchemy 實例
db = SQLAlchemy()

def init_db(engine):
    # 使用傳入的 SQLAlchemy engine 來建立連線
    conn = engine.raw_connection()
    c = conn.cursor()

    # 1. 建立所有基礎表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            skill_id TEXT,
            consecutive_correct INTEGER DEFAULT 0,
            consecutive_wrong INTEGER DEFAULT 0, -- 修正：補上此欄位以支援降級邏輯
            current_level INTEGER DEFAULT 1, 
            questions_solved INTEGER DEFAULT 0,
            last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP, -- 新增：記錄最後練習時間
            PRIMARY KEY (user_id, skill_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS skills_info (
            skill_id TEXT PRIMARY KEY,
            skill_en_name TEXT NOT NULL,
            skill_ch_name TEXT NOT NULL,
            category TEXT,
            description TEXT NOT NULL,
            input_type TEXT DEFAULT 'text',
            gemini_prompt TEXT NOT NULL,
            consecutive_correct_required INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            curriculum TEXT NOT NULL, -- 'general' (普高) 或 'vocational' (技高)
            grade INTEGER NOT NULL, -- 10, 11, 12 代表高一、二、三
            volume TEXT NOT NULL, -- '冊一', '數A', '數B', '數C' 等
            chapter TEXT NOT NULL, -- '第一章 多項式'
            section TEXT NOT NULL, -- '1-2 餘式定理'
            paragraph TEXT, -- 可選的段落
            display_order INTEGER DEFAULT 0,
            difficulty_level INTEGER DEFAULT 1, -- 新增：難易度欄位
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            UNIQUE(curriculum, grade, volume, chapter, section, paragraph, skill_id, difficulty_level)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            prerequisite_id TEXT NOT NULL,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            UNIQUE (skill_id, prerequisite_id)
        )
    ''')

    # 新增：建立 classes 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_code TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')

    # 新增：建立 class_students 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS class_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(class_id, student_id)
        )
    ''')

    # 新增：建立 mistake_logs 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS mistake_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            question_content TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            error_type TEXT,
            error_description TEXT,
            improvement_suggestion TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 新增：建立 exam_analysis 表格 (考卷診斷分析結果)
    c.execute('''
        CREATE TABLE IF NOT EXISTS exam_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            curriculum TEXT,
            grade INTEGER,
            volume TEXT,
            chapter TEXT,
            section TEXT,
            is_correct BOOLEAN NOT NULL,
            error_type TEXT,
            confidence FLOAT,
            student_answer_latex TEXT,
            feedback TEXT,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id)
        )
    ''')

    # 新增：建立 textbook_examples 表格 (課本例題)
    c.execute('''
        CREATE TABLE IF NOT EXISTS textbook_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            source_curriculum TEXT NOT NULL,
            source_volume TEXT NOT NULL,
            source_chapter TEXT NOT NULL,
            source_section TEXT NOT NULL,
            source_description TEXT NOT NULL,
            source_paragraph TEXT,
            problem_text TEXT NOT NULL,
            problem_type TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            difficulty_level INTEGER DEFAULT 1,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE
        )
    ''')

    # 新增：建立 learning_diagnosis 表格 (學生學習診斷)
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_diagnosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            radar_chart_data TEXT NOT NULL,
            ai_comment TEXT,
            recommended_unit TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    # 新增：建立 system_settings 表格 (系統設定)
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')



    # 2. 安全地為已存在的表格新增欄位（用於舊資料庫升級）
    def add_column_if_not_exists(table, column, definition):
        c.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in c.fetchall()]
        if column not in columns:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # 新增：為 users 表新增 role 欄位
    add_column_if_not_exists('users', 'role', 'TEXT DEFAULT "student"')

    conn.commit()
    conn.close()
    print("資料庫初始化成功！")

# 它會自動對應到 init_db() 中建立的 'users' 表格
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='student') # 新增身分欄位
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        """簡單的管理員權限判斷"""
        return self.username in ['admin', 'testuser'] # 將 'testuser' 替換成您的帳號

# 新增 Progress ORM 模型
# 它會自動對應到 init_db() 中建立的 'progress' 表格
class Progress(db.Model):
    __tablename__ = 'progress'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    skill_id = db.Column(db.String, primary_key=True)
    consecutive_correct = db.Column(db.Integer, default=0)
    consecutive_wrong = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    questions_solved = db.Column(db.Integer, default=0)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('progress', lazy=True))

# 新增 SkillInfo ORM 模型 (技能單元資訊)
class SkillInfo(db.Model):
    __tablename__ = 'skills_info'

    skill_id = db.Column(db.String, primary_key=True)
    skill_en_name = db.Column(db.String, nullable=False)
    skill_ch_name = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    input_type = db.Column(db.String, default='text')
    gemini_prompt = db.Column(db.String, nullable=False)
    consecutive_correct_required = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)

    # 新增：對應 Excel 中的 K, L, M 欄位
    suggested_prompt_1 = db.Column(db.String, nullable=True)
    suggested_prompt_2 = db.Column(db.String, nullable=True)
    suggested_prompt_3 = db.Column(db.String, nullable=True)

    # 定義技能之間的多對多自我參照關係
    # 'prerequisites' 屬性將會得到此技能的所有前置技能
    prerequisites = db.relationship(
        'SkillInfo',
        secondary='skill_prerequisites',
        primaryjoin='SkillInfo.skill_id == SkillPrerequisites.skill_id',
        secondaryjoin='SkillInfo.skill_id == SkillPrerequisites.prerequisite_id',
        backref=db.backref('subsequent_skills', lazy='dynamic')
    )
    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        return {
            'skill_id': self.skill_id,
            'skill_en_name': self.skill_en_name,
            'skill_ch_name': self.skill_ch_name,
            'category': self.category,
            'description': self.description,
            'input_type': self.input_type,
            'gemini_prompt': self.gemini_prompt,
            'consecutive_correct_required': self.consecutive_correct_required,
            'is_active': self.is_active,
            'order_index': self.order_index,
            'suggested_prompt_1': self.suggested_prompt_1,
            'suggested_prompt_2': self.suggested_prompt_2,
            'suggested_prompt_3': self.suggested_prompt_3
        }

# 新增 SkillCurriculum ORM 模型 (課程綱要)
class SkillCurriculum(db.Model):
    __tablename__ = 'skill_curriculum'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    curriculum = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.String, nullable=False)
    chapter = db.Column(db.String, nullable=False)
    section = db.Column(db.String, nullable=False)
    paragraph = db.Column(db.String)
    display_order = db.Column(db.Integer, default=0)
    difficulty_level = db.Column(db.Integer, default=1)

    # 建立與 SkillInfo 的關聯
    # 讓我們可以透過 SkillCurriculum.skill_info 來取得對應的技能資訊
    skill_info = db.relationship('SkillInfo', backref=db.backref('curriculum_entries', lazy=True, cascade="all, delete-orphan"))

    # 定義複合唯一約束
    __table_args__ = (db.UniqueConstraint('curriculum', 'grade', 'volume', 'chapter', 'section', 'paragraph', 'skill_id', 'difficulty_level', name='_curriculum_skill_uc'),)

    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'curriculum': self.curriculum,
            'grade': self.grade,
            'volume': self.volume,
            'chapter': self.chapter,
            'section': self.section,
            'paragraph': self.paragraph,
            'display_order': self.display_order,
            'difficulty_level': self.difficulty_level
        }

# 新增 SkillPrerequisites ORM 模型 (技能前置依賴關聯表)
class SkillPrerequisites(db.Model):
    __tablename__ = 'skill_prerequisites'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    prerequisite_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)

    # 定義複合唯一約束
    __table_args__ = (db.UniqueConstraint('skill_id', 'prerequisite_id', name='_skill_prerequisite_uc'),)

# 新增 Class ORM 模型 (班級)
class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯到教師
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('teaching_classes', lazy=True))
    
    # 關聯到學生 (透過 ClassStudent)
    students = db.relationship('User', secondary='class_students', backref=db.backref('enrolled_classes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_code': self.class_code,
            'student_count': len(self.students),
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# 新增 ClassStudent ORM 模型 (班級-學生關聯)
class ClassStudent(db.Model):
    __tablename__ = 'class_students'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

# 新增 MistakeLog ORM 模型 (錯誤記錄)
class MistakeLog(db.Model):
    __tablename__ = 'mistake_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.String, nullable=False)
    question_content = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    error_type = db.Column(db.String(50)) # e.g., 'calculation', 'concept', 'other'
    error_description = db.Column(db.Text)
    improvement_suggestion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('mistakes', lazy=True))

# 新增 ExamAnalysis ORM 模型 (考卷診斷分析結果)
class ExamAnalysis(db.Model):
    __tablename__ = 'exam_analysis'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id'), nullable=False)
    
    # 課程資訊 (從 skill_curriculum 複製)
    curriculum = db.Column(db.String)  # 'general', 'vocational', 'junior_high'
    grade = db.Column(db.Integer)      # 7, 10, 11, 12
    volume = db.Column(db.String)      # '數學1上', '數A', '數B' 等
    chapter = db.Column(db.String)     # '第一章 多項式'
    section = db.Column(db.String)     # '1-2 餘式定理'
    
    # 分析結果
    is_correct = db.Column(db.Boolean, nullable=False)
    error_type = db.Column(db.String)  # CALCULATION, CONCEPTUAL, LOGIC, COMPREHENSION, UNATTEMPTED
    confidence = db.Column(db.Float)   # 0.0 - 1.0
    
    # 學生作答內容
    student_answer_latex = db.Column(db.Text)
    feedback = db.Column(db.Text)
    
    # 圖片儲存路徑
    image_path = db.Column(db.String, nullable=False)
    
    # 時間戳記
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    user = db.relationship('User', backref=db.backref('exam_analyses', lazy=True))
    skill_info = db.relationship('SkillInfo', backref=db.backref('exam_analyses', lazy=True))
    
    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'curriculum': self.curriculum,
            'grade': self.grade,
            'volume': self.volume,
            'chapter': self.chapter,
            'section': self.section,
            'is_correct': self.is_correct,
            'error_type': self.error_type,
            'confidence': self.confidence,
            'student_answer_latex': self.student_answer_latex,
            'feedback': self.feedback,
            'image_path': self.image_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

# 新增 TextbookExample ORM 模型 (課本例題)
class TextbookExample(db.Model):
    __tablename__ = 'textbook_examples'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    
    # 來源資訊
    source_curriculum = db.Column(db.String, nullable=False)  # 'general', 'vocational', 'junior_high'
    source_volume = db.Column(db.String, nullable=False)      # '數學1上', '數A', '數B' 等
    source_chapter = db.Column(db.String, nullable=False)     # '3 多項式的運算'
    source_section = db.Column(db.String, nullable=False)     # '3-1 多項式的基本概念與四則運算'
    source_description = db.Column(db.String, nullable=False) # '1-2 餘式定理'
    source_paragraph = db.Column(db.String)                   # 更細的段落劃分 (可選)
    
    # 題目內容 (核心資產)
    problem_text = db.Column(db.Text, nullable=False)         # 題目完整文字 (支援 LaTeX)
    problem_type = db.Column(db.String)                       # 'calculation', 'word_problem', 'proof', 'true_false', 'multiple_choice'
    correct_answer = db.Column(db.String)                     # 最終答案
    detailed_solution = db.Column(db.Text)                    # 詳細解法 (供 AI 參考)
    difficulty_level = db.Column(db.Integer, default=1)       # 難易度等級
    
    # 關聯到 SkillInfo
    skill_info = db.relationship('SkillInfo', backref=db.backref('textbook_examples', lazy=True, cascade="all, delete-orphan"))
    
    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'source_curriculum': self.source_curriculum,
            'source_volume': self.source_volume,
            'source_chapter': self.source_chapter,
            'source_section': self.source_section,
            'source_description': self.source_description,
            'source_paragraph': self.source_paragraph,
            'problem_text': self.problem_text,
            'problem_type': self.problem_type,
            'correct_answer': self.correct_answer,
            'detailed_solution': self.detailed_solution,
            'difficulty_level': self.difficulty_level
        }

# 新增 LearningDiagnosis ORM 模型 (學生學習診斷)
class LearningDiagnosis(db.Model):
    __tablename__ = 'learning_diagnosis'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    radar_chart_data = db.Column(db.Text, nullable=False)  # JSON 格式字串
    ai_comment = db.Column(db.Text)
    recommended_unit = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯到學生
    student = db.relationship('User', backref=db.backref('learning_diagnoses', lazy=True))

    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        import json
        return {
            'id': self.id,
            'student_id': self.student_id,
            'radar_chart_data': json.loads(self.radar_chart_data) if self.radar_chart_data else {},
            'ai_comment': self.ai_comment,
            'recommended_unit': self.recommended_unit,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

# 新增 SystemSetting ORM 模型 (系統設定)
class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """將物件轉換為可序列化的字典。"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
