"""Registration and admit card routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import RegistrationCreate, RegistrationUpdate, RegistrationResponse
from models import User, Registration
from auth import AuthService
from admit_card import AdmitCardGenerator
import logging
import uuid
from typing import Optional

logger = logging.getLogger("registration_routes")

router = APIRouter(prefix="/registration", tags=["registration"])


def get_current_user_from_header(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    """
    Get authenticated user from JWT token in header.
    
    Args:
        db: Database session
        authorization: Bearer token
        
    Returns:
        Current user
        
    Raises:
        HTTPException if token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    user = AuthService.get_current_user(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


def generate_roll_number(user_id: int) -> str:
    """
    Generate unique roll number for user.
    
    Format: NSAT2026-XXXX
    
    Args:
        user_id: User ID
        
    Returns:
        Roll number string
    """
    return f"NSAT2026-{user_id:04d}"


@router.post("/", response_model=RegistrationResponse)
async def create_or_update_registration(
    request: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_header)
) -> RegistrationResponse:
    """
    Create or update registration form.
    
    Args:
        request: Registration data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created/updated registration
        
    Raises:
        HTTPException if registration fails
    """
    # Check if registration already exists
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id
    ).first()
    
    if registration:
        # Update existing registration
        registration.name = request.name
        registration.father_name = request.father_name
        registration.medium = request.medium
        registration.course = request.course
        registration.exam_date = request.exam_date
        registration.exam_centre = request.exam_centre
        
        logger.info(f"Registration updated for user: {current_user.email}")
    else:
        # Create new registration
        roll_no = generate_roll_number(current_user.id)
        
        registration = Registration(
            user_id=current_user.id,
            roll_no=roll_no,
            name=request.name,
            father_name=request.father_name,
            medium=request.medium,
            course=request.course,
            exam_date=request.exam_date,
            exam_centre=request.exam_centre
        )
        
        db.add(registration)
        logger.info(f"Registration created for user: {current_user.email}, roll_no: {roll_no}")
    
    db.commit()
    db.refresh(registration)
    
    return RegistrationResponse.model_validate(registration)


@router.get("/", response_model=RegistrationResponse)
async def get_registration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_header)
) -> RegistrationResponse:
    """
    Get user's registration data.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        User's registration
        
    Raises:
        HTTPException if registration not found
    """
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found. Please fill the form first."
        )
    
    return RegistrationResponse.model_validate(registration)


@router.get("/admit-card")
async def download_admit_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_header)
):
    """
    Generate and download admit card PDF.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        PDF file response
        
    Raises:
        HTTPException if registration not found
    """
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found. Please fill the form first."
        )
    
    try:
        # Generate PDF
        pdf_buffer = AdmitCardGenerator.generate_pdf(
            roll_no=registration.roll_no,
            name=registration.name,
            father_name=registration.father_name,
            medium=registration.medium,
            course=registration.course,
            exam_date=registration.exam_date,
            exam_centre=registration.exam_centre
        )
        
        filename = f"admit_card_{registration.roll_no}.pdf"
        
        # Reset buffer position to start
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating admit card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate admit card"
        )
