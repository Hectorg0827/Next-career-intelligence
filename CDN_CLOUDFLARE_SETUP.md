# Cloudflare CDN Setup Guide

## Overview

Cloudflare provides a global Content Delivery Network (CDN) to:
- **Cache static assets** (JS, CSS, images) at edge locations worldwide
- **Reduce latency** by serving content from nearest data center
- **Reduce bandwidth costs** on origin servers (Cloud Run, Vercel)
- **DDoS protection** and Web Application Firewall (WAF)
- **SSL/TLS encryption** with automatic certificate management

**Plan**: Cloudflare Pro ($20/mo) for advanced caching and WAF

---

## 1. Domain Setup

### Purchase Domain (if not already owned)

Recommended registrars:
- **Namecheap**: $10-15/year for `.com`
- **Google Domains**: $12/year
- **Cloudflare Registrar**: $9/year (no markup)

**Recommended domain**: `nextcareer.ai` or `next.careers`

### Transfer DNS to Cloudflare

1. **Sign up**: https://dash.cloudflare.com/sign-up
2. **Add Site**: Click "Add a Site" → Enter your domain
3. **Select Plan**: Choose "Pro" ($20/month)
4. **Update Nameservers**:
   - Cloudflare will show you 2 nameservers (e.g., `ns1.cloudflare.com`, `ns2.cloudflare.com`)
   - Go to your domain registrar (Namecheap, etc.)
   - Replace existing nameservers with Cloudflare's
   - Wait 24-48 hours for DNS propagation

---

## 2. DNS Configuration

### Add DNS Records

In Cloudflare Dashboard → DNS:

```
Type    Name        Content                             Proxy   TTL
----    ----        -------                             -----   ---
A       @           <Vercel IP or CNAME>                ✅      Auto
CNAME   www         nextcareer.ai                       ✅      Auto
CNAME   api         next-backend-xxx.run.app            ✅      Auto
CNAME   cdn         nextcareer.ai                       ✅      Auto
TXT     @           google-site-verification=xxx        ❌      Auto
```

**Important**: Enable "Proxied" (orange cloud) for caching and protection

### Explanation:

- **@ (root domain)**: Points to frontend (Vercel)
- **www**: Redirects to root domain
- **api**: Points to backend (Cloud Run)
- **cdn**: Dedicated subdomain for static assets
- **TXT**: Google Search Console verification

---

## 3. SSL/TLS Configuration

### Enable Full (Strict) SSL

Cloudflare → SSL/TLS → Overview:
- Select: **Full (strict)**
- This ensures end-to-end encryption (Cloudflare ↔ Origin server)

### Enable Always Use HTTPS

SSL/TLS → Edge Certificates:
- ✅ **Always Use HTTPS**: Redirect HTTP → HTTPS
- ✅ **Automatic HTTPS Rewrites**: Rewrite HTTP links to HTTPS
- ✅ **Minimum TLS Version**: TLS 1.2 (disable TLS 1.0/1.1)
- ✅ **Opportunistic Encryption**: Enable
- ✅ **TLS 1.3**: Enable (faster handshakes)

### HTTP Strict Transport Security (HSTS)

SSL/TLS → Edge Certificates → HSTS:
- **Enable HSTS**: Yes
- **Max Age**: 6 months (15768000 seconds)
- **Include Subdomains**: Yes
- **Preload**: Yes (after testing)

---

## 4. Caching Configuration

### Cache Rules (Page Rules)

Cloudflare → Rules → Page Rules:

#### Rule 1: Cache Static Assets Aggressively

```
URL Pattern: cdn.nextcareer.ai/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 week
```

#### Rule 2: Cache Frontend Pages

```
URL Pattern: nextcareer.ai/*
Settings:
  - Cache Level: Standard
  - Edge Cache TTL: 2 hours
  - Browser Cache TTL: 30 minutes
  - Bypass Cache on Cookie: session_id,auth_token
```

#### Rule 3: Don't Cache API Requests

```
URL Pattern: api.nextcareer.ai/*
Settings:
  - Cache Level: Bypass
```

### Cache by Device Type

Settings → Caching → Configuration:
- ✅ **Cache by Device Type**: Enable (separate cache for mobile/desktop)
- ❌ **Development Mode**: Disable (only use for testing)

### Browser Cache TTL

