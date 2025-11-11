# Customer Support System Setup Guide

## Overview

Complete guide to setting up production-ready customer support with:
- Live chat widget (Intercom recommended)
- Knowledge base (self-service help center)
- Ticket management and routing
- SLA targets and performance metrics
- Support team training materials

---

## Part 1: Support Platform Selection

### Option A: Intercom (Recommended)

**Pros**:
- Modern, user-friendly interface
- Excellent live chat with chatbots
- Product tours and onboarding
- Email campaigns integrated
- Mobile app for support team

**Cons**:
- Expensive ($74/seat/month)
- Less customizable than Zendesk

**Best for**: B2C SaaS, modern tech companies

### Option B: Zendesk

**Pros**:
- Industry standard
- Highly customizable
- Powerful ticketing system
- Better for large teams (50+ agents)
- Cheaper at scale ($55/seat/month Pro)

**Cons**:
- Older interface
- Steeper learning curve
- Chat costs extra ($14/agent/month)

**Best for**: Enterprise, large support teams

### Option C: Freshdesk (Budget Option)

**Pros**:
- Very affordable ($15-$49/agent/month)
- Good feature set
- Built-in gamification

**Cons**:
- Less polished than Intercom/Zendesk
- Smaller ecosystem

**Best for**: Startups, bootstrapped companies

### Recommendation

**Start**: Intercom (2 agents, $148/month)
- Covers chat, email, knowledge base
- Modern UI your users expect
- Easy to set up (< 1 day)

**Scale** (10+ agents): Migrate to Zendesk
- Better economics at scale
- More powerful workflow automation

---

## Part 2: Intercom Setup

### 2.1 Account Creation

1. **Sign up**: https://www.intercom.com/signup
2. **Plan**: Start ($74/seat/month, billed annually)
   - 2 seats minimum = $148/month
   - Includes: Live chat, email, help center, mobile SDK
3. **Workspace name**: `NEXT Career Intelligence`

### 2.2 Install Intercom Messenger

#### Frontend Integration (Next.js)

**Install Intercom package**:

```bash
cd frontend
npm install react-use-intercom
```

**Create Intercom provider** (`frontend/src/components/IntercomProvider.tsx`):

```typescript
'use client'

import { IntercomProvider as Provider } from 'react-use-intercom'
import { useAuth } from '@/contexts/AuthContext'

export function IntercomProvider({ children }: { children: React.ReactNode }) {
  const INTERCOM_APP_ID = process.env.NEXT_PUBLIC_INTERCOM_APP_ID || ''

  return (
    <Provider appId={INTERCOM_APP_ID} autoBoot>
      {children}
    </Provider>
  )
}
```

**Add to layout** (`frontend/src/app/layout.tsx`):

```typescript
import { IntercomProvider } from '@/components/IntercomProvider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <IntercomProvider>
          <AuthProvider>
            <Navigation />
            {children}
          </AuthProvider>
        </IntercomProvider>
      </body>
    </html>
  )
}
```

**Create support button** (`frontend/src/components/SupportButton.tsx`):

```typescript
'use client'

import { useIntercom } from 'react-use-intercom'
import { useAuth } from '@/contexts/AuthContext'

export function SupportButton() {
  const { show, update } = useIntercom()
  const { user } = useAuth()

  const handleClick = () => {
    // Update user context
    if (user) {
      update({
        userId: user.id,
        email: user.email,
        name: user.name,
        customAttributes: {
          plan: user.subscription_tier,
          signupDate: user.created_at,
        },
      })
    }

    // Show messenger
    show()
  }

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg hover:bg-blue-700 transition"
    >
      💬 Chat with us
    </button>
  )
}
```

**Environment variable**:

```bash
# frontend/.env.local
NEXT_PUBLIC_INTERCOM_APP_ID=your_intercom_app_id_here
```

### 2.3 Configure Messenger Settings

**Intercom Dashboard → Messenger Settings**:

**Appearance**:
- Color: `#667eea` (brand purple)
- Position: Bottom right
- Messenger greeting: "Hi! 👋 How can we help you today?"

**Behavior**:
- ✅ Show for logged-in users
- ✅ Show for visitors (limited - only help center)
- ✅ Show unread message count
- ❌ Show on mobile (optional - use native app)

**Expected reply time**: "We typically reply within 4 hours"

### 2.4 Set Up Team

**Settings → Teammates**:

1. **Add support agents**:
   - support@nextcareer.ai (Admin role)
   - agent1@nextcareer.ai (Agent role)

