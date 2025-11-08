# 🏗️ PDFPixie EC2 Deployment Architecture

Visual guide to understand how PDFPixie is deployed on AWS EC2 with DuckDNS.

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
│                    (Users Worldwide)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
                    ┌────▼─────┐
                    │  DuckDNS │ (Free DNS Service)
                    │  Domain  │ your-app.duckdns.org
                    └────┬─────┘
                         │
                         │ Resolves to
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                    AWS EC2 Instance                               │
│                  (Ubuntu 22.04 LTS)                               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Docker Container: pdfpixie-app              │    │
│  │                                                           │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │            Nginx (Reverse Proxy)                  │   │    │
│  │  │            Port 80 (HTTP) / 443 (HTTPS)          │   │    │
│  │  └──────────────┬──────────────────┬────────────────┘   │    │
│  │                 │                  │                      │    │
│  │        ┌────────▼─────────┐  ┌────▼──────────────┐      │    │
│  │        │   Static Files   │  │  FastAPI Backend  │      │    │
│  │        │   (React Build)  │  │   Port 8000       │      │    │
│  │        │  - index.html    │  │  - REST API       │      │    │
│  │        │  - JavaScript    │  │  - Socket.IO      │      │    │
│  │        │  - CSS           │  │  - WebSocket      │      │    │
│  │        │  - pdf.worker.js │  │  - PDF Processing │      │    │
│  │        └──────────────────┘  └────┬──────────────┘      │    │
│  │                                    │                      │    │
│  │                           ┌────────▼────────────┐        │    │
│  │                           │  Python Libraries   │        │    │
│  │                           │  - LangChain        │        │    │
│  │                           │  - PyMuPDF          │        │    │
│  │                           │  - ChromaDB         │        │    │
│  │                           └─────────────────────┘        │    │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Docker Container: pdfpixie-postgres              │    │
│  │              PostgreSQL 15 Database                       │    │
│  │              Port 5432 (internal only)                    │    │
│  │         - User sessions                                   │    │
│  │         - Chat history                                    │    │
│  │         - Document metadata                               │    │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          Docker Container: pdfpixie-redis                 │    │
│  │                Redis Cache                                │    │
│  │              Port 6379 (internal only)                    │    │
│  │         - Session storage                                 │    │
│  │         - Real-time chat state                            │    │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Docker Volumes                           │    │
│  │         - postgres_data (PostgreSQL data)                 │    │
│  │         - redis_data (Redis persistence)                  │    │
│  │         - app_data (PDFs, embeddings, SQLite)             │    │
│  │         - app_logs (Application logs)                     │    │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS API Calls
                         │
                    ┌────▼─────┐
                    │OpenRouter│ (AI Service)
                    │   API    │ api.openrouter.ai
                    └──────────┘
```

---

## 🔄 Request Flow Diagrams

### 1️⃣ PDF Upload Flow

```
User Browser                Nginx               FastAPI              Storage
─────────────              ──────              ────────             ────────
     │                        │                    │                    │
     │  Upload PDF            │                    │                    │
     ├───────────────────────>│                    │                    │
     │                        │  POST /upload      │                    │
     │                        ├───────────────────>│                    │
     │                        │                    │  Save to disk      │
     │                        │                    ├───────────────────>│
     │                        │                    │                    │
     │                        │                    │  Extract text      │
     │                        │                    │  (PyMuPDF)         │
     │                        │                    │                    │
     │                        │                    │  Create embeddings │
     │                        │                    │  (ChromaDB)        │
     │                        │                    │                    │
     │                        │  200 OK + doc_id   │                    │
     │  Success Response      │<───────────────────┤                    │
     │<───────────────────────┤                    │                    │
     │                        │                    │                    │
