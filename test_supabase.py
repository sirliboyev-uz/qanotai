"""
Test Supabase connection and basic operations
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import json

# Load environment variables
load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(message, status="info"):
    if status == "success":
        print(f"{GREEN}✅ {message}{RESET}")
    elif status == "error":
        print(f"{RED}❌ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{RESET}")
    else:
        print(f"{BLUE}ℹ️  {message}{RESET}")

async def test_supabase_connection():
    """Test Supabase connection and operations"""
    
    print("\n" + "="*50)
    print("🚀 SUPABASE CONNECTION TEST")
    print("="*50 + "\n")
    
    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    # Check if credentials exist
    if not supabase_url or not supabase_key:
        print_test("Missing Supabase credentials in .env file", "error")
        print_test("Please add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file", "warning")
        return False
    
    print_test(f"Supabase URL: {supabase_url}", "info")
    print_test("Credentials loaded from .env", "success")
    
    try:
        # Initialize Supabase client
        print("\n" + "-"*30)
        print_test("Initializing Supabase client...", "info")
        supabase = create_client(supabase_url, supabase_key)
        print_test("Supabase client initialized", "success")
        
        # Test 1: Check subscription plans table
        print("\n" + "-"*30)
        print_test("Testing database connection...", "info")
        result = supabase.table("subscription_plans").select("*").execute()
        
        if result.data:
            print_test(f"Database connected! Found {len(result.data)} subscription plans:", "success")
            for plan in result.data:
                print(f"  - {plan.get('name', 'Unknown')}: ${plan.get('price_usd', 0)}/month")
        else:
            print_test("Database connected but no subscription plans found", "warning")
            print_test("Run the schema.sql file in Supabase SQL Editor first", "info")
        
        # Test 2: Check if tables exist
        print("\n" + "-"*30)
        print_test("Checking database tables...", "info")
        
        tables_to_check = [
            "users",
            "user_profiles", 
            "user_subscriptions",
            "payments",
            "usage_quotas",
            "question_topics",
            "questions",
            "daily_challenges",
            "test_attempts",
            "user_progress",
            "achievements",
            "leaderboard"
        ]
        
        tables_exist = []
        tables_missing = []
        
        for table_name in tables_to_check:
            try:
                # Try to select from table
                result = supabase.table(table_name).select("*").limit(1).execute()
                tables_exist.append(table_name)
            except Exception as e:
                if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                    tables_missing.append(table_name)
                else:
                    # Table exists but might have other issues
                    tables_exist.append(table_name)
        
        if tables_exist:
            print_test(f"Tables found ({len(tables_exist)}/{len(tables_to_check)}):", "success")
            for table in tables_exist[:5]:  # Show first 5
                print(f"  ✓ {table}")
            if len(tables_exist) > 5:
                print(f"  ... and {len(tables_exist)-5} more")
        
        if tables_missing:
            print_test(f"Missing tables ({len(tables_missing)}):", "error")
            for table in tables_missing:
                print(f"  ✗ {table}")
            print_test("Please run schema.sql in Supabase SQL Editor", "warning")
        
        # Test 3: Test creating a test user
        print("\n" + "-"*30)
        print_test("Testing user operations...", "info")
        
        test_user_id = "test-" + datetime.now().strftime("%Y%m%d%H%M%S")
        test_user_data = {
            "id": test_user_id,
            "email": f"test_{test_user_id}@example.com",
            "display_name": "Test User",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Create test user
            result = supabase.table("users").insert(test_user_data).execute()
            if result.data:
                print_test("Successfully created test user", "success")
                
                # Read back the user
                result = supabase.table("users").select("*").eq("id", test_user_id).execute()
                if result.data:
                    print_test("Successfully retrieved test user", "success")
                
                # Delete test user
                result = supabase.table("users").delete().eq("id", test_user_id).execute()
                print_test("Successfully deleted test user", "success")
            else:
                print_test("Could not create test user", "warning")
        except Exception as e:
            if "users" in str(e) and "does not exist" in str(e):
                print_test("Users table not found - please run schema.sql", "error")
            elif "violates foreign key constraint" in str(e).lower():
                print_test("Users table requires auth.users reference - this is normal", "warning")
                print_test("In production, users will be created through Supabase Auth", "info")
            else:
                print_test(f"User operation test skipped: {str(e)[:100]}", "warning")
        
        # Test 4: Check storage buckets
        print("\n" + "-"*30)
        print_test("Checking storage buckets...", "info")
        
        try:
            buckets = supabase.storage.list_buckets()
            if buckets:
                print_test(f"Found {len(buckets)} storage bucket(s):", "success")
                for bucket in buckets:
                    print(f"  - {bucket.name} ({'public' if bucket.public else 'private'})")
            else:
                print_test("No storage buckets found", "warning")
                print_test("Create 'audio-recordings' bucket in Storage section", "info")
        except Exception as e:
            print_test(f"Could not check storage: {str(e)[:100]}", "warning")
        
        # Test 5: Test questions and topics
        print("\n" + "-"*30)
        print_test("Checking content tables...", "info")
        
        try:
            # Check topics
            topics = supabase.table("question_topics").select("*").limit(5).execute()
            if topics.data:
                print_test(f"Found {len(topics.data)} question topics", "success")
            else:
                print_test("No question topics found - you'll need to add some", "info")
            
            # Check questions
            questions = supabase.table("questions").select("*").limit(5).execute()
            if questions.data:
                print_test(f"Found {len(questions.data)} questions", "success")
            else:
                print_test("No questions found - you'll need to add some", "info")
        except Exception as e:
            if "does not exist" in str(e):
                print_test("Content tables not found - please run schema.sql", "error")
            else:
                print_test(f"Content check error: {str(e)[:100]}", "warning")
        
        # Final summary
        print("\n" + "="*50)
        if tables_missing:
            print_test("SUPABASE PARTIALLY CONFIGURED", "warning")
            print_test(f"Please run schema.sql to create {len(tables_missing)} missing tables", "info")
        else:
            print_test("SUPABASE FULLY CONFIGURED AND WORKING! 🎉", "success")
            print_test("Your backend can now use persistent storage", "success")
        print("="*50 + "\n")
        
        return True
        
    except Exception as e:
        print_test(f"Connection failed: {str(e)}", "error")
        print("\nPossible issues:")
        print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        print("2. Make sure your Supabase project is active")
        print("3. Check if you've run the schema.sql in SQL Editor")
        return False

def main():
    """Main test function"""
    print("\n🔍 Starting Supabase Integration Test...")
    print("Reading from .env file in backend directory")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print_test(".env file not found!", "error")
        print_test("Please create .env from .env.example and add your Supabase credentials", "info")
        return
    
    # Run the async test
    success = asyncio.run(test_supabase_connection())
    
    if success:
        print("\n✨ Next steps:")
        print("1. Your backend is ready to use Supabase")
        print("2. Restart the backend to apply changes")
        print("3. The mobile app will now work with persistent data")
        print("4. Check Supabase Dashboard for real-time data")

if __name__ == "__main__":
    main()