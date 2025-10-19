# PDFPixie Docker Quick Start Guide

## 🚀 Build & Run (Simple)

### Build the Image
```bash
# PowerShell (Windows)
$env:DOCKER_BUILDKIT=0
docker build -t pdfpixie:latest .

# Linux/macOS
DOCKER_BUILDKIT=0 docker build -t pdfpixie:latest .
```

### Run the Container
```bash
docker run -d \
  -p 80:80 \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key-change-me \
  -e OPENROUTER_API_KEY=your-api-key-here \
  --name pdfpixie-app \
  pdfpixie:latest
```

### Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Management Commands

```bash
# View logs
docker logs -f pdfpixie-app

# Stop container
docker stop pdfpixie-app

# Start container
docker start pdfpixie-app

# Restart container
docker restart pdfpixie-app

# Remove container
docker stop pdfpixie-app && docker rm pdfpixie-app

# Shell access
docker exec -it pdfpixie-app /bin/bash
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different ports
docker run -d -p 8080:80 -p 8001:8000 \
  -e SECRET_KEY=your-key \
  -e OPENROUTER_API_KEY=your-api-key \
  --name pdfpixie-app \
  pdfpixie:latest
```

### Build Cache Issues
```bash
# Clean Docker cache
docker builder prune -af

# Build without cache
DOCKER_BUILDKIT=0 docker build --no-cache -t pdfpixie:latest .
```

### Check Container Health
```bash
# Check if container is running
docker ps | grep pdfpixie

# Check logs for errors
docker logs pdfpixie-app | grep ERROR

# Test backend health
curl http://localhost:8000/health
```

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Application secret key (min 32 chars) |
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key for AI features |
| `ENVIRONMENT` | No | production | Application environment |
| `DEBUG` | No | false | Enable debug mode |

## 💡 Tips

- **Build time**: First build ~5-10 minutes, subsequent builds ~2-3 minutes
- **Image size**: ~800MB (includes Python, Node.js compiled frontend, Nginx)
- **Memory usage**: ~300-500MB RAM at idle
- **Why DOCKER_BUILDKIT=0**: Avoids BuildKit cache corruption issues

## 🎯 Quick Reference

```bash
# Complete workflow
$env:DOCKER_BUILDKIT=0
docker build -t pdfpixie:latest .
docker run -d -p 80:80 -p 8000:8000 --env-file .env --name pdfpixie-app pdfpixie:latest
docker logs -f pdfpixie-app
```

That's it! 🎉