```

### 2️⃣ Chat Message Flow

```
User Browser         WebSocket           FastAPI         OpenRouter API      ChromaDB
─────────────       ──────────          ────────        ──────────────      ────────
     │                   │                  │                   │               │
     │  Send Message     │                  │                   │               │
     ├──────────────────>│                  │                   │               │
     │                   │  Socket emit     │                   │               │
     │                   ├─────────────────>│                   │               │
     │                   │                  │  Search vectors   │               │
     │                   │                  ├──────────────────────────────────>│
     │                   │                  │  Relevant chunks  │               │
     │                   │                  │<──────────────────────────────────┤
     │                   │                  │                   │               │
     │                   │                  │  Send prompt      │               │
     │                   │                  ├──────────────────>│               │
     │                   │                  │  AI response      │               │
     │                   │                  │<──────────────────┤               │
     │                   │  Socket response │                   │               │
     │  Display Response │<─────────────────┤                   │               │
     │<──────────────────┤                  │                   │               │
     │                   │                  │  Save to SQLite   │               │
     │                   │                  │  (chat history)   │               │
     │                   │                  │                   │               │
```

### 3️⃣ Session Restore Flow

```
User Browser            Nginx              FastAPI           PostgreSQL/SQLite
─────────────          ──────             ────────          ─────────────────
     │                    │                   │                      │
     │  Page Load         │                   │                      │
     │  (with device_id)  │                   │                      │
     │                    │                   │                      │
     │  GET /sessions/all │                   │                      │
     ├───────────────────>│                   │                      │
     │                    │  Forward          │                      │
     │                    ├──────────────────>│                      │
     │                    │                   │  Query sessions      │
     │                    │                   ├─────────────────────>│
     │                    │                   │  Return sessions     │
     │                    │                   │<─────────────────────┤
     │                    │  200 + sessions   │                      │
     │  Render sidebar    │<──────────────────┤                      │
     │<───────────────────┤                   │                      │
     │                    │                   │                      │
```

---

## 🌐 Network Architecture

### Port Mapping

```
External                Internal (Docker)
────────               ──────────────────

