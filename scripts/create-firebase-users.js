/**
 * Firebase User Creation Script
 * Creates all 50 test users in Firebase Authentication
 * 
 * Usage: node scripts/create-firebase-users.js
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Firebase Admin SDK Configuration
// You need to download your service account key from Firebase Console:
// Project Settings > Service Accounts > Generate New Private Key
const serviceAccountPath = process.env.FIREBASE_SERVICE_ACCOUNT_KEY || './firebase-service-account.json';

// Check if service account exists
if (!fs.existsSync(serviceAccountPath)) {
  console.error('❌ Error: Firebase service account key not found!');
  console.error(`Expected location: ${serviceAccountPath}`);
  console.error('\n📝 To get your service account key:');
  console.error('1. Go to Firebase Console: https://console.firebase.google.com/');
  console.error('2. Select your project');
  console.error('3. Go to Project Settings > Service Accounts');
  console.error('4. Click "Generate New Private Key"');
  console.error('5. Save the file as firebase-service-account.json in the scripts directory');
  process.exit(1);
}

// Initialize Firebase Admin
const serviceAccount = require(serviceAccountPath);
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// Load test users from JSON
const testUsersPath = path.join(__dirname, '../TEST_USERS_CREDENTIALS.json');
const testUsers = JSON.parse(fs.readFileSync(testUsersPath, 'utf8'));

// Flatten all users into single array
const allUsers = [
  ...testUsers.elite_tier_accounts.map(u => ({ ...u, tier: 'elite' })),
  ...testUsers.pro_tier_accounts.map(u => ({ ...u, tier: 'pro' })),
  ...testUsers.basic_tier_accounts.map(u => ({ ...u, tier: 'basic' })),
  ...testUsers.free_tier_accounts.map(u => ({ ...u, tier: 'free' }))
];

console.log(`\n🚀 Starting Firebase user creation for ${allUsers.length} users...\n`);

// Function to create a single user
async function createUser(userData) {
  try {
    const userRecord = await admin.auth().createUser({
      email: userData.email,
      password: userData.password,
      displayName: userData.name,
      emailVerified: true // Auto-verify for testing
    });

    // Set custom claims for subscription tier
    await admin.auth().setCustomUserClaims(userRecord.uid, {
      subscriptionTier: userData.tier,
      role: userData.role || 'user'
    });

    console.log(`✅ Created: ${userData.email} (${userData.tier.toUpperCase()})`);
    return { success: true, email: userData.email, uid: userRecord.uid };
  } catch (error) {
    if (error.code === 'auth/email-already-exists') {
      console.log(`⚠️  Exists: ${userData.email} (already in Firebase)`);
      
      // Update existing user's custom claims
      try {
        const existingUser = await admin.auth().getUserByEmail(userData.email);
        await admin.auth().setCustomUserClaims(existingUser.uid, {
          subscriptionTier: userData.tier,
          role: userData.role || 'user'
        });
        console.log(`   ↳ Updated claims for ${userData.email}`);
        return { success: true, email: userData.email, uid: existingUser.uid, updated: true };
      } catch (updateError) {
        console.error(`   ↳ Failed to update claims: ${updateError.message}`);
        return { success: false, email: userData.email, error: updateError.message };
      }
    } else {
      console.error(`❌ Failed: ${userData.email} - ${error.message}`);
      return { success: false, email: userData.email, error: error.message };
    }
  }
}

// Function to create users in batches to avoid rate limiting
async function createUsersInBatches(users, batchSize = 10) {
  const results = {
    created: [],
    updated: [],
    failed: [],
    total: users.length
  };

  for (let i = 0; i < users.length; i += batchSize) {
    const batch = users.slice(i, i + batchSize);
    console.log(`\n📦 Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(users.length / batchSize)}...`);
    
    const batchResults = await Promise.all(batch.map(createUser));
    
    batchResults.forEach(result => {
      if (result.success) {
        if (result.updated) {
          results.updated.push(result);
        } else {
          results.created.push(result);
        }
      } else {
        results.failed.push(result);
      }
    });

    // Wait a bit between batches to avoid rate limiting
    if (i + batchSize < users.length) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  return results;
}

// Main execution
(async () => {
  try {
    const results = await createUsersInBatches(allUsers);

    console.log('\n' + '═'.repeat(70));
    console.log('📊 FIREBASE USER CREATION SUMMARY');
    console.log('═'.repeat(70));
    console.log(`✅ Successfully created: ${results.created.length} users`);
    console.log(`🔄 Updated existing:    ${results.updated.length} users`);
    console.log(`❌ Failed:              ${results.failed.length} users`);
    console.log(`📦 Total processed:     ${results.total} users`);
    console.log('═'.repeat(70));

    if (results.failed.length > 0) {
      console.log('\n❌ Failed users:');
      results.failed.forEach(f => {
        console.log(`   - ${f.email}: ${f.error}`);
      });
    }

    console.log('\n✨ Key test credentials:');
    console.log('   🏆 ELITE: elite.sarah.chen@careeriq.com / EliteTest123!');
    console.log('   💎 PRO:   pro.alex.kim@careeriq.com / ProTest123!');
    console.log('   ⭐ BASIC: basic.noah.jackson@careeriq.com / BasicTest123!');
    console.log('   🆓 FREE:  free.olivia.smith@careeriq.com / FreeTest123!');

    console.log('\n🎉 Done! You can now log in with any of these accounts.\n');

    process.exit(0);
  } catch (error) {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  }
})();
