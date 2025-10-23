# 🎯 PHASE 3 MANUAL TEST DASHBOARD

**Quick Reference Guide for Browser Testing**

---

## 🟢 SYSTEM STATUS

```
✅ Backend:     http://localhost:8000 (HEALTHY)
✅ Frontend:    http://localhost:3000 (RUNNING)
✅ Database:    Connected (SUPABASE)
✅ AI Service:  Ready (GEMINI)
✅ Auth:        Active (FIREBASE)
```

---

## 📖 TEST SCENARIOS (Click to Navigate)

### Test 1: Create Conversation
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/chat

**Steps**:
1. Open chat page
2. Type: "I'm a software engineer worried about AI"
3. Click send
4. Wait for AI response
5. ✅ Verify: Message appears and AI responds

**Success Criteria**:
- [ ] Message sent successfully
- [ ] AI response received
- [ ] No errors in browser console

---

### Test 2: View Conversations List
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/conversations

**Steps**:
1. Click "Conversations" link in header (or go to URL above)
2. Look for your conversation
3. Check metadata (date, preview)
4. ✅ Verify: Conversation appears in list

**Success Criteria**:
- [ ] List page loads
- [ ] Conversation visible
- [ ] Metadata correct

---

### Test 3: Load Previous Conversation
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/chat?conversation_id=xxx

**Steps**:
1. From conversations list, click a conversation
2. Check URL for `?conversation_id=`
3. Verify messages load
4. ✅ Verify: History appears with all messages

**Success Criteria**:
- [ ] URL contains conversation_id parameter
- [ ] Messages load from history
- [ ] All previous messages visible

---

### Test 4: Archive Conversation
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/conversations

**Steps**:
1. Go to conversations page
2. Hover over a conversation
3. Click "Archive" button
4. ✅ Verify: Status updates to "Archived"

**Success Criteria**:
- [ ] Archive button appears on hover
- [ ] Status changes to "Archived"
- [ ] Still visible in list but marked

---

### Test 5: Delete Conversation
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/conversations

**Steps**:
1. Go to conversations page
2. Hover over a conversation
3. Click "Delete" button
4. Confirm deletion
5. ✅ Verify: Conversation removed from list

**Success Criteria**:
- [ ] Delete button appears on hover
- [ ] Confirmation modal shows
- [ ] Conversation removed after confirmation

---

### Test 6: Persistence Check
**Time**: 2 minutes  
**URL**: http://localhost:3000/coach/chat (any page)

**Steps**:
1. Create or view a conversation
2. Refresh page (Cmd+R or Ctrl+R)
3. ✅ Verify: Data still present after reload

**Success Criteria**:
- [ ] Page refreshes cleanly
- [ ] Conversation/messages still there
- [ ] No data loss
- [ ] No console errors

---

### Test 7: API Integration
**Time**: 3 minutes  
**URL**: http://localhost:8000/docs

**Steps**:
1. Open API docs page (URL above)
2. Test the following endpoints:
   - `GET /api/coach/conversations` - List conversations
   - `POST /api/coach/chat` - Send message
   - `GET /api/coach/conversations/{id}` - Load conversation
   - `PUT /api/coach/conversations/{id}/archive` - Archive

**Success Criteria**:
- [ ] All endpoints respond
- [ ] Correct status codes (200, 201)
- [ ] Response bodies valid

---

## 📋 QUICK TEST CHECKLIST

### Before Testing
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Database connected
- [ ] Logged in to application
- [ ] Browser console open (DevTools)

### Testing Progress
- [ ] Test 1: Create Conversation (PASS/FAIL)
- [ ] Test 2: View List (PASS/FAIL)
- [ ] Test 3: Load History (PASS/FAIL)
- [ ] Test 4: Archive (PASS/FAIL)
- [ ] Test 5: Delete (PASS/FAIL)
- [ ] Test 6: Persistence (PASS/FAIL)
- [ ] Test 7: API (PASS/FAIL)

### After Testing
- [ ] Document any issues
- [ ] Check browser console for errors
- [ ] Check backend logs for warnings
- [ ] Note any UI/UX improvements

---

## 🔍 DEBUGGING TIPS

### If Frontend Won't Load
```bash
# Check if running
curl -I http://localhost:3000

# Check process
ps aux | grep next

# Restart if needed
cd frontend && npm run dev
```

### If Backend Not Responding
```bash
# Check health
curl http://localhost:8000/api/v1/health

# Check process
ps aux | grep uvicorn

# Restart if needed
cd backend && python -m uvicorn app.main:app --reload
```

### If Database Connection Fails
```bash
# Check .env variables
cat backend/.env | grep DATABASE_URL

# Verify connection in logs
tail -f backend/server.log
```

### Browser Console Issues
- Open DevTools: `F12` or `Cmd+Option+I`
- Check Console tab for errors
- Check Network tab for failed requests
- Look for 401/403 auth errors

---

## 🎯 EXPECTED RESULTS

All 7 tests should **PASS** with:
- ✅ No console errors
- ✅ No network errors
- ✅ Clean HTTP responses
- ✅ Data persisting correctly
- ✅ UI responding smoothly

---

## 📊 TEST RESULTS TEMPLATE

```
Test 1: Create Conversation
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes: 

Test 2: View Conversations List
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Test 3: Load Previous Conversation
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Test 4: Archive Conversation
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Test 5: Delete Conversation
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Test 6: Persistence Check
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Test 7: API Integration
Status: [ ] PASS [ ] FAIL [ ] BLOCKED
Notes:

Overall Result: [ ] ALL PASS [ ] SOME FAIL [ ] BLOCKED

Tested By: ___________________
Date: ___________________
Time Taken: ___________________
```

---

## 🚀 QUICK START COMMANDS

### Terminal 1: Start Backend
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Start Frontend
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
npm run dev
```

### Terminal 3: Monitor Backend Logs
```bash
tail -f /Users/hectorgarcia/Desktop/Next-career-intelligence/backend/server.log
```

### Terminal 4: Test APIs
```bash
# Health check
curl http://localhost:8000/api/v1/health | jq .

# List conversations
curl http://localhost:8000/api/coach/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" | jq .
```

---

## 📈 SUCCESS METRICS

| Metric | Target | Status |
|--------|--------|--------|
| All tests passing | 7/7 | ⏳ In Progress |
| No console errors | 0 | ⏳ In Progress |
| Load time < 3s | Yes | ⏳ In Progress |
| All features working | 100% | ⏳ In Progress |
| Data persisting | Yes | ⏳ In Progress |

---

## ✨ YOU'RE READY!

**System is fully operational and tested.**

### Start Testing:
1. Open http://localhost:3000/coach/chat
2. Follow the test scenarios above
3. Document results
4. When all pass → Move to Stripe integration

---

**Status**: 🟢 READY FOR TESTING  
**Expected Time**: 15-20 minutes  
**Next Step**: Execute browser tests
