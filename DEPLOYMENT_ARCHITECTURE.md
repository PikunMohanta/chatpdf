# PDFPixie Deployment Architecture

## 🏗️ **Current Architecture**

This deployment uses a **hybrid approach** optimized for single EC2 instances:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  Container: pdfpixie-postgres              │         │
│  │  Image: postgres:15-alpine                 │         │
│  │  Port: 5432                                │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  Container: pdfpixie-redis                 │         │
│  │  Image: redis:7-alpine                     │         │
│  │  Port: 6379                                │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  Container: pdfpixie-app                   │         │
│  │  (Built from root Dockerfile)              │         │
│  │  ┌──────────────────────────────────────┐  │         │
│  │  │  Supervisor Process Manager          │  │         │
│  │  │  ┌────────────────────────────────┐  │  │         │
│  │  │  │  Nginx (Port 80)               │  │  │         │
│  │  │  │  - Serves React frontend       │  │  │         │
│  │  │  │  - Proxies API to FastAPI      │  │  │         │
│  │  │  │  - WebSocket proxy             │  │  │         │
│  │  │  └────────────────────────────────┘  │  │         │
│  │  │                                       │  │         │
│  │  │  ┌────────────────────────────────┐  │  │         │
│  │  │  │  FastAPI (Port 8000)           │  │  │         │
│  │  │  │  - REST API endpoints          │  │  │         │
│  │  │  │  - Socket.IO WebSocket server  │  │  │         │
│  │  │  │  - PDF processing              │  │  │         │
│  │  │  │  - ChromaDB vector store       │  │  │         │
│  │  │  └────────────────────────────────┘  │  │         │
│  │  └──────────────────────────────────────┘  │         │
│  │  Ports: 80, 8000                           │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🎯 **Why This Architecture?**

### **1. Supervisor in App Container**
- ✅ **Simple**: One container for frontend + backend
- ✅ **Lightweight**: No need for separate containers
- ✅ **Fast**: Nginx and FastAPI communicate via localhost (no network overhead)
- ✅ **Easy debugging**: All logs in one place

### **2. Separate PostgreSQL Container**
- ✅ **Data persistence**: Database survives app restarts
- ✅ **Easy backups**: Can backup DB independently
- ✅ **Resource isolation**: DB memory separate from app
- ✅ **Easy upgrades**: Upgrade DB without rebuilding app

### **3. Separate Redis Container**
- ✅ **Session management**: Persistent sessions across app restarts
- ✅ **Caching**: Fast data access
- ✅ **Easy monitoring**: Monitor Redis independently

## 📁 **File Structure**

```
chatpdf/
├── Dockerfile                    # Main build file (builds frontend + backend)
├── docker-compose.yml            # Orchestrates 3 containers (app, postgres, redis)
├── deploy-ec2.sh                 # Deployment script
│
├── backend/
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   └── app/                      # Application modules
│
├── frontend/
│   ├── package.json              # Node.js dependencies
│   ├── src/                      # React source code
│   └── public/                   # Static assets
│
└── supervisor/                   
    └── supervisord.conf          # (Not used - config is in Dockerfile)
```

## 🚀 **Deployment Process**

### **What the Dockerfile Does:**

1. **Stage 1: Build Frontend** (node:20-alpine)
   - Installs npm packages
   - Runs `npm run build`
   - Creates optimized React bundle

2. **Stage 2: Production Image** (python:3.11-slim)
   - Installs Nginx, Supervisor
   - Installs Python packages
   - Copies backend code
   - Copies built frontend to `/var/www/html`
   - Creates Nginx config (proxies to FastAPI)
   - Creates Supervisor config (manages Nginx + FastAPI)
   - Sets up health check

### **What Docker Compose Does:**

1. Starts PostgreSQL container
2. Starts Redis container
3. Builds app container from Dockerfile
4. Connects all containers via network
5. Sets environment variables
6. Mounts persistent volumes

