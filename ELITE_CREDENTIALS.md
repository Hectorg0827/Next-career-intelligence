# 👑 Elite Admin Login Credentials

## Quick Access

**Elite Login URL:** https://www.nextci.net/auth/elite

### Credentials:
- **Username:** `elite_admin`
- **Password:** `NextElite2025!`

---

## What is Elite Access?

Elite access is a special admin account with **unlimited privileges** for testing and managing the NEXT Career Intelligence platform.

### Elite Privileges:
✅ **Unlimited career analyses** - No rate limits  
✅ **All AI features unlocked** - Full access to premium tools  
✅ **Admin dashboard** - Manage users and content  
✅ **Priority API access** - No throttling  
✅ **All subscription features** - Pro, Elite, everything  
✅ **Testing capabilities** - Full platform testing  

---

## How to Use Elite Login

### Option 1: Direct Login (Easiest)
1. Go to: https://www.nextci.net/auth/elite
2. Enter credentials:
   - Username: `elite_admin`
   - Password: `NextElite2025!`
3. Click "Elite Login"
4. You'll be redirected to the dashboard with full access

### Option 2: API Login (For Testing)
```bash
curl -X POST "https://next-backend-795538981829.us-central1.run.app/api/elite/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "elite_admin",
    "password": "NextElite2025!"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Elite login successful",
  "user_id": "...",
  "firebase_uid": "elite_...",
  "email": "elite@nextci.net",
  "role": "admin",
  "subscription_status": "elite"
}
```

---

## Elite Account Details

- **Email:** elite@nextci.net
- **Role:** admin
- **Subscription:** elite
- **Firebase UID:** elite_[auto-generated]
- **Created:** Automatically on first login
- **Status:** Permanent admin access

---

## Security Notes

⚠️ **Important:**
- This is a test/demo account for development and testing only
- The credentials are shown on the login page for easy access
- Do not use this in production without changing credentials
- Consider environment variables for production

### To Change Credentials:

Edit `backend/app/api/elite_auth.py`:
```python
ELITE_USERNAME = "your_custom_username"
ELITE_PASSWORD_HASH = hashlib.sha256("YourNewPassword!".encode()).hexdigest()
ELITE_EMAIL = "your_elite@email.com"
```

Then redeploy the backend.

---

## Testing Scenarios

### 1. Test Career Analysis
Login with elite credentials → Go to Dashboard → Run multiple analyses without limits

### 2. Test Premium Features
- AI Career Coach (unlimited conversations)
- Interview Simulator (unlimited practice)
- Resume Builder (unlimited resumes)
- Job Marketplace (full access)

### 3. Test Admin Functions
- View all users
- Manage subscriptions
- Access analytics
- Test system health

### 4. Test Different User Roles
Compare elite access vs regular user to see subscription restrictions

---

## Troubleshooting

### Cannot login?
1. Make sure backend is deployed with elite_auth module
2. Check that migration was run (user roles added to database)
3. Verify API URL is correct in frontend

### Error: "Invalid elite credentials"?
- Double-check username and password (case-sensitive)
- Username must be exactly: `elite_admin`
- Password must be exactly: `NextElite2025!`

### Elite features not working?
- Check elite status: GET `/api/elite/status?firebase_uid=elite_...`
- Should return: `is_elite: true`, `is_admin: true`, `role: "admin"`

---

## Regular User vs Elite User

| Feature | Free User | Pro User | Elite/Admin |
|---------|-----------|----------|-------------|
| Career Analyses | 3/month | Unlimited | Unlimited |
| AI Coach | Limited | Full Access | Full Access |
| Job Search | Basic | Advanced | Advanced + Admin |
| Resume Builder | 1 resume | 5 resumes | Unlimited |
| Interview Prep | Trial | Full Access | Full Access |
| Priority Support | ❌ | ✅ | ✅ |
| Admin Panel | ❌ | ❌ | ✅ |
| API Rate Limits | High | Medium | None |

---

## Quick Links

- **Elite Login:** https://www.nextci.net/auth/elite
- **Regular Login:** https://www.nextci.net/auth/login
- **Dashboard:** https://www.nextci.net/dashboard
- **Backend Health:** https://next-backend-795538981829.us-central1.run.app/api/health
- **API Docs:** https://next-backend-795538981829.us-central1.run.app/docs

---

## Support

Need help with elite access?
- Check logs: `gcloud logging read "resource.type=cloud_run_revision"`
- Test backend: `curl https://next-backend-795538981829.us-central1.run.app/api/health`
- Contact: Your email

---

**Remember:** Elite credentials are for testing only. Always use secure credentials in production! 🔒
