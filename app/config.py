import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field

# Load .env manually (important before Settings())
load_dotenv()

# ---------------------------------------------------
# Auth Config
# ---------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


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

    class Config:
        env_file = ".env"
        extra = "allow"


# Create settings object
settings = Settings()
