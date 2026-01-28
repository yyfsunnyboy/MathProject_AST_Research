import sqlite3

conn = sqlite3.connect('instance/kumon_math.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('\n'.join([t[0] for t in tables]))
conn.close()
