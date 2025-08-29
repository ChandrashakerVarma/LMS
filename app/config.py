import os
from dotenv import load_dotenv

load_dotenv()

#Auth configs
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

DEBUG = os.getenv("DEBUG", "False").lower() == "true"