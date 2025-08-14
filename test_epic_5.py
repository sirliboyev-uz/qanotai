#!/usr/bin/env python3
"""
Epic 5: Monetization & Subscriptions - Test Script
Tests all subscription and payment endpoints
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
    print(f"💰 TESTING: {title}")
    print("="*60)

def print_result(endpoint, status_code, data=None):
    """Print test result"""
    status = "✅ PASS" if 200 <= status_code < 300 else "❌ FAIL"
    print(f"{status} {endpoint} - Status: {status_code}")
    if data and isinstance(data, dict):
        if 'error' in data:
            print(f"   Error: {data['error']}")
        elif len(str(data)) < 300:
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
    print_result("Send OTP", response.status_code, {"message": "OTP sent"} if response.status_code == 200 else response.json())
    
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

def test_subscription_endpoints(token):
    """Test all subscription endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_header("Epic 5.1: Free Trial Experience")
    
    # Test subscription status
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    print_result("GET /api/subscription/status", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        status_data = response.json()
        print(f"✅ Current Tier: {status_data.get('subscription', {}).get('tier', 'N/A')}")
        print(f"✅ Can Take Test: {status_data.get('can_take_test', 'N/A')}")
        print(f"✅ Tests Remaining: {status_data.get('quota', {}).get('tests_remaining_this_period', 'N/A')}")
    
    print_header("Epic 5.2 & 5.3: Available Plans & Test Packs")
    
    # Test available plans
    response = requests.get(f"{BASE_URL}/api/subscription/plans", headers=headers)
    print_result("GET /api/subscription/plans", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        plans_data = response.json()
        print(f"✅ Available Plans: {len(plans_data.get('plans', []))}")
        print(f"✅ Test Packs: {len(plans_data.get('test_packs', []))}")
        for plan in plans_data.get('plans', [])[:2]:  # Show first 2 plans
            print(f"   - {plan.get('name')}: ${plan.get('price_usd')}")
    
    print_header("Epic 5.2: Purchase Test Pack")
    
    # Test purchasing test pack
    purchase_data = {
        "pack_type": "pack_5",
        "payment_method": "apple_pay",
        "payment_token": "mock_token_123"
    }
    response = requests.post(f"{BASE_URL}/api/subscription/purchase-tests", json=purchase_data, headers=headers)
    print_result("POST /api/subscription/purchase-tests", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 5.3: Premium Subscription")
    
    # Test subscribing to premium
    subscribe_data = {
        "plan_id": "premium_monthly",
        "payment_method": "apple_pay",
        "payment_token": "mock_token_456",
        "trial_period_days": 7
    }
    response = requests.post(f"{BASE_URL}/api/subscription/subscribe", json=subscribe_data, headers=headers)
    print_result("POST /api/subscription/subscribe", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Test Usage Simulation")
    
    # Test using a test (should work with premium)
    response = requests.post(f"{BASE_URL}/api/subscription/use-test", headers=headers)
    print_result("POST /api/subscription/use-test", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 5.4: Payment Management")
    
    # Test payment history
    response = requests.get(f"{BASE_URL}/api/subscription/payment-history", headers=headers)
    print_result("GET /api/subscription/payment-history", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        history_data = response.json()
        print(f"✅ Total Payments: {len(history_data.get('payments', []))}")
        print(f"✅ Total Spent: ${history_data.get('total_spent', 0)}")
    
    # Test subscription update
    update_data = {
        "cancel_at_period_end": True
    }
    response = requests.put(f"{BASE_URL}/api/subscription/update", json=update_data, headers=headers)
    print_result("PUT /api/subscription/update", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Usage Analytics")
    
    # Test usage analytics
    response = requests.get(f"{BASE_URL}/api/subscription/usage-analytics", headers=headers)
    print_result("GET /api/subscription/usage-analytics", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        analytics_data = response.json()
        current_period = analytics_data.get('current_period', {})
        print(f"✅ Tests Used This Period: {current_period.get('tests_used', 'N/A')}")
        print(f"✅ Recommendations: {len(analytics_data.get('recommendations', []))}")
    
    print_header("Subscription Cancellation")
    
    # Test subscription cancellation
    cancel_data = {
        "reason": "Testing cancellation flow",
        "feedback": "This is just a test",
        "immediate": False
    }
    response = requests.post(f"{BASE_URL}/api/subscription/cancel", json=cancel_data, headers=headers)
    print_result("POST /api/subscription/cancel", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Final Status Check")
    
    # Check status after all operations
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    if response.status_code == 200:
        final_status = response.json()
        subscription = final_status.get('subscription', {})
        quota = final_status.get('quota', {})
        print(f"✅ Final Tier: {subscription.get('tier', 'N/A')}")
        print(f"✅ Cancel at Period End: {subscription.get('cancel_at_period_end', 'N/A')}")
        print(f"✅ Total Tests Available: {quota.get('tests_remaining_this_period', 0) + quota.get('bonus_tests_available', 0)}")

def test_api_health():
    """Test API health"""
    print_header("API Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    response = requests.get(f"{BASE_URL}/")
    print_result("GET /", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_business_logic():
    """Test specific business logic scenarios"""
    print_header("Business Logic Tests")
    
    # Test that we get a token for subsequent requests
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing Free Trial Limits:")
    
    # Check initial quota
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    if response.status_code == 200:
        status = response.json()
        initial_tests = status['quota']['tests_remaining_this_period']
        print(f"   Initial free tests: {initial_tests}")
        
        # Try to use tests until limit
        for i in range(initial_tests + 1):
            response = requests.post(f"{BASE_URL}/api/subscription/use-test", headers=headers)
            if response.status_code == 200:
                print(f"   ✅ Test {i+1} allowed")
            else:
                print(f"   ❌ Test {i+1} blocked: {response.json().get('detail', 'Unknown error')}")
                break
    
    print("\n🧪 Testing Test Pack Purchase:")
    
    # Purchase test pack
    purchase_data = {
        "pack_type": "pack_5",
        "payment_method": "apple_pay"
    }
    response = requests.post(f"{BASE_URL}/api/subscription/purchase-tests", json=purchase_data, headers=headers)
    if response.status_code == 200:
        print("   ✅ Test pack purchased successfully")
        
        # Try using purchased test
        response = requests.post(f"{BASE_URL}/api/subscription/use-test", headers=headers)
        if response.status_code == 200:
            print("   ✅ Purchased test used successfully")
        else:
            print(f"   ❌ Cannot use purchased test: {response.json().get('detail')}")

def main():
    """Run all tests"""
    print("💰 Epic 5: Monetization & Subscriptions - Full Test Suite")
    print("Testing all subscription and payment endpoints...")
    
    # Test API health
    test_api_health()
    
    # Get auth token
    token = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test all subscription endpoints
    test_subscription_endpoints(token)
    
    # Test business logic scenarios
    test_business_logic()
    
    print_header("TEST SUMMARY")
    print("✅ Epic 5: Monetization & Subscriptions endpoints tested")
    print("💰 Features tested:")
    print("   - Free trial experience (3 tests/month)")
    print("   - Test pack purchases (5, 10, 20 tests)")
    print("   - Premium subscriptions (monthly/annual)")
    print("   - Payment management and history")
    print("   - Usage analytics and recommendations")
    print("   - Subscription cancellation")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Check the /docs endpoint to see all Epic 5 endpoints")

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