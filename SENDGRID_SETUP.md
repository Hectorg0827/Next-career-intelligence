# SendGrid Production Setup Guide

## Overview

Complete guide to configuring SendGrid for production email delivery with:
- Domain authentication (SPF, DKIM, DMARC)
- Sender reputation management
- Email analytics and tracking
- Bounce/spam handling
- Best practices for deliverability

---

## 1. SendGrid Account Setup

### Sign Up for SendGrid

1. **Create Account**: https://signup.sendgrid.com/
2. **Plan Selection**:
   - **Essentials Plan** ($19.95/mo): 50,000 emails/month, 2 teammates
   - **Pro Plan** ($89.95/mo): 100,000 emails/month, 1,000 teammates
   - **Recommended**: Start with Essentials, upgrade to Pro as you scale

3. **Verify Email**: Confirm your SendGrid account email

### Get API Key

1. Go to: Settings → API Keys → Create API Key
2. Name: `next-production`
3. Permissions: **Full Access** (for production)
4. **Save the API key immediately** (shown only once)

```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

5. Add to environment variables:
```bash
# Cloud Run
gcloud run services update next-backend \
  --region=us-east4 \
  --set-env-vars="SENDGRID_API_KEY=$SENDGRID_API_KEY"

# Local .env
echo "SENDGRID_API_KEY=$SENDGRID_API_KEY" >> backend/.env.production
```

---

## 2. Domain Authentication (Critical)

Domain authentication proves you own the domain and prevents emails from being marked as spam.

### Why Domain Authentication?

- **Without authentication**: Emails appear from `via sendgrid.net` → spam folder
- **With authentication**: Emails appear from `noreply@nextcareer.ai` → inbox
- **Improves deliverability by 30-40%**

### Authenticate Domain

1. **Go to**: Settings → Sender Authentication → Authenticate Your Domain
2. **Select DNS Host**: Choose your DNS provider (Cloudflare, GoDaddy, etc.)
3. **Enter Domain**: `nextcareer.ai`
4. **Use Automated Security**: Enable (recommended)

### DNS Records to Add

SendGrid will provide 3 DNS records to add to your domain:

#### SPF Record (Sender Policy Framework)

**Purpose**: Specifies which mail servers can send email from your domain

```
Type: TXT
Name: @
Value: v=spf1 include:sendgrid.net ~all
TTL: Auto
```

**Add to Cloudflare**:
1. Cloudflare Dashboard → DNS → Add Record
2. Type: TXT
3. Name: `@` (root domain)
4. Content: `v=spf1 include:sendgrid.net ~all`
5. TTL: Auto
6. Save

#### DKIM Records (DomainKeys Identified Mail)

**Purpose**: Cryptographically signs emails to verify they haven't been tampered with

SendGrid provides 2 CNAME records:

```
Record 1:
Type: CNAME
Name: s1._domainkey
Value: s1.domainkey.u12345.wl.sendgrid.net
TTL: Auto

Record 2:
Type: CNAME
Name: s2._domainkey
Value: s2.domainkey.u12345.wl.sendgrid.net
TTL: Auto
```

**Add both to Cloudflare DNS**

#### DMARC Record (Domain-based Message Authentication)

**Purpose**: Tells receiving servers what to do with emails that fail SPF/DKIM checks

```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@nextcareer.ai
TTL: Auto
```

**DMARC Policy Options**:
- `p=none`: Monitor only (start here)
- `p=quarantine`: Send to spam folder (after 2 weeks of monitoring)
- `p=reject`: Reject email completely (production, after 1 month)

**Recommended Progression**:
```
Week 1-2:  p=none (monitor)
Week 3-4:  p=quarantine
Month 2+:  p=reject
```

### Verify DNS Configuration

1. Wait 24-48 hours for DNS propagation
2. SendGrid → Sender Authentication → Verify
3. Status should show: ✅ **Verified**

### Check DNS Propagation

```bash
# Check SPF
dig nextcareer.ai TXT | grep spf

# Check DKIM
dig s1._domainkey.nextcareer.ai CNAME
dig s2._domainkey.nextcareer.ai CNAME

