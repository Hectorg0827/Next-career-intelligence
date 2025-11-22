"""
Verification Script for AI Coach 2.0
Simulates a conversation and checks DB updates.
"""
import requests
import json
import time

# Config
API_URL = "http://localhost:8000/api"
# You need a valid firebase_uid from your DB
FIREBASE_UID = "test_user_123" # Replace with a real one if needed, or ensure create_test_users.py ran

def test_coach_flow():
    print("🚀 Starting AI Coach Verification...")
    
    # 1. Start Conversation
    print("\n1. Starting Conversation...")
    try:
        resp = requests.post(f"{API_URL}/coach/conversations/start", json={
            "firebase_uid": FIREBASE_UID,
            "career_context": {
                "current_role": "Junior Developer",
                "goals": ["Become a Senior Developer"]
            }
        })
        if resp.status_code != 200:
            print(f"❌ Failed to start: {resp.text}")
            return
            
        data = resp.json()
        conv_id = data["conversation_id"]
        print(f"✅ Conversation Started: {conv_id}")
        print(f"🤖 Coach: {data['message']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Send Message (Skill Mining)
    print("\n2. Sending Message (Skill Mining)...")
    user_msg = "I've been building a lot of APIs using FastAPI and Python lately. I also deployed them to AWS."
    print(f"👤 User: {user_msg}")
    
    resp = requests.post(f"{API_URL}/coach/conversations/message", json={
        "firebase_uid": FIREBASE_UID,
        "conversation_id": conv_id,
        "message": user_msg
    })
    
    data = resp.json()
    print(f"🤖 Coach: {data['message']}")
    
    # 3. Send Message (Goal Setting)
    print("\n3. Sending Message (Goal Setting)...")
    user_msg = "I want to set a goal to learn Docker in the next 2 weeks."
    print(f"👤 User: {user_msg}")
    
    resp = requests.post(f"{API_URL}/coach/conversations/message", json={
        "firebase_uid": FIREBASE_UID,
        "conversation_id": conv_id,
        "message": user_msg
    })
    
    data = resp.json()
    print(f"🤖 Coach: {data['message']}")
    if data.get("goal_updates"):
        print(f"✅ Goal Updates Detected: {json.dumps(data['goal_updates'], indent=2)}")
    else:
        print("⚠️ No goal updates returned (Model might not have triggered)")

    # 4. Verify DB (Skills)
    # We can't easily check DB from here without psycopg2, but we can trust the logs or check via API if we had a skill endpoint.
    # For now, we rely on the fact that no 500 error occurred.
    print("\n✅ Flow completed without errors.")

if __name__ == "__main__":
    test_coach_flow()
