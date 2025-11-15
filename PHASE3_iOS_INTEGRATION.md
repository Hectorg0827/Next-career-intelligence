# Phase 3: iOS Integration - Complete Technical Specification

## 🎯 Overview

Phase 3 adds a native iOS application to Career OS with **offline-first** architecture, real-time data synchronization, and push notifications. Users can access Career OS from any device while maintaining data consistency.

**Status**: Planning & Design  
**Target Completion**: 2-3 weeks  
**Team**: 1-2 iOS developers  

---

## 📋 Phase 3 Deliverables

### Core Features
1. **Offline-First Mobile App** - Full functionality without internet
2. **Real-Time Sync Engine** - Bidirectional data sync with conflict resolution
3. **Push Notifications** - Job alerts, guidance, achievement notifications
4. **Background Sync** - Automatic sync when online with exponential backoff
5. **Profile Management** - Edit, export, share profile on iOS
6. **Job Search** - Browse, save, apply to jobs offline
7. **AI Guidance** - Receive career guidance downloaded locally
8. **Career Health Dashboard** - View health score and trends locally

### Technical Stack
- **UI Framework**: SwiftUI (iOS 14+)
- **Local Storage**: Core Data (SQLite)
- **Networking**: URLSession + custom sync engine
- **Push Notifications**: APNs (Apple Push Notification service)
- **Analytics**: Firebase Analytics (optional)
- **Authentication**: Firebase Auth (continue from web)

### Target Users
- Career seekers on-the-go
- Users in low-connectivity areas
- Power users wanting instant mobile access

---

## 🏗️ Architecture Design

### System Components

```
┌─────────────────────────────────────────────────────────┐
│           iOS Career OS Application                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │          SwiftUI User Interface Layer            │   │
│  ├──────────────────────────────────────────────────┤   │
│  │ • Dashboard View  • Profile View  • Jobs View    │   │
│  │ • Goals View      • AI Coach      • Settings     │   │
│  └────────┬─────────────────────────────┬───────────┘   │
│           │                             │                │
│  ┌────────┴──────────────────────────┬─┴────────────┐   │
│  │      ViewModel / State Layer      │              │   │
│  │  @EnvironmentObject containers   │              │   │
│  └────────┬─────────────────────────┬───────────────┘   │
│           │                         │                    │
│  ┌────────┴──────────────┬──────────┴────────────────┐   │
│  │   Sync Manager        │    Local Data Store      │   │
│  ├──────────────────────┬┴─────────────────────────┤   │
│  │ • Conflict Resolver  │ Core Data Stack          │   │
│  │ • Queue Manager      │ • Entities               │   │
│  │ • Retry Logic        │ • Relationships          │   │
│  │ • Background Sync    │ • Indexing               │   │
│  └────────┬─────────────┴──────────┬────────────────┘   │
│           │                        │                     │
│  ┌────────┴────────────────────────┴──────────────────┐  │
│  │        Network Layer (URLSession)                  │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ • API Client  • Push Notification Handler         │  │
│  │ • Connectivity Monitoring  • Certificate Pinning  │  │
│  └────────┬───────────────────────────────────────────┘  │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │    APNs (Apple Push Notification Service)           │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────┬───────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Backend API     │
                    │  (localhost:8000)│
                    └──────────────────┘
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│              User Interaction (SwiftUI)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   ViewModel / State Mgmt   │ (optimistic updates)
        └────────────────────────────┘
                     │
        ┌────────────┴────────────────┐
        │                             │
        ▼                             ▼
    ┌────────────┐         ┌──────────────────┐
    │ Sync Queue │         │ Local Data Store │
    │ (pending)  │         │  (Core Data)     │
    └────────────┘         └──────────────────┘
        │                           │
        │                           │ (read for UI)
        │                           │
        └────────────┬─────────────┘
                     │
                     ▼ (when online)
        ┌─────────────────────────────┐
        │  Sync Engine                │
        │  • Conflict Detection       │
        │  • Merge Strategy           │
        │  • Retry with Backoff       │
        └─────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  Network Layer (URLSession) │
        │  • Request Signing          │
        │  • Response Handling        │
        └─────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  Backend API Server         │
        │  (localhost:8000/api/...)   │
        └─────────────────────────────┘
```

