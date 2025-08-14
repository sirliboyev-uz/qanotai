# 🚀 Supabase Setup Guide for QanotAI

## Step 1: Create Supabase Account & Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub or email
4. Create a new project:
   - **Project Name**: `qanotai` (or your preferred name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Start with Free tier

## Step 2: Get Your API Keys

After project creation, go to:
1. **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon/Public Key**: For client-side operations
   - **Service Role Key**: For server-side admin operations (keep secret!)

## Step 3: Set Up Database Schema

### Option A: Using Supabase Dashboard (Easy)
1. Go to **SQL Editor** in Supabase Dashboard
2. Click "New Query"
3. Copy the entire contents of `supabase/schema.sql`
4. Paste and click "Run"
5. You should see "Success" message

### Option B: Using Supabase CLI (Advanced)
```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

## Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your Supabase credentials:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
```

## Step 5: Enable Authentication Providers

In Supabase Dashboard:

### Phone Authentication (for OTP):
1. Go to **Authentication** → **Providers**
2. Enable **Phone**
3. Configure SMS provider (Twilio recommended):
   - Sign up for [Twilio](https://www.twilio.com)
   - Get Account SID, Auth Token, and Phone Number
   - Add to Supabase Phone provider settings

### Email Authentication:
1. Enable **Email** provider
2. Configure SMTP settings (optional for custom domain)

## Step 6: Set Up Storage Buckets (for audio files)

1. Go to **Storage** in Supabase Dashboard
2. Create new bucket:
   - Name: `audio-recordings`
   - Public: No (private bucket)
3. Create policies for authenticated users:
   ```sql
   -- Allow users to upload their own audio
   CREATE POLICY "Users can upload own audio" ON storage.objects
   FOR INSERT WITH CHECK (auth.uid()::text = (storage.foldername(name))[1]);
   
   -- Allow users to view their own audio
   CREATE POLICY "Users can view own audio" ON storage.objects
   FOR SELECT USING (auth.uid()::text = (storage.foldername(name))[1]);
   ```

## Step 7: Test Your Setup

Run this Python script to test the connection:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Test connection
try:
    # Get subscription plans
    result = supabase.table("subscription_plans").select("*").execute()
    print("✅ Connection successful!")
    print(f"Found {len(result.data)} subscription plans")
    
    # Test auth
    # Note: This will fail if phone auth is not configured
    # response = supabase.auth.sign_in_with_otp({
    #     "phone": "+1234567890"
    # })
    # print("✅ Auth working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

## Step 8: Update Backend Code

The backend is already configured to use Supabase! Just ensure:

1. Your `.env` file has correct credentials
2. Restart the backend server:
```bash
cd backend
source venv/bin/activate
PYTHONPATH=. python app/main_complete.py
```

## Step 9: Mobile App Configuration

Update your Flutter app's backend URL:

```dart
// In lib/core/services/backend_auth_service.dart
static const String baseUrl = 'http://YOUR_BACKEND_URL:8000';
```

## 🎯 What's Working Now:

✅ **User Management**: Store users in Supabase
✅ **Subscriptions**: Track user plans and payments
✅ **Test Attempts**: Store test results and progress
✅ **Questions Bank**: Manage IELTS questions
✅ **Leaderboard**: Track and rank users
✅ **Progress Tracking**: Monitor user improvement
✅ **Audio Storage**: Store recordings in Supabase Storage

## 🚀 Next Steps:

1. **Production Deployment**:
   - Deploy backend to Railway/Heroku
   - Use production Supabase project
   - Enable Row Level Security (RLS)

2. **Payment Integration**:
   - Set up Stripe
   - Implement subscription webhooks

3. **Real-time Features**:
   - Use Supabase Realtime for live leaderboard
   - Push notifications for daily challenges

## 📚 Useful Supabase Features:

- **Edge Functions**: Run serverless functions
- **Realtime**: Subscribe to database changes
- **Vector embeddings**: For AI-powered search
- **Database Webhooks**: Trigger actions on data changes

## 🔒 Security Checklist:

- [ ] Enable RLS on all tables
- [ ] Use service key only on backend
- [ ] Never expose service key to client
- [ ] Set up proper CORS origins
- [ ] Enable 2FA on Supabase account
- [ ] Regular database backups

## 📞 Support:

- Supabase Discord: https://discord.supabase.com
- Documentation: https://supabase.com/docs
- Status: https://status.supabase.com

---

**Note**: The schema is already optimized for your IELTS app with proper indexes, RLS policies, and relationships!