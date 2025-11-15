# Phase 3: iOS Integration - Quick Reference

## 🎯 Quick Start (5 minutes)

### What is Phase 3?
Add a native iOS app to Career OS with **offline functionality**, **real-time sync**, and **push notifications**. Users can access their career profile, job search, and AI guidance from their iPhone - even without internet.

### Key Features
- ✅ Work offline, sync when online
- ✅ Real-time data synchronization with conflict detection
- ✅ Push notifications for job alerts and guidance
- ✅ Native SwiftUI interface (iOS 14+)
- ✅ Background sync with intelligent retry logic

### Architecture in 30 Seconds

```
iOS App (SwiftUI + Core Data)
    ↓ (offline-first)
    ├→ Local Storage (Core Data SQLite)
    ├→ Sync Queue (pending changes)
    └→ Sync Manager
        ↓ (when online)
        → API Server (localhost:8000)
        → Firebase (auth, analytics)
        → APNs (push notifications)
```

### Data Flow
```
User edits profile on iPhone
    ↓
Optimistic update (instant feedback)
    ↓
Add to sync queue
    ↓
Connect to internet (optional)
    ↓
Sync manager uploads changes
    ↓
Conflict detected? → Resolve locally
    ↓
Success → remove from queue, update version
    ↓
Download remote updates
    ↓
Merge and show notification
```

---

## 📱 Before You Start

### Requirements
```
- Xcode 15+ with iOS 14+ SDK
- Swift 5.9+
- macOS 12+ (development machine)
- Apple Developer Account ($99/year)
- Firebase Account (free tier available)
```

### Frameworks Needed
```
- SwiftUI (UI)
- Core Data (local storage)
- URLSession (networking)
- UserNotifications (push)
- BackgroundTasks (background sync)
- Firebase Auth
- Firebase Messaging
```

---

## 🏗️ Data Model (Core Data)

### Main Entities
```
Profile (root object)
├── firstName, lastName, email, phone, location
├── WorkExperience (1:N)
├── Education (1:N)
├── Skill (1:N)
├── SavedJob (1:N)
├── AIGuidance (1:N)
└── SyncQueueItem (1:N) - tracks unsync changes

SavedJob
├── jobId, title, company, location
├── isSaved, isApplied, appliedDate
└── status: saved, applied, rejected, etc.

SyncQueueItem - tracks what needs to sync
├── operationType: CREATE, UPDATE, DELETE
├── entityType: Profile, WorkExperience, etc.
├── entityId, payload (JSON)
├── retryCount, lastRetryDate
└── status: pending, synced, failed
```

### Version-Based Conflict Detection
```
Each entity has:
- version (Int32) - incremented on server update
- lastModified (Date) - local last change time

Conflict detection:
IF local.version < remote.version
  AND same field changed locally
  → CONFLICT!
  
Resolution strategy:
1. Last-Write-Wins (default)
2. Local-Preferred (for mobile)
3. Field-level merge
4. Manual conflict resolution UI
```

---

## 🔄 Sync System

### Upload (Local → Server)

```swift
// When user makes change:
1. Update Core Data
2. Add SyncQueueItem {
     operationType: "UPDATE"
     entityType: "Profile"
     entityId: profile.id
     payload: {firstName: "John"}
     status: "pending"
   }
3. When online, SyncManager:
   - Gets all "pending" items
   - Groups by entity
   - Sends to /api/profile/sync
   - On success: mark "synced"
   - On conflict: trigger ConflictResolver
   - On failure: increment retryCount, schedule retry
```

### Download (Server → Local)

```swift
// Periodically (every 5 min when online):
1. GET /api/profile/sync?lastSync=2024-01-01T10:00:00Z
2. Response: { updates: [Profile, SavedJob, ...] }
3. Merge each update:
   - Check local version
   - IF remote.version > local → update
   - IF conflict → resolve
4. Update lastSyncDate
5. Notify UI of changes
```

### Retry Strategy (Exponential Backoff)

```
Retry delays: 1s, 2s, 4s, 8s, 30s, 5min, 30min
Max retries: 10

After 10 failures:
- Move to "failed" status
- Show alert to user
- Offer manual retry
- Log for debugging
```

---

## 🔌 Connectivity Handling

### Reachability Monitor

```swift
import Reachability

let reachability = try Reachability()

NotificationCenter.default.addObserver(
  forName: .reachabilityChanged,
  object: reachability,
  queue: .main
) { _ in
  if reachability.isReachable {
    // Just came online
    syncManager.performSync()
  }
}
```

### Offline Queue Operations

```
When offline:
- All writes added to SyncQueue
- UI shows "pending sync" badge
- Retry logic paused
- Cache all reads

When online:
- Process sync queue (oldest first)
- Show progress notifications
- Retry failed items
- Download updates
```

