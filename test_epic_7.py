#!/usr/bin/env python3
"""
Epic 7: Social & Community Features - Test Script
Tests all social features and community endpoints
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000"

# Test data
test_user = {
    "phone": "+998901234567",
    "otp": "123456"
}

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🎪 TESTING: {title}")
    print("="*60)

def print_result(endpoint, status_code, data=None):
    """Print test result"""
    status = "✅ PASS" if 200 <= status_code < 300 else "❌ FAIL"
    print(f"{status} {endpoint} - Status: {status_code}")
    if data and isinstance(data, dict):
        if 'error' in data:
            print(f"   Error: {data['error']}")
        elif len(str(data)) < 400:
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

def test_social_endpoints(token):
    """Test all social and community endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_header("Epic 7.1: Share Results - Score Cards")
    
    # Test creating a score card
    score_card_data = {
        "test_attempt_id": "test_123",
        "achievement_title": "Personal Best!",
        "card_template": "achievement",
        "privacy_level": "public",
        "show_detailed_scores": True
    }
    response = requests.post(f"{BASE_URL}/api/social/score-card", json=score_card_data, headers=headers)
    print_result("POST /api/social/score-card", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    score_card_id = None
    if response.status_code == 200:
        card_data = response.json()
        score_card_id = card_data.get('score_card', {}).get('id')
        print(f"✅ Score Card Created: {score_card_id[:8] if score_card_id else 'N/A'}...")
        print(f"✅ Overall Band: {card_data.get('score_card', {}).get('overall_band', 'N/A')}")
        print(f"✅ Image URL: {card_data.get('image_url', 'N/A')[:50]}...")
        print(f"✅ Share URLs: {len(card_data.get('share_urls', {}))}")
    
    # Test sharing a score card
    if score_card_id:
        share_data = {
            "score_card_id": score_card_id,
            "platforms": ["whatsapp", "instagram", "facebook"],
            "privacy_level": "public"
        }
        response = requests.post(f"{BASE_URL}/api/social/share", json=share_data, headers=headers)
        print_result("POST /api/social/share", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            share_result = response.json()
            print(f"✅ Platforms Shared: {len(share_result.get('shares', []))}")
            print(f"✅ Total Shares: {share_result.get('total_shares', 0)}")
    
    print_header("Epic 7.2: Leaderboards")
    
    # Test weekly leaderboard
    response = requests.get(f"{BASE_URL}/api/social/leaderboard?period=weekly&limit=10", headers=headers)
    print_result("GET /api/social/leaderboard (weekly)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        lb_data = response.json()
        leaderboard = lb_data.get('leaderboard', {})
        print(f"✅ Total Participants: {leaderboard.get('total_participants', 0)}")
        print(f"✅ Average Score: {leaderboard.get('average_score', 0):.1f}")
        print(f"✅ User Rank: {lb_data.get('user_rank', 'Not ranked')}")
        print(f"✅ Rank Change: {lb_data.get('rank_change', 'N/A')}")
    
    # Test monthly leaderboard
    response = requests.get(f"{BASE_URL}/api/social/leaderboard?period=monthly", headers=headers)
    print_result("GET /api/social/leaderboard (monthly)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test regional leaderboard
    response = requests.get(f"{BASE_URL}/api/social/leaderboard?country=Uzbekistan", headers=headers)
    print_result("GET /api/social/leaderboard (regional)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 7.3: Study Groups - Browse & Create")
    
    # Test browsing study groups
    response = requests.get(f"{BASE_URL}/api/social/study-groups?limit=5", headers=headers)
    print_result("GET /api/social/study-groups", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        groups_data = response.json()
        print(f"✅ Available Groups: {groups_data.get('total_count', 0)}")
        if groups_data.get('groups'):
            sample_group = groups_data['groups'][0]
            print(f"✅ Sample Group: {sample_group.get('name', 'N/A')}")
            print(f"✅ Members: {sample_group.get('member_count', 0)}")
    
    # Test creating a study group
    create_group_data = {
        "name": "Test IELTS Group",
        "description": "A test group for practicing IELTS speaking together!",
        "is_public": True,
        "target_band_score": 7.0,
        "focus_areas": ["fluency", "pronunciation"]
    }
    response = requests.post(f"{BASE_URL}/api/social/study-groups", json=create_group_data, headers=headers)
    print_result("POST /api/social/study-groups", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    group_id = None
    if response.status_code == 200:
        group_data = response.json()
        group = group_data.get('group', {})
        group_id = group.get('id')
        print(f"✅ Group Created: {group.get('name', 'N/A')}")
        print(f"✅ Group Code: {group.get('group_code', 'N/A')}")
        print(f"✅ User Role: {group_data.get('user_role', 'N/A')}")
    
    # Test group details
    if group_id:
        response = requests.get(f"{BASE_URL}/api/social/study-groups/{group_id}", headers=headers)
        print_result(f"GET /api/social/study-groups/{group_id[:8]}...", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            detail_data = response.json()
            print(f"✅ Members: {len(detail_data.get('members', []))}")
            print(f"✅ Recent Messages: {len(detail_data.get('recent_messages', []))}")
            print(f"✅ Active Challenges: {len(detail_data.get('active_challenges', []))}")
    
    print_header("Epic 7.3: Study Groups - Messaging")
    
    # Test sending a group message
    if group_id:
        message_data = {
            "content": "Hello everyone! Looking forward to practicing together! 🎯",
            "message_type": "text"
        }
        response = requests.post(f"{BASE_URL}/api/social/study-groups/{group_id}/messages", json=message_data, headers=headers)
        print_result("POST /api/social/study-groups/.../messages", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # Test getting group messages
        response = requests.get(f"{BASE_URL}/api/social/study-groups/{group_id}/messages?limit=10", headers=headers)
        print_result("GET /api/social/study-groups/.../messages", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            messages_data = response.json()
            print(f"✅ Total Messages: {messages_data.get('total_count', 0)}")
            if messages_data.get('messages'):
                latest_msg = messages_data['messages'][0]
                print(f"✅ Latest Message: {latest_msg.get('content', 'N/A')[:30]}...")
    
    print_header("Social Settings & Privacy")
    
    # Test getting social settings
    response = requests.get(f"{BASE_URL}/api/social/settings", headers=headers)
    print_result("GET /api/social/settings", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test updating social settings
    settings_data = {
        "participate_in_leaderboards": True,
        "show_anonymous": False,
        "auto_share_achievements": True,
        "default_privacy_level": "public"
    }
    response = requests.put(f"{BASE_URL}/api/social/settings", json=settings_data, headers=headers)
    print_result("PUT /api/social/settings", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Social Statistics")
    
    # Test getting social stats
    response = requests.get(f"{BASE_URL}/api/social/stats", headers=headers)
    print_result("GET /api/social/stats", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        stats_data = response.json()
        print(f"✅ Total Shares: {stats_data.get('total_shares', 0)}")
        print(f"✅ Leaderboard Rank: {stats_data.get('leaderboard_rank', 'Unranked')}")
        print(f"✅ Study Groups: {stats_data.get('study_groups_count', 0)}")
        print(f"✅ Social Score: {stats_data.get('social_score', 0):.1f}")
    
    # Test getting user's study groups
    response = requests.get(f"{BASE_URL}/api/social/my-groups", headers=headers)
    print_result("GET /api/social/my-groups", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        my_groups_data = response.json()
        print(f"✅ My Groups Count: {my_groups_data.get('total_count', 0)}")

def test_api_health():
    """Test API health"""
    print_header("API Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    response = requests.get(f"{BASE_URL}/")
    print_result("GET /", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_social_workflows():
    """Test complete social workflows"""
    print_header("Social Workflow Tests")
    
    # Get a token for testing
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing Complete Score Sharing Workflow:")
    
    # 1. Create score card
    score_card_data = {
        "test_attempt_id": "workflow_test_123",
        "achievement_title": "Workflow Test Achievement",
        "privacy_level": "public"
    }
    response = requests.post(f"{BASE_URL}/api/social/score-card", json=score_card_data, headers=headers)
    if response.status_code == 200:
        card_data = response.json()
        score_card_id = card_data['score_card']['id']
        print(f"   ✅ Step 1: Score card created ({score_card_id[:8]}...)")
        
        # 2. Share to multiple platforms
        share_data = {
            "score_card_id": score_card_id,
            "platforms": ["whatsapp", "facebook", "telegram"]
        }
        response = requests.post(f"{BASE_URL}/api/social/share", json=share_data, headers=headers)
        if response.status_code == 200:
            print("   ✅ Step 2: Shared to 3 platforms successfully")
        else:
            print("   ❌ Step 2: Sharing failed")
    else:
        print("   ❌ Step 1: Score card creation failed")
    
    print("\n🧪 Testing Study Group Complete Workflow:")
    
    # 1. Browse available groups
    response = requests.get(f"{BASE_URL}/api/social/study-groups", headers=headers)
    if response.status_code == 200:
        print("   ✅ Step 1: Browsed available groups")
        
        # 2. Create new group
        create_data = {
            "name": "Workflow Test Group",
            "description": "Testing complete workflow",
            "target_band_score": 7.5
        }
        response = requests.post(f"{BASE_URL}/api/social/study-groups", json=create_data, headers=headers)
        if response.status_code == 200:
            group_data = response.json()
            group_id = group_data['group']['id']
            print(f"   ✅ Step 2: Created group ({group_id[:8]}...)")
            
            # 3. Send welcome message
            message_data = {
                "content": "Welcome to our workflow test group! 🚀"
            }
            response = requests.post(f"{BASE_URL}/api/social/study-groups/{group_id}/messages", json=message_data, headers=headers)
            if response.status_code == 200:
                print("   ✅ Step 3: Sent welcome message")
                
                # 4. Get group details
                response = requests.get(f"{BASE_URL}/api/social/study-groups/{group_id}", headers=headers)
                if response.status_code == 200:
                    print("   ✅ Step 4: Retrieved group details")
                    print("   🎉 Complete workflow successful!")
                else:
                    print("   ❌ Step 4: Failed to get group details")
            else:
                print("   ❌ Step 3: Failed to send message")
        else:
            print("   ❌ Step 2: Failed to create group")
    else:
        print("   ❌ Step 1: Failed to browse groups")

def main():
    """Run all tests"""
    print("🎪 Epic 7: Social & Community Features - Full Test Suite")
    print("Testing all social features and community endpoints...")
    
    # Test API health
    test_api_health()
    
    # Get auth token
    token = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test all social endpoints
    test_social_endpoints(token)
    
    # Test complete workflows
    test_social_workflows()
    
    print_header("TEST SUMMARY")
    print("✅ Epic 7: Social & Community Features endpoints tested")
    print("🎪 Features tested:")
    print("   - Score card creation and social sharing")
    print("   - Leaderboards (weekly, monthly, regional)")
    print("   - Study group creation and management")
    print("   - Group messaging and communication")
    print("   - Social settings and privacy controls")
    print("   - Social statistics and engagement tracking")
    print("   - Complete social interaction workflows")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Check the /docs endpoint to see all Epic 7 endpoints")

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