"""Send email via AWS SES (from env)."""
import os

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "")


def _get_ses_client():
    import boto3

    return boto3.client(
        "ses",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def send_email(to: str, subject: str, html: str) -> bool:
    """Send email with given HTML body via SES. Returns True on success."""
    if not SES_FROM_EMAIL:
        logger.warning("SES_FROM_EMAIL not configured; skipping email to %s", to)
        return False
    try:
        client = _get_ses_client()
        client.send_email(
            Source=SES_FROM_EMAIL,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html}},
            },
        )
        return True
    except Exception as e:
        logger.exception("Failed to send email to %s: %s", to, e)
        return False
