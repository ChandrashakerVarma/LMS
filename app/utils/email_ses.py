import boto3
from botocore.exceptions import ClientError
from app.config import settings


def send_email_ses(subject: str, body: str, to_email: str):
    """
    Sends an email using Amazon SES.
    """
    client = boto3.client(
        "ses",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        response = client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": body}},
            },
        )
        return response

    except ClientError as e:
        print("SES Email Error:", e.response["Error"]["Message"])
        return None
