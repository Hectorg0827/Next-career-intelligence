#!/usr/bin/env python3
"""
Phase 2 AI Agents - Route Registration Validation
==================================================

Validates that all 15 AI agent endpoints are:
1. Registered in FastAPI router
2. Appearing in OpenAPI spec
3. Accessible and responding

Usage:
    python3 PHASE2_ROUTE_VALIDATION.py
"""

import json
import subprocess
import sys
from typing import List, Dict, Tuple

BASE_URL = "http://localhost:8000"

# Expected AI endpoints from ai_agents.py
EXPECTED_ENDPOINTS = [
    "/api/ai/memory/form",
    "/api/ai/memory/context",
    "/api/ai/recommendations",
    "/api/ai/guidance",
    "/api/ai/predictions/churn",
    "/api/ai/predictions/success",
    "/api/ai/predictions/engagement",
    "/api/ai/predictions/intervention-time",
    "/api/ai/profile/analysis",
    "/api/ai/profile/suggestions",
    "/api/ai/profile/infer",
    "/api/ai/profile/generate-summary",
    "/api/ai/profile/optimize-ats",
    "/api/ai/intelligence",
    "/api/jobs/ai-recommendations",  # From jobs router
]

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def check_health() -> bool:
    """Check if backend is running"""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{BASE_URL}/api/health"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and "healthy" in result.stdout
    except Exception as e:
        return False

def get_openapi_spec() -> Dict:
    """Fetch OpenAPI spec from backend"""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{BASE_URL}/openapi.json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}
    except Exception as e:
        print_error(f"Failed to fetch OpenAPI spec: {e}")
        return {}

def test_endpoint_access(endpoint: str) -> Tuple[bool, int, str]:
    """Test if endpoint is accessible"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{BASE_URL}{endpoint}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        status_code = int(result.stdout.strip())
        
        # For AI endpoints, 404 means route not found
        # 403/401/503 means route exists but auth/service issues
        # 200 means it's working
        is_accessible = status_code != 404
        
        status_map = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            503: "Service Unavailable",
        }
        
        status_text = status_map.get(status_code, f"HTTP {status_code}")
        return is_accessible, status_code, status_text
    except Exception as e:
        return False, 0, str(e)

def main():
    print(f"\n{Colors.BOLD}Phase 2 AI Agents - Route Registration Validation{Colors.RESET}")
    print(f"Backend: {BASE_URL}")
    
    # Check if backend is running
    print_section("Checking Backend Status")
    if check_health():
        print_success("Backend is running and healthy")
    else:
        print_error("Backend is not running or not healthy")
        print_info("Please start the backend with: python3 -m uvicorn app.main:app --port 8000")
        sys.exit(1)
    
    # Fetch OpenAPI spec
    print_section("Validating OpenAPI Spec")
    spec = get_openapi_spec()
    if not spec:
        print_error("Failed to fetch OpenAPI spec")
        sys.exit(1)
    
    spec_paths = spec.get("paths", {})
    print_info(f"OpenAPI spec contains {len(spec_paths)} endpoints total")
    
    # Check AI endpoints in spec
    ai_paths = [p for p in spec_paths.keys() if "/ai" in p]
    print_success(f"Found {len(ai_paths)} AI-related endpoints in OpenAPI spec")
    
    # Validate each expected endpoint
    print_section("Validating Expected Endpoints")
    
    results = {
        "in_spec": [],
        "accessible": [],
        "working": [],
        "auth_issues": [],
        "missing": [],
        "errors": [],
    }
    
    for endpoint in EXPECTED_ENDPOINTS:
        # Check if in OpenAPI spec
        in_spec = endpoint in spec_paths
        
        # Check if accessible
        is_accessible, status_code, status_text = test_endpoint_access(endpoint)
        
        if not in_spec:
            print_error(f"{endpoint}")
            print_info(f"  Not in OpenAPI spec")
            results["missing"].append(endpoint)
        elif not is_accessible and status_code == 404:
            print_error(f"{endpoint}")
            print_info(f"  Route not found: {status_text}")
            results["missing"].append(endpoint)
        elif status_code == 200:
            print_success(f"{endpoint}")
            print_info(f"  Status: {status_text}")
            results["working"].append(endpoint)
        elif status_code in [401, 403, 503]:
            print_warning(f"{endpoint}")
            print_info(f"  Status: {status_text} (route exists, expected in dev)")
            results["auth_issues"].append(endpoint)
        else:
            print_warning(f"{endpoint}")
            print_info(f"  Status: {status_text}")
            results["errors"].append(endpoint)
        
        if in_spec:
            results["in_spec"].append(endpoint)
        if is_accessible:
            results["accessible"].append(endpoint)
    
    # Summary
    print_section("Validation Summary")
    
    total = len(EXPECTED_ENDPOINTS)
    in_spec_count = len(results["in_spec"])
    accessible_count = len(results["accessible"])
    working_count = len(results["working"])
    missing_count = len(results["missing"])
    auth_count = len(results["auth_issues"])
    
    print_info(f"Total Expected Endpoints: {total}")
    print_success(f"In OpenAPI Spec: {in_spec_count}/{total}")
    print_success(f"Accessible (not 404): {accessible_count}/{total}")
    
    if working_count > 0:
        print_success(f"Working (HTTP 200): {working_count}")
    if auth_count > 0:
        print_warning(f"Auth/Service Issues (expected in dev): {auth_count}")
    if missing_count > 0:
        print_error(f"Missing/Not Found: {missing_count}")
    
    # Overall result
    print("\n" + "=" * 60)
    if missing_count == 0 and accessible_count == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL ROUTES VALIDATED SUCCESSFULLY!{Colors.RESET}")
        print(f"{Colors.GREEN}All {total} AI agent endpoints are properly registered and accessible.{Colors.RESET}")
    elif in_spec_count == total and accessible_count >= total - 2:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ PHASE 2 AI ROUTES OPERATIONAL!{Colors.RESET}")
        print(f"{Colors.GREEN}All {total} routes are registered in OpenAPI spec.{Colors.RESET}")
        if auth_count > 0:
            print(f"{Colors.YELLOW}Note: {auth_count} endpoints showing auth/service issues (expected in dev without Firebase).{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ VALIDATION INCOMPLETE{Colors.RESET}")
        print(f"{Colors.RED}Missing: {missing_count} routes{Colors.RESET}")
    
    print("=" * 60 + "\n")
    
    return missing_count == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
