import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "mysql")  # mysql / postgresql / mssql / snowflake
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")           # optional
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    raise EnvironmentError("One or more DB environment variables are missing.")

def get_database_url():
    """Build SQLAlchemy DB URL dynamically based on DB_TYPE"""
    if DB_TYPE == "mysql":
        port = DB_PORT or "3306"
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"
    elif DB_TYPE == "postgresql":
        port = DB_PORT or "5432"
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"
    elif DB_TYPE == "mssql":
        port = DB_PORT or "1433"
        return (
            f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/"
            f"{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        )
    elif DB_TYPE == "snowflake":
        return f"snowflake://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
