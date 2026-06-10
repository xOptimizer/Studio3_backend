"""boto3 S3 client factory."""

import os


def get_s3_client():
    import boto3

    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def get_bucket() -> str:
    return os.getenv("S3_BUCKET") or os.getenv("STUDIO3_S3_BUCKET", "")


def get_public_base_url() -> str:
    explicit = os.getenv("S3_PUBLIC_BASE_URL") or os.getenv("STUDIO3_S3_PUBLIC_BASE_URL")
    if explicit:
        return explicit
    bucket = get_bucket()
    return f"https://{bucket}.s3.amazonaws.com" if bucket else ""


def s3_configured() -> bool:
    return bool(get_bucket())
