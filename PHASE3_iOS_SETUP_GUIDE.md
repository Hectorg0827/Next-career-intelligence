# Phase 3: iOS Project Setup Guide

Quick start for creating the Career OS iOS app.

## 📦 Project Creation

### 1. Create Xcode Project

```bash
# Using Xcode UI:
# File → New → Project
# iOS → App
# Product Name: CareerOS
# Team: None (personal)
# Organization: Career OS
# Bundle Identifier: com.careerOS.mobile
# Interface: SwiftUI
# Language: Swift
# Min iOS: 14.0
```

### 2. Project Structure

```
CareerOS/
├── App/
│   ├── CareerOSApp.swift (main entry point)
│   ├── AppDelegate.swift (lifecycle)
│   └── SceneDelegate.swift (scene lifecycle)
│
├── Features/
│   ├── Dashboard/
│   │   ├── Views/
│   │   │   ├── DashboardView.swift
│   │   │   ├── CareerHealthView.swift
│   │   │   ├── PriorityActionsView.swift
│   │   │   └── AIGuidanceView.swift
│   │   ├── ViewModels/
│   │   │   └── DashboardViewModel.swift
│   │   └── Models/
│   │       └── DashboardModels.swift
│   │
│   ├── Profile/
│   │   ├── Views/
│   │   │   ├── ProfileView.swift
│   │   │   ├── EditProfileView.swift
│   │   │   └── ProfileStrengthView.swift
│   │   ├── ViewModels/
│   │   │   └── ProfileViewModel.swift
│   │   └── Models/
│   │       └── ProfileModels.swift
│   │
│   ├── Jobs/
│   │   ├── Views/
│   │   │   ├── JobsView.swift
│   │   │   ├── JobSearchView.swift
│   │   │   ├── JobDetailView.swift
│   │   │   └── SavedJobsView.swift
│   │   ├── ViewModels/
│   │   │   └── JobsViewModel.swift
│   │   └── Models/
│   │       └── JobModels.swift
│   │
│   ├── AICoach/
│   │   ├── Views/
│   │   │   ├── AICoachView.swift
│   │   │   ├── GuidanceView.swift
│   │   │   └── GoalsView.swift
│   │   ├── ViewModels/
│   │   │   └── AICoachViewModel.swift
│   │   └── Models/
│   │       └── AICoachModels.swift
│   │
│   ├── Settings/
│   │   ├── Views/
│   │   │   ├── SettingsView.swift
│   │   │   ├── AccountSettingsView.swift
│   │   │   ├── SyncSettingsView.swift
│   │   │   └── NotificationSettingsView.swift
│   │   ├── ViewModels/
│   │   │   └── SettingsViewModel.swift
│   │   └── Models/
│   │       └── SettingsModels.swift
│   │
│   └── Auth/
│       ├── Views/
│       │   ├── LoginView.swift
│       │   ├── SignupView.swift
│       │   └── ForgotPasswordView.swift
│       ├── ViewModels/
│       │   └── AuthViewModel.swift
│       └── Models/
│           └── AuthModels.swift
│
├── Data/
│   ├── CoreData/
│   │   ├── PersistenceController.swift
│   │   ├── CoreDataStack.swift
│   │   └── Models/
│   │       ├── Profile+CoreDataClass.swift
│   │       ├── WorkExperience+CoreDataClass.swift
│   │       ├── SavedJob+CoreDataClass.swift
│   │       ├── SyncQueueItem+CoreDataClass.swift
│   │       └── CareerOS.xcdatamodeld
│   │
│   ├── Sync/
│   │   ├── SyncManager.swift
│   │   ├── ConflictResolver.swift
│   │   ├── BackoffStrategy.swift
│   │   └── SyncQueue.swift
│   │
│   ├── Network/
│   │   ├── APIClient.swift
│   │   ├── Endpoints.swift
│   │   ├── NetworkMonitor.swift
│   │   └── CertificatePinning.swift
│   │
│   └── Cache/
│       ├── CacheManager.swift
│       └── ImageCache.swift
│
├── Services/
│   ├── AuthService.swift
│   ├── StorageService.swift
│   ├── NotificationService.swift
│   ├── AnalyticsService.swift
│   └── LocalizationService.swift
│
├── Utilities/
│   ├── Constants.swift
│   ├── DateFormatter+Extensions.swift
│   ├── String+Extensions.swift
│   ├── View+Extensions.swift
│   └── Logging.swift
│
├── Resources/
│   ├── Localization/
│   │   └── Localizable.strings
│   ├── Assets.xcassets/
│   │   ├── AppIcon.appiconset/
│   │   ├── Colors/
│   │   └── Images/
│   └── Fonts/
│
└── Tests/
    ├── Unit/
    │   ├── SyncManagerTests.swift
    │   ├── ConflictResolverTests.swift
    │   └── APIClientTests.swift
    ├── Integration/
    │   ├── CoreDataTests.swift
    │   └── SyncIntegrationTests.swift
    └── UI/
        ├── ProfileViewTests.swift
        └── JobsViewTests.swift
```

