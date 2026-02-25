# Frontend Integration Checklist

Complete checklist for frontend verification.

## Environment Setup

- [ ] Node.js 16+ installed
- [ ] npm installed
- [ ] `frontend/package.json` exists
- [ ] Dependencies listed:
  - [ ] Vue 3
  - [ ] Axios
  - [ ] Vue Router

## Vite Configuration

- [ ] `vite.config.js` created
- [ ] Port: 5173 (default)
- [ ] Vue plugin configured

## Frontend Structure

### Pages (All created)
- [ ] `src/pages/Login.vue` - Email entry screen
- [ ] `src/pages/VerifyOTP.vue` - OTP verification
- [ ] `src/pages/RegistrationForm.vue` - Registration details
- [ ] `src/pages/Dashboard.vue` - User dashboard with download

### Core Files
- [ ] `src/main.js` - Entry point
- [ ] `src/App.vue` - Root component
- [ ] `src/index.html` - HTML template
- [ ] `src/router/index.js` - Routing setup
- [ ] `src/store/auth.js` - Auth state management
- [ ] `src/api/client.js` - Axios API client

## API Integration

- [ ] Axios client configured
- [ ] Base URL from env: `VITE_API_URL`
- [ ] Auth header handling
- [ ] Token interceptor setup
- [ ] API methods exported:
  - [ ] `authAPI.sendOTP()`
  - [ ] `authAPI.verifyOTP()`
  - [ ] `registrationAPI.createOrUpdate()`
  - [ ] `registrationAPI.getRegistration()`
  - [ ] `registrationAPI.downloadAdmitCard()`

## Authentication Flow

- [ ] Login page sends OTP
- [ ] OTP page validates token
- [ ] Token stored in localStorage
- [ ] Route guards protect pages
- [ ] Logout removes token

## Form Management

- [ ] Form validation working
- [ ] Field types correct:
  - [ ] Text inputs (name, etc.)
  - [ ] Date picker (exam_date)
- [ ] Edit functionality works
- [ ] Form persists (fetch on mount)

## PDF Download

- [ ] Download button functional
- [ ] File downloads as PDF
- [ ] Filename: `admit_card_NSAT2026-XXXX.pdf`

## Styling

- [ ] Pages are responsive
- [ ] Gradient background applied
- [ ] Form styling consistent
- [ ] Buttons have hover states
- [ ] Mobile-friendly layout

## Error Handling

- [ ] Error messages displayed
- [ ] 401 errors redirect to login
- [ ] Network errors handled gracefully

## Testing

- [ ] `npm install` works
- [ ] `npm run dev` starts server
- [ ] `npm run build` creates dist/
- [ ] dist/ folder ready for deployment

## Status Indicators

### Login Page
- Email input validation
- OTP sending feedback
- Error messages shown

### OTP Page
- 6-digit only input
- Rate limit message (if needed)
- Back to login option
- Email pre-filled

### Registration Page
- All 6 fields present
- Date picker functional
- Create vs. Update logic
- Success message

### Dashboard
- User email displayed
- Registration details shown
- Edit button works
- Download button works

## Performance

- [ ] Page loads < 3 seconds
- [ ] No console errors
- [ ] PDF generation < 2 seconds
- [ ] API responses < 500ms

---

**Verification Status**: Ready for deployment ✅