### Offline-First State Machine

```
┌─────────────────┐
│   Initialized   │
└────────┬────────┘
         │
         ▼
    ┌─────────────────────────────┐
    │  Check Network Connectivity │
    └─────────────────────────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
┌──────────────┐            ┌─────────────┐
│ Online       │            │  Offline    │
│ • Sync Queue │            │ • Cache     │
│ • Real-time  │            │ • Queue     │
│   Updates    │            │   Ops      │
└──────────────┘            └─────────────┘
    │                              │
    │                              │
    │◄─────┬──────────────────┬───►│
    │  Network Change Event  │
    │                        │
    │ • Reachability Monitor │
    └────────────────────────┘
```

---

## 🗄️ Core Data Model

### Entities & Relationships

```
Career Profile (Root)
├── Personal Info
│   ├── Name, Email, Phone
│   ├── Location, Website
│   └── Photo URL
├── Work History (1:N)
│   ├── Title, Company
│   ├── Dates, Description
│   └── Skills (synced from backend)
├── Education (1:N)
│   ├── Degree, School
│   └── Graduation Date
├── Skills (1:N)
│   ├── Name, Category
│   ├── Proficiency, Endorsements
│   └── Source
└── Certifications (1:N)
    ├── Name, Issuer
    ├── Date, Expiry
    └── Credential URL

Saved Jobs (1:N)
├── Job ID, Title, Company
├── Salary Range, Location
├── Remote Status
├── Description, Requirements
├── Saved Date
├── Applied (Boolean)
├── Application Date
└── Status (saved/applied/rejected)

AI Guidance Messages (1:N)
├── Message ID, Type
├── Priority, Content
├── Action Items (Array)
├── Created Date
├── Read Status
├── Dismissed Status
└── Sync Timestamp

User Events (1:N) - local event log
├── Event Type, Category
├── Event Data (JSON)
├── Created Date
├── Synced Status
└── Retry Count

Sync Queue (1:N)
├── Operation Type (CREATE/UPDATE/DELETE)
├── Entity Type, Entity ID
├── Payload (JSON)
├── Created Date
├── Retry Count
├── Last Retry Date
└── Status (pending/synced/failed)
```

### Core Data Schema (Swift)

```swift
// Profile Entity
@NSManaged var id: UUID
@NSManaged var userId: String
@NSManaged var firstName: String
@NSManaged var lastName: String
@NSManaged var email: String
@NSManaged var phone: String
@NSManaged var location: String
@NSManaged var bio: String
@NSManaged var workHistory: NSSet // -> WorkExperience
@NSManaged var education: NSSet // -> Education
@NSManaged var skills: NSSet // -> Skill
@NSManaged var savedJobs: NSSet // -> SavedJob
@NSManaged var localChanges: NSSet // -> SyncQueueItem
@NSManaged var lastSyncDate: Date
@NSManaged var version: Int // for conflict resolution

// Work Experience Entity
@NSManaged var id: UUID
@NSManaged var profile: Profile
@NSManaged var title: String
@NSManaged var company: String
@NSManaged var startDate: Date
@NSManaged var endDate: Date?
@NSManaged var isCurrent: Bool
@NSManaged var description: String
@NSManaged var localVersion: Int
@NSManaged var lastModified: Date

// Sync Queue Item
@NSManaged var id: UUID
@NSManaged var operationType: String // CREATE, UPDATE, DELETE
@NSManaged var entityType: String // Profile, WorkExperience, SavedJob, etc.
@NSManaged var entityId: UUID
@NSManaged var payload: Data // JSON encoded changes
@NSManaged var createdDate: Date
@NSManaged var retryCount: Int
@NSManaged var lastRetryDate: Date?
@NSManaged var status: String // pending, synced, failed
@NSManaged var error: String?
```

