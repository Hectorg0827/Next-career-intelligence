#!/usr/bin/env python3
"""
Phase 2 Deployment Verification
================================

Quick check to verify all Phase 2 components are properly integrated
and ready for deployment.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 70)
print("Phase 2 AI Agents - Deployment Verification")
print("=" * 70)
print()

def check_module(module_name, import_statement):
    """Check if a module can be imported"""
    try:
        exec(import_statement)
        print(f"✓ {module_name:40} OK")
        return True
    except Exception as e:
        print(f"✗ {module_name:40} FAILED")
        print(f"  Error: {str(e)[:60]}")
        return False

print("Checking Core AI Modules:")
print("-" * 70)

checks = [
    ("AI Memory System", "from app.services.foundation.ai.memory import ai_memory"),
    ("Recommendation Engine", "from app.services.foundation.ai.recommendations import recommendation_engine"),
    ("Career Guidance", "from app.services.foundation.ai.guidance import proactive_guidance"),
    ("Predictive Analytics", "from app.services.foundation.ai.predictions import predictive_analytics"),
    ("Profile Assistant", "from app.services.foundation.ai.profile_assistant import profile_assistant"),
]

results = []
for name, import_stmt in checks:
    results.append(check_module(name, import_stmt))

print()
print("Checking Integration Modules:")
print("-" * 70)

integration_checks = [
    ("AI Background Jobs", "from app.tasks.ai_jobs import start_ai_jobs, stop_ai_jobs"),
    ("AI API Endpoints", "from app.api.ai_agents import router"),
]

for name, import_stmt in integration_checks:
    results.append(check_module(name, import_stmt))

print()
print("=" * 70)

if all(results):
    print("✓ All Phase 2 modules verified successfully!")
    print()
    print("Next steps:")
    print("1. Install missing dependencies: pip install -r backend/requirements.txt")
    print("2. Start backend: cd backend && uvicorn app.main:app --reload")
    print("3. Run integration tests: python3 test-phase2-integration.py")
    sys.exit(0)
else:
    print("✗ Some modules failed to import")
    print()
    print("Fix the errors above, then run this script again.")
    sys.exit(1)
