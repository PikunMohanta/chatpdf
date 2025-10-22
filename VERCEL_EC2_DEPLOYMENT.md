# PDFPixie - Vercel + AWS EC2 Deployment Guide

## 🚀 **Production-Ready Architecture**

```
┌─────────────────────────┐
│   Vercel (Frontend)     │
│   - React App           │
│   - Global CDN          │
│   - Auto-deploy         │
└────────────┬────────────┘
             │ HTTPS
             ↓
        Domain DNS
             ↓
    ┌───────────────────┐
    │  AWS EC2 Instance │
    │  (All-in-One)     │
    ├───────────────────┤
    │  Frontend Files   │
    │  (Static HTML)    │
    │  Nginx (port 80,  │
    │  443)             │
    │                   │
    │  Backend API      │
    │  FastAPI (port    │
    │  8000)            │
    │  Socket.IO        │
    │                   │
    │  PostgreSQL       │
    │  (Local or RDS)   │
    │                   │
    │  Redis Cache      │
    │  ChromaDB         │
    │  Vector Store     │
    └───────────────────┘
             ↓
        AWS S3 (PDFs)
```

---

## 💰 **Cost Breakdown**

### **Free Tier (12 Months)**
```
✅ EC2 t3.micro:          $0 (750 hrs/month)
✅ 30GB EBS Storage:      $0 (free tier)
✅ Vercel Frontend:       $0 (free tier)
✅ Local PostgreSQL:      $0 (runs on EC2)
✅ Local Redis:           $0 (runs on EC2)
───────────────────────────
   TOTAL:                 $0/month
```

### **After Free Tier (Monthly)**
```
💰 EC2 t3.micro:          $9-12/month
💰 EC2 t3.small:          $17-20/month (recommended)
💰 30GB EBS Storage:      $2-3/month
💰 Data Transfer:         $0-5/month (if within AWS)
💰 Elastic IP:            $0 (free if attached) or $3.60/month
💰 Vercel Frontend:       $0 (free tier)
💰 S3 Storage (100GB):    $2.30/month
───────────────────────────
   TOTAL:                 $30-50/month
```

---

## 📋 **Prerequisites**

- ✅ AWS Account (with credit card for free tier)
- ✅ GitHub account (for code deployment)
- ✅ Domain name (optional, can use EC2 public IP)
- ✅ Your laptop with terminal/SSH client
- ✅ Git installed locally
- ✅ Vercel account (free)

---

## 🔧 **PHASE 1: AWS EC2 Setup (45 minutes)**

### **Step 1.1: Launch EC2 Instance**

**1. Go to AWS Console**
```
1. Open: https://console.aws.amazon.com
2. Search for "EC2" in the search bar
3. Click "EC2" from results
```

**2. Launch Instance**
```
1. Click "Launch Instance" (orange button)
2. Name: pdfpixie-backend
3. AMI (Amazon Machine Image):
   - Search: "Ubuntu 24.04 LTS"
   - Select "Ubuntu Server 24.04 LTS (HVM)"
   - ✅ Free tier eligible
4. Instance Type: t3.micro (FREE TIER)
   - If not free tier, select t3.micro anyway
5. Key Pair:
   - Click "Create new key pair"
   - Name: pdfpixie-key
   - Format: .pem
   - ⬇️ Download and SAVE in safe location
6. Network:
   - VPC: default
   - Auto-assign public IP: Enable
7. Security Group (NEW):
   - Name: pdfpixie-sg
   - Rules: (Add these)
     * SSH (22) from MY IP only
     * HTTP (80) from 0.0.0.0/0 (anywhere)
     * HTTPS (443) from 0.0.0.0/0 (anywhere)
8. Storage:
   - 30GB gp2 (free tier eligible)
9. Click "Launch Instance"
```

**3. Get Instance Public IP**
```
1. Go to EC2 Dashboard → Instances
2. Select your instance (pdfpixie-backend)
3. Copy the Public IPv4 address
   Example: 54.123.45.67
```

---

### **Step 1.2: Connect to EC2 via SSH**

