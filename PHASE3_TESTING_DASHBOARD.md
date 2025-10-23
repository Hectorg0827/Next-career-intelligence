# 🧪 Phase 3 Browser Testing Dashboard

**Quick Reference for Manual Testing**  
**All 7 Tests Ready to Execute**  
**Status**: ✅ Automated Tests Passed → Ready for Browser

---

## 🎯 TEST DASHBOARD

### TEST 1: Create New Conversation ⏱️ 2 min
**URL**: http://localhost:3000/coach/chat

**Action**:
1. Find message input field
2. Type: `I'm worried about AI replacing my job`
3. Click Send button
4. Wait 2-3 seconds

**Success Checklist**:
- [ ] Message appears in chat
- [ ] AI responds with helpful advice
- [ ] No console errors (F12 → Console)
- [ ] No network errors (F12 → Network)

**Result**: ⏳ PENDING

---

### TEST 2: View Conversations List ⏱️ 1 min
**URL**: http://localhost:3000/coach/conversations

**Action**:
1. Click "Conversations" link (should be in header)
2. Wait for page to load
3. Look for your conversation in the list

**Success Checklist**:
- [ ] Page loads without errors
- [ ] Your conversation appears in list
- [ ] Shows creation time
- [ ] Shows action buttons (archive, delete)

**Result**: ⏳ PENDING

---

### TEST 3: Load from History ⏱️ 1 min
**URL**: Automatic (URL should show ?conversation_id=xxx)

**Action**:
1. Click on your conversation in the list
2. Observe URL changing
3. Wait for messages to load

**Success Checklist**:
- [ ] URL includes `?conversation_id=` parameter
- [ ] Previous messages appear
- [ ] Conversation loads automatically
- [ ] Can send new message

**Result**: ⏳ PENDING

---

### TEST 4: Archive Conversation ⏱️ 1 min
**Location**: Conversations list page

**Action**:
1. Hover over a conversation
2. Look for "Archive" button
3. Click Archive
4. Verify status updates

**Success Checklist**:
- [ ] Archive button visible on hover
- [ ] Click triggers action
- [ ] Conversation shows archived status
- [ ] Data persists

**Result**: ⏳ PENDING

---

### TEST 5: Delete Conversation ⏱️ 1 min
**Location**: Conversations list page

**Action**:
1. Hover over a conversation
2. Look for "Delete" button
3. Click Delete
4. Confirm deletion in dialog

**Success Checklist**:
- [ ] Delete button visible on hover
- [ ] Confirmation dialog appears
- [ ] Conversation removed from list after confirm
- [ ] Deleted from database

**Result**: ⏳ PENDING

---

### TEST 6: Persistence Check ⏱️ 1 min
**Action**:
1. Create a conversation with a message
2. Press Cmd+R (reload page)
3. Navigate back to conversations
4. Check if conversation still there

**Success Checklist**:
- [ ] Page reloads without errors
- [ ] Conversation still appears
- [ ] All messages still there
- [ ] Data properly persisted

**Result**: ⏳ PENDING

---

### TEST 7: API Integration ⏱️ 2 min
**Method**: Terminal commands (no browser needed)

**Action**: Run these curl commands:

```bash
# Test 1: Create
curl -X POST http://localhost:8000/api/coach/conversations \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid":"test-user","title":"Test","career_context":"Testing"}' | jq

# Test 2: List
curl "http://localhost:8000/api/coach/conversations?firebase_uid=test-user" | jq

# Test 3: Get (use conversation ID from Test 1)
curl "http://localhost:8000/api/coach/conversations/[ID]?firebase_uid=test-user" | jq

# Test 4: Archive
curl -X PUT "http://localhost:8000/api/coach/conversations/[ID]/archive?firebase_uid=test-user" | jq

# Test 5: Delete
curl -X DELETE "http://localhost:8000/api/coach/conversations/[ID]?firebase_uid=test-user" | jq
```

**Success Checklist**:
- [ ] All commands return 200/201 status
- [ ] Responses include valid JSON
- [ ] Conversation IDs returned
- [ ] All operations complete

**Result**: ⏳ PENDING

---

## 📊 SUMMARY TABLE

| Test | Expected | Status |
|------|----------|--------|
| 1. Create | Message + AI response | ⏳ PENDING |
| 2. List | Conversations display | ⏳ PENDING |
| 3. Load | Messages appear | ⏳ PENDING |
| 4. Archive | Status updates | ⏳ PENDING |
| 5. Delete | Removed from list | ⏳ PENDING |
| 6. Persist | Data after reload | ⏳ PENDING |
| 7. API | All endpoints respond | ⏳ PENDING |

**Total**: 7/7 Ready

---

## 🔍 Troubleshooting Quick Tips

### If Chat Page Doesn't Load
```bash
# Check frontend
curl http://localhost:3000/coach/chat

# Should return HTML (not 404)
```

### If No AI Response
```bash
# Check backend health
curl http://localhost:8000/api/v1/health | jq

# Should show: "gemini_configured": true
```

### If Conversations List Empty
```bash
# Create test conversation via API
curl -X POST http://localhost:8000/api/coach/conversations \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid":"test","title":"Test","career_context":"Test"}'
```

### If Tests Fail
1. Check browser console (F12 → Console tab)
2. Check network tab (F12 → Network tab)
3. Review error messages
4. Check backend logs
5. Retry the test

---

## 🎯 SUCCESS CRITERIA

### All Tests Pass When:
- ✅ 7/7 tests show PASS
- ✅ 0 console errors
- ✅ 0 network errors
- ✅ All data persists
- ✅ All buttons responsive

### Ready for Next Phase When:
- ✅ All tests pass
- ✅ No critical issues
- ✅ Data integrity verified
- ✅ Performance acceptable

---

## ⏱️ TIMING ESTIMATE

| Component | Time |
|-----------|------|
| Test 1 (Create) | 2 min |
| Test 2 (List) | 1 min |
| Test 3 (Load) | 1 min |
| Test 4 (Archive) | 1 min |
| Test 5 (Delete) | 1 min |
| Test 6 (Persist) | 1 min |
| Test 7 (API) | 2 min |
| **TOTAL** | **9 min** |

---

## 🚀 READY TO TEST?

### Start Here:
1. Open http://localhost:3000/coach/chat in browser
2. Follow TEST 1 instructions
3. Work through all 7 tests
4. Mark results in table above
5. When all pass → Phase 3 Complete ✅

---

## 📝 TEST LOG

```
Date: ________________
Start Time: ________________
End Time: ________________
Tester: ________________

Results:
- Test 1: [ ] PASS [ ] FAIL
- Test 2: [ ] PASS [ ] FAIL
- Test 3: [ ] PASS [ ] FAIL
- Test 4: [ ] PASS [ ] FAIL
- Test 5: [ ] PASS [ ] FAIL
- Test 6: [ ] PASS [ ] FAIL
- Test 7: [ ] PASS [ ] FAIL

Issues Found:
1. ________________
2. ________________
3. ________________

Status: [ ] PASS [ ] FAIL

Signature: ________________
```

---

## 🎉 PHASE 3 STATUS

**Automated Tests**: ✅ 5/5 PASSED  
**Code Verification**: ✅ 17+ VERIFIED  
**Manual Tests**: ⏳ READY TO EXECUTE  
**Documentation**: ✅ COMPLETE  

**Next Step**: Execute tests above  
**Expected Result**: All 7 tests pass ✅  
**Then**: Move to Stripe integration

---

**Ready to test?** Open http://localhost:3000/coach/chat and start TEST 1! 🚀