### 3. Core Data Model Setup

```swift
// CareerOS.xcdatamodeld structure
```

**Entity: Profile**
```
Attributes:
- id (UUID)
- userId (String) - Firebase user ID
- firstName (String)
- lastName (String)
- email (String)
- phone (String)
- location (String)
- bio (String)
- photoURL (String, optional)
- lastSyncDate (Date)
- version (Integer 32) - for conflict detection

Relationships:
- workHistory (WorkExperience, one-to-many, ordered)
- education (Education, one-to-many, ordered)
- skills (Skill, one-to-many)
- savedJobs (SavedJob, one-to-many)
- syncQueue (SyncQueueItem, one-to-many)
```

**Entity: WorkExperience**
```
Attributes:
- id (UUID)
- title (String)
- company (String)
- startDate (Date)
- endDate (Date, optional)
- isCurrent (Boolean)
- description (String)
- localVersion (Integer 32)
- lastModified (Date)

Relationships:
- profile (Profile, many-to-one)
```

**Entity: Education**
```
Attributes:
- id (UUID)
- school (String)
- degree (String)
- fieldOfStudy (String)
- startDate (Date, optional)
- endDate (Date, optional)
- description (String, optional)

Relationships:
- profile (Profile, many-to-one)
```

**Entity: Skill**
```
Attributes:
- id (UUID)
- name (String)
- category (String)
- proficiency (Integer 32) - 1-5
- endorsements (Integer 32)
- source (String) - manual, inferred, etc.

Relationships:
- profile (Profile, many-to-one)
```

**Entity: SavedJob**
```
Attributes:
- id (UUID)
- jobId (String) - backend job ID
- title (String)
- company (String)
- location (String)
- salary (String, optional)
- description (String)
- isRemote (Boolean)
- isSaved (Boolean)
- isApplied (Boolean)
- appliedDate (Date, optional)
- savedDate (Date)
- status (String) - saved, applied, rejected, etc.

Relationships:
- profile (Profile, many-to-one)
```

**Entity: SyncQueueItem**
```
Attributes:
- id (UUID)
- operationType (String) - CREATE, UPDATE, DELETE
- entityType (String) - Profile, WorkExperience, SavedJob, etc.
- entityId (UUID)
- payload (Binary) - JSON encoded changes
- createdDate (Date)
- retryCount (Integer 32)
- lastRetryDate (Date, optional)
- status (String) - pending, synced, failed
- error (String, optional)

Relationships:
- profile (Profile, many-to-one)
```

**Entity: AIDuidance**
```
Attributes:
- id (UUID)
- guidanceId (String) - backend guidance ID
- type (String) - profile_completion, job_alert, etc.
- priority (Integer 32) - 1-5
- title (String)
- content (String)
- actionItems (String) - JSON array
- isRead (Boolean)
- isDismissed (Boolean)
- createdDate (Date)

Relationships:
- profile (Profile, many-to-one)
```

## 🔧 Dependencies (CocoaPods)

Create `Podfile`:

```ruby
platform :ios, '14.0'

target 'CareerOS' do
  pod 'Firebase/Auth'
  pod 'Firebase/Analytics'
  pod 'Firebase/Messaging'
  pod 'Reachability'
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] ||= [
        '$(inherited)',
        'FIREBASE_ANALYTICS_COLLECTION_ENABLED=1',
      ]
    end
  end
end
```

Install:
```bash
pod install
```

## 🔑 Environment Configuration

### Info.plist Additions

```xml
<dict>
  <!-- Firebase Configuration -->
  <key>FIREBASE_PROJECT_ID</key>
  <string>your-firebase-project-id</string>
  
  <!-- API Configuration -->
  <key>API_BASE_URL</key>
  <string>http://localhost:8000</string>
  <key>API_TIMEOUT</key>
  <integer>30</integer>
  
  <!-- Sync Configuration -->
  <key>SYNC_RETRY_MAX_ATTEMPTS</key>
  <integer>10</integer>
  <key>SYNC_RETRY_INITIAL_DELAY</key>
  <integer>1</integer>
  
  <!-- App Configuration -->
  <key>APP_VERSION</key>
  <string>1.0.0</string>
  <key>MINIMUM_iOS_VERSION</key>
  <string>14.0</string>
</dict>
```

### GoogleService-Info.plist

Download from Firebase Console:
1. Go to Firebase Console
2. Select Career OS project
3. Add iOS app
4. Download GoogleService-Info.plist
5. Add to Xcode project (check "Copy items if needed")

## 📦 Initial Code Structure