**On Windows (using PowerShell or Git Bash):**
```bash
# Navigate to where you saved pdfpixie-key.pem
cd ~/Downloads

# Change permissions
icacls pdfpixie-key.pem /inheritance:r

# SSH into instance
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67
```

**On macOS/Linux:**
```bash
# Change permissions
chmod 400 pdfpixie-key.pem

# SSH into instance
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67
```

**First time connection:**
```
Are you sure you want to continue connecting (yes/no)? → yes
```

---

### **Step 1.3: Initial System Setup**

Once connected to EC2, run these commands:

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required software
sudo apt install -y \
  python3.12 \
  python3-pip \
  python3-venv \
  python3.12-venv \
  nodejs \
  npm \
  nginx \
  postgresql \
  postgresql-contrib \
  git \
  curl \
  wget \
  vim \
  supervisor

# Verify installations
python3 --version    # Should show 3.12
node --version       # Should show v18+
nginx -v             # Should show nginx version
```

---

## 🗄️ **PHASE 2: Database Setup (30 minutes)**

### **Option A: Local PostgreSQL (Simpler, Recommended for MVP)**

**Step 2A.1: Setup PostgreSQL**

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << 'EOF'
-- Create database
CREATE DATABASE pdfpixie;

-- Create user
CREATE USER pdfpixie_user WITH PASSWORD 'YourSecurePassword123!';

-- Grant privileges
ALTER ROLE pdfpixie_user SET client_encoding TO 'utf8';
ALTER ROLE pdfpixie_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pdfpixie_user SET default_transaction_deferrable TO on;
ALTER ROLE pdfpixie_user SET default_time_zone TO 'UTC';

-- Grant database permissions
GRANT ALL PRIVILEGES ON DATABASE pdfpixie TO pdfpixie_user;

-- Connect to database
\c pdfpixie

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO pdfpixie_user;

-- Verify
\du
\l

-- Exit
\q
EOF

# Verify connection
psql -U pdfpixie_user -d pdfpixie -h localhost -c "SELECT version();"
```

**Step 2A.2: Enable Remote Access (Optional)**

If you want to access database from your laptop:

```bash
# Edit PostgreSQL config
sudo vim /etc/postgresql/*/main/postgresql.conf

# Find and change:
# listen_addresses = 'localhost'  →  listen_addresses = '*'

# Edit pg_hba.conf
sudo vim /etc/postgresql/*/main/pg_hba.conf

# Add at the end:
# host    all             all             0.0.0.0/0               md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Step 2A.3: Create .env with Database URL**

```bash
# Save this DATABASE_URL for later
# Format: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
# Local: postgresql://pdfpixie_user:YourSecurePassword123!@localhost:5432/pdfpixie

echo "DATABASE_URL=postgresql://pdfpixie_user:YourSecurePassword123!@localhost:5432/pdfpixie"
```

---

### **Option B: AWS RDS PostgreSQL (More Reliable, Paid)**

**Skip if using local PostgreSQL above.**

**Step 2B.1: Create RDS Instance**

```
1. Go to AWS Console → RDS
2. Click "Create Database"
3. Engine: PostgreSQL → Version 15
4. Templates: Free tier
5. DB Instance identifier: pdfpixie-db
6. Master username: admin
7. Master password: (create strong password)
8. Instance class: db.t3.micro (FREE)
9. Storage: 20GB, gp2 (FREE)
10. Multi-AZ: Disabled (save cost)
11. VPC: default
12. Publicly accessible: Yes (for testing)
13. Create database
```

**Step 2B.2: Get RDS Endpoint**

```
1. Go to RDS Dashboard → Databases
2. Select pdfpixie-db
3. Copy Endpoint
   Example: pdfpixie-db.xxxxx.rds.amazonaws.com
4. Port: 5432
```

**Step 2B.3: Create Database URL**

```
Format: postgresql://admin:PASSWORD@pdfpixie-db.xxxxx.rds.amazonaws.com:5432/pdfpixie

Example: postgresql://admin:YourPassword@pdfpixie-db.us-east-1.rds.amazonaws.com:5432/pdfpixie
```

---

## 📦 **PHASE 3: Deploy Backend (1 hour)**

### **Step 3.1: Clone Repository**

```bash
# Create app directory
mkdir -p /home/ubuntu/apps
cd /home/ubuntu/apps