# Check DMARC
dig _dmarc.nextcareer.ai TXT
```

---

## 3. Sender Identity Configuration

### Set From Address

1. **Settings → Sender Authentication → Single Sender Verification**
2. Create verified sender:
   - From Email: `noreply@nextcareer.ai`
   - From Name: `NEXT Career Intelligence`
   - Reply To: `support@nextcareer.ai`
   - Address: Company address
3. Verify email (check inbox for verification link)

### Additional Verified Senders

Create separate senders for different email types:

```
noreply@nextcareer.ai       - General notifications
support@nextcareer.ai       - Support emails
billing@nextcareer.ai       - Payment/billing emails
team@nextcareer.ai          - Product updates, marketing
security@nextcareer.ai      - Security alerts
```

---

## 4. Email Sending Best Practices

### Sender Reputation Warmup

**Why warmup?** New sending domains have no reputation. Sending 50,000 emails immediately = spam folder.

**Warmup Schedule** (gradually increase volume):

```
Day 1-2:    50 emails/day
Day 3-4:    100 emails/day
Day 5-6:    250 emails/day
Day 7-10:   500 emails/day
Day 11-14:  1,000 emails/day
Day 15-21:  2,500 emails/day
Day 22-30:  5,000 emails/day
Month 2:    10,000 emails/day
Month 3+:   Full volume
```

**Warmup Tips**:
- Start with highly engaged users (recent signups)
- High open rates boost reputation
- Avoid sending to old/inactive emails initially

### Email Content Best Practices

#### Avoid Spam Triggers

**Spam Words to Avoid**:
- ALL CAPS SUBJECT LINES
- Free!!! Click here now!!!
- You won a prize
- Act now, limited time
- Cheap, discount, $$$
- Too many exclamation marks!!!

**Safe Practices**:
- ✅ Use sentence case: "Your weekly career digest"
- ✅ Personalize: "Hi {user_name}"
- ✅ Clear unsubscribe link
- ✅ Real company address in footer
- ✅ Balanced text/image ratio (60% text, 40% images)

#### HTML/Text Ratio

- **HTML only**: Higher spam score
- **Plain text only**: Low engagement
- **Best**: Include both HTML and plain text versions

SendGrid automatically creates plain text version, but you can specify:

```python
from sendgrid.helpers.mail import Mail, PlainTextContent, HtmlContent

message = Mail(
    from_email='noreply@nextcareer.ai',
    to_emails='user@example.com',
    subject='Test Email',
    plain_text_content=PlainTextContent('Plain text version'),
    html_content=HtmlContent('<html>HTML version</html>')
)
```

---

## 5. Bounce and Spam Handling

### Types of Bounces

1. **Hard Bounce**: Email address doesn't exist (remove immediately)
2. **Soft Bounce**: Temporary issue (mailbox full, server down)
3. **Spam Report**: User marked as spam (remove immediately)
4. **Block**: Receiving server blocked email

### Automatic Suppression

SendGrid automatically suppresses:
- Hard bounces (after 1 bounce)
- Spam reports (after 1 report)
- Invalid emails

**View Suppressions**: Email Activity → Suppressions

### Webhook for Bounce Handling

Create endpoint to handle bounce events:

**backend/app/api/webhooks.py**:

```python
from fastapi import APIRouter, Request, HTTPException
from loguru import logger

router = APIRouter(prefix="/webhooks/sendgrid", tags=["Webhooks"])

@router.post("/events")
async def handle_sendgrid_events(request: Request):
    """
    Handle SendGrid webhook events

    Events:
    - bounce: Email bounced (hard/soft)
    - dropped: SendGrid dropped email (suppression list)
    - spam_report: User marked as spam
    - unsubscribe: User clicked unsubscribe
    """
    events = await request.json()

    for event in events:
        event_type = event.get("event")
        email = event.get("email")

        if event_type in ["bounce", "spam_report", "dropped"]:
            # Mark email as invalid in database
            await mark_email_invalid(email, reason=event_type)
            logger.warning(f"Email {email} marked invalid: {event_type}")

        elif event_type == "unsubscribe":
            # Update user notification preferences
            await update_notification_preferences(email, unsubscribed=True)
            logger.info(f"User {email} unsubscribed")

    return {"status": "processed"}
```

### Configure Webhook in SendGrid

1. **Settings → Mail Settings → Event Webhook**
2. Enable: ✅ Event Webhook
3. HTTP Post URL: `https://api.nextcareer.ai/webhooks/sendgrid/events`
4. Select Events:
   - ✅ Bounced
   - ✅ Dropped
   - ✅ Spam Reports
   - ✅ Unsubscribes
   - ✅ Opens (optional, for analytics)
   - ✅ Clicks (optional, for analytics)
5. Save

---

## 6. Email Analytics

### SendGrid Dashboard

