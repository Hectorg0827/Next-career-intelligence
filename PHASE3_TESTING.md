# 🧪 Phase 3 Testing Guide - Quick Start

## ✅ Ready to Test

**Systems Status**: All operational ✅
**Frontend**: http://localhost:3000
**Backend**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

---

## 🎯 What We're Testing

Phase 3 features implemented in this session:
- ✅ Conversations list page (NEW)
- ✅ Chat history loading (ENHANCED)
- ✅ Archive conversation endpoint (NEW)
- ✅ Full persistence through database

---

## 📋 Testing Workflow

### Test 1: Create a New Conversation
**Time**: 2 minutes

```
1. Navigate to http://localhost:3000/coach/chat
2. You should see a "Conversations" link in header
3. Type a message (e.g., "I'm a software engineer")
4. Click send button
5. System should:
   - Send message to AI Coach
   - Get response from Claude/Gemini
   - Display in chat
   - Show conversation created

✅ Expected Outcome: 
   - Message sent and responded
   - New conversation created
   - Conversation appears in database
```

### Test 2: View Conversations List
**Time**: 2 minutes

```
1. Click "Conversations" link in chat header
2. Should navigate to http://localhost:3000/coach/conversations
3. Your created conversation should appear in the list
4. List should show:
   - Conversation title (from first message)
   - Creation date
   - Last message time
   - Action buttons

✅ Expected Outcome:
   - Conversations page loads
   - Your conversation appears
   - Metadata displays correctly
```

### Test 3: Load Previous Conversation
**Time**: 2 minutes

```
1. In conversations list, click on a conversation
2. Should navigate to chat with ?conversation_id=xxx in URL
3. Previous messages should load automatically
4. Chat history should display

✅ Expected Outcome:
   - Chat loads previous messages
   - URL shows conversation_id parameter
   - History visible in UI
```

### Test 4: Archive Conversation
**Time**: 2 minutes

```
1. In conversations list, hover over a conversation card
2. Look for "Archive" button (archive icon)
3. Click archive button
4. Conversation status should change
5. You might see archived badge

✅ Expected Outcome:
   - Archive button functional
   - Conversation marked as archived
   - UI reflects status change
```

### Test 5: Delete Conversation
**Time**: 2 minutes

```
1. In conversations list, hover over a conversation card
2. Look for "Delete" button (trash icon)
3. Click delete button
4. Confirmation dialog should appear
5. Confirm deletion
6. Conversation should disappear from list

✅ Expected Outcome:
   - Delete button shows confirmation
   - Conversation removed after confirm
   - List updates immediately
```

### Test 6: Persistence Check
**Time**: 2 minutes

```
1. Create a conversation
2. Add multiple messages
3. Go to conversations list
4. Reload the page (Cmd+R)
5. Conversations should still be there
6. Click on conversation
7. All messages should load

✅ Expected Outcome:
   - Data persists across page reloads
   - Conversation history complete
   - No data loss
```

### Test 7: API Integration Check
**Time**: 3 minutes

```bash
# Check if conversations endpoint works
curl -X GET http://localhost:8000/api/coach/conversations \
  -H "Authorization: Bearer YOUR_TOKEN"

# Try archive endpoint
curl -X PUT http://localhost:8000/api/coach/conversations/{conversation_id}/archive \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

✅ Expected Outcome:
   - Both endpoints return 200 status
   - Data returned in correct format
   - No server errors in backend logs
```

---

## 🎬 Full Test Scenario (10 minutes)

**Goal**: Complete user flow from start to finish

```
STEP 1: Start conversation (2 min)
├─ Navigate to http://localhost:3000/coach/chat
├─ Send a message: "Analyze my career as a Product Manager"
├─ Get AI response
└─ Conversation created

STEP 2: Check list (2 min)
├─ Click "Conversations" link
├─ Verify conversation appears
├─ Check metadata displays
└─ Note the conversation ID

STEP 3: Load conversation (2 min)
├─ Click on conversation in list
├─ Verify messages load
├─ Check URL has ?conversation_id=xxx
└─ Continue conversation with new message

STEP 4: Archive & Delete (2 min)
├─ Create second test conversation
├─ Archive it (should move to archived state)
├─ Delete the first conversation
├─ Verify only one remains
└─ Reload page to verify persistence

STEP 5: API verification (2 min)
├─ Check /docs for API spec
├─ Try archive endpoint in Postman
├─ Try delete endpoint in Postman
└─ Verify all return correct status
```

---

## 🐛 Troubleshooting

