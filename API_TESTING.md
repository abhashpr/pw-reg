# API Testing Guide

Test the PWNSAT Registration System API using curl and other tools.

## Prerequisites

- Backend running on `http://localhost:8000`
- curl installed (or use Postman/Insomnia)
- Real email for OTP testing (or use test account)

## API Endpoints

Base URL: `http://localhost:8000`

## 🔐 Authentication Endpoints

### 1. Send OTP

Send a 6-digit code to user's email.

**Endpoint**: `POST /auth/send-otp`

**Request**:
```bash
curl -X POST http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Response** (200):
```json
{
  "message": "OTP sent successfully",
  "email": "test@example.com"
}
```

**Response** (429 - Rate Limited):
```json
{
  "detail": "Please wait before requesting another OTP"
}
```

---

### 2. Verify OTP

Verify OTP code and get JWT token.

**Endpoint**: `POST /auth/verify-otp`

**Request**:
```bash
curl -X POST http://localhost:8000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response** (401 - Invalid OTP):
```json
{
  "detail": "Invalid or expired OTP"
}
```

---

### 3. Get Current User

Get authenticated user's profile.

**Endpoint**: `GET /auth/me`

**Headers**: `Authorization: Bearer <access_token>`

**Request**:
```bash
# Save token from verify-otp
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200):
```json
{
  "id": 1,
  "email": "test@example.com",
  "is_verified": true,
  "created_at": "2024-02-25T10:30:00"
}
```

---

## 📝 Registration Endpoints

All below endpoints require JWT token (`Authorization: Bearer <token>`)

### 4. Create/Update Registration

Create new or update existing registration form.

**Endpoint**: `POST /registration/`

**Request**:
```bash
export TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/registration/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "father_name": "Jane Doe",
    "medium": "English",
    "course": "Engineering",
    "exam_date": "2024-03-15",
    "exam_centre": "Centre A, Delhi"
  }'
```

**Response** (200):
```json
{
  "id": 1,
  "user_id": 1,
  "roll_no": "NSAT2026-0001",
  "name": "John Doe",
  "father_name": "Jane Doe",
  "medium": "English",
  "course": "Engineering",
  "exam_date": "2024-03-15",
  "exam_centre": "Centre A, Delhi",
  "updated_at": "2024-02-25T10:35:00"
}
```

**Note**: Roll number is generated once and doesn't change on updates.

---

### 5. Get Registration

Fetch user's saved registration.

**Endpoint**: `GET /registration/`

**Request**:
```bash
curl -X GET http://localhost:8000/registration/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200):
```json
{
  "id": 1,
  "user_id": 1,
  "roll_no": "NSAT2026-0001",
  "name": "John Doe",
  "father_name": "Jane Doe",
  "medium": "English",
  "course": "Engineering",
  "exam_date": "2024-03-15",
  "exam_centre": "Centre A, Delhi",
  "updated_at": "2024-02-25T10:35:00"
}
```

**Response** (404 - Not registered):
```json
{
  "detail": "Registration not found. Please fill the form first."
}
```

---

### 6. Download Admit Card (PDF)

Generate and download admit card as PDF.

**Endpoint**: `GET /registration/admit-card`

**Request**:
```bash
curl -X GET http://localhost:8000/registration/admit-card \
  -H "Authorization: Bearer $TOKEN" \
  -o admit_card.pdf
```

**Response**: PDF file (application/pdf)
- Filename: `admit_card_NSAT2026-0001.pdf`
- Generated on-demand (not pre-generated)
- Includes all registration details

---

## 🧪 Complete Test Flow

Here's a complete flow to test the entire system:

