#!/bin/bash

# 🧪 Stripe Payment Flow Testing Script
# Tests the complete payment integration end-to-end

echo "🚀 NEXT Career Intelligence - Stripe Payment Testing"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "📋 Pre-flight Checks"
echo "-------------------"

# Check if backend is running
echo -n "1. Backend health check... "
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend running${NC}"
else
    echo -e "${RED}✗ Backend not running${NC}"
    echo "   Start with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# Check if frontend is running
echo -n "2. Frontend health check... "
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend running${NC}"
else
    echo -e "${RED}✗ Frontend not running${NC}"
    echo "   Start with: cd frontend && npm run dev"
    exit 1
fi

# Check environment variables
echo -n "3. Stripe configuration... "
if grep -q "STRIPE_SECRET_KEY=sk_" backend/.env && grep -q "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_" frontend/.env.local; then
    echo -e "${GREEN}✓ Keys configured${NC}"
else
    echo -e "${RED}✗ Keys missing${NC}"
    echo "   See STRIPE_SETUP_GUIDE.md"
    exit 1
fi

# Check for price IDs
echo -n "4. Price IDs configured... "
if grep -q "NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_" frontend/.env.local; then
    echo -e "${GREEN}✓ Price IDs set${NC}"
else
    echo -e "${YELLOW}⚠ Price IDs not set${NC}"
    echo "   Add to frontend/.env.local:"
    echo "   NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY=price_xxxxx"
    echo "   NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY=price_xxxxx"
fi

echo ""
echo "🧪 Manual Testing Checklist"
echo "----------------------------"
echo ""
echo "Follow these steps to test the payment flow:"
echo ""
echo "1. ${YELLOW}Visit Pricing Page${NC}"
echo "   → Open: $FRONTEND_URL/pricing"
echo ""
echo "2. ${YELLOW}Test Billing Toggle${NC}"
echo "   → Switch between Monthly ($29) and Yearly ($290)"
echo "   → Verify prices update correctly"
echo ""
echo "3. ${YELLOW}Start Checkout${NC}"
echo "   → Click 'Start Pro Trial' button"
echo "   → Should show loading spinner"
echo "   → Should redirect to Stripe Checkout"
echo ""
echo "4. ${YELLOW}Complete Payment (Test Mode)${NC}"
echo "   Email: test@example.com"
echo "   Card: 4242 4242 4242 4242"
echo "   Expiry: 12/25"
echo "   CVC: 123"
echo "   ZIP: 12345"
echo ""
echo "5. ${YELLOW}Verify Success Page${NC}"
echo "   → Should redirect to: $FRONTEND_URL/checkout/success"
echo "   → Shows 'Welcome to Pro!' message"
echo "   → Auto-redirects to dashboard after 5s"
echo ""
echo "6. ${YELLOW}Test Cancellation${NC}"
echo "   → Go back to pricing"
echo "   → Click 'Start Pro Trial'"
echo "   → In Stripe checkout, click back button"
echo "   → Should redirect to: $FRONTEND_URL/checkout/cancel"
echo ""
echo "7. ${YELLOW}Verify Database Update${NC}"
echo "   → Check Supabase dashboard"
echo "   → Find user by email: test@example.com"
echo "   → Verify fields:"
echo "     - subscription_status: 'pro'"
echo "     - stripe_customer_id: 'cus_...'"
echo "     - subscription_id: 'sub_...'"
echo ""
echo "8. ${YELLOW}Test Customer Portal${NC}"
echo "   → Navigate to: $FRONTEND_URL/subscription"
echo "   → Click 'Manage Subscription'"
echo "   → Should open Stripe Customer Portal"
echo "   → Try updating payment method"
echo "   → Try viewing invoices"
echo ""

echo "📊 Quick Database Check"
echo "----------------------"
echo "Run this SQL in Supabase SQL Editor:"
echo ""
echo "SELECT email, subscription_status, stripe_customer_id, subscription_id"
echo "FROM users"
echo "WHERE email = 'test@example.com';"
echo ""

echo "🔍 Debug Commands"
echo "----------------"
echo ""
echo "# View backend logs:"
echo "cd backend && tail -f logs/app.log"
echo ""
echo "# Check Stripe webhook events:"
echo "# Dashboard → Developers → Webhooks → [Your endpoint] → Events"
echo ""
echo "# Test webhook locally with Stripe CLI:"
echo "stripe listen --forward-to localhost:8000/api/payments/stripe-webhook"
echo ""

echo "✅ Test Card Numbers (Test Mode Only)"
echo "------------------------------------"
echo "Success:                4242 4242 4242 4242"
echo "Decline:                4000 0000 0000 0002"
echo "3D Secure Required:     4000 0025 0000 3155"
echo "Insufficient Funds:     4000 0000 0000 9995"
echo ""

echo "🎯 Expected API Calls"
echo "-------------------"
echo ""
echo "When clicking 'Start Pro Trial', you should see:"
echo ""
echo "1. POST $API_URL/payments/create-checkout-session"
echo "   Request: { price_id, success_url, cancel_url }"
echo "   Response: { url: 'https://checkout.stripe.com/...' }"
echo ""
echo "2. After payment, Stripe calls:"
echo "   POST $API_URL/payments/stripe-webhook"
echo "   Event: checkout.session.completed"
echo ""
echo "3. User upgraded in database"
echo "   UPDATE users SET subscription_status = 'pro' WHERE id = ..."
echo ""

echo "=================================================="
echo "Ready to test! Open your browser and start from step 1."
echo ""
