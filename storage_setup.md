# 🗂️ Supabase Storage Setup for Audio Recordings

## Quick Setup Instructions

### 1. Create Storage Bucket

Go to your Supabase Dashboard:
1. Navigate to **Storage** section
2. Click **New bucket** button
3. Configure:
   - **Name**: `audio-recordings`
   - **Public bucket**: ❌ No (keep it private)
   - Click **Create bucket**

### 2. Set Bucket Policies

After creating the bucket, click on it and go to **Policies** tab. Add these RLS policies:

#### Policy 1: Users can upload their own audio
```sql
-- Allow authenticated users to upload to their own folder
CREATE POLICY "Users can upload own audio" 
ON storage.objects FOR INSERT 
TO authenticated
WITH CHECK (
  bucket_id = 'audio-recordings' AND
  auth.uid()::text = (string_to_array(name, '/'))[1]
);
```

#### Policy 2: Users can view their own audio
```sql
-- Allow authenticated users to view their own files
CREATE POLICY "Users can view own audio" 
ON storage.objects FOR SELECT 
TO authenticated
USING (
  bucket_id = 'audio-recordings' AND
  auth.uid()::text = (string_to_array(name, '/'))[1]
);
```

#### Policy 3: Users can delete their own audio
```sql
-- Allow authenticated users to delete their own files
CREATE POLICY "Users can delete own audio" 
ON storage.objects FOR DELETE 
TO authenticated
USING (
  bucket_id = 'audio-recordings' AND
  auth.uid()::text = (string_to_array(name, '/'))[1]
);
```

### 3. Test Storage Access

Run this Python script to test storage:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# List buckets
buckets = supabase.storage.list_buckets()
print("Storage buckets:")
for bucket in buckets:
    print(f"  - {bucket.name}")

# Test file operations (requires authentication)
# This will be done through the mobile app
```

## File Structure

Audio files will be organized as:
```
audio-recordings/
├── {user_id}/
│   ├── {test_id}/
│   │   ├── part1_q1.webm
│   │   ├── part1_q2.webm
│   │   ├── part2.webm
│   │   └── part3_q1.webm
```

## Storage Limits (Free Tier)

- **Storage**: 1GB total
- **Transfer**: 2GB/month
- **File size limit**: 50MB per file

## Next Steps

After setting up storage:
1. ✅ Storage bucket created
2. ✅ RLS policies configured
3. ✅ Backend ready to handle audio uploads
4. ✅ Mobile app can record and upload audio

The backend is already configured to work with Supabase Storage through the `/api/test/submit` endpoint!