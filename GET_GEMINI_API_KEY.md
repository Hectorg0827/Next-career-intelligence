# 🔑 How to Get Your Gemini API Key

## ❌ Current Problem

Your `.env` file has an **invalid Gemini API key**:
```
GEMINI_API_KEY=AIzaSy795538981829-0c05b330697k523h6aehtabvbik8d9oe
```

This appears to be a mix of OAuth Client ID and an API key prefix, which won't work.

## ✅ Solution: Get a Real Gemini API Key

### Step 1: Go to Google AI Studio
🔗 **Visit**: https://aistudio.google.com/app/apikey

### Step 2: Create API Key
1. Click **"Get API key"** or **"Create API key"**
2. Select your Google Cloud project: **`next-career-intelligence-795538981829`**
   - Or create a new project if needed
3. Click **"Create API key in existing project"**
4. **Copy the API key** - it will look like:
   ```
   AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   (39 characters, starts with `AIzaSy`)

### Step 3: Update Your .env File

Replace the current invalid key with your new key:

```bash
# Open .env file
nano /Users/hectorgarcia/Desktop/Next-career-intelligence/backend/.env
```

Update this line:
```properties
# OLD (INVALID):
GEMINI_API_KEY=AIzaSy795538981829-0c05b330697k523h6aehtabvbik8d9oe

# NEW (YOUR REAL KEY):
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Restart Backend

```bash
# Kill old backend
lsof -ti :8000 | xargs kill -9

# Restart with new key
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend
export $(cat .env | grep -v '^#' | xargs)
PYTHONPATH=/Users/hectorgarcia/Desktop/Next-career-intelligence/backend \
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### Step 5: Test It Works

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Data Entry Clerk",
    "skills": ["Typing", "Excel"],
    "location": "United States",
    "years_experience": 3
  }'
```

You should get real analysis results, not a 500 error!

## 🆓 Free Tier Limits

Google's Gemini API free tier includes:
- ✅ **15 requests per minute**
- ✅ **1,500 requests per day**
- ✅ **1 million tokens per month**

Perfect for development and testing! 🎉

## 🔒 Security Notes

- ✅ Never commit `.env` file to Git (already in `.gitignore`)
- ✅ Rotate API key if accidentally exposed
- ✅ Use different keys for dev vs production

---

## 📝 Quick Reference

**What you have now:**
- ❌ Invalid key: `AIzaSy795538981829-0c05b330697k523h6aehtabvbik8d9oe`
- ❌ Mix of OAuth Client ID + API key prefix

**What you need:**
- ✅ Valid Gemini API key from: https://aistudio.google.com/app/apikey
- ✅ Format: `AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (39 chars)

**Then:**
1. Update `.env`
2. Restart backend
3. Test with curl
4. Enjoy real AI analysis! 🚀
