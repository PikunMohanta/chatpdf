# 🚀 PDFPixie - Complete AWS Deployment Guide
## One-Document Guide: From Zero to Production

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [AWS EC2 Setup](#aws-ec2-setup)
4. [Server Configuration](#server-configuration)
5. [Application Deployment](#application-deployment)
6. [Domain & SSL Setup](#domain--ssl-setup)
7. [Testing & Verification](#testing--verification)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Overview

This guide will help you deploy PDFPixie on a fresh AWS EC2 instance. The application includes:
- ✅ React frontend with Vite
- ✅ FastAPI backend with Socket.IO
- ✅ ChromaDB for vector storage
- ✅ PostgreSQL for chat history (via Docker)
- ✅ Nginx reverse proxy
- ✅ Multi-device access support

**Deployment Time**: ~45 minutes  
**Cost**: Free (12 months) or $20-30/month after

---

## Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (with credit card)
- [ ] OpenRouter API Key (get from https://openrouter.ai/)
- [ ] GitHub account (optional, for code updates)
- [ ] SSH client (Windows: PowerShell/Git Bash, Mac/Linux: Terminal)
- [ ] Domain name (optional - can use IP address)
- [ ] 45 minutes of time

---

## AWS EC2 Setup

### Step 1: Launch EC2 Instance

1. **Go to AWS Console**
   ```
   https://console.aws.amazon.com/ec2/
   ```

2. **Click "Launch Instance"** (orange button)

3. **Configure Instance**:
   ```
   Name: pdfpixie-production
   
   AMI: Ubuntu Server 24.04 LTS (HVM)
   ✅ 64-bit (x86)
   ✅ Free tier eligible
   
   Instance Type: t3.micro
   ✅ Free tier eligible (12 months)
   ℹ️ Or use t3.small for better performance ($17/month)
   ```

4. **Create Key Pair** (IMPORTANT!):
   ```
   Click: "Create new key pair"
   Name: pdfpixie-key
   Type: RSA
   Format: .pem
   
   ⬇️ Downloads to: ~/Downloads/pdfpixie-key.pem
   ⚠️ SAVE THIS FILE - You need it to access the server!
   ```

5. **Network Settings**:
   ```
   ✅ Create security group
   Name: pdfpixie-sg
   Description: PDFPixie Application Security Group
   
   Inbound Rules:
   ┌──────────────────────────────────────────────────┐
   │ Type          │ Port  │ Source    │ Description  │
   ├──────────────────────────────────────────────────┤
   │ SSH           │ 22    │ My IP     │ SSH access   │
   │ HTTP          │ 80    │ 0.0.0.0/0 │ Web traffic  │
   │ HTTPS         │ 443   │ 0.0.0.0/0 │ SSL traffic  │
   │ Custom TCP    │ 8000  │ 0.0.0.0/0 │ API (temp)   │
   └──────────────────────────────────────────────────┘
   ```

6. **Storage**:
   ```
   Volume Type: gp3 (General Purpose SSD)
   Size: 30 GB
   ✅ Free tier eligible
   ```

7. **Click "Launch Instance"**

8. **Get Public IP**:
   ```
   Wait 1-2 minutes for instance to start
   Go to: EC2 Dashboard → Instances
   Click on: pdfpixie-production
   Copy: Public IPv4 address (e.g., 13.201.129.219)
   
   📝 Save this IP - you'll need it!
   ```

---

### Step 2: Connect to EC2

**Windows (PowerShell or Git Bash)**:
```bash
# Navigate to downloads
cd ~/Downloads

# Fix key permissions (PowerShell)
icacls pdfpixie-key.pem /inheritance:r /grant:r "%username%:F"

# Connect via SSH (replace with YOUR IP)
ssh -i pdfpixie-key.pem ubuntu@13.201.129.219

# Type 'yes' when prompted
```

**Mac/Linux (Terminal)**:
```bash
# Navigate to downloads
cd ~/Downloads

# Fix key permissions
chmod 400 pdfpixie-key.pem

# Connect via SSH (replace with YOUR IP)
ssh -i pdfpixie-key.pem ubuntu@13.201.129.219

# Type 'yes' when prompted
```

**Expected Output**:
```
Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.8.0-1013-aws x86_64)
ubuntu@ip-172-31-xx-xx:~$
```

✅ **You're now connected to your AWS server!**

---

## Server Configuration

### Step 3: Install Docker & Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker and basic tools
sudo apt install -y docker.io docker-compose git curl wget

# Add user to docker group (no sudo needed)
sudo usermod -aG docker ubuntu

# Apply group changes
newgrp docker

# Install Node.js 20.x (required for frontend build)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
docker --version
# Expected: Docker version 24.0.x

docker-compose --version
# Expected: docker-compose version 1.29.x

git --version
# Expected: git version 2.43.x

node --version
# Expected: v20.x.x

npm --version
# Expected: 10.x.x
```

### Step 4: Clone Repository

```bash
# Create app directory
mkdir -p ~/apps && cd ~/apps

# Clone your repository
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf

# Switch to deployment branch
git checkout docker-deployment

# Verify files
ls -la
# Should see: Dockerfile, deploy.sh, nginx/, frontend/, backend/
```

---

## Application Deployment

### Step 5: Configure Environment

**Create `.env` file**:
```bash
cat > .env << 'EOF'
# Your OpenRouter API Key (REQUIRED - get from https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Environment
ENVIRONMENT=production
DEBUG=false

# Database (auto-configured in Docker)
DATABASE_URL=postgresql://pdfpixie_user:pdfpixie_pass@localhost:5432/pdfpixie

# Optional: AWS S3 (leave empty if not using)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
EOF
```

**⚠️ IMPORTANT: Update the OPENROUTER_API_KEY with your actual key!**

```bash
# Edit the file
nano .env

# Change this line:
# OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Press Ctrl+O to save, Enter, then Ctrl+X to exit
```

### Step 6: Deploy Application

```bash
# Make deploy script executable
chmod +x deploy.sh

# Export API key for current session
export OPENROUTER_API_KEY="your-key-here"

# Run deployment script
./deploy.sh
```

**What the script does**:
```
1. ✅ Builds frontend (npm run build)
2. ✅ Creates Docker image with Nginx + FastAPI
3. ✅ Stops old container (if exists)
4. ✅ Starts new container
5. ✅ Runs health checks
6. ✅ Shows access URLs
```

**Expected Output**:
```
🚀 PDFPixie Deployment Script
==============================

📦 Step 1: Building frontend with production config...
✅ Frontend built successfully

🐳 Step 2: Building Docker image...
✅ Docker image built successfully

🛑 Step 3: Stopping old container...
✅ Old container removed

▶️  Step 4: Starting new container...
✅ Container started

⏳ Step 5: Waiting for application to be healthy...
✅ Application is healthy!

🎉 Deployment Complete!
==============================

🌐 Access Your Application:
   • By IP:     http://13.201.129.219
   • By Domain: http://pdfpixie.duckdns.org
```

---

### Step 7: Verify Deployment

```bash
# Check container is running
docker ps | grep pdfpixie
# Should show: pdfpixie container with ports 80:80, 8000:8000

# Test health endpoint
curl http://localhost/health
# Expected: {"status":"healthy","service":"pdfpixie-api"}

# View logs
docker logs pdfpixie --tail 50
# Should show: Nginx started, FastAPI running
```

---

## Domain & SSL Setup

### Step 8: Configure Domain (Choose One)

#### Option A: Use IP Address (Quick Start)
```
✅ Your app is accessible at: http://13.201.129.219
ℹ️ No additional setup needed
⚠️ Not recommended for production
```

#### Option B: DuckDNS Free Domain (Recommended)

1. **Get Free Domain**:
   ```
   1. Go to: https://www.duckdns.org/
   2. Login with GitHub
   3. Create subdomain: pdfpixie
   4. Update IP: 13.201.129.219 (YOUR EC2 IP)
   5. Copy your token
   ```

2. **Update Frontend Config**:
   ```bash
   # Edit production environment
   nano frontend/.env.production
   
   # Change these lines:
   VITE_API_BASE_URL=http://pdfpixie.duckdns.org
   VITE_WS_URL=http://pdfpixie.duckdns.org
   
   # Save: Ctrl+O, Enter, Ctrl+X
   ```

3. **Rebuild & Deploy**:
   ```bash
   ./deploy.sh
   ```

4. **Test Domain**:
   ```bash
   # From your local computer
   ping pdfpixie.duckdns.org
   # Should return: 13.201.129.219
   
   # Open in browser
   http://pdfpixie.duckdns.org
   ```

#### Option C: Custom Domain (Namecheap, GoDaddy, etc.)

1. **Register domain** (e.g., your-app.com)

2. **Add DNS A Record**:
   ```
   Host: @
   Type: A
   Value: 13.201.129.219 (YOUR EC2 IP)
   TTL: 3600
   ```

3. **Wait 24-48 hours** for DNS propagation

4. **Update frontend config** (same as Option B)

---

### Step 9: Add HTTPS/SSL (Optional but Recommended)

**Prerequisites**:
- ✅ Domain configured (DuckDNS or custom)
- ✅ Domain resolves to your EC2 IP

```bash
# Stop container temporarily
docker stop pdfpixie

# Install Certbot
sudo apt update
sudo apt install -y certbot

# Get SSL certificate (replace with YOUR domain)
sudo certbot certonly --standalone -d pdfpixie.duckdns.org

# Follow prompts:
# Email: your-email@example.com
# Agree to terms: (A)
# Newsletter: (N)

# Verify certificate
sudo ls -la /etc/letsencrypt/live/pdfpixie.duckdns.org/
# Should show: fullchain.pem, privkey.pem

# Update Nginx config
nano nginx/conf.d/pdfpixie.conf

# Find line 40-41 and update:
# FROM:
# ssl_certificate /etc/letsencrypt/live/your-domain/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain/privkey.pem;

# TO:
# ssl_certificate /etc/letsencrypt/live/pdfpixie.duckdns.org/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/pdfpixie.duckdns.org/privkey.pem;

# Save: Ctrl+O, Enter, Ctrl+X

# Update frontend to use HTTPS
nano frontend/.env.production

# Change:
VITE_API_BASE_URL=https://pdfpixie.duckdns.org
VITE_WS_URL=https://pdfpixie.duckdns.org

# Rebuild with HTTPS support
cd frontend && npm run build && cd ..

# Deploy with SSL certificates
docker build -t pdfpixie:latest -f Dockerfile .
docker run -d \
  --name pdfpixie \
  -p 80:80 \
  -p 443:443 \
  -p 8000:8000 \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  -v $(pwd)/backend/data:/app/data \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  --restart unless-stopped \
  pdfpixie:latest

# Test HTTPS
curl https://pdfpixie.duckdns.org/health
# Expected: {"status":"healthy"}

# Setup auto-renewal
sudo certbot renew --dry-run
# Expected: Congratulations, all simulated renewals succeeded
```

---

## Testing & Verification

### Step 10: Complete Testing

#### Test 1: Health Check
```bash
# From EC2
curl http://localhost/health

# From your computer (replace with your IP/domain)
curl http://13.201.129.219/health
curl http://pdfpixie.duckdns.org/health

# Expected: {"status":"healthy","service":"pdfpixie-api"}
```

#### Test 2: Frontend Access
```
1. Open browser
2. Go to: http://13.201.129.219 (or your domain)
3. Should see: PDFPixie welcome screen
4. Open DevTools (F12) → Network tab
5. Should see: No errors, requests to correct IP/domain
```

#### Test 3: Full Workflow
```
1. Upload a PDF file
   ✅ Upload progress shows
   ✅ File processes successfully
   
2. Ask a question about the PDF
   ✅ AI responds
   ✅ Sources show page numbers
   
3. Test from mobile device
   ✅ Open http://your-ip on phone
   ✅ Upload and chat work
   
4. Test WebSocket connection
   ✅ Real-time responses
   ✅ No connection errors in console
```

#### Test 4: Multi-Device Access
```bash
# From different devices:
- ✅ Your computer: http://13.201.129.219
- ✅ Your phone: http://13.201.129.219
- ✅ Tablet: http://13.201.129.219
- ✅ Friend's device: http://pdfpixie.duckdns.org

All should work without "Failed to fetch" errors!
```

---

## Troubleshooting

### Issue 1: "Failed to fetch" from other devices

**Symptoms**: Works on server, fails on phone/other computers

**Cause**: Frontend still using localhost URLs

**Fix**:
```bash
# Check frontend build
docker exec pdfpixie cat /var/www/html/index.html | grep -o 'http://[^"]*' | head -5

# Should show YOUR IP (13.201.129.219), NOT localhost

# If showing localhost, rebuild:
cd ~/apps/chatpdf
cd frontend && npm run build && cd ..
docker build --no-cache -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie
./deploy.sh
```

### Issue 2: Container won't start

**Symptoms**: `docker ps` shows no pdfpixie container

**Fix**:
```bash
# Check logs
docker logs pdfpixie

# Common issues:
# 1. Port 80 in use
sudo lsof -i :80
# Kill conflicting process or stop nginx

# 2. API key not set
echo $OPENROUTER_API_KEY
# If empty: export OPENROUTER_API_KEY="your-key"

# 3. Rebuild from scratch
docker stop pdfpixie 2>/dev/null
docker rm pdfpixie 2>/dev/null
docker rmi pdfpixie:latest 2>/dev/null
./deploy.sh
```

### Issue 3: SSL Certificate Errors

**Symptoms**: "Your connection is not private" or certificate errors

**Fix**:
```bash
# Check certificate
sudo certbot certificates

# Renew if expired
sudo certbot renew --force-renewal

# Check Nginx config
docker exec pdfpixie cat /etc/nginx/conf.d/pdfpixie.conf | grep ssl_certificate

# Should point to correct domain files
```

### Issue 4: WebSocket Connection Failed

**Symptoms**: Chat not working, console shows WebSocket errors

**Fix**:
```bash
# Test WebSocket endpoint
curl -i http://13.201.129.219/socket.io/

# Should return HTTP 200

# Check logs
docker logs pdfpixie | grep -i socket

# Restart container
docker restart pdfpixie
```

### Issue 5: Out of Disk Space

**Symptoms**: "No space left on device" errors

**Fix**:
```bash
# Check disk usage
df -h

# If > 90% full, clean up:
# Remove old Docker images
docker image prune -a -f

# Remove old Docker volumes
docker volume prune -f

# Remove unused containers
docker container prune -f

# Clean up system
sudo apt autoremove -y
sudo apt clean
```

---

## Maintenance

### Daily Checks

```bash
# Check container is running
docker ps | grep pdfpixie

# Check disk space
df -h

# Check logs for errors
docker logs pdfpixie --tail 50 | grep ERROR
```

### Weekly Tasks

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart container
docker restart pdfpixie

# Check SSL certificate
sudo certbot certificates
```

### Monthly Tasks

```bash
# Backup data
docker exec pdfpixie tar -czf /app/backup-$(date +%Y%m%d).tar.gz /app/data

# Copy backup to local
docker cp pdfpixie:/app/backup-$(date +%Y%m%d).tar.gz ~/backups/

# Clean old logs
docker logs pdfpixie --tail 1000 > ~/logs/app-$(date +%Y%m%d).log
```

### Updating Application

```bash
# On your local machine, after making changes:
git add .
git commit -m "Update application"
git push origin docker-deployment

# On AWS instance:
cd ~/apps/chatpdf
git pull origin docker-deployment
./deploy.sh
```

---

## Quick Reference Commands

### Container Management
```bash
docker ps                              # List running containers
docker logs pdfpixie -f                # View live logs
docker restart pdfpixie                # Restart container
docker stop pdfpixie                   # Stop container
docker start pdfpixie                  # Start container
docker exec -it pdfpixie /bin/bash     # Shell access
```

### Application Access
```bash
# Health check
curl http://localhost/health

# API documentation
http://your-ip:8000/docs

# Frontend
http://your-ip or http://your-domain
```

### Logs & Debugging
```bash
# Application logs
docker logs pdfpixie --tail 100

# Nginx access logs
docker exec pdfpixie tail -f /var/log/nginx/access.log

# Nginx error logs
docker exec pdfpixie tail -f /var/log/nginx/error.log

# System resources
htop                                   # Interactive monitor
docker stats                           # Container resources
```

### SSL/Domain
```bash
# Check certificates
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## Cost Management

### Monitor Costs
```
1. Go to: AWS Console → Billing Dashboard
2. Check: Current charges
3. Set up: Budget alerts ($20/month threshold)
```

### Optimize Costs
```bash
# Use t3.micro (free tier) instead of t3.small
# Saves: $17/month

# Don't use Elastic IP unless needed
# Saves: $3.60/month if unattached

# Use gp2 instead of gp3 storage (free tier)
# Saves: Included in free tier

# Total free tier: $0/month for 12 months
# Total after free tier: ~$20-25/month
```

---

## Security Checklist

- [ ] SSH key-only access (no passwords)
- [ ] UFW firewall enabled
- [ ] Security group limits SSH to your IP
- [ ] SSL certificate installed (HTTPS)
- [ ] Regular system updates
- [ ] Strong database password
- [ ] API keys in environment variables (not code)
- [ ] Regular backups

---

## Support Resources

**Documentation**:
- This guide: Complete setup walkthrough
- AWS_DEPLOYMENT_GUIDE.md: Detailed reference
- QUICK_DEPLOY.md: Quick command reference
- FIX_SUMMARY.md: Technical changes summary

**Getting Help**:
```bash
# Check logs first
docker logs pdfpixie -f

# Test connectivity
curl -v http://localhost/health

# System status
docker ps
df -h
free -h
```

**Common URLs**:
- AWS Console: https://console.aws.amazon.com/
- DuckDNS: https://www.duckdns.org/
- OpenRouter: https://openrouter.ai/
- Let's Encrypt: https://letsencrypt.org/

---

## Success Checklist

### Deployment Complete When:
- [ ] EC2 instance running and accessible
- [ ] Docker installed and working
- [ ] Application deployed and container running
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads in browser (no console errors)
- [ ] PDF upload works from your computer
- [ ] PDF upload works from phone/tablet
- [ ] Chat responses work correctly
- [ ] Domain configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Multi-device access verified

---

## 🎉 Congratulations!

Your PDFPixie application is now:
- ✅ Running on AWS EC2
- ✅ Accessible from any device
- ✅ Production-ready
- ✅ Secure (with SSL)
- ✅ Cost-effective ($0-30/month)

**Access Your App**:
- 🌐 IP: http://13.201.129.219
- 🌐 Domain: http://pdfpixie.duckdns.org
- 📚 API Docs: http://13.201.129.219:8000/docs

**Next Steps**:
1. Share URL with users
2. Monitor usage and costs
3. Set up regular backups
4. Consider custom domain
5. Add analytics (optional)

---

**Questions or Issues?**  
Check the Troubleshooting section or review logs with `docker logs pdfpixie -f`

**Last Updated**: November 1, 2025  
**Version**: 1.0 (Multi-device fix included)
