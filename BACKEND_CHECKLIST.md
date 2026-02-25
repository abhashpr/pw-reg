# Backend Integration Checklist

Complete checklist for backend verification.

## Python Environment

- [ ] Python 3.9+ installed
- [ ] `python --version` shows correct version
- [ ] pip upgraded: `pip install --upgrade pip`

## Project Structure

### Core Files
- [ ] `main.py` - FastAPI app entry point
- [ ] `database.py` - SQLAlchemy setup
- [ ] `config.py` - Environment configuration
- [ ] `models.py` - ORM models
- [ ] `schemas.py` - Pydantic schemas
- [ ] `auth.py` - JWT management
- [ ] `otp_service.py` - OTP logic
- [ ] `email_service.py` - Email sending
- [ ] `admit_card.py` - PDF generation

### Routers
- [ ] `routers/auth_routes.py`
  - [ ] POST `/auth/send-otp`
  - [ ] POST `/auth/verify-otp`
  - [ ] GET `/auth/me`
- [ ] `routers/registration_routes.py`
  - [ ] POST `/registration/`
  - [ ] GET `/registration/`
  - [ ] GET `/registration/admit-card`

## Database Models

### User Table
- [ ] id (PK)
- [ ] email (UNIQUE)
- [ ] is_verified
- [ ] created_at, updated_at

### OTPCode Table
- [ ] id (PK)
- [ ] user_id (FK)
- [ ] email
- [ ] otp (6 digits)
- [ ] expiry
- [ ] created_at

### Registration Table
- [ ] id (PK)
- [ ] user_id (UNIQUE FK)
- [ ] roll_no (UNIQUE) [NSAT2026-XXXX format]
- [ ] name, father_name, medium, course, exam_date, exam_centre
- [ ] created_at, updated_at

## Pydantic Schemas

- [ ] SendOTPRequest - email validation
- [ ] VerifyOTPRequest - email + 6-digit OTP
- [ ] TokenResponse - JWT token
- [ ] RegistrationCreate - all 6 fields required
- [ ] RegistrationUpdate - all fields optional
- [ ] RegistrationResponse - with roll_no
- [ ] AdmitCardData - for PDF generation

## Authentication

- [ ] JWT token generation ✅
- [ ] Token expiry handling ✅
- [ ] Token verification ✅
- [ ] Route protection ✅
- [ ] Bearer token parsing ✅

## OTP Service

- [ ] 6-digit generation ✅
- [ ] 5-minute expiry ✅
- [ ] 60-second rate limiting ✅
- [ ] Expiry cleanup ✅
- [ ] Verification logic ✅

## Email Service

- [ ] Gmail SMTP connection ✅
- [ ] Credentials from env ✅
- [ ] OTP email template ✅
- [ ] Error handling ✅
- [ ] Fallback when credentials not set ✅

## PDF Generation

- [ ] reportlab imported ✅
- [ ] A4 page size ✅
- [ ] All fields positioned cleanly ✅
- [ ] Instructions section ✅
- [ ] Signature placeholders ✅
- [ ] Generated on-demand (not pre-stored) ✅

## API Endpoints

### Auth Endpoints
- [ ] POST `/auth/send-otp`
  - [ ] Accepts email
  - [ ] Rate limits OTP
  - [ ] Sends email
  - [ ] Returns 429 if rate limited
  - [ ] Returns 200 on success

- [ ] POST `/auth/verify-otp`
  - [ ] Accepts email + otp
  - [ ] Validates format
  - [ ] Checks expiry
  - [ ] Creates/marks user
  - [ ] Returns JWT token
  - [ ] Deletes used OTP

- [ ] GET `/auth/me`
  - [ ] Requires Bearer token
  - [ ] Returns user data
  - [ ] Returns 401 if invalid token

### Registration Endpoints
- [ ] POST `/registration/`
  - [ ] Requires auth
  - [ ] Creates if new
  - [ ] Updates if exists
  - [ ] Generates roll_no once (never changes)
  - [ ] Returns registration with roll_no

- [ ] GET `/registration/`
  - [ ] Requires auth
  - [ ] Returns user's registration
  - [ ] Returns 404 if not exists

- [ ] GET `/registration/admit-card`
  - [ ] Requires auth
  - [ ] Returns PDF file (application/pdf)
  - [ ] Filename: admit_card_NSAT2026-XXXX.pdf
  - [ ] Generated on-demand

## Configuration

- [ ] `.env.example` provided ✅
- [ ] All secrets from env vars ✅
- [ ] Debug mode configurable ✅
- [ ] CORS origins configurable ✅

## Health Checks

- [ ] GET `/` - root endpoint ✅
- [ ] GET `/health` - health check ✅
- [ ] GET `/docs` - API documentation ✅

## Validation

- [ ] Email validation (Pydantic EmailStr)
- [ ] OTP length validation (6 digits only)
- [ ] Form field validation
- [ ] Date format validation
- [ ] Required field checking

## Error Handling

- [ ] 400 - Bad Request (validation)
- [ ] 401 - Unauthorized (invalid/missing token)
- [ ] 404 - Not Found (no registration)
- [ ] 429 - Rate Limited (OTP)
- [ ] 500 - Server Error (db, email errors)
- [ ] Global exception handler in place

## Logging

- [ ] Structured logging configured
- [ ] Info logs for key actions
- [ ] Warning logs for issues
- [ ] Error logs for failures

## Dependencies

All in `requirements.txt`:
- [ ] fastapi
- [ ] uvicorn
- [ ] sqlalchemy
- [ ] pydantic
- [ ] python-jose (JWT)
- [ ] reportlab (PDF)
- [ ] python-dotenv
- [ ] email-validator

## Testing

- [ ] Curl commands work
- [ ] Send OTP endpoint working
- [ ] Verify OTP endpoint working
- [ ] Registration CRUD working
- [ ] PDF generation working
- [ ] Database auto-creates

## Performance

- [ ] Startup time < 5 seconds
- [ ] API response < 500ms
- [ ] PDF generation < 2 seconds
- [ ] OTP email < 2 seconds
- [ ] Database queries optimized (indexed)

## Security

- [ ] HTTPS ready (reverse proxy agnostic)
- [ ] JWT validation on all protected endpoints
- [ ] OTP expiry enforced
- [ ] Rate limiting implemented
- [ ] SQL injection prevented (SQLAlchemy ORM)
- [ ] CORS properly configured
- [ ] Secrets in environment vars
- [ ] User can only access own data

## Deployment Readiness

- [ ] Database creates automatically ✅
- [ ] No hardcoded secrets ✅
- [ ] Logging to console/file ✅
- [ ] Graceful error handling ✅
- [ ] Systemd service file provided ✅
- [ ] nginx config provided ✅

---

**Status**: Production-ready ✅
