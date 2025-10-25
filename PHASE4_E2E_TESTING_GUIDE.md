# 🧪 Phase 4 E2E Testing Guide

## Complete End-to-End Testing for Job Marketplace

---

## ✅ Pre-Testing Checklist

Before starting tests, verify:
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Database connected (Supabase)
- [ ] Firebase auth configured
- [ ] Gemini API key in backend .env
- [ ] Sample jobs seeded in database
- [ ] Chrome Developer Tools open (F12)
- [ ] No console errors before starting

**Command to verify backend:**
```bash
curl http://localhost:8000/api/v1/health
```

**Command to verify frontend:**
```bash
curl http://localhost:3000
```

---

## 🧪 Test Suite 1: Job Search & Browse (10 min)

### Test 1.1: View Job Listing Page
**Objective:** Verify job list loads with pagination

**Steps:**
1. Navigate to `http://localhost:3000/jobs/browse`
2. Wait for page to load (should show spinner first)
3. Verify job cards appear (title, company, location, salary, match score)
4. Check for "No jobs found" if database is empty

**Expected Result:**
- ✅ Jobs load within 2 seconds
- ✅ Cards display all job information
- ✅ Pagination controls visible
- ✅ No console errors

**Data to Check:**
- Job title visible
- Company name visible
- Salary range (min-max)
- Location displayed
- Match score with colored badge (0-30% red, 31-70% yellow, 71-100% green)

---

### Test 1.2: Search by Job Title
**Objective:** Verify search filter works

**Steps:**
1. On `/jobs/browse` page
2. Type "Python" in search box
3. Press Enter or wait for debounced search (1-2 seconds)
4. Verify filtered results

**Expected Result:**
- ✅ Search executes without page reload
- ✅ Only jobs with "Python" in title/description appear
- ✅ Result count updates
- ✅ No console errors

**Validation:**
- Filter by: "Python", "JavaScript", "DevOps"
- Verify each returns relevant jobs

---

### Test 1.3: Filter by Location
**Objective:** Verify location filter works

**Steps:**
1. On `/jobs/browse` page
2. Click location dropdown
3. Select "Remote"
4. Verify jobs filtered to remote only

**Expected Result:**
- ✅ Filter applies immediately
- ✅ Jobs show "Remote" in location field
- ✅ Can combine with other filters

**Validation:**
- Filter by: Remote, San Francisco, New York
- Verify location matches filter

---

### Test 1.4: Filter by Salary Range
**Objective:** Verify salary range filter

**Steps:**
1. On `/jobs/browse` page
2. Set min salary to $100,000
3. Set max salary to $200,000
4. Apply filter

**Expected Result:**
- ✅ Only jobs within range appear
- ✅ Salary bands match filter
- ✅ Real-time update

**Validation:**
- Test ranges: $50K-$100K, $100K-$150K, $150K+
- Verify all jobs fall within specified range

---

### Test 1.5: Filter by Experience Level
**Objective:** Verify experience level filter

**Steps:**
1. On `/jobs/browse` page
2. Select experience level filter
3. Choose "Senior"
4. Verify results

**Expected Result:**
- ✅ Only Senior level jobs appear
- ✅ Filter combines with other filters
- ✅ Result updates

**Validation:**
- Test: Entry, Mid, Senior
- Verify correct jobs returned

---

### Test 1.6: Multiple Filters Combined
**Objective:** Verify filters work together

**Steps:**
1. Search for "Python"
2. Filter location to "Remote"
3. Filter salary to $120K-$180K
4. Filter experience to "Senior"

**Expected Result:**
- ✅ All 4 filters apply simultaneously
- ✅ Results narrow correctly
- ✅ Can clear individual filters
- ✅ No console errors

---

## 🧪 Test Suite 2: Job Details & AI Match Analysis (10 min)

### Test 2.1: View Job Details
**Objective:** Verify job details page loads with full information

**Steps:**
1. On `/jobs/browse` page
2. Click any job card
3. Should navigate to `/jobs/[job_id]`
4. Verify all details load

**Expected Result:**
- ✅ Page loads within 2 seconds
- ✅ Full job information displayed
- ✅ AI match analysis visible
- ✅ Apply button present and enabled

