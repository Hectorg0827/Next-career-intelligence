# Testing Guide: Phase 1 Week 3-4

## 🚀 Quick Start

### **Backend Server** (Running on port 8000)
```bash
# Terminal 1: Start backend
cd /Users/hectorgarcia/Desktop/Next-career-intelligence
PYTHONPATH=/Users/hectorgarcia/Desktop/Next-career-intelligence/backend python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Frontend Server** (Running on port 3000)
```bash
# Terminal 2: Start frontend
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
npm run dev
```

### **API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 Testing the Authentication Flow

### **1. Test Signup API**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Signup successful. Please check your email to verify your account.",
  "user_id": "abc123def456",
  "email": "john@example.com"
}
```

### **2. Test Email Verification API**
```bash
curl -X POST http://localhost:8000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "verification_code": "123456"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Email verified successfully. Redirecting to onboarding...",
  "user_id": "abc123def456"
}
```

### **3. Test Login API**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "remember_me": true
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Login successful",
  "user_id": "abc123def456",
  "email": "john@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### **4. Test Password Reset Request API**
```bash
curl -X POST http://localhost:8000/api/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "If this email is registered, you'll receive password reset instructions",
  "email": "john@example.com"
}
```

---

## 🎯 Testing the Onboarding Flow

### **1. Test Onboarding Step 1 (Role/Industry)**
```bash
curl -X POST http://localhost:8000/api/onboarding/step/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "current_role": "Software Engineer",
    "industry": "tech",
    "years_experience": "2-5"
  }'
```

### **2. Test Onboarding Step 2 (Skills)**
```bash
curl -X POST http://localhost:8000/api/onboarding/step/2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "skills": ["Python", "JavaScript", "Problem Solving", "Leadership"]
  }'
```

### **3. Test Onboarding Step 3 (Goals)**
```bash
curl -X POST http://localhost:8000/api/onboarding/step/3 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "goals": ["Get promoted", "Learn new skills"]
  }'
```

### **4. Test Onboarding Step 4 (Learning Preferences)**
```bash
curl -X POST http://localhost:8000/api/onboarding/step/4 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "learning_style": "courses",
    "notification_preferences": {"email": true, "sms": false}
  }'
```

### **5. Test Complete Onboarding**
```bash
curl -X POST http://localhost:8000/api/onboarding/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "current_role": "Software Engineer",
    "industry": "tech",
    "years_experience": "2-5",
    "skills": ["Python", "JavaScript", "Problem Solving"],
    "goals": ["Get promoted", "Learn new skills"],
    "learning_style": "courses"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Welcome to NEXT! Your personalized learning path is ready.",
  "user_id": "abc123def456",
  "learning_path_id": "lp_xyz789",
  "dashboard_url": "/dashboard"
}
```

---

## 🖥️ Frontend Testing

### **Test 1: Signup Flow**
1. Go to http://localhost:3000
2. Click "Create Account"
3. Fill in form:
   - Full Name: "Test User"
   - Email: "test@example.com"
   - Password: "TestPass123"
   - Confirm: "TestPass123"
   - Check terms
4. Click "Create Account"
5. Should see email verification screen
6. Enter verification code (from backend logs)
7. Should redirect to onboarding

### **Test 2: Onboarding Flow**
1. Complete signup and verification
2. Onboarding screen should show with progress bar
3. Step 1: Select role, industry, experience
4. Step 2: Select skills (choose 3+)
5. Step 3: Select goals (choose 1+)
6. Step 4: Select learning style
7. Click "Complete Setup"
8. Should redirect to /dashboard

### **Test 3: Login Flow**
1. Go to http://localhost:3000
2. Click "Sign In"
3. Enter email and password
4. Check "Remember me" (optional)
5. Click "Sign In"
6. Should redirect to /dashboard

### **Test 4: Password Reset**
1. Go to login screen
2. Click "Forgot password?"
3. Enter email
4. Should show reset email sent message
5. Check email or logs for reset link

---

## 🔍 Validation Testing