### **What Supervisor Does (Inside App Container):**

1. Starts Nginx on port 80
2. Starts FastAPI (uvicorn) on port 8000
3. Auto-restarts if either crashes
4. Logs to stdout

## 🔧 **Configuration Files**

### **Dockerfile** (Root)
- Builds entire application
- Embeds Nginx config
- Embeds Supervisor config
- Multi-stage build for optimization

### **docker-compose.yml**
- Defines 3 services: postgres, redis, app
- Sets environment variables
- Manages volumes and networks
- Health checks

### **.env**
- API keys (OPENROUTER_API_KEY)
- Database credentials
- AWS credentials (optional)
- Environment settings

## 📊 **Resource Usage**

```
Container          Memory      CPU    Storage
-----------------------------------------------
pdfpixie-postgres  ~100MB      Low    Depends on data
pdfpixie-redis     ~50MB       Low    ~50MB
pdfpixie-app       ~300-500MB  Med    ~500MB image
-----------------------------------------------
TOTAL              ~500-650MB          ~600MB
```

**Fits comfortably in t3.micro (1GB RAM)** ✅

## 🔄 **Why NOT Separate Frontend/Backend Containers?**

### **Current Approach (1 app container):**
```
Browser → Nginx (port 80) → FastAPI (localhost:8000) → Response
         (same container, localhost)
```
✅ Fast (no network latency)
✅ Simple (one container)
✅ Efficient (shared resources)

### **Alternative Approach (2 containers):**
```
Browser → Nginx (container 1) → FastAPI (container 2) → Response
         (Docker network overhead)
```
❌ Slower (network latency)
❌ Complex (2 containers to manage)
❌ More resources (2 base images)

**For single EC2, current approach is optimal!**

## 🛠️ **Common Operations**

### **Deploy/Update:**
```bash
# On EC2
cd ~/apps/chatpdf
git pull origin main
./deploy-ec2.sh
```

### **View Logs:**
```bash
# All services
docker-compose logs -f

# Just app
docker-compose logs -f app

# Nginx logs inside container
docker-compose exec app tail -f /var/log/nginx/access.log

# FastAPI logs (from supervisor)
docker-compose exec app tail -f /var/log/supervisor/fastapi-stdout.log
```

### **Restart Services:**
```bash
# Restart app only (keeps DB and Redis running)
docker-compose restart app

# Restart everything
docker-compose restart

# Full rebuild
docker-compose down
docker-compose up -d --build
```

### **Database Operations:**
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie

# Backup database
docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > backup.sql

# Restore database
docker-compose exec -T postgres psql -U pdfpixie_user pdfpixie < backup.sql
```

### **Debugging:**
```bash
# Enter app container
docker-compose exec app bash

# Check if services are running
docker-compose exec app ps aux

# Check Nginx config
docker-compose exec app nginx -t

# Check supervisor status
docker-compose exec app supervisorctl status
```

## 🎯 **When to Change Architecture?**

### **Keep Current (Supervisor) If:**
- ✅ Using single EC2 instance (t3.micro/small)
- ✅ < 1000 concurrent users
- ✅ Simple deployment needs
- ✅ Cost-sensitive

### **Switch to Separate Containers If:**
- 🔄 Need independent scaling (scale backend separately)
- 🔄 Multiple EC2 instances with load balancer
- 🔄 Kubernetes deployment
- 🔄 > 5000 concurrent users
- 🔄 Need zero-downtime deployments

## 📝 **Summary**

**Current Setup:**
- 3 Docker containers (app, postgres, redis)
- Supervisor manages Nginx + FastAPI inside app container
- Optimized for single EC2 instance
- Simple, fast, cost-effective

**Why Supervisor Works:**
- Process management inside container
- Auto-restart on crash
- Unified logging
- Perfect for monolithic deployment

**Key Benefit:**
- Entire stack runs on FREE TIER EC2 (t3.micro) ✅
