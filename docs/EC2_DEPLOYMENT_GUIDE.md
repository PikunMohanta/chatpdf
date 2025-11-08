# PDFPixie EC2 Deployment Guide with DuckDNS

Complete step-by-step guide to deploy PDFPixie on AWS EC2 with a free DuckDNS domain.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [DuckDNS Setup](#duckdns-setup)
3. [EC2 Instance Setup](#ec2-instance-setup)
4. [Application Deployment](#application-deployment)
5. [Domain Configuration](#domain-configuration)
6. [SSL/HTTPS Setup (Optional)](#ssl-setup)
7. [Monitoring & Maintenance](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ AWS Account with EC2 access
- ✅ DuckDNS Account (free at https://www.duckdns.org/)
- ✅ OpenRouter API Key (from https://openrouter.ai/)

### Local Requirements
- Git installed on your local machine
- SSH client (comes with Windows 10+, macOS, Linux)
- Basic command line knowledge

---

## 🦆 DuckDNS Setup

DuckDNS provides free subdomain names that automatically update to your EC2 instance's IP address.

### Step 1: Create DuckDNS Account

1. Go to https://www.duckdns.org/
2. Sign in with Google, GitHub, or other providers
3. You'll get a unique **token** - save this securely!

### Step 2: Create Your Subdomain

1. In the DuckDNS dashboard, enter your desired subdomain
   - Example: `mypdfapp` (will become `mypdfapp.duckdns.org`)
2. Click **Add Domain**
3. Note your subdomain and token:
   ```
   Domain: mypdfapp.duckdns.org
   Token: 12345678-1234-1234-1234-123456789abc
   ```

### Step 3: Test DuckDNS (After EC2 Setup)

After creating your EC2 instance, you'll update the IP manually or use the auto-update script.

---

## 🖥️ EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**: https://console.aws.amazon.com/ec2/

2. **Click "Launch Instance"**

3. **Configure Instance**:
   
   | Setting | Value | Notes |
   |---------|-------|-------|
   | **Name** | PDFPixie-Server | Or your preferred name |
   | **AMI** | Ubuntu Server 22.04 LTS | 64-bit (x86) |
   | **Instance Type** | t3.small | 2 vCPU, 2GB RAM (recommended) |
   | | t3.micro | 2 vCPU, 1GB RAM (budget option, may be slow) |
   | **Key Pair** | Create new or use existing | Download `.pem` file securely |
   | **Storage** | 20 GB gp3 | Minimum recommended |

4. **Network Settings**:
   - ✅ Auto-assign Public IP: **Enabled**
   - Create new security group with these rules:

   | Type | Protocol | Port | Source | Description |
   |------|----------|------|--------|-------------|
   | SSH | TCP | 22 | My IP | SSH access (your current IP) |
   | HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic |
   | HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web (optional) |

5. **Review and Launch**

6. **Note Your Instance Details**:
   - Public IPv4 Address: `54.123.45.67` (example)
   - Public DNS: `ec2-54-123-45-67.compute-1.amazonaws.com`

### Step 2: Connect to Your EC2 Instance

**Windows (PowerShell or CMD):**
```bash
# Navigate to folder with your .pem key file
cd C:\Users\YourName\Downloads

# Set correct permissions (if needed)
icacls "your-key.pem" /inheritance:r /grant:r "%username%:R"

# Connect via SSH
ssh -i "your-key.pem" ubuntu@54.123.45.67
```

**macOS/Linux:**
```bash
# Set correct permissions
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@54.123.45.67
```

Replace `54.123.45.67` with your actual EC2 public IP.

### Step 3: Update System and Install Dependencies

Once connected to EC2, run these commands:

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get install -y git

# Verify installations
docker --version
docker-compose --version
git --version

# Log out and back in for docker group to take effect
exit
```

**Reconnect to EC2** (same SSH command as before)

---

## 🚀 Application Deployment

### Step 1: Clone Repository

```bash
# Clone your repository
cd ~
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf

# Checkout the docker-deployment branch
git checkout docker-deployment
```

### Step 2: Configure Environment Variables

```bash
# Copy production environment template
cp .env.production .env

# Edit environment file
nano .env
```

**Update these values in `.env`:**

```bash
# API Keys
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE

# Domain (replace with your DuckDNS domain)
DOMAIN_NAME=mypdfapp.duckdns.org
FRONTEND_URL=http://mypdfapp.duckdns.org

# Database Password (IMPORTANT: Change to a strong password!)
POSTGRES_PASSWORD=your_super_secure_password_here_123!

# Update DATABASE_URL with the same password
DATABASE_URL=postgresql://pdfpixie_user:your_super_secure_password_here_123!@postgres:5432/pdfpixie
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Update DuckDNS Script

```bash
# Edit the DuckDNS update script
nano update-duckdns.sh
```

Update these lines:
```bash
DUCKDNS_DOMAIN="mypdfapp"  # Your subdomain (without .duckdns.org)
DUCKDNS_TOKEN="your-duckdns-token"  # From DuckDNS dashboard
```

**Save and exit**, then make it executable:
```bash
chmod +x update-duckdns.sh
```

### Step 4: Update DuckDNS with EC2 IP

```bash
# Run the update script
./update-duckdns.sh
```

You should see:
```
✅ DuckDNS updated successfully!
Your domain: mypdfapp.duckdns.org
```

**Verify DNS propagation** (may take 1-2 minutes):
```bash
# Check if domain points to your EC2 IP
dig +short mypdfapp.duckdns.org

# Or using nslookup
nslookup mypdfapp.duckdns.org
```

### Step 5: Build and Start Application

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check container status
docker-compose ps
```

**Expected output:**
```
NAME                   STATUS              PORTS
chatpdf-app-1          Up (healthy)        0.0.0.0:80->80/tcp
chatpdf-postgres-1     Up (healthy)        5432/tcp
chatpdf-redis-1        Up (healthy)        6379/tcp
```

### Step 6: Verify Application

```bash
# Check backend health
curl http://localhost/health

# Should return: {"status":"healthy"}

# View logs
docker-compose logs -f app

# Press Ctrl+C to exit logs
```

---

## 🌐 Domain Configuration

### Auto-Update DuckDNS IP (Recommended)

Set up a cron job to automatically update DuckDNS every 5 minutes (in case EC2 IP changes):

```bash
# Open crontab editor
crontab -e

# Choose editor (nano is easiest for beginners)
# Add this line at the end:
*/5 * * * * /home/ubuntu/chatpdf/update-duckdns.sh >> /home/ubuntu/duckdns.log 2>&1

# Save and exit (Ctrl+X, Y, Enter)
```

### Test Your Domain

1. **Open browser** and navigate to:
   ```
   http://mypdfapp.duckdns.org
   ```

2. **You should see the PDFPixie upload screen!**

3. **Test the application**:
   - Upload a PDF file
   - Ask questions in the chat
   - Verify responses are generated
   - Check chat history persists

---

## 🔐 SSL/HTTPS Setup (Optional but Recommended)

Enable HTTPS for secure connections using free Let's Encrypt certificates.

### Prerequisites
- Your DuckDNS domain is working (HTTP)
- Port 443 is open in EC2 Security Group

### Step 1: Stop Application

```bash
cd ~/chatpdf
docker-compose down
```

### Step 2: Install Certbot

```bash
sudo apt-get update
sudo apt-get install -y certbot
```

### Step 3: Obtain SSL Certificate

```bash
# Replace with your actual domain
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d mypdfapp.duckdns.org
```

**Certificate will be saved to:**
```
/etc/letsencrypt/live/mypdfapp.duckdns.org/fullchain.pem
/etc/letsencrypt/live/mypdfapp.duckdns.org/privkey.pem
```

### Step 4: Update Nginx Configuration

```bash
cd ~/chatpdf

# Update nginx-ssl.conf with your domain
sed -i 's/your-subdomain.duckdns.org/mypdfapp.duckdns.org/g' nginx-ssl.conf

# Update Dockerfile to use SSL config
nano Dockerfile
```

**Find this line:**
```dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Replace with:**
```dockerfile
COPY nginx-ssl.conf /etc/nginx/conf.d/default.conf
```

**Save and exit**

### Step 5: Update Docker Compose for SSL

```bash
nano docker-compose.yml
```

**Find the `app` service and update ports and volumes:**

```yaml
  app:
    build: .
    container_name: pdfpixie-app
    ports:
      - "80:80"
      - "443:443"  # Add HTTPS port
    volumes:
      - ./backend/data:/app/data
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Add SSL certificates
```

**Save and exit**

### Step 6: Rebuild and Restart

```bash
# Rebuild with SSL configuration
docker-compose build

# Start with HTTPS enabled
docker-compose up -d

# Check logs
docker-compose logs -f app
```

### Step 7: Test HTTPS

Open browser and navigate to:
```
https://mypdfapp.duckdns.org
```

You should see a secure connection (lock icon in browser)!

### Step 8: Auto-Renew Certificates

SSL certificates expire after 90 days. Set up auto-renewal:

```bash
# Open crontab
crontab -e

# Add this line to renew certificates monthly
0 0 1 * * certbot renew --quiet && docker-compose restart app
```

---

## 📊 Monitoring & Maintenance

### Check Application Status

```bash
# Check if containers are running
docker-compose ps

# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Check System Resources

```bash
# Disk usage
df -h

# Memory usage
free -h

# Docker disk usage
docker system df

# Container resource usage
docker stats
```

### Backup Database

```bash
# Create backup directory
mkdir -p ~/backups

# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > ~/backups/pdfpixie-$(date +%Y%m%d).sql

# Backup uploaded files and chat history
tar -czf ~/backups/data-$(date +%Y%m%d).tar.gz ~/chatpdf/backend/data/
```

### Update Application

```bash
cd ~/chatpdf

# Pull latest changes
git pull origin docker-deployment

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Clean Up Old Docker Resources

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (CAUTION: May delete data!)
docker volume prune

# Full system cleanup
docker system prune -a
```

---

## 🔧 Troubleshooting

### Application Not Accessible

**Check if containers are running:**
```bash
docker-compose ps
```

**Check if port 80 is accessible:**
```bash
curl http://localhost/health
```

**Check EC2 Security Group:**
- Ensure port 80 (HTTP) is open to `0.0.0.0/0`
- Ensure port 443 (HTTPS) is open if using SSL

**Check DuckDNS domain:**
```bash
dig +short mypdfapp.duckdns.org
# Should return your EC2 public IP
```

### Chat Not Responding

**Check backend logs:**
```bash
docker-compose logs -f app | grep -i error
```

**Verify OpenRouter API key:**
```bash
# Check environment variable
docker-compose exec app env | grep OPENROUTER
```

**Test API directly:**
```bash
docker-compose exec app curl http://localhost:8000/health
```

### PDF Not Showing

**Check worker file:**
```bash
curl -I http://mypdfapp.duckdns.org/pdf.worker.min.js
# Should return: HTTP/1.1 200 OK
```

**Check browser console** (F12 in browser):
- Look for 404 errors related to pdf.worker.min.js
- Check for CORS errors

### Database Connection Issues

**Check PostgreSQL:**
```bash
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie -c "SELECT 1;"
```

**Check database logs:**
```bash
docker-compose logs -f postgres
```

### Out of Memory

**If using t3.micro (1GB RAM):**
```bash
# Check memory usage
free -h

# Restart containers to free memory
docker-compose restart
```

**Consider upgrading to t3.small (2GB RAM)** for better performance.

### Container Restart Loop

**Check container logs:**
```bash
docker-compose logs --tail=100 app
```

**Common causes:**
- Missing environment variables
- Port conflicts
- Database connection failures

**Fix:**
```bash
# Stop all containers
docker-compose down

# Remove orphaned containers
docker-compose down --remove-orphans

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### SSL Certificate Issues

**Check certificate expiry:**
```bash
sudo certbot certificates
```

**Manually renew:**
```bash
docker-compose down
sudo certbot renew
docker-compose up -d
```

---

## 🎯 Quick Reference Commands

### Daily Operations

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Restart application
docker-compose restart app

# Stop application
docker-compose down

# Start application
docker-compose up -d
```

### Emergency Fixes

```bash
# Full restart
docker-compose down && docker-compose up -d

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check what's using port 80
sudo lsof -i :80

# Kill process on port 80
sudo kill -9 $(sudo lsof -t -i:80)
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Application** | http://your-domain.duckdns.org | Main web interface |
| **Health Check** | http://your-domain.duckdns.org/health | Backend status |
| **Nginx Health** | http://your-domain.duckdns.org/nginx-health | Nginx status |
| **SSH** | ssh -i your-key.pem ubuntu@your-ip | Server access |

---

## 📞 Support Resources

- **Project GitHub**: https://github.com/PikunMohanta/chatpdf
- **DuckDNS Help**: https://www.duckdns.org/spec.jsp
- **Docker Docs**: https://docs.docker.com/
- **AWS EC2 Docs**: https://docs.aws.amazon.com/ec2/

---

## ✅ Post-Deployment Checklist

- [ ] EC2 instance running and accessible via SSH
- [ ] Security Group allows ports 80 and 443
- [ ] DuckDNS domain points to EC2 public IP
- [ ] Environment variables configured in `.env`
- [ ] Docker containers running (`docker-compose ps` shows "Up")
- [ ] Application accessible at http://your-domain.duckdns.org
- [ ] PDF upload works
- [ ] Chat generates responses
- [ ] Chat history persists across sessions
- [ ] DuckDNS auto-update cron job configured
- [ ] (Optional) SSL certificate obtained and HTTPS working
- [ ] (Optional) Certificate auto-renewal configured
- [ ] Database backup strategy in place

---

## 🎉 Success!

Your PDFPixie application is now deployed on EC2 with a DuckDNS domain!

**Share your app**: `http://your-subdomain.duckdns.org`

**Next Steps**:
1. Monitor application logs for first 24 hours
2. Test with different PDF files
3. Consider enabling HTTPS for production use
4. Set up regular database backups
5. Monitor AWS billing (t3.small costs ~$15-20/month)

Happy chatting with your PDFs! 🚀📄
