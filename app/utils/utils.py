from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get secrets from environment
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Truncate password to 72 bytes for bcrypt
    max_bytes = 72
    truncated = password.encode("utf-8")[:max_bytes].decode("utf-8", "ignore")
    return pwd_context.hash(truncated)


def verify_password(plain: str, hashed: str) -> bool:
    # Truncate input the same way before verifying
    max_bytes = 72
    truncated = plain.encode("utf-8")[:max_bytes].decode("utf-8", "ignore")
    return pwd_context.verify(truncated, hashed)

# JWT Token creation and decoding
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# from passlib.context import CryptContext

# # Initialize CryptContext for hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_and_print_password(plain_password: str) -> None:
#     """
#     Takes a plain password, hashes it using bcrypt, and prints the hashed password.
    
#     Args:
#         plain_password (str): The plain text password to hash.
#     """
#     hashed_password = pwd_context.hash(plain_password)
#     print(f"Plain password: {plain_password}")
#     print(f"Hashed password: {hashed_password}")

# if __name__ == "__main__":
#     password = input("Enter a password to hash: ")
#     hash_and_print_password(password)
