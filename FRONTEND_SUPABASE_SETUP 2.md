# Frontend Supabase Setup Guide

## Overview

This guide covers setting up Supabase in your Next.js frontend for authentication and data access.

**Status**: ✅ Code ready, needs environment variables configured

---

## Quick Setup (5 minutes)

### 1. Add Supabase Environment Variables

Edit or create `frontend/.env.local`:

```bash
# Supabase Configuration (Get from Supabase Settings → API)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase Configuration (Optional - for future OAuth)
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-app.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

### 2. Get Your Supabase Credentials

In Supabase Dashboard:
1. Click **Settings** (bottom left)
2. Click **API**
3. Copy these values:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

⚠️ **Important**: Use the `anon public` key in frontend, NOT the service role key

### 3. Start Frontend

```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
npm run dev
```

Access: http://localhost:3000

---

## Frontend Supabase Integration

### Current Implementation

**File**: `frontend/src/lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://...'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Auth helpers
export const auth = {
  signUp: async (email: string, password: string) => { ... },
  signIn: async (email: string, password: string) => { ... },
  signOut: async () => { ... },
  getUser: async () => { ... },
  getSession: async () => { ... }
}

// Data helpers
export const data = {
  getUsers: async () => { ... },
  getOnboarding: async (userId: string) => { ... },
  saveOnboarding: async (userId: string, data: any) => { ... }
}
```

### Available Functions

#### Authentication

```typescript
import { auth } from '@/lib/supabase'

// Sign up
const { data, error } = await auth.signUp('user@example.com', 'password123')

// Sign in
const { data, error } = await auth.signIn('user@example.com', 'password123')

// Sign out
await auth.signOut()

// Get current user
const user = await auth.getUser()

// Get session
const session = await auth.getSession()
```

#### Data Operations

```typescript
import { data } from '@/lib/supabase'

// Get all users
const users = await data.getUsers()

// Get user's onboarding data
const onboarding = await data.getOnboarding(userId)

// Save onboarding data
await data.saveOnboarding(userId, {
  current_role: 'Software Engineer',
  industry: 'tech',
  years_experience: '5-10'
})
```

---

## Frontend to Backend Flow

### Authentication Flow

```
Frontend (Next.js)              Backend (FastAPI)              Database (Supabase)
    ↓                                ↓                              ↓
1. User clicks "Sign Up"
    │
2. Call: POST /api/auth/signup
    │─────────────────────→ receives email, password
    │                       │
    │                       → hash password
    │                       → create user in DB
    │                       → generate verification code
    │                       → send email via SendGrid
    │                       │
    │                       → user created in Supabase
    │                       →
    │←─────────────────── returns { user_id, message }
    │
3. Display: "Check your email"
    │
4. User receives email with 6-digit code
    │
5. User enters code
    │
6. Call: POST /api/auth/verify-email
    │─────────────────────→ receives email, code
    │                       │
    │                       → check code in DB
    │                       → mark email verified
    │                       → send welcome email
    │                       │
    │                       → marked in Supabase
    │←─────────────────── returns { success: true }
    │
7. Redirect to onboarding
```

### Onboarding Flow

```
Frontend                        Backend                         Database
    ↓                               ↓                               ↓
1. User completes step 1
    │
2. Call: POST /api/onboarding/step/1
    │─────────────────────→ receives user_id, step_data
    │                       │
    │                       → save step_1_data in DB
    │                       │
    │                       → saved in Supabase
    │←─────────────────── returns { success: true }
    │
3. User continues to step 2-4 (repeat above)
    │
4. User clicks "Complete Onboarding"
    │
5. Call: POST /api/onboarding/complete
    │─────────────────────→ receives all onboarding data
    │                       │
    │                       → save all data in DB
    │                       → generate learning path
    │                       │
    │                       → all saved in Supabase
    │←─────────────────── returns { learning_path_id }
    │
6. Redirect to dashboard with learning_path_id
```

---

## Environment Variables Explained

### Public Variables (Safe in Frontend)

```bash
# Supabase - These are PUBLIC, can be exposed
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Why "NEXT_PUBLIC_"?**
- Variables prefixed with `NEXT_PUBLIC_` are embedded in client-side JavaScript
- Use only for non-sensitive data (public API keys, URLs)
- The anon key is restricted to specific database operations via RLS policies

