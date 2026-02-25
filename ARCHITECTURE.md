# Architecture & Design

High-level design of the PWNSAT Registration System.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Lightsail                             │
│  (Single Instance: 1GB RAM, 1 vCPU, Ubuntu 20.04)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐           ┌────────────────────────┐ │
│  │   NGINX (Reverse     │           │   FastAPI Backend      │ │
│  │   Proxy)             │◄────────►│   (Port 8000)          │ │
│  │   (Port 80/443)      │           │   - Auth               │ │
│  │                      │           │   - Registration       │ │
│  │ • SPA static files   │           │   - PDF Generation     │ │
│  │ • API routing        │           │   - OTP/Email          │ │
│  │ • Compression        │           │                        │ │
│  │ • SSL/TLS            │           │   Workers: 4           │ │
│  └──────────────────────┘           └────────────────────────┘
│                                              │
│                                     ┌────────▼─────────┐
│                                     │  SQLite Database │
│                                     │  (File-based)    │
│                                     │  • Users         │
│                                     │  • OTP Codes     │
│                                     │  • Registrations │
│                                     └──────────────────┘
│
│  ┌──────────────────────┐
│  │  External Services   │
│  ├──────────────────────┤
│  │  • Gmail SMTP        │
│  │    (OTP emails)      │
│  │  • reportlab         │
│  │    (PDF generation)  │
│  └──────────────────────┘
│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Client Side                              │
├─────────────────────────────────────────────────────────────────┤
│  Vue 3 SPA Application (Built to static files)                  │
│  ├─ Login Page (OTP entry)                                      │
│  ├─ OTP Verification Page                                       │
│  ├─ Registration Form                                           │
│  └─ Dashboard (View profile, Download PDF)                      │
│                                                                  │
│  Client-side Features:                                          │
│  • Local JWT token storage                                      │
│  • Route guards                                                 │
│  • Form state management                                        │
│  • API client with Axios                                        │
│  • Responsive UI                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Registration/Authentication Flow

```
User visits app
      ↓
Login Page (email input)
      ↓
User clicks "Send OTP"
      ↓
Frontend: POST /auth/send-otp {email}
      ↓
Backend: 
  - Create or find user
  - Generate 6-digit OTP
  - Check rate limit (1 OTP per 60s)
  - Save OTP with 5-min expiry
  - Send email via Gmail SMTP
      ↓
Email delivered to user's inbox
      ↓
User enters OTP on app
      ↓
Frontend: POST /auth/verify-otp {email, otp}
      ↓
Backend:
  - Check if OTP exists
  - Verify not expired
  - Mark user as verified
  - Generate JWT token
  - Delete used OTP
  - Return token
      ↓
Frontend: Store token in localStorage
      ↓
Redirect to Registration Form
```

### 2. Registration Form Flow

```
User on Registration Form
      ↓
User fills all fields:
  - Name, Father's Name
  - Medium, Course
  - Exam Date, Exam Centre
      ↓
User clicks "Save Form"
      ↓
Frontend: POST /registration/ {all fields}
  Header: Authorization: Bearer {token}
      ↓
Backend:
  - Verify JWT token
  - Check if registration exists
  - If new: Generate roll number (NSAT2026-{user_id:04d})
  - If exists: Update fields (roll number stays same)
  - Save to registrations table
  - Return registration with roll number
      ↓
Frontend: Store in local state
      ↓
Show success message
      ↓
Redirect to Dashboard
```

### 3. Admit Card Download Flow

```
User on Dashboard
      ↓
User clicks "Download Admit Card"
      ↓
Frontend: GET /registration/admit-card
  Header: Authorization: Bearer {token}
      ↓
Backend:
  - Verify JWT token
  - Get user's registration
  - Generate PDF using reportlab:
    * Create A4 page
    * Position title and fields
    * Add instructions
    * Add signature sections
    * Timestamp
  - Return as FileResponse (binary)
      ↓
Browser: Download as PDF file
  Filename: admit_card_NSAT2026-XXXX.pdf
      ↓
User has PDF locally
```

## Database Schema Relationships

