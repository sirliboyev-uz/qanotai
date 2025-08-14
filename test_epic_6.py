#!/usr/bin/env python3
"""
Epic 6: Content & Question Bank - Test Script
Tests all content management and question bank endpoints
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
    print(f"📚 TESTING: {title}")
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

def test_content_endpoints(token):
    """Test all content and question bank endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_header("Epic 6.1: Browse Question Topics")
    
    # Test browsing topics
    response = requests.get(f"{BASE_URL}/api/content/topics", headers=headers)
    print_result("GET /api/content/topics", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    topic_id = None
    if response.status_code == 200:
        topics_data = response.json()
        print(f"✅ Total Topics: {topics_data.get('total_count', 0)}")
        print(f"✅ Categories Available: {len(topics_data.get('categories', []))}")
        print(f"✅ Trending Topics: {len(topics_data.get('trending_topics', []))}")
        
        # Get first topic ID for detailed testing
        if topics_data.get('topics'):
            topic_id = topics_data['topics'][0]['id']
            print(f"✅ Sample Topic: {topics_data['topics'][0]['name']}")
    
    # Test topic filtering
    response = requests.get(f"{BASE_URL}/api/content/topics?category=family&difficulty=beginner", headers=headers)
    print_result("GET /api/content/topics (filtered)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test topic details
    if topic_id:
        response = requests.get(f"{BASE_URL}/api/content/topics/{topic_id}", headers=headers)
        print_result(f"GET /api/content/topics/{topic_id[:8]}...", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            detail_data = response.json()
            print(f"✅ Topic Details: {detail_data.get('topic', {}).get('name', 'N/A')}")
            print(f"✅ User Stats: {detail_data.get('user_stats', {}).get('is_favorite', False)}")
    
    print_header("Search Functionality")
    
    # Test search
    response = requests.get(f"{BASE_URL}/api/content/search?query=family&search_type=all", headers=headers)
    print_result("GET /api/content/search", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        search_data = response.json()
        print(f"✅ Topics Found: {search_data.get('total_topics', 0)}")
        print(f"✅ Questions Found: {search_data.get('total_questions', 0)}")
    
    print_header("Question Management")
    
    # Test getting questions
    response = requests.get(f"{BASE_URL}/api/content/questions?part=part_1&limit=5", headers=headers)
    print_result("GET /api/content/questions", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        questions_data = response.json()
        print(f"✅ Questions Retrieved: {questions_data.get('total_count', 0)}")
        if questions_data.get('questions'):
            sample_q = questions_data['questions'][0]
            print(f"✅ Sample Question: {sample_q.get('text', 'N/A')[:50]}...")
    
    print_header("Epic 6.1: Favorite Topics")
    
    # Test adding favorite topic
    if topic_id:
        favorite_data = {
            "topic_id": topic_id,
            "is_favorite": True,
            "interest_level": 4
        }
        response = requests.post(f"{BASE_URL}/api/content/favorites", json=favorite_data, headers=headers)
        print_result("POST /api/content/favorites", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test getting favorites
    response = requests.get(f"{BASE_URL}/api/content/favorites", headers=headers)
    print_result("GET /api/content/favorites", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        favorites_data = response.json()
        print(f"✅ Favorite Topics: {favorites_data.get('total_count', 0)}")
    
    print_header("Epic 6.2: Daily Challenge")
    
    # Test getting daily challenge
    response = requests.get(f"{BASE_URL}/api/content/daily-challenge", headers=headers)
    print_result("GET /api/content/daily-challenge", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    challenge_id = None
    if response.status_code == 200:
        challenge_data = response.json()
        challenge = challenge_data.get('challenge', {})
        challenge_id = challenge.get('id')
        print(f"✅ Today's Challenge: {challenge.get('title', 'N/A')}")
        print(f"✅ Theme: {challenge.get('theme', 'N/A')}")
        print(f"✅ Duration: {challenge.get('estimated_duration_minutes', 0)} minutes")
        print(f"✅ Questions: {len(challenge_data.get('questions', []))}")
    
    # Test starting daily challenge
    if challenge_id:
        start_data = {
            "challenge_id": challenge_id,
            "difficulty_preference": "intermediate"
        }
        response = requests.post(f"{BASE_URL}/api/content/daily-challenge/start", json=start_data, headers=headers)
        print_result("POST /api/content/daily-challenge/start", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # Test completing daily challenge
        complete_data = {
            "challenge_id": challenge_id,
            "responses": [
                {"question_id": "q1", "score": 7.5, "response_time": 30},
                {"question_id": "q2", "score": 8.0, "response_time": 45}
            ],
            "completion_time_minutes": 4
        }
        response = requests.post(f"{BASE_URL}/api/content/daily-challenge/complete", json=complete_data, headers=headers)
        print_result("POST /api/content/daily-challenge/complete", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            completion_data = response.json()
            print(f"✅ Overall Score: {completion_data.get('overall_score', 0)}")
            print(f"✅ Streak Count: {completion_data.get('streak_count', 0)}")
            print(f"✅ Badge Earned: {completion_data.get('badge_earned', False)}")
    
    print_header("Epic 6.3: Trending Topics")
    
    # Test getting trending topics
    response = requests.get(f"{BASE_URL}/api/content/trending", headers=headers)
    print_result("GET /api/content/trending", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        trending_data = response.json()
        print(f"✅ Trending Topics: {len(trending_data.get('trending', []))}")
        print(f"✅ Available Regions: {len(trending_data.get('regions', []))}")
        
        if trending_data.get('trending'):
            top_trend = trending_data['trending'][0]
            print(f"✅ Top Trending Score: {top_trend.get('trend_score', 0)}")
    
    # Test regional trending
    response = requests.get(f"{BASE_URL}/api/content/trending?period=weekly", headers=headers)
    print_result("GET /api/content/trending (weekly)", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("User Question Submission")
    
    # Test submitting a question
    submit_data = {
        "question_text": "What is your favorite family tradition?",
        "part": "part_1",
        "category": "family",
        "test_context": {
            "location": "Tashkent",
            "date": "2024-01-15"
        }
    }
    response = requests.post(f"{BASE_URL}/api/content/submit-question", json=submit_data, headers=headers)
    print_result("POST /api/content/submit-question", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        submission_data = response.json()
        print(f"✅ Submission ID: {submission_data.get('submission_id', 'N/A')[:8]}...")
        print(f"✅ Status: {submission_data.get('status', 'N/A')}")
        print(f"✅ Review Time: {submission_data.get('estimated_review_time', 'N/A')}")

def test_api_health():
    """Test API health"""
    print_header("API Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    response = requests.get(f"{BASE_URL}/")
    print_result("GET /", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_content_discovery():
    """Test content discovery and organization features"""
    print_header("Content Discovery Tests")
    
    # Get a token for testing
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing Topic Categories:")
    
    # Test different categories
    categories = ["family", "work_study", "technology", "travel"]
    for category in categories:
        response = requests.get(f"{BASE_URL}/api/content/topics?category={category}&per_page=2", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {category.title()}: {data.get('total_count', 0)} topics")
        else:
            print(f"   ❌ {category.title()}: Failed to fetch")
    
    print("\n🧪 Testing Difficulty Levels:")
    
    # Test different difficulty levels
    difficulties = ["beginner", "intermediate", "advanced"]
    for difficulty in difficulties:
        response = requests.get(f"{BASE_URL}/api/content/topics?difficulty={difficulty}&per_page=5", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {difficulty.title()}: {data.get('total_count', 0)} topics")
        else:
            print(f"   ❌ {difficulty.title()}: Failed to fetch")
    
    print("\n🧪 Testing Search Functionality:")
    
    # Test various search queries
    search_queries = ["family", "technology", "work", "travel"]
    for query in search_queries:
        response = requests.get(f"{BASE_URL}/api/content/search?query={query}&limit=3", headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_results = data.get('total_topics', 0) + data.get('total_questions', 0)
            print(f"   ✅ '{query}': {total_results} total results")
        else:
            print(f"   ❌ '{query}': Search failed")

def main():
    """Run all tests"""
    print("📚 Epic 6: Content & Question Bank - Full Test Suite")
    print("Testing all content management and question bank endpoints...")
    
    # Test API health
    test_api_health()
    
    # Get auth token
    token = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test all content endpoints
    test_content_endpoints(token)
    
    # Test content discovery features
    test_content_discovery()
    
    print_header("TEST SUMMARY")
    print("✅ Epic 6: Content & Question Bank endpoints tested")
    print("📚 Features tested:")
    print("   - Topic browsing and categorization")
    print("   - Question search and filtering")
    print("   - Favorite topics management")
    print("   - Daily challenge system")
    print("   - Trending topics tracking")
    print("   - User question submissions")
    print("   - Content discovery and organization")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Check the /docs endpoint to see all Epic 6 endpoints")

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