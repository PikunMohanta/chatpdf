# PDFPixie - AI-Powered PDF Chat Application 🤖📄

Your intelligent PDF companion. Upload PDFs, ask questions, and get AI-powered responses based on document content using advanced semantic search and real-time chat.

## ✨ Features

- 📄 **PDF Upload & Processing** - Drag-and-drop interface with instant text extraction
- 🤖 **AI-Powered Chat** - Interactive conversations with your PDF documents powered by OpenRouter
- 🔍 **Semantic Search** - ChromaDB vector embeddings for accurate context retrieval
- ⚡ **Real-time Communication** - WebSocket (Socket.IO) chat with typing indicators
- 💾 **Chat History** - Persistent conversation storage with SQLite database
- 🎨 **Modern UI** - Beautiful interface with glassmorphism effects and Zen Serif font
- � **Docker Ready** - Optimized Docker image (859MB) with single-command deployment
- ☁️ **AWS EC2 Compatible** - Complete deployment guide included

## 🛠️ Tech Stack

**Frontend:**
- React 18 + TypeScript
- Socket.IO Client (real-time communication)
- React-PDF (document preview)
- Vite (build tool)
- CSS3 with custom design system

**Backend:**
- FastAPI (async Python web framework)
- Socket.IO Server (WebSocket communication)
- LangChain (AI orchestration)
- ChromaDB (vector embeddings)
- PyMuPDF (PDF text extraction)
- OpenRouter API (AI responses)
- SQLite (chat history storage)

**Development:**
- UV Package Manager (faster than pip)
- Docker & Docker Compose (containerization)
- Python 3.10+
- Node.js 18+

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.10+** - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf
```

2. **Backend Setup**

```bash
cd backend

# Install UV package manager (optional but recommended - 10-100x faster)
# Windows PowerShell:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Unix/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
python -m venv .venv
# Or with UV:
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Or with UV (much faster):
uv pip install -r requirements.txt
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

### Running the Application

You need **two terminals** - one for backend, one for frontend:

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Unix/macOS

# IMPORTANT: Must use 'socket_app' for chat to work!
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Access the Application

- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## 📖 How to Use

1. **Upload a PDF**
   - Click "Upload PDF" or drag-and-drop a PDF file
   - Wait for processing to complete (text extraction + embeddings)

2. **Start Chatting**
   - Type your question in the chat input
   - Press Enter or click Send
   - AI will analyze the document and respond with relevant information

3. **View Chat History**
   - Previous conversations are automatically saved
   - Switch between different PDF sessions from the sidebar

4. **Search Modes**
   - Automatic semantic search finds relevant document sections
   - Context-aware AI responses based on document content

## 📁 Project Structure

```
chatpdf/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── index.html           # HTML template (includes Zen Serif font)
│   └── package.json
│
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── auth.py          # Authentication logic
│   │   ├── pdf_processing.py # PDF parsing & embeddings
│   │   ├── chat.py          # Chat & AI response generation
│   │   ├── chat_history_db.py # Chat history management
│   │   └── openrouter_client.py # AI client
│   ├── data/
│   │   ├── uploads/         # Uploaded PDFs
│   │   ├── chromadb/        # Vector embeddings
│   │   └── chat_history/    # SQLite chat database
│   ├── main.py              # FastAPI app + Socket.IO
│   └── requirements.txt
│
├── docker/                  # Docker configurations
├── scripts/                 # Setup scripts
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables (Optional)

Create `.env` file in `backend/` directory:

```env
# AI Configuration (optional - uses defaults if not set)
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Storage paths (auto-created)
UPLOAD_DIR=./data/uploads
CHROMA_DIR=./data/chromadb
CHAT_HISTORY_DIR=./data/chat_history
```

Create `.env.local` file in `frontend/` directory for custom overrides:

```env
# Development options
VITE_ENABLE_TEST_DOCUMENT=false  # Set to 'true' to auto-load sample PDFs (development only)
VITE_ENABLE_DEBUG=true           # Enable console debugging
```

The application works in **development mode** without any API keys:
- ✅ Local file storage for PDFs
- ✅ ChromaDB for local embeddings
- ✅ SQLite for chat history
- ✅ Mock authentication for development

## 🧪 Development

### Key Commands

```bash
# Backend
cd backend
uvicorn main:socket_app --reload    # Start with hot reload
pytest tests/                       # Run tests (if available)

