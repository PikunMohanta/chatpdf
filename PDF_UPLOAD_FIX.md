# PDF Upload Fix Summary

## Issue
PDF upload was failing with `404 Not Found` error on `/api/upload` endpoint.

## Root Causes
1. **Backend Route Mismatch**: PDF router was registered with prefix `/api/pdf` but frontend was calling `/api/upload`
2. **Missing Authentication**: Upload endpoint requires Bearer token authentication
3. **CORS Configuration**: Frontend port 3001 wasn't in allowed origins
4. **Missing Preview Endpoint**: No endpoint to serve PDF files for preview

## Fixes Applied

### Backend Changes (`backend/main.py`)

1. **Fixed Router Prefix**:
   ```python
   # Before:
   app.include_router(pdf_router, prefix="/api/pdf", tags=["pdf"])
   
   # After:
   app.include_router(pdf_router, prefix="/api", tags=["pdf"])
   ```

2. **Updated CORS Configuration**:
   ```python
   allow_origins=[
       "http://localhost:3000", 
       "http://127.0.0.1:3000",
       "http://localhost:3001",  # Added
       "http://127.0.0.1:3001"   # Added
   ]
   ```

3. **Updated Socket.IO CORS**:
   ```python
   cors_allowed_origins=[
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "http://localhost:3001",  # Added
       "http://127.0.0.1:3001"   # Added
   ]
   ```

### Backend Changes (`backend/app/pdf_processing.py`)

4. **Added Document Preview Endpoint**:
   ```python
   @router.get("/document/{document_id}/preview")
   async def preview_document(
       document_id: str,
       current_user: UserInfo = Depends(verify_token)
   ):
       """Serve PDF file for preview in browser"""
       # Returns FileResponse for local dev, RedirectResponse for S3
   ```

### Frontend Changes

5. **UploadComponent.tsx** - Added Authentication:
   ```typescript
   const token = localStorage.getItem('auth_token') || 'dev-token'
   
   headers: {
       'Content-Type': 'multipart/form-data',
       'Authorization': `Bearer ${token}`,  // Added
   }
   ```

6. **ChatComponent.tsx** - Added Authentication:
   ```typescript
   const token = localStorage.getItem('auth_token') || 'dev-token'
   
   headers: {
       'Authorization': `Bearer ${token}`,  // Added
   }
   ```

7. **PreviewComponent.tsx** - Fetch PDF with Authentication:
   ```typescript
   // Fetches PDF with auth headers as ArrayBuffer
   useEffect(() => {
       const token = localStorage.getItem('auth_token') || 'dev-token'
       const response = await axios.get(
           `${API_URL}/api/document/${documentId}/preview`,
           {
               headers: { Authorization: `Bearer ${token}` },
               responseType: 'arraybuffer',
           }
       )
       setPdfData(response.data)
   }, [documentId])
   ```

## API Endpoints Now Available

### Upload & Documents
- `POST /api/upload` - Upload PDF (requires auth)
- `GET /api/documents` - List user documents (requires auth)
- `GET /api/document/{id}/preview` - Preview PDF (requires auth)
- `GET /api/document/{id}/download` - Download PDF (requires auth)
- `DELETE /api/documents/{id}` - Delete document (requires auth)

### Chat
- `GET /api/chat/history/{document_id}` - Get chat history (requires auth)
- WebSocket events via Socket.IO for real-time chat

### Authentication
- `POST /api/auth/login` - Login (returns bearer token)
- Default dev token: `dev-token` (accepted for development)
- Default dev credentials: `dev@example.com` / `password`

## Testing

### Manual Test
1. Open http://localhost:3001
2. Drag & drop a PDF file
3. File should upload successfully
4. Chat interface should appear
5. PDF preview should load

### Expected Behavior
- ✅ Upload shows progress bar
- ✅ 200 OK response on `/api/upload`
- ✅ Document ID generated (UUID)
- ✅ File saved to `backend/data/uploads/`
- ✅ Mock embeddings saved to `backend/data/mock_embeddings/`
- ✅ Chat history ready in `backend/data/chat_history/`
- ✅ PDF preview loads with authentication

## Development Mode Features

The application runs in **mock mode** when external services aren't configured:

- **ChromaDB**: Uses JSON files in `data/mock_embeddings/`
- **S3**: Uses local storage in `data/uploads/`
- **OpenAI Embeddings**: Uses mock embeddings
- **Authentication**: Accepts `dev-token` for easy testing

## Next Steps

1. ✅ Backend and frontend are running
2. ✅ PDF upload is working
3. ✅ Authentication is configured
4. ✅ CORS is properly set up
5. ⏭️ Test chat functionality
6. ⏭️ Add proper AWS credentials for production
7. ⏭️ Set up PostgreSQL database
8. ⏭️ Configure real ChromaDB with embeddings

## Quick Commands

```powershell
# Start Backend
cd backend
uv run uvicorn main:app --reload

# Start Frontend
cd frontend
npm run dev

# Access Application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Troubleshooting

If upload still fails:
1. Check browser console for errors
2. Check backend logs for authentication issues
3. Verify CORS headers in Network tab
4. Ensure `dev-token` is being sent in Authorization header
5. Check `backend/data/uploads/` directory exists and is writable