### Private Variables (Backend Only)

```bash
# Backend .env (NOT shared with frontend)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SENDGRID_API_KEY=SG.your-api-key-here
DATABASE_URL=postgresql://...
```

**Why separate?**
- Service key has full admin access
- Private keys must never be exposed to frontend
- Backend .env is never sent to browser

---

## Testing Frontend Setup

### Test 1: Verify Supabase Connection

In browser console:

```javascript
// Check if Supabase is initialized
console.log(window.supabase)
```

Expected output: Supabase client object

### Test 2: Test Sign Up

```javascript
import { auth } from '@/lib/supabase'

const result = await auth.signUp('test@example.com', 'TestPass123')
console.log(result)
```

Expected: User created, verification email sent

### Test 3: Test Data Access

```javascript
import { data } from '@/lib/supabase'

const users = await data.getUsers()
console.log(users)
```

Expected: Array of user records from Supabase

---

## Common Issues & Fixes

### Issue 1: "NEXT_PUBLIC_SUPABASE_ANON_KEY is not set"

**Cause**: Environment variable missing or not loaded

**Fix**:
1. Check `frontend/.env.local` exists
2. Verify variable name matches exactly (case-sensitive)
3. Restart dev server: `npm run dev`

### Issue 2: "Failed to fetch from Supabase"

**Cause**: Wrong URL or network issue

**Fix**:
1. Verify URL format: `https://xxxxx.supabase.co` (not http://)
2. Check internet connection
3. Verify Supabase project is active

### Issue 3: "Error: Invalid API Key"

**Cause**: Using wrong key type

**Fix**:
- ✅ Use: `anon public` key in frontend
- ❌ Don't use: `service_role` key in frontend
- ❌ Don't use: Backend API key in frontend

### Issue 4: "RLS policy violation"

**Cause**: Row Level Security policy blocking access

**Fix**:
- Frontend uses anon key, so RLS policies must allow public access
- Backend uses service role key, so policies allow service role
- Check policies in Supabase Dashboard → SQL Editor

---

## Next Steps

### Phase 1 (This Week)
- ✅ Setup Supabase client in frontend
- ✅ Configure environment variables
- ✅ Test authentication flow
- ✅ Test onboarding flow

### Phase 2 (Week 5-6)
- [ ] Add JWT token verification in middleware
- [ ] Secure routes with authentication checks
- [ ] Implement session management
- [ ] Add OAuth (Google, LinkedIn)

### Phase 3 (Week 7-8)
- [ ] Create dashboard page
- [ ] Add real-time updates (Supabase subscriptions)
- [ ] Implement learning path generation
- [ ] Add analytics tracking

---

## File Reference

**Frontend Supabase Files**:
- `frontend/src/lib/supabase.ts` - Supabase client and helpers
- `frontend/.env.local` - Environment variables (not in git)
- `frontend/.env.example` - Template for environment variables

**Backend Supabase Files**:
- `backend/app/services/supabase_client.py` - Database operations
- `backend/.env` - Backend configuration (not in git)

**Documentation**:
- `SUPABASE_SENDGRID_SETUP.md` - Backend setup guide
- `FRONTEND_SUPABASE_SETUP.md` - This file

---

## Quick Reference Commands

```bash
# Start frontend dev server
cd frontend && npm run dev

# View environment variables (frontend only, don't show values)
echo "NEXT_PUBLIC_SUPABASE_URL: $(echo $NEXT_PUBLIC_SUPABASE_URL | head -c 20)..."

# Test Supabase connection
curl -H "Authorization: Bearer $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
  https://your-project.supabase.co/rest/v1/users \
  -X GET

# View logs
tail -f /var/log/app.log
```

---

## Support & Documentation

- Supabase Docs: https://supabase.com/docs
- Next.js Docs: https://nextjs.org/docs
- Supabase Client Docs: https://supabase.com/docs/reference/javascript/introduction
- Our Backend API: http://localhost:8000/docs

---

**Status**: ✅ Ready for frontend development
**Next Action**: Add environment variables to `frontend/.env.local` and start dev server