# Frontend
cd frontend
npm run dev                         # Start dev server
npm run build                       # Build for production
npm run preview                     # Preview production build
```

### Important Notes

- ⚠️ **Must use `main:socket_app`** - Using `main:app` will break Socket.IO chat!
- 💡 Frontend runs on port 3000 (not 3001)
- 🔄 Backend uses async Socket.IO for real-time communication
- 💾 Chat history automatically persists to SQLite database
- 🧹 **Clear localStorage**: If you see old test documents, open browser console and run `clearPDFPixieData()` to reset

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker

**Prerequisites:**
- Docker Desktop installed
- OpenRouter API key ([Get one here](https://openrouter.ai/))

**1. Build the Docker image:**
```bash
docker build -t pdfpixie:latest .
```

**2. Run the container:**
```bash
docker run -d \
  --name pdfpixie-app \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -p 80:80 \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_api_key_here \
  pdfpixie:latest
```

**3. Access the application:**
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**4. Check logs:**
```bash
docker logs -f pdfpixie-app
```

**5. Stop the container:**
```bash
docker stop pdfpixie-app
docker rm pdfpixie-app
```

### Docker Image Details
- **Size**: 859MB (optimized from 1.12GB)
- **Base**: Python 3.11-slim + nginx-light
- **Includes**: Frontend (React) + Backend (FastAPI) + Nginx + Supervisor
- **Features**: WebSocket support, DNS resolution, health checks

---

## ☁️ AWS EC2 Deployment

### Complete EC2 Deployment Guide

For detailed step-by-step instructions, see: **[EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md](./EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md)**

### Quick EC2 Setup

**1. Launch EC2 Instance:**
- Instance Type: t3.micro (free tier) or t3.small (recommended)
- AMI: Ubuntu 24.04 LTS
- Security Groups: Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Storage: 30GB EBS volume

**2. SSH to EC2 and install Docker:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker
```

**3. Clone and deploy:**
```bash
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf

# Build image
docker build -t pdfpixie:latest .

# Run container
docker run -d \
  --name pdfpixie-app \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -p 80:80 \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_api_key_here \
  pdfpixie:latest
```

**4. Access via EC2 public IP:**
```
http://your-ec2-ip
```

### Cost Estimate
- **Free Tier (12 months)**: $0/month
- **After Free Tier**: ~$20-30/month (t3.small + 30GB storage)

### SSL Certificate (Optional)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (requires domain)
sudo certbot --nginx -d yourdomain.com
```

---

## 💻 Local Development

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git

### Setup Instructions

**1. Clone repository:**
```bash
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf
```

**2. Backend setup:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Unix/macOS

pip install -r requirements.txt
```

**3. Frontend setup:**
```bash
cd frontend
npm install
```

**4. Run the application:**

Terminal 1 (Backend):
```bash
cd backend
.venv\Scripts\activate
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

**5. Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```env
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=sqlite:///./data/chat_history.db

# Storage
UPLOAD_DIR=./data/uploads
CHROMA_DIR=./data/chromadb
```

### Important Notes

⚠️ **CRITICAL**: Always use `main:socket_app` when running the backend:
```bash
# ✅ CORRECT (includes WebSocket)
uvicorn main:socket_app --host 0.0.0.0 --port 8000

# ❌ WRONG (chat won't work)
uvicorn main:app --host 0.0.0.0 --port 8000
```

💡 **DNS Configuration**: When running Docker, always include `--dns 8.8.8.8 --dns 8.8.4.4` to ensure OpenRouter API connectivity.

🧹 **Clear Cache**: If you see old test documents, open browser console and run:
```javascript
localStorage.clear()
location.reload()
```

---

## 📁 Project Structure

```
chatpdf/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── auth.py            # Authentication
│   │   ├── pdf_processing.py  # PDF parsing & embeddings
│   │   ├── chat.py            # AI chat logic
│   │   ├── chat_history_db.py # Database management
│   │   └── openrouter_client.py # OpenRouter API client
│   ├── data/
│   │   ├── uploads/           # PDF storage
│   │   ├── chromadb/          # Vector embeddings
│   │   └── chat_history/      # SQLite database
│   ├── main.py                # FastAPI + Socket.IO app
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ChatPanel.tsx  # Chat interface
│   │   │   ├── PdfViewer.tsx  # PDF preview
│   │   │   ├── Sidebar.tsx    # Navigation
│   │   │   └── UploadScreen.tsx # Upload UI
│   │   ├── App.tsx            # Main app
│   │   └── main.tsx           # Entry point
│   ├── public/
│   │   └── pdf.worker.min.js  # PDF.js worker (local)
│   └── package.json
│
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Multi-service setup
├── EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md  # Deployment guide
└── README.md                   # This file
```

---

## 🧪 Testing

### Test Docker Build
```bash
docker build -t pdfpixie:test .
```

### Test Docker Run
```bash
docker run --rm -p 80:80 -p 8000:8000 \
  -e OPENROUTER_API_KEY=test \
  pdfpixie:test
