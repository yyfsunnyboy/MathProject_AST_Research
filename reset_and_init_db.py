from app import app, db, initialize_skills

with app.app_context():
    print("--- Step 1: Dropping all tables... ---")
    db.drop_all()
    print("--- Step 2: Creating all tables... ---")
    db.create_all()
    print("--- Step 3: Initializing skills from SKILL_ENGINE... ---")
    initialize_skills()
    print("--- Database has been reset and initialized successfully! ---")
    print("--- You can now run 'python app.py' ---")
