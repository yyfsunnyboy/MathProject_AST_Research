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

    conn.commit()
    conn.close()
    print("資料庫初始化成功！")

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username