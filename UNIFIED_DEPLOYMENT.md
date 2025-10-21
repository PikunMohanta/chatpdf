# PDFPixie - Unified Single Service Deployment Guide

## 🚀 **What Changed?**

You've successfully switched from **two separate services** to **one unified service** that serves both your API and frontend from a single deployment.

### **Before (Two Services):**
```
Frontend Service (Static Site) ←→ Backend Service (Web Service)
     ↓                                ↓
   React App                      FastAPI + Socket.IO
   (Static Files)                 (Python API)
```

### **After (Unified Service):**
```
Single Service: FastAPI + React
         ↓
FastAPI serves both API + Static Files
```

## ✅ **Benefits of Unified Deployment**

- ✅ **No CORS Issues** - Everything is same origin
- ✅ **Simpler Deployment** - One service instead of two
- ✅ **Lower Cost** - Single service pricing
- ✅ **Easier URL Management** - No need for `VITE_API_URL`
- ✅ **Persistent Storage** - Built-in disk support

## 🛠️ **Deployment Instructions**

### **Step 1: Delete Old Services (Optional but Recommended)**

In your Render Dashboard:
1. **Delete your existing frontend static site**
2. **Keep or delete your backend service** (we'll create a new unified one)

### **Step 2: Create New Unified Service**

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository: `PikunMohanta/chatpdf`**
4. **Select the `render` branch**

### **Step 3: Configure the Service**

**Basic Configuration:**
- **Name**: `pdfpixie-unified`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `render`
- **Root Directory**: Leave empty (use project root)

**Build & Start Commands:**
- **Build Command**: 
  ```bash
  cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist ../backend/static
  ```
- **Start Command**: 
  ```bash
  cd backend && python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT
  ```

**Environment Variables:**
```
PYTHON_VERSION=3.10.0
NODE_VERSION=18.17.0
ENVIRONMENT=production
OPENROUTER_API_KEY=your_actual_api_key_here
```

### **Step 4: Add Persistent Storage**

**In the service configuration:**
1. **Go to "Storage" tab**
2. **Add Disk:**
   - **Name**: `pdfpixie-data`
   - **Mount Path**: `/opt/render/project/data`
   - **Size**: `1 GB`

### **Step 5: Deploy**

Click **"Create Web Service"** and wait for deployment to complete.

## 🔧 **Technical Details**

### **How It Works**

1. **Build Process**:
   - Installs Python dependencies
   - Installs Node.js dependencies  
   - Builds React frontend with Vite
   - Copies built files to `backend/static/`

2. **Runtime**:
   - FastAPI serves API routes (`/api/*`, `/socket.io/*`)
   - FastAPI serves static files for all other routes
   - Single-page app routing handled by serving `index.html`

3. **URL Structure**:
   ```
   https://pdfpixie-unified.onrender.com/          → React App
   https://pdfpixie-unified.onrender.com/api/      → API Endpoints
   https://pdfpixie-unified.onrender.com/socket.io → WebSocket
   https://pdfpixie-unified.onrender.com/docs      → API Documentation
   ```

### **Configuration Changes Made**

**Backend (`main.py`):**
- ✅ Added static file serving
- ✅ Removed CORS (not needed for same origin)
- ✅ Added SPA routing support
- ✅ Serves `index.html` for non-API routes

**Frontend (`config.ts`):**
- ✅ Uses relative URLs in production
- ✅ Removed dependency on `VITE_API_URL`
- ✅ Same-origin requests

**Build System:**
- ✅ Unified build script (`build-unified.bat/sh`)
- ✅ Copies frontend to `backend/static/` 
- ✅ Single deployment artifact

## 🧪 **Testing Your Deployment**

After deployment completes:

1. **Visit your service URL**: `https://pdfpixie-unified.onrender.com`
2. **Upload a PDF** - should work without CORS errors
3. **Refresh the page** - should not break (SPA routing)
4. **Chat with document** - should save properly (persistent storage)
5. **Check API docs**: `https://pdfpixie-unified.onrender.com/docs`

## 🐛 **Troubleshooting**

### **Build Fails**
- Check that both Python and Node.js versions are set
- Verify all dependencies in `requirements.txt` and `package.json`

### **Static Files Not Loading**
- Check that `backend/static/` directory exists after build
- Verify that `index.html` is in `backend/static/`

### **API Not Working**
- Check that API routes still work: `/docs`, `/health`
- Verify environment variables are set

### **Chat Not Saving**
- Ensure persistent disk is mounted at `/opt/render/project/data`
- Check logs for database initialization errors

## 🎯 **Local Development**

For local development, use the unified build:

```bash
# Build frontend into backend
./build-unified.bat  # Windows
# or
./build-unified.sh   # Linux/Mac

# Start unified server
cd backend
python main.py
```

Your app will be available at `http://localhost:8000` with both frontend and API.

## 🔄 **Rollback Plan**

If you need to go back to two services:

1. **Use the old `RENDER_DEPLOYMENT.md` guide**
2. **Revert these commits**:
   ```bash
   git revert HEAD~1  # Revert unified changes
   git push origin render
   ```
3. **Deploy frontend and backend separately**

## 🎉 **Success!**

Your PDFPixie application is now running as a unified service with:
- ✅ Single service deployment
- ✅ No CORS issues  
- ✅ Persistent storage
- ✅ Simplified architecture
- ✅ Better reliability

Enjoy your streamlined deployment! 🚀