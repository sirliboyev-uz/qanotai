# 🚀 QanotAI Backend Deployment Guide

## Option 1: Railway (Recommended - Easiest)

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- Your backend code pushed to GitHub

### Deployment Steps

1. **Push your code to GitHub**
```bash
cd /Users/sirliboyevuz/Documents/sirli\ AI/QanotAI/backend
git init
git add .
git commit -m "Initial QanotAI backend with Payme integration"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/qanotai-backend.git
git push -u origin main
```

2. **Deploy on Railway**
- Go to [railway.app](https://railway.app)
- Click "Start a New Project"
- Select "Deploy from GitHub repo"
- Choose your `qanotai-backend` repository
- Railway will auto-detect Python and start deployment

3. **Configure Environment Variables**
In Railway dashboard, go to Variables tab and add:

```env
# Required Variables
SECRET_KEY=generate-new-32-char-secret-key-here
OPENAI_API_KEY=your-openai-key
SUPABASE_URL=https://mnpwlubbpvlgaulwbicx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Payme Production
PAYME_MERCHANT_ID=your-merchant-id
PAYME_SECRET_KEY=your-secret-key
PAYME_TEST_MODE=false

# Database (Railway provides this automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

4. **Get your deployment URL**
- Railway will provide URL like: `qanotai-backend.up.railway.app`
- Your API will be available at: `https://qanotai-backend.up.railway.app`

## Option 2: Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deployment Steps

1. **Create Heroku app**
```bash
heroku create qanotai-backend
```

2. **Add PostgreSQL addon**
```bash
heroku addons:create heroku-postgresql:mini
```

3. **Set environment variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-openai-key
heroku config:set SUPABASE_URL=your-supabase-url
heroku config:set SUPABASE_ANON_KEY=your-anon-key
heroku config:set PAYME_MERCHANT_ID=your-merchant-id
heroku config:set PAYME_SECRET_KEY=your-secret-key
heroku config:set PAYME_TEST_MODE=false
```

4. **Deploy**
```bash
git push heroku main
```

## Option 3: DigitalOcean App Platform

1. **Create App**
- Go to DigitalOcean App Platform
- Connect GitHub repository
- Select Python buildpack

2. **Configure**
- Set environment variables in App Settings
- Choose $5/month basic plan

3. **Deploy**
- Click Deploy
- Get URL: `qanotai-backend.ondigitalocean.app`

## 📱 Update Mobile App with Production URL

After deployment, update your Flutter app:

### 1. Update backend URL in Flutter

Edit `/mobile/lib/core/services/backend_auth_service.dart`:
```dart
class BackendAuthService {
  static const String baseUrl = 'https://qanotai-backend.up.railway.app';
  // Replace with your actual deployment URL
```

Edit `/mobile/lib/core/services/payment_service.dart`:
```dart
class PaymentService {
  static const String baseUrl = 'https://qanotai-backend.up.railway.app';
```

### 2. Update other service files
Search and replace all instances of:
- `http://localhost:8000` → `https://your-backend-url.com`

## 🔒 Production Security Checklist

- [ ] Generate new SECRET_KEY (use: `openssl rand -hex 32`)
- [ ] Set DEBUG=False
- [ ] Configure CORS for your domain only
- [ ] Enable HTTPS (Railway/Heroku provide this)
- [ ] Set up domain name (optional)
- [ ] Configure Payme webhook URL in Payme dashboard
- [ ] Test all endpoints with production URL
- [ ] Set up monitoring (UptimeRobot, Sentry)
- [ ] Enable database backups

## 🧪 Testing Production Deployment

1. **Test API Health**
```bash
curl https://your-backend-url.com/health
```

2. **Test Docs**
```bash
open https://your-backend-url.com/docs
```

3. **Test Auth Endpoint**
```bash
curl -X POST https://your-backend-url.com/api/auth/phone-verify \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567", "verification_code": "123456"}'
```

## 🎯 Configure Payme Webhook

In Payme Business Dashboard:
1. Go to Settings → API
2. Set Webhook URL: `https://your-backend-url.com/api/payment/payme-webhook`
3. Save and test

## 🚨 Monitoring Setup

### Option 1: UptimeRobot (Free)
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add monitor for: `https://your-backend-url.com/health`
3. Set check interval: 5 minutes
4. Add alert contact (email/SMS)

### Option 2: Railway Metrics
- Railway provides built-in metrics
- View in Railway dashboard → Metrics tab

## 📊 Database Management

### View Supabase Data
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Use Table Editor to view/edit data

### Backup Strategy
- Supabase automatically backs up daily (Pro plan)
- Export data regularly: SQL Editor → Export

## 🔄 Continuous Deployment

Railway automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway auto-deploys in ~2 minutes
```

## 📝 Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | 32+ char secret | `openssl rand -hex 32` |
| DATABASE_URL | PostgreSQL URL | Auto-provided by Railway |
| SUPABASE_URL | Supabase project URL | https://xxx.supabase.co |
| SUPABASE_ANON_KEY | Public Supabase key | eyJhbG... |
| OPENAI_API_KEY | OpenAI API key | sk-proj-... |
| PAYME_MERCHANT_ID | Payme merchant ID | From Payme dashboard |
| PAYME_SECRET_KEY | Payme secret | From Payme dashboard |
| PAYME_TEST_MODE | Test mode flag | false (for production) |

## 🆘 Troubleshooting

### Issue: "Application failed to respond"
- Check logs: `railway logs`
- Verify all environment variables are set
- Ensure `railway.json` is correct

### Issue: "Database connection failed"
- Check DATABASE_URL is set
- Verify Supabase credentials
- Check network/firewall settings

### Issue: "Import error"
- Ensure all dependencies in requirements.txt
- Check Python version (3.11 required)

## 🎉 Success Indicators

✅ API docs accessible at `/docs`
✅ Health check returns 200 at `/health`  
✅ Can create test user via phone auth
✅ Payme webhook responds correctly
✅ Mobile app connects successfully

---

**Deployment Support**: If you encounter issues, check Railway logs or contact support.