# 🎯 Quick Start: Stripe Price ID Setup (5 Minutes)

## ⚠️ Action Required

Your payment system is **95% complete**. You just need to add Price IDs from Stripe Dashboard.

---

## 🚀 3 Simple Steps

### Step 1: Create Products in Stripe (2 min)

1. **Go to**: https://dashboard.stripe.com/test/products
   
2. **Create Monthly Plan**:
   - Click **"+ Add product"**
   - Name: `NEXT Career Pro - Monthly`
   - Description: `Full access to AI Career Coach, job marketplace, and advanced features`
   - Price: `$29`
   - Billing: `Recurring - Monthly`
   - Click **"Save product"**
   - ⚠️ **COPY THE PRICE ID** (looks like `price_1ABC...`)

3. **Create Yearly Plan**:
   - Click **"+ Add product"**
   - Name: `NEXT Career Pro - Yearly`  
   - Description: `Full access to AI Career Coach, job marketplace, and advanced features (Save $58/year)`
   - Price: `$290`
   - Billing: `Recurring - Yearly`
   - Click **"Save product"**
   - ⚠️ **COPY THE PRICE ID** (looks like `price_1XYZ...`)

### Step 2: Add Price IDs to Config (1 min)

Open `/frontend/.env.local` and add these lines at the bottom:

```bash
# ===== STRIPE PRICE IDS =====
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_xxxxxxxxxxxxx  # Paste monthly price ID here
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY=price_xxxxxxxxxxxxx   # Paste yearly price ID here
```

### Step 3: Restart Frontend (1 min)

```bash
# Stop the frontend (Ctrl+C in the terminal running it)
# Then restart:
cd frontend
npm run dev
```

---

## ✅ That's It!

Your payment system is now **100% functional**.

Test it:
```bash
./test_stripe.sh
```

Then visit: http://localhost:3000/pricing

---

## 🔄 Alternative: Use Test Mode First

If you want to test without creating live products:

1. **Switch to Test Mode** in Stripe Dashboard (toggle top-right)
2. Create test products with same names/prices
3. Use test keys in `.env` files:
   ```bash
   # Backend .env
   STRIPE_SECRET_KEY=sk_test_...
   
   # Frontend .env.local  
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
   NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_test_...
   NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY=price_test_...
   ```
4. Test with card: 4242 4242 4242 4242

---

## 📞 Need Help?

See full guide: `STRIPE_SETUP_GUIDE.md`

---

**Current Status**: ✅ Backend running | ✅ Frontend running | ✅ API keys configured | ⏳ Price IDs needed
