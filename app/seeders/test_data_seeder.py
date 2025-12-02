
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user_m import User
from app.models.role_m import Role
from app.models.organization_m import Organization
from app.models.department_m import Department
from app.models.course_m import Course
from app.models.attendance_m import Attendance
from app.utils.utils import hash_password
from datetime import datetime, timedelta
import random
import app.models  # ✅ Register all models

def seed_test_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding Test Data...")

        # 0. Organization (Crucial for Anomaly Detection)
        org = db.query(Organization).filter_by(id=1).first()
        if not org:
            org = Organization(
                id=1,
                name="Test Organization",
                contact_email="admin@testorg.com",
                subscription_status="active"
            )
            db.add(org)
            db.commit()
            print("✅ Organization seeded")

        # 1. Departments
        deps = ["Engineering", "Human Resources", "Sales", "Marketing"]
        db_deps = []
        for d_name in deps:
            dep = db.query(Department).filter_by(name=d_name).first()
            if not dep:
                dep = Department(name=d_name, code=d_name[:3].upper(), description=f"{d_name} Department", organization_id=org.id)
                db.add(dep)
                db.flush()
            db_deps.append(dep)
        db.commit()
        print(f"✅ Departments seeded: {deps}")

        # 2. Roles (Ensure they exist - usually seeded by role_seeder)
        # Assuming roles exist, if not we'd need to create them. 
        # For safety, let's fetch 'employee' role.
        employee_role = db.query(Role).filter_by(name="employee").first()
        if not employee_role:
            print("⚠️ 'employee' role not found. Skipping user creation requiring this role.")

        # 3. Users (for Fuzzy Search)
        users_data = [
            {"first": "John", "last": "Doe", "email": "john.doe@example.com", "dept": db_deps[0]},
            {"first": "Jon", "last": "Dough", "email": "jon.dough@example.com", "dept": db_deps[0]}, # Fuzzy match
            {"first": "Jane", "last": "Smith", "email": "jane.smith@example.com", "dept": db_deps[1]},
            {"first": "Jan", "last": "Smyth", "email": "jan.smyth@example.com", "dept": db_deps[1]}, # Fuzzy match
            {"first": "Alice", "last": "Wonder", "email": "alice.w@example.com", "dept": db_deps[2]},
        ]

        created_users = []
        for u in users_data:
            user = db.query(User).filter_by(email=u["email"]).first()
            if not user and employee_role:
                user = User(
                    first_name=u["first"],
                    last_name=u["last"],
                    email=u["email"],
                    hashed_password=hash_password("User@123"),
                    role_id=employee_role.id,
                    department_id=u["dept"].id,
                    organization_id=1,
                    is_active=True
                )
                db.add(user)
                db.flush()
                created_users.append(user)
        db.commit()
        print(f"✅ Users seeded: {len(created_users)} new users")

        # 4. Courses (for Unified Search)
        courses_data = [
            "Python for Beginners",
            "Advanced Machine Learning",
            "HR Management 101",
            "Sales Strategies 2024",
            "Workplace Safety"
        ]
        for c_title in courses_data:
            if not db.query(Course).filter_by(title=c_title).first():
                course = Course(title=c_title, description="Test Course", duration=10)
                db.add(course)
        db.commit()
        print(f"✅ Courses seeded")

        # 5. Attendance (for Anomaly Detection)
        # Generate last 30 days of data for John Doe (Normal) and Jane Smith (Anomalous)
        
        # John Doe - Normal (9 AM - 6 PM)
        john = db.query(User).filter_by(email="john.doe@example.com").first()
        if john:
            for i in range(30):
                date = datetime.now().date() - timedelta(days=i)
                # Skip weekends
                if date.weekday() >= 5: continue
                
                # Normal time with slight random variance
                in_time = datetime.combine(date, datetime.strptime("09:00", "%H:%M").time()) + timedelta(minutes=random.randint(-5, 10))
                out_time = datetime.combine(date, datetime.strptime("18:00", "%H:%M").time()) + timedelta(minutes=random.randint(-10, 15))
                
                att = Attendance(user_id=john.id, date=date, check_in=in_time, check_out=out_time, status="Present")
                db.add(att)
        
        # Jane Smith - Anomalous (Late arrivals, Early leaves)
        jane = db.query(User).filter_by(email="jane.smith@example.com").first()
        if jane:
            for i in range(30):
                date = datetime.now().date() - timedelta(days=i)
                if date.weekday() >= 5: continue
                
                # 50% chance of anomaly
                if random.random() > 0.5:
                    # Late In (10:30 AM)
                    in_time = datetime.combine(date, datetime.strptime("10:30", "%H:%M").time()) + timedelta(minutes=random.randint(0, 30))
                    # Early Out (3:00 PM)
                    out_time = datetime.combine(date, datetime.strptime("15:00", "%H:%M").time()) + timedelta(minutes=random.randint(0, 30))
                else:
                    in_time = datetime.combine(date, datetime.strptime("09:00", "%H:%M").time())
                    out_time = datetime.combine(date, datetime.strptime("18:00", "%H:%M").time())

                att = Attendance(user_id=jane.id, date=date, check_in=in_time, check_out=out_time, status="Present")
                db.add(att)
        
        db.commit()
        print("✅ Attendance data seeded (Normal & Anomalous)")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()
