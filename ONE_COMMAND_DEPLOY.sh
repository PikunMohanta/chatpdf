#!/bin/bash
# ⚡ ONE COMMAND DEPLOYMENT - Copy and paste this entire block into your EC2 terminal

set -e

cd ~/apps/chatpdf

echo "================================================"
echo "🚀 PDFPixie One-Command Deployment"
echo "================================================"
echo ""

echo "📥 Step 1: Pulling latest code..."
git pull origin docker-deployment
echo ""

echo "🛑 Step 2: Stopping old containers..."
docker-compose down -v
echo ""

echo "🧹 Step 3: Cleaning Docker..."
docker system prune -af
echo ""

echo "🔨 Step 4: Building new image (5-10 minutes)..."
docker-compose build --no-cache app
echo ""

echo "🚀 Step 5: Starting services..."
docker-compose up -d
echo ""

echo "⏳ Step 6: Waiting 60 seconds for startup..."
for i in {60..1}; do
  echo -ne "   $i seconds remaining...\r"
  sleep 1
done
echo "   ✅ Wait complete          "
echo ""

echo "📊 Step 7: Checking status..."
docker-compose ps
echo ""

echo "📋 Step 8: Checking app logs..."
docker-compose logs --tail=30 app
echo ""

echo "🏥 Step 9: Testing health endpoint..."
if curl -sf http://localhost/health; then
  echo ""
  echo "✅ Health check PASSED!"
else
  echo ""
  echo "❌ Health check FAILED"
  echo ""
  echo "Running debug script..."
  bash DEBUG.sh
  exit 1
fi

echo ""
echo "================================================"
echo "🎉 Deployment Complete!"
echo "================================================"
echo ""
echo "Your app is accessible at:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR-EC2-IP')"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f app  # Watch logs"
echo "  docker-compose ps           # Check status"
echo "  bash DEBUG.sh               # Run diagnostics"
echo ""
