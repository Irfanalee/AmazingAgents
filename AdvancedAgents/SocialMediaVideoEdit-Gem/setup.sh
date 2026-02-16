#!/bin/bash

echo "=========================================="
echo "  Agentic Video Editor - Setup Assistant"
echo "=========================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH."
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "✅ Docker is installed."

# Check for .env file
if [ -f .env ]; then
    echo "✅ .env file already exists."
else
    echo "⚠️  .env file not found."
    echo "Please enter your Google Gemini API Key:"
    read -r api_key
    
    if [ -z "$api_key" ]; then
        echo "❌ API Key cannot be empty."
        exit 1
    fi
    
    echo "GEMINI_API_KEY=$api_key" > .env
    echo "✅ .env file created."
fi

echo "------------------------------------------"
echo "🚀 Starting the application with Docker..."
echo "------------------------------------------"

docker-compose up --build