---

## 🔄 Real-Time Sync Engine

### Sync Architecture

```
┌──────────────────────────────────────────────────┐
│         SyncManager (Main Coordinator)            │
│  • Monitors network  • Triggers sync  • Logs     │
└──────────────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
    ▼             ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐
│  Upload │ │Download │ │Conflict│ │ Backoff  │
│ Manager │ │Manager  │ │Manager │ │ Manager  │
└─────────┘ └─────────┘ └────────┘ └──────────┘
```

### Upload Sync Process

```
1. User makes change in UI (edit profile, save job, etc.)
2. Optimistic update: immediately update Core Data
3. Add to SyncQueue with operation details
4. When online, SyncManager triggers upload:
   a. Get pending items from SyncQueue
   b. Batch or send individually (configurable)
   c. Send to backend API
   d. On success: mark as synced, update version
   e. On conflict: trigger conflict resolution
   f. On failure: increment retry count, schedule retry

Retry Strategy:
- Exponential backoff: 1s, 2s, 4s, 8s, 30s, 5min, 30min
- Max retries: 10 (configurable)
- Failed items stay in queue for manual review
```

### Download Sync Process (Pull Updates)

```
1. App connects to network
2. SyncManager checks for remote updates:
   a. Pull latest changes since lastSyncDate
   b. Check version numbers
   c. Merge changes into local store
   d. Update lastSyncDate
3. Periodically (every 5 min when online):
   a. Fetch AI guidance messages
   b. Fetch job recommendations
   c. Update health scores
4. On disconnect:
   a. Stop polling
   b. Cache last successful response
   c. Prepare to sync on reconnect
```

### Conflict Resolution Strategy

```
Conflict Detection:
- Version number mismatch detected
- Same field modified locally and remotely
- Different values after merge attempt

Resolution Priority (configurable):
1. Last-Write-Wins (LWW)
   - Remote version newer → use remote
   - Local version newer → keep local
   
2. Local-Preferred (for mobile)
   - Default for offline-first: keep user's changes
   - Report conflict in UI for review
   
3. Field-Level Merge
   - Merge field-by-field if possible
   - Example: name changed locally, email changed remotely
   - Keep both changes
   
4. Manual Resolution
   - Show conflict to user
   - Let them choose: local, remote, or manual merge

Example Scenario:
User A edits profile on web       User B edits profile on iOS
  └─ name: "John Doe"              └─ name: "John David Doe"
  └─ profile version: 5            └─ profile version: 5
  
On sync:
- Detect: both modified version 5
- Strategy: ask user if field-level merge possible
- Result: Keep mobile change (last edit), flag for review
```

### Background Sync (iOS Background Modes)

```
Background Processing Methods:

1. Background App Refresh (BGTask)
   - Requested by system every 15-30 minutes
   - Perform sync for 30 seconds
   - Perfect for light sync operations
   
2. Silent Push Notification
   - Server sends background notification
   - App wakes and performs sync
   - Limit: max 2-3 per hour (iOS throttling)
   
3. URLSession Background Transfer
   - For large uploads/downloads
   - Works even if app is terminated
   - System retries automatically

Implementation:
- Request BGProcessingTaskRequest for sync
- Set task ID: "com.careerOS.backgroundSync"
- System calls handleBGSync() when ready
- Sync critical data + check for new guidance
```

---

## 📱 User Interface Layers

### SwiftUI View Architecture

