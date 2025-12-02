# app/utils/s3_utils.py

import boto3
from uuid import uuid4
from mimetypes import guess_type
from app.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

def upload_organization_logo(file_content: bytes, filename: str) -> str:
    """
    Upload organization logo to S3 and return public URL.
    Bucket must handle access via policies, not ACLs.
    """

    content_type, _ = guess_type(filename)
    content_type = content_type or "application/octet-stream"

    unique_filename = f"organization_logos/{uuid4()}_{filename}"

    # Remove ACL parameter
    s3_client.put_object(
        Bucket=settings.AWS_BUCKET_NAME,
        Key=unique_filename,
        Body=file_content,
        ContentType=content_type
    )

    return (
        f"https://{settings.AWS_BUCKET_NAME}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
    )
