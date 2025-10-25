# iOS Simulator Networking Fix

## Problem
The iOS app (LyoApp) is trying to reach `http://localhost:8000` but getting **Connection refused** errors (error code -1004, errno 61).

```
Error Domain=NSURLErrorDomain Code=-1004 "Could not connect to the server."
nw_endpoint_flow_failed_with_error [C4.1.2 127.0.0.1:8000 in_progress socket-flow]
Connection 4: failed to connect 1:61
```

## Root Cause
iOS simulators have isolated networking. They can't access `localhost` or `127.0.0.1` on the host Mac directly. You need to use the **host machine's actual IP address**.

## Solution

### Option 1: Use Your Machine's IP Address (Recommended)

**Step 1: Find your Mac's IP address**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Look for something like `192.168.x.x` or `10.0.x.x` (on the same network as your Mac).

**Step 2: Update iOS app to use this IP**

In your iOS app code, change:
```swift
// FROM:
let baseURL = "http://localhost:8000"

// TO (example with 192.168.1.100):
let baseURL = "http://192.168.1.100:8000"
```

**Step 3: Verify backend is accessible**
```bash
# From your Mac:
curl http://<YOUR_IP>:8000/api/v1/health

# From iOS simulator, it should now work
```

### Option 2: Use .local Domain (Alternative)

```swift
let baseURL = "http://local.machine:8000"
```

And add to your Mac's hosts file:
```bash
sudo nano /etc/hosts
# Add: 127.0.0.1 local.machine
```

### Option 3: Use Docker Bridge (If using Docker)

If running backend in Docker:
```bash
# Get Docker bridge IP
docker inspect <container_id> | grep IPAddress
```

### Option 4: Special IP for Simulator

iOS 14+ simulators can reach the host using:
```swift
let baseURL = "http://127.0.0.1:8000"  // FOR REAL DEVICE
let baseURL = "http://10.0.2.2:8000"   // FOR ANDROID EMULATOR

// For iOS simulator, best is actual machine IP
```

## Quick Test

**From terminal:**
```bash
# Find your IP
ifconfig | grep "inet " | grep -v 127.0.0.1
# Output might be: inet 192.168.1.100

# Test it
curl http://192.168.1.100:8000/api/v1/health
```

**In iOS app:**
Change any hardcoded `localhost:8000` to your actual IP.

## Common Issues

### Still Getting Connection Refused?

1. **Check firewall**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   ```

2. **Check if backend is listening on all interfaces**
   ```bash
   # Backend should be running on 0.0.0.0:8000
   lsof -i :8000
   ```

3. **Restart simulator**
   ```bash
   xcrun simctl erase all
   ```

4. **Check backend logs for errors**
   ```bash
   # Look for connection attempts in backend logs
   ```

## Next Steps

1. ✅ Get your Mac's IP address
2. ✅ Update iOS app configuration to use that IP
3. ✅ Restart the iOS simulator app
4. ✅ Verify connection works
5. ✅ Test API calls from app

---

**Note:** This is only needed for iOS simulator. Real iOS devices on the same network can typically reach your Mac directly using the IP address.
