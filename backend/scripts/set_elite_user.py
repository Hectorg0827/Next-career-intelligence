#!/usr/bin/env python3
"""
Script to set a user as elite/admin for testing purposes
Usage: python set_elite_user.py <firebase_uid> [role] [subscription]
Example: python set_elite_user.py abc123xyz elite elite
"""

import sys
import requests

# Backend URL
BACKEND_URL = "https://next-backend-795538981829.us-central1.run.app"

def set_user_role(firebase_uid: str, role: str = "elite", subscription: str = "elite"):
    """Set user role and subscription status"""
    
    url = f"{BACKEND_URL}/api/users/{firebase_uid}/set-role"
    params = {
        "role": role,
        "subscription_status": subscription
    }
    
    print(f"Setting user role...")
    print(f"  Firebase UID: {firebase_uid}")
    print(f"  Role: {role}")
    print(f"  Subscription: {subscription}")
    print()
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        user_data = response.json()
        print("✅ Success! User updated:")
        print(f"  Email: {user_data.get('email')}")
        print(f"  Name: {user_data.get('name')}")
        print(f"  Role: {user_data.get('role')}")
        print(f"  Subscription: {user_data.get('subscription_status')}")
        print()
        print("🎉 You can now test all elite/admin features!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_elite_user.py <firebase_uid> [role] [subscription]")
        print()
        print("Roles: user, elite, admin")
        print("Subscriptions: free, pro, elite")
        print()
        print("Example: python set_elite_user.py abc123xyz elite elite")
        sys.exit(1)
    
    firebase_uid = sys.argv[1]
    role = sys.argv[2] if len(sys.argv) > 2 else "elite"
    subscription = sys.argv[3] if len(sys.argv) > 3 else "elite"
    
    set_user_role(firebase_uid, role, subscription)
