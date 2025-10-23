# Phase 2 Authentication Testing Guide

**Date:** October 22, 2025
**Status:** Ready for Testing ✅

---

## 🎯 Testing Overview

This guide will walk you through testing all Phase 2 authentication features systematically.

**Prerequisites:**
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ SendGrid email service configured (check backend .env)

---

## Test Suite 1: Email Verification Flow 📧

### Test 1.1: New User Signup with Email Verification

**Steps:**
1. Navigate to http://localhost:3000/auth/signup
2. Fill in the form:
   - Full Name: "Test User"
   - Email: Use a real email you can access
   - Password: "test123456"
3. Click "Create Account"

**Expected Results:**
- ✅ User created successfully
- ✅ Redirected to `/auth/verify-email?email=your@email.com`
- ✅ Page shows "Verify Your Email" with mail icon
- ✅ 6-digit code input field displayed
- ✅ Countdown timer shows "60" seconds
- ✅ "Resend Code" button is disabled
- ✅ Check your email for 6-digit verification code

**Potential Issues:**
- If email doesn't arrive: Check SendGrid configuration in backend/.env
- If redirected to dashboard: Check signup/page.tsx redirect logic (should go to verify-email)

---

### Test 1.2: Enter Verification Code

**Steps:**
1. Check your email for the 6-digit code
2. Enter the code in the verification page
3. Click "Verify Email"

**Expected Results:**
- ✅ Loading spinner appears on button
- ✅ Success! Redirected to `/onboarding`
- ✅ User is now logged in (Firebase Auth)

**Test with Wrong Code:**
1. Enter incorrect code: "000000"
2. Click "Verify Email"

**Expected Results:**
- ✅ Error message displayed: "Invalid or expired verification code"
- ✅ Input remains, can try again
- ✅ No redirect

---

### Test 1.3: Resend Verification Code

**Steps:**
1. Go back to signup and create another test account
2. On verification page, wait for countdown timer to reach 0 (or wait 60 seconds)
3. Click "Resend Code" button

**Expected Results:**
- ✅ Loading spinner on "Resend Code" button
- ✅ Countdown resets to 60 seconds
- ✅ Button becomes disabled again
- ✅ New email sent with new 6-digit code
- ✅ New code works, old code expires

**Test Rate Limiting:**
1. Try clicking "Resend Code" before 60 seconds

**Expected Results:**
- ✅ Button is disabled (grayed out)
- ✅ Cannot click until countdown reaches 0

---

## Test Suite 2: Login Flow 🔐

### Test 2.1: Login with Verified Account

**Steps:**
1. Navigate to http://localhost:3000/auth/login
2. Enter email and password from Test 1.1
3. Click "Sign In"

**Expected Results:**
- ✅ Loading spinner appears
- ✅ Successfully logged in
- ✅ Redirected to `/dashboard`
- ✅ User info displayed (name, email)

**Test Wrong Password:**
1. Enter correct email but wrong password
2. Click "Sign In"

**Expected Results:**
- ✅ Error message: "Invalid credentials. Please check your email and password."
- ✅ Stays on login page

---

### Test 2.2: Google Sign-In

**Steps:**
1. On login page, click "Continue with Google"
2. Select Google account

**Expected Results:**
- ✅ Google popup opens
- ✅ Account selected
- ✅ Redirected to `/dashboard`
- ✅ Logged in successfully

---

## Test Suite 3: Settings Page ⚙️

### Test 3.1: Update Personal Information

**Steps:**
1. Navigate to http://localhost:3000/settings
2. Change "Full Name" to "Updated Name"
3. Click "Save Changes"

**Expected Results:**
- ✅ Loading spinner on button
- ✅ Success message: "Profile updated successfully!"
- ✅ Green banner appears at top
- ✅ Name persists on refresh
- ✅ Name updated in Firebase Auth

**Test Email Update:**
1. Change email to different address
2. Click "Save Changes"

**Expected Results:**
- ✅ Success message OR re-authentication notice
- ✅ Note: Changing email requires recent login in production

---

### Test 3.2: Change Password

**Steps:**
1. Scroll to "Password & Security" section
2. Enter current password (wrong one first)
3. Enter new password: "newpassword123"
4. Confirm new password: "newpassword123"
5. Click "Change Password"

**Expected Results with Wrong Current Password:**
- ✅ Error message displayed
- ✅ Password not changed

**Steps (Correct Password):**
1. Enter correct current password
2. Enter new password: "newpassword123"
3. Confirm new password: "newpassword123"
4. Click "Change Password"

**Expected Results:**
- ✅ Loading spinner
- ✅ Success message: "Password changed successfully!"
- ✅ Fields cleared
- ✅ Logout and login with new password works

**Test Mismatched Passwords:**
1. New password: "test123"
2. Confirm password: "test456"
3. Click "Change Password"

