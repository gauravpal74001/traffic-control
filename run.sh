#!/bin/bash

# S.A.D.A.K Docker Run Script
# This script helps you run the project easily

echo "🚀 S.A.D.A.K - Docker Run Script"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if image exists
if ! docker images | grep -q "sadak\|sangya"; then
    echo "⚠️  Docker image not found!"
    echo "Building image first (this will take 20-60 minutes)..."
    docker-compose build
    if [ $? -ne 0 ]; then
        echo "❌ Build failed! Check the error messages above."
        exit 1
    fi
fi

# Check if container is already running
if docker ps | grep -q "sadak-traffic-analysis"; then
    echo "✅ Application is already running!"
    echo "Access it at: http://localhost:8080"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    exit 0
fi

echo "Starting S.A.D.A.K application..."
echo ""
echo "📋 Instructions:"
echo "  1. Wait for 'You can now view your Streamlit app' message"
echo "  2. Open browser: http://localhost:8080"
echo "  3. Press Ctrl+C to stop the application"
echo ""
echo "Starting now..."
echo ""

# Start the application
docker-compose up