```

### Check Container Health
```bash
docker ps
# Should show STATUS: Up X seconds (healthy)

# Or check manually
curl http://localhost/health
# Should return: {"status":"healthy","service":"pdfpixie-api"}
```

### View Container Logs
```bash
# Real-time logs
docker logs -f pdfpixie-app

# Last 100 lines
docker logs --tail 100 pdfpixie-app

# Check for WebSocket errors
docker logs pdfpixie-app | grep -i "socket\|websocket"
```

---

## 🚨 Troubleshooting

### Common Issues

**1. WebSocket Connection Fails (403 Forbidden)**
```bash
# Solution: Ensure you're using socket_app
docker exec -it pdfpixie-app ps aux | grep uvicorn
# Should show: uvicorn main:socket_app

# If not, rebuild the container
```

**2. OpenRouter API Not Reachable**
```bash
# Test DNS resolution inside container
docker exec -it pdfpixie-app nslookup api.openrouter.ai

# If fails, restart with DNS flags
docker stop pdfpixie-app
docker rm pdfpixie-app
docker run -d --dns 8.8.8.8 --dns 8.8.4.4 ... pdfpixie:latest
```

**3. PDF Worker Fails to Load**
```bash
# Check if worker file exists
docker exec -it pdfpixie-app ls /var/www/html/pdf.worker.min.js

# Should exist at root of web directory
curl http://localhost/pdf.worker.min.js
# Should return 200 OK
```

**4. Container Won't Start**
```bash
# Check logs
docker logs pdfpixie-app

# Common issues:
# - Port already in use: Change -p 8080:80 instead of -p 80:80
# - Missing API key: Add -e OPENROUTER_API_KEY=your_key
# - Out of memory: Upgrade to t3.small on EC2
```

**5. Large Image Size**
```bash
# Current optimized size
docker images | grep pdfpixie
# Should show ~859MB

# If larger, rebuild with clean Docker cache
docker system prune -a
docker build --no-cache -t pdfpixie:latest .
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Docker Image Size | 859MB (optimized) |
| Container Memory | ~512MB RAM |
| Startup Time | ~30 seconds |
| PDF Processing | ~5-10 sec per document |
| Chat Response Time | ~2-5 seconds |
| WebSocket Latency | <100ms |

---

## 🔐 Security Best Practices

✅ **For Production:**
1. Use environment variables for secrets (never commit API keys)
2. Enable HTTPS with Let's Encrypt SSL certificates
3. Configure firewall rules (UFW on EC2)
4. Use SSH key authentication (disable password login)
5. Regular security updates: `sudo apt update && sudo apt upgrade`
6. Set up automated backups for persistent data
7. Monitor logs for suspicious activity

❌ **Never:**
- Commit `.env` files to Git
- Use default passwords
- Expose port 8000 directly (use Nginx proxy)
- Run as root user in production

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - High-performance Python web framework
- **React** - Powerful UI library
- **Socket.IO** - Real-time WebSocket communication
- **LangChain** - AI orchestration framework
- **ChromaDB** - Vector database for embeddings
- **OpenRouter** - Multi-model AI API access
- **PDF.js** - PDF rendering in browser
- **Nginx** - High-performance web server

---

**Made with ❤️ for intelligent document interaction**

**Repository**: [github.com/yourusername/chatpdf](https://github.com/yourusername/chatpdf)
**Issues**: [Report a bug](https://github.com/yourusername/chatpdf/issues)
**Docs**: [Full Documentation](./EC2_SINGLE_INSTANCE_DOCKER_DEPLOYMENT.md)