```
TabView (Main Navigation)
├── Dashboard Tab
│   ├── CareerHealthView (shows health score)
│   ├── PriorityActionsView (top 3 action items)
│   ├── AIGuidanceCardsView (latest guidance)
│   └── SyncStatusBadge (online/offline indicator)
│
├── Jobs Tab
│   ├── JobSearchView
│   │   ├── SearchBar (local search + backend search)
│   │   ├── FilterView (category, location, salary, remote)
│   │   └── JobListView (with sync status indicators)
│   ├── JobDetailView
│   │   ├── SaveButton (add to saved jobs)
│   │   ├── ApplyButton (apply to job)
│   │   └── ShareButton
│   └── SavedJobsView
│       ├── FilterView (applied, saved, archived)
│       └── JobListView
│
├── Profile Tab
│   ├── ProfileSummaryView
│   ├── EditProfileView
│   │   ├── PersonalInfoSection (editable)
│   │   ├── WorkHistorySection (with add/edit/delete)
│   │   ├── EducationSection
│   │   ├── SkillsSection
│   │   └── SaveButton (queues to sync)
│   ├── ProfileStrengthView (completeness score)
│   └── ExportProfileButton (PDF/JSON)
│
├── AI Coach Tab
│   ├── CareerGuidanceView
│   │   ├── GuidanceCardsView (priority ordered)
│   │   ├── ChatView (conversation with AI coach)
│   │   └── TipsView (curated career tips)
│   └── GoalsView
│       ├── GoalListView
│       ├── GoalDetailView
│       └── AddGoalView
│
└── Settings Tab
    ├── AccountSection
    │   ├── Profile (name, email)
    │   ├── Authentication (change password, 2FA)
    │   └── Logout Button
    ├── SyncSection
    │   ├── Manual Sync Button
    │   ├── Auto-Sync Toggle
    │   ├── Sync Status Log
    │   └── Clear Sync Queue Button
    ├── NotificationsSection
    │   ├── Push Notifications Toggle
    │   ├── Job Alerts Settings
    │   ├── Guidance Alerts Settings
    │   └── Achievement Alerts Settings
    ├── OfflineSection
    │   ├── Offline Mode Toggle
    │   ├── Storage Usage
    │   ├── Cache Management
    │   └── Clear Cache Button
    └── About Section
        ├── App Version
        ├── Build Number
        └── Help & Support
```

### Offline-First UI Patterns

```
1. Sync Status Indicator
   - Green dot: online & synced
   - Yellow dot: online but syncing
   - Gray dot: offline mode
   - Red dot: offline with pending changes
   - Tap to see details

2. Pending Changes Badge
   - On items with unsync changes
   - Shows count of items pending sync
   - Tap to see sync queue

3. Conflict Resolution Dialog
   - Shows conflicting values
   - "Keep Local" / "Use Remote" / "Manual Merge" buttons
   - Saves user's choice

4. Offline Graceful Degradation
   - Read-only mode when offline
   - Show cached data with "cached" badge
   - Queue all write operations
   - Show sync will happen when online

5. Background Sync Progress
   - Notification when sync starts
   - Progress badge in tab bar
   - Notification when sync completes
```

---

## 🔔 Push Notifications

### Notification Types

```
1. Job Alerts
   Content: "New job matching your profile"
   Payload: {
     type: "job_alert",
     jobId: "uuid",
     title: "Senior iOS Engineer",
     company: "Apple",
     matchScore: 0.95,
     action: "View Job"
   }
   
2. Career Guidance
   Content: "AI Coach: Complete your resume skills section"
   Payload: {
     type: "guidance",
     guidanceId: "uuid",
     category: "profile_completion",
     priority: 1,
     action: "View Advice"
   }
   
3. Achievement Unlocked
   Content: "🎉 You've completed your 10th job application!"
   Payload: {
     type: "achievement",
     achievementId: "uuid",
     title: "Application Master",
     icon: "🎉"
   }
   
4. Sync Notifications
   Content: "Profile changes synced" / "Sync failed, retry?"
   Payload: {
     type: "sync_status",
     status: "success" | "failed",
     itemCount: 5
   }
   
5. Churn Prevention Nudge
   Content: "Hey! We found 3 perfect jobs for you this week"
   Payload: {
     type: "nudge",
     content: "job_recommendations",
     count: 3
   }
```