Settings → Caching → Configuration:
- **Browser Cache TTL**: 4 hours (default)
- This tells browsers how long to cache before revalidating

---

## 5. Performance Optimization

### Enable HTTP/3 (QUIC)

Network → HTTP/3: **Enable**
- Faster than HTTP/2
- Better mobile performance
- Reduced latency

### Enable 0-RTT Connection Resumption

Network → 0-RTT Connection Resumption: **Enable**
- Reduces TLS handshake time
- Faster repeat visits

### Enable Brotli Compression

Speed → Optimization:
- ✅ **Brotli**: Enable (better than gzip)
- ✅ **Auto Minify**: JavaScript, CSS, HTML
- ✅ **Rocket Loader**: Enable (async JS loading)
- ⚠️ **Mirage**: Disable (can cause image loading issues)

### Enable Early Hints

Speed → Optimization:
- ✅ **Early Hints**: Enable
- Sends HTTP 103 responses with Link headers to preload resources

---

## 6. Security Configuration

### Web Application Firewall (WAF)

Security → WAF:
- **Managed Rules**: Enable all recommended rules
  - ✅ Cloudflare Managed Ruleset
  - ✅ Cloudflare OWASP Core Ruleset
  - ✅ Cloudflare Exposed Credentials Check
- **Sensitivity**: Medium (adjust if false positives)

### Rate Limiting

Security → WAF → Rate Limiting Rules:

#### Rule 1: Protect Login Endpoint

```
If:
  - Hostname equals api.nextcareer.ai
  - URI Path equals /api/auth/login
Then:
  - Rate limit: 5 requests per minute per IP
  - Action: Block for 1 hour
```

#### Rule 2: Protect Signup Endpoint

```
If:
  - Hostname equals api.nextcareer.ai
  - URI Path equals /api/auth/signup
Then:
  - Rate limit: 3 requests per hour per IP
  - Action: Block for 24 hours
```

#### Rule 3: General API Rate Limit

```
If:
  - Hostname equals api.nextcareer.ai
Then:
  - Rate limit: 1000 requests per minute per IP
  - Action: Challenge (CAPTCHA)
```

### DDoS Protection

Security → DDoS:
- **HTTP DDoS Attack Protection**: Enable (automatic)
- **Sensitivity Level**: High

### Bot Fight Mode

Security → Bots:
- ✅ **Bot Fight Mode**: Enable
- ✅ **Super Bot Fight Mode** (Pro plan): Enable
  - Block AI scrapers (ChatGPT, etc.)
  - Challenge suspicious bots
  - Allow verified bots (Google, Bing)

---

## 7. Frontend Integration (Vercel)

### Update Next.js Configuration

**frontend/next.config.js**:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable image optimization via Cloudflare
  images: {
    domains: ['cdn.nextcareer.ai'],
    formats: ['image/avif', 'image/webp'],
  },

  // CDN configuration
  assetPrefix: process.env.NODE_ENV === 'production'
    ? 'https://cdn.nextcareer.ai'
    : '',

  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  // Rewrites for API proxy
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.nextcareer.ai/:path*',
      },
    ]
  },
}

module.exports = nextConfig
```

### Update Environment Variables

**frontend/.env.production**:

```bash
NEXT_PUBLIC_API_URL=https://api.nextcareer.ai
NEXT_PUBLIC_CDN_URL=https://cdn.nextcareer.ai
NEXT_PUBLIC_SITE_URL=https://nextcareer.ai
```

### Update Image Imports

**Before**:
```tsx
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="NEXT Logo"
  width={200}
  height={50}
/>
```

**After** (using CDN):
```tsx
import Image from 'next/image'

const CDN_URL = process.env.NEXT_PUBLIC_CDN_URL || ''

<Image
  src={`${CDN_URL}/logo.png`}
  alt="NEXT Logo"
  width={200}
  height={50}
/>
```

---

## 8. Backend Integration (Cloud Run)

### Update CORS Configuration

**backend/app/main.py**:

```python
from fastapi.middleware.cors import CORSMiddleware

# Allow Cloudflare-proxied domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nextcareer.ai",
        "https://www.nextcareer.ai",
        "https://cdn.nextcareer.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Add Cache-Control Headers