```
┌─────────────┐
│    Users    │
├─────────────┤
│ id (PK)     │
│ email       │◄─────────┐
│ is_verified │          │
│ created_at  │          │
│ updated_at  │          │
└─────────────┘          │
       │                  │
       │1                 │
       │                  │
       │M                 │
┌──────────────────┐      │
│   OTP Codes      │      │
├──────────────────┤      │
│ id (PK)          │      │
│ user_id (FK)     │      │
│ email            │      │
│ otp              │      │
│ expiry           │      │
│ created_at       │      │
└──────────────────┘      │
                          │
       ┌──────────────────┘
       │1                  
       │                   
       │1                  
┌──────────────────────────────┐
│     Registrations            │
├──────────────────────────────┤
│ id (PK)                      │
│ user_id (FK, UNIQUE)         │
│ roll_no (UNIQUE) [Immutable] │
│ name                         │
│ father_name                  │
│ medium                       │
│ course                       │
│ exam_date                    │
│ exam_centre                  │
│ created_at                   │
│ updated_at                   │
└──────────────────────────────┘
```

## Authentication & Security Flow

```
1. Token Generation
   ├─ User verified OTP
   ├─ Backend creates JWT with:
   │  ├─ Email (sub claim)
   │  ├─ User ID
   │  ├─ Expiry (24 hours)
   │  └─ Issued timestamp
   └─ Signed with SECRET_KEY (HS256)

2. Token Storage
   ├─ Frontend stores in localStorage
   ├─ Included in all API requests
   └─ Vulnerable to XSS (production: use httpOnly cookies)

3. Token Validation
   ├─ Backend receives token
   ├─ Verifies signature
   ├─ Checks expiry
   ├─ Extracts user_id
   ├─ Gets user from database
   └─ Allows access

4. Token Refresh
   ├─ Current: No refresh mechanism
   ├─ User: Re-login after 24 hours
   └─ TODO: Implement refresh tokens
```

## OTP Security

```
Generation
├─ 6 random digits: 000000-999999
├─ Probability of guessing: 1 in 1,000,000
└─ Time to brute force (worst): ~8000 seconds

Expiry
├─ 5-minute window: Configurable
├─ Expired OTPs deleted automatically
└─ User: "OTP expired - request new one"

Rate Limiting
├─ Only 1 OTP per 60 seconds (per email)
├─ Prevents brute force
├─ Returns 429 Too Many Requests
└─ User: "Please wait 60 seconds..."

Storage
├─ Stored in database (not memory)
├─ Deleted after successful verification
└─ No sensitive data in logs
```

## PDF Generation

```
Trigger
├─ User clicks "Download Admit Card"
├─ Only generates if registration complete
└─ On-demand (not pre-generated)

Process
├─ Create BytesIO buffer (in-memory)
├─ Use reportlab to build PDF:
│  ├─ Document structure (Title, Details)
│  ├─ Table layouts with styling
│  ├─ Instructions section
│  ├─ Signature placeholders
│  ├─ Footer with timestamp
│  └─ Professional formatting
└─ Return as FileResponse (binary)

Performance
├─ Generation time: 1-2 seconds
├─ Memory efficient (not saved to disk)
├─ PDF destroyed after download
└─ Scale to 5000 concurrent users: No problem

Customization
├─ Title: "PWNSAT ADMIT CARD"
├─ Fields: All 7 registration fields
├─ Color: Professional blue (#1f4788)
├─ Layout: Centered, clean, print-friendly
└─ Format: A4 (210mm × 297mm)
```

## Scalability Considerations

### Current Setup (5000 users)

**Single Lightsail Instance**
- 1 GB RAM
- 1 vCPU
- SQLite database
- ✅ Sufficient for expected load

**Resource Usage**
- Python process: ~150-200 MB
- SQLite: ~10-50 MB (depending on data)
- nginx: ~20-50 MB
- Available: ~600-700 MB for requests

**Concurrency**
- 4 uvicorn workers (configurable)
- Each worker: ~100 concurrent requests
- Total: ~400 concurrent users possible

### If Scaling Beyond 5000 Users

