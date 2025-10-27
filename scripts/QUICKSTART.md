# Quick Start - Firebase User Creation

## Step 1: Download Service Account Key

1. Open: https://console.firebase.google.com/project/next-fc055/settings/serviceaccounts/adminsdk
2. Click **"Generate new private key"**
3. Click **"Generate key"** in the popup
4. Save the downloaded file as `firebase-service-account.json` in the `scripts/` directory

## Step 2: Run the Script

```bash
cd scripts
node create-firebase-users.js
```

## Step 3: Test Login

Go to http://localhost:3000/login and try:

```
Email: elite.sarah.chen@careeriq.com
Password: EliteTest123!
```

## That's it! 🎉

All 50 users will be created with proper subscription tiers and custom claims.

---

## Troubleshooting

### "Firebase service account key not found"
Make sure the file is named exactly: `firebase-service-account.json` and is in the `scripts/` directory.

### "Permission denied"
Make sure you have Owner or Editor permissions on the Firebase project.

### Want to delete all users?
```bash
node delete-firebase-users.js
```

---

## User Distribution

- **Elite**: 5 users (9-agent access)
- **Pro**: 10 users (7-agent access)  
- **Basic**: 10 users (5-agent access)
- **Free**: 25 users (3-agent access)
- **Total**: 50 users

All credentials are in `TEST_USERS_CREDENTIALS.json`
