# 🚀 Simple Deployment (No Supervisor)

## ✅ What Changed

**REMOVED:** Supervisor (was causing the restart loop)  
**ADDED:** Simple bash startup script that runs Nginx + FastAPI

This is simpler, more reliable, and easier to debug.

---

## 📋 Deploy on EC2 (Copy/Paste These Commands)

### **Option 1: Automated Script (Recommended)**

```bash
# SSH to your EC2
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Run this one command
cd ~/apps/chatpdf && \
  git pull origin docker-deployment && \
  bash SIMPLE_DEPLOY.sh
```

That's it! The script will:
- ✅ Pull latest code
- ✅ Check .env file
- ✅ Clean up old containers
- ✅ Build new image
- ✅ Start services
- ✅ Test health endpoint

---

### **Option 2: Manual Step-by-Step**

```bash
# 1. SSH to EC2
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# 2. Go to app directory
cd ~/apps/chatpdf

# 3. Pull latest code
git pull origin docker-deployment

# 4. Stop old containers
docker-compose down -v

# 5. Clean Docker
docker system prune -af

# 6. Build new image (takes 5-10 minutes)
docker-compose build --no-cache app

# 7. Start services
docker-compose up -d

# 8. Wait 60 seconds
sleep 60

# 9. Check status
docker-compose ps

# 10. Test health
curl http://localhost/health
```

---

## 🔍 Verify It's Working

### **Check Container Status**
```bash
docker-compose ps
```

Should show:
```
NAME                STATUS
pdfpixie-app        Up (healthy)
pdfpixie-postgres   Up (healthy)
pdfpixie-redis      Up (healthy)
```

### **Check Logs**
```bash
docker-compose logs app
```

Should show:
```
Starting PDFPixie services...
Starting Nginx...
Starting FastAPI...
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### **Test Health Endpoint**
```bash
curl http://localhost/health
```

Should return:
```json
{"status":"healthy","service":"pdfpixie-api"}
```

### **Test from Browser**
```
http://YOUR-EC2-IP
```

Should show the React frontend with upload screen.

---

## 🐛 Troubleshooting

### **If app container is still restarting:**

```bash
# View logs
docker-compose logs app

# Common issues:
# 1. Missing .env file → Create it
# 2. Wrong API key → Check OPENROUTER_API_KEY
# 3. Port conflict → Check if port 80/8000 in use
```

### **If health check fails:**

```bash
# Check if FastAPI is running
docker-compose exec app ps aux | grep uvicorn

# Check if Nginx is running
docker-compose exec app ps aux | grep nginx

# Check if ports are listening
docker-compose exec app netstat -tuln | grep -E ':(80|8000)'
```

### **If you see "bash: SIMPLE_DEPLOY.sh: Permission denied":**

```bash
chmod +x SIMPLE_DEPLOY.sh
bash SIMPLE_DEPLOY.sh
```

### **Complete fresh start:**

```bash
cd ~/apps/chatpdf
docker-compose down -v
docker system prune -af --volumes
git pull origin docker-deployment
docker-compose up -d --build
sleep 60
docker-compose ps
curl http://localhost/health
```

---

## 📊 Key Differences from Old Setup

| Old (Supervisor) | New (Simple Script) |
|------------------|---------------------|
| Supervisor manages services | Bash script starts services |
| Complex config files | Simple 10-line script |
| Restart loops on errors | Clear error messages |
| Hard to debug | Easy to see what's running |
| `/var/run/supervisor.sock` issues | No socket files needed |

---

## 🎯 How It Works Now

1. **Container starts** → Runs `/app/start.sh`
2. **start.sh** starts Nginx in background
3. **start.sh** starts FastAPI in foreground (keeps container alive)
4. **Health check** tests `http://localhost/health` every 30s
5. **Nginx** proxies requests from port 80 → FastAPI on port 8000

---

## ✅ Success Checklist

- [ ] `git pull` successful
- [ ] `.env` file exists with valid `OPENROUTER_API_KEY`
- [ ] `docker-compose build` completed without errors
- [ ] `docker-compose ps` shows all containers as "Up (healthy)"
- [ ] `curl http://localhost/health` returns JSON
- [ ] Browser shows React app at `http://YOUR-EC2-IP`
- [ ] Can upload a PDF file
- [ ] Can chat with the PDF

---

## 📞 Still Having Issues?

Run this diagnostic:

```bash
echo "=== DIAGNOSTIC ==="
docker-compose ps
echo ""
docker-compose logs app | tail -50
echo ""
docker-compose exec app ps aux
echo ""
curl http://localhost/health
```

Share the output for further help.

---

## 🚀 Next Steps After Deployment

1. **Set up SSL/HTTPS** (optional)
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

2. **Set up monitoring** (optional)
   - CloudWatch for logs
   - Prometheus + Grafana for metrics

3. **Enable auto-restart** (already done)
   - `restart: unless-stopped` in docker-compose.yml

4. **Backup data** (optional)
   ```bash
   docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > backup.sql
   ```

---

🎉 **That's it! Your app should now be running smoothly without Supervisor!**
