#!/bin/bash

# PDFPixie EC2 Deployment Script
# This script deploys the application using the existing Dockerfile with supervisor

set -e

echo "🚀 PDFPixie Deployment Starting..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo "Creating .env from template..."
    cat > .env << 'EOF'
ENVIRONMENT=production
DEBUG=false
OPENROUTER_API_KEY=your-api-key-here
FRONTEND_URL=http://localhost

POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=ChangeThisPassword123!
POSTGRES_DB=pdfpixie

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
EOF
    print_warning "Please edit .env file with your actual values!"
    print_warning "Then run: nano .env"
    exit 1
fi

# Stop existing containers
print_warning "Stopping existing containers..."
docker-compose down

# Remove old images (optional - uncomment to force rebuild)
# docker rmi pdfpixie-app 2>/dev/null || true

# Build the image
print_warning "Building Docker image (this may take 5-10 minutes)..."
docker-compose build --no-cache app

# Start all services
print_warning "Starting all services..."
docker-compose up -d

# Wait for services to be healthy
print_warning "Waiting for services to start..."
sleep 10

# Check container status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🔍 Checking health..."
sleep 5

# Test health endpoint
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "Application is healthy!"
else
    print_error "Application health check failed!"
    echo ""
    echo "📋 Recent logs:"
    docker-compose logs --tail=50 app
    exit 1
fi

echo ""
print_success "Deployment completed successfully!"
echo ""
echo "📝 Useful commands:"
echo "  View logs:        docker-compose logs -f app"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart app"
echo "  Check status:     docker-compose ps"
echo ""
echo "🌐 Access your application:"
echo "  Frontend:         http://$(curl -s ifconfig.me)"
echo "  API Docs:         http://$(curl -s ifconfig.me)/docs"
echo "  Health Check:     http://$(curl -s ifconfig.me)/health"
echo ""
