import sys
import os
import random
from datetime import datetime, timedelta

# Set dummy key for app initialization
os.environ["GEMINI_API_KEY"] = "dummy_key_for_test_generation_only"

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import User, MistakeLog, ExamAnalysis, SkillInfo, SkillPrerequisites
from werkzeug.security import generate_password_hash

def generate_data():
    app = create_app()
    with app.app_context():
        print("Starting data generation...")
        
        # 1. Ensure test user
        username = "test_student"
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                password_hash=generate_password_hash("password"),
                role="student"
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {username}")
        else:
            print(f"Using existing user: {username} (ID: {user.id})")
            
        # 2. Ensure some skills exist
        skills = [
            ("quadratic_eq", "一元二次方程式", "Quadratic Equation", "Algebra"),
            ("linear_eq", "一元一次方程式", "Linear Equation", "Algebra"),
            ("factorization", "因式分解", "Factorization", "Algebra"),
            ("arithmetic_seq", "等差數列", "Arithmetic Sequence", "Number"),
            ("geometry_circle", "圓的性質", "Circle Properties", "Geometry")
        ]
        
        for sk_id, ch_name, en_name, cat in skills:
            if not SkillInfo.query.get(sk_id):
                sk = SkillInfo(
                    skill_id=sk_id, 
                    skill_ch_name=ch_name, 
                    skill_en_name=en_name, 
                    category=cat,
                    gemini_prompt="Explain {context}",
                    description="Basic skill"
                )
                db.session.add(sk)
        db.session.commit()
        
        # 3. Add Prerequisites
        if not SkillPrerequisites.query.filter_by(skill_id="quadratic_eq", prerequisite_id="linear_eq").first():
             db.session.add(SkillPrerequisites(skill_id="quadratic_eq", prerequisite_id="linear_eq"))
        
        db.session.commit()

        # 4. Generate MistakeLogs
        error_types = ["Concept (觀念錯誤)", "Calculation (計算錯誤)", "Other (審題不清)", "Concept (公式誤用)", "Calculation (粗心)"]
        
        print(f"Generating MistakeLogs for user {user.id}...")
        for _ in range(15):
            skill = random.choice(skills)[0]
            log = MistakeLog(
                user_id=user.id,
                skill_id=skill,
                question_content=f"Sample question for {skill}",
                user_answer="Wrong Answer",
                correct_answer="Correct Answer",
                error_type=random.choice(error_types),
                error_description="AI analysis description...",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(log)
        
        # 5. Generate ExamAnalysis
        print(f"Generating ExamAnalysis for user {user.id}...")
        for _ in range(8):
            skill = random.choice(skills)[0]
            is_correct = random.choice([True, False])
            error_type = random.choice(error_types) if not is_correct else None
            
            exam = ExamAnalysis(
                user_id=user.id,
                skill_id=skill,
                is_correct=is_correct,
                error_type=error_type,
                confidence=random.uniform(0.5, 0.9),
                student_answer_latex="x=1",
                feedback="AI feedback: Pay attention to signs." if not is_correct else "Good job!",
                image_path="dummy.jpg"
            )
            db.session.add(exam)
            
        db.session.commit()
        print("Data generation completed!")
        print(f"User: '{username}' / Paasword: 'password'")

if __name__ == "__main__":
    generate_data()
