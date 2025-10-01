# 🔧 Chat Not Working - Complete Fix Guide

## ✅ **ROOT CAUSE IDENTIFIED**

The chat wasn't working because the backend was being run with:
```bash
uvicorn main:app --reload    # ❌ WRONG - No Socket.IO support
```

Instead of:
```bash
uvicorn main:socket_app --reload    # ✅ CORRECT - Includes Socket.IO
```

## The Problem Explained

In `backend/main.py`, there are TWO ASGI applications:

1. **`app`** - Plain FastAPI app (REST API only)
   ```python
   app = FastAPI(...)
   ```

2. **`socket_app`** - FastAPI + Socket.IO combined
   ```python
   socket_app = socketio.ASGIApp(sio, app)
   ```

### What Happens with Each:

| Command | WebSocket | REST API | Chat Works? |
|---------|-----------|----------|-------------|
| `uvicorn main:app` | ❌ No | ✅ Yes | ❌ No |
| `uvicorn main:socket_app` | ✅ Yes | ✅ Yes | ✅ Yes |

## Complete Fix Steps

### 1. Stop Any Running Backend
```powershell
Stop-Process -Name uvicorn -Force
# Or press Ctrl+C in the backend terminal
```

### 2. Start Backend with Socket.IO
```powershell
cd D:\my\chatpdf\backend
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
```

**Important:** Notice `main:socket_app` not `main:app`

### 3. Verify Backend is Running Correctly
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Server initialized for asgi.    ← This confirms Socket.IO is loaded!
INFO:     Application startup complete.
```

### 4. Start Frontend
```powershell
cd D:\my\chatpdf\frontend
npm run dev
```

### 5. Test the Chat

#### Option A: Use the Frontend
1. Open http://localhost:3001
2. Upload a PDF
3. Check status indicator: Should show **"Connected"** with green dot
4. Type a message and send
5. You should see typing indicator and then AI response

#### Option B: Use Test Page
1. Open `test_chat_live.html` in your browser
2. Click "Connect" button
3. Should show "✅ Connected"
4. Enter a document ID and question
5. Click "Send Query"
6. Check console logs for response

## Quick Startup Scripts

### Windows PowerShell
```powershell
# Use the provided script
.\start_servers.ps1

# Or manually:
# Terminal 1 - Backend
cd backend
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### Batch File (Windows)
```batch
# Use the provided batch file
start_server.bat
```

## Troubleshooting Checklist

### ✅ Backend Issues

**Q: Backend starts but chat shows "Disconnected"**
- Check if you used `main:socket_app` (correct) or `main:app` (wrong)
- Look for "Server initialized for asgi" in backend logs
- If missing, you're running the wrong app

**Q: "Connection refused" or "Cannot connect"**
- Verify backend is on port 8000: `curl http://localhost:8000/health`
- Check firewall settings
- Try http://127.0.0.1:8000 instead

**Q: Backend crashes on startup**
- Check `.env` file exists in `backend/` folder
- Verify Python version: `python --version` (need 3.10+)
- Reinstall dependencies: `uv pip install -r requirements.txt`

### ✅ Frontend Issues

**Q: Frontend won't start**
- PowerShell execution policy issue: Use the provided scripts
- Or run: `& "C:\Program Files\nodejs\node.exe" "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" run dev`

**Q: Frontend shows "Disconnected" status**
- Check browser console (F12) for errors
- Verify `frontend/.env` has correct URLs:
  ```
  VITE_API_URL=http://localhost:8000
  VITE_SOCKET_URL=http://localhost:8000
  ```
- Backend must be running with `socket_app`

**Q: PDF uploads but chat doesn't work**
- This is the classic "main:app vs main:socket_app" issue
- Restart backend with correct command

### ✅ Chat Functionality

**Q: Status shows "Connected" but no response**
- Check backend terminal for errors
- Look for "Received query from..." log
- Check if OpenRouter API key is set (optional, will use mock otherwise)
- Verify document was uploaded successfully