**Data to Check:**
- Job title
- Company name and logo
- Full description
- Salary range
- Location and remote type
- Required skills list
- Experience level
- Match score with color badge

---

### Test 2.2: View AI Match Analysis
**Objective:** Verify match score calculation and analysis

**Steps:**
1. On job details page
2. Scroll to "Match Analysis" section
3. Verify match score (0-100%)
4. Check skill gaps
5. Check recommended prep

**Expected Result:**
- ✅ Match score calculated (0-100%)
- ✅ Skill gaps listed (if any)
- ✅ Interview prep recommendations shown
- ✅ Loading state visible while calculating

**Validation:**
- Match score between 0-100%
- Skill gaps are relevant missing skills
- Interview prep is personalized text

---

### Test 2.3: Save Job to Bookmarks
**Objective:** Verify save job functionality

**Steps:**
1. On job details page
2. Click "Save Job" button (heart icon)
3. Verify button changes state
4. Check confirmation message

**Expected Result:**
- ✅ Button changes to filled heart
- ✅ Success message shows
- ✅ Job added to saved list
- ✅ No console errors

**Data Validation:**
- Check database: job_id in saved_jobs table
- Verify user_id matches current user

---

### Test 2.4: Remove Saved Job
**Objective:** Verify unsave functionality

**Steps:**
1. On saved job details page
2. Click filled heart button to unsave
3. Verify state change

**Expected Result:**
- ✅ Button returns to outline
- ✅ Success message shown
- ✅ Job removed from saved list

---

## 🧪 Test Suite 3: Job Application Flow (15 min)

### Test 3.1: Apply to Job
**Objective:** Verify job application submission

**Steps:**
1. On job details page
2. Scroll to "Apply Now" section
3. Click "Apply" button
4. Verify modal/form appears
5. Submit application

**Expected Result:**
- ✅ Apply modal appears
- ✅ Form has message field
- ✅ Submit button enabled
- ✅ Success message shows
- ✅ Redirects to applications page or shows confirmation

**Data Validation:**
- Check database: new entry in job_applications table
- user_id matches current user
- job_id matches job
- status = "applied"
- match_score populated
- applied_at timestamp set

---

### Test 3.2: Prevent Duplicate Applications
**Objective:** Verify can't apply twice to same job

**Steps:**
1. Navigate back to same job
2. Try to apply again
3. Should get error message

**Expected Result:**
- ✅ Apply button disabled or hidden
- ✅ Error message: "Already applied to this job"
- ✅ No duplicate created in database

---

### Test 3.3: View All Applications
**Objective:** Verify applications list page

**Steps:**
1. Navigate to `/jobs/applications`
2. Should list all user applications
3. Verify columns: Job, Company, Status, Date, Match Score

**Expected Result:**
- ✅ Page loads within 2 seconds
- ✅ All applications shown
- ✅ Correct information displayed
- ✅ Pagination works if many applications

**Data Validation:**
- Application status matches database
- Match score displayed correctly
- Applied date shown

---

### Test 3.4: Update Application Status
**Objective:** Verify status updates (e.g., applied → interview)

**Steps:**
1. On applications page
2. Click on an application
3. Click "Update Status" button
4. Select new status (e.g., "Interview Scheduled")
5. Add details (interview date, notes)
6. Submit

**Expected Result:**
- ✅ Modal/form appears for editing
- ✅ Status changes in list
- ✅ Details saved (interview date, notes)
- ✅ Timestamp updates

**Status Flow to Test:**
- applied → interview_scheduled
- interview_scheduled → offer_received
- offer_received → accepted/rejected

---

### Test 3.5: View Application Details
**Objective:** Verify detailed view of single application

**Steps:**
1. On applications page
2. Click application row or "View Details" button
3. Verify expanded view shows all data

**Expected Result:**
- ✅ Full application details displayed
- ✅ Job information shown
- ✅ Application history visible
- ✅ Edit button accessible

---

### Test 3.6: Withdraw Application
**Objective:** Verify application withdrawal

**Steps:**
1. On application details page
2. Click "Withdraw" button
3. Confirm withdrawal
4. Verify removed from active list

**Expected Result:**
- ✅ Confirmation dialog appears
- ✅ Application status changes to "withdrawn"
- ✅ Removed from active applications list
- ✅ Moved to archive or deleted

