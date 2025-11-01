#!/bin/bash
# Debug script - Run this on EC2 to see what's failing

echo "================================================"
echo "🔍 PDFPixie Debugging Script"
echo "================================================"
echo ""

cd ~/apps/chatpdf

echo "1️⃣  Container Status:"
echo "-------------------"
docker-compose ps
echo ""

echo "2️⃣  App Container Logs (last 100 lines):"
echo "---------------------------------------"
docker-compose logs --tail=100 app
echo ""

echo "3️⃣  Environment File Check:"
echo "-------------------------"
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo "Variables present:"
    grep -v "^#" .env | grep -v "^$" | cut -d= -f1
    echo ""
    if grep -q "YOUR_KEY_HERE" .env; then
        echo "⚠️  WARNING: .env contains placeholder values!"
    fi
    if grep -q "OPENROUTER_API_KEY=sk-" .env; then
        echo "✅ OPENROUTER_API_KEY appears to be set"
    else
        echo "❌ OPENROUTER_API_KEY not properly set"
    fi
else
    echo "❌ .env file not found!"
fi
echo ""

echo "4️⃣  Docker Images:"
echo "----------------"
docker images | grep -E "chatpdf|pdfpixie"
echo ""

echo "5️⃣  Port Status:"
echo "--------------"
sudo netstat -tuln | grep -E ":(80|8000|5432|6379)" || echo "No ports listening"
echo ""

echo "6️⃣  Disk Space:"
echo "-------------"
df -h | grep -E "Filesystem|/$"
echo ""

echo "7️⃣  Docker System Info:"
echo "---------------------"
docker system df
echo ""

echo "8️⃣  Try to enter container (if running):"
echo "---------------------------------------"
if docker-compose ps | grep -q "pdfpixie-app.*Up"; then
    echo "Container is running, checking inside..."
    docker-compose exec -T app ls -la /app/data/ 2>/dev/null || echo "Cannot access container"
    docker-compose exec -T app ps aux 2>/dev/null || echo "Cannot run ps in container"
else
    echo "Container is not running (can't inspect)"
fi
echo ""

echo "9️⃣  Check if container keeps restarting:"
echo "---------------------------------------"
RESTARTS=$(docker inspect pdfpixie-app 2>/dev/null | grep -i "RestartCount" | grep -oE "[0-9]+")
if [ -n "$RESTARTS" ]; then
    echo "Container has restarted $RESTARTS times"
    if [ "$RESTARTS" -gt 5 ]; then
        echo "⚠️  Container is in crash loop!"
    fi
else
    echo "Cannot determine restart count"
fi
echo ""

echo "🔟  Last container exit reason:"
echo "-----------------------------"
docker inspect pdfpixie-app 2>/dev/null | grep -A 5 "State" | head -10 || echo "Cannot inspect container"
echo ""

echo "================================================"
echo "💡 Common Issues & Solutions:"
echo "================================================"
echo ""
echo "Issue: Container keeps restarting"
echo "  → Check logs above for Python errors"
echo "  → Verify .env file has correct OPENROUTER_API_KEY"
echo "  → Check if ports 80/8000 are already in use"
echo ""
echo "Issue: 'Connection refused' when testing"
echo "  → Wait 60 seconds for container to fully start"
echo "  → Check if AWS Security Group allows port 80"
echo "  → Verify container shows 'Up (healthy)' status"
echo ""
echo "Issue: Build fails"
echo "  → Run: docker system prune -af"
echo "  → Check disk space: df -h"
echo "  → Verify Dockerfile exists"
echo ""
echo "================================================"
echo "Need more help? Run:"
echo "  docker-compose logs -f app    # Watch live logs"
echo "  docker-compose restart app    # Restart container"
echo "  docker-compose down -v        # Stop everything"
echo "================================================"
