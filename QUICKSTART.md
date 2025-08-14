# 🚀 QanotAI Backend Quick Start Guide

## Option 1: Docker (Recommended) - Requires Docker Desktop

### Step 1: Install Docker Desktop
```bash
# macOS - Download from:
https://www.docker.com/products/docker-desktop/

# Or via Homebrew:
brew install --cask docker
```

### Step 2: Start Docker Desktop
Open Docker Desktop app and wait for it to start (whale icon in menu bar)

### Step 3: Run Setup
```bash
cd backend
./setup.sh
```

This will:
- Check Docker installation
- Create .env file
- Start PostgreSQL, Redis, and API
- Services available at http://localhost:8000

### Step 4: Use Docker Compose Commands
```bash
# Modern Docker (v2 - built into Docker Desktop)
docker compose up -d      # Start services
docker compose ps         # Check status
docker compose logs -f    # View logs
docker compose down       # Stop services

# If above doesn't work, try legacy version:
docker-compose up -d
```

---

## Option 2: Local Python (Without Docker)

### Prerequisites
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Create database
createdb qanotai
```

### Step 1: Setup Python Environment
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials:
# - Set DATABASE_URL to your local PostgreSQL
# - Add Firebase credentials
# - Add OpenAI/Anthropic API keys
```

### Step 3: Initialize Database
```bash
# Run migrations
alembic upgrade head

# Seed sample questions
python app/db/seed_data.py
```

### Step 4: Start Server
```bash
# Option A: Use helper script
python run_local.py

# Option B: Direct command
uvicorn app.main:app --reload
```

---

## 🎯 Testing the API

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. View API Documentation
Open browser: http://localhost:8000/docs

### 3. Test Authentication (requires Firebase setup)
```bash
# Get Firebase token from your app, then:
curl -X POST http://localhost:8000/api/v1/auth/firebase \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "YOUR_TOKEN"}'
```

### 4. Get Questions (no auth for testing)
```bash
curl http://localhost:8000/api/v1/questions/topics
```

---

## 🛠 Troubleshooting

### Docker Issues

**"docker: command not found"**
- Install Docker Desktop first
- Make sure Docker Desktop is running

**"Cannot connect to Docker daemon"**
- Start Docker Desktop application
- Wait for whale icon to appear in menu bar

**Port already in use**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
docker compose run --service-ports api uvicorn app.main:app --port 8001
```

### Python Issues

**"Module not found"**
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Database connection failed**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Check connection
psql -U postgres -d qanotai
```

---

## 📝 Environment Variables

Critical variables to set in `.env`:

```env
# Required
SECRET_KEY=generate-random-32-char-string
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/qanotai

# Firebase (for auth)
FIREBASE_PROJECT_ID=your-project
FIREBASE_PRIVATE_KEY=your-key

# AI (for scoring)
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Storage (for audio files)
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
SPACES_KEY=your-key
SPACES_SECRET=your-secret
SPACES_BUCKET=qanotai-audio
```

---

## 🚦 Next Steps

1. **Frontend Development**
   - Flutter app in `/mobile` directory
   - Connect to API at `http://localhost:8000`

2. **Production Deployment**
   - Use Docker Compose for staging
   - Deploy to DigitalOcean App Platform
   - Set production environment variables

3. **Monitoring**
   - Prometheus metrics at `/metrics`
   - Structured logs in JSON format
   - Health checks at `/health`

---

## 💡 Tips

- Use `docker compose logs -f api` to debug issues
- API auto-reloads on code changes (with --reload flag)
- Swagger UI at `/docs` for testing endpoints
- Database viewer: `docker compose exec postgres psql -U postgres qanotai`