Port 80 (HTTP)    ──>  Nginx (Container port 80)
                        │
                        └──> FastAPI (Container port 8000)
                             - REST API: /api/*
                             - Health: /health
                             - Upload: /upload
                             - WebSocket: /socket.io/*

Port 443 (HTTPS)  ──>  Nginx (Container port 443) [If SSL enabled]

Port 22 (SSH)     ──>  EC2 Instance (Not Docker)


Internal Only (No external access):
────────────────────────────────────
PostgreSQL: 5432 (Container to Container)
Redis: 6379 (Container to Container)
```

### Docker Network

```
┌──────────────────────────────────────────────┐
│       Docker Network: pdfpixie-network        │
│               (Bridge Mode)                   │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   App    │  │ Postgres │  │  Redis   │   │
│  │Container │  │Container │  │Container │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │          │
│       └─────────────┴──────────────┘          │
│         Internal DNS Resolution:              │
│         - postgres:5432                       │
│         - redis:6379                          │
└──────────────────────────────────────────────┘
```

---

## 💾 Data Flow & Storage

### File Storage Hierarchy

```
EC2 Instance: /home/ubuntu/chatpdf/
│
├── backend/data/                    # Mounted to Docker volume
│   ├── uploads/                     # Uploaded PDF files
│   │   └── user_document.pdf
│   │
│   ├── chromadb/                    # Vector embeddings
│   │   ├── chroma.sqlite3
│   │   └── embeddings/
│   │
│   ├── chat_history/                # SQLite chat database
│   │   └── chat_history.db
│   │
│   └── mock_embeddings/             # Keyword-based search cache
│       └── doc_*.json
│
└── Docker Volumes: /var/lib/docker/volumes/
    ├── chatpdf_postgres_data/       # PostgreSQL database
    │   └── pgdata/
    │
    ├── chatpdf_redis_data/          # Redis persistence
    │   └── dump.rdb
    │
    └── chatpdf_app_logs/            # Application logs
        └── app.log
```

### Data Persistence Strategy

```
                     ┌─────────────────────┐
                     │   Docker Volume     │
                     │    (Named)          │
                     │  - Survives restart │
                     │  - Survives rebuild │
                     └──────────┬──────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
    ┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼───────┐
    │ postgres_data  │  │ redis_data  │  │   app_data     │
    │  (PostgreSQL)  │  │   (Redis)   │  │ (PDFs/Vectors) │
    └────────────────┘  └─────────────┘  └────────────────┘
```

---

## 🔒 Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: AWS Security                     │
│  - EC2 Security Group (Firewall)                             │
│  - SSH Key-based Authentication                              │
│  - Restricted Port Access (22, 80, 443)                      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Layer 2: SSL/TLS (Optional)                 │
│  - Let's Encrypt Certificates                                │
│  - HTTPS Encryption                                          │
│  - HTTP to HTTPS Redirect                                    │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Layer 3: Docker Isolation                   │
│  - Container Network Isolation                               │
│  - Internal-only Database Access                             │
│  - No Direct Internet Access to DB/Redis                     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              Layer 4: Application Security                   │
│  - Environment Variable Secrets                              │
│  - Device-based Authentication                               │
│  - Input Validation                                          │
│  - API Rate Limiting (Future)                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Update & Rollback Strategy

### Deployment Pipeline

```
Developer          GitHub           EC2 Instance        Docker
──────────        ───────          ────────────        ──────
     │                │                  │                │
     │  git push      │                  │                │
     ├───────────────>│                  │                │
     │                │                  │                │
     │                │  git pull        │                │
     │                │<─────────────────┤                │
     │                │                  │                │
     │                │                  │  docker build  │
     │                │                  ├───────────────>│
     │                │                  │                │
     │                │                  │  docker up -d  │
     │                │                  ├───────────────>│
     │                │                  │                │
     │                │  Verify Health   │                │
     │                │<─────────────────┤                │
     │                │                  │                │
```

### Zero-Downtime Update (Future)

```
┌────────────────────────────────────────────────────────┐
│               Blue-Green Deployment                     │
│                                                         │
│  ┌─────────────┐              ┌─────────────┐         │
│  │   Current   │              │    New      │         │
│  │  Container  │              │  Container  │         │
│  │   (Blue)    │              │  (Green)    │         │
│  └──────┬──────┘              └──────┬──────┘         │
│         │                            │                 │
│         │     Switch Traffic ────────┘                 │
│         │     After Health Check                       │
│         │                                              │
│  Shared: PostgreSQL, Redis, Volumes                    │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring Architecture

### Health Check Flow

```
                    ┌─────────────────┐
                    │  Docker Health  │
                    │     Check       │
                    │  (Every 30s)    │
                    └────────┬────────┘
                             │
                    curl http://localhost/health
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼────────┐ ┌──▼──────┐ ┌─────▼──────┐
    │   Nginx Check    │ │FastAPI  │ │ PostgreSQL │
    │  (200 OK = ✅)   │ │ Check   │ │   Check    │
    └──────────────────┘ └─────────┘ └────────────┘
```

### Log Aggregation

```
Application Logs         Docker Logs          Monitoring
────────────────        ──────────────        ──────────
     │                       │                     │
     │  Write to stdout      │                     │
     ├──────────────────────>│                     │
     │                       │  docker logs -f     │
     │                       ├────────────────────>│
     │                       │                     │
     │                       │  Forward to         │
     │                       │  CloudWatch         │
     │                       │  (Future)           │
     │                       │                     │
```

---

## 🚀 Scaling Architecture (Future)

### Multi-Instance Deployment

```
                    ┌─────────────┐
                    │  Route 53   │
                    │   (DNS)     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │     ALB     │
                    │(Load Balance)│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼────┐     ┌─────▼────┐    ┌─────▼────┐
    │ EC2 (1)  │     │ EC2 (2)  │    │ EC2 (3)  │
    │PDFPixie  │     │PDFPixie  │    │PDFPixie  │
    └─────┬────┘     └─────┬────┘    └─────┬────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼────┐     ┌─────▼────┐    ┌─────▼────┐
    │   RDS    │     │ElastiCache│   │    S3    │
    │(Postgres)│     │  (Redis)  │    │(PDF Files)│
    └──────────┘     └───────────┘    └──────────┘
```

---

## 📚 References

- **Deployment Guide**: See `docs/EC2_DEPLOYMENT_GUIDE.md`
- **Quick Start**: See `docs/QUICK_DEPLOY.md`
- **Architecture Source**: PDFPixie current implementation

---

*This architecture diagram represents the current production deployment on a single EC2 instance with Docker containers.*
