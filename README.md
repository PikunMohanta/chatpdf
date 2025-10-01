# Newchat - AI-Powered PDF Chat Application

A full-stack AI-powered PDF ingestion, parsing, and interactive chat application. Upload PDFs, ask questions, and get intelligent responses based on document content.

## Features

- 📄 **PDF Upload & Processing**: Drag-and-drop PDF uploads with text extraction
- 🤖 **AI-Powered Chat**: Interactive chat with AI based on PDF content
- 🔍 **Semantic Search**: ChromaDB vector embeddings for accurate document search
- 🔐 **Authentication**: AWS Cognito integration with JWT tokens
- ⚡ **Real-time**: WebSocket-based chat with typing indicators
- 📱 **Responsive**: Modern UI with Tailwind CSS
- 🐳 **Containerized**: Docker and Kubernetes ready
- ☁️ **Cloud Native**: AWS S3, RDS, and Bedrock integration

## Tech Stack

- **Frontend**: React 18 + TypeScript, CSS, Socket.io-client, React-PDF, Vite
- **Backend**: FastAPI, LangChain, PyMuPDF, ChromaDB
- **Package Manager**: UV (10-100x faster than pip)
- **Storage**: AWS S3, PostgreSQL/RDS
- **AI**: OpenRouter API, ChromaDB embeddings
- **Deployment**: Docker, Kubernetes, GitHub Actions

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- AWS CLI configured

### Development Setup

1. **Clone and setup**:
```bash
git clone <repository-url>
cd Newchat
```

2. **Backend Setup**:
```bash
cd backend
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix
# Or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

3. **Frontend Setup**:
```bash
cd frontend
npm install
```

4. **Environment Variables**:
Create `.env` files in both frontend and backend directories (see `.env.example` files)

5. **Start Development**:
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend  
cd frontend
npm start

# Terminal 3: Local services (optional)
docker-compose up -d
```

## Project Structure

```
Newchat/
├── frontend/          # React + Tailwind CSS UI
├── backend/           # FastAPI async backend
├── docker/           # Containerization configs
├── k8s/              # Kubernetes YAMLs/Helm charts
├── scripts/          # CI/CD pipelines, setup scripts
├── docs/             # API documentation
└── .github/          # GitHub workflows and instructions
```

## API Documentation

- Development: http://localhost:8000/docs
- Production: Available after deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details