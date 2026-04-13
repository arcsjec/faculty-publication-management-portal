"""
Initial Setup Script - Create Admin, Leadership, and AIML Department
"""
from app import app, db
from models import User, Department
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_initial_data():
    with app.app_context():
        print("=" * 80)
        print("INITIAL SETUP - Creating Admin, Leadership & AIML Department")
        print("=" * 80)
        print()
        
        # Step 1: Create AIML Department
        print("Step 1: Creating AIML Department...")
        aiml_dept = Department.query.filter_by(code='AIML').first()
        if not aiml_dept:
            aiml_dept = Department(
                name='Artificial Intelligence and Machine Learning',
                code='AIML'
            )
            db.session.add(aiml_dept)
            db.session.commit()
            print(f"[SUCCESS] Created: {aiml_dept.name} ({aiml_dept.code})")
        else:
            print(f"[EXISTS] Department: {aiml_dept.name} ({aiml_dept.code})")
        print()
        
        # Step 2: Create R&D Department for leadership roles
        print("Step 2: Creating R&D Department...")
        rnd_dept = Department.query.filter_by(code='RND').first()
        if not rnd_dept:
            rnd_dept = Department(
                name='Research and Development',
                code='RND'
            )
            db.session.add(rnd_dept)
            db.session.commit()
            print(f"[SUCCESS] Created: {rnd_dept.name} ({rnd_dept.code})")
        else:
            print(f"[EXISTS] Department: {rnd_dept.name} ({rnd_dept.code})")
        print()
        
        # Step 3: Create Admin and Leadership Users
        print("Step 3: Creating Admin and Leadership Users...")
        
        users = [
            {
                'name': 'Admin',
                'email': 'ad@sjec.ac.in',
                'password': 'admin123',
                'role': 'admin',
                'department_id': None
            },
            {
                'name': 'Principal',
                'email': 'pr@sjec.ac.in',
                'password': 'principal123',
                'role': 'principal',
                'department_id': None
            },
            {
                'name': 'Dean R&D',
                'email': 'dean@sjec.ac.in',
                'password': 'dean123',
                'role': 'dean',
                'department_id': None
            },
            {
                'name': 'Director',
                'email': 'dir@sjec.ac.in',
                'password': 'director123',
                'role': 'director',
                'department_id': None
            },
            {
                'name': 'Dean Secretary',
                'email': 'deansec@sjec.ac.in',
                'password': 'deansec123',
                'role': 'dean_secretary',
                'department_id': None
            }
        ]
        
        for user_data in users:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    department_id=user_data['department_id'],
                    is_active=True,
                    created_at=datetime.now()
                )
                db.session.add(user)
                print(f"[SUCCESS] Created: {user_data['name']} ({user_data['email']}) - Role: {user_data['role']}")
            else:
                print(f"[EXISTS] User: {user_data['name']} ({user_data['email']})")
        
        print()
        
        # Step 4: Create HoD AIML
        print("Step 4: Creating HoD for AIML...")
        hod_email = 'hodaiml@sjec.ac.in'
        existing_hod = User.query.filter_by(email=hod_email).first()
        if not existing_hod:
            hod = User(
                name='HOD AIML',
                email=hod_email,
                password_hash=generate_password_hash('hod123'),
                role='hod',
                department_id=aiml_dept.id,
                is_active=True,
                created_at=datetime.now()
            )
            db.session.add(hod)
            print(f"[SUCCESS] Created: HOD AIML ({hod_email}) - Department: {aiml_dept.name}")
        else:
            print(f"[EXISTS] User: HOD AIML ({hod_email})")
        
        # Commit all changes
        db.session.commit()
        
        print()
        print("=" * 80)
        print("✅ SETUP COMPLETE!")
        print("=" * 80)
        print()
        print("LOGIN CREDENTIALS:")
        print("-" * 80)
        print(f"{'Role':<20} {'Email':<30} {'Password':<15}")
        print("-" * 80)
        print(f"{'Admin':<20} {'ad@sjec.ac.in':<30} {'admin123':<15}")
        print(f"{'Principal':<20} {'pr@sjec.ac.in':<30} {'principal123':<15}")
        print(f"{'Dean R&D':<20} {'dean@sjec.ac.in':<30} {'dean123':<15}")
        print(f"{'Director':<20} {'dir@sjec.ac.in':<30} {'director123':<15}")
        print(f"{'Dean Secretary':<20} {'deansec@sjec.ac.in':<30} {'deansec123':<15}")
        print(f"{'HoD AIML':<20} {'hodaiml@sjec.ac.in':<30} {'hod123':<15}")
        print("-" * 80)
        print()
        print("DEPARTMENTS CREATED:")
        print("-" * 80)
        print(f"1. Artificial Intelligence and Machine Learning (AIML)")
        print(f"2. Research and Development (RND)")
        print("-" * 80)
        print()
        
        # Display current database stats
        total_users = User.query.count()
        total_depts = Department.query.count()
        print(f"Total Users: {total_users}")
        print(f"Total Departments: {total_depts}")
        print()

if __name__ == '__main__':
    setup_initial_data()
