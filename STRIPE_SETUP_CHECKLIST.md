# 🎯 STRIPE SETUP - LIVE ACTION CHECKLIST

## Your Mission: Add 3 Price IDs (10 minutes)

---

## ✅ STEP 1: Go to Stripe Dashboard (2 minutes)

**URL:** https://dashboard.stripe.com/

**Login with:** stripe@nextcareer.ai (or your Stripe account)

**Verify you see:**
- ✅ Account dashboard
- ✅ Products section in left sidebar
- ✅ Your account balance

---

## ✅ STEP 2: Find or Create Products (3 minutes)

### Navigate to Products
1. Left sidebar → **Products**
2. Look for: "NEXT Career Intelligence Pro" or "Pro" product

### If Product Doesn't Exist - CREATE IT:

**Product A: Pro Monthly**
1. Click **"Add product"**
2. Fill in:
   - **Product name:** "Pro Monthly"
   - **Type:** Service
   - **Description:** "NEXT Career Intelligence Pro - Monthly Subscription"
3. Click **"Add pricing"**
4. Fill in:
   - **Price:** 29.00 (USD)
   - **Billing period:** Monthly
   - **Nickname:** "Pro Monthly"
5. Click **"Save product"**
6. **Copy the Price ID** (starts with `price_`)
   - Save it as: `PRICE_ID_MONTHLY = price_xxxxx`

**Product B: Pro Yearly**
1. Click **"Add product"**
2. Fill in:
   - **Product name:** "Pro Yearly"
   - **Type:** Service
   - **Description:** "NEXT Career Intelligence Pro - Annual Subscription"
3. Click **"Add pricing"**
4. Fill in:
   - **Price:** 290.00 (USD)
   - **Billing period:** Yearly
   - **Nickname:** "Pro Yearly"
5. Click **"Save product"**
6. **Copy the Price ID** (starts with `price_`)
   - Save it as: `PRICE_ID_YEARLY = price_xxxxx`

---

## ✅ STEP 3: Update Environment Variables (3 minutes)

### Edit Frontend `.env.local`

**File location:** `/frontend/.env.local`

**Current content (with placeholders):**
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_51SKRgL...
# PRICE IDS (to be filled):
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_placeholder
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY=price_placeholder
```

**Replace with your actual price IDs:**
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_51SKRgL...
# PRICE IDS (from Stripe Dashboard):
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_1ABC1234567890ABC
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY=price_1ABC1234567890XYZ
```

**Save the file** (Ctrl+S or Cmd+S)

---

## ✅ STEP 4: Restart Frontend (2 minutes)

**Terminal command:**
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
npm run dev
```

**Wait for:**
```
> ready - started server on 0.0.0.0:3000
```

---

## ✅ STEP 5: Test Pricing Page (5 minutes)

**In your browser, go to:**
```
http://localhost:3000/pricing
```

**You should see:**
- ✅ Free plan card
- ✅ Pro plan card with YOUR price ($29/month or $290/year)
- ✅ Enterprise plan card
- ✅ Billing toggle button (Monthly/Yearly)
- ✅ "Start Pro Trial" button (clickable)

**Quick tests:**
1. Toggle between Monthly/Yearly
2. Price should update correctly
3. Click "Start Pro Trial"
4. Should redirect to Stripe Checkout

---

## 🎯 TEST CHECKOUT FLOW (Bonus - 5 minutes)

**If you want to test payment (optional):**

1. On pricing page, click **"Start Pro Trial"**
2. You'll be taken to Stripe Checkout
3. Enter test card: `4242 4242 4242 4242`
4. Enter expiry: `12/26` (any future date)
5. Enter CVC: `123` (any 3 digits)
6. Click **"Pay"**
7. Should see success page

**Expected:** Success page or redirect to `/checkout/success`

---

## ✅ COMPLETION CHECKLIST

Before marking done:

- [ ] Logged into Stripe Dashboard
- [ ] Located or created products
- [ ] Copied 2 price IDs from Stripe
- [ ] Updated frontend `.env.local` with price IDs
- [ ] Restarted frontend (npm run dev)
- [ ] Pricing page loads at http://localhost:3000/pricing
- [ ] Pricing page shows correct prices
- [ ] Billing toggle works
- [ ] Can click "Start Pro Trial" button

---

## 🎉 SUCCESS CRITERIA

**When done, you'll have:**
- ✅ Stripe payment system configured
- ✅ Real price IDs in use
- ✅ Pricing page with correct prices
- ✅ Functional checkout flow
- ✅ 100% payment setup complete

**Platform status:** 65% → 75% (after Stripe) ✅

---

## ❓ COMMON ISSUES

### Issue: Pricing page shows placeholder prices
**Solution:** 
- Check `.env.local` has correct price IDs
- Restart frontend: `npm run dev`
- Hard refresh browser: Cmd+Shift+R or Ctrl+Shift+R

### Issue: Can't find Stripe Dashboard
**Solution:**
- Go to: https://dashboard.stripe.com/
- Make sure you're logged in with correct account
- Check email in top right

### Issue: Checkout button doesn't work
**Solution:**
- Make sure backend is running (port 8000)
- Check browser console for errors (F12)
- Verify price IDs are correct format: `price_xxxxx`

### Issue: Error creating product
**Solution:**
- Try again - might be temporary error
- Use existing product if available
- Contact Stripe support if persists

---

## ⏱️ TIME TRACKER

| Step | Time | Status |
|------|------|--------|
| 1. Stripe Dashboard | 2 min | ⏳ |
| 2. Find/Create Products | 3 min | ⏳ |
| 3. Update .env.local | 3 min | ⏳ |
| 4. Restart Frontend | 2 min | ⏳ |
| 5. Test Pricing Page | 5 min | ⏳ |
| **TOTAL** | **~15 min** | |

---

## 🚀 AFTER COMPLETION

**Next steps:**
1. ✅ Mark Stripe as COMPLETE
2. ✅ Platform is now 75% complete
3. ✅ Can deploy to production
4. ✅ Ready to start Phase 4 (Job Marketplace)

**Or, continue immediately:**
- Deploy to production
- Start Phase 4 implementation
- Test with real users

---

## 💡 NOTES

- These are PRODUCTION price IDs (not test mode)
- You can change prices anytime in Stripe Dashboard
- Webhook setup is OPTIONAL for MVP (already configured for success)
- Test payment uses test card: 4242 4242 4242 4242

---

**Status:** Ready to begin Stripe setup  
**Time Estimate:** 15 minutes  
**Difficulty:** Easy (3 copy-paste operations)  
**Outcome:** 100% payment system live 🎉

**Let's go! ➡️ Open Stripe Dashboard now**

---

Generated: October 23, 2025  
Session: Stripe Integration Phase
