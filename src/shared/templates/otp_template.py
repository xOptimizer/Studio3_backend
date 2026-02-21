"""OTP email HTML template."""


def get_otp_html(otp: str) -> str:
    """Return inline HTML for OTP email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Your OTP</title></head>
    <body style="font-family: sans-serif; padding: 20px;">
        <h2>Verification Code</h2>
        <p>Your one-time password is:</p>
        <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">{otp}</p>
        <p>This code expires in 5 minutes. Do not share it with anyone.</p>
    </body>
    </html>
    """
