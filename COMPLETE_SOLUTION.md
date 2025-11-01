# 🎯 Multi-Device Access Fix - Complete Solution

## 🚨 Problem Summary

Your PDFPixie application was working perfectly on the AWS instance itself, but when trying to access it from other devices (phones, tablets, other computers), you got this error:

```
Failed to fetch
fetch("http://localhost:8000/api/upload", {Failed to load resource: net::ERR_CONNECTION_REFUSED
```

**Root Cause**: The frontend code had hardcoded `localhost:8000` URLs, which only work on the same machine. Other devices tried to connect to *their own* localhost instead of your AWS server.

---

## ✅ Solution Applied

### All Fixed Files (8 total):

1. **`frontend/.env.production`** - Updated to use AWS IP
2. **`frontend/src/components/ChatWorkspace.tsx`** - Dynamic API URLs
3. **`frontend/src/components/UploadScreen.tsx`** - Dynamic API URLs
4. **`frontend/src/components/PdfViewer.tsx`** - Dynamic API URLs
5. **`frontend/src/components/ChatPanel.tsx`** - Dynamic API + WebSocket URLs
6. **`frontend/src/App.tsx`** - Dynamic session management URLs
7. **`nginx/nginx.conf`** - Complete nginx configuration
8. **`nginx/conf.d/pdfpixie.conf`** - Domain + IP routing

### What Changed:

**Before:**
```typescript
fetch('http://localhost:8000/api/upload', {...})
```

**After:**
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
fetch(`${apiUrl}/api/upload`, {...})
```

---

## 🚀 Deployment Options

### Option A: Automated Transfer & Deploy (RECOMMENDED)

**From your Windows machine:**
```batch
transfer_to_aws.bat "C:\path\to\your\aws-key.pem"
```

**From Linux/Mac:**
```bash
chmod +x transfer_to_aws.sh
./transfer_to_aws.sh ~/.ssh/your-aws-key.pem
```

This will:
1. Transfer all fixed files to AWS
2. Rebuild the frontend
3. Build new Docker image
4. Deploy the updated container
5. Test the deployment

### Option B: Manual Deployment on AWS

**Step 1: Transfer files to AWS**
```bash
# Using Git (if you pushed to GitHub)
ssh -i your-key.pem ubuntu@13.201.129.219
cd /home/ubuntu/chatpdf
git pull

# Or using SCP
scp -i your-key.pem -r frontend nginx deploy.sh ubuntu@13.201.129.219:/home/ubuntu/chatpdf/
```

**Step 2: Deploy on AWS instance**
```bash
ssh -i your-key.pem ubuntu@13.201.129.219
cd /home/ubuntu/chatpdf

# Set your API key
export OPENROUTER_API_KEY="your-key-here"

# Run deployment
chmod +x deploy.sh
./deploy.sh
```

---

## 🧪 Testing the Fix

### 1. From AWS Instance Itself
```bash
curl http://localhost/health
# Should return: {"status":"healthy"}
```

### 2. From Your Local Computer
```bash
curl http://13.201.129.219/health
# Or open in browser: http://13.201.129.219
```

### 3. From Mobile Device
1. Connect to WiFi or mobile data
2. Open browser
3. Navigate to `http://13.201.129.219`
4. Upload a PDF
5. Test chat functionality

### 4. Expected Results ✅
- ✅ App loads correctly
- ✅ PDF upload works from any device
- ✅ Chat responds properly
- ✅ PDF preview displays
- ✅ Real-time WebSocket connection works

---

## 🌐 Domain Configuration (pdfpixie.duckdns.org)

### Quick Setup:

1. **Update DuckDNS**
   - Go to https://www.duckdns.org/
   - Login and find your domain: `pdfpixie`
   - Set IP to: `13.201.129.219`
   - Copy your token for auto-updates

2. **Test DNS Resolution**
   ```bash
   ping pdfpixie.duckdns.org
   # Should resolve to 13.201.129.219
   ```

