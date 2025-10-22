# PDFPixie - AI-Powered PDF Chat Application 🤖📄

Your intelligent PDF companion. Upload PDFs, ask questions, and get AI-powered responses based on document content using advanced semantic search and real-time chat.

## 🚀 **Quick Deploy (100% Free)**

Deploy to **Fly.io** (backend) + **Vercel** (frontend):

**📚 [Complete Deployment Guide →](FLY_VERCEL_DEPLOYMENT.md)**

```bash
# Backend to Fly.io
fly launch --dockerfile Dockerfile.fly
fly deploy

# Frontend to Vercel  
vercel --prod
```

## ✨ Features

- 📄 **PDF Upload & Processing** - Drag-and-drop interface with instant text extraction
- 🤖 **AI-Powered Chat** - Interactive conversations with your PDF documents
- 🔍 **Semantic Search** - ChromaDB vector embeddings for accurate context retrieval
- ⚡ **Real-time Communication** - WebSocket-based chat with typing indicators
- 💬 **Chat History** - Persistent conversation storage with PostgreSQL
- 🎨 **Modern UI** - Beautiful interface with glassmorphism effects and Zen Serif font
- 🚀 **Fast Development** - UV package manager for 10-100x faster installations

## 🛠️ Tech Stack

**Frontend (Vercel):**
- React 18 + TypeScript
- Socket.IO Client (real-time communication)
- React-PDF (document preview)
- Vite (build tool)
- CSS3 with custom design system

**Backend (Fly.io):**
- FastAPI (async Python web framework)
- Socket.IO Server (WebSocket communication)
- LangChain (AI orchestration)
- ChromaDB (vector embeddings)
- PyMuPDF (PDF text extraction)
- OpenRouter API (AI responses)
- PostgreSQL (chat history & metadata)

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

## � Production Deployment

See the complete deployment guide: **[FLY_VERCEL_DEPLOYMENT.md](FLY_VERCEL_DEPLOYMENT.md)**

### Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel (CDN)   │ ←─────→ │   Fly.io (API)   │
│                 │         │                  │
│  React Frontend │  HTTPS  │  FastAPI Backend │
│  Global Edge    │         │  PostgreSQL DB   │
│                 │         │  Persistent Vol. │
└─────────────────┘         └──────────────────┘
```

**Benefits:**
- ✅ 100% Free hosting
- ✅ Global CDN (Vercel)
- ✅ Persistent storage (Fly.io)
- ✅ PostgreSQL included
- ✅ Auto-deploy on git push

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- React team for the powerful UI library
- LangChain for AI orchestration tools
- ChromaDB for vector embeddings
- OpenRouter for AI API access

---

**Made with ❤️ for intelligent document interaction**