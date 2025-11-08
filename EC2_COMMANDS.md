# 🚀 EC2 Deployment - Copy/Paste Commands

## ⚡ **Quick Fix (30 seconds)**

SSH to your EC2 and run these commands:

```bash
# Navigate to app directory
cd ~/apps/chatpdf

# Pull fixed configuration
git pull origin docker-deployment

# Stop old containers
docker-compose down

# Clean up Docker
docker system prune -af

# Rebuild and start
docker-compose up -d --build

# Wait 30 seconds for services to start
sleep 30

# Check status
docker-compose ps

# Test health
curl http://localhost/health
```

Expected output:
```
{"status":"healthy","service":"pdfpixie-api"}
```

## 📋 **Step-by-Step (If Quick Fix Doesn't Work)**

### **Step 1: Check Current Directory**
```bash
pwd
# Should show: /home/ubuntu/apps/chatpdf
```

If not in correct directory:
```bash
cd ~/apps/chatpdf
```

### **Step 2: Verify Git Repository**
```bash
git status
git branch
```

Should show you're in the `chatpdf` repository.

### **Step 3: Pull Latest Changes**
```bash
git pull origin docker-deployment
```

Expected: "Updating ... Fast-forward"

### **Step 4: Verify Files Exist**
```bash
ls -la
```

Should see:
- ✅ `Dockerfile` (at root)
- ✅ `docker-compose.yml` (at root)
- ✅ `backend/` directory
- ✅ `frontend/` directory

### **Step 5: Check .env File**
```bash
cat .env
```

Should contain:
- `OPENROUTER_API_KEY=sk-or-v1-...` (your actual key)
- `DATABASE_URL=postgresql://...`
- Other environment variables

If `.env` doesn't exist:
```bash
cat > .env << 'EOF'
ENVIRONMENT=production
DEBUG=false
OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
FRONTEND_URL=http://YOUR-EC2-IP

POSTGRES_USER=pdfpixie_user
POSTGRES_PASSWORD=SecurePassword123!
POSTGRES_DB=pdfpixie

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
EOF

# Edit with your actual values
nano .env
```

### **Step 6: Stop Existing Containers**
```bash
docker-compose down -v
```

This removes all containers and volumes.

### **Step 7: Clean Docker System**
```bash
# Remove old images
docker system prune -af

# Verify cleanup
docker images
docker ps -a
```

Should show minimal or no containers/images.

### **Step 8: Build Fresh**
```bash
# Build the app container (takes 5-10 minutes)
docker-compose build --no-cache app

# Watch for errors during build
```

Expected output:
```
[+] Building 300.5s (20/20) FINISHED
 => [frontend-builder 1/5] FROM node:20-alpine
 => [stage-1 1/8] FROM python:3.11-slim
 ...
 => => naming to docker.io/library/chatpdf-app
```

### **Step 9: Start All Services**
```bash
docker-compose up -d
```

Expected output:
```
[+] Running 3/3
 ✔ Container pdfpixie-postgres  Started
 ✔ Container pdfpixie-redis     Started
 ✔ Container pdfpixie-app       Started
```

### **Step 10: Wait for Services**
```bash
# Wait 30 seconds for services to initialize
sleep 30

# Check container status
docker-compose ps
```

Expected output:
```
NAME                  STATUS                   PORTS
pdfpixie-app          Up (healthy)            0.0.0.0:80->80/tcp
pdfpixie-postgres     Up (healthy)            5432/tcp
pdfpixie-redis        Up (healthy)            6379/tcp
```

**Important:** All should show `Up (healthy)` or `Up`.

### **Step 11: Check Logs**
```bash
# View all logs
docker-compose logs

# View just app logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

Look for:
- ✅ "INFO:     Started server process"
- ✅ "INFO:     Application startup complete"
- ✅ "nginx: ready"
- ❌ No ERROR messages

Press `Ctrl+C` to exit logs.

### **Step 12: Test Health Endpoint**
```bash
# Test from EC2
curl http://localhost/health

# Expected response:
# {"status":"healthy","service":"pdfpixie-api"}
```

### **Step 13: Test from Your Laptop**
```bash
# On your laptop (not EC2)
curl http://YOUR-EC2-IP/health

