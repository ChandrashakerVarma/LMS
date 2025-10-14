from dotenv import load_dotenv
import os
from uuid import uuid4
import boto3
from fastapi import HTTPException
from urllib.parse import urlparse
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")

# Validate env variables
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME]):
    missing = [v for v in ["AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_REGION","AWS_S3_BUCKET"]
               if not os.getenv(v)]
    raise ValueError(f"Missing required AWS environment variables: {', '.join(missing)}")

# Create S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_resume(file_obj, folder="resumes", existing_key: str = None):
    """
    Uploads a file to S3. Returns the public URL.
    """
    try:
        # Validate extension
        allowed_extensions = ["pdf", "jpg", "jpeg", "png"]
        extension = file_obj.filename.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {extension}")

        # Validate file size (max 25MB)
        file_obj.file.seek(0, 2)
        size = file_obj.file.tell()
        if size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 25MB")
        file_obj.file.seek(0)

        # Generate S3 key
        s3_key = existing_key if existing_key else f"{folder}/{uuid4()}.{extension}"

        # Upload
        s3_client.upload_fileobj(file_obj.file, BUCKET_NAME, s3_key)

        return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

def delete_file_from_s3(file_url: str):
    """
    Deletes a file from S3 given its URL.
    """
    try:
        parsed_url = urlparse(file_url)
        key = parsed_url.path.lstrip("/")
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        print(f"Error deleting {file_url} from S3: {e}")
        return False
