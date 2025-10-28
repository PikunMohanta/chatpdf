# PDFPixie - Quick Deployment Guide

## 🚀 3 Ways to Deploy

### 1️⃣ Docker (Fastest - 5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf

# Build image
docker build -t pdfpixie:latest .

# Run container
docker run -d \
  --name pdfpixie-app \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -p 80:80 \
  -e OPENROUTER_API_KEY=your_key_here \
  pdfpixie:latest

# Access at http://localhost
```

### 2️⃣ AWS EC2 (Production - 1 hour)

**See full guide**: [EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md](./EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md)

**Quick steps:**
1. Launch EC2 t3.small with Ubuntu 24.04
2. Open ports 22, 80, 443 in Security Groups
3. SSH and install Docker
4. Clone repo and run Docker command above
5. Access at `http://your-ec2-ip`

**Cost**: $0 (free tier 12 months) → $20-30/month after

### 3️⃣ Local Development (2 terminals)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:socket_app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

Access at http://localhost:3000

---

## ✅ Deployment Checklist

### Before Deploying
- [ ] Get OpenRouter API key from https://openrouter.ai
- [ ] Have Docker installed locally or on EC2
- [ ] Have domain name (optional, can use IP)

### After Deploying
- [ ] Test health endpoint: `curl http://your-ip/health`
- [ ] Test upload PDF functionality
- [ ] Test chat WebSocket connection
- [ ] Check logs: `docker logs -f pdfpixie-app`
- [ ] Setup SSL with Let's Encrypt (production)
- [ ] Configure automated backups

---

## 🔧 Essential Commands

```bash
# Build
docker build -t pdfpixie:latest .

# Run (with DNS fix for OpenRouter API)
docker run -d --name pdfpixie-app \
  --dns 8.8.8.8 --dns 8.8.4.4 \
  -p 80:80 -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_key \
  pdfpixie:latest

# Stop
docker stop pdfpixie-app

# Remove
docker rm pdfpixie-app

# View logs
docker logs -f pdfpixie-app

# Check status
docker ps

# Restart
docker restart pdfpixie-app

# Shell access
docker exec -it pdfpixie-app bash
```

---

## 🚨 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Chat not working | Ensure using `main:socket_app` in Dockerfile |
| OpenRouter API fails | Add `--dns 8.8.8.8 --dns 8.8.4.4` flags |
| PDF worker error | Check `/pdf.worker.min.js` is at web root |
| Port 80 in use | Change to `-p 8080:80` |
| Container unhealthy | Check logs with `docker logs pdfpixie-app` |

---

## 📊 Image Specifications

- **Size**: 859MB (optimized)
- **Base**: Python 3.11-slim
- **Services**: Nginx + FastAPI + Socket.IO
- **Ports**: 80 (HTTP), 8000 (API)
- **Health Check**: Automated every 30s

---

## 🌐 Access Points

| Service | Local | EC2 |
|---------|-------|-----|
| Frontend | http://localhost | http://your-ec2-ip |
| Backend API | http://localhost:8000 | http://your-ec2-ip:8000 |
| API Docs | http://localhost:8000/docs | http://your-ec2-ip:8000/docs |
| Health Check | http://localhost/health | http://your-ec2-ip/health |

---

## 💡 Pro Tips

1. **Use Docker** - Simplest and most reliable deployment method
2. **DNS is critical** - Always include `--dns 8.8.8.8 --dns 8.8.4.4`
3. **Monitor logs** - Use `docker logs -f` to watch real-time activity
4. **SSL in production** - Use Let's Encrypt for free certificates
5. **Backup data** - Persist `/app/data` volume for chat history
6. **Scale up** - Use t3.small on EC2 for better performance

---

**Need detailed instructions?** → [EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md](./EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md)

**Need help?** → Open an issue on GitHub
