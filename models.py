# models.py
import sqlite3
from flask_login import UserMixin

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            skill_id TEXT,
            consecutive_correct INTEGER DEFAULT 0,
            total_attempted INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, skill_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username