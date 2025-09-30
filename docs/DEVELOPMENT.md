# Development Guide

This guide will help you set up and run the Newchat application locally for development.

## Prerequisites

Make sure you have the following installed:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.13.7** - [Download here](https://www.python.org/)
- **UV Package Manager** - [Install guide](https://github.com/astral-sh/uv)
- **Docker & Docker Compose** - [Download here](https://www.docker.com/)
- **Git** - [Download here](https://git-scm.com/)

## Quick Setup

### Automated Setup (Recommended)

Run the setup script for your platform:

**Windows:**
```bash
.\scripts\setup.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup

If you prefer to set up manually:

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Newchat
```

#### 2. Set Up Backend
```bash
cd backend

# Install UV (if not already installed)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Unix: curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with UV
uv venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies (much faster with UV)
# Note: Using ChromaDB instead of FAISS for Python 3.13 compatibility
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Set Up Frontend
```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

#### 4. Start Development Services
```bash
# Start PostgreSQL and Redis
docker-compose -f docker-compose.dev.yml up -d
```

## Running the Application

### Development Mode

Start each service in separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn main:socket_app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 - Services (if not already running):**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Production Mode

Build and run with Docker:

```bash
docker-compose up --build
```

## Application URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **PGAdmin:** http://localhost:5050 (admin@newchat.dev / admin)
- **Redis Commander:** http://localhost:8081

## Environment Variables

### Backend (.env)

```env
# Required for AI functionality
OPENAI_API_KEY=your-openai-api-key

# AWS Configuration (for S3 and Cognito)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-s3-bucket-name

# Database (auto-configured for development)
DATABASE_URL=postgresql://newchat_user:newchat_password@localhost:5432/newchat

# Redis (auto-configured for development)
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SOCKET_URL=http://localhost:8000
```

## Development Workflow

### 1. Making Changes

- **Backend:** Files are auto-reloaded with `--reload` flag
- **Frontend:** Hot reloading is enabled by default with Create React App

### 2. Database Changes

If you modify the database schema:

```bash
# Restart the database container
docker-compose -f docker-compose.dev.yml restart postgres

# Or recreate with fresh data
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Adding Dependencies

**Backend:**
```bash
cd backend
source .venv/bin/activate
uv pip install new-package
uv pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install new-package
```

### 4. Testing

**Backend Tests:**
```bash
cd backend
source .venv/bin/activate
pytest tests/
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if services are already running: `docker ps`
   - Stop conflicting services: `docker-compose -f docker-compose.dev.yml down`

2. **Python virtual environment issues**
   - Delete and recreate: `rm -rf .venv && uv venv`

3. **Node modules issues**
   - Clear cache: `npm cache clean --force`
   - Reinstall: `rm -rf node_modules package-lock.json && npm install`

4. **Database connection issues**
   - Check if PostgreSQL is running: `docker-compose -f docker-compose.dev.yml ps`
   - Check logs: `docker-compose -f docker-compose.dev.yml logs postgres`

### Logs

View logs for debugging:

```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f postgres
docker-compose -f docker-compose.dev.yml logs -f redis

# Backend logs (when running locally)
tail -f backend/logs/app.log
```

## Development Tips

1. **Use the API documentation** at http://localhost:8000/docs for testing endpoints
2. **Monitor database** with PGAdmin at http://localhost:5050
3. **Check Redis data** with Redis Commander at http://localhost:8081
4. **Use browser dev tools** for frontend debugging
5. **Check backend logs** for API errors and debugging info

## Project Structure

```
Newchat/
├── frontend/           # React TypeScript app
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   └── ...
│   └── public/
├── backend/            # FastAPI Python app
│   ├── app/           # Application modules
│   │   ├── auth.py    # Authentication logic
│   │   ├── pdf_processing.py  # PDF handling
│   │   └── chat.py    # Chat functionality
│   └── main.py        # Application entry point
├── docker/            # Docker configurations
├── scripts/           # Setup and utility scripts
└── docs/             # Documentation
```

## Next Steps

Once you have the development environment running:

1. **Configure your API keys** in the `.env` files
2. **Test PDF upload** functionality
3. **Try the chat interface** with a sample PDF
4. **Explore the API documentation** at `/docs`
5. **Check the database** to see how data is stored

For production deployment, see the [Deployment Guide](./DEPLOYMENT.md).