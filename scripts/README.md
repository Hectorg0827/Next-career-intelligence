# Firebase User Management Scripts

These scripts automatically create and manage test users in Firebase Authentication.

## 📋 Prerequisites

1. **Firebase Admin SDK Service Account Key**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select your project: `next-fc055`
   - Navigate to **Project Settings** > **Service Accounts**
   - Click **"Generate New Private Key"**
   - Download the JSON file
   - Save it as `firebase-service-account.json` in this `scripts/` directory

2. **Node.js and npm** (already installed)

## 🚀 Setup

```bash
# Navigate to scripts directory
cd scripts

# Install dependencies
npm install
```

## 📝 Usage

### Create All 50 Test Users

```bash
npm run create-users
```

This will:
- ✅ Create all 50 test users in Firebase Auth
- ✅ Set custom claims for subscription tiers (elite, pro, basic, free)
- ✅ Auto-verify emails for testing
- ✅ Handle duplicates gracefully (updates existing users)

### Delete All Test Users

```bash
npm run delete-users
```

This will:
- 🗑️ Remove all 50 test users from Firebase Auth
- ⚠️ Cannot be undone! Use with caution

### Manual Execution

```bash
# Create users
node create-firebase-users.js

# Delete users
node delete-firebase-users.js
```

## 🔑 Test Credentials

After running the creation script, you can log in with:

### Elite Tier (9 Agents)
```
Email: elite.sarah.chen@careeriq.com
Password: EliteTest123!
```

### Pro Tier (7 Agents)
```
Email: pro.alex.kim@careeriq.com
Password: ProTest123!
```

### Basic Tier (5 Agents)
```
Email: basic.noah.jackson@careeriq.com
Password: BasicTest123!
```

### Free Tier (3 Agents)
```
Email: free.olivia.smith@careeriq.com
Password: FreeTest123!
```

## 📊 Features

- **Batch Processing**: Creates users in batches of 10 to avoid rate limiting
- **Duplicate Handling**: Updates existing users instead of failing
- **Custom Claims**: Sets `subscriptionTier` and `role` claims for each user
- **Progress Tracking**: Shows detailed progress for each user
- **Summary Report**: Provides complete statistics at the end

## 🔒 Security Notes

⚠️ **IMPORTANT**: 
- Never commit `firebase-service-account.json` to git
- Keep your service account key secure
- Add `firebase-service-account.json` to `.gitignore`

## 🐛 Troubleshooting

### Error: "Firebase service account key not found"
Make sure you've downloaded the service account key and placed it in the `scripts/` directory as `firebase-service-account.json`.

### Error: "auth/email-already-exists"
The script handles this automatically by updating the existing user's custom claims.

### Rate Limiting
The script includes delays between batches. If you still hit rate limits, increase the delay in the code.

## 📚 Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firebase Auth User Management](https://firebase.google.com/docs/auth/admin/manage-users)
- [Custom Claims Documentation](https://firebase.google.com/docs/auth/admin/custom-claims)
