from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# ---------------------------------------------------------
# TEST DATABASE (SQLite local file)
# ---------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_hrms.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_test_db():
    """Create a fresh test database (clean tables)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def drop_test_db():
    """Drop all tables after test run."""
    Base.metadata.drop_all(bind=engine)
