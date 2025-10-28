# PDFPixie - Complete Application on Single EC2 Instance with Docker

## 🚀 **Architecture: Everything on One EC2 Instance**

```
┌────────────────────────────────────────────────────────────┐
│                   AWS EC2 Instance                         │
│                  (Single t3.micro/small)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │          Docker Container (pdfpixie)                │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  Nginx (Port 80/443)                        │   │ │
│  │  │  - Serves React Frontend                    │   │ │
│  │  │  - Proxies API to FastAPI                   │   │ │
│  │  │  - Proxies WebSocket to Socket.IO           │   │ │
│  │  │  - SSL/TLS Termination                      │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  FastAPI Backend (Port 8000)                │   │ │
│  │  │  - REST API Endpoints                       │   │ │
│  │  │  - WebSocket/Socket.IO                      │   │ │
│  │  │  - PDF Processing                           │   │ │
│  │  │  - ChromaDB Integration                     │   │ │
│  │  │  - LangChain Chains                         │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  PostgreSQL Database (Port 5432)            │   │ │
│  │  │  - Chat History                             │   │ │
│  │  │  - Document Metadata                        │   │ │
│  │  │  - User Sessions                            │   │ │
│  │  │  - Persistent Storage                       │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  Redis Cache (Port 6379)                    │   │ │
│  │  │  - Session Cache                            │   │ │
│  │  │  - Real-time State                          │   │ │
│  │  │  - Chat State Management                    │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  ChromaDB Vector Store                      │   │ │
│  │  │  - Vector Embeddings                        │   │ │
│  │  │  - Document Chunks                          │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │  Supervisor                                 │   │ │
│  │  │  - Manages all processes                    │   │ │
│  │  │  - Auto-restart on crash                    │   │ │
│  │  │  - Logs monitoring                          │   │ │
│  │  └─────────────────────────────────────────────┘   │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Volumes (Persistent Storage):                            │
│  - /app/data/chromadb/                                    │
│  - /app/data/uploads/                                     │
│  - /app/data/chat_history/                                │
│  - PostgreSQL data directory                              │
│  - Redis data directory                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
         ↓ (Optional)
    AWS S3 Bucket
    - Additional PDF Storage
    - Backup Location
```

---

## 💰 **Cost Analysis**

### **Free Tier (12 Months)**
```
✅ EC2 t3.micro:              $0 (750 hrs/month)
✅ EBS Storage (30GB):        $0 (free tier)
✅ Elastic IP:                $0 (if attached)
✅ Data Transfer:             $0 (within AWS)
───────────────────────────────────
   TOTAL:                     $0/month
```

### **After Free Tier (Monthly)**
```
💰 EC2 t3.micro:              $9/month
💰 EC2 t3.small:              $17/month (recommended)
💰 EBS Storage (30GB):        $2-3/month
💰 Data Transfer (1GB):       $0.09/month
💰 Elastic IP:                $0 (free if attached)
───────────────────────────────────
   TOTAL:                     $20-30/month
```

**With S3 Backup:**
```
💰 S3 Storage (100GB):        $2.30/month
💰 S3 Transfer:               $9/month
───────────────────────────────────
   TOTAL WITH S3:             $31-41/month
```

---

## 📋 **Prerequisites**

- ✅ AWS Account with credit card
- ✅ GitHub account
- ✅ Domain name (optional - can use EC2 IP initially)
- ✅ OpenRouter API key
- ✅ SSH client (Terminal, PuTTY, or Git Bash)
- ✅ Git installed locally

---

## 🔧 **PHASE 1: AWS EC2 Setup (30 minutes)**

### **Step 1.1: Launch EC2 Instance**

**Navigate to AWS Console:**

```
1. Go to https://console.aws.amazon.com
2. Search for "EC2" in the search bar
3. Click "EC2" from services
```

**Launch Instance:**