# Clone your repository
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf/backend

# Verify structure
ls -la
# Should show: app/, main.py, requirements.txt, pyproject.toml
```

---

### **Step 3.2: Setup Python Virtual Environment**

```bash
# Navigate to backend
cd /home/ubuntu/apps/chatpdf/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

---

### **Step 3.3: Create Environment Configuration**

```bash
# Create .env file in backend directory
cat > /home/ubuntu/apps/chatpdf/backend/.env << 'EOF'
# Environment
ENVIRONMENT=production
IS_PRODUCTION=true

# Database URL
# LOCAL: postgresql://pdfpixie_user:YourPassword@localhost:5432/pdfpixie
# RDS: postgresql://admin:YourPassword@pdfpixie-db.xxxxx.rds.amazonaws.com:5432/pdfpixie
DATABASE_URL=postgresql://pdfpixie_user:YourSecurePassword123!@localhost:5432/pdfpixie

# API Keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Frontend URLs
FRONTEND_URL=https://pdfpixie.vercel.app

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=pdfpixie-documents

# Optional settings
LOG_LEVEL=INFO
DEBUG=false
EOF

# Verify
cat .env
```

**Important:** Replace placeholder values with actual keys!

---

### **Step 3.4: Test Backend Locally**

```bash
# Ensure venv is activated
source /home/ubuntu/apps/chatpdf/backend/venv/bin/activate

# Run the app
cd /home/ubuntu/apps/chatpdf/backend
python -m uvicorn main:socket_app --host 0.0.0.0 --port 8000

# Output should show:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test the health endpoint:**

Open a new terminal/SSH session:
```bash
# From your laptop or new EC2 terminal
curl http://54.123.45.67:8000/health

# Should return:
# {"status":"healthy","service":"pdfpixie-api"}
```

**Press Ctrl+C** to stop the test server.

---

### **Step 3.5: Configure Gunicorn (Production Server)**

```bash
# Install Gunicorn
source /home/ubuntu/apps/chatpdf/backend/venv/bin/activate
pip install gunicorn

# Test with Gunicorn
cd /home/ubuntu/apps/chatpdf/backend
gunicorn -w 4 -b 0.0.0.0:8000 main:socket_app

# Should show:
# [INFO] listening at: http://0.0.0.0:8000
# [INFO] Using worker: uvicorn.workers.UvicornWorker
# [INFO] 4 workers
```

**Press Ctrl+C** to stop.

---

### **Step 3.6: Create Supervisor Service (Auto-start & Monitor)**

Supervisor will automatically start your app and restart if it crashes.

```bash
# Create supervisor config
sudo tee /etc/supervisor/conf.d/pdfpixie.conf > /dev/null << 'EOF'
[program:pdfpixie]
# Working directory
directory=/home/ubuntu/apps/chatpdf/backend

# Command to run
command=/home/ubuntu/apps/chatpdf/backend/venv/bin/gunicorn \
  -w 4 \
  -b 127.0.0.1:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120 \
  --access-logfile /var/log/pdfpixie/access.log \
  --error-logfile /var/log/pdfpixie/error.log \
  main:socket_app

# Autostart when system boots
autostart=true

# Restart if crashes
autorestart=true

# Restart if memory exceeds 200MB
memmon-group-include=pdfpixie
memory_limit=200M

# User to run as
user=ubuntu

# Environment variables
environment=PATH="/home/ubuntu/apps/chatpdf/backend/venv/bin"

# Logging
stdout_logfile=/var/log/pdfpixie/stdout.log
stderr_logfile=/var/log/pdfpixie/stderr.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10

# Process name
process_name=%(program_name)s_%(process_num)02d
numprocs=1
EOF

# Create log directory
sudo mkdir -p /var/log/pdfpixie
sudo chown ubuntu:ubuntu /var/log/pdfpixie

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start the service
sudo supervisorctl start pdfpixie

# Verify it's running
sudo supervisorctl status pdfpixie

# Should show: pdfpixie                 RUNNING   pid 1234, uptime 0:00:10
```

---

### **Step 3.7: Verify Backend is Running**

```bash
# Check if listening on port 8000
netstat -tuln | grep 8000

