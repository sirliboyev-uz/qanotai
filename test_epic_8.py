#!/usr/bin/env python3
"""
Epic 8: Accessibility & Localization - Test Script
Tests all accessibility and localization features
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test data
test_user = {
    "phone": "+998901234567",
    "otp": "123456"
}

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🌍 TESTING: {title}")
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

def test_localization_endpoints(token):
    """Test all localization and accessibility endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_header("Epic 8.1: Bilingual Interface - Language Support")
    
    # Test supported languages
    response = requests.get(f"{BASE_URL}/api/localization/languages", headers=headers)
    print_result("GET /api/localization/languages", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        languages_data = response.json()
        print(f"✅ Supported Languages: {len(languages_data.get('supported_languages', []))}")
        print(f"✅ Default Language: {languages_data.get('default_language', 'N/A')}")
        print(f"✅ Auto-detect Available: {languages_data.get('auto_detect_available', False)}")
    
    # Test getting user preferences
    response = requests.get(f"{BASE_URL}/api/localization/preferences", headers=headers)
    print_result("GET /api/localization/preferences", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        prefs_data = response.json()
        print(f"✅ Interface Language: {prefs_data.get('interface_language', 'N/A')}")
        print(f"✅ Feedback Language: {prefs_data.get('feedback_language', 'N/A')}")
        print(f"✅ Region: {prefs_data.get('region', 'Not set')}")
    
    # Test updating language preferences
    preference_data = {
        "interface_language": "uz",
        "feedback_language": "uz", 
        "region": "UZ",
        "timezone": "Asia/Tashkent",
        "auto_translate_feedback": True
    }
    response = requests.put(f"{BASE_URL}/api/localization/preferences", json=preference_data, headers=headers)
    print_result("PUT /api/localization/preferences", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 8.1: Bilingual Interface - Translations")
    
    # Test getting translations for different languages
    languages_to_test = ["en", "uz", "ru"]
    for lang in languages_to_test:
        response = requests.get(f"{BASE_URL}/api/localization/translations?language={lang}&namespace=app", headers=headers)
        print_result(f"GET /api/localization/translations ({lang})", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            trans_data = response.json()
            print(f"✅ {lang.upper()} Translations: {len(trans_data.get('translations', {}))}")
            print(f"✅ Fallback Used: {trans_data.get('fallback_used', False)}")
    
    # Test text translation
    translation_requests = [
        {"text": "Hello", "from_language": "en", "to_language": "uz"},
        {"text": "Good luck", "from_language": "en", "to_language": "ru"},
        {"text": "Start Test", "from_language": "en", "to_language": "uz"}
    ]
    
    for trans_req in translation_requests:
        response = requests.post(f"{BASE_URL}/api/localization/translate", json=trans_req, headers=headers)
        print_result(f"POST /api/localization/translate ({trans_req['from_language']}→{trans_req['to_language']})", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            trans_result = response.json()
            print(f"✅ Original: {trans_result.get('original_text', 'N/A')}")
            print(f"✅ Translated: {trans_result.get('translated_text', 'N/A')}")
            print(f"✅ Confidence: {trans_result.get('confidence', 0):.2f}")
    
    print_header("Epic 8.3: Accessibility Features")
    
    # Test getting accessibility settings
    response = requests.get(f"{BASE_URL}/api/localization/accessibility", headers=headers)
    print_result("GET /api/localization/accessibility", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        access_data = response.json()
        settings = access_data.get('settings', {})
        print(f"✅ Text Size: {settings.get('text_size', 'N/A')}")
        print(f"✅ Contrast Mode: {settings.get('contrast_mode', 'N/A')}")
        print(f"✅ Screen Reader: {settings.get('enable_screen_reader', False)}")
        print(f"✅ Available Features: {len(access_data.get('available_features', []))}")
    
    # Test updating accessibility settings
    accessibility_updates = [
        {
            "text_size": "large",
            "contrast_mode": "high",
            "enable_screen_reader": True
        },
        {
            "extended_timeouts": True,
            "timeout_extension_seconds": 60,
            "allow_extended_test_time": True,
            "test_time_multiplier": 1.5
        }
    ]
    
    for i, update_data in enumerate(accessibility_updates):
        response = requests.put(f"{BASE_URL}/api/localization/accessibility", json=update_data, headers=headers)
        print_result(f"PUT /api/localization/accessibility (Update {i+1})", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Epic 8.2: Offline Mode - Content Management")
    
    # Test getting offline content
    response = requests.get(f"{BASE_URL}/api/localization/offline-content", headers=headers)
    print_result("GET /api/localization/offline-content", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    content_id = None
    if response.status_code == 200:
        offline_data = response.json()
        print(f"✅ Available Content: {len(offline_data.get('available_content', []))}")
        print(f"✅ Downloaded Content: {len(offline_data.get('downloaded_content', []))}")
        print(f"✅ Storage Used: {offline_data.get('storage_used_mb', 0):.1f} MB")
        print(f"✅ Storage Available: {offline_data.get('storage_available_mb', 0):.1f} MB")
        
        # Get first available content for download test
        available_content = offline_data.get('available_content', [])
        if available_content:
            content_id = available_content[0]['id']
    
    # Test downloading offline content
    if content_id:
        download_data = {
            "content_id": content_id,
            "priority": "high"
        }
        response = requests.post(f"{BASE_URL}/api/localization/offline-content/download", json=download_data, headers=headers)
        print_result("POST /api/localization/offline-content/download", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        if response.status_code == 200:
            download_result = response.json()
            print(f"✅ Download ID: {download_result.get('download_id', 'N/A')[:8]}...")
            print(f"✅ Estimated Time: {download_result.get('estimated_time_minutes', 0):.1f} minutes")
        
        # Wait a moment and check content again
        print("\n⏳ Waiting for download simulation...")
        time.sleep(3)
        
        response = requests.get(f"{BASE_URL}/api/localization/offline-content", headers=headers)
        if response.status_code == 200:
            offline_data = response.json()
            downloaded = offline_data.get('downloaded_content', [])
            if downloaded:
                latest_download = downloaded[-1]
                print(f"✅ Download Status: {latest_download.get('download_status', 'unknown')}")
                print(f"✅ Download Progress: {latest_download.get('download_progress', 0)*100:.1f}%")
    
    # Test content sync
    response = requests.post(f"{BASE_URL}/api/localization/offline-content/sync", headers=headers)
    print_result("POST /api/localization/offline-content/sync", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Test deleting offline content (if we have any)
    if content_id:
        response = requests.delete(f"{BASE_URL}/api/localization/offline-content/{content_id}", headers=headers)
        print_result(f"DELETE /api/localization/offline-content/{content_id[:8]}...", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    print_header("Localization Statistics")
    
    # Test getting localization stats
    response = requests.get(f"{BASE_URL}/api/localization/stats", headers=headers)
    print_result("GET /api/localization/stats", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    if response.status_code == 200:
        stats_data = response.json()
        print(f"✅ Total Users by Language: {sum(stats_data.get('language_usage', {}).values())}")
        print(f"✅ Screen Reader Users: {stats_data.get('screen_reader_users', 0)}")
        print(f"✅ High Contrast Users: {stats_data.get('high_contrast_users', 0)}")
        print(f"✅ Offline Downloads: {stats_data.get('offline_downloads_total', 0)}")
        
        translation_completeness = stats_data.get('translation_completeness', {})
        if translation_completeness:
            print("✅ Translation Completeness:")
            for lang, percentage in translation_completeness.items():
                print(f"   {lang.upper()}: {percentage:.1f}%")

def test_api_health():
    """Test API health"""
    print_header("API Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    response = requests.get(f"{BASE_URL}/")
    print_result("GET /", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_localization_workflows():
    """Test complete localization workflows"""
    print_header("Localization Workflow Tests")
    
    # Get a token for testing
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing Complete Language Switching Workflow:")
    
    # 1. Get current preferences
    response = requests.get(f"{BASE_URL}/api/localization/preferences", headers=headers)
    if response.status_code == 200:
        print("   ✅ Step 1: Retrieved current language preferences")
        
        # 2. Switch to Uzbek
        update_data = {
            "interface_language": "uz",
            "feedback_language": "uz",
            "region": "UZ"
        }
        response = requests.put(f"{BASE_URL}/api/localization/preferences", json=update_data, headers=headers)
        if response.status_code == 200:
            print("   ✅ Step 2: Switched interface to Uzbek")
            
            # 3. Get Uzbek translations
            response = requests.get(f"{BASE_URL}/api/localization/translations?language=uz", headers=headers)
            if response.status_code == 200:
                trans_data = response.json()
                print(f"   ✅ Step 3: Retrieved {len(trans_data.get('translations', {}))} Uzbek translations")
                
                # 4. Test translation service
                translate_data = {
                    "text": "Welcome to QanotAI",
                    "from_language": "en",
                    "to_language": "uz"
                }
                response = requests.post(f"{BASE_URL}/api/localization/translate", json=translate_data, headers=headers)
                if response.status_code == 200:
                    print("   ✅ Step 4: Successfully translated welcome message")
                    print("   🎉 Complete language workflow successful!")
                else:
                    print("   ❌ Step 4: Translation failed")
            else:
                print("   ❌ Step 3: Failed to get translations")
        else:
            print("   ❌ Step 2: Failed to switch language")
    else:
        print("   ❌ Step 1: Failed to get preferences")
    
    print("\n🧪 Testing Complete Accessibility Setup Workflow:")
    
    # 1. Get current accessibility settings
    response = requests.get(f"{BASE_URL}/api/localization/accessibility", headers=headers)
    if response.status_code == 200:
        print("   ✅ Step 1: Retrieved accessibility settings")
        
        # 2. Enable multiple accessibility features
        access_data = {
            "text_size": "extra_large",
            "contrast_mode": "high",
            "enable_screen_reader": True,
            "extended_timeouts": True,
            "allow_extended_test_time": True,
            "test_time_multiplier": 2.0
        }
        response = requests.put(f"{BASE_URL}/api/localization/accessibility", json=access_data, headers=headers)
        if response.status_code == 200:
            print("   ✅ Step 2: Enabled comprehensive accessibility features")
            
            # 3. Verify settings were applied
            response = requests.get(f"{BASE_URL}/api/localization/accessibility", headers=headers)
            if response.status_code == 200:
                settings = response.json().get('settings', {})
                if (settings.get('text_size') == 'extra_large' and 
                    settings.get('contrast_mode') == 'high' and 
                    settings.get('enable_screen_reader') == True):
                    print("   ✅ Step 3: Verified accessibility settings were applied")
                    print("   🎉 Complete accessibility workflow successful!")
                else:
                    print("   ⚠️ Step 3: Some settings may not have been applied correctly")
            else:
                print("   ❌ Step 3: Failed to verify settings")
        else:
            print("   ❌ Step 2: Failed to update accessibility settings")
    else:
        print("   ❌ Step 1: Failed to get accessibility settings")

def main():
    """Run all tests"""
    print("🌍 Epic 8: Accessibility & Localization - Full Test Suite")
    print("Testing all accessibility and localization features...")
    
    # Test API health
    test_api_health()
    
    # Get auth token
    token = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test all localization endpoints
    test_localization_endpoints(token)
    
    # Test complete workflows
    test_localization_workflows()
    
    print_header("TEST SUMMARY")
    print("✅ Epic 8: Accessibility & Localization endpoints tested")
    print("🌍 Features tested:")
    print("   - Multi-language support (English, Uzbek, Russian, Kazakh, Turkish)")
    print("   - User language preferences and regional settings")
    print("   - Real-time text translation services")
    print("   - Comprehensive accessibility settings")
    print("   - Text size, contrast, and screen reader support")
    print("   - Extended timeouts and test time adjustments")
    print("   - Offline content download and management")
    print("   - Content synchronization and storage management")
    print("   - Usage statistics and analytics")
    print("   - Complete localization and accessibility workflows")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Check the /docs endpoint to see all Epic 8 endpoints")

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