3. **Access via Domain**
   - Open browser: `http://pdfpixie.duckdns.org`
   - Should work exactly like IP access

### (Optional) Use Domain in Frontend

If you want to use the domain name instead of IP:

```bash
# Edit frontend/.env.production
VITE_API_BASE_URL=http://pdfpixie.duckdns.org
VITE_WS_URL=http://pdfpixie.duckdns.org

# Rebuild and redeploy
cd frontend && npm run build && cd ..
./deploy.sh
```

---

## 🔒 Adding HTTPS (Optional)

### Why Add HTTPS?
- ✅ Secure data transmission
- ✅ Better browser compatibility
- ✅ Professional appearance
- ✅ Required for some features (like camera access)

### Quick Setup:

```bash
# On AWS instance
sudo apt update
sudo apt install certbot -y

# Get SSL certificate (domain must be configured first)
sudo certbot certonly --standalone -d pdfpixie.duckdns.org

# Update frontend to use HTTPS
cd /home/ubuntu/chatpdf
nano frontend/.env.production
# Change http:// to https://

# Rebuild with HTTPS support
cd frontend && npm run build && cd ..

# Edit nginx config to enable HTTPS
nano nginx/conf.d/pdfpixie.conf
# Uncomment the HTTPS server block

# Rebuild and deploy with port 443
docker build -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie
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

### Auto-Renew Certificate
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot sets up auto-renewal by default
sudo systemctl status certbot.timer
```

---

## 🔧 Troubleshooting

### Issue 1: Still getting "Failed to fetch"

**Check 1: Verify new build**
```bash
# On AWS instance
docker exec pdfpixie cat /var/www/html/index.html | grep -o 'http://[^"]*' | head -5
# Should show 13.201.129.219, NOT localhost
```

**Check 2: Browser console**
- Open browser DevTools (F12)
- Go to Network tab
- Try uploading a PDF
- Look at the request URL - should be `http://13.201.129.219/api/upload`

**Fix:**
```bash
# Rebuild from scratch
cd /home/ubuntu/chatpdf
cd frontend && npm run build && cd ..
docker build --no-cache -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie
./deploy.sh
```

### Issue 2: WebSocket Connection Failed

**Check:**
```bash
# Test WebSocket endpoint
curl -i http://13.201.129.219/socket.io/
# Should return HTTP 200 or 101
```

**Check logs:**
```bash
docker logs pdfpixie | grep -i "socket\|websocket"
```

### Issue 3: Port 8000 Not Accessible

**AWS Security Group Check:**
1. Go to AWS Console → EC2 → Security Groups
2. Find your instance's security group
3. Check Inbound Rules:
   ```
   Port 80   - TCP - 0.0.0.0/0
   Port 8000 - TCP - 0.0.0.0/0
   Port 443  - TCP - 0.0.0.0/0 (if using HTTPS)
   ```

### Issue 4: Large PDF Upload Fails

**Check nginx config:**
```bash
docker exec pdfpixie grep client_max_body_size /etc/nginx/conf.d/pdfpixie.conf
# Should show: client_max_body_size 100M;
```

**Check logs during upload:**
```bash
docker logs pdfpixie -f
# Upload a large PDF and watch for errors
```

### Issue 5: DNS Not Resolving

**Test DNS:**
```bash
nslookup pdfpixie.duckdns.org
# Should return 13.201.129.219
```

**Update DuckDNS manually:**
```bash
curl "https://www.duckdns.org/update?domains=pdfpixie&token=YOUR_TOKEN&ip=13.201.129.219"
```

---

## 📊 Verification Checklist

Use this checklist after deployment:

