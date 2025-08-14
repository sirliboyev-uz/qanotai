# QanotAI Backend API

FastAPI-based backend for QanotAI IELTS Speaking test preparation platform.

## Tech Stack

- **Framework:** FastAPI with async/await
- **Database:** PostgreSQL with SQLAlchemy (async)
- **Cache/Queue:** Redis + Celery
- **Storage:** DigitalOcean Spaces / AWS S3
- **Auth:** Firebase Authentication
- **AI:** OpenAI Whisper (STT) + GPT-4/Claude (Scoring)

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── workers/      # Celery tasks
├── tests/            # Test suite
├── alembic/          # Database migrations
└── docker-compose.yml
```

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### 2. Local Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 3. Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run PostgreSQL and Redis locally or use cloud services

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/v1/auth/firebase` - Authenticate with Firebase token
- `GET /api/v1/auth/me` - Get current user

### Questions
- `GET /api/v1/questions/next` - Get question set for test
- `GET /api/v1/questions/topics` - List available topics

### Attempts
- `POST /api/v1/attempts` - Create test attempt, get upload URLs
- `PUT /api/v1/attempts/{id}/complete` - Submit audio, trigger scoring
- `GET /api/v1/attempts/{id}` - Get attempt with score

### Scores
- `GET /api/v1/scores/attempt/{id}` - Get detailed score
- `GET /api/v1/scores/history` - Score history
- `GET /api/v1/scores/progress` - Progress analysis

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py::test_firebase_auth
```

## Deployment

### DigitalOcean App Platform

1. Push to GitHub
2. Create App in DO console
3. Set environment variables
4. Deploy

### Manual VPS Deployment

```bash
# On server
git clone <repo>
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

## Performance

- **Async endpoints:** 10x faster than Django
- **WebSocket support:** Real-time score updates
- **Auto-scaling:** Celery workers scale with queue
- **Caching:** Redis for hot data

## Security

- Firebase token verification
- JWT for session management
- Rate limiting per user/IP
- CORS configured
- SQL injection protected (SQLAlchemy)
- XSS protected (Pydantic validation)

## Monitoring

- Health check: `GET /health`
- Metrics: Prometheus endpoint
- Logs: Structured JSON logging
- Tracing: OpenTelemetry ready

## License

Proprietary - QanotAI