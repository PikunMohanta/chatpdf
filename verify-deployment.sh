#!/bin/bash
# PDFPixie EC2 Deployment Verification Script
# Run this after deployment to verify everything is working

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PDFPixie Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running on EC2
echo -e "\n${BLUE}[1] Checking Environment...${NC}"
if curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    print_success "Running on EC2 Instance: $INSTANCE_ID"
    print_info "Public IP: $PUBLIC_IP"
else
    print_info "Not running on EC2 (or metadata service not accessible)"
fi

# Check Docker installation
echo -e "\n${BLUE}[2] Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | tr -d ',')
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker not found! Install with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f4 | tr -d ',')
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose not found!"
    exit 1
fi

# Check if .env file exists
echo -e "\n${BLUE}[3] Checking Configuration...${NC}"
if [ -f .env ]; then
    print_success ".env file exists"
    
    # Check critical environment variables
    if grep -q "OPENROUTER_API_KEY=sk-or-v1-" .env; then
        print_success "OpenRouter API key configured"
    else
        print_error "OpenRouter API key not configured!"
    fi
    
    if grep -q "DOMAIN_NAME=" .env && ! grep -q "DOMAIN_NAME=your-subdomain" .env; then
        DOMAIN=$(grep "DOMAIN_NAME=" .env | cut -d'=' -f2)
        print_success "Domain configured: $DOMAIN"
    else
        print_info "Domain not configured (using localhost)"
    fi
    
    if grep -q "POSTGRES_PASSWORD=.*CHANGE_THIS" .env; then
        print_error "PostgreSQL password still has default value! Change it for security."
    else
        print_success "PostgreSQL password customized"
    fi
else
    print_error ".env file not found! Copy from .env.production"
    exit 1
fi

# Check Docker containers
echo -e "\n${BLUE}[4] Checking Docker Containers...${NC}"
if docker-compose ps | grep -q "Up"; then
    print_success "Docker containers are running"
    
    # Check individual containers
    if docker-compose ps | grep "pdfpixie-app" | grep -q "Up"; then
        print_success "App container: Running"
    else
        print_error "App container: Not running"
    fi
    
    if docker-compose ps | grep "pdfpixie-postgres" | grep -q "Up"; then
        print_success "PostgreSQL container: Running"
    else
        print_error "PostgreSQL container: Not running"
    fi
    
    if docker-compose ps | grep "pdfpixie-redis" | grep -q "Up"; then
        print_success "Redis container: Running"
    else
        print_error "Redis container: Not running"
    fi
else
    print_error "No containers running! Start with: docker-compose up -d"
    exit 1
fi

# Check health endpoints
echo -e "\n${BLUE}[5] Checking Health Endpoints...${NC}"

# Backend health check
if curl -sf http://localhost/health > /dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost/health)
    print_success "Backend health: $HEALTH_RESPONSE"
else
    print_error "Backend health check failed!"
fi

# Nginx health check
if curl -sf http://localhost/nginx-health > /dev/null 2>&1; then
    print_success "Nginx health: OK"
else
    print_info "Nginx health endpoint not accessible (might be normal)"
fi

# Check PDF worker file
if curl -sf -I http://localhost/pdf.worker.min.js | grep -q "200 OK"; then
    print_success "PDF worker file accessible"
else
    print_error "PDF worker file not accessible (PDF viewer won't work!)"
fi

# Check disk space
echo -e "\n${BLUE}[6] Checking System Resources...${NC}"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Disk usage: ${DISK_USAGE}% (healthy)"
else
    print_error "Disk usage: ${DISK_USAGE}% (low space!)"
fi

# Check memory
MEMORY_TOTAL=$(free -h | grep Mem | awk '{print $2}')
MEMORY_USED=$(free -h | grep Mem | awk '{print $3}')
print_info "Memory: $MEMORY_USED / $MEMORY_TOTAL"

# Check Docker volumes
echo -e "\n${BLUE}[7] Checking Data Persistence...${NC}"
if docker volume ls | grep -q "chatpdf_postgres_data"; then
    print_success "PostgreSQL data volume exists"
fi
if docker volume ls | grep -q "chatpdf_redis_data"; then
    print_success "Redis data volume exists"
fi
if docker volume ls | grep -q "chatpdf_app_data"; then
    print_success "App data volume exists"
fi

# Check DuckDNS (if configured)
echo -e "\n${BLUE}[8] Checking Domain Configuration...${NC}"
if [ -f update-duckdns.sh ]; then
    if grep -q "your-subdomain" update-duckdns.sh || grep -q "your-duckdns-token" update-duckdns.sh; then
        print_info "DuckDNS not configured yet (update update-duckdns.sh)"
    else
        DUCKDNS_DOMAIN=$(grep "DUCKDNS_DOMAIN=" update-duckdns.sh | cut -d'"' -f2)
        FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
        
        # Check DNS resolution
        if command -v dig &> /dev/null; then
            DNS_IP=$(dig +short $FULL_DOMAIN | tail -1)
            if [ ! -z "$DNS_IP" ]; then
                print_success "DuckDNS resolves to: $DNS_IP"
                if [ "$DNS_IP" == "$PUBLIC_IP" ]; then
                    print_success "DNS matches EC2 public IP!"
                else
                    print_info "DNS IP ($DNS_IP) differs from EC2 IP ($PUBLIC_IP)"
                fi
            else
                print_error "Domain not resolving: $FULL_DOMAIN"
            fi
        fi
    fi
fi

# Test database connection
echo -e "\n${BLUE}[9] Testing Database Connection...${NC}"
if docker-compose exec -T postgres psql -U pdfpixie_user -d pdfpixie -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "PostgreSQL connection successful"
else
    print_error "Cannot connect to PostgreSQL"
fi

# Test Redis connection
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis connection successful"
else
    print_error "Cannot connect to Redis"
fi

# Check recent logs for errors
echo -e "\n${BLUE}[10] Checking for Recent Errors...${NC}"
ERROR_COUNT=$(docker-compose logs --tail=100 app 2>/dev/null | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    print_info "Found $ERROR_COUNT error messages in recent logs"
    echo -e "${YELLOW}Run 'docker-compose logs app' to investigate${NC}"
else
    print_success "No recent errors in application logs"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ ! -z "$PUBLIC_IP" ]; then
    echo -e "\n${GREEN}Access your application at:${NC}"
    echo -e "  ${BLUE}http://${PUBLIC_IP}${NC}"
fi

if [ ! -z "$FULL_DOMAIN" ] && [ ! -z "$DNS_IP" ]; then
    echo -e "  ${BLUE}http://${FULL_DOMAIN}${NC}"
fi

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  ${BLUE}docker-compose logs -f app${NC}    # View logs"
echo -e "  ${BLUE}docker-compose ps${NC}              # Check status"
echo -e "  ${BLUE}docker-compose restart${NC}         # Restart all"
echo -e "  ${BLUE}curl http://localhost/health${NC}  # Test backend"

echo -e "\n${GREEN}✅ Verification complete!${NC}\n"