- [ ] Container is running: `docker ps | grep pdfpixie`
- [ ] Health check passes: `curl http://localhost/health`
- [ ] Accessible from outside: `curl http://13.201.129.219/health`
- [ ] Frontend loads in browser: `http://13.201.129.219`
- [ ] No console errors in browser (F12)
- [ ] PDF upload works from local machine
- [ ] PDF upload works from phone/tablet
- [ ] Chat responses work
- [ ] PDF preview displays
- [ ] WebSocket connection established (check browser console)
- [ ] Domain resolves correctly: `ping pdfpixie.duckdns.org`
- [ ] Domain access works: `http://pdfpixie.duckdns.org`

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `FIX_SUMMARY.md` | Detailed summary of what was fixed |
| `AWS_DEPLOYMENT_GUIDE.md` | Complete deployment guide with all options |
| `QUICK_DEPLOY.md` | Quick reference card for common tasks |
| `THIS_FILE.md` | Complete solution overview (this file) |
| `deploy.sh` | Automated deployment script |
| `transfer_to_aws.sh` | Linux/Mac file transfer script |
| `transfer_to_aws.bat` | Windows file transfer script |

---

## 🎓 Understanding the Fix

### Environment Variables in Vite

Vite uses environment variables prefixed with `VITE_`:

```bash
# .env.production
VITE_API_BASE_URL=http://13.201.129.219
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

### Build-time vs Runtime

**Important**: Vite environment variables are **build-time**, not runtime. This means:
- ✅ You must rebuild frontend after changing `.env.production`
- ✅ The API URL is baked into the JavaScript bundle
- ✅ Each deployment environment needs its own build

### Dynamic API Configuration

All API calls now follow this pattern:
```typescript
// Get API URL from environment, fallback to localhost for development
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Use it in API calls
fetch(`${apiUrl}/api/endpoint`, {...})
axios.get(`${apiUrl}/api/endpoint`, {...})
io(apiUrl, {...})  // For Socket.IO
```

---

## 🚀 Next Steps

### Immediate (Required):
1. ✅ Deploy the fix using `./deploy.sh` or transfer scripts
2. ✅ Test from multiple devices
3. ✅ Verify all functionality works

### Short-term (Recommended):
1. 🔒 Set up HTTPS with Let's Encrypt
2. 🌐 Configure DuckDNS properly
3. 🔐 Replace `dev-token` with proper authentication
4. 📊 Set up monitoring and logging

### Long-term (Production):
1. 🗄️ Set up PostgreSQL backups
2. ⚖️ Configure load balancing if needed
3. 🔄 Set up CI/CD pipeline
4. 📈 Implement analytics and error tracking
5. 🛡️ Add rate limiting and security headers

---

## 💡 Key Takeaways

1. **Never hardcode URLs** - Always use environment variables
2. **Test from multiple devices** - What works locally might not work remotely
3. **Check browser console** - Most networking errors show up there
4. **Verify security groups** - AWS firewall rules are crucial
5. **Use HTTPS in production** - It's easier than you think with Let's Encrypt

---

## 🆘 Getting Help

### Check Logs:
```bash
# Container logs
docker logs pdfpixie -f

# Nginx access logs
docker exec pdfpixie tail -f /var/log/nginx/access.log

# Nginx error logs
docker exec pdfpixie tail -f /var/log/nginx/error.log
```

### Common Commands:
```bash
# Restart everything
docker restart pdfpixie

# Rebuild from scratch
cd frontend && npm run build && cd ..
docker build --no-cache -t pdfpixie:latest -f Dockerfile .
docker stop pdfpixie && docker rm pdfpixie
./deploy.sh

# Check what's running on ports
sudo lsof -i :80
sudo lsof -i :8000

# Test API directly
curl http://13.201.129.219/api/health
curl http://13.201.129.219/health
```

---

## ✨ Success!

Your PDFPixie application is now configured for multi-device access! 

**Access URLs:**
- 🌐 **IP**: http://13.201.129.219
- 🌐 **Domain**: http://pdfpixie.duckdns.org
- 📚 **API Docs**: http://13.201.129.219:8000/docs

Share these URLs with anyone, and they'll be able to use your PDF analysis tool from any device!

---

**Questions?** Check the documentation files or review the logs for troubleshooting.