```
1. Click "Launch Instance" (orange button)
2. Name your instance:
   - Instance name: pdfpixie-app
3. Choose AMI (Amazon Machine Image):
   - Search: "Ubuntu 24.04 LTS"
   - Select: "Ubuntu Server 24.04 LTS (HVM)"
   - ✅ Free tier eligible
4. Instance Type:
   - Select: t3.micro (FREE TIER for 12 months)
   - Free tier eligible
5. Key Pair (important!):
   - Click "Create new key pair"
   - Name: pdfpixie-key
   - Key pair type: RSA
   - Format: .pem
   - Click "Create key pair"
   - ⬇️ Downloads pdfpixie-key.pem to your laptop
   - ⚠️ SAVE THIS FILE SECURELY - You'll need it to access EC2
6. Network Settings:
   - VPC: default (or create new)
   - Auto-assign public IP: Enable
7. Security Group (NEW):
   - Name: pdfpixie-sg
   - Description: PDFPixie Application
   - Inbound Rules:
     * SSH (22): Type=SSH, Source=My IP (or 0.0.0.0/0 for testing)
     * HTTP (80): Type=HTTP, Source=0.0.0.0/0 (anyone)
     * HTTPS (443): Type=HTTPS, Source=0.0.0.0/0 (anyone)
     * Custom TCP (8000): Type=Custom TCP, Port=8000, Source=0.0.0.0/0 (for testing)
8. Storage:
   - Volume type: gp2 (General Purpose)
   - Size: 30GB (FREE TIER eligible)
   - Encrypted: No (not needed for free tier)
9. Click "Launch Instance"
10. Wait for instance to start (1-2 minutes)
```

### **Step 1.2: Get EC2 Public IP Address**

```
1. Go to EC2 Dashboard → Instances
2. Select your instance (pdfpixie-app)
3. Copy the "Public IPv4 address"
   Example: 54.123.45.67
   SAVE THIS - You'll need it for:
   - SSH connections
   - Domain pointing
   - Accessing application
```

### **Step 1.3: Connect to EC2 via SSH**

**On Windows (PowerShell or Git Bash):**

```bash
# Navigate to where you saved pdfpixie-key.pem
cd ~/Downloads

# Change key permissions (Windows)
icacls pdfpixie-key.pem /inheritance:r /grant:r "%username%:F"

# SSH into instance
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67

# First connection will ask:
# "Are you sure you want to continue connecting (yes/no)?"
# Type: yes
```

**On macOS/Linux:**

```bash
# Navigate to where you saved pdfpixie-key.pem
cd ~/Downloads

# Change key permissions (must be 400 for SSH)
chmod 400 pdfpixie-key.pem

# SSH into instance
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67
```

**Expected Output:**
```
Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.8.0-1013-aws x86_64)
ubuntu@ip-172-31-xx-xx:~$
```

---

## 📦 **PHASE 2: Install Docker & Dependencies (20 minutes)**

### **Step 2.1: Update System Packages**

```bash
# SSH to EC2 (from previous step)

# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  docker.io \
  docker-compose \
  git \
  curl \
  wget \
  nano \
  vim

# Verify installations
docker --version
docker-compose --version
git --version
```

### **Step 2.2: Configure Docker Access**

```bash
# Add ubuntu user to docker group (so you don't need sudo)
sudo usermod -aG docker ubuntu

# Apply group membership without relogging
newgrp docker

# Test Docker (should not need sudo)
docker ps

# Should return:
# CONTAINER ID   IMAGE      COMMAND   CREATED   STATUS    PORTS     NAMES
# (empty table - no containers yet)
```

### **Step 2.3: Create Application Directory**

```bash
# Create app directory
mkdir -p /home/ubuntu/apps
cd /home/ubuntu/apps

# Verify
pwd
# Should output: /home/ubuntu/apps
```

---

## 🔍 **PHASE 3: Prepare Your Dockerfile (15 minutes)**

### **Step 3.1: Review Your Current Dockerfile**

Your existing Dockerfile is **almost perfect**. It:
- ✅ Builds React frontend
- ✅ Runs FastAPI backend
- ✅ Includes Nginx proxy
- ✅ Uses Supervisor for process management

### **Step 3.2: Complete Dockerfile Setup**

**Create folder structure locally (on your laptop):**

```
chatpdf/
├── docker-compose.yml          (NEW)
├── Dockerfile                   (EXISTING - already have it)
├── supervisor/
│   └── supervisord.conf        (NEW)
├── nginx/
│   ├── nginx.conf              (NEW)
│   └── conf.d/
│       └── pdfpixie.conf       (NEW)
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── app/
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
└── .dockerignore               (NEW)
```

---

## 📄 **PHASE 4: Create Docker Configuration Files**