---

## 🧪 Test Suite 4: Saved Jobs Management (8 min)

### Test 4.1: View Saved Jobs
**Objective:** Verify saved jobs list

**Steps:**
1. Navigate to `/jobs/saved`
2. Should show all bookmarked jobs
3. Verify cards match job listing

**Expected Result:**
- ✅ Page loads within 2 seconds
- ✅ Only saved jobs displayed
- ✅ Can search/filter within saved list
- ✅ Correct count shown

**Data Validation:**
- All jobs were previously saved
- Job information complete
- Timestamps accurate

---

### Test 4.2: Remove Saved Job from List
**Objective:** Verify removal from saved

**Steps:**
1. On saved jobs page
2. Click heart icon on job card
3. Verify removal

**Expected Result:**
- ✅ Job removed from list immediately
- ✅ Success message shown
- ✅ No errors

---

### Test 4.3: Quick Apply from Saved
**Objective:** Verify can apply directly from saved jobs

**Steps:**
1. On saved jobs page
2. Click job card to go to details
3. Click Apply
4. Submit application

**Expected Result:**
- ✅ Same apply flow as from browse page
- ✅ Application created successfully
- ✅ Job stays in saved list

---

## 🧪 Test Suite 5: Performance & Mobile (8 min)

### Test 5.1: Page Load Performance
**Objective:** Verify pages load quickly

**Steps:**
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Navigate to `/jobs/browse`
4. Check load time

**Expected Result:**
- ✅ Initial load < 3 seconds
- ✅ Job list renders < 2 seconds after API response
- ✅ Images optimized (< 50KB each)
- ✅ No waterfall blocking requests

**Metrics to Check:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1

---

### Test 5.2: Mobile Responsiveness
**Objective:** Verify mobile layout

**Steps:**
1. Open DevTools (F12)
2. Click device toggle (mobile view)
3. Select iPhone 12
4. Navigate through all pages
5. Test all interactions

**Pages to Test:**
- [ ] `/jobs/browse` - Jobs list (check card stacking)
- [ ] `/jobs/[id]` - Job details (check readability)
- [ ] `/jobs/applications` - Application list
- [ ] `/jobs/saved` - Saved jobs

**Expected Result:**
- ✅ All text readable without zooming
- ✅ Buttons large enough to tap (48px min)
- ✅ No horizontal scrolling
- ✅ Forms fill full width
- ✅ Navigation accessible on mobile

---

### Test 5.3: Tablet Responsiveness
**Objective:** Verify tablet layout

**Steps:**
1. In DevTools, select iPad
2. Navigate through pages
3. Verify layout optimization

**Expected Result:**
- ✅ Layout optimized for medium screen
- ✅ Proper spacing and sizing
- ✅ No text cutoff

---

## 🧪 Test Suite 6: Error Handling (5 min)

### Test 6.1: Network Error Handling
**Objective:** Verify behavior when API fails

**Steps:**
1. Open DevTools Network tab
2. Throttle to "Offline"
3. Try to load `/jobs/browse`
4. Should show error message

**Expected Result:**
- ✅ Error message appears
- ✅ Retry button available
- ✅ No crashes
- ✅ User can retry when online

---

### Test 6.2: Invalid Job ID
**Objective:** Verify behavior with bad URL

**Steps:**
1. Navigate to `/jobs/invalid-id`
2. Should handle gracefully

**Expected Result:**
- ✅ 404 error shown or redirected
- ✅ No crashes
- ✅ Back button available

---

### Test 6.3: Authentication Required
**Objective:** Verify auth protection

**Steps:**
1. Clear cookies/logout
2. Try to apply to job
3. Should require login

**Expected Result:**
- ✅ Redirected to login page
- ✅ Can login and complete application
- ✅ No data loss

---

## 🧪 Test Suite 7: Data Consistency (5 min)

### Test 7.1: Apply and Verify Database
**Objective:** Verify data persists to database

**Steps:**
1. Apply to job in UI
2. Check Supabase directly
3. Verify record exists

**Expected Result:**
- ✅ job_applications entry created
- ✅ All fields populated correctly
- ✅ Timestamps accurate

**Fields to Check:**
- user_id
- job_id
- status (should be "applied")
- match_score (0-100)
- applied_at (current timestamp)