### Issue: "Conversations" link not showing
**Solution**: 
- Check if chat page loaded properly
- Check browser console for errors
- Verify frontend running on :3000

### Issue: Conversations list empty
**Solution**:
- Make sure conversation was created (check chat)
- Check backend logs for errors
- Try creating a new conversation

### Issue: Delete confirmation doesn't appear
**Solution**:
- Check browser console for JavaScript errors
- Verify modal component loaded
- Try different conversation

### Issue: Archive not working
**Solution**:
- Check if user authenticated
- Verify backend archive endpoint exists
- Check browser network tab for 404 errors

### Issue: Persistence not working
**Solution**:
- Check Supabase connection
- Verify database tables exist
- Check backend logs for errors

---

## ✅ Test Results Template

Use this to track your testing:

```markdown
# Phase 3 Testing Results

## Test 1: Create Conversation
- [ ] Message sent successfully
- [ ] AI response received
- [ ] Conversation created
- Status: _____ (PASS/FAIL)

## Test 2: View Conversations List
- [ ] Conversations page loads
- [ ] New conversation appears
- [ ] Metadata displays correctly
- Status: _____ (PASS/FAIL)

## Test 3: Load Previous Conversation
- [ ] Chat loads with URL parameter
- [ ] Previous messages display
- [ ] Can continue conversation
- Status: _____ (PASS/FAIL)

## Test 4: Archive Conversation
- [ ] Archive button visible
- [ ] Archive request succeeds
- [ ] Status updates
- Status: _____ (PASS/FAIL)

## Test 5: Delete Conversation
- [ ] Delete button visible
- [ ] Confirmation dialog appears
- [ ] Conversation removed
- Status: _____ (PASS/FAIL)

## Test 6: Persistence
- [ ] Data survives page reload
- [ ] Full history loads
- [ ] All messages present
- Status: _____ (PASS/FAIL)

## Test 7: API Integration
- [ ] GET conversations works
- [ ] PUT archive works
- [ ] DELETE works
- Status: _____ (PASS/FAIL)

## Overall Result: PASS / FAIL
```

---

## 📊 Success Criteria

✅ **All tests pass** = Phase 3 ready for production
⚠️ **1-2 failures** = Minor issues to fix
❌ **3+ failures** = Major issues, requires rework

---

## 🔧 If Tests Fail

### Check Logs
```bash
# Backend logs
tail -f backend/server.log

# Frontend console
Open http://localhost:3000 → Right-click → Inspect → Console
```

### Check Database
```sql
-- Verify conversations exist
SELECT * FROM conversations LIMIT 5;

-- Check messages
SELECT * FROM coach_messages LIMIT 5;
```

### API Testing
```bash
# Test health
curl http://localhost:8000/api/v1/health

# Test conversations
curl http://localhost:8000/docs  # Open in browser
```

---

## 🎯 Next After Testing

### If All Tests Pass ✅
1. Move to Stripe integration (30 min)
2. Then start Phase 4 design
3. Begin Phase 4 implementation

### If Some Tests Fail ⚠️
1. Document the specific failures
2. Check backend/frontend logs
3. Debug the issue
4. Re-run failing test
5. Once fixed, proceed

### If Major Issues ❌
1. Review the architecture
2. Check database connections
3. Verify API endpoints
4. Restart both services
5. Re-run full test suite

---

## 📞 Quick Reference

| Feature | Endpoint | Status |
|---------|----------|--------|
| Create Conversation | POST /coach/conversations/start | ✅ |
| Send Message | POST /coach/conversations/message | ✅ |
| List Conversations | GET /coach/conversations | ✅ |
| Load Conversation | GET /coach/conversations/{id} | ✅ |
| Archive Conversation | PUT /coach/conversations/{id}/archive | ✅ NEW |
| Delete Conversation | DELETE /coach/conversations/{id} | ✅ |

---

## ⏱️ Time Estimate

| Test | Time | Complexity |
|------|------|------------|
| Create Conversation | 2 min | Low |
| View List | 2 min | Low |
| Load Conversation | 2 min | Low |
| Archive | 2 min | Low |
| Delete | 2 min | Low |
| Persistence | 2 min | Low |
| API Check | 3 min | Medium |
| **TOTAL** | **15 min** | **Low** |

---

## 🎉 Success!

Once all tests pass:
- ✅ Phase 3 complete and verified
- ✅ Ready for Phase 4
- ✅ Ready for production deployment
- ✅ Ready for user testing

**Next Step**: Start Phase 4 (Job Marketplace)

---

*Ready to test?* Start with Test 1: Create a Conversation!
