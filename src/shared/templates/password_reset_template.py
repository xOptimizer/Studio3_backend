"""Password reset email HTML template."""


def get_password_reset_html(reset_url: str) -> str:
    """Return inline HTML for password reset email (link to frontend + token)."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Reset your password</title></head>
    <body style="font-family: sans-serif; padding: 20px;">
        <h2>Password Reset</h2>
        <p>You requested a password reset. Click the link below to set a new password:</p>
        <p><a href="{reset_url}" style="color: #0066cc;">Reset password</a></p>
        <p>This link expires in 1 hour. If you did not request this, ignore this email.</p>
    </body>
    </html>
    """
