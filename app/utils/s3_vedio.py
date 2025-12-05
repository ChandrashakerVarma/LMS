# app/utils/s3.py
import boto3
import os
from uuid import uuid4
from fastapi import HTTPException
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from dotenv import load_dotenv
import os

# Force load .env from project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME]):
    raise ValueError("Missing required AWS environment variables")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_obj, folder="videos", existing_key: str = None, max_size_bytes: int = 1024*1024*1024):
    """
    Uploads file to S3 and returns dict with {s3_key, s3_url, content_type, size_bytes}.
    max_size_bytes default = 1GB (adjust as needed).
    """
    try:
        allowed_extensions = ["mp4", "mov", "mkv", "webm", "ogg", "pdf", "jpg", "jpeg", "png"]
        filename = file_obj.filename
        file_extension = filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

        # check size
        file_obj.file.seek(0, 2)
        file_size = file_obj.file.tell()
        if file_size > max_size_bytes:
            raise HTTPException(status_code=400, detail=f"File size exceeds {max_size_bytes} bytes limit")
        file_obj.file.seek(0)

        content_type = file_obj.content_type or f"video/{file_extension}"

        # key generation
        if existing_key:
            s3_key = existing_key
        else:
            s3_key = f"{folder}/{uuid4()}.{file_extension}"

        # Upload with metadata
        s3_client.upload_fileobj(
            Fileobj=file_obj.file,
            Bucket=BUCKET_NAME,
            Key=s3_key,
            ExtraArgs={"ContentType": content_type}
        )

        # optional public url (works if bucket/object is public)
        s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        return {
            "s3_key": s3_key,
            "s3_url": s3_url,
            "content_type": content_type,
            "size_bytes": file_size
        }

    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

def generate_s3_key(filename: str, course_id: int, folder: str = "videos"):
    ext = filename.split(".")[-1]
    return f"{folder}/course_{course_id}/{uuid4()}.{ext}"

def generate_presigned_post(key: str, content_type: str, expires_in: int = 3600):
    return s3_client.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}],
        ExpiresIn=expires_in,
    )

def generate_presigned_get(key: str, expires_in: int = 3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )

def upload_fileobj(file_obj, key: str, content_type: str):
    s3_client.upload_fileobj(file_obj, BUCKET_NAME, key, ExtraArgs={"ContentType": content_type})
