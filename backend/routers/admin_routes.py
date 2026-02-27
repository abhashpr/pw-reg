"""Admin routes - restricted to SENDER_EMAIL only."""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, Registration
from auth import AuthService
from admit_card import AdmitCardGenerator
from email_service import email_service
from config import get_settings
from typing import Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger("admin_routes")

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Response schemas ──────────────────────────────────────────────────────────

class RegistrationDetail(BaseModel):
    roll_no: str
    name: str
    father_name: str
    medium: str
    course: str
    exam_date: str
    exam_centre: str

    model_config = {"from_attributes": True}


class UserAdminRow(BaseModel):
    id: int
    email: str
    is_verified: bool
    registration: Optional[RegistrationDetail] = None

    model_config = {"from_attributes": True}


# ── Dependency: admin-only guard ──────────────────────────────────────────────

def get_admin_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    """Only allow access to the SENDER_EMAIL account."""
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

    settings = get_settings()
    if user.email.lower() != settings.sender_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )

    return user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserAdminRow])
async def list_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Return all users with their registration details."""
    users = db.query(User).order_by(User.id.desc()).all()
    return [UserAdminRow.model_validate(u) for u in users]


@router.get("/users/{user_id}/admit-card")
async def admin_download_admit_card(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Download admit card PDF for any registered user."""
    registration = db.query(Registration).filter(
        Registration.user_id == user_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found for this user"
        )

    pdf_buffer = AdmitCardGenerator.generate_pdf(
        roll_no=registration.roll_no,
        name=registration.name,
        father_name=registration.father_name,
        medium=registration.medium,
        course=registration.course,
        exam_centre=registration.exam_centre,
        exam_date=registration.exam_date,
        exam_time=registration.exam_time or ""
    )
    pdf_buffer.seek(0)

    filename = f"admit_card_{registration.roll_no}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/users/{user_id}/send-admit-card")
async def admin_send_admit_card(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Generate and email the admit card PDF to the registered user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    registration = db.query(Registration).filter(
        Registration.user_id == user_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found for this user"
        )

    pdf_buffer = AdmitCardGenerator.generate_pdf(
        roll_no=registration.roll_no,
        name=registration.name,
        father_name=registration.father_name,
        medium=registration.medium,
        course=registration.course,
        exam_centre=registration.exam_centre,
        exam_date=registration.exam_date,
        exam_time=registration.exam_time or ""
    )
    pdf_buffer.seek(0)

    success = email_service.send_admit_card_email(
        recipient_email=user.email,
        student_name=registration.name,
        roll_no=registration.roll_no,
        pdf_bytes=pdf_buffer.read()
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

    logger.info(f"Admit card sent to {user.email} (roll: {registration.roll_no})")
    return {"message": f"Admit card sent to {user.email}"}
