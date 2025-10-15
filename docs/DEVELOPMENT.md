# PDFPixie Development Guide 🛠️

Additional development information for contributors and developers.

## Architecture Overview

### Backend (FastAPI)
- **main.py** - FastAPI app with Socket.IO integration
- **app/pdf_processing.py** - PDF text extraction with PyMuPDF
- **app/chat.py** - AI response generation with LangChain
- **app/chat_history_db.py** - SQLite-based chat persistence
- **app/openrouter_client.py** - OpenRouter API client
- **app/auth.py** - Authentication handlers (dev mode)
- **app/database.py** - Database initialization

### Frontend (React + TypeScript)
- **App.tsx** - Main application with routing
- **components/ChatWorkspace.tsx** - Main workspace layout
- **components/ChatPanel.tsx** - Chat interface with Socket.IO
- **components/UploadSection.tsx** - PDF upload with drag-and-drop
- **components/Sidebar.tsx** - Session management sidebar

## Key Technologies

### Vector Search
- **ChromaDB** - Vector embeddings storage
- **Semantic search** - Context-aware document retrieval
- Automatic chunking with overlap for better context

### Real-time Communication
- **Socket.IO** - WebSocket-based chat
- Event-driven architecture
- Automatic reconnection handling

### Database
- **SQLite** - Lightweight chat history storage
- Session-based message persistence
- Automatic database initialization

## Development Workflow

### Adding New Features

1. **Backend Changes**
   ```bash
   # Add new route or functionality
   cd backend/app
   # Edit relevant file
   # Backend auto-reloads with --reload flag
   ```

2. **Frontend Changes**
   ```bash
   # Add new component or feature
   cd frontend/src/components
   # Create or edit component
   # Vite provides instant HMR
   ```

### Debugging

**Backend Logs:**
```python
# Add logging statements
logger.info(f"Debug: {variable}")
logger.error(f"Error occurred: {e}", exc_info=True)
```

**Frontend Console:**
```typescript
// Debug Socket.IO events
socket.on('response', (data) => {
  console.log('Received response:', data)
})
```

### Common Tasks

**Clear Chat History:**
```bash
rm -rf backend/data/chat_history/*.db
```

**Clear Vector Embeddings:**
```bash
rm -rf backend/data/chromadb/*
```

**Reset Everything:**
```bash
rm -rf backend/data/uploads/*
rm -rf backend/data/chromadb/*
rm -rf backend/data/chat_history/*.db
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Keep functions focused and small
- Document complex logic with comments

### TypeScript (Frontend)
- Use functional components with hooks
- Proper TypeScript typing
- CSS modules for styling
- Keep components reusable

## Testing

**Manual Testing Checklist:**
1. ✅ Upload PDF file
2. ✅ Send chat message
3. ✅ Receive AI response
4. ✅ View chat history
5. ✅ Switch between sessions
6. ✅ Refresh page (state persistence)

## Performance Optimization

### Backend
- Async/await for I/O operations
- Efficient chunking strategy
- ChromaDB query optimization
- Connection pooling for database

### Frontend
- React.memo for expensive components
- Lazy loading for PDFs
- Debouncing for search inputs
- Virtual scrolling for long chat histories

## Troubleshooting

### Socket.IO Issues
```bash
# Check Socket.IO events in browser console
# Ensure using 'socket_app' not 'app' in uvicorn
uvicorn main:socket_app --reload  # ✅ Correct
uvicorn main:app --reload          # ❌ Wrong - breaks Socket.IO
```

### Port Conflicts
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Unix/macOS

# Kill process if needed
taskkill /PID <pid> /F        # Windows
kill -9 <pid>                 # Unix/macOS
```

### ChromaDB Issues
```bash
# If ChromaDB corrupts, remove and recreate
rm -rf backend/data/chromadb
# Re-upload PDFs to regenerate embeddings
```

## Deployment Notes

- Set proper environment variables for production
- Use production-grade database (PostgreSQL) instead of SQLite
- Enable HTTPS for WebSocket connections
- Configure proper CORS origins
- Add rate limiting for API endpoints
- Implement proper authentication (remove dev mode)

## Contributing

1. Create feature branch from `main`
2. Make changes with clear commits
3. Test thoroughly
4. Update documentation if needed
5. Submit pull request with description

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Socket.IO Docs](https://socket.io/docs/v4/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [React Docs](https://react.dev/)

---

For basic setup instructions, see the main [README.md](../README.md)