### CareerOSApp.swift

```swift
import SwiftUI
import Firebase

@main
struct CareerOSApp: App {
  let persistenceController = PersistenceController.shared
  @StateObject private var authViewModel = AuthViewModel()
  @StateObject private var syncManager = SyncManager.shared
  
  init() {
    FirebaseApp.configure()
  }
  
  var body: some Scene {
    WindowGroup {
      if authViewModel.isLoggedIn {
        ContentView()
          .environment(\.managedObjectContext,
            persistenceController.container.viewContext)
          .environmentObject(authViewModel)
          .environmentObject(syncManager)
      } else {
        LoginView()
          .environmentObject(authViewModel)
      }
    }
  }
}
```

### PersistenceController.swift

```swift
import CoreData

struct PersistenceController {
  static let shared = PersistenceController()
  
  let container: NSPersistentCloudKitContainer
  
  init(inMemory: Bool = false) {
    container = NSPersistentCloudKitContainer(name: "CareerOS")
    
    if inMemory {
      container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
    }
    
    container.loadPersistentStores { description, error in
      if let error = error as NSError? {
        fatalError("Unresolved error \(error), \(error.userInfo)")
      }
    }
    
    container.viewContext.automaticallyMergesChangesFromParent = true
  }
}
```

### SyncManager.swift

```swift
import Foundation
import Combine
import CoreData

class SyncManager: NSObject, ObservableObject {
  static let shared = SyncManager()
  
  @Published var isSyncing = false
  @Published var lastSyncDate: Date?
  @Published var syncError: String?
  @Published var pendingChangesCount = 0
  
  private var reachability: Reachability?
  private let apiClient = APIClient.shared
  private let persistenceController = PersistenceController.shared
  
  override init() {
    super.init()
    setupReachability()
    observePersistenceChanges()
  }
  
  private func setupReachability() {
    reachability = try? Reachability()
    NotificationCenter.default.addObserver(
      self,
      selector: #selector(reachabilityChanged),
      name: .reachabilityChanged,
      object: reachability
    )
    try? reachability?.startNotifier()
  }
  
  @objc private func reachabilityChanged() {
    if reachability?.isReachable == true {
      syncIfNeeded()
    }
  }
  
  func syncIfNeeded() {
    Task {
      await performSync()
    }
  }
  
  private func performSync() async {
    guard !isSyncing else { return }
    
    DispatchQueue.main.async {
      self.isSyncing = true
    }
    
    defer {
      DispatchQueue.main.async {
        self.isSyncing = false
      }
    }
    
    // Upload pending changes
    await uploadPendingChanges()
    
    // Download remote updates
    await downloadRemoteUpdates()
    
    DispatchQueue.main.async {
      self.lastSyncDate = Date()
    }
  }
  
  private func uploadPendingChanges() async {
    // Implementation: get sync queue items and send to backend
  }
  
  private func downloadRemoteUpdates() async {
    // Implementation: fetch updates from backend
  }
  
  private func observePersistenceChanges() {
    NotificationCenter.default.addObserver(
      self,
      selector: #selector(contextsDidSave),
      name: NSManagedObjectContext.didSaveNotification,
      object: persistenceController.container.viewContext
    )
  }
  
  @objc private func contextsDidSave() {
    updatePendingChangesCount()
  }
  
  private func updatePendingChangesCount() {
    let request: NSFetchRequest<SyncQueueItem> = SyncQueueItem.fetchRequest()
    request.predicate = NSPredicate(format: "status == %@", "pending")
    
    if let count = try? persistenceController.container.viewContext.count(for: request) {
      DispatchQueue.main.async {
        self.pendingChangesCount = count
      }
    }
  }
}
```

## 🚀 Next Steps

1. **Create project** using this structure
2. **Install dependencies**: `pod install`
3. **Configure Firebase**: Set up GoogleService-Info.plist
4. **Implement Auth**: Firebase auth flows
5. **Build Core Data**: Create entities and relationships
6. **Implement Sync**: Build SyncManager and conflict resolution
7. **Create UI**: Build views with SwiftUI
8. **Add Tests**: Unit and integration tests
9. **Push Notifications**: Set up APNs
10. **Deploy**: TestFlight and App Store

---

## 📚 Resources

- [Apple SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Core Data Fundamentals](https://developer.apple.com/documentation/coredata)
- [Firebase iOS Setup](https://firebase.google.com/docs/ios/setup)
- [URLSession Documentation](https://developer.apple.com/documentation/foundation/urlsession)
- [Background App Refresh](https://developer.apple.com/documentation/backgroundtasks)

---

## 📝 Status

- [ ] Project created
- [ ] Core Data model set up
- [ ] Firebase integrated
- [ ] Sync manager implemented
- [ ] UI screens built
- [ ] Testing complete
- [ ] Ready for TestFlight

