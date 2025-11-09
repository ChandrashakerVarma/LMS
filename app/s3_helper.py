import boto3
import os
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

# Validate environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME]):
    raise ValueError("Missing required AWS environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, or AWS_S3_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com"
)

def upload_file_to_s3(file_obj, folder, existing_key: str = None):
    """
    Uploads file to S3 and returns the file URL.
    If existing_key is provided, overwrite the same file.
    """
    try:
        # Validate file extension
        allowed_extensions = ["pdf", "jpg", "jpeg", "png"]
        file_extension = file_obj.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

        # Validate file size (max 25MB)
        file_obj.file.seek(0, 2)
        file_size = file_obj.file.tell()
        if file_size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 25MB limit")
        file_obj.file.seek(0)

        # Use same key if provided, else generate new
        if existing_key:
            s3_key = existing_key
        else:
            s3_key = f"{folder}/{uuid4()}.{file_extension}"

        # Upload (this will overwrite if key already exists)
        s3_client.upload_fileobj(file_obj.file, BUCKET_NAME, s3_key)

        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return file_url

    except boto3.exceptions.S3UploadFailedError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
