import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# AUTH CONFIGS
# -------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# -------------------------------
# PYDANTIC SETTINGS
# -------------------------------
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):

    # Database
    DATABASE_URL: str

    # Email
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    # S3 – Resume Bucket
    AWS_ACCESS_KEY_ID_RESUME: str
    AWS_SECRET_ACCESS_KEY_RESUME: str
    AWS_REGION_RESUME: str
    BUCKET_NAME_RESUME: str

    # S3 – LMS Video Bucket
    AWS_ACCESS_KEY_ID_VIDEO: str
    AWS_SECRET_ACCESS_KEY_VIDEO: str
    AWS_REGION_VIDEO: str
    AWS_S3_BUCKET_VIDEO: str

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow additional keys


settings = Settings()