---

### Test 7.2: Save Job and Verify Database
**Objective:** Verify saved jobs persist

**Steps:**
1. Save job in UI
2. Check Supabase saved_jobs table
3. Verify record exists

**Expected Result:**
- ✅ saved_jobs entry created
- ✅ user_id and job_id correct
- ✅ saved_at timestamp accurate

---

### Test 7.3: Update Application and Verify
**Objective:** Verify updates persist

**Steps:**
1. Update application status in UI
2. Check Supabase job_applications
3. Verify status changed

**Expected Result:**
- ✅ Status updated in database
- ✅ updated_at timestamp changed
- ✅ New fields saved (interview_date, etc.)

---

## 📊 Test Execution Checklist

### Test Suite 1: Job Search & Browse
- [ ] Test 1.1: View Job Listing
- [ ] Test 1.2: Search by Title
- [ ] Test 1.3: Filter by Location
- [ ] Test 1.4: Filter by Salary
- [ ] Test 1.5: Filter by Experience
- [ ] Test 1.6: Combined Filters

**Result:** ______ / 6 passed

---

### Test Suite 2: Job Details & AI Match
- [ ] Test 2.1: View Job Details
- [ ] Test 2.2: View AI Match Analysis
- [ ] Test 2.3: Save Job to Bookmarks
- [ ] Test 2.4: Remove Saved Job

**Result:** ______ / 4 passed

---

### Test Suite 3: Job Application Flow
- [ ] Test 3.1: Apply to Job
- [ ] Test 3.2: Prevent Duplicates
- [ ] Test 3.3: View Applications
- [ ] Test 3.4: Update Status
- [ ] Test 3.5: View Details
- [ ] Test 3.6: Withdraw Application

**Result:** ______ / 6 passed

---

### Test Suite 4: Saved Jobs
- [ ] Test 4.1: View Saved Jobs
- [ ] Test 4.2: Remove Saved Job
- [ ] Test 4.3: Quick Apply

**Result:** ______ / 3 passed

---

### Test Suite 5: Performance & Mobile
- [ ] Test 5.1: Load Performance
- [ ] Test 5.2: Mobile Responsiveness
- [ ] Test 5.3: Tablet Responsiveness

**Result:** ______ / 3 passed

---

### Test Suite 6: Error Handling
- [ ] Test 6.1: Network Errors
- [ ] Test 6.2: Invalid Job ID
- [ ] Test 6.3: Auth Required

**Result:** ______ / 3 passed

---

### Test Suite 7: Data Consistency
- [ ] Test 7.1: Apply & Verify DB
- [ ] Test 7.2: Save & Verify DB
- [ ] Test 7.3: Update & Verify DB

**Result:** ______ / 3 passed

---

## 📈 Overall Results

**Total Tests:** 28  
**Passed:** ______ / 28  
**Failed:** ______ / 28  
**Pass Rate:** ______ %

### Success Criteria:
- ✅ All tests pass (100%)
- ✅ No console errors
- ✅ Mobile responsive
- ✅ Load time < 3 seconds
- ✅ Data persists correctly

---

## 🐛 Issues Found

### Critical Issues (Blocks Launch)
1. ___________________________
2. ___________________________

### Major Issues (Must Fix)
1. ___________________________
2. ___________________________

### Minor Issues (Nice to Fix)
1. ___________________________
2. ___________________________

---

## ✅ Sign-Off

**Tested By:** _______________  
**Date:** _______________  
**Status:** [ ] Ready for Production [ ] Need Fixes

**Notes:**
_________________________________________________________________

---

## 🚀 Post-Testing Steps

When all tests pass:

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Phase 4 complete: Job marketplace fully tested and ready"
   ```

2. **Push to Main Branch**
   ```bash
   git push origin main
   ```

3. **Deploy to Production**
   - See PRODUCTION_DEPLOYMENT.md

4. **Run Smoke Tests in Production**
   - Verify endpoints accessible
   - Check database connections
   - Test with real users

5. **Monitor Metrics**
   - Page load times
   - API response times
   - Error rates
   - User engagement

---

**Generated:** October 23, 2025  
**Phase:** 4 - Job Marketplace  
**Status:** Ready for Testing  
**Next:** Execute tests above, then deploy