---

## 📲 Push Notifications

### Types & Payloads

```
1. Job Alert
   {
     type: "job_alert",
     jobId: "uuid",
     title: "Senior iOS Engineer",
     company: "Apple",
     action: "View"
   }

2. Guidance
   {
     type: "guidance",
     guidanceId: "uuid",
     category: "profile_completion",
     priority: 1,
     action: "View Advice"
   }

3. Achievement
   {
     type: "achievement",
     title: "Your 10th application!",
     icon: "🎉"
   }

4. Sync Status
   {
     type: "sync",
     status: "success" | "failed",
     itemCount: 3
   }
```

### APNs Setup

```swift
// Request permission
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
  if granted {
    DispatchQueue.main.async {
      UIApplication.shared.registerForRemoteNotifications()
    }
  }
}

// Get device token
func application(_ application: UIApplication, 
  didFinishLaunchingWithOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
  let center = UNUserNotificationCenter.current()
  center.delegate = self
  return true
}

func application(_ application: UIApplication,
  didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
  let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
  // Send token to backend: POST /api/notifications/register
}

// Handle notification
func userNotificationCenter(
  _ center: UNUserNotificationCenter,
  didReceive response: UNNotificationResponse,
  withCompletionHandler: () -> Void
) {
  let userInfo = response.notification.request.content.userInfo
  let type = userInfo["type"] as? String
  
  switch type {
  case "job_alert":
    navigateToJob(userInfo["jobId"] as? String)
  case "guidance":
    navigateToGuidance()
  default:
    break
  }
  
  withCompletionHandler()
}
```

---

## 🎨 UI Architecture

### View Hierarchy

```
ContentView (main)
├── TabView
│   ├── DashboardView
│   │   ├── CareerHealthView
│   │   ├── PriorityActionsView
│   │   ├── AIGuidanceView
│   │   └── SyncStatusBadge
│   │
│   ├── JobsView
│   │   ├── JobSearchView
│   │   ├── JobDetailView
│   │   └── SavedJobsView
│   │
│   ├── ProfileView
│   │   ├── EditProfileView
│   │   ├── ProfileStrengthView
│   │   └── ExportProfileView
│   │
│   ├── AICoachView
│   │   ├── GuidanceView
│   │   ├── ChatView
│   │   └── GoalsView
│   │
│   └── SettingsView
│       ├── AccountSettings
│       ├── SyncSettings
│       ├── NotificationSettings
│       └── OfflineSettings
```

### State Management

```swift
@main
struct CareerOSApp: App {
  @StateObject var authViewModel = AuthViewModel()
  @StateObject var syncManager = SyncManager.shared
  
  var body: some Scene {
    WindowGroup {
      ContentView()
        .environmentObject(authViewModel)
        .environmentObject(syncManager)
    }
  }
}

// In views:
@EnvironmentObject var syncManager: SyncManager
@FetchRequest var savedJobs: FetchedResults<SavedJob>
```

### Offline UI Patterns

```
Sync Status Badge:
🟢 Online & synced
🟡 Online & syncing
⚪ Offline
🔴 Offline with pending

Pending Changes Badge:
Shows count: "3 pending"
Tap to see sync queue

Conflict Dialog:
"Profile name conflict"
Keep Local | Use Remote | Manual Merge

Graceful Degradation:
- Read-only mode when offline
- Show cached data with "cached" label
- Queue all writes
- Notify when online
```

---

## 🚀 Development Phases

### Phase 3.1: Foundation (Week 1-2)
```
✅ iOS project setup
✅ Core Data model
✅ Firebase integration
✅ Authentication flow
✅ Profile viewing/editing
✅ Sync queue system
```

### Phase 3.2: Features (Week 3)
```
✅ Job search & saved jobs
✅ AI guidance display
✅ Career health dashboard
✅ Background sync
✅ Conflict resolution
```

### Phase 3.3: Polish (Week 4-5)
```
✅ Push notifications
✅ Performance optimization
✅ Unit & integration tests
✅ App Store submission
✅ TestFlight beta
```

---

## 🔐 Security Checklist

- [ ] All API calls use HTTPS
- [ ] Certificate pinning enabled
- [ ] Firebase tokens stored in Keychain
- [ ] Core Data encrypted at rest
- [ ] No sensitive data in logs
- [ ] Biometric + passcode for sensitive ops
- [ ] Data wiped on logout
- [ ] Privacy policy reviewed

---

## 🧪 Testing Strategy

### Unit Tests
```
- ConflictResolver logic
- Sync queue operations
- Network request formatting
- Date/time calculations
- Cache invalidation
```

### Integration Tests
```
- Full sync flow (upload + download)
- Conflict detection & resolution
- Offline → online transition
- Cache consistency
- Notification handling
```

