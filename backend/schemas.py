"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re

ALLOWED_MEDIUMS = {"Hindi", "English"}
ALLOWED_COURSES = {
    "Engineering (JEE)",
    "Medical (NEET)",
    "Foundation (Class 6-10)",
}
# Name: letters (including Indian Unicode), spaces, dots, hyphens, apostrophes
NAME_RE = re.compile(r"^[\w\s.\-']+$", re.UNICODE)


class SendOTPRequest(BaseModel):
    """Request for sending OTP."""
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Request for verifying OTP."""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegistrationCreate(BaseModel):
    """Registration form input."""
    name: str = Field(..., min_length=1, max_length=200)
    father_name: str = Field(..., min_length=1, max_length=200)
    medium: str = Field(..., min_length=1, max_length=100)
    course: str = Field(..., min_length=1, max_length=100)
    exam_centre: str = Field(..., min_length=1, max_length=200)
    exam_date: str = Field(..., min_length=1, max_length=100)
    exam_time: str = Field(..., min_length=1, max_length=200)

    @field_validator("name", "father_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not NAME_RE.match(v):
            raise ValueError("Only letters, spaces, dots, hyphens and apostrophes are allowed")
        return v

    @field_validator("medium")
    @classmethod
    def validate_medium(cls, v: str) -> str:
        v = v.strip()
        if v not in ALLOWED_MEDIUMS:
            raise ValueError(f"Medium must be one of: {', '.join(ALLOWED_MEDIUMS)}")
        return v

    @field_validator("course")
    @classmethod
    def validate_course(cls, v: str) -> str:
        v = v.strip()
        if v not in ALLOWED_COURSES:
            raise ValueError(f"Course must be one of: {', '.join(ALLOWED_COURSES)}")
        return v

    @field_validator("exam_centre", "exam_date", "exam_time")
    @classmethod
    def strip_field(cls, v: str) -> str:
        return v.strip()


class RegistrationUpdate(BaseModel):
    """Registration form update (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    father_name: Optional[str] = Field(None, min_length=1, max_length=200)
    medium: Optional[str] = Field(None, min_length=1, max_length=100)
    course: Optional[str] = Field(None, min_length=1, max_length=100)
    exam_centre: Optional[str] = Field(None, min_length=1, max_length=200)
    exam_date: Optional[str] = Field(None, max_length=100)
    exam_time: Optional[str] = Field(None, max_length=200)


class RegistrationResponse(BaseModel):
    """Registration response schema."""
    id: int
    user_id: int
    roll_no: str
    name: str
    father_name: str
    medium: str
    course: str
    exam_centre: str
    exam_date: str
    exam_time: Optional[str] = ""
    admit_card_sent: bool = False
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdmitCardData(BaseModel):
    """Data for admit card generation."""
    roll_no: str
    name: str
    father_name: str
    medium: str
    course: str
    exam_centre: str
    exam_date: str
    exam_time: Optional[str] = ""
