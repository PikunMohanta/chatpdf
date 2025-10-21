# PDFPixie - Vercel + Railway Deployment Guide

## 🚀 **Architecture Overview**

**Best of Both Worlds: Global CDN + Persistent Storage**

```
Frontend (Vercel)        Backend (Railway)
   ↓                         ↓
React App              FastAPI + Socket.IO
Global CDN             PostgreSQL Database
Instant Loading        Persistent Volumes
```

### **Why This Architecture?**

- ✅ **Frontend on Vercel**: Global CDN, instant loading, free SSL
- ✅ **Backend on Railway**: Persistent storage, PostgreSQL, WebSockets
- ✅ **Best Performance**: Frontend cached globally, backend with database
- ✅ **100% Free Tier**: Both platforms offer generous free tiers

---

## 📋 **Prerequisites**

- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))
- Railway account (sign up at [railway.app](https://railway.app))
- Your code pushed to GitHub `render` branch

---

## 🛤️ **Part 1: Deploy Backend to Railway**

### **Step 1: Create Railway Account**

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway

### **Step 2: Deploy Backend**

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository**: `PikunMohanta/chatpdf`
4. **Select branch**: `render`
5. **Configure root directory**: Click "Settings" → Set root directory to `backend`

### **Step 3: Add PostgreSQL Database**

1. In your Railway project, click **"+ New"**
2. Select **"Database" → "Add PostgreSQL"**
3. Railway will automatically create a database and set `DATABASE_URL` environment variable

### **Step 4: Add Persistent Volume (Optional but Recommended)**

1. In your backend service, go to **"Settings"**
2. Scroll to **"Volumes"**
3. Click **"+ New Volume"**
   - **Mount Path**: `/data`
   - **Size**: `1 GB` (free tier)

### **Step 5: Configure Environment Variables**

In Railway backend service → **"Variables"** tab:

```env
ENVIRONMENT=production
OPENROUTER_API_KEY=your_openrouter_api_key_here
PYTHON_VERSION=3.10
```

**Note:** `DATABASE_URL` and `PORT` are automatically set by Railway

### **Step 6: Deploy**

1. Railway will automatically deploy your backend
2. Wait for deployment to complete (2-3 minutes)
3. **Copy your backend URL**: `https://your-project.up.railway.app`

---

## 🎨 **Part 2: Deploy Frontend to Vercel**

### **Step 1: Create Vercel Account**

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel

### **Step 2: Import Project**

1. Click **"Add New..." → "Project"**
2. **Import your GitHub repository**: `PikunMohanta/chatpdf`
3. Vercel will detect it as a Vite project

### **Step 3: Configure Build Settings**

**Framework Preset**: Vite  
**Root Directory**: `frontend`  
**Build Command**: `npm run build`  
**Output Directory**: `dist`  
**Install Command**: `npm install`

### **Step 4: Add Environment Variable**

In **"Environment Variables"** section:

```env
VITE_API_URL=https://your-railway-backend-url.up.railway.app
```

**Replace with your actual Railway backend URL from Part 1, Step 6**

### **Step 5: Deploy**

1. Click **"Deploy"**
2. Wait for deployment (1-2 minutes)
3. Your frontend will be live at: `https://your-project.vercel.app`

---

## 🔧 **Part 3: Configure CORS**

### **Update Backend CORS Origins**

You need to update your Railway backend to allow requests from Vercel:

1. **Go to Railway** → Your backend service → **"Variables"**
2. **Add new variable**:
   ```env
   FRONTEND_URL=https://your-project.vercel.app
   ```

Then update `backend/main.py` CORS settings to use this variable:

```python
# In main.py, replace the hardcoded Vercel URL with:
allowed_origins = [
    os.getenv("FRONTEND_URL", "https://chatpdf-frontend.vercel.app"),
    "https://*.vercel.app",  # Allow all Vercel preview deployments
    "http://localhost:3000",
    "http://localhost:5173",
]
```

**Or simply update the hardcoded URL in the code:**
- Line 27 in `main.py`: Replace `https://chatpdf-frontend.vercel.app` with your actual Vercel URL
- Line 51 in `main.py`: Same replacement for Socket.IO CORS

---

## ✅ **Testing Your Deployment**

### **1. Test Backend (Railway)**

Visit: `https://your-railway-url.up.railway.app/docs`

You should see the FastAPI Swagger documentation.

### **2. Test Frontend (Vercel)**

Visit: `https://your-project.vercel.app`

You should see the PDFPixie upload screen.

### **3. Test Full Flow**

1. Upload a PDF document
2. Ask a question about the document
3. Verify chat responses work
4. Refresh the page - should stay on the same page
5. Check if chat history persists after page reload

---

## 🎯 **Environment Variables Reference**

### **Railway (Backend)**

```env
# Automatically set by Railway
DATABASE_URL=postgresql://...
PORT=8000

# You need to set these
ENVIRONMENT=production
OPENROUTER_API_KEY=your_api_key
FRONTEND_URL=https://your-project.vercel.app
```

### **Vercel (Frontend)**

```env
# You need to set this
VITE_API_URL=https://your-railway-url.up.railway.app
```

---

## 🔄 **Continuous Deployment**

### **Automatic Deployments**

Both platforms support auto-deploy on git push:

**Railway:**
- Automatically redeploys backend on push to `render` branch
- Configure in Settings → "Deployments"

**Vercel:**
- Automatically redeploys frontend on push to `render` branch
- Creates preview deployments for PRs

### **Manual Deployments**

**Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Vercel:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy frontend
cd frontend
vercel --prod
```

---

## 🐛 **Troubleshooting**

### **Issue: Frontend Can't Connect to Backend**

**Solution:**
1. Check `VITE_API_URL` in Vercel is correct
2. Verify CORS settings in backend include your Vercel URL
3. Check backend is running: visit `/docs` endpoint

### **Issue: Database Connection Error**

**Solution:**
1. Verify `DATABASE_URL` is set in Railway
2. Check PostgreSQL service is running in Railway
3. Review logs: Railway → Backend service → "Deployments" → View logs

### **Issue: Chat Not Saving**

**Solution:**
1. Verify PostgreSQL database is attached
2. Check database migrations ran successfully
3. Review backend logs for database errors

### **Issue: CORS Error**

**Solution:**
1. Update `allowed_origins` in `backend/main.py` with your Vercel URL
2. Redeploy backend after changes
3. Clear browser cache and try again

### **Issue: 404 on Page Refresh (Vercel)**

**Solution:**
- Verify `vercel.json` has the rewrite rule (already configured)
- Check that `dist` directory has `index.html` after build

---

## 💰 **Cost Breakdown (Free Tier)**

### **Railway Free Tier**
- ✅ **$5 credit/month** (about 500 hours of usage)
- ✅ **PostgreSQL included**
- ✅ **1 GB persistent volume**
- ✅ **Shared CPU**

### **Vercel Free Tier**
- ✅ **100 GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **Global CDN**
- ✅ **Preview deployments**

**Total Monthly Cost: $0** 🎉

---

## 🚀 **Performance Optimization**

### **Frontend (Vercel)**
- ✅ Automatically optimized by Vercel
- ✅ Global CDN caching
- ✅ Compressed assets
- ✅ HTTP/2 and brotli compression

### **Backend (Railway)**
- ⚡ Keep connections alive with persistent DB
- ⚡ Use Railway's persistent volume for file caching
- ⚡ Optimize database queries
- ⚡ Consider Redis for session caching (Railway add-on)

---

## 📊 **Monitoring**

### **Railway Dashboard**
- View real-time logs
- Monitor CPU and memory usage
- Check deployment history
- Database connection stats

### **Vercel Dashboard**
- Analytics and performance metrics
- Deployment logs
- Build times
- Bandwidth usage

---

## 🔐 **Security Best Practices**

1. ✅ **Environment Variables**: Never commit API keys
2. ✅ **CORS**: Only allow your Vercel domain
3. ✅ **HTTPS**: Both platforms provide free SSL
4. ✅ **Database**: Railway PostgreSQL has SSL by default
5. ✅ **API Keys**: Rotate OpenRouter API key regularly

---

## 🎉 **Success Checklist**

- [ ] Backend deployed to Railway with PostgreSQL
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured on both platforms
- [ ] CORS settings updated with correct URLs
- [ ] Test PDF upload and chat functionality
- [ ] Verify chat history persists after refresh
- [ ] Check API documentation is accessible
- [ ] Test page refresh doesn't break SPA routing

---

## 🔗 **Useful Links**

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Your Frontend**: https://your-project.vercel.app
- **Your Backend API**: https://your-railway-url.up.railway.app/docs
- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard

---

## 🆘 **Need Help?**

1. **Check logs** in Railway and Vercel dashboards
2. **Review this guide** for common issues
3. **Test locally** first: 
   ```bash
   # Backend
   cd backend
   python main.py

   # Frontend
   cd frontend
   VITE_API_URL=http://localhost:8000 npm run dev
   ```

---

## 🎯 **Next Steps**

1. **Custom Domain**: Add your own domain in Vercel/Railway
2. **Redis Caching**: Add Redis on Railway for better performance
3. **Monitoring**: Set up error tracking (Sentry, LogRocket)
4. **Analytics**: Add analytics to track usage
5. **CI/CD**: Add GitHub Actions for automated testing

**Congratulations! Your PDFPixie is now live! 🚀**