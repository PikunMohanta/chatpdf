# 📋 EC2 Deployment Checklist

Use this checklist to ensure successful deployment of PDFPixie on AWS EC2 with DuckDNS.

---

## Pre-Deployment

### Account Setup
- [ ] AWS account created and verified
- [ ] DuckDNS account created at https://www.duckdns.org/
- [ ] DuckDNS subdomain created (e.g., `mypdfapp.duckdns.org`)
- [ ] DuckDNS token saved securely
- [ ] OpenRouter API key obtained from https://openrouter.ai/

### Local Prerequisites
- [ ] Git installed and configured
- [ ] SSH client available (Windows 10+, macOS, Linux)
- [ ] EC2 key pair (.pem file) downloaded and saved securely

---

## EC2 Instance Setup

### Launch Instance
- [ ] EC2 instance launched (t3.small recommended, t3.micro budget)
- [ ] Ubuntu 22.04 LTS selected as AMI
- [ ] Instance type selected (2GB+ RAM recommended)
- [ ] 20GB+ gp3 storage configured
- [ ] Security Group configured with rules:
  - [ ] Port 22 (SSH) - Your IP only
  - [ ] Port 80 (HTTP) - 0.0.0.0/0
  - [ ] Port 443 (HTTPS) - 0.0.0.0/0 (optional for SSL)
- [ ] Auto-assign Public IP enabled
- [ ] Key pair selected/created
- [ ] Instance launched successfully

### Instance Information Recorded
- [ ] Instance ID: ________________
- [ ] Public IPv4 Address: ________________
- [ ] Public IPv4 DNS: ________________
- [ ] Security Group ID: ________________

### Initial Connection
- [ ] SSH key file permissions set correctly (chmod 400 on Unix)
- [ ] Successfully connected via SSH
- [ ] Can execute commands as ubuntu user

---

## System Configuration

### Docker Installation
- [ ] System packages updated (`sudo apt-get update && upgrade`)
- [ ] Docker installed (`curl -fsSL https://get.docker.com | sh`)
- [ ] User added to docker group (`sudo usermod -aG docker ubuntu`)
- [ ] Docker Compose installed
- [ ] Git installed (`sudo apt-get install git`)
- [ ] Logged out and back in (for docker group to take effect)
- [ ] Docker version verified (`docker --version`)
- [ ] Docker Compose version verified (`docker-compose --version`)

---

## Application Deployment

### Repository Setup
- [ ] Repository cloned (`git clone https://github.com/PikunMohanta/chatpdf.git`)
- [ ] Changed to chatpdf directory
- [ ] Checked out docker-deployment branch
- [ ] All files present and readable

### Environment Configuration
- [ ] `.env.production` copied to `.env`
- [ ] `.env` file edited with correct values:
  - [ ] `OPENROUTER_API_KEY` set to actual API key
  - [ ] `DOMAIN_NAME` set to DuckDNS domain
  - [ ] `FRONTEND_URL` set to http://your-domain.duckdns.org
  - [ ] `POSTGRES_PASSWORD` changed from default
  - [ ] `DATABASE_URL` updated with new password
- [ ] `.env` file saved and verified

### DuckDNS Configuration
- [ ] `update-duckdns.sh` edited with:
  - [ ] `DUCKDNS_DOMAIN` set (subdomain only, without .duckdns.org)
  - [ ] `DUCKDNS_TOKEN` set to actual token
- [ ] Script made executable (`chmod +x update-duckdns.sh`)
- [ ] Script executed successfully (`./update-duckdns.sh`)
- [ ] DuckDNS update confirmed (should see "✅ DuckDNS updated successfully!")
- [ ] DNS resolution verified (`dig +short your-domain.duckdns.org`)
- [ ] Domain points to correct EC2 IP

### Auto-Update Cron Job
- [ ] Crontab edited (`crontab -e`)
- [ ] DuckDNS auto-update line added:
  ```
  */5 * * * * /home/ubuntu/chatpdf/update-duckdns.sh >> /home/ubuntu/duckdns.log 2>&1
  ```
- [ ] Crontab saved successfully

---

## Docker Deployment

### Build and Start
- [ ] Docker images built (`docker-compose build`)
- [ ] No build errors occurred
- [ ] Containers started (`docker-compose up -d`)
- [ ] All 3 containers running:
  - [ ] pdfpixie-app (app)
  - [ ] pdfpixie-postgres (postgres)
  - [ ] pdfpixie-redis (redis)
- [ ] Container status checked (`docker-compose ps`)
- [ ] All containers show "Up (healthy)" status

### Verification Script
- [ ] Verification script made executable (`chmod +x verify-deployment.sh`)
- [ ] Verification script executed (`./verify-deployment.sh`)
- [ ] All checks passed (✅)

---

## Application Testing

### Backend Verification
- [ ] Health endpoint responds (`curl http://localhost/health`)
- [ ] Returns: `{"status":"healthy"}`
- [ ] PDF worker file accessible (`curl -I http://localhost/pdf.worker.min.js`)
- [ ] Returns: `200 OK`
- [ ] No errors in application logs (`docker-compose logs app`)

### Frontend Verification
- [ ] Can access http://your-domain.duckdns.org in browser
- [ ] PDFPixie upload screen loads
- [ ] No console errors in browser (F12 Developer Tools)
- [ ] UI renders correctly

