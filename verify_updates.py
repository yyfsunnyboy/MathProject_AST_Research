from app import create_app
from models import db, init_db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    # 1. Trigger schema update
    print("Running init_db to ensure schema is updated...")
    init_db(db.engine)
    
    # 2. Inspect columns
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('experiment_log')]
    
    print(f"Current columns in experiment_log: {columns}")
    
    required_cols = [
        'start_time', 'prompt_len', 'code_len', 'error_msg', 'repaired',
        'model_size_class', 'prompt_level', 'raw_response', 'final_code',
        'score_syntax', 'score_math', 'score_visual', 'healing_duration',
        'is_executable', 'ablation_id', 'missing_imports_fixed', 'resource_cleanup_flag'
    ]
    
    missing = [col for col in required_cols if col not in columns]
    
    if missing:
        print(f"❌ Verification FAILED. Missing columns: {missing}")
        exit(1)
    else:
        print("✅ Verification SUCCESS. All new columns are present.")
