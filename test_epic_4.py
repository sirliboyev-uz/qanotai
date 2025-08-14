#!/usr/bin/env python3
"""
Epic 4: Progress Tracking - Test Script
Tests all progress tracking endpoints
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

# Test data
test_user = {
    "phone": "+998901234567",
    "otp": "123456"
}

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🧪 TESTING: {title}")
    print("="*60)

def print_result(endpoint, status_code, data=None):
    """Print test result"""
    status = "✅ PASS" if 200 <= status_code < 300 else "❌ FAIL"
    print(f"{status} {endpoint} - Status: {status_code}")
    if data and isinstance(data, dict):
        if 'error' in data:
            print(f"   Error: {data['error']}")
        elif len(str(data)) < 200:
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"   Response: {type(data).__name__} with {len(data)} items" if hasattr(data, '__len__') else "Large response")
    print()

def authenticate():
    """Get auth token"""
    print_header("Authentication")
    
    # Send OTP
    response = requests.post(f"{BASE_URL}/api/v1/auth/phone/send-otp", json={
        "phone_number": test_user["phone"]
    })
    print_result("Send OTP", response.status_code, response.json() if response.status_code != 200 else {"message": "OTP sent"})
    
    # Verify OTP
    response = requests.post(f"{BASE_URL}/api/v1/auth/phone/verify", json={
        "phone_number": test_user["phone"],
        "verification_code": test_user["otp"]
    })
    
    if response.status_code == 200:
        token_data = response.json()
        print_result("Verify OTP", response.status_code, {"token": "received", "user": token_data.get("user", {}).get("phone")})
        return token_data["access_token"]
    else:
        print_result("Verify OTP", response.status_code, response.json())
        return None

def test_progress_endpoints(token):
    """Test all progress tracking endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_header("Epic 4.1: Progress Dashboard")
    
    # Test dashboard endpoint
    response = requests.get(f"{BASE_URL}/api/progress/dashboard", headers=headers)
    print_result("GET /api/progress/dashboard", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 4.2: Test History")
    
    # Test history endpoint
    response = requests.get(f"{BASE_URL}/api/progress/history", headers=headers)
    print_result("GET /api/progress/history", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test history with pagination
    response = requests.get(f"{BASE_URL}/api/progress/history?page=1&per_page=5", headers=headers)
    print_result("GET /api/progress/history (paginated)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 4.3: Performance Analytics")
    
    # Test analytics endpoint
    response = requests.get(f"{BASE_URL}/api/progress/analytics", headers=headers)
    print_result("GET /api/progress/analytics", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test analytics with custom period
    response = requests.get(f"{BASE_URL}/api/progress/analytics?period_days=7", headers=headers)
    print_result("GET /api/progress/analytics (7 days)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 4.4: Achievement Badges")
    
    # Test badges endpoint
    response = requests.get(f"{BASE_URL}/api/progress/badges", headers=headers)
    print_result("GET /api/progress/badges", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Goal Setting & Tracking")
    
    # Test set goal
    goal_data = {
        "target_band_score": 7.5,
        "target_date": (date.today() + timedelta(days=90)).isoformat(),
        "reason": "University application",
        "reward": "Celebrate with family dinner"
    }
    response = requests.post(f"{BASE_URL}/api/progress/goal", json=goal_data, headers=headers)
    print_result("POST /api/progress/goal", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test practice streak
    response = requests.get(f"{BASE_URL}/api/progress/streak", headers=headers)
    print_result("GET /api/progress/streak", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Simulate Test Completion")
    
    # Create a mock test attempt
    test_attempt = {
        "user_id": "user_123",  # Will be overridden by endpoint
        "attempt_id": f"test_attempt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "test_date": datetime.utcnow().isoformat(),
        "test_mode": "full",
        "target_band_score": 7.0,
        "overall_band": 6.5,
        "fluency_coherence": 6.5,
        "lexical_resource": 6.0,
        "grammatical_range_accuracy": 6.5,
        "pronunciation": 7.0,
        "part1_score": 6.5,
        "part2_score": 6.0,
        "part3_score": 6.5,
        "total_questions": 15,
        "completion_percentage": 100.0,
        "test_duration_minutes": 14,
        "word_count_total": 450,
        "unique_words_used": 180,
        "filler_words_count": 8,
        "hesitations_count": 12,
        "speaking_rate_wpm": 145.0,
        "is_completed": True,
        "notes": "Good performance overall, some hesitations in Part 2"
    }
    
    response = requests.post(f"{BASE_URL}/api/progress/test-completed", json=test_attempt, headers=headers)
    print_result("POST /api/progress/test-completed", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Check dashboard again after test completion
    print_header("Dashboard After Test Completion")
    response = requests.get(f"{BASE_URL}/api/progress/dashboard", headers=headers)
    if response.status_code == 200:
        data = response.json()
        metrics = data.get('metrics', {})
        print(f"✅ Current Band: {metrics.get('current_band', 'N/A')}")
        print(f"✅ Target Band: {metrics.get('target_band', 'N/A')}")
        print(f"✅ Total Tests: {metrics.get('total_tests', 'N/A')}")
        print(f"✅ Current Streak: {metrics.get('current_streak', 'N/A')}")
        print(f"✅ Badges Count: {len(data.get('badges', []))}")

def test_api_health():
    """Test API health"""
    print_header("API Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    response = requests.get(f"{BASE_URL}/")
    print_result("GET /", response.status_code, response.json() if response.status_code == 200 else response.text)

def main():
    """Run all tests"""
    print("🚀 Epic 4: Progress Tracking - Full Test Suite")
    print("Testing all progress tracking endpoints...")
    
    # Test API health
    test_api_health()
    
    # Get auth token
    token = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test all progress endpoints
    test_progress_endpoints(token)
    
    print_header("TEST SUMMARY")
    print("✅ Epic 4: Progress Tracking endpoints tested")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Check the /docs endpoint to see all Epic 4 endpoints")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:8000")
        print("💡 Run: cd backend && python app/main_full.py")
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")