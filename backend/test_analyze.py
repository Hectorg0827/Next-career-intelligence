#!/usr/bin/env python3
"""Test the analyze endpoint"""
import requests
import json

url = "http://localhost:8000/api/analyze"

payload = {
    "job_title": "Software Engineer",
    "skills": ["Python", "JavaScript", "React"],
    "years_experience": 3,
    "location": "San Francisco, CA",
}

print("🧪 Testing analyze endpoint...")
print(f"POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload, timeout=120)

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")

    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS!")
        result = response.json()
        print(f"Analysis ID: {result.get('analysis_id')}")
        print(f"AI Displacement Risk: {result.get('ai_displacement_risk')}")
        print(f"Compatibility Score: {result.get('compatibility_score')}")
    else:
        print("❌ ERROR!")
        try:
            error = response.json()
            print(f"Error: {json.dumps(error, indent=2)}")
        except:
            print(f"Raw response: {response.text}")

except requests.exceptions.Timeout:
    print("❌ REQUEST TIMEOUT (120s)")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
