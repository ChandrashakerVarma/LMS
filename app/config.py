import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
<<<<<<< HEAD
from pydantic import EmailStr, Field
=======
from fastapi_mail import ConnectionConfig
>>>>>>> origin/main

# Load .env manually (important before Settings())
load_dotenv()

<<<<<<< HEAD
# ---------------------------------------------------
# Auth Config
# ---------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
=======
# -------------------------------
# AUTH CONFIGS
# -------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
>>>>>>> origin/main
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

<<<<<<< HEAD

# ---------------------------------------------------
# Main Settings Class
# ---------------------------------------------------
class Settings(BaseSettings):
    # ❗ Provide default to prevent startup crash
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:Sainanda%40169@localhost:3306/lms",
        env="DATABASE_URL"
    )

    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field(default="", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(default="", env="EMAIL_PASSWORD")
    EMAIL_FROM: EmailStr = Field(default="example@example.com", env="EMAIL_FROM")
=======
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
>>>>>>> origin/main

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



# Create settings object
settings = Settings()

# Email config
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
