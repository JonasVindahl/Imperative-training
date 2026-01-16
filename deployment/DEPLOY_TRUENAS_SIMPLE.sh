#!/bin/bash
# Simple deployment script for TrueNAS SCALE 24.10
# Run this on TrueNAS after copying project files

set -e

echo "=========================================="
echo "C Programming Practice - TrueNAS Deploy"
echo "=========================================="
echo ""

# Configuration
POOL_NAME="MainPool"  # Change this to your pool name
APP_DIR="/mnt/${POOL_NAME}/Apps/c-practice"
DATA_DIR="/mnt/${POOL_NAME}/Apps/c-practice-data"

# Check if we're in the right directory
if [ ! -f "truenas-scale-app.yaml" ]; then
    echo "❌ Error: truenas-scale-app.yaml not found"
    echo "Please run this script from the project directory"
    echo "Example: cd /mnt/${POOL_NAME}/Apps/c-practice && ./DEPLOY_TRUENAS_SIMPLE.sh"
    exit 1
fi

# Create data directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
    echo "📁 Creating data directory..."
    mkdir -p "$DATA_DIR"
    chmod 755 "$DATA_DIR"
fi

# Generate secret key if needed
if grep -q "change-this-to-random-string" truenas-scale-app.yaml; then
    echo "🔑 Generating secure secret key..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    sed -i.bak "s/change-this-to-random-string-abc123xyz/${SECRET}/" truenas-scale-app.yaml
    echo "✅ Secret key generated and saved"
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Is this TrueNAS SCALE?"
    exit 1
fi

# Stop existing container if running
if docker ps -a | grep -q c-programming-practice; then
    echo "⏹️  Stopping existing container..."
    docker compose -f truenas-scale-app.yaml down 2>/dev/null || docker-compose -f truenas-scale-app.yaml down 2>/dev/null || true
fi

# Start the application
echo ""
echo "🚀 Starting application..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f truenas-scale-app.yaml up -d
else
    docker compose -f truenas-scale-app.yaml up -d
fi

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check if running
if docker ps | grep -q c-programming-practice; then
    # Get TrueNAS IP
    IP=$(hostname -I | awk '{print $1}')

    echo ""
    echo "=========================================="
    echo "✅ Deployment Successful!"
    echo "=========================================="
    echo ""
    echo "🌐 Access your app at:"
    echo "   http://${IP}:5067"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs:    docker logs -f c-programming-practice"
    echo "   Restart:      docker restart c-programming-practice"
    echo "   Stop:         docker stop c-programming-practice"
    echo "   Remove:       docker compose -f truenas-scale-app.yaml down"
    echo ""
    echo "📁 Data location:"
    echo "   App files:    ${APP_DIR}"
    echo "   Database:     ${DATA_DIR}"
    echo ""

    # Show first few log lines
    echo "📋 Latest logs:"
    docker logs --tail 10 c-programming-practice
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check logs: docker logs c-programming-practice"
    exit 1
fi
