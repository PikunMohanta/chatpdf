# PDFPixie - Single Service Alternative

This directory contains configuration for deploying both frontend and backend as a single service.

## Why Single Service?

**Pros:**
- Simpler deployment and management
- No CORS issues (same origin)
- Easier URL management
- Lower cost (one service instead of two)
- Shared persistent storage

**Cons:**
- Frontend can't use CDN optimizations
- Mixed concerns (static files + API)
- Harder to scale independently
- Frontend rebuilds require backend restart

## Single Service Setup

### Option 1: FastAPI Serving Static Files

Update `backend/main.py` to serve the built frontend:

```python
from fastapi.staticfiles import StaticFiles

# After creating the FastAPI app
app.mount("/", StaticFiles(directory="./frontend/dist", html=True), name="static")
```

### Option 2: Use the unified deployment config

See `render-unified.yaml` for a single service that builds both frontend and backend.

## Migration from Two Services

If you want to switch to single service:

1. Delete your current frontend static site in Render
2. Use the unified configuration
3. Update your backend to serve static files
4. No need for separate VITE_API_URL (use relative paths)

Choose based on your needs:
- **Two services**: Better for scaling, more complex setup
- **Single service**: Simpler, more traditional web app approach