import sendgrid
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from app.core.security import create_email_verification_token
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            self.sg = None
            logger.warning("SendGrid API key not configured. Email sending disabled.")

    def send_email_verification(self, email: str, name: str) -> bool:
        """Send email verification link to new employee"""
        if not self.sg:
            logger.info(f"Would send email verification to {email} (SendGrid not configured)")
            return True
            
        token = create_email_verification_token(email)
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=email,
            subject=f"Welcome to {settings.APP_NAME} - Verify Your Email",
            html_content=f"""
            <h2>Welcome to {settings.APP_NAME}, {name}!</h2>
            <p>You have been invited to join our time tracking platform.</p>
            <p>Please click the link below to verify your email and set up your password:</p>
            <p><a href="{verification_link}">Verify Email & Set Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't expect this email, please ignore it.</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            logger.info(f"Email verification sent to {email}. Status: {response.status_code}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send email verification to {email}: {str(e)}")
            return False

    def send_password_reset(self, email: str, name: str) -> bool:
        """Send password reset link"""
        if not self.sg:
            logger.info(f"Would send password reset to {email} (SendGrid not configured)")
            return True
            
        token = create_email_verification_token(email)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=email,
            subject=f"{settings.APP_NAME} - Password Reset",
            html_content=f"""
            <h2>Password Reset Request</h2>
            <p>Hello {name},</p>
            <p>You requested a password reset for your {settings.APP_NAME} account.</p>
            <p>Please click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this, please ignore this email.</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            logger.info(f"Password reset sent to {email}. Status: {response.status_code}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send password reset to {email}: {str(e)}")
            return False


email_service = EmailService()