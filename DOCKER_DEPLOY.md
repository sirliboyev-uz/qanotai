# Docker Deployment Guide for QanotAI Backend

## Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- `.env` file configured with all required environment variables

## Quick Start (Local Development)

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

3. **Stop the services:**
```bash
docker-compose down
```

## Production Deployment

### Option 1: Deploy to VPS (DigitalOcean, Linode, AWS EC2)

1. **Prepare your server:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone your repository:**
```bash
git clone <your-repo>
cd qanotai-backend
```

3. **Create production environment file:**
```bash
cp .env.example .env.production
# Edit .env.production with your production values
```

4. **Build and run:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

5. **Set up SSL (optional but recommended):**
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx.conf with SSL paths
# Restart nginx container
docker-compose -f docker-compose.prod.yml restart nginx
```

### Option 2: Deploy to Google Cloud Run

1. **Build and push to Google Container Registry:**
```bash
# Configure gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/qanotai-backend .
docker push gcr.io/YOUR_PROJECT_ID/qanotai-backend
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy qanotai-backend \
  --image gcr.io/YOUR_PROJECT_ID/qanotai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env.production | tr '\n' ',')"
```

### Option 3: Deploy to AWS ECS

1. **Build and push to ECR:**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

# Build and tag
docker build -t qanotai-backend .
docker tag qanotai-backend:latest YOUR_ECR_URI/qanotai-backend:latest

# Push
docker push YOUR_ECR_URI/qanotai-backend:latest
```

2. **Create ECS task definition and service via AWS Console or CLI**

### Option 4: Deploy to DigitalOcean App Platform

1. **Push to GitHub/GitLab**

2. **Create new app in DigitalOcean:**
- Connect your repository
- Choose Dockerfile as build option
- Set environment variables
- Deploy

### Option 5: Deploy to Fly.io (Recommended for simplicity)

1. **Install flyctl:**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Launch app:**
```bash
fly launch
# Follow prompts, it will detect Dockerfile
```

3. **Set secrets:**
```bash
fly secrets set SUPABASE_URL="your-url" SUPABASE_KEY="your-key" # etc
```

4. **Deploy:**
```bash
fly deploy
```

## Docker Commands Reference

### Build image:
```bash
docker build -t qanotai-backend .
```

### Run container:
```bash
docker run -d -p 8000:8000 --env-file .env qanotai-backend
```

### View logs:
```bash
docker-compose logs -f api
```

### Execute command in container:
```bash
docker-compose exec api bash
```

### Clean up:
```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove all unused images
docker system prune -a
```

## Environment Variables

Create `.env.production` with:
```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Firebase (for OTP)
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-auth-domain
FIREBASE_PROJECT_ID=your-project-id

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# OpenAI (optional for production)
OPENAI_API_KEY=your-openai-key

# Payme
PAYME_MERCHANT_ID=your-merchant-id
PAYME_SECRET_KEY=your-secret-key
PAYME_TEST_MODE=false

# App Settings
ENVIRONMENT=production
LOG_LEVEL=info
```

## Monitoring

1. **Check health:**
```bash
curl http://localhost:8000/health
```

2. **View container stats:**
```bash
docker stats
```

3. **Monitor logs:**
```bash
docker-compose logs -f --tail=100 api
```

## Troubleshooting

### Container won't start:
```bash
# Check logs
docker-compose logs api

# Verify environment variables
docker-compose config
```

### Permission issues:
```bash
# Fix ownership
sudo chown -R 1000:1000 .
```

### Port already in use:
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

## Security Best Practices

1. **Never commit `.env` files to git**
2. **Use secrets management in production (AWS Secrets Manager, GCP Secret Manager)**
3. **Enable SSL/TLS for production**
4. **Regularly update base images**
5. **Scan images for vulnerabilities:**
```bash
docker scan qanotai-backend
```

## Scaling

### Horizontal scaling with Docker Swarm:
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml qanotai

# Scale service
docker service scale qanotai_api=3
```

### With Kubernetes:
Create `k8s-deployment.yaml` and deploy to your cluster.

## Cost-Effective Options

1. **Fly.io** - Free tier includes 3 shared-cpu VMs
2. **Google Cloud Run** - Free tier: 2M requests/month
3. **Railway** - $5/month starter plan
4. **Render** - Free tier available
5. **DigitalOcean** - $5/month droplet

## Support

For issues with Docker deployment, check:
- Docker logs: `docker-compose logs`
- Container status: `docker ps`
- System resources: `docker system df`