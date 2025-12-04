import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, dotenv_values
from urllib.parse import quote_plus

# -----------------------------------------
# Load environment variables SAFELY
# -----------------------------------------

# Explicitly load from the main .env (to avoid Alembic loading wrong env file)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(env_path)

# Use dotenv_values to avoid partial parsing issues
env = dotenv_values(env_path)

DB_USER = env.get("DB_USER")
DB_PASSWORD = env.get("DB_PASSWORD")
DB_HOST = env.get("DB_HOST")
DB_NAME = env.get("DB_NAME")

# -----------------------------------------
# Validate .env Inputs
# -----------------------------------------
missing = [key for key in ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"] if env.get(key) is None]
if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

# -----------------------------------------
# Encode password safely
# -----------------------------------------
DB_PASSWORD_QUOTED = quote_plus(DB_PASSWORD)

# -----------------------------------------
# Build final SQLAlchemy URL
# -----------------------------------------
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_QUOTED}@{DB_HOST}:3306/{DB_NAME}"
)

print("Using DATABASE_URL:", DATABASE_URL)

# -----------------------------------------
# Database engine + session
# -----------------------------------------
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
