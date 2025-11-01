# 🚀 Quick Deployment Reference Card

## ⚡ Quick Deploy (Copy-Paste Ready)

### On Your AWS Instance (13.201.129.219):

```bash
# Step 1: Navigate to project
cd /path/to/chatpdf

# Step 2: Set your API key
export OPENROUTER_API_KEY="your-key-here"

# Step 3: Make deploy script executable
chmod +x deploy.sh

# Step 4: Deploy!
./deploy.sh
```

That's it! Your app will be accessible from any device at:
- **http://13.201.129.219**
- **http://pdfpixie.duckdns.org** (after DuckDNS setup)

---

## 🔍 Quick Checks

### Is it deployed?
```bash
docker ps | grep pdfpixie
```

### Is it healthy?
```bash
curl http://localhost/health
```

### Check logs
```bash
docker logs pdfpixie -f
```

### Test from outside
```bash
# From your local machine:
curl http://13.201.129.219/health
```

---

## 🐛 Quick Fixes

### Container not starting?
```bash
docker logs pdfpixie
docker restart pdfpixie
```

### Still seeing localhost errors?
Make sure you rebuilt after the fixes:
```bash
cd frontend && npm run build && cd ..
docker build -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie
# Then run deploy.sh again
```

### Port already in use?
```bash
sudo lsof -i :80
sudo lsof -i :8000
# Kill the process or stop old container
docker stop pdfpixie && docker rm pdfpixie
```

---

## 🌐 Domain Setup (pdfpixie.duckdns.org)

### 1. Configure DuckDNS:
- Go to https://www.duckdns.org/
- Login and update `pdfpixie` to point to `13.201.129.219`
- Save your token

### 2. Test DNS:
```bash
ping pdfpixie.duckdns.org
# Should return 13.201.129.219
```

### 3. (Optional) Use domain in frontend:
```bash
# Edit frontend/.env.production
VITE_API_BASE_URL=http://pdfpixie.duckdns.org
VITE_WS_URL=http://pdfpixie.duckdns.org

# Rebuild
cd frontend && npm run build && cd ..
./deploy.sh
```

---

## 🔒 Add HTTPS (Optional but Recommended)

### Install Certbot:
```bash
sudo apt update
sudo apt install certbot -y
```

### Get Certificate:
```bash
sudo certbot certonly --standalone -d pdfpixie.duckdns.org
```

### Update Frontend:
```bash
# Edit frontend/.env.production
VITE_API_BASE_URL=https://pdfpixie.duckdns.org
VITE_WS_URL=https://pdfpixie.duckdns.org
```

### Rebuild with HTTPS:
```bash
cd frontend && npm run build && cd ..
docker build -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie

# Run with port 443 and SSL certs
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
```

Don't forget to uncomment HTTPS section in `nginx/conf.d/pdfpixie.conf`!

---

## 📱 Test from Multiple Devices

### From Phone:
1. Connect to WiFi or mobile data
2. Open browser
3. Go to `http://13.201.129.219`
4. Upload PDF and test chat

### From Tablet/Other Computer:
1. Open browser
2. Go to `http://13.201.129.219` or `http://pdfpixie.duckdns.org`
3. Upload PDF and test

### Expected Result:
✅ App loads
✅ Upload works
✅ Chat responds
✅ PDF preview shows

---

## 🆘 Emergency Commands

### Complete Reset:
```bash
docker stop pdfpixie
docker rm pdfpixie
docker rmi pdfpixie:latest
./deploy.sh
```

### View All Logs:
```bash
docker logs pdfpixie --tail 200
```

### Get Shell Access:
```bash
docker exec -it pdfpixie /bin/bash
```

### Check Nginx Inside Container:
```bash
docker exec pdfpixie nginx -t
docker exec pdfpixie cat /etc/nginx/conf.d/pdfpixie.conf
```

---

## 📊 What Was Fixed?

**Before:**
- Frontend hardcoded `localhost:8000` URLs
- Only worked on server itself
- Other devices got "Failed to fetch" error

**After:**
- Frontend uses environment variables
- Points to `13.201.129.219` (your AWS IP)
- Works from ANY device on internet

**Fixed Files:**
- ChatWorkspace.tsx
- UploadScreen.tsx
- PdfViewer.tsx
- ChatPanel.tsx (+ Socket.IO)
- App.tsx
- .env.production
- nginx configuration

---

## 📚 More Info

- **Full Guide**: `AWS_DEPLOYMENT_GUIDE.md`
- **Detailed Summary**: `FIX_SUMMARY.md`
- **API Docs**: http://13.201.129.219:8000/docs

---

## ✅ Success Checklist

- [ ] Deployed using `./deploy.sh`
- [ ] Container is running (`docker ps`)
- [ ] Health check passes (`curl http://localhost/health`)
- [ ] Accessible from local machine (`curl http://13.201.129.219`)
- [ ] Tested from phone/tablet
- [ ] PDF upload works from other device
- [ ] Chat responses work
- [ ] (Optional) DuckDNS configured
- [ ] (Optional) HTTPS with Let's Encrypt

---

🎉 **Your PDFPixie is now accessible from anywhere!**
