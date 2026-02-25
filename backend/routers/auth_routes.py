"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import SendOTPRequest, VerifyOTPRequest, TokenResponse
from models import User
from otp_service import OTPService
from email_service import email_service
from auth import AuthService, create_or_get_user
import logging

logger = logging.getLogger("auth_routes")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp")
async def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Send OTP to email address.
    
    Args:
        request: SendOTPRequest with email
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException if email is invalid or OTP send fails
    """
    email = request.email.lower().strip()
    
    # Create or get user
    user = create_or_get_user(db, email)
    
    # Generate OTP
    otp = OTPService.create_otp(db, email, user.id)
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another OTP"
        )
    
    # Send email
    success = email_service.send_otp_email(email, otp.otp)
    
    if not success:
        logger.error(f"Failed to send OTP email to {email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again later."
        )
    
    return {"message": "OTP sent successfully", "email": email}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Verify OTP and return JWT token.
    
    Args:
        request: VerifyOTPRequest with email and OTP
        db: Database session
        
    Returns:
        TokenResponse with JWT access token
        
    Raises:
        HTTPException if OTP is invalid or expired
    """
    email = request.email.lower().strip()
    otp_code = request.otp.strip()
    
    # Verify OTP
    is_valid = OTPService.verify_otp(db, email, otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    # Get or create user
    user = create_or_get_user(db, email)
    
    # Mark user as verified
    user.is_verified = True
    db.commit()
    
    # Delete used OTP
    OTPService.delete_otp(db, email, otp_code)
    
    # Generate JWT token
    token = AuthService.create_access_token(email, user.id)
    
    logger.info(f"User verified and logged in: {email}")
    
    return TokenResponse(access_token=token)


@router.get("/me")
async def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = None
) -> dict:
    """
    Get current authenticated user.
    
    Args:
        db: Database session
        authorization: Bearer token from header
        
    Returns:
        Current user details
        
    Raises:
        HTTPException if token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Verify token and get user
    user = AuthService.get_current_user(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }
