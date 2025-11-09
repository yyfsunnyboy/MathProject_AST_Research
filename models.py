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

    # 2. 安全地為已存在的表格新增欄位（用於舊資料庫升級）
    def add_column_if_not_exists(table, column, definition):
        c.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in c.fetchall()]
        if column not in columns:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # 為 progress 表新增欄位（安全）
    add_column_if_not_exists('progress', 'current_level', 'INTEGER DEFAULT 1')
    add_column_if_not_exists('progress', 'questions_solved', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('progress', 'consecutive_wrong', 'INTEGER DEFAULT 0') # 修正：安全新增
    add_column_if_not_exists('progress', 'last_practiced', 'DATETIME') # 新增

    # 為 skills_info 表新增欄位（安全）
    add_column_if_not_exists('skills_info', 'category', 'TEXT')
    add_column_if_not_exists('skills_info', 'input_type', 'TEXT DEFAULT "text"')
    add_column_if_not_exists('skills_info', 'is_active', 'BOOLEAN DEFAULT TRUE')
    add_column_if_not_exists('skills_info', 'order_index', 'INTEGER DEFAULT 0')

    conn.commit()
    conn.close()
    print("資料庫初始化成功！")

# 將 User 類別改寫為 SQLAlchemy ORM 模型
# 它會自動對應到 init_db() 中建立的 'users' 表格
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        """簡單的管理員權限判斷"""
        return self.username in ['admin', 'my_user'] # 將 'my_user' 替換成您的帳號

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
            'order_index': self.order_index
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