2. **Define roles**:
   - **Admin**: Full access, settings, reports
   - **Agent**: Reply to messages, view conversations
   - **Viewer**: Read-only access (for product managers)

3. **Set availability**:
   - Monday-Friday: 9 AM - 6 PM PST
   - Weekends: 10 AM - 4 PM PST (optional)
   - Holidays: Closed (auto-responder)

### 2.5 Configure Routing Rules

**Settings → Inbox → Assignment Rules**:

```
Rule 1: Premium Support (Elite users)
IF: User plan = "Elite"
THEN: Assign to → Elite Support Team
Priority: High
Response SLA: 1 hour

Rule 2: Billing Issues
IF: Message contains "payment", "billing", "charge", "refund"
THEN: Assign to → Billing Team
Priority: High

Rule 3: Technical Issues
IF: Message contains "error", "bug", "broken", "not working"
THEN: Assign to → Engineering Team
Priority: Medium

Rule 4: General Support
ELSE: Assign to → General Support Team
Priority: Normal
Response SLA: 4 hours
```

### 2.6 Create Auto-Responders

**Settings → Automations → New Bot**:

**Bot 1: Office Hours Auto-Reply**

```
Trigger: New conversation
Condition: Outside office hours (6 PM - 9 AM PST)
Action: Send message
Message:
  "Thanks for reaching out! 🌙

  Our team is currently offline but we'll respond first thing in the morning (usually within 1 hour of opening at 9 AM PST).

  In the meantime, check out our Help Center for instant answers: [Link]

  Urgent billing issue? Email: billing@nextcareer.ai"
```

**Bot 2: Common Questions Router**

```
Trigger: First message contains keywords
Condition: Message contains "password", "reset", "login"
Action: Show help article + Ask if resolved

Message:
  "It looks like you're having trouble logging in. Here's our guide: [Password Reset Article]

  Did this solve your issue?
  [Yes, thanks!] [No, I need more help]"
```

---

## Part 3: Knowledge Base (Help Center)

### 3.1 Create Help Center

**Intercom → Help Center → Create**:

- URL: `help.nextcareer.ai` (custom domain)
- Or: `nextcareer.intercom.help` (Intercom subdomain)

**Customize branding**:
- Logo: Upload NEXT logo
- Colors: Match brand (`#667eea`)
- Favicon: Upload favicon.ico

### 3.2 Help Center Structure

Create **8 Collections** (categories):

#### Collection 1: Getting Started

**Articles**:
1. How to create an account
2. Completing your profile
3. Uploading your first resume
4. Understanding your Career Health Score
5. Navigating the dashboard

#### Collection 2: Resume Studio

**Articles**:
1. How resume tailoring works
2. Understanding AI suggestions
3. Accepting or rejecting bullet points
4. Downloading your tailored resume
5. Resume best practices and tips
6. Troubleshooting: "Resume not uploading"

#### Collection 3: Job Search & Applications

**Articles**:
1. How job matching works
2. Saving jobs for later
3. Tracking your applications
4. Understanding compatibility scores
5. Setting job alerts
6. Troubleshooting: "No jobs showing"

#### Collection 4: AI Career Coach

**Articles**:
1. Asking career questions effectively
2. Getting salary negotiation advice
3. Career transition guidance
4. Setting and tracking career goals
5. Coach conversation history

#### Collection 5: Interviewer AI

**Articles**:
1. Scheduling a mock interview
2. Types of interviews available (behavioral, technical, case)
3. Understanding interview feedback scores
4. Improving your interview skills
5. Troubleshooting: Audio/video issues

#### Collection 6: Billing & Subscriptions

**Articles**:
1. Subscription plans explained (Free, Pro, Elite)
2. How to upgrade or downgrade
3. Payment methods and changing cards
4. Canceling your subscription
5. Refund policy and requesting refunds
6. Understanding charges on your statement
7. Troubleshooting: "Payment declined"

#### Collection 7: Account & Security

**Articles**:
1. Changing your password
2. Enabling two-factor authentication (2FA)
3. Privacy settings and data control
4. Exporting your data (GDPR)
5. Deleting your account permanently
6. Troubleshooting: "Can't log in"

#### Collection 8: Technical Issues

**Articles**:
1. Supported browsers and devices
2. Clearing cache and cookies
3. Enabling JavaScript
4. Common error messages explained
5. Reporting a bug
6. Feature requests

### 3.3 Article Template

