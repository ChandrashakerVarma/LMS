"""
Run this directly: python tests/manual_db_test.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.database import SessionLocal, engine, Base
from app.models.test_report_m import TestReport
from sqlalchemy import text

print("\n" + "="*60)
print("🔧 MANUAL DATABASE TEST")
print("="*60)

# Load environment
load_dotenv(".env.test")
db_url = os.getenv("DATABASE_URL")
print(f"\n1. DATABASE_URL: {db_url}")

# Test connection
try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    print("✅ 2. Database connection works")
except Exception as e:
    print(f"❌ 2. Database connection failed: {e}")
    exit(1)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ 3. Tables created/verified")
except Exception as e:
    print(f"❌ 3. Table creation failed: {e}")
    exit(1)

# Insert test record
try:
    db = SessionLocal()
    
    # Delete old test records
    db.query(TestReport).filter_by(module_name="manual_test").delete()
    db.commit()
    
    # Insert new record
    record = TestReport(
        module_name="manual_test",
        total_tests=5,
        passed=3,
        failed=2,
        failures="Test failure 1\nTest failure 2"
    )
    db.add(record)
    db.commit()
    print("✅ 4. Test record inserted")
    
    # Query back
    records = db.query(TestReport).filter_by(module_name="manual_test").all()
    print(f"✅ 5. Found {len(records)} record(s)")
    
    if records:
        r = records[0]
        print(f"\n📊 Record details:")
        print(f"   ID: {r.id}")
        print(f"   Module: {r.module_name}")
        print(f"   Total: {r.total_tests}")
        print(f"   Passed: {r.passed}")
        print(f"   Failed: {r.failed}")
        print(f"   Created: {r.created_at}")
    
    db.close()
    
except Exception as e:
    print(f"❌ 4. Database operation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ ALL CHECKS PASSED - Database is working!")
print("="*60)
print("\nNow run: pytest tests/test_debug.py -v -s")
print("="*60 + "\n")