# Copilot Instructions for PDFPixie

## Project Overview

PDFPixie is a full-stack AI-powered PDF ingestion, parsing, and interactive chat application. Think smart document analyzer with real-time interactions, drag-and-drop features, and seamless AI responses. Your intelligent PDF companion.

## Project Structure

```
PDFPixie/
├── frontend/          # React + TypeScript UI
├── backend/           # FastAPI async backend
├── docker/           # Containerization configs
├── k8s/              # Kubernetes YAMLs/Helm charts
├── scripts/          # CI/CD pipelines, setup scripts
├── .github/
│   └── copilot-instructions.md
└── docs/             # API documentation
```

## Tech Stack

**Frontend**: React, Tailwind CSS, React Dropzone, React-PDF, Socket.io-client
**Backend**: FastAPI, LangChain, PyMuPDF, ChromaDB, Celery, Redis
**Storage**: AWS S3 (PDFs), PostgreSQL/RDS (metadata, chat history) will implement later
**Auth**: AWS Cognito (JWT tokens, role-based access)
**AI**: openrouter, FAISS for vector embeddings
**Deployment**: Docker, Kubernetes (EKS), GitHub Actions CI/CD

## Development Workflow

### Environment Setup
```bash
# Backend dependencies (using UV for faster installs)
cd backend
# Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh (Unix)
# Or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex" (Windows)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Frontend dependencies  
cd frontend
npm install react react-dropzone react-pdf socket.io-client tailwindcss framer-motion
```

### Key Commands
- `uvicorn main:app --reload` - Start FastAPI dev server
- `npm start` - Start React dev server
- `docker-compose up` - Full stack locally
- `kubectl apply -f k8s/` - Deploy to Kubernetes

### Testing
- Backend: `pytest tests/`
- Frontend: `npm test` (Jest), `npm run e2e` (Cypress)
- Integration: `python scripts/test_integration.py`

## Key Conventions

### Code Organization
- **Frontend**: React components in `frontend/src/components/`
  - `UploadComponent.js` - Drag-and-drop PDF uploader with progress bars
  - `ChatComponent.js` - Real-time chat interface with typing indicators
  - `PreviewComponent.js` - PDF preview using react-pdf
- **Backend**: FastAPI routes in `backend/app/`
  - `main.py` - FastAPI app with async endpoints
  - `auth.py` - AWS Cognito JWT validation
  - `pdf_processing.py` - PyMuPDF parsing and FAISS embedding
  - `chat.py` - WebSocket handlers for real-time chat

### API Patterns
```python
# Standard FastAPI endpoint pattern
@app.post("/upload")
async def upload_pdf(file: UploadFile, token: str = Depends(oauth2_scheme)):
    # 1. Validate JWT token via Cognito
    # 2. Upload to S3 with signed URLs
    # 3. Extract text/tables with PyMuPDF
    # 4. Chunk and embed with FAISS
    # 5. Store metadata in PostgreSQL
```

### Frontend Patterns
```jsx
// Real-time chat with Socket.io
const socket = io('http://backend-url');
useEffect(() => {
    socket.on('response', (msg) => setMessages([...messages, { text: msg, from: 'ai' }]));
}, [messages]);
```

### Security Conventions
- All API endpoints require JWT tokens from AWS Cognito
- S3 access via signed URLs only
- Rate limiting on `/query` endpoints
- Input validation for all user uploads

## Integration Points

### AWS Services
- **S3**: PDF storage with lifecycle policies (`your-bucket`)
- **RDS PostgreSQL**: Metadata, chat history, user sessions
- **Cognito**: User pools, JWT tokens, role-based access (admin vs user)
- **Bedrock**: LLM integration (Claude/Llama models)
- **CloudWatch**: Logging and monitoring

### Database Schema
```sql
-- Core tables
sessions: id, user_id, doc_id, history_json, created_at
documents: id, s3_key, filename, user_id, vector_index_path
users: cognito_user_id, email, role, created_at
```

### External Dependencies
- **ChromaDB**: Local vector search (stored as `data/chromadb/`)
- **LangChain**: Prompt templates and embedding chains
- **Socket.io**: Real-time WebSocket communication
- **Redis**: Session caching and real-time chat state

### AI Processing Pipeline
1. PDF upload → PyMuPDF text extraction
2. Text chunking (500 char chunks with overlap)
3. Bedrock embeddings → ChromaDB vector store
4. Query → similarity search → LLM prompt → response

## Development Notes

### Critical Dependencies
- Node.js 18+ for frontend, Python 3.10+ for backend
- **UV package manager** (10-100x faster than pip)
- AWS CLI configured with appropriate IAM roles
- Docker and kubectl for local development
- `.env` files: `AWS_ACCESS_KEY`, `COGNITO_CLIENT_ID`, `DATABASE_URL`

### Performance Patterns
- Lazy loading for PDF previews in React
- Redis caching for chat sessions
- S3 Intelligent-Tiering for cost optimization
- Auto-scaling EKS pods based on CPU metrics

### Deployment Workflow
1. GitHub Actions → Build Docker images
2. Push to ECR → Deploy to EKS via Helm
3. Health checks via `/health` endpoint
4. Monitoring via Prometheus + Grafana

### File Upload Flow
```python
# Backend: Signed URL generation
s3.upload_fileobj(file.file, 'your-bucket', file.filename, 
                  ExtraArgs={'ACL': 'private'})
```

### Chat Context Management
- Store conversation history in PostgreSQL `sessions.history_json`
- Use LangChain Q&A chains for context-aware responses
- Export conversations as markdown via `/export` endpoint

## Quick Reference

### Essential Commands
- `docker-compose up -d` - Start local stack (Redis, PostgreSQL)
- `python -m pytest tests/ -v` - Run backend tests
- `npm run build && npm run preview` - Test production build
- `kubectl get pods -n newchat` - Check deployment status

### Key Files
- `backend/main.py` - FastAPI app entry point
- `frontend/src/components/UploadComponent.js` - PDF drag-and-drop
- `frontend/src/components/ChatComponent.js` - Real-time chat UI
- `k8s/values.yaml` - Helm deployment configuration
- `docker-compose.yml` - Local development environment