**Settings → Stats**:
- Delivery rate (target: > 98%)
- Open rate (target: > 20%)
- Click rate (target: > 3%)
- Bounce rate (target: < 2%)
- Spam rate (target: < 0.1%)

### Track Opens and Clicks

Enable tracking:

**Settings → Tracking**:
- ✅ Open Tracking: Track when emails are opened
- ✅ Click Tracking: Track link clicks
- ✅ Subscription Tracking: Track unsubscribes

**Note**: Open tracking uses invisible pixel (less accurate with Apple Mail Privacy Protection)

### Custom Analytics in Backend

Store email events in database:

**backend/app/models/email_analytics.py**:

```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime

class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    email = Column(String, index=True)
    template_name = Column(String)  # e.g., "payment_confirmation"
    event_type = Column(String)  # sent, delivered, opened, clicked, bounced
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)  # Additional event data
```

**Track email sends**:

```python
async def send_email_with_tracking(user_id: str, template: str, email: str):
    # Send email
    await email_service.send_payment_confirmation(...)

    # Log to database
    event = EmailEvent(
        user_id=user_id,
        email=email,
        template_name=template,
        event_type="sent",
        metadata={"subject": "Payment Confirmation"}
    )
    db.add(event)
    await db.commit()
```

---

## 7. Email Templates in SendGrid

### Dynamic Templates (Optional)

SendGrid offers a drag-and-drop template editor:

**Pros**:
- No-code template editing
- A/B testing built-in
- Version control

**Cons**:
- Less flexible than HTML
- Requires Handlebars syntax
- Harder to test locally

**Recommendation**: Use our custom HTML templates (already created) for maximum control.

---

## 8. Testing

### Test Email Delivery

```python
# Test script: backend/scripts/test_email.py
from app.services.email_service import get_email_service
import asyncio

async def test_emails():
    email_service = get_email_service()

    # Test verification email
    await email_service.send_verification_email(
        email="test@example.com",
        full_name="Test User",
        verification_code="123456"
    )

    print("✅ Test email sent! Check inbox.")

asyncio.run(test_emails())
```

Run:
```bash
cd backend
python scripts/test_email.py
```

### Inbox Testing Tools

1. **Mail-Tester**: https://www.mail-tester.com/
   - Send test email to provided address
   - Get spam score (target: 10/10)
   - Shows SPF, DKIM, DMARC results

2. **Litmus**: https://litmus.com/ (paid)
   - Test across 90+ email clients
   - Check rendering in Gmail, Outlook, Apple Mail, etc.

3. **Email on Acid**: https://www.emailonacid.com/ (paid)
   - Similar to Litmus
   - Spam filter testing

### SendGrid Sandbox Mode

For testing without actually sending emails:

```python
import os
os.environ["SENDGRID_SANDBOX_MODE"] = "true"

# Emails will be validated but not sent
```

---

## 9. Compliance (GDPR, CAN-SPAM)

### Unsubscribe Link (Required)

Every marketing email MUST have an unsubscribe link:

```html
<p style="font-size: 11px; color: #718096; margin-top: 10px;">
    <a href="{{ unsubscribe_url }}">Unsubscribe</a> from marketing emails
</p>
```

**Backend implementation**:

```python
@router.post("/unsubscribe")
async def unsubscribe_user(token: str):
    """Handle unsubscribe requests"""
    user_id = decode_unsubscribe_token(token)

    # Update preferences
    await db.execute(
        "UPDATE users SET marketing_emails = false WHERE id = $1",
        user_id
    )

    return {"message": "Successfully unsubscribed"}
```

### Physical Address (Required by CAN-SPAM)

Include company physical address in email footer:

```html
<p style="font-size: 11px; color: #718096;">
    NEXT Career Intelligence Inc.<br>
    123 Market Street, San Francisco, CA 94103
</p>
```

### Transactional vs Marketing Emails

**Transactional** (no unsubscribe required):
- Password resets
- Email verification
- Payment receipts
- Order confirmations

**Marketing** (unsubscribe required):
- Weekly digests
- Feature announcements
- Promotional offers
- Tips and tutorials

---

## 10. Cost Optimization

### SendGrid Pricing

**Essentials Plan** ($19.95/mo):
- 50,000 emails/month
- $0.0004 per additional email
- 2 teammates

**Pro Plan** ($89.95/mo):
- 100,000 emails/month
- $0.00035 per additional email
- 1,000 teammates

### Cost Estimates

