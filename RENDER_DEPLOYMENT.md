# PDFPixie Render Deployment Guide

This guide will help you deploy PDFPixie to Render.com with proper configuration.

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure you're on the `render` branch with all the deployment changes:

```bash
git checkout render
git add .
git commit -m "Configure for Render deployment"
git push origin render
```

### 2. Deploy Backend Service

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the backend service:**

   - **Name**: `pdfpixie-backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `render`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT`

5. **Set Environment Variables:**
   ```
   ENVIRONMENT=production
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   PYTHON_VERSION=3.10.0
   ```

6. **Click "Create Web Service"**

### 3. Deploy Frontend Service

1. **Click "New +" → "Static Site"**
2. **Connect your GitHub repository**
3. **Configure the frontend service:**

   - **Name**: `pdfpixie-frontend`
   - **Branch**: `render`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Set Environment Variables:**
   ```
   NODE_VERSION=18.17.0
   VITE_API_URL=https://pdfpixie-backend.onrender.com
   ```

5. **Click "Create Static Site"**

## 🔧 Important Configuration Notes

### Backend Configuration
- **Port**: Automatically set by Render via `$PORT` environment variable
- **Database**: Uses SQLite stored in `/tmp` (temporary but sufficient for demo)
- **File Storage**: Files stored in `/tmp/pdfpixie` (temporary)
- **CORS**: Configured to allow requests from your frontend domain

### Frontend Configuration
- **API URL**: Set via `VITE_API_URL` environment variable
- **Build**: Uses Vite for optimized production build
- **Routing**: Configured for single-page application

### Environment Variables Required

**Backend (.env or Render environment):**
```env
ENVIRONMENT=production
OPENROUTER_API_KEY=your_api_key
PORT=10000  # Set automatically by Render
```

**Frontend (.env.production or Render environment):**
```env
VITE_API_URL=https://your-backend-url.onrender.com
NODE_ENV=production
```

## 🛠️ Post-Deployment Setup

### 1. Update CORS Origins
After deployment, update the backend CORS configuration with your actual frontend URL:

1. Go to your backend service in Render
2. Update the environment variable or code to include your frontend URL
3. Redeploy if necessary

### 2. Test the Deployment
1. Visit your frontend URL
2. Try uploading a PDF
3. Test the chat functionality
4. Check the logs in Render dashboard for any errors

## 📁 File Structure for Deployment

```
PDFPixie/
├── backend/                 # Backend service root
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── app/               # Application modules
├── frontend/               # Frontend service root
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.ts     # Vite configuration
│   └── src/              # React source code
├── render.yaml            # Render configuration (optional)
├── Procfile              # Process configuration
└── README.md
```

## 🔐 Security Considerations

### Environment Variables
- **Never commit API keys** to the repository
- Use Render's environment variable settings
- Keep production and development configs separate

### Database
- Current setup uses SQLite in `/tmp` (temporary storage)
- For production, consider upgrading to Render's PostgreSQL
- Data will be lost on service restarts with current setup

### CORS
- Frontend and backend domains must be properly configured
- Wildcard CORS (`*`) disabled in production

## 🚨 Troubleshooting

### Common Issues

**Backend fails to start:**
- Check Python version (should be 3.10+)
- Verify all dependencies in requirements.txt
- Check environment variables are set
- Review build logs in Render dashboard

**Frontend can't connect to backend:**
- Verify `VITE_API_URL` is correct
- Check CORS configuration in backend
- Ensure both services are running
- Check network requests in browser dev tools

**Database errors:**
- Verify `/tmp` directory permissions
- Check if database initialization ran successfully
- Review backend logs for SQLite errors

**File upload issues:**
- Check file size limits
- Verify `/tmp/pdfpixie` directory creation
- Review storage permissions

### Useful Commands

**Check backend logs:**
```bash
# In Render dashboard -> Backend Service -> Logs
```

**Test API directly:**
```bash
curl https://your-backend-url.onrender.com/health
```

**Local testing with production config:**
```bash
# Backend
cd backend
ENVIRONMENT=production python main.py

# Frontend
cd frontend
VITE_API_URL=https://your-backend-url.onrender.com npm run build
npm run preview
```

## 🎯 Next Steps

1. **Custom Domain**: Configure custom domains for both services
2. **Database Upgrade**: Move to Render PostgreSQL for persistent storage
3. **Monitoring**: Set up error tracking and performance monitoring
4. **SSL**: Ensure HTTPS is properly configured
5. **CDN**: Consider using a CDN for static assets

## 📞 Support

If you encounter issues:
1. Check Render documentation
2. Review deployment logs
3. Test locally with production environment variables
4. Check this guide for common solutions

Your PDFPixie application should now be successfully deployed on Render! 🎉