### Functional Testing
- [ ] PDF upload works (drag-and-drop or click upload)
- [ ] PDF file processes successfully
- [ ] PDF viewer displays document
- [ ] Chat input accepts text
- [ ] Can send chat message
- [ ] AI generates response (within 5-10 seconds)
- [ ] Response displays in chat panel
- [ ] Page refresh preserves session
- [ ] Chat history loads in sidebar
- [ ] Can switch between sessions
- [ ] Previous messages load correctly

---

## SSL/HTTPS Setup (Optional but Recommended)

### Certificate Acquisition
- [ ] Certbot installed (`sudo apt-get install certbot`)
- [ ] Containers stopped (`docker-compose down`)
- [ ] SSL certificate obtained via Let's Encrypt
- [ ] Certificate files created in `/etc/letsencrypt/live/your-domain/`
- [ ] `fullchain.pem` exists
- [ ] `privkey.pem` exists

### SSL Configuration
- [ ] `nginx-ssl.conf` updated with actual domain name
- [ ] Dockerfile updated to use `nginx-ssl.conf`
- [ ] `docker-compose.yml` updated with:
  - [ ] Port 443 exposed
  - [ ] SSL certificate volumes mounted
- [ ] Containers rebuilt (`docker-compose build`)
- [ ] Containers restarted (`docker-compose up -d`)

### HTTPS Verification
- [ ] Can access https://your-domain.duckdns.org
- [ ] Browser shows secure connection (lock icon)
- [ ] No certificate warnings
- [ ] HTTP redirects to HTTPS
- [ ] All application features work over HTTPS

### Certificate Auto-Renewal
- [ ] Crontab edited for cert renewal
- [ ] Renewal cron job added:
  ```
  0 0 1 * * certbot renew --quiet && docker-compose restart app
  ```

---

## Monitoring & Maintenance

### Log Monitoring
- [ ] Know how to view logs (`docker-compose logs -f`)
- [ ] Checked recent logs for errors
- [ ] No critical errors present

### Resource Monitoring
- [ ] Disk space checked (`df -h`) - should be <80% used
- [ ] Memory usage checked (`free -h`)
- [ ] Docker container resources checked (`docker stats`)

### Backup Strategy
- [ ] Backup directory created (`mkdir ~/backups`)
- [ ] Database backup tested:
  ```bash
  docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > ~/backups/backup.sql
  ```
- [ ] Data directory backup tested:
  ```bash
  tar -czf ~/backups/data-backup.tar.gz ~/chatpdf/backend/data/
  ```
- [ ] Backup schedule planned (daily/weekly)

---

## Security Hardening

### Basic Security
- [ ] Strong PostgreSQL password set (not default)
- [ ] SSH password authentication disabled (key-only)
- [ ] Security Group rules restrictive (SSH only from your IP)
- [ ] Firewall configured if needed (`ufw`)
- [ ] `.env` file permissions set (`chmod 600 .env`)
- [ ] No sensitive data in Git repository

### Optional Enhancements
- [ ] Fail2Ban installed for SSH protection
- [ ] Automatic security updates enabled
- [ ] CloudWatch monitoring enabled
- [ ] Backup automation configured

---

## Documentation

### Information Recorded
- [ ] EC2 instance details saved
- [ ] DuckDNS domain and token saved securely
- [ ] Database password saved securely
- [ ] OpenRouter API key saved securely
- [ ] SSH key file backed up securely
- [ ] Deployment date recorded: ________________

### Access Information
- [ ] Application URL: http(s)://________________
- [ ] SSH command documented: `ssh -i ________.pem ubuntu@________`
- [ ] Deployment guide location known

---

## Post-Deployment

### Monitoring Plan
- [ ] Set up daily health checks
- [ ] Configure alerting for downtime
- [ ] Schedule weekly log reviews
- [ ] Plan monthly security updates

### Performance Baseline
- [ ] PDF upload time recorded: ________ seconds
- [ ] Chat response time recorded: ________ seconds
- [ ] Initial container memory usage: ________ MB
- [ ] Initial disk usage: ________ GB

---

## Troubleshooting Reference

### If Application Not Accessible
1. Check EC2 instance running
2. Verify Security Group port 80 open
3. Confirm containers running (`docker-compose ps`)
4. Check DuckDNS domain resolves (`dig +short domain`)
5. Review logs (`docker-compose logs -f`)

### If Chat Not Responding
1. Check OpenRouter API key in `.env`
2. Verify backend logs for errors
3. Test health endpoint
4. Check WebSocket connection in browser console

### If PDF Not Showing
1. Verify worker file: `curl -I http://localhost/pdf.worker.min.js`
2. Check browser console for 404 errors
3. Review Nginx configuration
4. Rebuild Docker image if needed

---

## ✅ Deployment Complete!

**Date Deployed**: ________________
**Deployed By**: ________________
**Version**: docker-deployment branch
**Domain**: http(s)://________________

### Next Steps
- [ ] Share URL with team/users
- [ ] Monitor logs for first 24 hours
- [ ] Test with various PDF files
- [ ] Set up regular backups
- [ ] Plan for scaling if needed

---

**For detailed troubleshooting, see [EC2_DEPLOYMENT_GUIDE.md](./EC2_DEPLOYMENT_GUIDE.md)**