### **Step 4.1: Create .dockerignore**

**Create file: `.dockerignore` in project root**

```
# Git
.git
.gitignore
.gitattributes

# Node
node_modules
npm-debug.log
yarn-error.log
.npm

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
pip-log.txt
pip-delete-this-directory.txt

# IDE
.vscode
.idea
*.swp
*.swo
*~
.DS_Store

# OS
.DS_Store
.gitkeep

# Project
data/
uploads/
.env
.env.local
dist/
build/

# CI/CD
.github
.gitlab-ci.yml
Jenkinsfile
```

---

### **Step 4.2: Create docker-compose.yml**

**Create file: `docker-compose.yml` in project root**

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: pdfpixie-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: pdfpixie_user
      POSTGRES_PASSWORD: YourSecurePassword123!
      POSTGRES_DB: pdfpixie
      POSTGRES_INITDB_ARGS: "-E UTF8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pdfpixie_user -d pdfpixie"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks:
      - pdfpixie-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: pdfpixie-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks:
      - pdfpixie-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Main Application (Frontend + Backend)
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: pdfpixie-app
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8000:8000"
    environment:
      # Application
      ENVIRONMENT: production
      IS_PRODUCTION: "true"
      
      # Database Connection
      DATABASE_URL: "postgresql://pdfpixie_user:YourSecurePassword123!@postgres:5432/pdfpixie"
      
      # Redis Connection
      REDIS_URL: "redis://redis:6379"
      
      # API Keys (from .env file)
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      
      # Frontend URL
      FRONTEND_URL: "https://your-domain.com"
      
      # AWS S3 (Optional)
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_REGION: ap-south-1
      S3_BUCKET_NAME: ${S3_BUCKET_NAME}
      
      # Logging
      LOG_LEVEL: INFO
      DEBUG: "false"
    
    volumes:
      # Persistent data
      - app_data:/app/data
      - chromadb_data:/app/data/chromadb
      - uploads_data:/app/data/uploads
      
      # SSL certificates (if using Let's Encrypt)
      - /etc/letsencrypt:/etc/letsencrypt:ro
    
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    
    networks:
      - pdfpixie-network
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    logging:
      driver: "json-file"
      options:
        max-size: "20m"
        max-file: "5"

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  app_data:
    driver: local
  chromadb_data:
    driver: local
  uploads_data:
    driver: local

networks:
  pdfpixie-network:
    driver: bridge
```

---

### **Step 4.3: Create Nginx Configuration**

**Create file: `nginx/nginx.conf`**

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml 
               text/x-component text/x-cross-domain-policy;

    # Include site configurations
    include /etc/nginx/conf.d/*.conf;
}
```

**Create file: `nginx/conf.d/pdfpixie.conf`**

```nginx
# Upstream backend
upstream pdfpixie_backend {
    server app:8000;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS main server
server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    server_name _;
    
    # SSL Configuration (update with your certificate path)
    # These will be populated by Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/your-domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain/privkey.pem;
    
    # SSL Best Practices
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Logging
    access_log /var/log/nginx/pdfpixie_access.log main buffer=32k;
    error_log /var/log/nginx/pdfpixie_error.log warn;
    
    # Root document for static files
    root /app/frontend/dist;
    
    # Frontend routes - serve index.html for React Router
    location / {
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
    
    # Static assets with long cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
    }
    
    # API endpoints - proxy to FastAPI
    location /api/ {
        proxy_pass http://pdfpixie_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # WebSocket endpoints (Socket.IO)
    location /socket.io {
        proxy_pass http://pdfpixie_backend/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        
        # WebSocket headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeouts for WebSocket
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 7d;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /redoc {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /openapi.json {
        proxy_pass http://pdfpixie_backend;
        proxy_set_header Host $host;
    }
}
```

---

### **Step 4.4: Create Supervisor Configuration**

**Create file: `supervisor/supervisord.conf`**

