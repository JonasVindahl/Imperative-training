#!/bin/bash
# Quick deployment script for C Programming Practice System

set -e

echo "========================================="
echo "C Programming Practice System - Deploy"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

# Generate secret key if .env doesn't exist
if [ ! -f .env ]; then
    echo "🔑 Generating secure secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

    cat > .env << EOF
# Flask Configuration
FLASK_SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URL=sqlite:///instance/practice.db

# Code Execution Limits
MAX_CODE_EXECUTION_TIME=3
MAX_MEMORY_MB=50
EOF
    echo "✅ Created .env file with secure settings"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
mkdir -p instance temp
echo "✅ Created necessary directories"

# Build and start containers
echo ""
echo "🚀 Building and starting containers..."
docker-compose up -d --build

# Wait for container to be healthy
echo ""
echo "⏳ Waiting for application to start..."
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "========================================="
    echo "✅ Deployment successful!"
    echo "========================================="
    echo ""
    echo "Application is running at:"
    echo "  🌐 http://localhost:5067"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Status:       docker-compose ps"
    echo ""
    echo "First time? Register an account at:"
    echo "  http://localhost:5067/auth/register"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Check logs:"
    echo "  docker-compose logs"
    exit 1
fi
