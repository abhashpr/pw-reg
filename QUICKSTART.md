# PWNSAT Registration System - Quick Start Guide

Get the system running in 10 minutes!

## ⚡ Local Development (5 minutes)

### Backend

```bash
# 1. Go to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy from example)
cd ..
cp .env.example .env

# 5. Edit .env with your Gmail App Password
# (Optional for testing - create a test account)

# 6. Run backend
cd backend
python main.py
```

✅ Backend running: **http://localhost:8000**
📚 API Docs: **http://localhost:8000/docs**

### Frontend

In a **new terminal**:

```bash
# 1. Go to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

✅ Frontend running: **http://localhost:5173**

## Email Setup (Gmail)

Essential for OTP functionality:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows, Mac, or Linux" (your OS)
5. Copy the **16-character password**
6. Paste in `.env`:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

## Test the Flow

1. **Open frontend**: http://localhost:5173
2. **Enter email**: Use a real email to receive OTP
3. **Check inbox**: Copy the 6-digit OTP
4. **Enter OTP**: Verify in the app
5. **Fill form**: Registration details
6. **Download PDF**: Admit card (dynamic generation)

## 💾 Database

- Auto-created: `backend/data/app.db`
- SQLite - no external DB needed
- Reset: Delete the file and restart backend

## 🐛 Debugging

### Backend won't start?
```bash
# Check Python version
python --version    # Need 3.9+

# Check dependencies
pip list | grep fastapi

# Debug mode - see all errors
cd backend
python -c "from main import app; print('OK')"
```

### Frontend not connecting to API?
- Check `VITE_API_URL` in `.env`
- Backend must be running on port 8000
- Check CORS headers in logs

### Email won't send?
- Verify Gmail credentials
- Allow "Less secure app access" (old accounts)
- 2FA must be enabled first
- Check SMTP credentials in API logs

## 📦 Production Deployment

See [README.md](README.md#deployment-to-aws-lightsail) for full AWS Lightsail setup.

Quick version:
```bash
# On your Lightsail instance:
git clone https://github.com/yourusername/pw-reg.git
cd pw-reg
sudo bash deploy.sh
```

## 🎯 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/send-otp` | POST | Send OTP to email |
| `/auth/verify-otp` | POST | Verify OTP, get JWT |
| `/auth/me` | GET | Get user info |
| `/registration/` | POST | Create/update form |
| `/registration/` | GET | Get saved form |
| `/registration/admit-card` | GET | Download PDF |

See API Docs at http://localhost:8000/docs (interactive)

## 📝 .env Template

```env
# Frontend
VITE_API_URL=http://localhost:8000

# Gmail (required for email)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Security (change in production!)
SECRET_KEY=super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OTP & App
OTP_EXPIRY_MINUTES=5
OTP_RATE_LIMIT_SECONDS=60
DEBUG=false
```

## 🗂️ Project Structure at a Glance

```
backend/           FastAPI app - handles auth, registration, PDF
├── main.py       Start here - routes everything
├── models.py     Database tables
├── auth.py       JWT token logic
└── routers/      Endpoint definitions

frontend/          Vue 3 app - user interface
├── pages/        Login → OTP → Form → Dashboard
├── api/          Axios HTTP client
└── store/        Auth token management
```

## 🚀 What's Included

✅ Email authentication with OTP
✅ JWT token-based session
✅ Editable registration form
✅ Dynamic PDF generation (no pre-generation)
✅ Roll number generation (never changes)
✅ SQLite database
✅ Vue 3 SPA frontend
✅ nginx config for production
✅ Systemd service file
✅ Ready for AWS Lightsail

## 📖 Full Documentation

- [README.md](README.md) - Complete guide
- [API Docs](http://localhost:8000/docs) - Interactive Swagger UI
- [Deployment Guide](README.md#deployment-to-aws-lightsail) - Lightsail setup

## 💡 Tips

- Keep `.env` secure - never commit to git
- Database auto-creates on first run
- PDF files generated on-demand (not stored)
- All endpoints require JWT auth except `/auth/`
- Change `SECRET_KEY` before production

---

**Need help?** Check the [README.md](README.md) or API docs at `/docs`
