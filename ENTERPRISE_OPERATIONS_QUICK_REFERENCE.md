# ENTERPRISE OPERATIONS QUICK REFERENCE

**Last Updated**: November 15, 2025  
**For**: Founder, Sales, Customer Success, DevOps  
**Purpose**: Quick answers on how enterprise will function

---

## 🎯 One-Sentence Pitch to Enterprises

> **"Career OS reduces your hiring time from 30 days to 14 days by using AI to find the best candidates. You save $1.8M annually in recruiting costs with 12x ROI."**

---

## 💰 Pricing Tiers (Easy to Remember)

### Tier 1: Starter ($50K/year)
- **For**: Early-stage companies, startups
- **Includes**: 10,000 API calls/month, basic search, email support
- **ROI**: ~$500K/year (10x return)
- **Customers**: Early adopters, proof-of-concept

### Tier 2: Professional ($150K/year)  
- **For**: Mid-market companies, fast-growing recruiting teams
- **Includes**: 100,000 API calls/month, advanced analytics, analytics API, phone support
- **ROI**: ~$2M/year (13x return)
- **Customers**: Main revenue segment (target 10+ by Month 6)

### Tier 3: Enterprise ($500K+/year)
- **For**: Fortune 500, global recruiting operations
- **Includes**: Unlimited API calls, white-label, custom integrations, dedicated CSM, SLA 99.99%
- **ROI**: ~$5M+/year (10x+ return)
- **Customers**: Aspirational, but high-margin (3-5 by Year 2)

---

## 🔄 Customer Lifecycle (12-Month Journey)

```
MONTH 1: DISCOVERY → MONTHS 2-3: IMPLEMENTATION → MONTHS 4-12: PRODUCTION → RENEWAL

Week 1      Week 2        Week 3          Month 2      Month 3      Month 4-12    Month 12
Sales Demo → Contract     Onboarding      Integration  Training     Live Ops      Renewal
            Signed        Starts          Complete     Complete     Running

ENTERPRISE DECISION: "We're seeing $500K annual recruiting ROI"
RESULT: Renewal at $250K/year (upgrade to Professional tier)
```

---

## 📊 What Enterprise Customers Need from You

### Week 1-2: Sales Team Needs
- [ ] ROI Calculator: Show them their specific savings
- [ ] Case Study: "How ACME Corp reduced hiring time by 50%"
- [ ] Product Demo: Live search + API integration demo
- [ ] Pricing Comparison: vs. LinkedIn, Indeed, traditional recruiting

### Week 3: Legal/Contracts Need
- [ ] Master Service Agreement (MSA)
- [ ] Data Processing Agreement (DPA) for GDPR
- [ ] SLA Document (99.95% uptime guarantee)
- [ ] Security & Compliance Checklist (SOC 2, ISO 27001)

### Month 1-2: Implementation Team Needs
- [ ] API Documentation (REST endpoints, webhooks)
- [ ] Integration Guides: Workday, Greenhouse, ATS/HRIS
- [ ] Candidate Portal Setup (white-label domain)
- [ ] Training Materials (for 50 recruiters)

### Month 2-3: Customer Success Needs
- [ ] Dashboard Access (real-time analytics)
- [ ] Metrics Tracking (API usage, ROI calculation)
- [ ] Support Channels (Slack, email, phone)
- [ ] Monthly Business Review Agenda

### Month 4+: Operations Team Needs
- [ ] Usage Monitoring (stay within API quota)
- [ ] Billing Automation (monthly invoicing)
- [ ] Escalation Process (critical issues, urgent support)
- [ ] Renewal Negotiation (6-month advance planning)

---

## 🏢 Enterprise Feature Map (What They Actually Use)

### Feature 1: Candidate Search API
**What it does**: Search 500K+ candidates in <2 seconds  
**API Endpoint**: `POST /api/v1/candidates/search`  
**Usage**: 100-500 searches/day per recruiter  
**ROI**: 24x faster than manual LinkedIn search

### Feature 2: Batch Scoring API
**What it does**: Score 10,000 candidates against a job description  
**API Endpoint**: `POST /api/v1/candidates/score-batch`  
**Usage**: 10-50 batch operations/month  
**ROI**: Automatically ranks candidates by fit (20-50% better hires)

