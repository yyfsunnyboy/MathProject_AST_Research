import os

models_path = r'c:\Python\MathProject_AST_Research\models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define start and end markers
start_marker = "class ExperimentLog(db.Model):"
end_marker = "# [補上缺漏] 練習歷程紀錄相關表格"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1:
    print(f"Start marker '{start_marker}' not found")
    exit(1)
if end_idx == -1:
    print(f"End marker '{end_marker}' not found. Looking for 'class Question'.")
    end_marker = "class Question(db.Model):"
    end_idx = content.find(end_marker)
    if end_idx == -1:
        print("End marker Question not found too")
        exit(1)

# New code for ExperimentLog
new_code = """class ExperimentLog(db.Model):
    __tablename__ = 'experiment_log'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Float)
    duration_seconds = db.Column(db.Float)
    prompt_len = db.Column(db.Integer)
    code_len = db.Column(db.Integer)
    is_success = db.Column(db.Boolean)
    error_msg = db.Column(db.Text)
    repaired = db.Column(db.Boolean, default=False)
    model_name = db.Column(db.String(50))
    
    # --- [科研新增欄位] ---
    model_size_class = db.Column(db.String(20))     # '7B', '14B', 'Cloud'
    prompt_level = db.Column(db.String(20))          # 'Bare', 'Engineered', 'Self-Healing'
    raw_response = db.Column(db.Text)               # LLM 原始輸出
    final_code = db.Column(db.Text)                 # 最終修復代碼
    score_syntax = db.Column(db.Float, default=0.0) # 語法分
    score_math = db.Column(db.Float, default=0.0)   # 邏輯分
    score_visual = db.Column(db.Float, default=0.0) # 視覺分
    healing_duration = db.Column(db.Float)          # 自癒耗時
    is_executable = db.Column(db.Boolean)           # 是否可執行成功
    ablation_id = db.Column(db.Integer)             # 對應實驗組 ID
    missing_imports_fixed = db.Column(db.Text)      # 紀錄補上的庫
    resource_cleanup_flag = db.Column(db.Boolean)    # 資源釋放標記
    # ----------------------

    # 原有 Token 欄位
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    code_complexity = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ExperimentLog {self.model_name}: {self.duration_seconds}s>"
"""

# Replace content
# Ensure newlines around the new block
new_content = content[:start_idx] + new_code + "\n\n" + content[end_idx:]

with open(models_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully updated models.py with new ExperimentLog class.")
