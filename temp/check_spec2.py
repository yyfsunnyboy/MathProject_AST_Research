import sqlite3

conn = sqlite3.connect('instance/kumon_math.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT prompt_content 
    FROM skill_gencode_prompt 
    WHERE skill_id='jh_數學1上_FourArithmeticOperationsOfNumbers' 
    AND prompt_type='MASTER_SPEC' 
    ORDER BY created_at DESC 
    LIMIT 1
""")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print('No MASTER_SPEC found')
conn.close()