**10,000 users**:
- Transactional emails: ~20,000/month (verification, payments)
- Marketing emails: ~40,000/month (weekly digests)
- Total: 60,000 emails/month
- Cost: **$19.95/mo** (Essentials plan + 10K overage = $24)

**100,000 users**:
- Transactional: 200,000/month
- Marketing: 400,000/month
- Total: 600,000/month
- Cost: **Pro plan + overage** = $90 + (500K × $0.00035) = $90 + $175 = **$265/mo**

### Reduce Costs

1. **Batch emails**: Send weekly digests on same day (not individual emails)
2. **Segment users**: Only send to engaged users (last 30 days)
3. **Unsubscribe inactive**: Remove users who never open emails (> 6 months)
4. **Throttle**: Don't send welcome email + digest + announcement same day

---

## 11. Monitoring & Alerts

### SendGrid Alerts

**Settings → Alerts**:

Create alerts for:
- **Bounce rate > 5%**: Email to engineering team
- **Spam rate > 0.5%**: Immediate alert
- **Daily send volume > 50,000**: Cost alert

### Sentry Integration

Log email failures to Sentry:

```python
from app.core.monitoring import alert_error, handle_external_api_error

try:
    response = sendgrid_client.send(message)
    if response.status_code not in [200, 201, 202]:
        alert_error(
            f"SendGrid error: {response.status_code}",
            context={"email": email, "template": template_name}
        )
except Exception as e:
    handle_external_api_error(e, service="SendGrid", endpoint="/mail/send")
    raise
```

---

## 12. Migration Checklist

- [ ] Create SendGrid account (Essentials plan)
- [ ] Generate API key with Full Access
- [ ] Add API key to Cloud Run environment variables
- [ ] Authenticate domain (SPF, DKIM, DMARC records)
- [ ] Wait 24-48 hours for DNS propagation
- [ ] Verify domain authentication (should show ✅)
- [ ] Create verified senders (noreply, support, billing)
- [ ] Configure webhook endpoint for bounce handling
- [ ] Enable open and click tracking
- [ ] Test email delivery (send test emails)
- [ ] Check spam score on Mail-Tester (target: 10/10)
- [ ] Set up warmup schedule (start with 50 emails/day)
- [ ] Configure SendGrid alerts (bounce rate, spam rate)
- [ ] Add unsubscribe link to all marketing emails
- [ ] Add physical address to email footers
- [ ] Monitor deliverability for first 2 weeks

---

## 13. Troubleshooting

### Issue: Emails going to spam

**Causes**:
- Domain not authenticated (missing SPF/DKIM)
- Sending too many emails too fast (warmup needed)
- Spam trigger words in subject/content
- High bounce rate (> 5%)

**Fixes**:
1. Verify SPF/DKIM records in DNS
2. Reduce send volume (follow warmup schedule)
3. Review email content for spam triggers
4. Clean email list (remove bounces)

### Issue: SPF/DKIM verification failing

**Cause**: DNS records not propagated or incorrect

**Fix**:
```bash
# Check DNS
dig nextcareer.ai TXT | grep spf
dig s1._domainkey.nextcareer.ai CNAME

# Wait 24-48 hours after adding records
# If still failing, check for typos in DNS records
```

### Issue: High bounce rate

**Causes**:
- Sending to old/invalid emails
- Email addresses with typos
- Using purchased email lists (don't do this!)

**Fixes**:
1. Validate emails before adding to database
2. Use double opt-in (email verification)
3. Remove hard bounces immediately
4. Clean list every 6 months (remove inactive users)

### Issue: SendGrid API errors

**Common errors**:
- 401 Unauthorized: Invalid API key
- 403 Forbidden: Account suspended (check billing)
- 429 Too Many Requests: Rate limit exceeded

**Fixes**:
- Regenerate API key if invalid
- Check account status in SendGrid dashboard
- Implement rate limiting (max 1000 req/sec)

---

## 14. Next Steps

After SendGrid is configured:

1. **Customer Support Setup** (Day 5-6): Intercom or Zendesk
2. **Knowledge Base** (Day 7): FAQ expansion
3. **Email Automation** (Week 4): Triggered campaigns (onboarding drip, re-engagement)

---

## References

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [SPF Record Syntax](https://www.dmarcanalyzer.com/spf/)
- [DMARC Guide](https://dmarc.org/)
- [CAN-SPAM Act Compliance](https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business)
- [Email Deliverability Best Practices](https://sendgrid.com/resource/email-deliverability-guide/)