# Should show:
# tcp        0      0 127.0.0.1:8000      0.0.0.0:*       LISTEN

# Check supervisor status
sudo supervisorctl tail pdfpixie

# Test health endpoint (from another SSH session)
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"pdfpixie-api"}
```

---

## 🌐 **PHASE 4: Configure Nginx (Web Server & Proxy)**

### **Step 4.1: Create Nginx Configuration**

```bash
# Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Create new config
sudo tee /etc/nginx/sites-available/pdfpixie > /dev/null << 'EOF'
# Upstream backend
upstream pdfpixie_backend {
    server 127.0.0.1:8000;
}

# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name _;
    
    location / {
        return 301 https://$host$request_uri;
    }
    
    # Allow certbot challenges
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

# HTTPS main server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name _;
    
    # SSL certificates (will add after certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Logging
    access_log /var/log/nginx/pdfpixie_access.log;
    error_log /var/log/nginx/pdfpixie_error.log;
    
    # API endpoints → FastAPI
    location /api/ {
        proxy_pass http://pdfpixie_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
    
    # WebSocket endpoints
    location /socket.io {
        proxy_pass http://pdfpixie_backend/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Health check
    location /health {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
    }
    
    # API docs
    location /docs {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
    }
    
    # Root path
    location / {
        return 404;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/pdfpixie /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Should show:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### **Step 4.2: Start Nginx**

```bash
# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify it's running
sudo systemctl status nginx

# Check if listening on ports 80, 443
sudo netstat -tuln | grep -E ':(80|443)'
```

---

### **Step 4.3: Test Nginx (Without SSL yet)**

```bash
# Test from your laptop
curl http://54.123.45.67/health

# Should return:
# {"status":"healthy","service":"pdfpixie-api"}
```

---

## 🔒 **PHASE 5: Setup SSL/HTTPS with Let's Encrypt (15 minutes)**

### **Step 5.1: Get Free SSL Certificate**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain if you have one)
# If no domain, skip this and use IP address

# If you have a domain:
sudo certbot certify --nginx -d your-domain.com -d www.your-domain.com

# If using EC2 public IP only (no domain):
# Just use: http://54.123.45.67
# (SSL won't work with raw IPs, which is okay for MVP)
```

**If you don't have a domain yet:**
```bash
# You can:
1. Use IP address temporarily: http://54.123.45.67
2. Setup domain later and renew certificate
3. Use free domain services like: no-ip.com, duckdns.org
```

---

### **Step 5.2: Setup Auto-Renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Should show: Congratulations, all renewals succeeded

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

### **Step 5.3: Update Nginx SSL Paths (If you got certificate)**

Edit the Nginx config with your domain:

```bash
# Edit config
sudo vim /etc/nginx/sites-available/pdfpixie

# Update these lines with your domain:
# ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
# server_name your-domain.com www.your-domain.com;

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🎨 **PHASE 6: Deploy Frontend to Vercel (30 minutes)**

### **Step 6.1: Prepare Frontend Code**

Make sure your frontend code is updated:

```bash
# Navigate to frontend locally
cd /path/to/chatpdf/frontend

# Update environment file
cat > .env.example << 'EOF'
VITE_API_URL=https://your-backend-url
EOF

# Or update .env directly (don't commit this)
echo "VITE_API_URL=http://54.123.45.67" > .env.local
```

---

### **Step 6.2: Deploy to Vercel**

**Option A: Using Vercel Dashboard (Recommended)**

```
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Select repository: PikunMohanta/chatpdf
5. Project name: pdfpixie
6. Framework: Vite
7. Root Directory: frontend
8. Build Command: npm run build (auto-detected)
9. Output Directory: dist (auto-detected)
10. Environment Variables:
    - VITE_API_URL: https://your-backend-url
      (Or http://54.123.45.67 temporarily)
11. Click "Deploy"
12. Wait 2-3 minutes for build
13. Get your URL: https://pdfpixie-xxx.vercel.app
```

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod

# When prompted:
# Set up and deploy? → y
# Scope? → your-username
# Linked to existing project? → n
# Project name? → pdfpixie
# Directory? → ./
# Build command? → npm run build
# Output directory? → dist

# Get your URL from terminal output
```

---

### **Step 6.3: Configure Backend URL in Vercel**

After deployment, update the API URL:

```
1. Vercel Dashboard → pdfpixie project
2. Settings → Environment Variables
3. Add new variable:
   Name: VITE_API_URL
   Value: https://your-domain.com (or http://your-ec2-ip)
4. Click "Save"
5. Trigger redeployment:
   - Go to Deployments
   - Click "Redeploy" on latest deployment
```

---

### **Step 6.4: Update EC2 Backend CORS**

Make sure your backend allows requests from Vercel:

```bash
# SSH to EC2
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67

# Edit backend config
vim /home/ubuntu/apps/chatpdf/backend/app/config.py

# Update ALLOWED_ORIGINS to include:
ALLOWED_ORIGINS = [
    "https://pdfpixie-xxx.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

# Save and restart
sudo supervisorctl restart pdfpixie

# Or if using Gunicorn manually:
# Kill the process and restart
```

---

## 🧪 **PHASE 7: Testing (30 minutes)**

### **Step 7.1: Test Backend Endpoints**

From your laptop:

```bash
# Test health
curl https://your-backend-url/health

# Should return:
# {"status":"healthy","service":"pdfpixie-api"}

# Test API docs
curl https://your-backend-url/docs
# Should return HTML with Swagger UI
```

---

### **Step 7.2: Test Frontend**

```
1. Open https://pdfpixie-xxx.vercel.app in browser
2. Browser console should show:
   "Configuration loaded:"
   "environment: production"
   "apiBaseUrl: https://your-backend-url"
3. Try uploading a PDF
4. Check browser Network tab → should see requests to backend
```

---

### **Step 7.3: Test Full Workflow**

```
1. Upload PDF from frontend
2. Wait for processing
3. Ask a question about the PDF
4. Receive answer from AI
5. Refresh page
6. Chat history should persist (from database)
```

---

### **Step 7.4: Check Logs**

```bash
# SSH to EC2
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67

# Check backend logs
sudo tail -f /var/log/pdfpixie/error.log

# Check Nginx logs
sudo tail -f /var/log/nginx/pdfpixie_error.log

# Check supervisor status
sudo supervisorctl tail pdfpixie
```

---

## 📊 **PHASE 8: Monitoring & Maintenance**

### **Step 8.1: Monitor System Resources**

```bash
# SSH to EC2

# CPU and memory usage
top

# Press 'q' to exit

# Disk space
df -h

# Should show good free space (> 5GB)
```

---

### **Step 8.2: Check Database**

```bash
# Connect to PostgreSQL
psql -U pdfpixie_user -d pdfpixie -h localhost

# List tables
\dt

# Check size of tables
SELECT schemaname, tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Exit
\q
```

---

### **Step 8.3: Setup Automated Backups**

**Local PostgreSQL:**

```bash
# Create backup script
cat > /home/ubuntu/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U pdfpixie_user pdfpixie > $BACKUP_DIR/pdfpixie_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "pdfpixie_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/pdfpixie_$DATE.sql"
EOF

chmod +x /home/ubuntu/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e

# Add this line:
# 0 2 * * * /home/ubuntu/backup-db.sh
```

---

### **Step 8.4: Monitor Application Health**

```bash
# Check if app is running
ps aux | grep gunicorn

# Check supervisor status
sudo supervisorctl status pdfpixie

# Restart if needed
sudo supervisorctl restart pdfpixie
```

---

## 🔐 **PHASE 9: Security Hardening**

### **Step 9.1: Configure UFW Firewall**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Verify rules
sudo ufw status
```

---

### **Step 9.2: Setup SSH Key Authentication**

```bash
# Disable password login
sudo vim /etc/ssh/sshd_config

# Change:
# PasswordAuthentication yes  →  PasswordAuthentication no

# Restart SSH
sudo systemctl restart ssh
```

---

### **Step 9.3: Keep System Updated**

```bash
# Automatic security updates
sudo apt install -y unattended-upgrades

# Enable
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🚀 **PHASE 10: Domain Setup (Optional, 15 minutes)**

### **Step 10.1: Register Domain**

```
1. Go to domain registrar:
   - GoDaddy
   - Namecheap
   - Route 53
   - Freenom (free)

2. Register domain: your-domain.com

3. Get nameservers (if using Route 53):
   OR keep registrar's nameservers
```

---

### **Step 10.2: Point Domain to EC2**

**If using Route 53:**

```
1. AWS Console → Route 53
2. Create hosted zone for your domain
3. Create A record:
   - Name: your-domain.com
   - Type: A
   - Value: Your EC2 Public IP (54.123.45.67)
   - TTL: 300
4. Get nameservers from Route 53
5. Update domain registrar with these nameservers
6. Wait 24-48 hours for DNS propagation
```

**If using domain registrar's DNS:**

```
1. Go to domain registrar
2. Edit DNS records
3. Create A record:
   - Name: @ (or your-domain.com)
   - Type: A
   - Value: Your EC2 Public IP
   - TTL: 3600
4. Wait 24-48 hours
```

---

### **Step 10.3: Update SSL Certificate**

```bash
# SSH to EC2

# Get certificate for your domain
sudo certbot certify --nginx -d your-domain.com -d www.your-domain.com

# Update Nginx config
sudo vim /etc/nginx/sites-available/pdfpixie

# Change server_name line:
# server_name your-domain.com www.your-domain.com;

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

---

### **Step 10.4: Update Vercel Frontend URL**

```
1. Vercel Dashboard → Settings → Environment Variables
2. Update VITE_API_URL:
   From: https://54.123.45.67
   To: https://your-domain.com
3. Click "Save"
4. Redeploy on Deployments tab
```

---

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] GitHub account set up
- [ ] AWS account created
- [ ] Domain registered (optional)
- [ ] OpenRouter API key obtained
- [ ] Code pushed to GitHub render branch

### **EC2 Setup**
- [ ] EC2 instance launched (t3.micro)
- [ ] Security groups configured
- [ ] Key pair downloaded and saved
- [ ] SSH connection working

### **Backend Setup**
- [ ] Repository cloned on EC2
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] PostgreSQL database created
- [ ] .env file configured
- [ ] Backend tested locally (port 8000)
- [ ] Gunicorn working
- [ ] Supervisor service running

### **Nginx Setup**
- [ ] Nginx installed and configured
- [ ] Proxy settings working
- [ ] SSL certificate obtained
- [ ] HTTPS redirecting properly

### **Frontend Setup**
- [ ] Frontend code updated with API URL
- [ ] Deployed to Vercel
- [ ] Environment variables set
- [ ] Frontend accessible

### **Testing**
- [ ] Health endpoint working
- [ ] API docs accessible
- [ ] Frontend loading
- [ ] PDF upload working
- [ ] Chat functionality working
- [ ] Database persisting data

### **Security**
- [ ] UFW firewall enabled
- [ ] SSH key-only access
- [ ] SSL certificates installed
- [ ] CORS configured correctly

### **Monitoring**
- [ ] Log files accessible
- [ ] Backup script running
- [ ] System resources healthy
- [ ] Application auto-restarts on crash

---

## 🆘 **Troubleshooting**

### **Problem: "Connection refused" on port 8000**

```bash
# Check if backend is running
sudo supervisorctl status pdfpixie

# Should show RUNNING

# If not, restart it
sudo supervisorctl restart pdfpixie

# Check logs
sudo tail -f /var/log/pdfpixie/error.log
```

### **Problem: "502 Bad Gateway" in browser**

```bash
# Check Nginx
sudo nginx -t

# Check backend is listening
netstat -tuln | grep 8000

# Should show: 127.0.0.1:8000

# Restart Nginx
sudo systemctl restart nginx
```

### **Problem: "CORS error" in browser console**

```bash
# SSH to EC2
vim /home/ubuntu/apps/chatpdf/backend/app/config.py

# Update ALLOWED_ORIGINS with your Vercel URL:
ALLOWED_ORIGINS = [
    "https://pdfpixie-xxx.vercel.app",
    "http://localhost:5173",
]

# Restart backend
sudo supervisorctl restart pdfpixie
```

### **Problem: Database connection error**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U pdfpixie_user -d pdfpixie -h localhost

# Verify DATABASE_URL in .env
cat /home/ubuntu/apps/chatpdf/backend/.env | grep DATABASE_URL
```

### **Problem: Frontend can't find backend**

```
1. Check VITE_API_URL in Vercel environment
2. Vercel Dashboard → Settings → Environment Variables
3. Should match your backend URL
4. Redeploy frontend
5. Check browser Network tab to see actual API calls
```

### **Problem: High memory/CPU usage**

```bash
# Monitor in real-time
top

# Find pdfpixie process
# Note the PID

# Check memory limit for Gunicorn
sudo supervisorctl tail pdfpixie

# Reduce workers if needed
# Edit: /etc/supervisor/conf.d/pdfpixie.conf
# Change: -w 4  →  -w 2
# Restart: sudo supervisorctl restart pdfpixie
```

---

## 📈 **Performance Tips**

### **Optimize EC2**
```
1. Monitor with: top, htop
2. Increase workers if CPU < 20%
3. Decrease workers if memory > 80%
4. Use t3.small if consistently high usage
```

### **Optimize Database**
```
1. Add indexes on frequently queried columns
2. Regular VACUUM and ANALYZE
3. Monitor slow queries
4. Backup regularly
```

### **Optimize Frontend**
```
1. Enable gzip compression in Nginx
2. Use Vercel Analytics
3. Monitor Core Web Vitals
4. Optimize images
```

---

## 🎯 **Scaling for Production**

### **If traffic increases:**

**Step 1: Upgrade EC2 instance**
```
t3.micro → t3.small ($17/mo) → t3.medium ($40/mo)
```

**Step 2: Add load balancer**
```
AWS Application Load Balancer
Distribute traffic between multiple EC2 instances
```

**Step 3: Use RDS for database**
```
Better reliability
Automated backups
Multi-AZ for high availability
```

**Step 4: Add CloudFront CDN**
```
Cache static assets
Reduce server load
Faster global access
```

---

## 💡 **Key Takeaways**

✅ **You now have:**
- Production-ready FastAPI backend
- PostgreSQL database running
- Nginx reverse proxy with SSL
- Vercel frontend deployed
- Auto-restarting services
- Full control over infrastructure

✅ **Best practices implemented:**
- Environment variables for secrets
- Automatic monitoring (supervisor)
- Backup strategy
- Security hardening (firewall, SSH keys)
- Logging and debugging

✅ **Total cost: $0-50/month**
- Free for 12 months (EC2, RDS)
- $30-50/month after

---

## 📞 **Quick Reference Commands**

```bash
# Backend management
sudo supervisorctl status pdfpixie              # Check status
sudo supervisorctl restart pdfpixie             # Restart
sudo supervisorctl tail pdfpixie                # View logs
sudo tail -f /var/log/pdfpixie/error.log       # Error logs

# Database management
psql -U pdfpixie_user -d pdfpixie -h localhost # Connect
pg_dump -U pdfpixie_user pdfpixie > backup.sql # Backup
psql -U pdfpixie_user pdfpixie < backup.sql    # Restore

# Nginx management
sudo nginx -t                                   # Test config
sudo systemctl restart nginx                    # Restart
sudo systemctl reload nginx                     # Reload (no downtime)
sudo tail -f /var/log/nginx/pdfpixie_error.log# Error logs

# System monitoring
top                                             # CPU/Memory
df -h                                           # Disk space
netstat -tuln                                   # Listening ports
htop                                            # Better top

# SSL management
sudo certbot renew --dry-run                    # Test renewal
sudo certbot certificates                       # List certificates
sudo certbot delete --cert-name your-domain    # Remove cert

# Git deployment
cd /home/ubuntu/apps/chatpdf
git pull origin render                          # Update code
sudo supervisorctl restart pdfpixie             # Restart service
```

---

## 🎉 **Congratulations!**

You now have a production-ready application deployed on:
- **Frontend**: Vercel (global CDN)
- **Backend**: AWS EC2 (full control)
- **Database**: PostgreSQL (persistent)
- **Files**: AWS S3 (scalable storage)

Your PDFPixie is live and ready! 🚀

