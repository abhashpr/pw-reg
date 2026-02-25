"""Email service for sending OTP via Gmail SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_settings
import logging

logger = logging.getLogger("email_service")


class EmailService:
    """Service for sending emails via Gmail SMTP."""
    
    def __init__(self):
        """Initialize email service with Gmail credentials."""
        self.settings = get_settings()
        self.smtp_server = self.settings.smtp_server
        self.smtp_port = self.settings.smtp_port
        self.sender_email = self.settings.sender_email
        self.sender_password = self.settings.sender_password
    
    def send_otp_email(self, recipient_email: str, otp: str) -> bool:
        """
        Send OTP via email.
        
        Args:
            recipient_email: Email to send OTP to
            otp: The OTP code (6 digits)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Check if credentials are configured
            if not self.sender_email or not self.sender_password:
                logger.error("Email credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "PWNSAT - Your OTP Code"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Email body
            text = f"""\
            Hi,
            
            Your One-Time Password (OTP) for PWNSAT Registration is:
            
            {otp}
            
            This OTP is valid for 5 minutes.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            PWNSAT Registration System
            """
            
            html = f"""\
            <html>
              <body>
                <p>Hi,</p>
                <p>Your One-Time Password (OTP) for PWNSAT Registration is:</p>
                <h2 style="font-family: monospace; letter-spacing: 5px; color: #0066cc;">{otp}</h2>
                <p><strong>This OTP is valid for 5 minutes.</strong></p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>Best regards,<br/>PWNSAT Registration System</p>
              </body>
            </html>
            """
            
            # Attach parts
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            logger.info(f"OTP email sent successfully to {recipient_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {recipient_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
