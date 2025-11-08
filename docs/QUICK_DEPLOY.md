# 🚀 PDFPixie EC2 Deployment Quick Start

This document provides a quick reference for deploying PDFPixie on AWS EC2 with DuckDNS.

For the complete detailed guide, see [EC2_DEPLOYMENT_GUIDE.md](./EC2_DEPLOYMENT_GUIDE.md)

---

## ⚡ Quick Deploy (5 Minutes)

### 1️⃣ Setup DuckDNS (2 min)
```bash
# Go to https://www.duckdns.org/
# Sign in and create subdomain (e.g., mypdfapp)
# Save your token!
```

### 2️⃣ Launch EC2 Instance (2 min)
- **AMI**: Ubuntu 22.04 LTS
- **Type**: t3.small (2GB RAM recommended)
- **Storage**: 20GB
- **Security Group**: Allow ports 22, 80, 443
- **Save your .pem key file!**

### 3️⃣ Connect & Install Docker (1 min)
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Quick install script
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in
exit
```

### 4️⃣ Deploy Application (3 min)
```bash
# Reconnect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Clone repository
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf
git checkout docker-deployment

# Configure environment
cp .env.production .env
nano .env
# Update: OPENROUTER_API_KEY, DOMAIN_NAME, POSTGRES_PASSWORD

# Update DuckDNS
nano update-duckdns.sh
# Set: DUCKDNS_DOMAIN and DUCKDNS_TOKEN
chmod +x update-duckdns.sh
./update-duckdns.sh

# Deploy!
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

### 5️⃣ Access Your App
```
http://your-subdomain.duckdns.org
```

---

## 📋 Essential Environment Variables

Edit `.env` file with these required values:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
DOMAIN_NAME=your-subdomain.duckdns.org
FRONTEND_URL=http://your-subdomain.duckdns.org
POSTGRES_PASSWORD=your_strong_password_here

# Auto-configured (usually don't need to change)
DATABASE_URL=postgresql://pdfpixie_user:your_strong_password_here@postgres:5432/pdfpixie
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=production
```

---

## 🔐 Enable HTTPS (Optional - 5 min)

```bash
# Install certbot
sudo apt-get update && sudo apt-get install -y certbot

# Stop app temporarily
docker-compose down

# Get certificate
sudo certbot certonly --standalone \
    -d your-subdomain.duckdns.org \
    --email your-email@example.com \
    --agree-tos

# Update Dockerfile nginx config
nano Dockerfile
# Change: COPY nginx.conf -> COPY nginx-ssl.conf

# Update domain in SSL config
sed -i 's/your-subdomain.duckdns.org/YOUR_ACTUAL_DOMAIN/g' nginx-ssl.conf

# Update docker-compose.yml to add SSL volumes
nano docker-compose.yml
# Add under app service:
#   ports:
#     - "443:443"
#   volumes:
#     - /etc/letsencrypt:/etc/letsencrypt:ro

# Rebuild and restart
docker-compose build
docker-compose up -d
```

Access at: `https://your-subdomain.duckdns.org`

---

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f app

# Restart
docker-compose restart

# Stop
docker-compose down

# Start
docker-compose up -d

# Rebuild
docker-compose build && docker-compose up -d

# Check health
curl http://localhost/health
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't access site | Check EC2 security group has port 80 open |
| Domain not working | Run `./update-duckdns.sh` and verify with `dig +short your-domain.duckdns.org` |
| Chat not responding | Check `docker-compose logs app` for errors, verify `OPENROUTER_API_KEY` |
| Containers not starting | Run `docker-compose down && docker-compose up -d` |
| PDF not showing | Verify nginx serving worker: `curl -I http://localhost/pdf.worker.min.js` |

---

## 📊 Cost Estimate

| Component | Type | Monthly Cost |
|-----------|------|--------------|
| EC2 t3.small | 2GB RAM, 2 vCPU | ~$15-18 USD |
| EBS Storage | 20GB | ~$2 USD |
| Data Transfer | <1TB | Free (within free tier) |
| **Total** | | **~$17-20 USD/month** |

**Free Tier Option**: t3.micro (1GB RAM) - May be slow but works for testing.

---

## ✅ Post-Deployment Checklist

- [ ] EC2 instance accessible via SSH
- [ ] DuckDNS domain points to EC2 IP
- [ ] `.env` file configured with API key
- [ ] Docker containers running (`docker-compose ps`)
- [ ] App accessible at http://your-domain.duckdns.org
- [ ] PDF upload works
- [ ] Chat generates responses
- [ ] Chat history persists
- [ ] (Optional) HTTPS enabled

---

## 📚 Full Documentation

- **Complete Guide**: [EC2_DEPLOYMENT_GUIDE.md](./EC2_DEPLOYMENT_GUIDE.md)
- **Chat Fix**: [CHAT_HISTORY_FIX.md](../CHAT_HISTORY_FIX.md)
- **PDF Viewer Fix**: [PDF_VIEWER_FIX.md](../PDF_VIEWER_FIX.md)
- **Docker Guide**: [DOCKER.md](./DOCKER.md)

---

## 🆘 Need Help?

- Check full troubleshooting section in [EC2_DEPLOYMENT_GUIDE.md](./EC2_DEPLOYMENT_GUIDE.md)
- View container logs: `docker-compose logs -f`
- GitHub Issues: https://github.com/PikunMohanta/chatpdf/issues

---

**Ready to deploy? Follow the steps above or see the [complete guide](./EC2_DEPLOYMENT_GUIDE.md) for detailed instructions!** 🚀