```ini
[supervisord]
nodaemon=true
logfile=/var/log/supervisord.log
pidfile=/var/run/supervisord.pid
loglevel=info

[unix_http_server]
file=/var/run/supervisor.sock

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

# PostgreSQL Service
[program:postgresql]
command=/usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main -c config_file=/etc/postgresql/15/main/postgresql.conf
autostart=true
autorestart=true
stderr_logfile=/var/log/postgresql.err.log
stdout_logfile=/var/log/postgresql.out.log
user=postgres
priority=999

# Redis Service
[program:redis]
command=/usr/local/bin/redis-server /usr/local/etc/redis/redis.conf
autostart=true
autorestart=true
stderr_logfile=/var/log/redis.err.log
stdout_logfile=/var/log/redis.out.log
priority=998

# FastAPI Application
[program:fastapi]
directory=/app/backend
command=/usr/local/bin/gunicorn \
  -w 4 \
  -b 127.0.0.1:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  --worker-tmp-dir /dev/shm \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  main:socket_app
autostart=true
autorestart=true
stderr_logfile=/var/log/fastapi.err.log
stdout_logfile=/var/log/fastapi.out.log
stopasgroup=true
priority=997

# Nginx Web Server
[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stderr_logfile=/var/log/nginx.err.log
stdout_logfile=/var/log/nginx.out.log
stopasgroup=true
priority=996

[group:pdfpixie]
programs=postgresql,redis,fastapi,nginx
priority=10
```

---

## 📝 **PHASE 5: Prepare Environment File**

### **Step 5.1: Create .env File**

**Create file: `.env` in project root (on your laptop)**

```bash
# Application Environment
ENVIRONMENT=production
IS_PRODUCTION=true

# API Keys (Replace with your actual keys)
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here

# Frontend URL (Update with your domain)
FRONTEND_URL=https://your-domain.com

# AWS S3 (Optional - if not using, leave empty)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

# Database Settings (already in docker-compose.yml)
POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=pdfpixie

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
```

### **Step 5.2: Create .env.example (for Git)**

**Create file: `.env.example` in project root**

```bash
# This file shows the structure of .env
# Copy this to .env and fill in actual values

ENVIRONMENT=production
IS_PRODUCTION=true

OPENROUTER_API_KEY=sk-or-v1-your-key-here

FRONTEND_URL=https://your-domain.com

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=pdfpixie

REDIS_HOST=redis
REDIS_PORT=6379
```

---

## 🚀 **PHASE 6: Deploy to EC2 (20 minutes)**

### **Step 6.1: Push Code to GitHub**

**On your laptop:**

```bash
# Navigate to project
cd /path/to/chatpdf

# Create new branch for docker deployment
git checkout -b docker-deployment

# Add all new files
git add .
git status

# Should show:
# - Dockerfile (modified)
# - docker-compose.yml (new)
# - .dockerignore (new)
# - nginx/ folder (new)
# - supervisor/ folder (new)
# - .env.example (new)

# Commit
git commit -m "Add Docker deployment configuration for single EC2 instance"

# Push to GitHub
git push origin docker-deployment

# Switch back to main for deployment
git checkout main
git merge docker-deployment
git push origin main
```

### **Step 6.2: Clone on EC2**

**SSH to EC2:**

```bash
# Already connected from Phase 2, or:
ssh -i pdfpixie-key.pem ubuntu@54.123.45.67

# Navigate to apps directory
cd /home/ubuntu/apps

# Clone your repository
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf

# Verify structure
ls -la
# Should show: Dockerfile, docker-compose.yml, nginx/, supervisor/, etc.
```

### **Step 6.3: Create .env on EC2**

```bash
# SSH to EC2, in chatpdf directory

# Create .env file (copy from .env.example and update)
cat > .env << 'EOF'
ENVIRONMENT=production
IS_PRODUCTION=true

OPENROUTER_API_KEY=your-actual-api-key-here

FRONTEND_URL=https://your-domain.com

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=pdfpixie

REDIS_HOST=redis
REDIS_PORT=6379
EOF

# Verify
cat .env
```

### **Step 6.4: Build Docker Image**

```bash
# SSH to EC2, in chatpdf directory

# Build the Docker image (first time, takes 5-10 minutes)
docker build -t pdfpixie:latest .

# Watch the build output:
# [1/20] FROM node:20-alpine AS frontend-builder
# [2/20] WORKDIR /app/frontend
# ... (lots of output)
# [20/20] Successfully tagged pdfpixie:latest

# Verify image was created
docker images | grep pdfpixie
# Should show: pdfpixie | latest | xxx | 2 hours ago
```

### **Step 6.5: Start All Services with Docker Compose**

