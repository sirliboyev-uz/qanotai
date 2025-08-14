#!/bin/bash

# QanotAI Backend Setup Script
echo "🚀 QanotAI Backend Setup"

# Check OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 macOS detected"
    
    # Install Docker Desktop if not present
    if ! command -v docker &> /dev/null; then
        echo "🐳 Docker not found. Please install Docker Desktop:"
        echo "   1. Download from: https://www.docker.com/products/docker-desktop/"
        echo "   2. Install and start Docker Desktop"
        echo "   3. Run this script again"
        exit 1
    fi
else
    echo "🐧 Linux detected"
fi

# Check Docker Compose
if command -v docker compose &> /dev/null; then
    echo "✅ Docker Compose (v2) found"
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose (v1) found"
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Docker Compose not found"
    echo "   Docker Desktop should include it. Make sure Docker is running."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before continuing"
    echo "   Required: Firebase credentials, OpenAI/Anthropic API keys"
    read -p "Press Enter after updating .env..." 
fi

# Start services
echo "🚀 Starting services..."
$DOCKER_COMPOSE up -d

# Wait for services
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check status
$DOCKER_COMPOSE ps

echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Access API: http://localhost:8000"
echo "   2. View API docs: http://localhost:8000/docs"
echo "   3. View logs: $DOCKER_COMPOSE logs -f"
echo "   4. Stop services: $DOCKER_COMPOSE down"