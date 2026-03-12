"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas import SendOTPRequest, VerifyOTPRequest, TokenResponse
from models import User
from otp_service import OTPService
from email_service import email_service
from auth import AuthService, create_or_get_user
from config import get_settings
from rate_limit import rate_limit
import logging

logger = logging.getLogger("auth_routes")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp")
@rate_limit(5, 60)
async def send_otp(
    request: Request,
    payload: SendOTPRequest,
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
    email = payload.email.lower().strip()
    settings = get_settings()

    # Determine if this OTP request is for admin flow. Admin flow requires a pre-generated token
    # and the email must be one of the configured admin emails.
    is_admin_intent = bool(payload.admin) or (request.query_params.get('admin') == '1')

    if is_admin_intent:
        # Ensure admin access token is configured on the server
        if not settings.admin_access_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access token not configured on server"
            )

        # Validate provided admin token
        if not payload.admin_token or payload.admin_token != settings.admin_access_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin access token"
            )

        # Ensure the email is authorized as an admin email
        allowed_admins = [e.lower() for e in (settings.admin_emails or [settings.sender_email])]
        if email not in allowed_admins:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not authorized for admin access"
            )

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
@rate_limit(10, 60)
async def verify_otp(
    request: Request,
    payload: VerifyOTPRequest,
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
    email = payload.email.lower().strip()
    otp_code = payload.otp.strip()
    
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
    authorization: Optional[str] = Header(None)
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
        "is_admin": user.email.lower() in [e.lower() for e in (get_settings().admin_emails or [get_settings().sender_email])],
        "created_at": user.created_at.isoformat()
    }