```bash
# SSH to EC2, in chatpdf directory

# Start all containers in the background
docker-compose up -d

# Watch the startup
docker-compose logs -f

# Wait for all services to start (2-3 minutes):
# - PostgreSQL initializing database
# - Redis starting
# - FastAPI loading
# - Nginx starting
# - All becoming healthy

# Press Ctrl+C to exit logs view
```

### **Step 6.6: Verify All Services Are Running**

```bash
# SSH to EC2

# Check container status
docker-compose ps

# Should show (all HEALTHY or UP):
# NAME                  STATUS              PORTS
# pdfpixie-postgres     Up (healthy)        0.0.0.0:5432->5432
# pdfpixie-redis        Up (healthy)        0.0.0.0:6379->6379
# pdfpixie-app          Up (healthy)        0.0.0.0:80->80, 443->443, 8000->8000
```

---

## 🧪 **PHASE 7: Testing (15 minutes)**

### **Step 7.1: Test Health Endpoint**

```bash
# From EC2 or your laptop

# Test from EC2:
curl http://localhost/health

# Test from laptop:
curl http://54.123.45.67/health

# Should return:
# {"status":"healthy","service":"pdfpixie-api"}
```

### **Step 7.2: Test Frontend**

```bash
# Open in browser (replace with your EC2 IP)
http://54.123.45.67

# Should see:
# PDFPixie application homepage
# Upload interface
# No errors in Network tab
```

### **Step 7.3: Test API Documentation**

```bash
# Open in browser
http://54.123.45.67/docs

# Should see:
# FastAPI Swagger UI
# All API endpoints listed
# Ability to test endpoints
```

### **Step 7.4: Test Full Workflow**

```bash
# In browser at http://54.123.45.67:

1. Upload a PDF file
2. Wait for processing (should see status updates)
3. Ask a question about the PDF
4. Receive AI response
5. Upload another PDF
6. Refresh page
7. Chat history should still be there (persisted in PostgreSQL)
```

### **Step 7.5: Check Container Logs**

```bash
# SSH to EC2

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs postgres
docker-compose logs redis
docker-compose logs app

# View logs in real-time
docker-compose logs -f app

# View only last 100 lines
docker-compose logs --tail=100
```

---

## 🔒 **PHASE 8: Setup Domain & SSL (30 minutes)**

### **Step 8.1: Setup Domain Name (Optional)**

**Option A: Use EC2 IP Address (For Testing)**
```
You already have: http://54.123.45.67
Works for testing but not production-recommended
```

**Option B: Use Free Domain (DuckDNS)**

```bash
# 1. Go to https://www.duckdns.org
# 2. Sign in with GitHub
# 3. Create subdomain: pdfpixie
# 4. Click "Install" (choose other)
# 5. Update your EC2 IP in DuckDNS dashboard
# 6. Your domain: pdfpixie.duckdns.org

# Update FRONTEND_URL in .env
# FRONTEND_URL=https://pdfpixie.duckdns.org
```

**Option C: Buy Cheap Domain (Namecheap - $1-3/year)**

```bash
# 1. Go to https://www.namecheap.com
# 2. Register domain (e.g., your-app.com)
# 3. Go to Dashboard → Your domains → your-app.com
# 4. Manage → All Host Records
# 5. Add A record:
#    Host: @ (or www)
#    Type: A
#    Value: 54.123.45.67 (your EC2 IP)
#    TTL: 3600
# 6. Save changes
# 7. Wait 24-48 hours for DNS propagation

# Update FRONTEND_URL in .env
# FRONTEND_URL=https://your-app.com
```

### **Step 8.2: Setup SSL Certificate with Let's Encrypt**

**SSH to EC2:**

```bash
# Stop the app to access port 80 for certificate verification
docker-compose stop

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# You'll be prompted to enter your email - do that
# Agree to terms (A)
# Accept optional newsletter (N)

# Verify certificate was created
sudo ls -la /etc/letsencrypt/live/your-domain.com/

# Should show:
# fullchain.pem → certificate
# privkey.pem → private key
```

### **Step 8.3: Update Nginx Configuration**

**SSH to EC2:**