### APNs Implementation

```swift
// Request user permission
UNUserNotificationCenter.current().requestAuthorization(
  options: [.alert, .sound, .badge]
) { granted, error in
  // Handle response
}

// Get device token
DispatchQueue.main.async {
  UIApplication.shared.registerForRemoteNotifications()
}

// Handle in AppDelegate
func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
  // Set notification delegate
  UNUserNotificationCenter.current().delegate = self
  return true
}

// Process notification
func userNotificationCenter(
  _ center: UNUserNotificationCenter,
  willPresent notification: UNNotification,
  withCompletionHandler: (UNNotificationPresentationOptions) -> Void
) {
  // Handle while app in foreground
  // Parse payload, update UI, sync if needed
}

func userNotificationCenter(
  _ center: UNUserNotificationCenter,
  didReceive response: UNNotificationResponse,
  withCompletionHandler: () -> Void
) {
  // Handle tap: navigate to relevant section
}
```

---

## 🔗 API Integration Points

### Modified Backend APIs

Existing backend APIs continue to work. iOS app adds these considerations:

```
1. GET /api/profile
   Response includes: lastModified, version
   iOS checks: version > local version?
   
2. POST /api/profile (Update)
   Request includes: version (for conflict detection)
   Response: success | conflict (with remote version)
   
3. GET /api/jobs/ai-recommendations?platform=mobile
   Returns: cached/downloadable format
   Optimization: return only essential fields
   
4. GET /api/guidance?platform=mobile
   Returns: batch of guidance messages
   Includes: actionable items, priority
   
5. POST /api/events (Event tracking)
   Same events, includes: offline=true/false
   Backend can identify offline-generated events
   
6. GET /api/sync/status
   Returns: lastSyncTimestamp, pendingCount
   iOS checks: am I up to date?
```

### New iOS-Specific APIs

```
1. POST /api/auth/request-device-token
   Body: { userId, deviceToken, platform: "iOS" }
   Purpose: Register device for push notifications
   
2. POST /api/sync/batch-check
   Body: { entityType, localVersions: {id: version} }
   Response: { updates: [{id, version, data}], conflicts: [...] }
   Purpose: Check for conflicts before upload
   
3. POST /api/events/batch (Offline Events)
   Body: { events: [...], offline: true }
   Response: { accepted, errors }
   Purpose: Sync events accumulated offline
   
4. GET /api/profile/export?format=pdf
   Response: PDF of profile
   Purpose: Download shareable profile
```

---

## 🚀 Development Roadmap

### Week 1: Foundation
- [ ] Set up iOS project structure (SwiftUI + Core Data)
- [ ] Implement authentication (Firebase integration)
- [ ] Design Core Data schema
- [ ] Create base ViewModels with state management

### Week 2: Core Features
- [ ] Implement profile viewing and editing (offline)
- [ ] Build job search with local filtering
- [ ] Create saved jobs functionality
- [ ] Add career guidance display

### Week 3: Sync Engine
- [ ] Implement sync manager with queue
- [ ] Add conflict resolution
- [ ] Build retry logic with exponential backoff
- [ ] Implement background sync (BGTask)

### Week 4: Polish & Testing
- [ ] Add push notifications
- [ ] Implement offline-first UI patterns
- [ ] Performance optimization
- [ ] Comprehensive testing (unit, integration, E2E)

### Week 5: Deployment
- [ ] App Store setup
- [ ] Signing certificates and provisioning profiles
- [ ] TestFlight beta testing
- [ ] App Store submission

---

## 🔐 Security Considerations

