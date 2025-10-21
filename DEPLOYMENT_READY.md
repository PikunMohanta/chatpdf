# 🎉 PDFPixie - Ready for Vercel + Railway Deployment!

## ✅ **Configuration Complete**

Your project is now configured for optimal split deployment with:
- **Frontend on Vercel** (Global CDN)
- **Backend on Railway** (PostgreSQL + Persistent Storage)

## 📋 **Quick Start Guide**

### **1. Deploy Backend to Railway** (5 minutes)

1. Go to [railway.app](https://railway.app) → Login with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `PikunMohanta/chatpdf` → Branch: `render`
4. Set root directory to: `backend`
5. Add PostgreSQL: Click "+ New" → "Database" → "PostgreSQL"
6. Add environment variables:
   ```
   ENVIRONMENT=production
   OPENROUTER_API_KEY=your_key_here
   ```
7. Copy your Railway backend URL (looks like: `https://xxx.up.railway.app`)

### **2. Deploy Frontend to Vercel** (3 minutes)

1. Go to [vercel.com](https://vercel.com) → Login with GitHub
2. Click "Add New" → "Project"
3. Import `PikunMohanta/chatpdf`
4. Set root directory to: `frontend`
5. Add environment variable:
   ```
   VITE_API_URL=https://your-railway-url.up.railway.app
   ```
6. Click "Deploy"

### **3. Update CORS** (2 minutes)

After Vercel deployment completes:

1. Copy your Vercel URL (looks like: `https://xxx.vercel.app`)
2. Go to Railway → Your backend → "Variables"
3. Add: `FRONTEND_URL=https://your-vercel-url.vercel.app`
4. Or manually update `backend/main.py` lines 27 and 51 with your Vercel URL

### **4. Test** ✅

Visit your Vercel URL and:
- Upload a PDF
- Ask questions about it
- Verify chat saves after page refresh

## 📚 **Full Documentation**

See `VERCEL_RAILWAY_DEPLOYMENT.md` for complete step-by-step guide with:
- Detailed setup instructions
- Troubleshooting guide
- Performance optimization tips
- Cost breakdown
- Security best practices

## 🆘 **Quick Troubleshooting**

**Frontend can't connect to backend?**
- Check `VITE_API_URL` in Vercel matches your Railway URL
- Verify CORS allows your Vercel domain

**Database errors?**
- Ensure PostgreSQL is added in Railway
- Check `DATABASE_URL` is automatically set

**Chat not saving?**
- Verify PostgreSQL database is running
- Check backend logs in Railway dashboard

## 🎯 **What's Configured**

✅ Vercel configuration (`frontend/vercel.json`)  
✅ Railway configuration (`backend/railway.json`, `nixpacks.toml`)  
✅ PostgreSQL support (`psycopg2-binary` in requirements.txt)  
✅ CORS configured for Vercel ↔ Railway  
✅ Environment-based config (dev uses SQLite, prod uses PostgreSQL)  
✅ SPA routing support on Vercel  
✅ Persistent volumes on Railway  

## 🚀 **Ready to Deploy!**

Your code is committed and pushed to the `render` branch. 

Follow the Quick Start Guide above or read the full documentation in `VERCEL_RAILWAY_DEPLOYMENT.md`.

**Good luck! 🎉**