```bash
# Edit Nginx config
sudo nano nginx/conf.d/pdfpixie.conf

# Find these lines (around line 40):
# ssl_certificate /etc/letsencrypt/live/your-domain/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain/privkey.pem;

# Replace "your-domain" with your actual domain name:
# ssl_certificate /etc/letsencrypt/live/your-app.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-app.com/privkey.pem;

# Save: Ctrl+O → Enter → Ctrl+X

# Also update server_name if needed
```

### **Step 8.4: Restart Services**

```bash
# SSH to EC2, in chatpdf directory

# Restart all services
docker-compose up -d

# Check Nginx loaded correctly
docker-compose logs nginx | grep -i ssl

# Should show no errors related to SSL
```

### **Step 8.5: Setup Auto-Renewal**

```bash
# SSH to EC2

# Certbot auto-renewal timer already enabled, but verify:
sudo systemctl status certbot.timer

# Test renewal process (dry run)
sudo certbot renew --dry-run

# Should show: Congratulations, all renewals succeeded
```

---

## 📊 **PHASE 9: Production Setup & Optimization (30 minutes)**

### **Step 9.1: Setup System Limits**

```bash
# SSH to EC2

# Edit sysctl.conf
sudo nano /etc/sysctl.conf

# Add these lines at the end:
# Network optimization
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 1024
net.ipv4.ip_local_port_range = 10000 65000

# Apply changes
sudo sysctl -p
```

### **Step 9.2: Update Backend .env**

**SSH to EC2:**

```bash
# Update .env with production settings
nano .env

# Change:
FRONTEND_URL=https://your-domain.com

# Restart app to apply changes
docker-compose restart app
```

### **Step 9.3: Setup Log Rotation**

```bash
# SSH to EC2

# Create logrotate config for Docker logs
sudo tee /etc/logrotate.d/docker-compose > /dev/null << 'EOF'
/var/lib/docker/containers/*/*.log {
  rotate 5
  daily
  compress
  delaycompress
  missingok
  copytruncate
}
EOF

# Test logrotate
sudo logrotate -f /etc/logrotate.d/docker-compose
```

### **Step 9.4: Monitor Disk Space**

```bash
# SSH to EC2

# Check current disk usage
df -h

# Should show available space
# If > 20GB free, you're fine

# Cleanup Docker images not in use
docker image prune -a --force

# Cleanup old Docker volumes
docker volume prune -f
```

### **Step 9.5: Setup Automated Backups**

```bash
# SSH to EC2

# Create backup script
cat > /home/ubuntu/backup-db.sh << 'EOF'
#!/bin/bash

# Backup database
docker-compose exec -T postgres pg_dump -U pdfpixie_user pdfpixie > \
  /home/ubuntu/backups/pdfpixie_$(date +%Y%m%d_%H%M%S).sql

# Keep only last 7 days
find /home/ubuntu/backups -name "pdfpixie_*.sql" -mtime +7 -delete

# Compress backup
gzip /home/ubuntu/backups/pdfpixie_*.sql 2>/dev/null

echo "Backup completed"
EOF

# Make it executable
chmod +x /home/ubuntu/backup-db.sh

# Create backups directory
mkdir -p /home/ubuntu/backups

# Add to crontab for daily backup at 2 AM
crontab -e

# Add this line:
# 0 2 * * * /home/ubuntu/backup-db.sh
```

---

## 🔐 **PHASE 10: Security Hardening (20 minutes)**

### **Step 10.1: Configure UFW Firewall**

```bash
# SSH to EC2

# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status

# Should show:
# Status: active
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

### **Step 10.2: Disable Password SSH Login**

```bash
# SSH to EC2

# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Find and change:
# PasswordAuthentication yes  →  PasswordAuthentication no
# PubkeyAuthentication yes    →  PubkeyAuthentication yes (keep enabled)

# Restart SSH
sudo systemctl restart ssh

# Don't close current SSH session! Test in new terminal first
```

### **Step 10.3: Setup Fail2Ban (Optional)**

```bash
# SSH to EC2

# Install fail2ban
sudo apt install -y fail2ban

# Start service
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Check status
sudo fail2ban-client status sshd
```

### **Step 10.4: Secure Docker Socket**

```bash
# SSH to EC2

# Docker socket permissions (already secure in docker-compose)
ls -l /var/run/docker.sock