Use consistent structure for all articles:

```markdown
# [Article Title]

**Last updated**: November 2025
**Estimated reading time**: 3 minutes

## Overview

[Brief 2-3 sentence summary of what this article covers]

## Step-by-Step Guide

### Step 1: [Action]
[Detailed instructions with screenshots]

### Step 2: [Action]
[Detailed instructions with screenshots]

### Step 3: [Action]
[Detailed instructions with screenshots]

## Troubleshooting

**Issue**: [Common problem]
**Solution**: [How to fix]

## Still need help?

If you're still having trouble, please [contact support](mailto:support@nextcareer.ai) or use the chat widget below.

**Related articles**:
- [Link to related article 1]
- [Link to related article 2]
```

### 3.4 Add Search Functionality

Intercom's help center includes built-in search:

- Powered by Elasticsearch
- Auto-suggests articles as user types
- Tracks search terms (see what users can't find)

**Optimize search**:
- Add keywords to articles (SEO meta tags)
- Use synonyms (e.g., "cancel" = "unsubscribe")
- Review "no results" searches monthly (add missing articles)

---

## Part 4: SLA Targets & Performance Metrics

### Service Level Agreements (SLAs)

Set response time targets by user tier:

```
Free Users:
- First response: < 24 hours
- Resolution: < 72 hours

Pro Users:
- First response: < 4 hours
- Resolution: < 24 hours

Elite Users:
- First response: < 1 hour
- Resolution: < 8 hours
- Priority queue (jump ahead)
```

### Key Metrics to Track

**Response Metrics**:
- First response time (FRT)
- Average response time
- Resolution time

**Quality Metrics**:
- Customer Satisfaction Score (CSAT): Target > 90%
- Net Promoter Score (NPS): Target > 50
- Conversation rating: Target > 4.5/5

**Volume Metrics**:
- Conversations per day
- Self-service rate (% resolved via help center)
- Chat-to-ticket ratio

**Agent Metrics** (don't overemphasize - focus on quality):
- Conversations handled per agent
- Average handle time
- First contact resolution rate

### Intercom Reports

**Dashboard → Reports**:

1. **Conversation Volume Report**: Track daily/weekly trends
2. **Team Performance**: Compare agent response times
3. **Customer Satisfaction**: CSAT scores by conversation
4. **Self-Service**: Help center article views, search terms

### Alert Rules

Set up alerts for SLA violations:

**Settings → Notifications**:
- ⚠️ Elite user waiting > 1 hour: Slack alert to #support-urgent
- ⚠️ Any user waiting > 24 hours: Email to support manager
- ⚠️ CSAT < 80%: Weekly digest to product team

---

## Part 5: Support Team Training

### 5.1 Support Playbook

Create internal wiki with:

**Common Scenarios**:
1. User can't log in (password reset)
2. Payment failed (update card)
3. Feature not working (bug report process)
4. Refund request (policy + approval flow)
5. Angry customer (de-escalation tactics)

**Response Templates**:

```
Template: Password Reset
---
Hi {name}!

I can help you reset your password. Click this link:
{password_reset_link}

The link is valid for 1 hour. If it expires, you can request a new one from the login page.

Let me know if you have any other questions!

Best,
{agent_name}
```

```
Template: Refund Request (Approved)
---
Hi {name},

I've processed your refund request for ${amount}. You should see the credit back on your card within 5-7 business days.

Your subscription has been canceled effective immediately. You can reactivate anytime from your billing settings.

Is there anything else I can help with today?

Best,
{agent_name}
```

### 5.2 Escalation Path

Define when to escalate:

**Tier 1 (Support Agent)**:
- Handles: Account issues, how-to questions, basic troubleshooting
- Escalate to Tier 2 if: Technical bug, feature request, billing dispute > $100

**Tier 2 (Senior Agent / Product)**:
- Handles: Complex technical issues, product feedback, escalated complaints
- Escalate to Engineering if: Confirmed bug, data issue, security concern

**Tier 3 (Engineering)**:
- Handles: Production bugs, database issues, API errors
- Escalate to CTO if: Security incident, data breach, system outage

### 5.3 Tone and Voice Guidelines

**NEXT Support Voice**:
- Friendly but professional
- Empathetic and patient
- Clear and concise (avoid jargon)
- Proactive (anticipate next question)

**Examples**:

❌ **Bad**:
"The system is experiencing latency issues due to elevated traffic on the backend infrastructure."

✅ **Good**:
"Our servers are running a bit slow right now due to high traffic. We're working on it and everything should be back to normal in about 20 minutes. Sorry for the inconvenience!"

❌ **Bad**:
"That's not how the product works."

✅ **Good**:
"I can see how that would be confusing! Let me explain how it actually works..."

---

## Part 6: Integration with Backend

### 6.1 Create Support Ticket from Backend

Sometimes you need to create tickets programmatically (e.g., payment failures):

```python
import httpx
from app.core.config import settings

async def create_support_ticket(
    user_email: str,
    subject: str,
    message: str,
    priority: str = "normal"  # normal, high, urgent
):
    """
    Create Intercom ticket from backend

    Use cases:
    - Payment failed: Alert billing team
    - Account locked: Security alert
    - Data export requested: GDPR compliance
    """
    url = "https://api.intercom.io/conversations"
    headers = {
        "Authorization": f"Bearer {settings.INTERCOM_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "from": {
            "type": "user",
            "email": user_email
        },
        "body": f"**{subject}**\n\n{message}",
        "priority": priority
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
```

### 6.2 User Context API

Send user data to Intercom for better support:

```python
import httpx

async def update_intercom_user(user_id: str, user_data: dict):
    """
    Update user attributes in Intercom

    Provides context to support agents:
    - Subscription plan
    - Last activity date
    - Total resumes created
    - Account age
    """
    url = f"https://api.intercom.io/users"
    headers = {
        "Authorization": f"Bearer {settings.INTERCOM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "email": user_data["email"],
        "name": user_data["name"],
        "custom_attributes": {
            "plan": user_data["subscription_tier"],
            "signup_date": user_data["created_at"],
            "last_seen": user_data["last_activity"],
            "resumes_created": user_data["resumes_count"],
            "interviews_completed": user_data["interviews_count"],
            "career_health_score": user_data["career_health_score"]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()

# Call on user login/activity
await update_intercom_user(user.id, user.dict())
```

---

## Part 7: Cost Breakdown

### Intercom Pricing

**Start Plan** ($74/seat/month, billed annually):
- 2 seats minimum: $148/month = $1,776/year
- Includes: Chat, email, help center, mobile SDK
- Resolution Bot: +$99/month (optional)

**Grow Plan** ($395/month for up to 5 seats):
- Custom bots
- Product tours
- A/B testing

**Estimated Costs**:

```
Startup (2 agents): $148/month
Small Team (5 agents): $395/month (Grow plan)
Scale (10 agents): Switch to Zendesk (~$550/month)
```

### Zendesk Pricing (Alternative)

**Suite Team** ($55/agent/month):
- Ticketing, chat, call center, help center
- 10 agents: $550/month

**Zendesk cheaper at 8+ agents**

---

## Part 8: Migration Checklist

- [ ] Choose support platform (Intercom recommended)
- [ ] Sign up and configure workspace
- [ ] Install Intercom Messenger on frontend
- [ ] Set up team members (2 agents minimum)
- [ ] Configure routing rules (billing, technical, general)
- [ ] Create auto-responders (office hours, common questions)
- [ ] Build help center with 8 collections
- [ ] Write 40+ help articles (5 per collection)
- [ ] Add search functionality
- [ ] Set SLA targets by user tier
- [ ] Configure Intercom-backend integration (user context API)
- [ ] Train support team on playbook
- [ ] Define escalation path
- [ ] Set up metrics dashboard
- [ ] Configure alerts (SLA violations, CSAT drops)
- [ ] Test chat widget on staging environment
- [ ] Launch to production
- [ ] Monitor first week closely (CSAT, response times)

---

## Part 9: Ongoing Maintenance

### Weekly Tasks

- Review "no results" searches in help center (add missing articles)
- Check SLA compliance (response times)
- Review CSAT scores (investigate low ratings)

### Monthly Tasks

- Analyze conversation volume trends
- Update help articles (mark outdated content)
- Review agent performance (coaching if needed)
- Export Intercom data to data warehouse (analytics)

### Quarterly Tasks

- Survey customers (NPS, feature requests)
- Review support costs vs headcount
- Optimize routing rules based on data
- Update support playbook with new scenarios

---

## References

- [Intercom Documentation](https://www.intercom.com/help)
- [Zendesk Documentation](https://support.zendesk.com/)
- [Customer Support Best Practices](https://www.intercom.com/blog/customer-support-best-practices/)
- [SLA Benchmarks by Industry](https://www.zendesk.com/blog/customer-service-metrics/)
