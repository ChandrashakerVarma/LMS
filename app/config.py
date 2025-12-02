import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig

load_dotenv()

class Settings(BaseSettings):

    # Organization
    ORGANIZATION_NAME: str = os.getenv("ORGANIZATION_NAME", "Your Organization")
    ORGANIZATION_LOGO_URL: str = os.getenv("ORGANIZATION_LOGO_URL")

    # Auth / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    # Email config
    EMAIL_HOST: str = os.getenv("EMAIL_HOST")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")

    # ⭐ Correct AWS Fields (MATCHES s3_utils.py)
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME")

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
