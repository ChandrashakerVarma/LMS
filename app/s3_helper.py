import boto3
from uuid import uuid4
from fastapi import HTTPException
from app.config import settings

# -----------------------------
# S3 CLIENT FOR RESUME UPLOADS
# -----------------------------
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID_RESUME,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_RESUME,
    region_name=settings.AWS_REGION_RESUME,
)

def upload_file_to_s3(file, folder):
    try:
        if not file.filename or "." not in file.filename:
            raise HTTPException(status_code=400, detail="File must have an extension")

        ext = file.filename.split(".")[-1].lower()

        allowed = ["pdf", "jpg", "jpeg", "png"]
        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Unique filename
        key = f"{folder}/{uuid4()}.{ext}"

        # Upload
        s3_client.upload_fileobj(
            file.file,
            settings.BUCKET_NAME_RESUME,
            key
        )

        # Public URL
        file_url = (
            f"https://{settings.BUCKET_NAME_RESUME}.s3."
            f"{settings.AWS_REGION_RESUME}.amazonaws.com/{key}"
        )

        return file_url

    except Exception as e:
<<<<<<< HEAD
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
=======
        raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
>>>>>>> origin/main
