#!/bin/bash
# Simple EC2 Deployment Script - No Supervisor Version
# Run this on your EC2 instance

set -e

echo "🚀 PDFPixie Deployment (No Supervisor)"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Navigate to app directory
echo -e "${YELLOW}Step 1: Navigating to app directory...${NC}"
cd ~/apps/chatpdf || { echo -e "${RED}Error: Directory not found${NC}"; exit 1; }
echo -e "${GREEN}✓ In correct directory${NC}"
echo ""

# Step 2: Pull latest code
echo -e "${YELLOW}Step 2: Pulling latest code from GitHub...${NC}"
git pull origin docker-deployment || { echo -e "${RED}Error: Git pull failed${NC}"; exit 1; }
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 3: Check .env file
echo -e "${YELLOW}Step 3: Checking .env file...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Creating template .env file..."
    cat > .env << 'EOF'
ENVIRONMENT=production
DEBUG=false
OPENROUTER_API_KEY=YOUR_KEY_HERE
FRONTEND_URL=http://YOUR_EC2_IP

POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=SecurePassword123!
POSTGRES_DB=pdfpixie
EOF
    echo -e "${YELLOW}⚠ Please edit .env file with your actual values!${NC}"
    echo "Run: nano .env"
    exit 1
fi

# Check if API key is set
if grep -q "YOUR_KEY_HERE" .env; then
    echo -e "${RED}Error: Please set your OPENROUTER_API_KEY in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env file exists and configured${NC}"
echo ""

# Step 4: Stop existing containers
echo -e "${YELLOW}Step 4: Stopping existing containers...${NC}"
docker-compose down -v || true
echo -e "${GREEN}✓ Old containers stopped${NC}"
echo ""

# Step 5: Clean up Docker
echo -e "${YELLOW}Step 5: Cleaning up Docker system...${NC}"
docker system prune -af --volumes || true
echo -e "${GREEN}✓ Docker cleaned${NC}"
echo ""

# Step 6: Build new image
echo -e "${YELLOW}Step 6: Building new image (this takes 5-10 minutes)...${NC}"
docker-compose build --no-cache app || { echo -e "${RED}Error: Build failed${NC}"; exit 1; }
echo -e "${GREEN}✓ Image built successfully${NC}"
echo ""

# Step 7: Start services
echo -e "${YELLOW}Step 7: Starting all services...${NC}"
docker-compose up -d || { echo -e "${RED}Error: Failed to start services${NC}"; exit 1; }
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Step 8: Wait for services to be ready
echo -e "${YELLOW}Step 8: Waiting for services to be healthy (60 seconds)...${NC}"
sleep 60
echo -e "${GREEN}✓ Wait complete${NC}"
echo ""

# Step 9: Check container status
echo -e "${YELLOW}Step 9: Checking container status...${NC}"
docker-compose ps
echo ""

# Step 10: Test health endpoint
echo -e "${YELLOW}Step 10: Testing health endpoint...${NC}"
if curl -sf http://localhost/health > /dev/null; then
    echo -e "${GREEN}✓ Health check passed!${NC}"
    curl http://localhost/health
    echo ""
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "Showing logs:"
    docker-compose logs app | tail -30
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Your app should be accessible at:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "Useful commands:"
echo "  docker-compose ps           # Check status"
echo "  docker-compose logs -f app  # View logs"
echo "  docker-compose restart app  # Restart app"
echo "  docker-compose down         # Stop all"
echo ""
