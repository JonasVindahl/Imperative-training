#!/bin/bash
# Build Docker image for TrueNAS (AMD64/x86_64 platform)

set -e

echo "🐳 Building Docker image for AMD64 (TrueNAS compatible)..."

# Build for AMD64 platform
docker buildx build --platform linux/amd64 \
  -t ghcr.io/jonasvindahl/imperative-training:latest \
  --push \
  .

echo "✅ Image built and pushed for linux/amd64!"
echo ""
echo "Now deploy in TrueNAS:"
echo "  Image: ghcr.io/jonasvindahl/imperative-training:latest"
echo "  Container Port: 8000"
echo "  Host Port: 8000 (or any host port you want)"
