import os
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from app.config import settings
import boto3

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID_RESUME,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_RESUME,
    region_name=settings.AWS_REGION_RESUME,
)

def upload_file_to_s3(file: UploadFile, folder: str) -> str:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="File is required")

    filename = file.filename.split(";")[0]
    ext = os.path.splitext(filename)[1].lower().replace(".", "")

    allowed = {"pdf", "jpg", "jpeg", "png"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed)}"
        )

    key = f"{folder}/{uuid4()}.{ext}"

    s3_client.upload_fileobj(
        file.file,
        settings.BUCKET_NAME_RESUME,
        key,
        ExtraArgs={"ContentType": file.content_type}
    )

    return (
        f"https://{settings.BUCKET_NAME_RESUME}.s3."
        f"{settings.AWS_REGION_RESUME}.amazonaws.com/{key}"
    )
