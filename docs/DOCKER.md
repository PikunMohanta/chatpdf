# PDFPixie Docker Deployment Guide

This guide covers all Docker deployment options for PDFPixie, from development to production.

## 📋 Quick Start

### Option 1: All-in-One Container (Simplest)
```bash
# Build and run single container
docker build -t pdfpixie .
docker run -p 80:80 -p 8000:8000 --name pdfpixie-app pdfpixie
docker run -d \
  -p 80:80 \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e OPENROUTER_API_KEY=your-api-key \
  --name pdfpixie-app \
  pdfpixie

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
```

### Option 2: Multi-Service Production (Recommended)
```bash
# Copy environment template
cp .env.template .env
# Edit .env with your configuration

# Build and start all services
./docker-deploy.sh full
# or on Windows: .\docker-deploy.ps1 full
```

### Option 3: Development Environment
```bash
# Start development services only (database, cache)
./docker-deploy.sh start dev
# or on Windows: .\docker-deploy.ps1 start dev

# Run frontend and backend manually for hot reload
cd frontend && npm run dev    # Terminal 1
cd backend && uvicorn main:app --reload  # Terminal 2
```

## 🏗️ Architecture Overview

PDFPixie uses a multi-container architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   PostgreSQL    │
│   (Nginx)       │◄──►│   (FastAPI)      │◄──►│   Database      │
│   Port 80       │    │   Port 8000      │    │   Port 5432     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Cache)       │
                       │   Port 6379     │
                       └─────────────────┘
```

## 🐳 Docker Files Explained

### Core Dockerfiles

1. **`docker/Dockerfile.backend`** - Multi-stage FastAPI backend
   - Uses Python 3.11 with UV package manager
   - Security: Non-root user, minimal dependencies
   - Health checks and proper logging

2. **`docker/Dockerfile.frontend`** - Multi-stage React frontend
   - Uses Node.js 20 for building, Nginx for serving
   - Optimized bundle with static asset caching
   - Security headers and gzip compression

3. **`Dockerfile`** - All-in-one container (development/testing)
   - Single container with both frontend and backend
   - Nginx proxy configuration
   - Simpler deployment for small setups

### Docker Compose Files

1. **`docker-compose.yml`** - Production deployment
   - Full PostgreSQL + Redis + Backend + Frontend + Celery
   - Health checks, resource limits, restart policies
   - Environment variable configuration

2. **`docker-compose.dev.yml`** - Development environment
   - Only database and cache services
   - Volume mounting for hot reload
   - Development-friendly ports

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:
```bash
cp .env.template .env
```

Key variables to configure:
```bash
# Required
SECRET_KEY=your-super-secret-key-min-32-chars-long
OPENROUTER_API_KEY=your-openrouter-api-key

# Database
POSTGRES_PASSWORD=your-strong-database-password

# Optional AWS (for S3 storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
```

### Port Configuration

Default ports:
- **Frontend**: 80 (production), 3001 (development)
- **Backend**: 8000 (production), 8001 (development)
- **PostgreSQL**: 5432 (production), 5433 (development)
- **Redis**: 6379 (production), 6380 (development)

## 🚀 Deployment Scripts

### Linux/macOS: `docker-deploy.sh`
```bash
# Make executable
chmod +x docker-deploy.sh

# Commands
./docker-deploy.sh build              # Build images
./docker-deploy.sh start              # Start production
./docker-deploy.sh start dev          # Start development
./docker-deploy.sh logs               # View all logs
./docker-deploy.sh logs prod backend  # View backend logs
./docker-deploy.sh restart            # Restart services
./docker-deploy.sh clean              # Clean up everything
./docker-deploy.sh full               # Build + start
```

### Windows: `docker-deploy.ps1`
```powershell
# Commands (same as bash script)
.\docker-deploy.ps1 build
.\docker-deploy.ps1 start
.\docker-deploy.ps1 start dev
.\docker-deploy.ps1 logs
.\docker-deploy.ps1 restart
.\docker-deploy.ps1 clean
.\docker-deploy.ps1 full
```

## 🔧 Advanced Usage

### Custom Build with Specific Tags
```bash
# Build with custom tags
docker build -f docker/Dockerfile.backend -t pdfpixie-backend:v1.0 ./backend
docker build -f docker/Dockerfile.frontend -t pdfpixie-frontend:v1.0 ./frontend
```

### Production with Custom Configuration
```bash
# Use custom compose file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Scale Services
```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Scale celery workers
docker-compose --profile full up -d --scale celery-worker=2
```