### Data Protection
```
1. Local Encryption
   - Core Data encrypted with SQLite encryption
   - Keychain for sensitive data (auth tokens)
   - App Groups data protection (minimum: app-visible)
   
2. Network Security
   - Certificate pinning for API calls
   - TLS 1.2+ required
   - Disable logging of sensitive data in production
   
3. Authentication
   - Firebase Auth tokens cached securely
   - Token refresh before expiry
   - Biometric + passcode for sensitive operations
   
4. Offline Data
   - All local data encrypted at rest
   - Wipe on logout
   - Device lock required for sensitive views
```

### Privacy
```
1. Data Collection
   - Analytics only with user consent
   - No event tracking without opt-in
   - Clear privacy policy in app
   
2. Push Notifications
   - User can disable per category
   - No tracking pixels in notifications
   - Server-side opt-out respected
   
3. Profile Sharing
   - Export with no personal data by default
   - User chooses what to include
   - Expiring share links (optional)
```

---

## 📊 Success Metrics

- **Users on Day 1**: Target 100+ beta testers
- **DAU (Daily Active Users)**: Target 40% of web users
- **Sync Success Rate**: >99.9% of operations sync successfully
- **Offline Availability**: Works 100% without internet
- **Avg Response Time**: <500ms locally, <2s with network
- **Battery Impact**: <5% per hour in background
- **Storage**: <200MB app + data cache
- **Crash Rate**: <0.1%
- **User Retention**: 70% 30-day retention

---

## 📝 Next Steps

1. **Review & Feedback** (24 hours)
   - Review this architecture with iOS experts
   - Get feedback on sync strategy
   - Confirm API requirements

2. **iOS Project Setup** (1 day)
   - Create Xcode project
   - Set up Firebase
   - Configure Core Data stack
   - Implement authentication flow

3. **Feature Development** (2 weeks)
   - Build UI screens
   - Implement offline functionality
   - Add sync engine
   - Integrate push notifications

4. **Testing & QA** (1 week)
   - Unit tests for sync logic
   - Integration tests for data flow
   - E2E testing on multiple devices
   - Beta testing with real users

5. **App Store Submission** (1 week)
   - Prepare metadata
   - Configure signing
   - Submit for review
   - Monitor for approval

---

## 📚 Resources & References

### Documentation
- [Apple SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Core Data Best Practices](https://developer.apple.com/documentation/coredata)
- [URLSession Background Transfer](https://developer.apple.com/documentation/foundation/urlsession)
- [APNs Certificate Setup](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server)

### Tools
- Xcode 15+
- SwiftUI Preview
- Core Data Model Editor
- iOS Simulator + real device testing

### Dependencies
```
- Firebase/Auth
- Firebase/Analytics
- Firebase/Messaging
- Reachability (for network monitoring)
```

---

## ✅ Sign-off

**Document Status**: Draft for Review  
**Created**: 2025-11-14  
**Last Updated**: 2025-11-14  
**Author**: Career OS Dev Team  

**TODO**: Get stakeholder approval before proceeding to development

---

## Appendix: Quick Reference

### Core Data Setup
```swift
@main
struct CareerOSApp: App {
  let persistenceController = PersistenceController.shared
  
  var body: some Scene {
    WindowGroup {
      ContentView()
        .environment(\.managedObjectContext, 
          persistenceController.container.viewContext)
    }
  }
}
```

### Sync Manager Usage
```swift
let syncManager = SyncManager.shared

// Mark change for sync
try syncManager.queueChange(
  operation: .update,
  entity: profile,
  changes: ["firstName": "John"]
)

// Trigger sync when online
await syncManager.syncIfNeeded()

// Monitor sync progress
syncManager.$isSyncing
  .sink { isSyncing in
    print("Syncing: \(isSyncing)")
  }
  .store(in: &cancellables)
```

### Conflict Detection
```swift
func checkForConflicts(_ local: Profile, _ remote: Profile) -> [String] {
  var conflicts: [String] = []
  
  if local.version < remote.version {
    // Check field-level differences
    if local.name != remote.name {
      conflicts.append("name")
    }
    if local.email != remote.email {
      conflicts.append("email")
    }
  }
  
  return conflicts
}
```
