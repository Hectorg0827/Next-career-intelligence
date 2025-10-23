# 🧪 Phase 3 Testing - Command Reference

**Copy and paste these commands to test Phase 3**

---

## 🌐 Browser Tests (Most Important)

### Step 1: Open Chat Page
```
http://localhost:3000/coach/chat
```
Copy and paste this URL into your browser.

### Step 2: Send a Test Message
In the chat input, type any message like:
```
I'm a software engineer worried about AI replacing my job
```
Then click Send.

### Step 3: Open Conversations List
In your browser address bar, go to:
```
http://localhost:3000/coach/conversations
```

### Step 4: Test Loading Conversation
On the conversations page, click on a conversation card. The URL should change to include `?conversation_id=abc123...`

### Step 5: Test Archive
Hover over a conversation and click "Archive" button.

### Step 6: Test Delete
Hover over a conversation and click "Delete" button, then confirm.

### Step 7: Test Persistence
Reload the page with Cmd+R. Your conversations should still be there.

---

## 🔧 API Tests (Terminal Commands)

### Check Backend Health
```bash
curl http://localhost:8000/api/v1/health | jq
```

### Create Test Conversation
```bash
curl -X POST http://localhost:8000/api/coach/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "test-user-123",
    "title": "Test Conversation",
    "career_context": "Software Engineer"
  }' | jq
```

### List All Conversations
```bash
curl "http://localhost:8000/api/coach/conversations?firebase_uid=test-user-123" | jq
```

### Get Specific Conversation
Replace `CONVERSATION_ID` with the ID from the create command:
```bash
curl "http://localhost:8000/api/coach/conversations/CONVERSATION_ID?firebase_uid=test-user-123" | jq
```

### Archive a Conversation
```bash
curl -X PUT "http://localhost:8000/api/coach/conversations/CONVERSATION_ID/archive?firebase_uid=test-user-123" | jq
```

### Delete a Conversation
```bash
curl -X DELETE "http://localhost:8000/api/coach/conversations/CONVERSATION_ID?firebase_uid=test-user-123" | jq
```

---

## 📋 Full Test Checklist

### Before Testing
- [ ] Backend running: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend running: `curl http://localhost:3000` (should return 200)
- [ ] Browser open: Chrome, Safari, or Firefox
- [ ] Console open: F12 → Console tab

### Browser Tests
- [ ] Create conversation (chat sends message, AI responds)
- [ ] Conversations list loads (shows new conversation)
- [ ] Load from history (URL has conversation_id, messages load)
- [ ] Archive works (button visible, status changes)
- [ ] Delete works (conversation removed)
- [ ] Persistence (reload page, data still there)

### API Tests
- [ ] Create conversation returns 201
- [ ] List conversations returns array
- [ ] Get conversation returns full details
- [ ] Archive returns success
- [ ] Delete returns success

### Success Criteria
- [ ] No console errors (F12 → Console)
- [ ] No network errors (F12 → Network)
- [ ] All data persists
- [ ] All buttons responsive
- [ ] Fast loading (<2 seconds)

---

## 🚨 If Something Doesn't Work

### Issue: Can't access localhost:3000
```bash
# Check if frontend is running
curl -I http://localhost:3000

# Should show "HTTP/1.1 200 OK"
```

### Issue: Can't access localhost:8000
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Should show: {"status":"healthy",...}
```

### Issue: No AI Response in Chat
```bash
# Check if Gemini is configured
curl http://localhost:8000/api/v1/health | grep gemini_configured

# Should show: "gemini_configured": true
```

### Issue: Conversations List Empty
```bash
# Create a test conversation via API
curl -X POST http://localhost:8000/api/coach/conversations \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid":"test-user","title":"Test","career_context":"Testing"}' | jq
```

### Issue: Can't Archive or Delete
```bash
# Check that conversation ID is correct
# Open browser console (F12)
# Look for error messages
# Check network tab for failed requests
```

---

## 📊 Success Output Examples

### Backend Health (Should Look Like This)
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gemini_configured": true
}
```

### Create Conversation (Should Look Like This)
```json
{
  "id": "abc123def456",
  "user_id": "test-user-123",
  "title": "Test Conversation",
  "career_context": "Software Engineer",
  "is_active": "active",
  "created_at": "2025-10-23T02:09:54",
  "updated_at": "2025-10-23T02:09:54"
}
```

### List Conversations (Should Look Like This)
```json
[
  {
    "id": "abc123def456",
    "title": "Test Conversation",
    "user_id": "test-user-123",
    "is_active": "active",
    "created_at": "2025-10-23T02:09:54"
  }
]
```

---

## ⏱️ Estimated Test Times

| Test | Time |
|------|------|
| Chat message | 2 min |
| View list | 1 min |
| Load history | 1 min |
| Archive | 1 min |
| Delete | 1 min |
| Persistence | 1 min |
| API tests | 2 min |
| **Total** | **9 min** |

---

## 📝 Test Log Template

```
Date: October 23, 2025
Time: ___________
Tester: ___________

Test Results:
- Create conversation: [ ] PASS [ ] FAIL
- View list: [ ] PASS [ ] FAIL
- Load history: [ ] PASS [ ] FAIL
- Archive: [ ] PASS [ ] FAIL
- Delete: [ ] PASS [ ] FAIL
- Persistence: [ ] PASS [ ] FAIL
- API tests: [ ] PASS [ ] FAIL

Issues Found:
1. ___________
2. ___________
3. ___________

Status: [ ] PASS [ ] FAIL [ ] CONDITIONAL

Signature: ___________
```

---

## 🎯 Quick Reference

**Chat Page**: http://localhost:3000/coach/chat  
**Conversations**: http://localhost:3000/coach/conversations  
**API Docs**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/api/v1/health

---

**Ready to test? Start with the Browser Tests above!** 🚀