### **Invalid Email**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -d '{"full_name":"Test","email":"invalid","password":"Pass123","confirm_password":"Pass123"}'
```
**Expected**: 422 Unprocessable Entity (invalid email format)

### **Short Password**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -d '{"full_name":"Test","email":"test@example.com","password":"Short1","confirm_password":"Short1"}'
```
**Expected**: 400 Bad Request (password too short)

### **Passwords Don't Match**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -d '{"full_name":"Test","email":"test@example.com","password":"Pass123","confirm_password":"Pass456"}'
```
**Expected**: 422 Unprocessable Entity (passwords don't match)

### **Missing Required Fields**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -d '{"email":"test@example.com","password":"Pass123"}'
```
**Expected**: 422 Unprocessable Entity (missing full_name)

---

## 📊 Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Successful signup/login |
| 201 | Created | User created |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | Email not verified |
| 404 | Not Found | User not found |
| 409 | Conflict | Email already registered |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |

---

## 🐛 Debugging

### **Check Backend Logs**
```bash
# View last 20 lines of logs
tail -n 20 /path/to/backend/logs.txt

# Search for errors
grep "ERROR\|❌" /path/to/backend/logs.txt
```

### **Check Frontend Logs**
```bash
# Browser Console (F12)
- Network tab: Check API requests
- Console tab: Check errors
- Application tab: Check localStorage tokens
```

### **Test Database Connection**
```bash
# In Python REPL
from app.db.supabase import get_supabase_client
client = get_supabase_client()
response = client.table('users').select('*').execute()
print(response.data)
```

### **Test Email Service**
```bash
# In Python REPL
from app.services.email_service import send_email
await send_email('test@example.com', 'subject', 'body')
```

---

## ✅ Success Checklist

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Swagger docs load at http://localhost:8000/docs
- [ ] Signup API returns success response
- [ ] Verification API marks email as verified
- [ ] Login API returns access token
- [ ] Onboarding API stores all data
- [ ] AuthFlow component renders on frontend
- [ ] OnboardingSequence component renders on frontend
- [ ] Signup → Verification → Onboarding → Dashboard flow works
- [ ] Form validation prevents invalid submissions
- [ ] Error messages display correctly
- [ ] Token is stored in localStorage
- [ ] Authenticated requests include Authorization header
- [ ] Protected routes require authentication

---

## 🚨 Troubleshooting

### **Backend won't start**
- Check Python version: `python3 --version` (need 3.8+)
- Check dependencies: `pip list | grep fastapi`
- Check port 8000: `lsof -i :8000`
- Check PYTHONPATH: `echo $PYTHONPATH`

### **API returns 404**
- Check router is registered in main.py
- Check endpoint URL spelling
- Check HTTP method (GET vs POST)
- Check request body format (JSON)

### **Authentication fails**
- Check credentials in database
- Check email is verified in database
- Check access token isn't expired
- Check Authorization header format: `Bearer {token}`

### **Frontend can't reach backend**
- Check backend is running on 8000
- Check CORS is enabled in backend
- Check firewall allows localhost:8000
- Check frontend uses correct API URL: `http://localhost:8000`

---

## 📚 Reference

**Routes Registered**:
- ✅ /api/auth/* (6 endpoints)
- ✅ /api/onboarding/* (6 endpoints)
- ✅ /api/health (existing)
- ✅ /api/analyze (existing)
- ✅ /api/roadmap (existing)
- ✅ /api/jobs/* (existing)
- ✅ /api/users/* (existing)

**Frontend Pages**:
- http://localhost:3000 - Landing page
- http://localhost:3000/auth - AuthFlow (when integrated)
- http://localhost:3000/onboarding - OnboardingSequence (when integrated)
- http://localhost:3000/dashboard - Dashboard (when created)

**Database Tables Needed**:
- users (user_id, email, password_hash, email_verified, created_at)
- onboarding (user_id, role, industry, skills, goals, learning_style)
- verification_codes (email, code, expires_at)
- password_resets (email, reset_code, expires_at)

---

**Last Updated**: October 20, 2025  
**Status**: Ready for Integration Testing  
**Next**: Database integration and email service setup