```python
from fastapi import Response

@app.get("/api/jobs")
async def get_jobs(response: Response):
    """Get job listings (cacheable)"""

    # Allow Cloudflare to cache for 1 hour
    response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=3600"

    jobs = await db.query("SELECT * FROM jobs WHERE active = true")
    return {"jobs": jobs}

@app.post("/api/analyze")
async def analyze_resume(response: Response):
    """Analyze resume (don't cache)"""

    # Never cache personalized responses
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"

    result = await analyze_resume_logic()
    return result
```

---

## 9. Static Assets Setup

### Create CDN Bucket

Upload static assets to Google Cloud Storage:

```bash
# Create bucket
gsutil mb -l us-east4 gs://next-career-cdn

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://next-career-cdn

# Upload assets
gsutil -m cp -r frontend/public/* gs://next-career-cdn/

# Set cache headers
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" gs://next-career-cdn/**
```

### Configure Cloud CDN (Optional Fallback)

If Cloudflare has issues, use Cloud CDN:

```bash
# Create load balancer
gcloud compute backend-buckets create next-cdn-backend \
  --gcs-bucket-name=next-career-cdn

# Create URL map
gcloud compute url-maps create next-cdn-map \
  --default-backend-bucket=next-cdn-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create next-cdn-proxy \
  --url-map=next-cdn-map \
  --ssl-certificates=next-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create next-cdn-rule \
  --global \
  --target-https-proxy=next-cdn-proxy \
  --ports=443
```

---

## 10. Monitoring & Analytics

### Cloudflare Analytics

Dashboard → Analytics:

**Traffic Metrics**:
- Requests per second
- Bandwidth usage
- Cache hit rate (target: > 80%)
- Status codes (4xx, 5xx errors)

**Performance Metrics**:
- Time to First Byte (TTFB): Target < 200ms
- DNS resolution time: Target < 20ms
- Connection time: Target < 50ms
- TLS negotiation: Target < 50ms

**Security Metrics**:
- Threats blocked
- Bot requests
- DDoS attacks mitigated

### Set Up Alerts

Cloudflare → Notifications:

- ✅ **DDoS Attack**: Email + Slack
- ✅ **High Error Rate** (> 5% 5xx): Email + PagerDuty
- ✅ **SSL Certificate Expiring**: Email (30 days)
- ✅ **Zone SSL Disabled**: Immediate alert

### Web Analytics (Cloudflare vs Google Analytics)

Cloudflare Analytics:
- Privacy-friendly (no cookies)
- Real-time traffic data
- Bot filtering

Google Analytics 4:
- User behavior tracking
- Conversion funnels
- Demographic data

**Use both**: Cloudflare for infrastructure, GA4 for user insights

---

## 11. Cache Purging

### Manual Purge

Dashboard → Caching → Configuration → Purge Cache:

- **Purge Everything**: Nuclear option (use sparingly)
- **Purge by URL**: Specific files
- **Purge by Tag**: Grouped resources
- **Purge by Hostname**: Entire subdomain

### Automated Purge via API

```bash
# Purge specific URLs after deployment
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "files": [
      "https://nextcareer.ai/",
      "https://nextcareer.ai/pricing",
      "https://cdn.nextcareer.ai/assets/main.js"
    ]
  }'
```

### Cache Purge on Deploy

**frontend/.github/workflows/deploy.yml**:

```yaml
- name: Purge Cloudflare Cache
  run: |
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${{ secrets.CF_ZONE_ID }}/purge_cache" \
      -H "Authorization: Bearer ${{ secrets.CF_API_TOKEN }}" \
      -H "Content-Type: application/json" \
      --data '{"purge_everything": true}'
```

---

## 12. Testing

### Test Cache Hit Rate

```bash
# First request (MISS - fetches from origin)
curl -I https://cdn.nextcareer.ai/logo.png
# Should see: cf-cache-status: MISS

# Second request (HIT - served from edge)
curl -I https://cdn.nextcareer.ai/logo.png
# Should see: cf-cache-status: HIT
```

### Test Geographic Performance

Use WebPageTest: https://www.webpagetest.org/

- Test from: New York, London, Tokyo, Sydney
- Target: < 2 second load time from all locations
- Cloudflare should serve from nearest edge (< 50ms TTFB)

### Test DDoS Protection

Use Cloudflare's "Under Attack Mode":
- Security → Settings → Security Level: **I'm Under Attack**
- Shows CAPTCHA challenge to all visitors (temporary)
- Use only during actual DDoS

### SSL Test

