import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------
# Auth Config
# ---------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ---------------------------------------------------
# Main Settings Class (from origin/main)
# ---------------------------------------------------
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    DATABASE_URL: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
