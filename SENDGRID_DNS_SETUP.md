# SendGrid DNS Configuration Guide

## Overview

The DNS records shown are needed to verify your domain with SendGrid for sending emails. This is a one-time setup that enables email deliverability.

**Status**: ⏳ Needs DNS records added to your domain registrar

---

## DNS Records You Need to Add

Based on the screenshot, add these 6 records to your DNS provider:

| Type | Host | Value |
|------|------|-------|
| CNAME | `url1859.nextci.com` | `sendgrid.net` |
| CNAME | `56863448.nextci.com` | `sendgrid.net` |
| CNAME | `em1249.nextci.com` | `u56863448.wl199.sendgrid.net` |
| CNAME | `s1._domainkey.nextci.com` | `s1.domainkey.u56863448.wl199.sendgrid.net` |
| CNAME | `s2._domainkey.nextci.com` | `s2.domainkey.u56863448.wl199.sendgrid.net` |
| TXT | `_dmarc.nextci.com` | `v=DMARC1; p=none;` |

---

## Where to Add These Records

### Step 1: Identify Your DNS Provider

Find where your domain is registered (you bought it there):

- **GoDaddy**: https://www.godaddy.com
- **Namecheap**: https://www.namecheap.com
- **AWS Route 53**: https://aws.amazon.com/route53/
- **Google Domains**: https://domains.google
- **Cloudflare**: https://www.cloudflare.com
- **BlueHost**: https://www.bluehost.com
- **Other providers**: Search "[your registrar] add DNS records"

### Step 2: Login to Your DNS Provider

Access your domain management dashboard

### Step 3: Find DNS Settings

Look for:
- DNS Settings
- DNS Management
- DNS Records
- Nameserver settings

### Step 4: Add Records

For each record in the table above:

1. Click "Add Record" or similar button
2. Select Type (CNAME or TXT)
3. Enter Host name
4. Enter Value
5. Save

**CNAME Records Example** (for GoDaddy):
```
Type: CNAME
Name: url1859.nextci.com
Value: sendgrid.net
TTL: 3600 (or default)
```

**TXT Record Example** (for GoDaddy):
```
Type: TXT
Name: _dmarc.nextci.com
Value: v=DMARC1; p=none;
TTL: 3600 (or default)
```

---

## What These Records Do

### CNAME Records (5 records)
- Allow SendGrid to track clicks and opens
- Enable email bounce notifications
- Verify domain ownership
- Support multiple sending domains

**Records 1-2** (CNAME → sendgrid.net):
- Domain verification
- Click/open tracking setup

**Records 3-5** (CNAME → u56863448.wl199.sendgrid.net):
- Email authentication
- DKIM signing
- Bounce handling

### TXT Record (1 record)
- DMARC policy
- Tells receiving email servers how to handle failures
- `p=none` = monitoring mode (doesn't reject emails)
- Later: Change to `p=quarantine` or `p=reject` for stricter policy

---

## How Long This Takes

| Step | Time | Notes |
|------|------|-------|
| Add DNS records | 5 min | Actual copy/paste |
| DNS propagation | 15-30 min | Varies by provider |
| SendGrid verification | Automatic | Happens when DNS resolves |
| **Total** | **30 min** | Then emails will send |

---

## Verify Setup Was Successful

### Option 1: Using SendGrid Dashboard

1. Go to: SendGrid Dashboard → Settings → Sender Authentication
2. Click "Verify" next to your domain
3. Wait for verification (might take 5-30 min)
4. ✅ Status should show "Verified"

### Option 2: Using Terminal

Check if DNS records are set correctly:

```bash
# Check CNAME records
nslookup url1859.nextci.com
nslookup 56863448.nextci.com
nslookup em1249.nextci.com

# Check TXT record
nslookup -type=TXT _dmarc.nextci.com

# Or use dig (if installed)
dig url1859.nextci.com CNAME
dig _dmarc.nextci.com TXT
```

Expected output: Shows the values you added

### Option 3: Using Online Tools

Use free DNS lookup tools:
- https://mxtoolbox.com
- https://dnschecker.org
- https://www.whatsmydns.net

---

## Troubleshooting

### DNS Records Not Showing Up

**Problem**: `nslookup` returns "can't find" or "NXDOMAIN"

**Causes**:
1. DNS records not yet added
2. Wrong domain name entered
3. DNS not propagated yet (24-48 hours sometimes)

**Solutions**:
1. Verify records are actually in your DNS provider's dashboard
2. Check for typos (case-sensitive)
3. Wait 30 minutes and try again
4. Use `nslookup -type=A` to check basic domain works

### SendGrid Still Says Unverified

**Problem**: Records are added but SendGrid says "Not Verified"

**Causes**:
1. Records not fully propagated
2. Values copied incorrectly
3. Wrong record type selected

**Solutions**:
1. Wait 15-30 minutes for propagation
2. Double-check each record value matches exactly
3. Delete and recreate the record
4. Try manual verification in SendGrid

### Emails Not Sending

**Problem**: API works but emails don't arrive

**Causes**:
1. Domain not verified in SendGrid
2. Sender email not verified in SendGrid
3. Wrong API key
4. Rate limited (too many emails)

**Solutions**:
1. Check DNS records are verified in SendGrid
2. Check sender email verified (Settings → Sender Authentication)
3. Verify API key in `.env` is correct and not revoked
4. Check SendGrid activity logs for errors

---

## Production vs Development

### Development (Current)
- ✅ DNS records added (DKIM, SPF, DMARC)
- ✅ Domain verified in SendGrid
- ✅ Emails sent to test accounts
- ✅ DMARC policy: `p=none` (monitoring only)

### Production (Later)
- ✅ Same DNS records from development
- ✅ All above plus:
  - DMARC policy: `p=quarantine` or `p=reject` (stricter)
  - Send rate limits configured
  - Bounce handling configured
  - Unsubscribe list configured
  - SMTP relay configured
  - Compliance automation setup

**For now, keep `p=none` and focus on sending emails successfully**

---

## Current Status

### ✅ Completed
- SendGrid account created
- API key generated
- Domain added to SendGrid
- Backend code ready

### ⏳ IN PROGRESS
- DNS records added to domain (THIS STEP)
- SendGrid verifies domain

### ⏳ NEXT
- Backend receives verified domain notification
- Emails start sending successfully
- Test full authentication flow

---

## Quick Reference

**SendGrid Dashboard**: https://app.sendgrid.com

**Files involved**:
- `backend/.env` - Contains SENDGRID_API_KEY
- `backend/app/services/email_service.py` - Sends emails using SendGrid
- `SUPABASE_SENDGRID_SETUP.md` - Backend setup guide

**DNS Provider**: Your domain registrar (where you bought the domain)

---

## Next Steps

1. ✅ Add the 6 DNS records to your DNS provider
2. ⏳ Wait 15-30 minutes for DNS propagation
3. ⏳ Verify in SendGrid Dashboard
4. ✅ Test by sending a verification email via API
5. ✅ Check your email inbox

Once DNS is verified, emails will automatically send through SendGrid!

---

## Support

- SendGrid Docs: https://docs.sendgrid.com
- SendGrid Domain Verification: https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication
- DNS Records Guide: https://docs.sendgrid.com/ui/account-and-settings/dkim-spf-dmarc-dmarcagree
- Our Project: Check SUPABASE_SENDGRID_SETUP.md

**Status**: Ready for DNS configuration
**Next Action**: Add the 6 DNS records to your domain provider