**Expected Results:**
- ✅ Error: "New passwords do not match."

---

### Test 3.3: Notification Preferences

**Steps:**
1. Scroll to "Notification Preferences"
2. Toggle each preference on/off:
   - Email Notifications
   - Job Alerts
   - Newsletter Subscription
   - Weekly Digest
3. Click "Save Preferences"

**Expected Results:**
- ✅ Loading spinner
- ✅ Success message: "Preferences updated successfully!"
- ✅ Toggles stay in selected state
- ✅ Settings persist on page refresh

**Note:** Currently frontend-only. Backend integration coming soon.

---

### Test 3.4: Delete Account

**Steps:**
1. Scroll to "Account Management"
2. Click "Delete Account" button
3. Confirmation modal appears
4. Type "DELETE" in the input field
5. Click "Delete Account" button

**Expected Results:**
- ✅ Red confirmation modal appears
- ✅ Warning message displayed
- ✅ Delete button disabled until "DELETE" typed
- ✅ After clicking: Account deleted
- ✅ Redirected to home page
- ✅ Logged out automatically
- ✅ Cannot login with old credentials

**Test Cancel:**
1. Click "Delete Account"
2. Type "DELETE"
3. Click "Cancel"

**Expected Results:**
- ✅ Modal closes
- ✅ Account NOT deleted
- ✅ Input field cleared

---

## Test Suite 4: Password Reset Flow 🔑

### Test 4.1: Request Password Reset

**Steps:**
1. Logout (if logged in)
2. Navigate to http://localhost:3000/auth/login
3. Click "Forgot password?" link
4. Enter email address
5. Click "Send Reset Code"

**Expected Results:**
- ✅ Loading spinner
- ✅ Success screen: "Check Your Email"
- ✅ Shows email address
- ✅ "Enter Reset Code" button visible
- ✅ Email received with 6-digit code

**Test with Non-existent Email:**
1. Enter email that doesn't exist
2. Click "Send Reset Code"

**Expected Results:**
- ✅ Error message: "User not found" or similar
- ✅ Stays on page

---

### Test 4.2: Reset Password with Code

**Steps:**
1. Click "Enter Reset Code" button (or navigate directly)
2. Page shows `/auth/reset-password?email=your@email.com`
3. Enter 6-digit code from email
4. Enter new password: "resetpassword123"
5. Confirm password: "resetpassword123"
6. Click "Reset Password"

**Expected Results:**
- ✅ Loading spinner
- ✅ Success screen: "Password Reset!"
- ✅ Auto-redirects to login after 2 seconds
- ✅ Can login with new password

**Test with Wrong Code:**
1. Enter incorrect code: "000000"
2. Enter new password
3. Click "Reset Password"

**Expected Results:**
- ✅ Error message: "Invalid or expired reset code"
- ✅ Stays on page

**Test Mismatched Passwords:**
1. Enter correct code
2. New password: "password1"
3. Confirm password: "password2"
4. Click "Reset Password"

**Expected Results:**
- ✅ Error: "Passwords do not match."
- ✅ No API call made

---

### Test 4.3: Login with Reset Password

**Steps:**
1. After password reset, wait for redirect to login
2. Enter email and NEW password
3. Click "Sign In"

**Expected Results:**
- ✅ Successfully logged in
- ✅ Redirected to dashboard
- ✅ Old password no longer works

---

## Test Suite 5: Edge Cases & Error Handling 🐛

### Test 5.1: Authentication Protection

**Steps:**
1. Logout completely
2. Try to navigate to http://localhost:3000/dashboard
3. Try to navigate to http://localhost:3000/settings

**Expected Results:**
- ✅ Redirected to `/auth/login`
- ✅ Protected routes require authentication

---

### Test 5.2: Already Verified Email

**Steps:**
1. Signup with NEW email
2. Verify email successfully
3. Try to navigate back to `/auth/verify-email?email=your@email.com`
4. Try to verify again

**Expected Results:**
- ✅ Error message: "Email already verified" or similar
- ✅ Redirected to dashboard

---

### Test 5.3: Expired Verification Code

**Steps:**
1. Signup with new email
2. Receive verification code
3. Wait 16 minutes (code expires after 15 minutes)
4. Try to verify with old code

**Expected Results:**
- ✅ Error: "Invalid or expired verification code"
- ✅ Must request new code

---

### Test 5.4: Rate Limiting

**Steps:**
1. On verification page, click "Resend Code"
2. Immediately try to click again (within 60 seconds)

**Expected Results:**
- ✅ Button disabled
- ✅ Countdown shows remaining time
- ✅ Cannot spam resend

---

## Test Suite 6: UI/UX Testing 🎨

### Test 6.1: Responsive Design

**Steps:**
1. Test each page on different screen sizes:
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)

