"""
Test Payme payment flow
"""
import asyncio
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_PHONE = "+998901234567"
TEST_USER_TOKEN = None  # Will be set after login

def test_create_payment():
    """Test creating a payment link"""
    print("\n🔄 Testing Payme payment creation...")
    
    # First, create a test user and get token
    print("1. Creating test user...")
    response = requests.post(
        f"{BASE_URL}/api/auth/phone-verify",
        json={
            "phone_number": TEST_USER_PHONE,
            "verification_code": "123456"  # Test code
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Got auth token")
        
        # Create payment for Standard plan
        print("\n2. Creating payment for Standard plan (49,000 UZS)...")
        response = requests.post(
            f"{BASE_URL}/api/payment/create-payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"subscription_plan": "standard"}
        )
        
        if response.status_code == 200:
            payment_data = response.json()
            print(f"✅ Payment created successfully!")
            print(f"   Order ID: {payment_data['order_id']}")
            print(f"   Amount: {payment_data['amount_uzs']:,} UZS")
            print(f"   Payment URL: {payment_data['payment_url']}")
            
            # Test webhook simulation
            print("\n3. Simulating Payme webhook...")
            test_webhook(payment_data['order_id'])
            
            # Check payment status
            print("\n4. Checking payment status...")
            response = requests.get(
                f"{BASE_URL}/api/payment/check-payment/{payment_data['order_id']}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Payment status: {status['status']}")
            
            return payment_data
        else:
            print(f"❌ Failed to create payment: {response.text}")
    else:
        print(f"❌ Failed to authenticate: {response.text}")
    
    return None

def test_webhook(order_id):
    """Simulate Payme webhook calls"""
    
    # Payme webhook methods to test
    methods = [
        {
            "method": "CheckPerformTransaction",
            "params": {
                "amount": 4900000,  # 49,000 UZS in tiyin
                "account": {
                    "order_id": order_id,
                    "user_id": "test_user"
                }
            }
        },
        {
            "method": "CreateTransaction",
            "params": {
                "id": f"test_transaction_{datetime.now().timestamp()}",
                "time": int(datetime.now().timestamp() * 1000),
                "amount": 4900000,
                "account": {
                    "order_id": order_id,
                    "user_id": "test_user"
                }
            }
        },
        {
            "method": "PerformTransaction",
            "params": {
                "id": f"test_transaction_{datetime.now().timestamp()}"
            }
        }
    ]
    
    for webhook_data in methods:
        webhook_data["id"] = 1
        webhook_data["jsonrpc"] = "2.0"
        
        response = requests.post(
            f"{BASE_URL}/api/payment/payme-webhook",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Basic UGF5Y29tOnRlc3Rfc2VjcmV0"  # Test credentials
            },
            json=webhook_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"   ✅ {webhook_data['method']}: Success")
            else:
                print(f"   ⚠️  {webhook_data['method']}: {result.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"   ❌ {webhook_data['method']}: HTTP {response.status_code}")

def test_payment_history():
    """Test getting payment history"""
    print("\n5. Testing payment history...")
    
    # Get token first
    response = requests.post(
        f"{BASE_URL}/api/auth/phone-verify",
        json={
            "phone_number": TEST_USER_PHONE,
            "verification_code": "123456"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/payment/payment-history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} payments")
            for payment in data['payments'][:3]:
                print(f"   - {payment.get('subscription_plan', 'N/A')}: {payment.get('amount_uzs', 0):,} UZS ({payment.get('status', 'unknown')})")
        else:
            print(f"❌ Failed to get history: {response.text}")

def main():
    """Run all payment tests"""
    print("=" * 50)
    print("🧪 PAYME PAYMENT INTEGRATION TEST")
    print("=" * 50)
    
    # Test payment creation
    payment = test_create_payment()
    
    # Test payment history
    test_payment_history()
    
    print("\n" + "=" * 50)
    print("✅ Payment integration test complete!")
    print("\nNext steps:")
    print("1. Register as Payme merchant at business.payme.uz")
    print("2. Get real merchant credentials")
    print("3. Update .env with real credentials")
    print("4. Test with Payme test cards")
    print("5. Submit for Payme approval")
    print("=" * 50)

if __name__ == "__main__":
    main()