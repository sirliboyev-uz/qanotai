# 🚀 Deploy to Replit (FREE & EASY)

## Quick Deploy Steps

### 1. Push to GitHub First
```bash
cd "/Users/sirliboyevuz/Documents/sirli AI/QanotAI/backend"
git init
git add .
git commit -m "QanotAI backend ready for deployment"
git remote add origin https://github.com/YOUR-USERNAME/qanotai-backend.git
git push -u origin main
```

### 2. Import to Replit

1. Go to [replit.com](https://replit.com)
2. Click **"+ Create"**
3. Click **"Import from GitHub"**
4. Paste your GitHub URL: `https://github.com/YOUR-USERNAME/qanotai-backend`
5. Click **"Import from GitHub"**

### 3. Configure Replit

The files are already configured:
- `.replit` - Tells Replit how to run the app
- `main.py` - Entry point that handles PORT properly
- `requirements_minimal.txt` - Simplified dependencies

### 4. Set Environment Variables

In Replit:
1. Click **"Secrets"** (🔒 icon) in left sidebar
2. Add these secrets:

```
SECRET_KEY = generate-32-char-secret-here
OPENAI_API_KEY = sk-proj-ud8uyBLjcub3gUnU...
SUPABASE_URL = https://mnpwlubbpvlgaulwbicx.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI...
PAYME_TEST_MODE = true
```

### 5. Install Dependencies

In Replit Shell:
```bash
pip install -r requirements_minimal.txt
```

Or Replit will auto-install when you click Run.

### 6. Run the App

Click the big **"Run"** button!

Your app will be available at:
```
https://qanotai-backend.YOUR-USERNAME.repl.co
```

## 🔧 Troubleshooting

### If you see "PORT" error:
The `main.py` file handles this automatically now.

### If dependencies fail:
Use the Shell:
```bash
pip install fastapi uvicorn supabase openai python-jose passlib python-multipart
```

### If import errors:
Add to Shell:
```bash
export PYTHONPATH=/home/runner/qanotai-backend:$PYTHONPATH
```

## 📱 Update Flutter App

After deployment, update your Flutter app:

```dart
// lib/core/config/app_config.dart
static String get apiBaseUrl {
  if (isProduction) {
    return 'https://qanotai-backend.YOUR-USERNAME.repl.co';
  } else {
    return 'http://localhost:8000';
  }
}
```

## ✅ What Works on Replit

- ✅ FastAPI with all endpoints
- ✅ Supabase integration
- ✅ OpenAI integration
- ✅ Payme webhooks
- ✅ JWT authentication
- ✅ Auto-restart on crash
- ✅ Public HTTPS URL

## 🎯 Replit Features

- **Always On**: Upgrade to keep running 24/7 ($7/month)
- **Custom Domain**: Connect your domain
- **Secrets**: Environment variables UI
- **Shell**: Full terminal access
- **Auto-deploy**: Push to GitHub = auto update

## 📊 Test Your Deployment

1. **Check API docs**:
```
https://qanotai-backend.YOUR-USERNAME.repl.co/docs
```

2. **Test health endpoint**:
```bash
curl https://qanotai-backend.YOUR-USERNAME.repl.co/health
```

3. **Test auth**:
```bash
curl -X POST https://qanotai-backend.YOUR-USERNAME.repl.co/api/auth/phone-verify \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567", "verification_code": "123456"}'
```

## 🎉 Success!

Your backend is now live on Replit! Share the URL with your Flutter app and start testing.

---

**Note**: Replit free tier sleeps after 1 hour of inactivity. First request wakes it up (~5-10 seconds).