# Or open in browser:
http://YOUR-EC2-IP
```

## 🔍 **Troubleshooting**

### **Problem: "Unlinking stale socket" loop**

This means supervisor is crashing. Check app logs:

```bash
docker-compose logs app | tail -50
```

**Fix:**
```bash
docker-compose down
docker system prune -af
docker-compose up -d --build
```

### **Problem: "Unable to prepare context: no such file or directory"**

This means docker-compose is looking for wrong Dockerfile.

**Verify docker-compose.yml has:**
```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile  # ← Should be just "Dockerfile"
```

**Fix:**
```bash
nano docker-compose.yml
# Find the app service
# Make sure it says: dockerfile: Dockerfile
# Save: Ctrl+O, Enter, Ctrl+X

docker-compose up -d --build
```

### **Problem: Container immediately exits**

Check why it's exiting:

```bash
docker-compose logs app
```

Common causes:
- Missing .env file → Create .env
- Wrong port bindings → Check ports 80, 8000 aren't in use
- Syntax error in code → Check logs for Python errors

**Fix:**
```bash
# Check what's using port 80
sudo netstat -tuln | grep :80

# If something is using it, stop it
sudo systemctl stop apache2  # or nginx, etc.

# Restart
docker-compose restart app
```

### **Problem: "Connection refused" when accessing app**

Check firewall and ports:

```bash
# Check if containers are running
docker-compose ps

# Check if port 80 is listening
sudo netstat -tuln | grep :80

# Check AWS Security Group allows port 80
# Go to EC2 Console → Security Groups → Check inbound rules
```

**Fix:**
```bash
# Restart app
docker-compose restart app

# Check Nginx inside container
docker-compose exec app ps aux | grep nginx

# Should show nginx processes
```

### **Problem: Health check keeps failing**

Check if FastAPI is running:

```bash
# Check if port 8000 is responding
docker-compose exec app curl http://localhost:8000/health

# Check supervisor status
docker-compose exec app supervisorctl status

# Should show:
# fastapi    RUNNING
# nginx      RUNNING
```

**Fix:**
```bash
# Restart supervisor inside container
docker-compose exec app supervisorctl restart all

# Or restart entire container
docker-compose restart app
```

## 📊 **Verification Checklist**

After deployment, verify:

- [ ] `docker-compose ps` shows all containers as "Up (healthy)"
- [ ] `curl http://localhost/health` returns JSON with "healthy"
- [ ] Browser shows React frontend at `http://YOUR-EC2-IP`
- [ ] API docs accessible at `http://YOUR-EC2-IP/docs`
- [ ] Can upload a PDF file
- [ ] Can ask questions about PDF
- [ ] Responses appear in chat
- [ ] No errors in `docker-compose logs`

## 🎯 **Expected Timeline**

- **Pull code**: 5 seconds
- **Build image**: 5-10 minutes (first time)
- **Start containers**: 30 seconds
- **Health checks**: 30-60 seconds
- **Total**: 7-12 minutes

## 📝 **Quick Reference**

```bash
# View logs
docker-compose logs -f app

# Restart app
docker-compose restart app

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Rebuild
docker-compose up -d --build

# Check status
docker-compose ps

# Check resource usage
docker stats

# Enter container
docker-compose exec app bash

# Database access
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie
```

## 🆘 **Still Not Working?**

Run this diagnostic:

```bash
#!/bin/bash
echo "=== DIAGNOSTIC REPORT ==="
echo ""
echo "1. Current directory:"
pwd
echo ""
echo "2. Git status:"
git status
echo ""
echo "3. Files present:"
ls -la | head -20
echo ""
echo "4. Docker containers:"
docker-compose ps
echo ""
echo "5. Docker images:"
docker images | grep pdfpixie
echo ""
echo "6. Listening ports:"
sudo netstat -tuln | grep -E ':(80|8000|5432|6379)'
echo ""
echo "7. App container logs (last 30 lines):"
docker-compose logs app | tail -30
echo ""
echo "8. Environment file:"
ls -la .env
echo ""
echo "=== END REPORT ==="
```

Copy the output and share it for help.

## ✅ **Success Indicators**

You'll know it's working when:

1. **Terminal shows:**
   ```
   [+] Running 3/3
    ✔ Container pdfpixie-postgres  Started
    ✔ Container pdfpixie-redis     Started
    ✔ Container pdfpixie-app       Started
   ```

2. **Status shows healthy:**
   ```
   $ docker-compose ps
   NAME                STATUS
   pdfpixie-app        Up (healthy)
   pdfpixie-postgres   Up (healthy)
   pdfpixie-redis      Up (healthy)
   ```

3. **Health endpoint works:**
   ```
   $ curl http://localhost/health
   {"status":"healthy","service":"pdfpixie-api"}
   ```

4. **Browser shows React app** at your EC2 IP address

5. **You can upload PDFs and chat with them**

🎉 **Congratulations - you're deployed!**
