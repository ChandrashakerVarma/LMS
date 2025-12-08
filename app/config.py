import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field
from fastapi_mail import ConnectionConfig

# ---------------------------------------------------
# Load env first
# ---------------------------------------------------
load_dotenv()

# ---------------------------------------------------
# Auth Config
# ---------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# ---------------------------------------------------
# Settings Class
# ---------------------------------------------------
class Settings(BaseSettings):

    # ❗ safe default so backend boots even if .env missing
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:1234@localhost:3306/lms",
        env="DATABASE_URL"
    )

    # EMAIL
    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field(default="", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(default="", env="EMAIL_PASSWORD")
    EMAIL_FROM: EmailStr = Field(default="example@example.com", env="EMAIL_FROM")

    # S3 Resume Bucket
    AWS_ACCESS_KEY_ID_RESUME: str = Field(default="", env="AWS_ACCESS_KEY_ID_RESUME")
    AWS_SECRET_ACCESS_KEY_RESUME: str = Field(default="", env="AWS_SECRET_ACCESS_KEY_RESUME")
    AWS_REGION_RESUME: str = Field(default="", env="AWS_REGION_RESUME")
    BUCKET_NAME_RESUME: str = Field(default="", env="BUCKET_NAME_RESUME")

    # S3 Video Bucket
    AWS_ACCESS_KEY_ID_VIDEO: str = Field(default="", env="AWS_ACCESS_KEY_ID_VIDEO")
    AWS_SECRET_ACCESS_KEY_VIDEO: str = Field(default="", env="AWS_SECRET_ACCESS_KEY_VIDEO")
    AWS_REGION_VIDEO: str = Field(default="", env="AWS_REGION_VIDEO")
    AWS_S3_BUCKET_VIDEO: str = Field(default="", env="AWS_S3_BUCKET_VIDEO")

    class Config:
        env_file = ".env"
        extra = "allow"     # allow extra keys silently


# ---------------------------------------------------
# Instantiate Settings
# ---------------------------------------------------
settings = Settings()


# ---------------------------------------------------
# Email connection (FastAPI-Mail)
# ---------------------------------------------------
mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
