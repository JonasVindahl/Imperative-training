#!/bin/bash
# Build Docker image for TrueNAS (AMD64/x86_64 platform)

set -e

echo "🐳 Building Docker image for AMD64 (TrueNAS compatible)..."

# Build for AMD64 platform using multiarch builder
docker buildx build --builder multiarch --platform linux/amd64 \
  -t ghcr.io/jonasvindahl/imperative-training:latest \
  --push \
  .

echo "✅ Image built and pushed for linux/amd64!"
echo ""
echo "Now deploy in TrueNAS:"
echo "  Image: ghcr.io/jonasvindahl/imperative-training:latest"
echo "  Container Port: 8000"
echo "  Host Port: 8000 (or any host port you want)"
echo ""
echo "To add new exams without rebuilding:"
echo "  1. Edit exams.json"
echo "  2. Add question JSON files to questions/<exam_id>/"
echo "  3. Restart the container"
