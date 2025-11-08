# 🚀 PDFPixie EC2 Deployment - Quick Reference Card

**Print this out or keep it handy during deployment!**

---

## 📋 Pre-Deployment Info to Gather

| Item | Your Value | Where to Get It |
|------|------------|----------------|
| **AWS EC2 IP** | ______________ | AWS Console after launch |
| **SSH Key File** | ______________ | Downloaded from AWS |
| **DuckDNS Subdomain** | ______________.duckdns.org | https://duckdns.org |
| **DuckDNS Token** | ______________ | https://duckdns.org dashboard |
| **OpenRouter API Key** | sk-or-v1-______________ | https://openrouter.ai/keys |

---

## ⚡ Essential Commands (Copy & Paste)

### 1️⃣ SSH to EC2
```bash
ssh -i YOUR_KEY.pem ubuntu@YOUR_EC2_IP
```

### 2️⃣ Install Docker (One-Time)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
exit
# Reconnect: ssh -i YOUR_KEY.pem ubuntu@YOUR_EC2_IP
```

### 3️⃣ Deploy Application
```bash
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf
git checkout docker-deployment
cp .env.production .env
nano .env  # Update: API_KEY, DOMAIN, PASSWORD
nano update-duckdns.sh  # Set DOMAIN and TOKEN
chmod +x update-duckdns.sh
./update-duckdns.sh
docker-compose build
docker-compose up -d
chmod +x verify-deployment.sh
./verify-deployment.sh
```

### 4️⃣ Access Your App
```
http://YOUR_SUBDOMAIN.duckdns.org
```

---

## 🔧 Daily Operations

| Task | Command |
|------|---------|
| **View Logs** | `docker-compose logs -f app` |
| **Check Status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Stop** | `docker-compose down` |
| **Start** | `docker-compose up -d` |
| **Health Check** | `curl http://localhost/health` |
| **Update App** | `git pull && docker-compose build && docker-compose up -d` |

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| **Can't access site** | 1. Check EC2 running<br>2. `docker-compose ps`<br>3. Security group port 80 open |
| **Domain not working** | `./update-duckdns.sh`<br>`dig +short YOUR_DOMAIN.duckdns.org` |
| **Chat not responding** | `docker-compose logs app \| grep error`<br>Check OPENROUTER_API_KEY in .env |
| **PDF not showing** | `curl -I http://localhost/pdf.worker.min.js`<br>Should return 200 OK |
| **Containers stopped** | `docker-compose down && docker-compose up -d` |

---

## 📊 Health Check Checklist

Run these to verify everything works:

```bash
# ✅ Check containers running
docker-compose ps
# Should show 3 containers: app, postgres, redis (all "Up")

# ✅ Test backend
curl http://localhost/health
# Should return: {"status":"healthy"}

# ✅ Test PDF worker
curl -I http://localhost/pdf.worker.min.js
# Should return: HTTP/1.1 200 OK

# ✅ Check DNS
dig +short YOUR_DOMAIN.duckdns.org
# Should return your EC2 IP

# ✅ View recent logs
docker-compose logs --tail=50 app
# Should have no ERROR messages
```

---

## 🔒 Security Checklist

- [ ] Changed POSTGRES_PASSWORD in .env
- [ ] Security Group: Port 22 restricted to your IP only
- [ ] Security Group: Ports 80/443 open to public (0.0.0.0/0)
- [ ] SSH key file permissions: `chmod 400 YOUR_KEY.pem`
- [ ] .env file not committed to Git
- [ ] OpenRouter API key kept secret

---

## 💰 Cost Tracking

| Item | Cost/Month |
|------|------------|
| t3.small EC2 | ~$15-18 |
| 20GB Storage | ~$2 |
| DuckDNS | $0 |
| SSL Cert | $0 |
| **Total** | **~$17-20** |

---

## 📞 Emergency Contacts

| Service | URL |
|---------|-----|
| **AWS Console** | https://console.aws.amazon.com/ec2 |
| **DuckDNS** | https://www.duckdns.org |
| **OpenRouter** | https://openrouter.ai |
| **GitHub Repo** | https://github.com/PikunMohanta/chatpdf |

---

## 📚 Full Docs

- **Complete Guide**: `docs/EC2_DEPLOYMENT_GUIDE.md` (718 lines)
- **Quick Deploy**: `docs/QUICK_DEPLOY.md` (214 lines)
- **Checklist**: `docs/DEPLOYMENT_CHECKLIST.md` (304 lines)
- **Summary**: `PRODUCTION_DEPLOYMENT_SUMMARY.md` (547 lines)

---

## 🎯 Success Indicators

Your deployment is working when:
- ✅ Can access http://YOUR_DOMAIN.duckdns.org
- ✅ Upload PDF completes successfully
- ✅ Chat responds to questions
- ✅ History saves after page refresh
- ✅ No errors in logs

---

**Need help?** Run: `./verify-deployment.sh` for automated diagnostics

**Print this page and keep it with your SSH key file!**