# Should show: srw-rw---- root docker
```

---

## 📈 **PHASE 11: Monitoring & Maintenance (Ongoing)**

### **Step 11.1: Setup Resource Monitoring**

```bash
# SSH to EC2

# Install htop for interactive monitoring
sudo apt install -y htop

# View system resources
htop

# Press 'q' to exit

# Disk usage
du -sh /home/ubuntu/apps/*

# Docker storage
docker system df
```

### **Step 11.2: Monitor Application**

```bash
# SSH to EC2

# View running containers
docker ps

# Check container resource usage
docker stats

# View recent logs
docker-compose logs --tail=50 app

# View specific errors
docker-compose logs app | grep ERROR
```

### **Step 11.3: Database Maintenance**

```bash
# SSH to EC2

# Connect to PostgreSQL inside Docker
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie

# List tables
\dt

# Check database size
SELECT pg_size_pretty(pg_database_size('pdfpixie'));

# Optimize database (weekly)
VACUUM ANALYZE;

# Exit
\q
```

### **Step 11.4: Restart Services**

```bash
# SSH to EC2

# Restart single service
docker-compose restart app
docker-compose restart postgres
docker-compose restart redis

# Restart all services
docker-compose restart

# Rebuild and restart (if code changed)
docker-compose up -d --build

# Full restart (clean slate)
docker-compose down
docker-compose up -d
```

---

## 🆘 **Troubleshooting Guide**

### **Problem: Container won't start**

```bash
# SSH to EC2

# Check error logs
docker-compose logs app

# Common issues:
# 1. Port already in use
docker ps | grep 80
# Solution: Stop conflicting service or change port

# 2. Out of memory
free -h
# Solution: Stop other containers, upgrade instance

# 3. Database connection failed
docker-compose logs postgres
# Solution: Check DATABASE_URL in .env
```

### **Problem: "Connection refused" when accessing app**

```bash
# Check if containers are running
docker-compose ps

# Check if ports are listening
sudo netstat -tuln | grep -E ':(80|443|8000)'

# Restart Nginx
docker-compose restart nginx

# Check Nginx logs
docker-compose logs nginx
```

### **Problem: SSL certificate errors**

```bash
# Check certificate status
sudo certbot certificates

# Check certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/your-domain/fullchain.pem -text -noout | grep -A2 "Validity"

# Renew manually
sudo certbot renew --force-renewal

# Check Nginx loads certificate
docker-compose logs nginx | grep ssl
```

### **Problem: Database running out of space**

```bash
# Check database size
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie -c \
  "SELECT pg_size_pretty(pg_database_size('pdfpixie'));"

# Cleanup old data
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie -c \
  "DELETE FROM chat_messages WHERE timestamp < NOW() - INTERVAL '90 days';"

# Vacuum to reclaim space
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie -c \
  "VACUUM FULL ANALYZE;"
```

### **Problem: High memory usage**

```bash
# Check what's using memory
docker stats

# If FastAPI using too much:
# Reduce workers in supervisor/supervisord.conf
# Change: -w 4  →  -w 2

# Restart
docker-compose restart app

# If still high, restart entire app
docker-compose down
docker-compose up -d
```

### **Problem: Slow response times**

```bash
# Check network connectivity
docker-compose exec app ping redis
docker-compose exec app ping postgres

# Check database performance
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check if services are healthy
docker-compose ps

# If not healthy, restart
docker-compose restart
```

---

## 📋 **Complete Deployment Checklist**

### **Pre-Deployment**
- [ ] AWS Account created
- [ ] EC2 key pair created and saved securely
- [ ] All configuration files created (Dockerfile, docker-compose.yml, nginx, supervisor)
- [ ] .env file created with actual keys
- [ ] Code committed to GitHub
- [ ] OpenRouter API key obtained
- [ ] Domain registered (optional but recommended)

### **EC2 Setup**
- [ ] EC2 instance launched (t3.micro)
- [ ] Security groups configured (ports 22, 80, 443 open)
- [ ] SSH connection working
- [ ] Docker and Docker Compose installed
- [ ] Git installed
- [ ] Application directory created

### **Deployment**
- [ ] Repository cloned on EC2
- [ ] .env file created with actual values
- [ ] Docker image built successfully
- [ ] All containers started (`docker-compose ps` shows all running)
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads in browser
- [ ] API documentation accessible
- [ ] Full workflow tested (upload, question, answer)
- [ ] Database contains persisted data

### **SSL & Domain**
- [ ] Domain registered and pointing to EC2 IP
- [ ] SSL certificate obtained from Let's Encrypt
- [ ] HTTPS working (green lock in browser)
- [ ] HTTP redirects to HTTPS
- [ ] Certificate renewal setup

### **Security**
- [ ] UFW firewall enabled
- [ ] SSH key-only access configured
- [ ] Environment variables not committed to Git
- [ ] Database password changed from default
- [ ] Security headers configured in Nginx
- [ ] CORS properly configured

### **Monitoring**
- [ ] Log files accessible
- [ ] Container health checks passing
- [ ] Resource usage monitored (disk, memory, CPU)
- [ ] Backup script running daily
- [ ] SSL certificate renewal automated

### **Production**
- [ ] FRONTEND_URL updated to production domain
- [ ] ENVIRONMENT=production set
- [ ] DEBUG=false set
- [ ] Database optimized and indexed
- [ ] Logging rotation configured
- [ ] System updates applied

---

## 🎯 **Quick Command Reference**

```bash
# Container Management
docker-compose up -d                    # Start all services
docker-compose down                     # Stop all services
docker-compose restart                  # Restart all services
docker-compose logs -f                  # View live logs
docker-compose ps                       # List running containers
docker-compose stats                    # View resource usage

# Database Access
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie
# Inside PostgreSQL:
\dt                                     # List tables
SELECT COUNT(*) FROM chat_messages;     # Count messages
DELETE FROM chat_messages WHERE ...;    # Delete old data
VACUUM ANALYZE;                         # Optimize database
\q                                      # Exit

# Backups
docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > backup.sql
docker-compose exec postgres psql -U pdfpixie_user pdfpixie < backup.sql

# SSL Management
sudo certbot certificates                # List certificates
sudo certbot renew --dry-run            # Test renewal
sudo certbot delete --cert-name yourdomain.com

# Monitoring
df -h                                   # Disk usage
free -h                                 # Memory usage
docker system df                        # Docker storage
htop                                    # Interactive monitoring

# Logs
tail -f /var/log/docker                 # Docker daemon logs
docker-compose logs --tail=100 app      # Last 100 lines
docker-compose logs app | grep ERROR    # Show errors
```

---

## 📞 **Support & Additional Resources**

### **Docker Documentation**
- Docker Compose: https://docs.docker.com/compose/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

### **Nginx Documentation**
- Nginx: https://nginx.org/
- Configuration: https://nginx.org/en/docs/http/ngx_http_proxy_module.html

### **PostgreSQL Documentation**
- PostgreSQL: https://www.postgresql.org/docs/
- Optimization: https://wiki.postgresql.org/wiki/Performance_Optimization

### **Let's Encrypt**
- Certbot: https://certbot.eff.org/
- Documentation: https://certbot.eff.org/docs/

### **AWS EC2**
- EC2 User Guide: https://docs.aws.amazon.com/ec2/
- Best Practices: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html

---

## 🎉 **Congratulations!**

You now have a **production-ready application** deployed on AWS EC2 with:

✅ **Complete Stack in One Container**
- Frontend (React + Nginx)
- Backend (FastAPI + Socket.IO)
- Database (PostgreSQL)
- Cache (Redis)
- Vector Store (ChromaDB)

✅ **Production Features**
- SSL/HTTPS encryption
- Auto-restarting services
- Persistent data storage
- Daily automated backups
- Security hardening
- Resource monitoring
- Easy scaling

✅ **Low Cost**
- Free for 12 months (EC2 free tier)
- $20-30/month after free tier
- Full control over infrastructure

Your PDFPixie application is now **live, secure, and ready for users!** 🚀

---

## 📝 **Next Steps**

1. **Customize branding** - Update colors, logo, domain
2. **Optimize performance** - Monitor and tune database indexes
3. **Add monitoring** - Setup CloudWatch or monitoring service
4. **Enable S3 backup** - Add AWS S3 for additional file storage
5. **Scale horizontally** - Add load balancer for multiple instances
6. **Setup CI/CD** - Automate deployments with GitHub Actions
7. **Monitor costs** - Track AWS spending in billing dashboard
8. **Gather feedback** - Collect user feedback for improvements

