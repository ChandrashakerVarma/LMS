# tests/test_database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.database import Base

# --------------------------------------------------
# Load TEST environment ONLY
# --------------------------------------------------
load_dotenv(".env.test", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL not found in .env.test")

# --------------------------------------------------
# MySQL TEST DATABASE ENGINE
# --------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# Create tables (TEST DB ONLY)
# --------------------------------------------------
def create_test_db():
    print("🧪 Ensuring tables exist in MySQL test_db...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready in test_db")
