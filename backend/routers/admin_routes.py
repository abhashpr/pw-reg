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
    exam_time: Optional[str] = ""
    admit_card_sent: bool = False

    model_config = {"from_attributes": True}


class BulkUserIds(BaseModel):
    user_ids: List[int]


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

    registration.admit_card_sent = True
    db.commit()
    logger.info(f"Admit card sent to {user.email} (roll: {registration.roll_no})")
    return {"message": f"Admit card sent to {user.email}"}


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Permanently delete a user and their registration."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    logger.info(f"User {user.email} (id={user_id}) deleted by admin")
    return {"message": f"User {user.email} deleted"}


@router.post("/users/bulk-send")
async def admin_bulk_send(
    body: BulkUserIds,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Send admit card emails to multiple users."""
    sent, failed, skipped = [], [], []

    for uid in body.user_ids:
        user = db.query(User).filter(User.id == uid).first()
        reg = db.query(Registration).filter(Registration.user_id == uid).first() if user else None

        if not user or not reg:
            skipped.append(uid)
            continue

        try:
            pdf_buffer = AdmitCardGenerator.generate_pdf(
                roll_no=reg.roll_no, name=reg.name, father_name=reg.father_name,
                medium=reg.medium, course=reg.course, exam_centre=reg.exam_centre,
                exam_date=reg.exam_date, exam_time=reg.exam_time or ""
            )
            pdf_buffer.seek(0)
            ok = email_service.send_admit_card_email(
                recipient_email=user.email,
                student_name=reg.name,
                roll_no=reg.roll_no,
                pdf_bytes=pdf_buffer.read()
            )
            if ok:
                reg.admit_card_sent = True
                db.commit()
            (sent if ok else failed).append(uid)
        except Exception as e:
            logger.error(f"Bulk send failed for uid={uid}: {e}")
            failed.append(uid)

    logger.info(f"Bulk send: sent={len(sent)}, failed={len(failed)}, skipped={len(skipped)}")
    return {"message": f"Sent: {len(sent)}, Failed: {len(failed)}, Skipped (no reg): {len(skipped)}",
            "sent": sent, "failed": failed, "skipped": skipped}


@router.post("/users/bulk-delete")
async def admin_bulk_delete(
    body: BulkUserIds,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Permanently delete multiple users and their registrations."""
    deleted = []
    for uid in body.user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            db.delete(user)
            deleted.append(uid)
    db.commit()
    logger.info(f"Bulk delete: removed {len(deleted)} users")
    return {"message": f"{len(deleted)} user(s) deleted", "deleted": deleted}