### E2E Tests
```
- Create profile → sync → check backend
- Edit job → offline → save → online → sync
- Delete entity → conflict resolution
- Multiple device sync scenarios
```

---

## 📊 Key Metrics

| Metric | Target |
|--------|--------|
| Daily Active Users | 40% of web users |
| Sync Success Rate | >99.9% |
| Average Sync Time | <2 seconds |
| Battery Impact | <5%/hour background |
| Cache Size | <200MB |
| Crash Rate | <0.1% |
| 30-Day Retention | 70% |

---

## 📚 Code Examples

### Sync Manager Init

```swift
class SyncManager: ObservableObject {
  static let shared = SyncManager()
  
  @Published var isSyncing = false
  @Published var pendingChangesCount = 0
  
  private let apiClient = APIClient.shared
  private var reachability: Reachability?
  
  override init() {
    super.init()
    setupReachability()
  }
  
  func syncIfNeeded() {
    Task {
      await performSync()
    }
  }
}
```

### Core Data View Model

```swift
class ProfileViewModel: NSObject, ObservableObject {
  @Published var profile: Profile?
  @FetchRequest<Profile>(
    entity: Profile.entity(),
    sortDescriptors: [],
    predicate: NSPredicate(format: "id == %@", "current-user-id")
  ) var profiles: FetchedResults<Profile>
  
  func updateProfile(_ changes: [String: Any]) {
    // Update locally
    // Add to sync queue
    // Trigger sync if online
  }
}
```

### Conflict Resolution

```swift
class ConflictResolver {
  static func resolve(
    local: Profile,
    remote: Profile,
    strategy: ResolutionStrategy = .lastWriteWins
  ) -> Profile {
    switch strategy {
    case .lastWriteWins:
      return local.version > remote.version ? local : remote
    case .localPreferred:
      return local
    case .fieldLevelMerge:
      return mergeFieldByField(local, remote)
    }
  }
}
```

---

## 🔗 API Endpoints Used

```
Authentication:
POST /api/auth/login
POST /api/auth/signup
POST /api/auth/refresh

Profile Sync:
GET /api/profile
POST /api/profile (update)
GET /api/profile/sync?lastSync=...

Job Search:
GET /api/jobs/search?query=...
GET /api/jobs/{id}
POST /api/jobs/{id}/save
POST /api/jobs/{id}/apply
GET /api/jobs/ai-recommendations

AI Guidance:
GET /api/guidance?limit=10
POST /api/guidance/{id}/dismiss

Push Notifications:
POST /api/notifications/register
POST /api/notifications/unregister
```

---

## 🎯 Success Criteria

- [ ] App runs on iOS 14+
- [ ] All 14 backend endpoints accessible from iOS
- [ ] Offline mode fully functional
- [ ] Sync success rate > 99.9%
- [ ] <200MB storage usage
- [ ] Passes App Store review
- [ ] 1000+ beta users in TestFlight
- [ ] <0.1% crash rate

---

## 📞 Getting Help

### Common Issues

**"Sync always fails"**
- Check API endpoint in Constants
- Verify Firebase auth working
- Check network request logs

**"Core Data corruption"**
- Clear app data and reinstall
- Check data model versioning
- Enable verbose logging

**"Notifications not working"**
- Verify device token sent to backend
- Check APNs certificate in Apple Developer
- Ensure notification permission granted

**"Conflict never resolves"**
- Check version number logic
- Verify timestamp accuracy
- Test with manual conflict scenario

---

## 📝 Files to Create

```
iOS Project Structure:
├── CareerOSApp.swift
├── PersistenceController.swift
├── SyncManager.swift
├── ConflictResolver.swift
├── APIClient.swift
├── Views/
│   ├── DashboardView.swift
│   ├── ProfileView.swift
│   ├── JobsView.swift
│   ├── AICoachView.swift
│   └── SettingsView.swift
├── ViewModels/
│   ├── DashboardViewModel.swift
│   ├── ProfileViewModel.swift
│   ├── JobsViewModel.swift
│   └── AICoachViewModel.swift
└── Core Data Models/
    └── CareerOS.xcdatamodeld
```

---

## ✅ Ready to Start?

1. ✅ **Read**: `PHASE3_iOS_INTEGRATION.md` (full technical spec)
2. ✅ **Follow**: `PHASE3_iOS_SETUP_GUIDE.md` (step-by-step setup)
3. ✅ **Code**: Implement features following this roadmap
4. ✅ **Test**: Unit, integration, E2E tests
5. ✅ **Deploy**: TestFlight beta, App Store

---

**Phase 3 Status**: Ready for development  
**Estimated Duration**: 4-6 weeks  
**Team Size**: 1-2 iOS developers  
**Next Review**: Week 1 completion review

