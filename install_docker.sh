#!/bin/bash

# Docker Installation Script for macOS

echo "Docker Installation Guide for macOS"
echo "===================================="
echo ""
echo "Please install Docker Desktop for Mac from:"
echo "https://www.docker.com/products/docker-desktop/"
echo ""
echo "Or use Homebrew:"
echo "brew install --cask docker"
echo ""
echo "After installation:"
echo "1. Launch Docker Desktop from Applications"
echo "2. Wait for Docker to start (icon in menu bar)"
echo "3. Then run: docker --version"
echo ""
echo "Once Docker is installed, you can build the QanotAI backend with:"
echo "cd /Users/sirliboyevuz/Documents/sirli\ AI/QanotAI/backend"
echo "docker build -t qanotai-backend ."
echo "docker-compose up"