https://www.ssllabs.com/ssltest/analyze.html?d=nextcareer.ai

Target: **A+ rating**
- TLS 1.3 enabled
- HSTS enabled
- No weak ciphers

---

## 13. Cost Breakdown

### Cloudflare Pro: $20/month

Includes:
- Unlimited bandwidth (no overage charges)
- 50 Page Rules
- Advanced DDoS protection
- WAF managed rules
- Image optimization
- Argo Smart Routing (optional: +$5/mo)
- Load Balancing (optional: +$5/mo per LB)

### Domain Registration: $10-15/year

Total monthly: **$20-25**

### Bandwidth Savings

Without Cloudflare (Vercel + Cloud Run bandwidth):
- Vercel: 100 GB free, $40 per 100 GB after
- Cloud Run: $0.12 per GB egress

With Cloudflare:
- All static assets served from edge (free)
- Estimated savings: $50-100/month at scale

**ROI**: Cloudflare pays for itself in bandwidth savings

---

## 14. Advanced Features (Optional)

### Cloudflare Workers (Edge Computing)

Deploy serverless functions at the edge:

```javascript
// workers/auth-check.js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // Check authentication before hitting origin
  const authToken = request.headers.get('Authorization')

  if (!authToken && url.pathname.startsWith('/dashboard')) {
    return new Response('Unauthorized', { status: 401 })
  }

  // Pass to origin
  return fetch(request)
}
```

**Cost**: $5/month for 10M requests

### Cloudflare Images (Paid)

Automatic image optimization:
- Resize images on-the-fly
- Convert to WebP/AVIF
- Lazy loading
- Responsive images

**Cost**: $5/month + $1 per 1,000 images

### Cloudflare Stream (Video Hosting)

Host career coaching videos:
- Adaptive bitrate streaming
- Global delivery
- Video analytics

**Cost**: $1 per 1,000 minutes viewed

---

## 15. Migration Checklist

- [ ] Sign up for Cloudflare Pro ($20/mo)
- [ ] Add domain to Cloudflare
- [ ] Update nameservers at registrar
- [ ] Wait for DNS propagation (24-48 hours)
- [ ] Configure DNS records (A, CNAME, TXT)
- [ ] Enable Full (Strict) SSL
- [ ] Configure Page Rules for caching
- [ ] Enable WAF and rate limiting
- [ ] Update frontend to use CDN URLs
- [ ] Update backend CORS configuration
- [ ] Test cache hit rate (target: > 80%)
- [ ] Run WebPageTest from multiple locations
- [ ] Set up Cloudflare Analytics alerts
- [ ] Configure automated cache purge on deploy
- [ ] Document Cloudflare API token in password manager

---

## 16. Troubleshooting

### Issue: "Too Many Redirects" Error

**Cause**: SSL/TLS mode mismatch

**Fix**:
- Cloudflare → SSL/TLS → Overview
- Change to: **Full (strict)** or **Full**
- Ensure origin server (Vercel/Cloud Run) has valid SSL certificate

### Issue: Assets Not Caching

**Cause**: Missing Cache-Control headers from origin

**Fix**:
- Add Cache-Control headers in backend responses
- Or use Page Rules to override (Cache Everything)

### Issue: Cache Serving Stale Content

**Fix**:
- Purge cache manually (Dashboard → Caching → Purge Everything)
- Or use versioned URLs for static assets: `/assets/main.v2.js`

### Issue: Low Cache Hit Rate (< 50%)

**Causes**:
- Too many unique URLs (query parameters)
- Cookies preventing caching
- Short TTLs

**Fixes**:
- Use Page Rules to ignore query strings
- Exclude cache-busting cookies
- Increase Edge Cache TTL for static assets

---

## 17. Next Steps

After CDN is configured:

1. **Sentry Monitoring** (Week 2, Day 5): Enhanced error tracking
2. **PagerDuty Integration** (Week 2, Day 6): Critical alerts
3. **Load Testing** (Week 10): Verify CDN performance under load

---

## References

- [Cloudflare Pro Documentation](https://developers.cloudflare.com/)
- [Page Rules Guide](https://support.cloudflare.com/hc/en-us/articles/218411427)
- [Cache Best Practices](https://developers.cloudflare.com/cache/)
- [Rate Limiting Rules](https://developers.cloudflare.com/waf/rate-limiting-rules/)
