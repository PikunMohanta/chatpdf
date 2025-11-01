#!/bin/bash
# PDFPixie Quick Deployment Script for AWS
set -e

echo "🚀 PDFPixie Deployment Script"
echo "=============================="
echo ""

# Check if running on AWS instance
if [ ! -f /.dockerenv ] && [ -z "$AWS_EXECUTION_ENV" ]; then
    echo "⚠️  This script should be run on your AWS EC2 instance"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for OPENROUTER_API_KEY
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ Error: OPENROUTER_API_KEY environment variable not set"
    echo "Set it with: export OPENROUTER_API_KEY='your-key-here'"
    exit 1
fi

# Step 1: Build Frontend
echo "📦 Step 1: Building frontend with production config..."
cd frontend
if [ ! -f ".env.production" ]; then
    echo "❌ Error: frontend/.env.production not found"
    exit 1
fi
npm run build
cd ..
echo "✅ Frontend built successfully"
echo ""

# Step 2: Build Docker Image
echo "🐳 Step 2: Building Docker image..."
docker build -t pdfpixie:latest -f Dockerfile .
echo "✅ Docker image built successfully"
echo ""

# Step 3: Stop Old Container
echo "🛑 Step 3: Stopping old container..."
docker stop pdfpixie 2>/dev/null || echo "No existing container to stop"
docker rm pdfpixie 2>/dev/null || echo "No existing container to remove"
echo "✅ Old container removed"
echo ""

# Step 4: Run New Container
echo "▶️  Step 4: Starting new container..."
docker run -d \
  --name pdfpixie \
  -p 80:80 \
  -p 8000:8000 \
  -v "$(pwd)/backend/data:/app/data" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  -e ENVIRONMENT="production" \
  --restart unless-stopped \
  pdfpixie:latest

echo "✅ Container started"
echo ""

# Step 5: Wait for Health Check
echo "⏳ Step 5: Waiting for application to be healthy..."
sleep 15

# Check if container is running
if ! docker ps | grep -q pdfpixie; then
    echo "❌ Error: Container failed to start"
    echo "Check logs with: docker logs pdfpixie"
    exit 1
fi

# Test health endpoint
if curl -sf http://localhost/health > /dev/null; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Health check failed, but container is running"
    echo "Check logs with: docker logs pdfpixie"
fi
echo ""

# Step 6: Display Info
echo "🎉 Deployment Complete!"
echo "=============================="
echo ""
echo "📊 Container Status:"
docker ps | grep pdfpixie || echo "Container not found in ps"
echo ""
echo "🌐 Access Your Application:"
echo "   • By IP:     http://13.201.129.219"
echo "   • By Domain: http://pdfpixie.duckdns.org"
echo ""
echo "🔧 Useful Commands:"
echo "   • View logs:      docker logs pdfpixie -f"
echo "   • Restart:        docker restart pdfpixie"
echo "   • Stop:           docker stop pdfpixie"
echo "   • Shell access:   docker exec -it pdfpixie /bin/bash"
echo ""
echo "📝 Next Steps:"
echo "   1. Test from another device: http://13.201.129.219"
echo "   2. Configure DuckDNS (see AWS_DEPLOYMENT_GUIDE.md)"
echo "   3. Set up HTTPS with Let's Encrypt (optional)"
echo ""
