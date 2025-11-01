# PDFPixie AWS Deployment Guide

## Current Deployment Status
- **AWS Instance IP**: 13.201.129.219
- **Domain**: pdfpixie.duckdns.org
- **Status**: Configured for multi-device access ✅

---

## Quick Fix Deployment Steps

### 1. Rebuild Frontend with Production Config
```bash
cd frontend
npm run build
```

This will use the `.env.production` file which now points to `http://13.201.129.219` instead of localhost.

### 2. Rebuild Docker Image
```bash
# From project root
docker build -t pdfpixie:latest -f Dockerfile .
```

### 3. Stop Current Container (if running)
```bash
docker stop pdfpixie 2>/dev/null || true
docker rm pdfpixie 2>/dev/null || true
```

### 4. Deploy Updated Container
```bash
docker run -d \
  --name pdfpixie \
  -p 80:80 \
  -p 8000:8000 \
  -v $(pwd)/backend/data:/app/data \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  --restart unless-stopped \
  pdfpixie:latest
```

### 5. Verify Deployment
```bash
# Check container status
docker ps | grep pdfpixie

# Check logs
docker logs pdfpixie --tail 50

# Test from AWS instance
curl http://localhost/health

# Test from outside (replace with your IP)
curl http://13.201.129.219/health
```

---

## Domain Configuration (pdfpixie.duckdns.org)

### Step 1: Configure DuckDNS
1. Go to https://www.duckdns.org/
2. Login and find your domain: `pdfpixie`
3. Update the IP to your AWS instance: `13.201.129.219`
4. Save the token for automatic updates

### Step 2: Setup DuckDNS Auto-Update (Optional)
Create a cron job to keep your IP updated:
```bash
# On your AWS instance
mkdir -p ~/duckdns
cd ~/duckdns

# Create update script
cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=pdfpixie&token=YOUR_TOKEN_HERE&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x duck.sh

# Add to crontab (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1") | crontab -
```

### Step 3: Update Frontend for Domain
Edit `frontend/.env.production` to use domain:
```bash
VITE_API_BASE_URL=http://pdfpixie.duckdns.org
VITE_WS_URL=http://pdfpixie.duckdns.org
```

Then rebuild and redeploy.

### Step 4: Access Your App
- **Via IP**: http://13.201.129.219
- **Via Domain**: http://pdfpixie.duckdns.org

---

## Adding HTTPS (SSL) with Let's Encrypt

### Prerequisites
- Domain properly configured (pdfpixie.duckdns.org)
- Port 80 and 443 open in AWS security group

### Install Certbot on AWS Instance
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot certonly --standalone -d pdfpixie.duckdns.org
```

### Update Nginx Configuration
The nginx config in `nginx/conf.d/pdfpixie.conf` already has HTTPS section commented out. Uncomment it after getting certificates.

### Update Frontend for HTTPS
Edit `frontend/.env.production`:
```bash
VITE_API_BASE_URL=https://pdfpixie.duckdns.org
VITE_WS_URL=https://pdfpixie.duckdns.org
```

### Rebuild and Deploy
```bash
cd frontend && npm run build && cd ..
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

### Auto-Renew SSL Certificate
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is configured by default
# Verify: sudo systemctl status certbot.timer
```

---

## AWS Security Group Configuration

Ensure these ports are open:
- **Port 80** (HTTP) - Allow from 0.0.0.0/0
- **Port 443** (HTTPS) - Allow from 0.0.0.0/0
- **Port 8000** (Backend API) - Allow from 0.0.0.0/0
- **Port 22** (SSH) - Allow from your IP only

### Update Security Group
1. Go to AWS Console → EC2 → Security Groups
2. Select your instance's security group
3. Edit Inbound Rules:
   ```
   Type          Protocol   Port Range   Source
   HTTP          TCP        80           0.0.0.0/0
   HTTPS         TCP        443          0.0.0.0/0
   Custom TCP    TCP        8000         0.0.0.0/0
   SSH           TCP        22           Your-IP/32
   ```

---

## Troubleshooting

### Issue: "Failed to fetch" from other devices
**Cause**: Frontend trying to connect to localhost instead of server IP
**Fix**: Rebuild frontend with proper `.env.production` settings

### Issue: CORS errors
**Check**: Backend CORS settings in `backend/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: WebSocket connection fails
**Check**: 
1. Nginx WebSocket proxy configuration
2. Port 8000 accessible from outside
3. Socket.IO CORS settings in backend

