# PDF Pal - AI-Powered PDF Chat Application

> **Professional PDF analysis and interactive chat powered by AI**

A modern, full-stack application for uploading PDFs and having intelligent conversations about their content. Built with React, FastAPI, and Socket.IO for real-time interactions.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Node Version](https://img.shields.io/badge/node-18%2B-green)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)

---

## 🎯 Features

- 📄 **PDF Upload & Processing**: Drag-and-drop interface with real-time progress
- 🤖 **AI-Powered Chat**: Ask questions and get intelligent answers about your PDFs
- ⚡ **Real-time Communication**: Socket.IO WebSockets for instant messaging
- 🎨 **Modern UI**: Beautiful animations with Framer Motion and professional design
- 📱 **Responsive**: Works seamlessly on desktop, tablet, and mobile
- 🔍 **Source Citations**: Click to jump to specific pages in the PDF
- 💾 **Chat History**: All conversations saved and easily accessible
- 🚀 **Fast Development**: UV package manager for 10-100x faster Python installs

---

## 📋 Table of Contents

- [Quick Start (5 Minutes)](#-quick-start-5-minutes)
- [Detailed Setup](#-detailed-setup)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Common Issues & Solutions](#-common-issues--solutions)
- [Configuration](#-configuration)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.10, 3.11, or 3.12** (Python 3.13 not fully supported yet)
- **Git** - [Download here](https://git-scm.com/)

### Installation

#### For Windows Users:

```powershell
# 1. Clone the repository
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf

# 2. Run the automated setup script
.\scripts\setup.bat

# 3. Start the application
.\scripts\quick-start.bat
```

#### For Mac/Linux Users:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/chatpdf.git
cd chatpdf

# 2. Run the automated setup script
chmod +x scripts/setup.sh scripts/quick-start.sh
./scripts/setup.sh

# 3. Start the application
./scripts/quick-start.sh
```

### Access the Application

- **Frontend**: http://localhost:3000 (or 3001 if 3000 is in use)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📦 Detailed Setup

### Step 1: Install Dependencies

#### Backend Setup

```bash
cd backend

# Install UV (faster than pip) - Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install UV - Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install packages
uv venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows PowerShell

# Install all dependencies
uv pip install -r requirements.txt
```

#### Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Or use yarn if you prefer
yarn install
```

### Step 2: Configure Environment Variables

#### Backend Configuration

```bash
# Copy the example environment file
cd backend
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows

# Edit .env and add your API key (REQUIRED for AI responses)
```

**Get your OpenRouter API key** (free tier available):
1. Visit https://openrouter.ai/keys
2. Sign up/login
3. Click "Create Key"
4. Copy the key and paste into `.env`:

```bash
# backend/.env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Optional: Use free models to avoid costs
# Edit backend/app/openrouter_client.py line 30:
# model="meta-llama/llama-3.1-8b-instruct:free"
```

#### Frontend Configuration

```bash
cd frontend
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows

# Edit .env (defaults are usually fine)
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

### Step 3: Start the Application

**⚠️ CRITICAL**: Backend **MUST** use `socket_app` for chat to work!

#### Option A: Manual Start (Recommended for Development)

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

#### Option B: Use Startup Scripts

**Windows:**
```powershell
.\start_servers.ps1
```

**Mac/Linux:**
```bash
chmod +x scripts/quick-start.sh
./scripts/quick-start.sh
```

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool
- **Socket.IO Client** - Real-time communication
- **React-PDF** - PDF viewing and navigation
- **React Dropzone** - Drag-and-drop file uploads
- **Framer Motion** - Smooth animations
- **Axios** - HTTP requests

### Backend
- **FastAPI** - Modern async Python web framework
- **Socket.IO** - Real-time WebSocket communication
- **PyMuPDF (fitz)** - PDF text extraction
- **LangChain** - AI/LLM integration framework
- **OpenRouter API** - Access to multiple AI models
- **ChromaDB** - Vector database for embeddings (when available)
- **Uvicorn** - ASGI server

### Development Tools
- **UV** - Ultra-fast Python package installer
- **ESLint** - JavaScript linting
- **TypeScript** - Static typing
- **Git** - Version control

---

## 📁 Project Structure

```
chatpdf/
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── SplashScreen.tsx
│   │   │   ├── UploadScreen.tsx
│   │   │   ├── ChatWorkspace.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── PdfViewer.tsx
│   │   │   └── ...
│   │   ├── App.tsx             # Main app with routing
│   │   ├── main.tsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── .env.example
│   └── .env                    # Your local config
│
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication logic
│   │   ├── chat.py            # AI chat response generation
│   │   ├── chat_history.py    # Chat session management
│   │   ├── pdf_processing.py  # PDF upload & processing
│   │   └── openrouter_client.py  # OpenRouter API client
│   ├── data/
│   │   ├── uploads/           # Uploaded PDF files
│   │   ├── chat_history/      # Chat session JSON files
│   │   └── mock_embeddings/   # Mock vector embeddings
│   ├── main.py                # FastAPI app entry (MUST use socket_app!)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example
│   └── .env                   # Your local config (with API keys)
│
├── docker/                     # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── scripts/                    # Setup and utility scripts
│   ├── setup.bat              # Windows setup
│   ├── setup.sh               # Mac/Linux setup
│   ├── quick-start.bat        # Windows quick start
│   └── quick-start.sh         # Mac/Linux quick start
│
├── docs/                       # Documentation
│   ├── DEVELOPMENT.md
│   ├── PYTHON_313_MIGRATION.md
│   └── UV_MIGRATION.md
│
├── .github/
│   └── copilot-instructions.md  # Project guidelines
│
├── docker-compose.yml         # Full-stack Docker setup
├── README.md                  # This file
└── start_servers.ps1          # Windows startup script
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Chat Input Disabled / "Disconnected" Status

**Symptoms:**
- Gray chat input field
- Send button disabled
- Red "Disconnected" indicator in UI
- Console shows: `❌ Socket connection error`

**Solutions:**

1. **Check you're running the correct backend app:**
   ```bash
   # ❌ WRONG - This won't work for chat!
   uvicorn main:app --reload
   
   # ✅ CORRECT - Must use socket_app!
   python -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
   ```

2. **Check backend logs for errors:**
   - Look for `✅ Client <sid> connected` messages
   - If you see 403/404 errors, CORS might be misconfigured

3. **Check frontend Socket.IO configuration:**
   - Open browser DevTools (F12) → Console
   - Should see: `🔌 Initializing Socket.IO connection`
   - Should NOT see: `connect_error` messages

4. **Verify ports:**
   ```powershell
   # Windows
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   
   # Mac/Linux
   lsof -i :8000
   lsof -i :3000
   ```

5. **Restart both servers:**
   ```bash
   # Kill existing processes and restart
   # Windows: Ctrl+C in terminal, then restart
   # Linux/Mac: killall uvicorn && killall node
   ```

### Issue 2: Getting Mock Responses Instead of Real AI

**Symptoms:**
- Responses start with "Mock response:"
- Backend logs show: `OpenRouter API call failed or is not configured`

**Solutions:**

1. **Get a valid OpenRouter API key:**
   - Visit https://openrouter.ai/keys
   - Create a free account
   - Generate new API key
   - Copy the key (starts with `sk-or-v1-...`)

2. **Update your `.env` file:**
   ```bash
   cd backend
   # Edit .env file
   OPENROUTER_API_KEY=sk-or-v1-your-new-key-here
   ```

3. **Restart the backend server:**
   ```bash
   # Stop with Ctrl+C, then:
   python -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
   ```

4. **Test the API key:**
   ```bash
   curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": "Hello"}]}'
   
   # Should return AI response, NOT {"error": {"code": 401}}
   ```

5. **Use free models to save costs:**
   - Edit `backend/app/openrouter_client.py` line 30
   - Change to: `model="meta-llama/llama-3.1-8b-instruct:free"`

### Issue 3: Port Already in Use

**Symptoms:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solutions:**

```powershell
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux - Find and kill process
lsof -ti:8000 | xargs kill -9

# Or change port in backend startup:
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8001
# Then update frontend/.env: VITE_API_URL=http://localhost:8001
```

### Issue 4: npm/node Commands Not Found

**Symptoms:**
```
'npm' is not recognized as an internal or external command
```

**Solutions:**

1. **Install Node.js:**
   - Download from https://nodejs.org/ (LTS version)
   - Restart terminal after installation
   - Verify: `node --version` and `npm --version`

2. **Fix PowerShell execution policy (Windows):**
   ```powershell
   # Run PowerShell as Administrator
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Use cmd instead of PowerShell:**
   ```cmd
   cmd /c "npm run dev"
   ```

### Issue 5: Python Version Issues

**Symptoms:**
- Import errors with langchain or chromadb
- `No module named 'hnswlib'`

**Solutions:**

1. **Use Python 3.10, 3.11, or 3.12** (NOT 3.13):
   ```bash
   python --version  # Check your version
   
   # If 3.13, install 3.12:
   # Windows: Download from python.org
   # Mac: brew install python@3.12
   # Linux: sudo apt install python3.12
   ```

2. **Recreate virtual environment:**
   ```bash
   cd backend
   rm -rf .venv  # or rmdir /s .venv on Windows
   python3.12 -m venv .venv  # Use specific Python version
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

### Issue 6: PDF Upload Fails / 404 Errors

**Symptoms:**
- Upload hangs forever
- 404 on `/api/pdf/{document_id}`

**Solutions:**

1. **Check `data/uploads/` directory exists:**
   ```bash
   mkdir -p backend/data/uploads
   ```

2. **Check file permissions:**
   - Ensure backend has write access to `data/` folder

3. **Check backend logs:**
   - Look for PDF processing errors
   - Verify PyMuPDF is installed: `pip list | grep PyMuPDF`

4. **Test API endpoint:**
   ```bash
   curl -X GET http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

---

## ⚙️ Configuration

### Backend Configuration (backend/.env)

```bash
# === REQUIRED FOR AI RESPONSES ===
OPENROUTER_API_KEY=sk-or-v1-your-key-here  # Get from https://openrouter.ai/keys

# === OPTIONAL (for production) ===
# AWS Services
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/chatpdf

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=your-secret-key-change-in-production
COGNITO_USER_POOL_ID=your-pool-id
COGNITO_CLIENT_ID=your-client-id

# Server Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Frontend Configuration (frontend/.env)

```bash
# Backend URLs
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
```

### Development vs Production

**Development Mode** (default):
- ✅ No AWS credentials needed
- ✅ Local file storage (`backend/data/uploads/`)
- ✅ Mock embeddings for vector search
- ✅ Dev token authentication
- ✅ Hot reload enabled

**Production Mode** (requires setup):
- AWS S3 for file storage
- PostgreSQL for chat history
- Redis for caching
- AWS Cognito for authentication
- Real embeddings with OpenAI/ChromaDB

---

## 👩‍💻 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# E2E tests
npm run e2e
```

### Code Formatting

```bash
# Backend (Python)
cd backend
black .
ruff check .

# Frontend (TypeScript)
cd frontend
npm run lint
npm run format
```

### Adding New Features

1. Create a feature branch: `git checkout -b feature/my-new-feature`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -m "Add: my new feature"`
5. Push: `git push origin feature/my-new-feature`
6. Create Pull Request

### Debugging

**Backend Debugging:**
```python
# Add to any Python file
import pdb; pdb.set_trace()  # Breakpoint

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

**Frontend Debugging:**
```typescript
// Browser DevTools (F12)
console.log('Debug:', variable);
debugger;  // Breakpoint

// React DevTools Extension
// Install: https://react.dev/learn/react-developer-tools
```

**Network Debugging:**
```bash
# Check Socket.IO events in browser DevTools:
# F12 → Network → WS (WebSocket) → Messages

# Backend logs show all Socket.IO events:
✅ Client <sid> connected
📥 Received query from <sid>: what is this pdf about...
🤖 Generating AI response...
✅ Generated response for <sid>: Based on the document...
```

---

## 🐳 Deployment

### Docker Compose (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Manual Deployment

#### Backend

```bash
cd backend
gunicorn main:socket_app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend

```bash
cd frontend
npm run build
# Serve the 'dist' folder with nginx, caddy, or any static host
```

### Environment Variables for Production

```bash
# backend/.env (production)
DEBUG=False
SECRET_KEY=<strong-random-key>
OPENROUTER_API_KEY=<your-production-key>
DATABASE_URL=<production-db-url>
REDIS_URL=<production-redis-url>
FRONTEND_URL=https://your-domain.com
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Socket.IO Docs**: https://socket.io/docs/
- **OpenRouter API**: https://openrouter.ai/docs
- **UV Package Manager**: https://github.com/astral-sh/uv

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new features
5. Update documentation
6. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- OpenRouter for AI API access
- React team for the UI library
- All open-source contributors

---

## 📞 Support

**Having issues?**
1. Check [Common Issues & Solutions](#-common-issues--solutions)
2. Search existing [GitHub Issues](https://github.com/yourusername/chatpdf/issues)
3. Create a new issue with:
   - Your OS and Python/Node versions
   - Error messages and logs
   - Steps to reproduce

**Questions?**
- Open a [Discussion](https://github.com/yourusername/chatpdf/discussions)
- Check project documentation in `/docs`

---

<div align="center">

**Made with ❤️ using FastAPI, React, and Socket.IO**

⭐ **Star this repo** if you find it helpful!

</div>