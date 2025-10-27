/**
 * Firebase User Deletion Script
 * Deletes all test users from Firebase Authentication
 * 
 * Usage: node scripts/delete-firebase-users.js
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Firebase Admin SDK Configuration
const serviceAccountPath = process.env.FIREBASE_SERVICE_ACCOUNT_KEY || './firebase-service-account.json';

// Check if service account exists
if (!fs.existsSync(serviceAccountPath)) {
  console.error('❌ Error: Firebase service account key not found!');
  console.error(`Expected location: ${serviceAccountPath}`);
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

// Get all emails
const allEmails = [
  ...testUsers.elite_tier_accounts.map(u => u.email),
  ...testUsers.pro_tier_accounts.map(u => u.email),
  ...testUsers.basic_tier_accounts.map(u => u.email),
  ...testUsers.free_tier_accounts.map(u => u.email)
];

console.log(`\n🗑️  Starting deletion of ${allEmails.length} test users...\n`);

// Function to delete a user by email
async function deleteUser(email) {
  try {
    const userRecord = await admin.auth().getUserByEmail(email);
    await admin.auth().deleteUser(userRecord.uid);
    console.log(`✅ Deleted: ${email}`);
    return { success: true, email };
  } catch (error) {
    if (error.code === 'auth/user-not-found') {
      console.log(`⚠️  Not found: ${email}`);
      return { success: true, email, notFound: true };
    } else {
      console.error(`❌ Failed: ${email} - ${error.message}`);
      return { success: false, email, error: error.message };
    }
  }
}

// Main execution
(async () => {
  try {
    const results = {
      deleted: [],
      notFound: [],
      failed: [],
      total: allEmails.length
    };

    // Delete in batches
    for (let i = 0; i < allEmails.length; i += 10) {
      const batch = allEmails.slice(i, i + 10);
      console.log(`\n📦 Processing batch ${Math.floor(i / 10) + 1}/${Math.ceil(allEmails.length / 10)}...`);
      
      const batchResults = await Promise.all(batch.map(deleteUser));
      
      batchResults.forEach(result => {
        if (result.success) {
          if (result.notFound) {
            results.notFound.push(result);
          } else {
            results.deleted.push(result);
          }
        } else {
          results.failed.push(result);
        }
      });

      // Wait between batches
      if (i + 10 < allEmails.length) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    console.log('\n' + '═'.repeat(70));
    console.log('📊 FIREBASE USER DELETION SUMMARY');
    console.log('═'.repeat(70));
    console.log(`✅ Successfully deleted: ${results.deleted.length} users`);
    console.log(`⚠️  Not found:           ${results.notFound.length} users`);
    console.log(`❌ Failed:              ${results.failed.length} users`);
    console.log(`📦 Total processed:     ${results.total} users`);
    console.log('═'.repeat(70));

    if (results.failed.length > 0) {
      console.log('\n❌ Failed deletions:');
      results.failed.forEach(f => {
        console.log(`   - ${f.email}: ${f.error}`);
      });
    }

    console.log('\n🎉 Done!\n');
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  }
})();