### Issue: Large PDF uploads fail
**Check**:
1. Nginx `client_max_body_size` (set to 100M)
2. AWS security group timeout settings
3. Backend timeout configuration

### Check Logs
```bash
# Container logs
docker logs pdfpixie --tail 100 -f

# Nginx logs (inside container)
docker exec pdfpixie tail -f /var/log/nginx/access.log
docker exec pdfpixie tail -f /var/log/nginx/error.log

# Backend logs
docker exec pdfpixie tail -f /app/logs/backend.log
```

---

## Quick Deployment Script

Create `deploy.sh` in project root:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying PDFPixie to AWS..."

# Build frontend
echo "📦 Building frontend..."
cd frontend && npm run build && cd ..

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t pdfpixie:latest -f Dockerfile .

# Stop and remove old container
echo "🛑 Stopping old container..."
docker stop pdfpixie 2>/dev/null || true
docker rm pdfpixie 2>/dev/null || true

# Run new container
echo "▶️  Starting new container..."
docker run -d \
  --name pdfpixie \
  -p 80:80 \
  -p 443:443 \
  -p 8000:8000 \
  -v $(pwd)/backend/data:/app/data \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  --restart unless-stopped \
  pdfpixie:latest

# Wait for container to start
echo "⏳ Waiting for container to be healthy..."
sleep 10

# Check status
echo "✅ Deployment complete!"
docker ps | grep pdfpixie
echo ""
echo "🌐 Access your app at:"
echo "   - http://13.201.129.219"
echo "   - http://pdfpixie.duckdns.org"
```

Make it executable:
```bash
chmod +x deploy.sh
```

Run deployment:
```bash
./deploy.sh
```

---

## Environment Variables Checklist

### On AWS Instance
```bash
export OPENROUTER_API_KEY="your-key-here"
export POSTGRES_PASSWORD="secure-password"
export SECRET_KEY="$(openssl rand -hex 32)"
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export OPENROUTER_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Testing Multi-Device Access

### From Your Local Machine
```bash
# Test health endpoint
curl http://13.201.129.219/health
curl http://pdfpixie.duckdns.org/health

# Test from browser
http://13.201.129.219
http://pdfpixie.duckdns.org
```

### From Mobile Device
1. Connect to same WiFi or use mobile data
2. Open browser
3. Navigate to `http://13.201.129.219` or `http://pdfpixie.duckdns.org`
4. Upload a PDF and test chat

---

## Production Best Practices

1. **Use HTTPS**: Set up SSL certificates with Let's Encrypt
2. **Secure Backend**: Replace `dev-token` with proper JWT authentication
3. **Database Backup**: Regular backups of PostgreSQL data
4. **Monitoring**: Set up CloudWatch or similar monitoring
5. **Auto-scaling**: Use AWS Auto Scaling Groups for high traffic
6. **CDN**: Consider CloudFront for static assets
7. **Rate Limiting**: Implement rate limiting on API endpoints
8. **Logging**: Centralized logging with ELK or CloudWatch Logs

---

## Support

If you encounter issues:
1. Check container logs: `docker logs pdfpixie`
2. Verify network connectivity: `curl http://localhost/health`
3. Check AWS security group settings
4. Review nginx logs inside container
5. Test API endpoints directly: `curl http://13.201.129.219/api/health`