### Resource Limits
Edit `docker-compose.yml` to adjust resource limits:
```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.5'
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :80
   netstat -tulpn | grep :8000
   
   # Change ports in .env
   FRONTEND_PORT=8080
   BACKEND_PORT=8001
   ```

2. **Permission Errors**
   ```bash
   # Fix Docker permissions (Linux)
   sudo usermod -aG docker $USER
   # Log out and back in
   
   # Fix file permissions
   sudo chown -R $USER:$USER ./data
   ```

3. **Database Connection Issues**
   ```bash
   # Check database health
   docker-compose exec postgres pg_isready -U pdfpixie_user
   
   # Reset database
   docker-compose down -v
   docker-compose up postgres -d
   ```

4. **Memory Issues**
   ```bash
   # Check Docker memory usage
   docker stats
   
   # Increase Docker Desktop memory limit
   # Docker Desktop > Settings > Resources > Memory
   ```

5. **Build Failures**
   ```bash
   # Clean Docker build cache
   docker builder prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Health Checks

Check service health:
```bash
# All services
docker-compose ps

# Specific health check
curl http://localhost:8000/health  # Backend
curl http://localhost:80/health    # Frontend

# Container health
docker inspect --format='{{.State.Health.Status}}' pdfpixie-backend
```

### Logs and Debugging

```bash
# View logs
docker-compose logs -f                # All services
docker-compose logs -f backend        # Backend only
docker-compose logs -f --tail=100     # Last 100 lines

# Container shell access
docker-compose exec backend bash      # Backend container
docker-compose exec postgres psql -U pdfpixie_user -d pdfpixie  # Database
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Strong `SECRET_KEY` (32+ characters)
- [ ] Strong database passwords
- [ ] Environment variables not in code
- [ ] Regular security updates
- [ ] Non-root container users
- [ ] Network isolation
- [ ] SSL/TLS termination (reverse proxy)
- [ ] API rate limiting
- [ ] File upload restrictions

### Nginx Security Headers
The frontend container includes security headers:
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `X-Content-Type-Options: nosniff`
- Content Security Policy
- Referrer Policy

## 📊 Monitoring

### Basic Monitoring
```bash
# Resource usage
docker stats

# Service health
docker-compose ps

# Log monitoring
docker-compose logs -f | grep ERROR
```

### Production Monitoring
Consider adding:
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Health check endpoints
- Application metrics

## 🚀 Production Deployment

### Cloud Deployment Options

1. **Docker Compose on VPS**
   ```bash
   # Copy files to server
   scp -r . user@server:/opt/pdfpixie/
   
   # Run on server
   ssh user@server "cd /opt/pdfpixie && ./docker-deploy.sh full"
   ```

2. **Kubernetes Deployment**
   ```bash
   # Generate Kubernetes manifests (future feature)
   kubectl apply -f k8s/
   ```

3. **Cloud Container Services**
   - AWS ECS/Fargate
   - Google Cloud Run
   - Azure Container Instances

### Load Balancing
For high availability, use a reverse proxy:
```nginx
upstream pdfpixie_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream pdfpixie_frontend {
    server frontend1:80;
    server frontend2:80;
}
```

## 📝 Maintenance

### Regular Maintenance Tasks

1. **Update Dependencies**
   ```bash
   # Update base images
   docker-compose pull
   
   # Rebuild with latest dependencies
   docker-compose build --pull
   ```

2. **Database Backups**
   ```bash
   # Backup database
   docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > backup.sql
   
   # Restore database
   docker-compose exec -T postgres psql -U pdfpixie_user pdfpixie < backup.sql
   ```

3. **Clean Up Resources**
   ```bash
   # Clean up old images and containers
   docker system prune -a
   
   # Clean up volumes (careful!)
   docker volume prune
   ```

4. **Log Rotation**
   ```bash
   # Configure log rotation in docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

This completes the comprehensive Docker setup for PDFPixie! 🎉