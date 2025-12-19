"""Debug test to verify database saving works"""
import pytest
from app.database import SessionLocal, engine
from app.models.test_report_m import TestReport, Base
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv(".env.test")


def test_database_connection():
    """Test if database connection works"""
    print("\n" + "="*60)
    print("🔍 DEBUGGING DATABASE CONNECTION")
    print("="*60)
    
    db_url = os.getenv("DATABASE_URL")
    print(f"\n1. DATABASE_URL: {db_url}")
    
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print("✅ 2. Database connection: SUCCESS")
        db.close()
    except Exception as e:
        print(f"❌ 2. Database connection: FAILED - {e}")
        assert False, f"Database connection failed: {e}"
    
    try:
        db = SessionLocal()
        result = db.execute(text("SHOW TABLES LIKE 'test_reports'"))
        table_exists = result.fetchone()
        if table_exists:
            print("✅ 3. Table 'test_reports': EXISTS")
        else:
            print("⚠️ 3. Table 'test_reports': DOES NOT EXIST")
            print("   Creating table...")
            Base.metadata.create_all(bind=engine)
            print("✅ Table created!")
        db.close()
    except Exception as e:
        print(f"❌ 3. Table check: FAILED - {e}")
        assert False, f"Table check failed: {e}"
    try:
        db = SessionLocal()
        db.query(TestReport).filter_by(module_name="test_debug").delete()
        db.commit()
        test_report = TestReport(
            module_name="test_debug",
            total_tests=1,
            passed=1,
            failed=0,
            failures=None
        )
        db.add(test_report)
        db.commit()
        print("✅ 4. Manual insert: SUCCESS")
        
        count = db.query(TestReport).filter_by(module_name="test_debug").count()
        print(f"✅ 5. Verification: {count} record(s) found")
        db.close()
    except Exception as e:
        print(f"❌ 4. Manual insert: FAILED - {e}")
        assert False, f"Insert failed: {e}"
    
    print("\n" + "="*60)
    print("✅ ALL DATABASE CHECKS PASSED!")
    print("="*60 + "\n")


def test_one():
    """Simple test 1"""
    print("\n🔍 Running test_one")
    assert 1 + 1 == 2


def test_two():
    """Simple test 2"""
    print("\n🔍 Running test_two")
    assert 2 + 2 == 4


def test_three():
    """Simple test 3"""
    print("\n🔍 Running test_three")
    assert 3 + 3 == 6