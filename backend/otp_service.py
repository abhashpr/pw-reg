"""OTP generation and verification service."""

import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User, OTPCode
from config import get_settings
from typing import Optional
import logging

logger = logging.getLogger("otp_service")


class OTPService:
    """Service for generating and verifying OTP codes."""
    
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a 6-digit OTP.
        
        Returns:
            6-digit OTP as string
        """
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_otp(db: Session, email: str, user_id: Optional[int] = None) -> Optional[OTPCode]:
        """
        Create and store a new OTP for given email.
        
        Args:
            db: Database session
            email: Email address
            user_id: Optional user ID
            
        Returns:
            OTPCode object if created, None if rate limited
        """
        settings = get_settings()
        
        # Check if OTP was recently sent (rate limiting)
        recent_otp = db.query(OTPCode).filter(
            OTPCode.email == email
        ).order_by(OTPCode.created_at.desc()).first()
        
        if recent_otp:
            time_diff = datetime.utcnow() - recent_otp.created_at
            if time_diff.total_seconds() < settings.otp_rate_limit_seconds:
                logger.warning(f"OTP rate limit exceeded for {email}")
                return None
        
        # Clean up old OTPs
        db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.expiry < datetime.utcnow()
        ).delete()
        db.commit()
        
        # Generate new OTP
        otp_code = OTPService.generate_otp()
        expiry = datetime.utcnow() + timedelta(minutes=settings.otp_expiry_minutes)
        
        otp = OTPCode(
            user_id=user_id,
            email=email,
            otp=otp_code,
            expiry=expiry
        )
        
        db.add(otp)
        db.commit()
        db.refresh(otp)
        
        logger.info(f"OTP created for {email}")
        return otp
    
    @staticmethod
    def verify_otp(db: Session, email: str, otp_code: str) -> bool:
        """
        Verify OTP code.
        
        Args:
            db: Database session
            email: Email address
            otp_code: OTP to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """
        otp = db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.otp == otp_code
        ).first()
        
        if not otp:
            logger.warning(f"OTP not found for {email}")
            return False
        
        if otp.expiry < datetime.utcnow():
            logger.warning(f"OTP expired for {email}")
            db.delete(otp)
            db.commit()
            return False
        
        logger.info(f"OTP verified for {email}")
        return True
    
    @staticmethod
    def delete_otp(db: Session, email: str, otp_code: str) -> None:
        """
        Delete OTP after successful verification.
        
        Args:
            db: Database session
            email: Email address
            otp_code: OTP to delete
        """
        db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.otp == otp_code
        ).delete()
        db.commit()

        """
        Create and store a new OTP for given email.
        
        Args:
            db: Database session
            email: Email address
            user_id: Optional user ID
            
        Returns:
            OTPCode object if created, None if rate limited
        """
        settings = get_settings()
        
        # Check if OTP was recently sent (rate limiting)
        recent_otp = db.query(OTPCode).filter(
            OTPCode.email == email
        ).order_by(OTPCode.created_at.desc()).first()
        
        if recent_otp:
            time_diff = datetime.utcnow() - recent_otp.created_at
            if time_diff.total_seconds() < settings.otp_rate_limit_seconds:
                logger.warning(f"OTP rate limit exceeded for {email}")
                return None
        
        # Clean up old OTPs
        db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.expiry < datetime.utcnow()
        ).delete()
        db.commit()
        
        # Generate new OTP
        otp_code = OTPService.generate_otp()
        expiry = datetime.utcnow() + timedelta(minutes=settings.otp_expiry_minutes)
        
        otp = OTPCode(
            user_id=user_id,
            email=email,
            otp=otp_code,
            expiry=expiry
        )
        
        db.add(otp)
        db.commit()
        db.refresh(otp)
        
        logger.info(f"OTP created for {email}")
        return otp
    
    @staticmethod
    def verify_otp(db: Session, email: str, otp_code: str) -> bool:
        """
        Verify OTP code.
        
        Args:
            db: Database session
            email: Email address
            otp_code: OTP to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """
        otp = db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.otp == otp_code
        ).first()
        
        if not otp:
            logger.warning(f"OTP not found for {email}")
            return False
        
        if otp.expiry < datetime.utcnow():
            logger.warning(f"OTP expired for {email}")
            db.delete(otp)
            db.commit()
            return False
        
        logger.info(f"OTP verified for {email}")
        return True
    
    @staticmethod
    def delete_otp(db: Session, email: str, otp_code: str) -> None:
        """
        Delete OTP after successful verification.
        
        Args:
            db: Database session
            email: Email address
            otp_code: OTP to delete
        """
        db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.otp == otp_code
        ).delete()
        db.commit()
