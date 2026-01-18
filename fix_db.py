# fix_db.py
import sqlite3
import os

db_path = os.path.join('instance', 'kumon_math.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 檢查並補齊缺失欄位
columns_to_add = [
    ("prompt_type", "VARCHAR(50)"),
    ("prompt_content", "TEXT"),
    ("prompt_strategy", "VARCHAR(100)"),
    ("system_prompt", "TEXT"),
    ("user_prompt_template", "TEXT")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE skill_gencode_prompt ADD COLUMN {col_name} {col_type}")
        print(f"✅ 成功新增欄位: {col_name}")
    except sqlite3.OperationalError:
        print(f"ℹ️ 欄位 {col_name} 已存在，跳過。")

conn.commit()
conn.close()
print("🚀 資料庫源頭校準完成！")