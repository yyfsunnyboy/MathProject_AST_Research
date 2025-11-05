# models.py
import sqlite3
from flask_login import UserMixin
from datetime import datetime

DB_NAME = "math_master.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. 建立 users 表 (根據確認後的格式)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 建立 progress 表
    # 結構根據確認後的格式進行修正，補上缺失的欄位
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

    # 3. 安全新增欄位（如果不存在才加）
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

    # 5. 建立 skill_curriculum 表（課程分類表）- 採用新的、更靈活的結構
    # 由於結構變化較大，直接重建
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_curriculum ( -- 改為安全的 IF NOT EXISTS
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

    conn.commit()
    conn.close()
    print("資料庫初始化成功！")

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username