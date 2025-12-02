# app/utils/s3_utils.py

import boto3
from uuid import uuid4
from fastapi import HTTPException
from app.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)
def upload_file_to_s3(file, folder):
    try:
        if not file.filename or "." not in file.filename:
            raise HTTPException(status_code=400, detail="File must have an extension")

        ext = file.filename.split(".")[-1].lower()
        allowed = ["pdf", "jpg", "jpeg", "png"]
        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid file type")

        key = f"{folder}/{uuid4()}.{ext}"
        s3_client.upload_fileobj(file.file, settings.AWS_BUCKET_NAME, key)

        # Optional: Pre-signed URL for private bucket
        # file_url = s3_client.generate_presigned_url(
        #     'get_object',
        #     Params={'Bucket': settings.BUCKET_NAME, 'Key': key},
        #     ExpiresIn=3600
        # )

        file_url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return file_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
