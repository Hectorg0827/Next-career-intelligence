#!/usr/bin/env python3
"""
Quick test script to verify backend setup
Run after migrations are complete
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")
        print("   Make sure backend is running: python -m uvicorn app.main:app --reload")
        return False

def test_api_docs():
    """Test API documentation"""
    print("\n📚 Testing API docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible at http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not access docs: {e}")
        return False

def test_coach_endpoint_exists():
    """Check if coach endpoint is registered"""
    print("\n🤖 Testing AI Coach endpoint...")
    try:
        # This will fail with 401 (no auth), but that's expected
        response = requests.post(
            f"{BASE_URL}/api/coach/conversations/start",
            json={"firebase_uid": "test", "career_context": {}}
        )
        if response.status_code in [401, 403, 422]:
            print("✅ Coach endpoint exists (authentication required)")
            return True
        elif response.status_code == 404:
            print("❌ Coach endpoint not found - check main.py router registration")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Could not reach coach endpoint: {e}")
        return False

def test_payments_endpoint():
    """Check if payments endpoint exists"""
    print("\n💳 Testing Payments endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/payments/subscription-status")
        if response.status_code in [401, 403, 422]:
            print("✅ Payments endpoint exists")
            return True
        elif response.status_code == 404:
            print("❌ Payments endpoint not found")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Could not reach payments endpoint: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 NEXT Career Intelligence - Backend Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("API Docs", test_api_docs()))
    results.append(("AI Coach Endpoint", test_coach_endpoint_exists()))
    results.append(("Payments Endpoint", test_payments_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready.")
        print("\n📝 Next steps:")
        print("   1. Run migrations in Supabase (see MIGRATION_GUIDE.md)")
        print("   2. Start frontend: cd frontend && npm run dev")
        print("   3. Visit http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Make sure backend is running and migrations are complete.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