**Pages to Test:**
- /auth/signup
- /auth/login
- /auth/verify-email
- /auth/forgot-password
- /auth/reset-password
- /settings

**Expected Results:**
- ✅ All pages responsive
- ✅ No horizontal scrolling
- ✅ Buttons accessible
- ✅ Forms readable on mobile

---

### Test 6.2: Loading States

**Check all loading states work:**
- ✅ Signup button: "Creating Account..."
- ✅ Login button: "Signing In..."
- ✅ Verify button: "Verifying..."
- ✅ Resend button: Loading spinner
- ✅ Save Changes: "Saving..."
- ✅ Change Password: "Changing..."
- ✅ Delete Account: "Deleting..."
- ✅ Send Reset Code: "Sending Code..."
- ✅ Reset Password: "Resetting Password..."

---

### Test 6.3: Error Messages

**Check all error messages display correctly:**
- ✅ Red banner with error icon
- ✅ Clear, user-friendly text
- ✅ Dismissible or auto-clears
- ✅ Doesn't break layout

---

### Test 6.4: Success Messages

**Check all success messages display correctly:**
- ✅ Green banner with checkmark icon
- ✅ Auto-disappears after 3 seconds
- ✅ Clear, positive feedback
- ✅ Doesn't break layout

---

## Test Suite 7: Backend Integration 🔌

### Test 7.1: API Endpoints

**Check all endpoints working:**

```bash
# Test signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Test verify email
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","verification_code":"123456"}'

# Test resend code
curl -X POST http://localhost:8000/auth/resend-verification-code \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Test request password reset
curl -X POST http://localhost:8000/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Test reset password
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","reset_code":"123456","new_password":"newpass123"}'
```

**Expected Results:**
- ✅ All endpoints return 200 OK or appropriate error codes
- ✅ Proper JSON responses
- ✅ Error messages in detail field

---

## 🐛 Bug Tracking

### Known Issues:
- [ ] Database connection shows "error" but functional
- [ ] Re-authentication notice for email change (expected behavior)
- [ ] Download data button (placeholder - not implemented)

### Issues Found During Testing:
_(Add any issues you find here)_

- [ ] Issue 1: ...
- [ ] Issue 2: ...
- [ ] Issue 3: ...

---

## ✅ Test Results Summary

### Test Suite 1: Email Verification Flow
- [ ] 1.1 New User Signup with Email Verification
- [ ] 1.2 Enter Verification Code
- [ ] 1.3 Resend Verification Code

### Test Suite 2: Login Flow
- [ ] 2.1 Login with Verified Account
- [ ] 2.2 Google Sign-In

### Test Suite 3: Settings Page
- [ ] 3.1 Update Personal Information
- [ ] 3.2 Change Password
- [ ] 3.3 Notification Preferences
- [ ] 3.4 Delete Account

### Test Suite 4: Password Reset Flow
- [ ] 4.1 Request Password Reset
- [ ] 4.2 Reset Password with Code
- [ ] 4.3 Login with Reset Password

### Test Suite 5: Edge Cases & Error Handling
- [ ] 5.1 Authentication Protection
- [ ] 5.2 Already Verified Email
- [ ] 5.3 Expired Verification Code
- [ ] 5.4 Rate Limiting

### Test Suite 6: UI/UX Testing
- [ ] 6.1 Responsive Design
- [ ] 6.2 Loading States
- [ ] 6.3 Error Messages
- [ ] 6.4 Success Messages

### Test Suite 7: Backend Integration
- [ ] 7.1 API Endpoints

---

## 🎓 Testing Tips

1. **Use Real Email:** Use a real email address you can access to receive codes
2. **Clear Browser Cache:** If issues occur, try clearing cache and cookies
3. **Check Console:** Open browser DevTools (F12) to see any JavaScript errors
4. **Check Network Tab:** Monitor API calls and responses
5. **Test Multiple Browsers:** Try Chrome, Firefox, Safari
6. **Take Screenshots:** Document any bugs with screenshots
7. **Note Timing:** Track how long each operation takes

---

## 📊 Testing Metrics

**Target Metrics:**
- ✅ 0 TypeScript errors
- ✅ All pages load in < 2 seconds
- ✅ All API calls return in < 1 second
- ✅ 100% of features work as expected
- ✅ No console errors
- ✅ Mobile responsive on all pages

---

## 🚀 After Testing

Once all tests pass:

1. **Mark Todo as Complete**
   - ✅ Test Phase 2 Authentication Flow

2. **Move to Next Phase**
   - Option A: Add Security Features (sessions, login history)
   - Option B: Complete Stripe Integration (payment testing)
   - Option C: Start Phase 3 (AI Coach, Job Marketplace)

3. **Deploy to Staging** (optional)
   - Test in production-like environment
   - Verify SendGrid emails work in production

---

**Happy Testing!** 🎉

If you find any issues, document them and we'll fix them together!