**Q: "Error: Missing query or document_id"**
- Make sure PDF is uploaded first
- Check document ID is being passed correctly
- Try refreshing the page

**Q: Slow responses or timeouts**
- Check network tab in browser (F12)
- Verify OpenRouter API key is valid
- May be using mock mode (slower, basic responses)

## Environment Variables

### Backend `.env` (Required)
```bash
# API Keys (optional for basic testing)
OPENROUTER_API_KEY=your-key-here

# Server Config
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

### Frontend `.env` (Required)
```bash
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

## Verification Steps

### 1. Check Backend Health
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"newchat-api"}
```

### 2. Check Socket.IO Endpoint
```powershell
curl http://localhost:8000/socket.io/
# Should return Socket.IO handshake data
```

### 3. Test WebSocket Connection
Open browser console on http://localhost:3001 and run:
```javascript
const socket = io('http://localhost:8000');
socket.on('connect', () => console.log('Connected!', socket.id));
socket.on('connected', (data) => console.log('Server says:', data));
```

Should see:
```
Connected! <some-socket-id>
Server says: {message: "Connected to Newchat"}
```

### 4. Test Query Event
```javascript
socket.emit('query', {
    document_id: 'test-doc',
    query: 'What is this about?'
});

socket.on('response', (data) => {
    console.log('AI Response:', data.message);
});
```

## Common Mistakes

1. ❌ **Running `uvicorn main:app` instead of `uvicorn main:socket_app`**
   - This is the #1 issue!
   - Always use `socket_app`

2. ❌ **Not activating virtual environment**
   - Use `uv run` prefix or activate venv first

3. ❌ **Frontend and backend on wrong ports**
   - Backend: 8000
   - Frontend: 3001 (or 3000)

4. ❌ **Missing .env files**
   - Both frontend and backend need them

5. ❌ **CORS errors**
   - Check `main.py` allows your frontend port
   - Currently allows: 3000, 3001, 127.0.0.1:3000, 127.0.0.1:3001

## Expected Behavior

### When Everything Works:

1. **Upload PDF**
   ```
   Backend Log: INFO: Processing file: example.pdf
   Backend Log: INFO: Saved to local storage: data/uploads/...
   Frontend: Shows "✅ example.pdf uploaded successfully"
   ```

2. **Connect to Chat**
   ```
   Backend Log: INFO: Client <socket-id> connected
   Frontend: Status shows "Connected" with green dot
   ```

3. **Send Message**
   ```
   User: "What is this document about?"
   Backend Log: INFO: Received query from <sid>: What is...
   Backend Log: INFO: Found 3 relevant chunks from mock embeddings
   Backend Log: INFO: Generated response for <sid>: Based on...
   Frontend: Shows typing indicator → AI response
   ```

## Debug Mode

### Enable Verbose Logging

**Backend** - Already enabled in `main.py`:
```python
logger=True,
engineio_logger=True
```

**Frontend** - Add to browser console:
```javascript
localStorage.debug = 'socket.io-client:socket';
```

Reload page to see detailed Socket.IO logs.

## Still Not Working?

1. **Check Backend Logs**: Look for errors in the terminal
2. **Check Browser Console**: Press F12, look for red errors
3. **Use Test Page**: Open `test_chat_live.html` for isolated testing
4. **Verify Socket.IO**: Check if `http://localhost:8000/socket.io/` responds
5. **Restart Everything**: Kill all processes and start fresh

## Working Example URLs

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Socket.IO**: http://localhost:8000/socket.io/
- **Test Page**: file:///D:/my/chatpdf/test_chat_live.html

## Key Takeaway

**The chat works perfectly when you run the backend with:**
```bash
uvicorn main:socket_app --reload
```

**Not with:**
```bash
uvicorn main:app --reload
```

That's it! The socket_app includes both the REST API and Socket.IO, which is required for real-time chat. 🚀
