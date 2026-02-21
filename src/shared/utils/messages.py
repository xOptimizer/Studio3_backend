"""Message constants for API responses."""

# Generic
INTERNAL_SERVER_ERROR = "Something went wrong."
UNAUTHORIZED = "Unauthorized."
FORBIDDEN = "Forbidden."

# Auth
OTP_SENT = "OTP sent successfully."
OTP_VERIFICATION_FAILED = "Invalid or expired OTP."
EMAIL_REQUIRED = "Email is required."
INVALID_CREDENTIALS = "Invalid email or password."
USER_ALREADY_EXISTS = "User with this email already exists."
REGISTRATION_SUCCESS = "Registration successful."
LOGIN_SUCCESS = "Login successful."
LOGOUT_SUCCESS = "Logout successful."
LOGOUT_ALL_SUCCESS = "Logged out from all devices."
REFRESH_SUCCESS = "Token refreshed."
PASSWORD_RESET_EMAIL_SENT = "If an account exists with this email, you will receive a password reset link."
PASSWORD_RESET_SUCCESS = "Password has been reset successfully."
INVALID_RESET_TOKEN = "Invalid or expired reset token."

# User
USERS_FETCHED = "Users fetched successfully."