### Feature 3: Analytics Dashboard
**What it does**: Real-time recruiting metrics and talent pool insights  
**API Endpoint**: `GET /api/v1/analytics/talent-pool`  
**Usage**: 2-5 queries/day (recruiting managers)  
**ROI**: Data-driven hiring decisions (reduces bad hires by 30%)

### Feature 4: Webhooks Integration
**What it does**: Send events to their ATS in real-time  
**API Endpoint**: `POST /api/v1/webhooks/subscribe`  
**Usage**: 1,000-10,000 events/day  
**ROI**: Automated candidate flow (no manual data entry = 10 hrs saved/week)

### Feature 5: Enterprise Reporting
**What it does**: Monthly recruiting ROI reports  
**API Endpoint**: `GET /api/v1/reports/{customer_id}/monthly`  
**Usage**: 1 report/month  
**ROI**: Justify budget spend to executive leadership

---

## 🎤 Common Enterprise Questions (Answers)

**Q: Can you integrate with our ATS (Applicant Tracking System)?**
> A: Yes! We support Workday, Greenhouse, Lever, BambooHR, and 20+ other ATS platforms via REST API and webhooks. Custom integration takes 1-2 weeks.

**Q: How secure is our candidate data?**
> A: Enterprise-grade security with AES-256 encryption at rest, TLS 1.2+ in transit, ISO 27001 certified, regular penetration testing, and encrypted daily backups.

**Q: What if we need to terminate the contract?**
> A: 60-day cancellation notice, we provide full data export in CSV format within 48 hours. No lock-in.

**Q: How many concurrent users can the system support?**
> A: 10,000+ simultaneous users. We auto-scale from 2 to 20 instances based on load. Designed for Fortune 500 scale.

**Q: What's your uptime SLA?**
> A: Professional tier: 99.95% (max 22 hours downtime/year). Enterprise tier: 99.99% (max 52 minutes downtime/year). Monitored 24/7 with instant alerts.

**Q: Can we use this for other hiring besides technical roles?**
> A: Yes! The system works for ANY role: sales, marketing, operations, finance. Skills, location, experience matching applies across all industries.

**Q: What if we outgrow your system?**
> A: Unlikely - we support unlimited API calls and 100K+ concurrent users. But if you do, we have enterprise support team ready to optimize architecture.

**Q: How long is the contract?**
> A: Standard 12-month annual contract with automatic renewal. 3-year discount available (15% off). 60-day termination clause.

---

## 📈 Revenue Flow (Simple Version)

```
Enterprise Signs $150K/year Contract
                    ↓
         We invoice them $12,500/month
                    ↓
    We pay for infrastructure: $2,000/month
         (Other costs: support, monitoring, etc)
                    ↓
    GROSS PROFIT: $10,500/month per customer
                    ↓
     By Month 6 with 10 customers:
     $10,500 × 10 = $105K/month recurring revenue
                    ↓
     By Year 2 with 25 customers:
     $10,500 × 25 = $262.5K/month ($3.15M ARR)
```

---

## 🚨 Critical Enterprise Commitments

### You Must Have These In Place Before Selling

- [ ] **Uptime SLA**: 99.95% monitored 24/7, alerts to Slack
- [ ] **Data Backup**: Automated hourly backups, tested recovery monthly
- [ ] **Security Audit**: Third-party penetration test completed
- [ ] **Support Response**: <1 hour response time, 24/7 coverage
- [ ] **Data Export**: Customer can export all data within 48 hours
- [ ] **Compliance**: GDPR, CCPA, SOC 2 Type II ready
- [ ] **Roadmap**: Quarterly feature roadmap shared with customers

---

## 🎯 Sales Conversation Framework

### Discovery Call (15 minutes)
- "How many people do you recruit per year?" (Answer: 100-500)
- "How long does your average hire take?" (Answer: 30-60 days)
- "What's your recruiting team size?" (Answer: 5-50 recruiters)

### Value Prop (5 minutes)
- "We reduce your hire time from 30 days to 14 days"
- "You save $300-500 per hire (40% cost reduction)"
- "With 200 hires/year, that's $60-100K annual savings"
- "ROI: Your $150K contract investment pays for itself in 2-3 months"