```bash
#!/bin/bash

API="http://localhost:8000"
EMAIL="test@example.com"

echo "1️⃣  Sending OTP..."
curl -X POST $API/auth/send-otp \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\"}"

# ⏸️  Check email for OTP code
read -p "Enter OTP from email: " OTP

echo ""
echo "2️⃣  Verifying OTP..."
RESPONSE=$(curl -s -X POST $API/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"otp\": \"$OTP\"}")

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

echo ""
echo "3️⃣  Getting user profile..."
curl -s -X GET $API/auth/me \
  -H "Authorization: Bearer $TOKEN" | json_pp

echo ""
echo "4️⃣  Creating registration..."
curl -s -X POST $API/registration/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "father_name": "Parent Name",
    "medium": "English",
    "course": "Science",
    "exam_date": "2024-03-20",
    "exam_centre": "Centre A"
  }' | json_pp

echo ""
echo "5️⃣  Getting registration..."
curl -s -X GET $API/registration/ \
  -H "Authorization: Bearer $TOKEN" | json_pp

echo ""
echo "6️⃣  Downloading admit card..."
curl -X GET $API/registration/admit-card \
  -H "Authorization: Bearer $TOKEN" \
  -o admit_card.pdf

echo "✅ Admit card saved as admit_card.pdf"
```

Save as `test_api.sh` and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 🔧 Testing Tools

### Postman Collection

Create a new Postman collection with these requests:

**Auth - Send OTP**
- Method: POST
- URL: `{{base_url}}/auth/send-otp`
- Body (JSON):
```json
{
  "email": "test@example.com"
}
```

**Auth - Verify OTP**
- Method: POST
- URL: `{{base_url}}/auth/verify-otp`
- Body (JSON):
```json
{
  "email": "test@example.com",
  "otp": "123456"
}
```

**Auth - Get Me**
- Method: GET
- URL: `{{base_url}}/auth/me`
- Headers: `Authorization: Bearer {{token}}`

**Registration - Create**
- Method: POST
- URL: `{{base_url}}/registration/`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
```json
{
  "name": "John Doe",
  "father_name": "Jane Doe",
  "medium": "English",
  "course": "Engineering",
  "exam_date": "2024-03-15",
  "exam_centre": "Centre A"
}
```

**Registration - Get**
- Method: GET
- URL: `{{base_url}}/registration/`
- Headers: `Authorization: Bearer {{token}}`

**Registration - Download Admit Card**
- Method: GET
- URL: `{{base_url}}/registration/admit-card`
- Headers: `Authorization: Bearer {{token}}`

---

## 📊 Error Responses

### 400 - Bad Request

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### 401 - Unauthorized

```json
{
  "detail": "Invalid or expired token"
}
```

### 404 - Not Found

```json
{
  "detail": "Registration not found. Please fill the form first."
}
```

### 429 - Too Many Requests (Rate Limited)

```json
{
  "detail": "Please wait before requesting another OTP"
}
```

### 500 - Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## 🔍 Debugging Tips

### 1. Check Backend Logs

```bash
# Terminal where backend is running
# Look for:
# - "OTP created for..."
# - "OTP verified for..."
# - "User verified and logged in..."
# - "Registration created..."
# - "Admit card generated..."
```

### 2. Check Token Claims

Decode JWT token at https://jwt.io:
- Copy `access_token` from verify-otp response
- Paste in jwt.io decoder
- Should see:
  - `sub`: email
  - `user_id`: integer
  - `exp`: expiry timestamp

### 3. Database Check

```bash
# Check SQLite database
sqlite3 backend/data/app.db

# List tables
.tables

# Count users
SELECT COUNT(*) FROM users;

# View registrations
SELECT roll_no, name FROM registrations;
```

### 4. Network Debug

```bash
# See all request/response details
curl -v http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## ✅ Test Checklist

- [ ] Send OTP returns 200
- [ ] Email received in inbox
- [ ] Verify OTP with correct code works
- [ ] Invalid OTP returns 401
- [ ] Expired OTP returns 401
- [ ] Rate limit works (2nd OTP in <60s returns 429)
- [ ] JWT token is valid
- [ ] Get user with token works
- [ ] Get user without token returns 401
- [ ] Create registration works
- [ ] Roll number format is NSAT2026-XXXX
- [ ] Get registration returns saved data
- [ ] Update registration preserves roll number
- [ ] Download PDF returns file
- [ ] PDF is valid and readable

---

**API Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)