**Database**
```
Current: SQLite (file-based)
├─ Limit: ~10 concurrent writes
├─ Problem: Locking under heavy write load
└─ Solution: Migrate to PostgreSQL (RDS)

PostgreSQL (AWS RDS)
├─ Managed, multi-AZ
├─ Unlimited concurrent connections
├─ Automated backups
└─ Better query optimization
```

**Caching**
```
Current: No caching
├─ Database hit per request
└─ Problem: Slow with many reads

Add Redis
├─ Cache user sessions
├─ Cache registration data (TTL: 1 hour)
├─ Cache admit card PDFs (30 minutes)
└─ Result: 10x faster response times
```

**Static Files**
```
Current: Served from Lightsail
├─ OK for small scale
└─ Problem: Single point of failure

Add CloudFront CDN
├─ Cache frontend assets globally
├─ Faster downloads for users
├─ Offload bandwidth from instance
└─ Better performance globally
```

**Application Servers**
```
Current: 1 instance
├─ Processing: 4 workers
└─ Problem: Single point of failure

Add Load Balancer
├─ Multiple Lightsail instances
├─ AWS Load Balancer distributing traffic
├─ Automatic failover
├─ Better uptime SLA
└─ Cost: ~$20+ more per month
```

## Deployment Topology

### Development
```
Machine
├─ Backend: Python venv, http://localhost:8000
│  └─ Database: SQLite (in-memory or file)
├─ Frontend: Vite dev server, http://localhost:5173
│  └─ Hot reload enabled
└─ Email: Gmail SMTP (test account)
```

### Production (Single Lightsail)
```
AWS Lightsail Instance
├─ nginx (reverse proxy, port 80/443)
│  ├─ Serves Vue frontend (static files)
│  └─ Routes /auth/* and /registration/* to backend
├─ FastAPI (gunicorn/uvicorn, port 8000)
│  ├─ 4 worker processes
│  ├─ Auto-restart on failure
│  └─ Systemd service
└─ SQLite database (/home/ubuntu/pw-reg/backend/data/app.db)
```

## Security Layers

```
1. Network
   ├─ UFW Firewall (allow SSH, HTTP, HTTPS)
   ├─ Static IP for database if needed
   └─ SSL/TLS certificate (Let's Encrypt)

2. Application
   ├─ Input validation (Pydantic schemas)
   ├─ SQL injection prevention (SQLAlchemy ORM)
   ├─ CORS headers (allow only frontend origin)
   ├─ JWT token validation
   └─ OTP rate limiting

3. Data
   ├─ Email hashing would be needed for user lookup
   ├─ OTP stored salted/hashed (TODO)
   ├─ Passwords: None (OTP-based auth)
   └─ Database: Local file on instance

4. Secrets Management
   ├─ Environment variables (.env file)
   ├─ Not in source code
   ├─ Read by systemd service
   └─ Protected file permissions
```

## Monitoring & Logging

```
Logs
├─ Application: Stdout (captured by journalctl)
├─ nginx: /var/log/nginx/access.log, error.log
├─ systemd: journalctl -u pwnsat-api
└─ View: tail -f, journalctl -f

Health Checks
├─ GET /health (application level)
├─ GET / (basic connectivity)
├─ Database: Auto-check on startup
└─ Email: Silent fail (logged)

Alerts (When to Investigate)
├─ Service not running
├─ Error rate > 5%
├─ Response time > 5 seconds
├─ Database locked errors
└─ Email failures
```

## Future Architecture

If requirements change:

```
Microservices (NOT recommended for <50K users)
├─ Auth service (OTP, JWT)
├─ Registration service (CRUD)
├─ PDF generation service (scales independently)
└─ Email service (async queue)

Event-Driven (NOT recommended for initial scale)
├─ User verified → Event → Generate welcome email
├─ Registration updated → Event → Audit log
└─ PDF generated → Event → Track access

Real-time (NOT recommended for initial scale)
├─ WebSocket for live updates
├─ Push notifications for OTP
└─ Live admin dashboard
```

---

**Key Principle**: Keep it simple until you need complexity!