### Demo (10 minutes)
- Search for "Senior Engineer in San Francisco"
- Show 50 ranked results in 2 seconds
- Show API documentation
- Show analytics dashboard
- "This is what your recruiting team will use daily"

### Close (5 minutes)
- "Can we do a 30-day pilot to prove ROI?"
- If yes: "Great! Pilot is $0 cost. Let's get started."
- If no: "What would change your mind?"

---

## 📊 Monthly Check-in Template (For Customer Success)

**Customer Name**: ACME Corp  
**Account Manager**: You  
**Month**: November 2025

```
METRICS THIS MONTH
├─ API Calls: 45,234 / 100,000 quota (45% used) ✅
├─ Candidates Found: 1,250
├─ Interviews Scheduled: 145  
├─ Offers Made: 28
├─ Hires Completed: 12
└─ Recruiting Team Efficiency: +40% vs baseline ✅

CALCULATED ROI
├─ Cost per hire (traditional): $30,000
├─ Cost per hire (with us): $12,000  
├─ Savings per hire: $18,000
├─ Hires this month: 12
├─ Total savings this month: $216,000
├─ Contract cost this month: $12,500
└─ Net ROI this month: $203,500 ✅

ISSUES/BLOCKERS
├─ ATS integration taking longer than expected
├─ Slack webhook not delivering all events
└─ Training for 20 new recruiters needed

ACTION ITEMS
├─ [ ] Fix Slack webhook issue (next 24 hours)
├─ [ ] Schedule additional training (this week)
└─ [ ] Follow up on ATS integration timeline

RENEWAL CONVERSATION START
├─ "We're seeing great ROI. Can we expand?"
├─ "Would you like to add analytics + white-label?"
├─ "Could we discuss Enterprise tier upgrade?"
```

---

## 🎓 Training Deck Topics (For Customer Team)

1. **Overview** (15 min)
   - Career OS platform overview
   - What the API does
   - Security and compliance

2. **Candidate Search** (20 min)
   - How to search candidates
   - Understanding match scores
   - Filtering and sorting
   - Exporting results

3. **Analytics Dashboard** (15 min)
   - Viewing your recruiting metrics
   - Understanding talent pool insights
   - Running custom reports
   - Exporting data

4. **API Integration** (20 min)
   - API authentication (API keys)
   - Rate limiting and quotas
   - Webhook setup and testing
   - Error handling

5. **Support & Escalation** (10 min)
   - Getting help (Slack, email, phone)
   - Reporting bugs
   - Feature requests
   - Emergency contacts

**Total Training Time**: 90 minutes  
**Format**: Video + live Q&A  
**Certification**: After completing quiz

---

## 🏁 Success Criteria for Enterprise Deployment

**Week 1-2**: Technical go-live complete
- [ ] Production system live and stable
- [ ] Monitoring shows 99.95%+ uptime
- [ ] First 3 enterprises can access production

**Month 1**: Business momentum building
- [ ] 5+ enterprise pilots launched
- [ ] 50K+ B2C users on platform
- [ ] $20-30K/month recurring revenue

**Month 3**: Market validation
- [ ] 10+ enterprise customers signed
- [ ] Customer satisfaction (NPS >40)
- [ ] $100K+/month revenue run-rate

**Month 6**: Scale phase
- [ ] 15+ enterprise customers
- [ ] 500K+ B2C users
- [ ] $300K+/month revenue run-rate

**Year 1**: Established market leader
- [ ] 25+ enterprise customers
- [ ] 1M+ B2C users  
- [ ] $1-2M revenue (established)

---

## ✅ Your Enterprise Go-To-Market Checklist

### Before Launch (Next Week)
- [ ] Pricing page created
- [ ] Sales one-pager written
- [ ] 2-3 case studies drafted
- [ ] Demo recording prepared
- [ ] Contract template reviewed by lawyer

### At Launch
- [ ] Email sent to prospects
- [ ] Press release published
- [ ] Product Hunt post
- [ ] Twitter/LinkedIn announcement
- [ ] Customer success team ready

### First Month  
- [ ] 5+ demo calls scheduled
- [ ] 2-3 pilots started
- [ ] First revenue transactions processed
- [ ] Customer feedback collected
- [ ] Product improvements prioritized

---

**This is your enterprise operations playbook. Use it for every customer conversation, sales call, and support interaction.**

**Print this and keep it handy! 📋**
