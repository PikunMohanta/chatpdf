# PDFPixie - Render + Supabase + Vercel Deployment Guide

## 🚀 **100% Free Deployment Architecture**

```
Frontend (Vercel)        Backend (Render)         Database (Supabase)      Storage (AWS S3)
   ↓                         ↓                         ↓                        ↓
React App              FastAPI + Socket.IO        PostgreSQL DB         PDF Files (Optional)
Global CDN             Free Web Service           500MB FREE            Pay-per-use
Instant Loading        Auto-deploy on push        Auto-backups          99.999999999% durable
```

### **Why Render + Supabase + Vercel?**

- ✅ **100% Free** - No credit card required
- ✅ **Persistent Database** - Supabase PostgreSQL (500MB free)
- ✅ **Optional S3 Storage** - For persistent file storage
- ✅ **WebSockets** - Full Socket.IO support
- ✅ **Global CDN** - Vercel's edge network
- ✅ **Auto-Deploy** - Push to GitHub to deploy

### **Trade-offs:**

| Feature | Status | Note |
|---------|--------|------|
| **Cost** | ✅ FREE | No payment method required |
| **Database** | ✅ 500MB | Supabase PostgreSQL |
| **File Storage** | ⚠️ Ephemeral | Use S3 for persistence |
| **Sleep Time** | ⚠️ 15 min | Wakes in ~30 seconds |
| **Performance** | ✅ Good | Great for learning/small apps |

---

## 📋 **Prerequisites**

- GitHub account
- Supabase account ([supabase.com](https://supabase.com))
- Render account ([render.com](https://render.com))
- Vercel account ([vercel.com](https://vercel.com))
- AWS account (optional - for S3 storage)
- Code pushed to GitHub `render` branch

---

## 🗄️ **Part 1: Setup Supabase Database (5 minutes)**

### **Step 1: Create Supabase Project**

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"** → **"Sign in with GitHub"**
3. Click **"New Project"**
4. Fill in details:
   - **Name**: `pdfpixie`
   - **Database Password**: (create a strong password - **SAVE THIS!**)
   - **Region**: `Southeast Asia (Singapore)`
   - **Pricing Plan**: `Free` (500MB database, no credit card)
5. Click **"Create new project"** (takes 2-3 minutes)

### **Step 2: Get Database Connection String**

1. In your Supabase project dashboard:
2. Go to **Settings** (gear icon) → **Database**
3. Scroll to **Connection string**
4. Select **URI** tab
5. Copy the connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. **Replace `[YOUR-PASSWORD]`** with the password you created in Step 1

postgresql://postgres:IZdlpwtluJRudGan@db.civvmgyopzblyqugyfbk.supabase.co:5432/postgres

**Save this URL - you'll need it for Render!**

### **Step 3: Create Database Tables (Optional)**

Tables will be auto-created by SQLAlchemy, but you can verify:

1. Go to **Table Editor** in Supabase
2. After first deployment, you should see tables like:
   - `chat_sessions`
   - `chat_messages`
   - `documents`

---

## ☁️ **Part 2: Setup AWS S3 (Optional - for persistent file storage)**

### **Step 1: Create S3 Bucket**

1. Go to [AWS Console](https://console.aws.amazon.com/s3/)
2. Click **"Create bucket"**
3. Configuration:
   - **Bucket name**: `pdfpixie-documents` (must be globally unique)
   - **Region**: `Asia Pacific (Singapore) ap-southeast-1`
   - **Block Public Access**: Keep all boxes **checked** (files are private)
4. Click **"Create bucket"**

### **Step 2: Create IAM User**

1. Go to **IAM** → **Users** → **Create user**
2. **User name**: `pdfpixie-app`
3. **Permissions**: Attach policy **"AmazonS3FullAccess"**
4. Click **"Create user"**

### **Step 3: Generate Access Keys**

1. Click on the user `pdfpixie-app`
2. Go to **Security credentials** tab
3. Click **"Create access key"**
4. Select **"Application running outside AWS"**
5. Click **"Next"** → **"Create access key"**
6. **SAVE THESE CREDENTIALS:**
   - `AWS_ACCESS_KEY_ID`: `AKIAIOSFODNN7EXAMPLE`
   - `AWS_SECRET_ACCESS_KEY`: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

**⚠️ Important:** You can only see the secret key once! Save it securely.

### **Step 4: Configure S3 CORS (for frontend uploads)**

1. Go to your S3 bucket → **Permissions** tab
2. Scroll to **Cross-origin resource sharing (CORS)**
3. Click **"Edit"** and paste:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST"],
        "AllowedOrigins": [
            "https://your-vercel-url.vercel.app",
            "http://localhost:5173"
        ],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```

4. **Replace `your-vercel-url.vercel.app`** with your actual Vercel URL (add after Vercel deployment)

---

## 🚢 **Part 3: Deploy Backend to Render (10 minutes)**

### **Step 1: Create Render Account**

1. Go to [render.com](https://render.com)
2. Click **"Get Started"** → **"Sign in with GitHub"**
3. Authorize Render

### **Step 2: Create New Web Service**

1. Click **"New +"** → **"Web Service"**
2. Connect your repository: `PikunMohanta/chatpdf`
3. Click **"Connect"**

### **Step 3: Configure Service**

**Basic Settings:**
- **Name**: `pdfpixie-backend`
- **Region**: `Singapore (Southeast Asia)`
- **Branch**: `render`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- **Plan**: `Free` (no credit card required!)

### **Step 4: Add Environment Variables**

Click **"Advanced"** → **Add Environment Variable**

**Required Variables:**
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
OPENROUTER_API_KEY=your_openrouter_api_key_here
FRONTEND_URL=http://localhost:5173
```

**Optional Variables (if using S3):**
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=pdfpixie-documents
```

**Replace:**
- `[PASSWORD]` with your Supabase database password
- `your_openrouter_api_key_here` with your actual OpenRouter API key
- AWS credentials with your actual keys (if using S3)

### **Step 5: Deploy**

1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. You'll see logs like:
   ```
   ==> Building...
   ==> Deploying...
   ==> Your service is live 🎉
   ```

### **Step 6: Get Your Render Backend URL**

Your URL will be:
```
https://pdfpixie-backend.onrender.com
```

**Copy this URL - you'll need it for Vercel!**

### **Step 7: Verify Backend is Running**

Visit: `https://pdfpixie-backend.onrender.com/health`

You should see:
```json
{"status": "healthy", "service": "pdfpixie-api"}
```

Visit: `https://pdfpixie-backend.onrender.com/docs`

You should see the FastAPI Swagger UI.

---

## 🎨 **Part 4: Deploy Frontend to Vercel (5 minutes)**

### **Step 1: Create Vercel Account**

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"** → **"Continue with GitHub"**
3. Authorize Vercel

### **Step 2: Import Repository**

1. Click **"Add New..."** → **"Project"**
2. Find your repository: `PikunMohanta/chatpdf`
3. Click **"Import"**

### **Step 3: Configure Project**

**Framework Preset:** Vite  
**Root Directory:** `frontend`  
**Build Command:** `npm run build` (auto-detected)  
**Output Directory:** `dist` (auto-detected)  
**Install Command:** `npm install` (auto-detected)

### **Step 4: Add Environment Variable**

In the **Environment Variables** section:

```env
VITE_API_URL=https://pdfpixie-backend.onrender.com
```

**Replace with your actual Render backend URL from Part 3, Step 6**

### **Step 5: Deploy**

1. Click **"Deploy"**
2. Wait for build and deployment (1-2 minutes)
3. Your frontend will be live at: `https://your-project.vercel.app`

**Copy your Vercel URL!**

---

## 🔧 **Part 5: Connect Frontend to Backend (Final Step)**

### **Step 1: Update Render with Vercel URL**

1. Go to Render Dashboard → Your service (`pdfpixie-backend`)
2. Go to **Environment** tab
3. Find `FRONTEND_URL` variable
4. Update to your Vercel URL:
   ```env
   FRONTEND_URL=https://your-project.vercel.app
   ```
5. Click **"Save Changes"**
6. Service will automatically redeploy

### **Step 2: Update S3 CORS (if using S3)**

1. Go to AWS S3 → Your bucket → **Permissions** → **CORS**
2. Update `AllowedOrigins` to include your Vercel URL:
   ```json
   "AllowedOrigins": [
       "https://your-project.vercel.app",
       "http://localhost:5173"
   ]
   ```

---

## ✅ **Testing Your Deployment**

### **1. Test Backend (Render)**

Visit: `https://pdfpixie-backend.onrender.com/health`

Expected response:
```json
{"status": "healthy", "service": "pdfpixie-api"}
```

### **2. Test API Documentation**

Visit: `https://pdfpixie-backend.onrender.com/docs`

You should see the FastAPI Swagger UI.

### **3. Test Frontend (Vercel)**

Visit: `https://your-project.vercel.app`

You should see the PDFPixie upload screen.

### **4. Test Full Integration**

1. **Upload a PDF document**
2. **Ask a question about the PDF**
3. **Verify the response appears**
4. **Refresh the page** - chat history should persist (from Supabase)
5. **Check database** - Go to Supabase → Table Editor to see data

---

## 🎯 **Environment Variables Reference**

### **Render (Backend)**

```env
# Required
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres
OPENROUTER_API_KEY=sk-or-v1-xxx
FRONTEND_URL=https://your-project.vercel.app

# Optional (for S3 persistent storage)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=pdfpixie-documents
```

### **Vercel (Frontend)**

```env
VITE_API_URL=https://pdfpixie-backend.onrender.com
```

### **Local Development**

**Backend `.env`:**
```env
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/database/chat_history.db
OPENROUTER_API_KEY=your_key_here
FRONTEND_URL=http://localhost:5173
```

**Frontend `.env.local`:**
```env
VITE_API_URL=http://localhost:8000
```

---

## 🔄 **Continuous Deployment**

### **Automatic Deployments**

**Render:**
- Automatically redeploys on push to `render` branch
- Zero configuration needed
- View logs in Render dashboard

**Vercel:**
- Automatically redeploys on push to `render` branch
- Creates preview deployments for PRs
- View logs in Vercel dashboard

### **Manual Deployments**

**Backend (Render):**
1. Go to Render Dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

**Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

---

## 💰 **Cost Breakdown (100% Free)**

### **Supabase Free Tier**
- ✅ **500MB PostgreSQL database**
- ✅ **1GB file storage** (if using Supabase Storage)
- ✅ **Unlimited API requests**
- ✅ **Automatic backups**
- ✅ **50,000 monthly active users**

### **Render Free Tier**
- ✅ **750 hours/month** (enough for 24/7)
- ✅ **100GB bandwidth/month**
- ✅ **Free SSL certificates**
- ⚠️ **Sleeps after 15 min inactivity** (wakes in ~30 sec)
- ⚠️ **No persistent disk** (use S3 or accept data loss)

### **Vercel Free Tier**
- ✅ **100GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **Global CDN**
- ✅ **Serverless functions**

### **AWS S3 (Optional)**
- ✅ **5GB free for 12 months** (new accounts)
- ✅ **20,000 GET requests/month**
- ✅ **2,000 PUT requests/month**
- 💰 **After free tier: ~$0.023/GB/month**

**Total Monthly Cost: $0-3** 💸

---

## 🚀 **Performance Optimization**

### **Handle Render Sleep Time**

Render free tier sleeps after 15 minutes. Add a ping service:

1. Go to [cron-job.org](https://cron-job.org)
2. Create free account
3. Add new cron job:
   - **URL**: `https://pdfpixie-backend.onrender.com/health`
   - **Interval**: Every 10 minutes
4. This keeps your service awake during active hours

### **Database Optimization**

```sql
-- Add indexes for faster queries
CREATE INDEX idx_session_user ON chat_sessions(user_id);
CREATE INDEX idx_message_session ON chat_messages(session_id);
CREATE INDEX idx_document_user ON documents(user_id);
```

### **S3 Optimization**

1. **Enable S3 Transfer Acceleration** for faster uploads
2. **Use CloudFront CDN** for faster downloads
3. **Set Lifecycle Policies** to delete old files

---

## 🐛 **Troubleshooting**

### **Issue: Frontend Can't Connect to Backend**

**Symptoms:**
- API requests fail
- CORS errors in browser console

**Check:**
1. Verify `VITE_API_URL` in Vercel matches your Render URL
2. Ensure `FRONTEND_URL` is set correctly in Render
3. Check CORS settings in `backend/main.py`

**Fix:**
```bash
# In Render Dashboard
FRONTEND_URL=https://your-actual-vercel-url.vercel.app

# Redeploy Render service
```

### **Issue: Database Connection Error**

**Symptoms:**
- Backend logs show "connection refused"
- 500 errors on API calls

**Check:**
```bash
# Verify Supabase connection string
# Should start with: postgresql://postgres:...
```

**Fix:**
1. Go to Supabase → Settings → Database
2. Copy the correct connection string
3. Update `DATABASE_URL` in Render
4. Ensure password is correct (no special URL encoding needed)

### **Issue: Service Sleeping Too Often**

**Fix:**
1. Set up cron job to ping `/health` every 10 minutes
2. Or upgrade to Render paid plan ($7/month for no sleep)

### **Issue: Files Not Persisting**

**Expected Behavior:**
- Render free tier has ephemeral storage
- Files uploaded are lost on service restart

**Solutions:**
1. ✅ **Use AWS S3** (configure S3 environment variables)
2. ✅ **Use Supabase Storage** (free 1GB)
3. ⚠️ **Accept data loss** (good for testing only)

### **Issue: Build Fails on Render**

**Check logs:**
1. Go to Render Dashboard → Your service
2. Click **"Logs"** tab
3. Look for error messages

**Common fixes:**
```bash
# Ensure requirements.txt has all dependencies
pip freeze > backend/requirements.txt

# Check Python version
# Render uses Python 3.7 by default, set to 3.10
# Add environment variable: PYTHON_VERSION=3.10.0
```

---

## 🔐 **Security Best Practices**

1. ✅ **Environment Variables**: Never commit secrets to Git
2. ✅ **Database**: Supabase has built-in security and backups
3. ✅ **CORS**: Only allow your Vercel domain
4. ✅ **S3**: Use signed URLs, never make bucket public
5. ✅ **HTTPS**: Both Render and Vercel provide free SSL

---

## 📊 **Monitoring**

### **Render Dashboard**
- View logs: Dashboard → Your service → **Logs**
- Check metrics: Dashboard → Your service → **Metrics**
- View events: Dashboard → Your service → **Events**

### **Vercel Dashboard**
- Visit [vercel.com/dashboard](https://vercel.com/dashboard)
- View deployment logs
- Check analytics and performance
- Monitor bandwidth usage

### **Supabase Dashboard**
- View database size: Dashboard → **Database** → **Database Size**
- Check queries: Dashboard → **SQL Editor**
- Monitor API usage: Dashboard → **API** → **Usage**

---

## 🔗 **Important URLs**

After deployment, save these URLs:

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://pdfpixie-backend.onrender.com`
- **API Docs**: `https://pdfpixie-backend.onrender.com/docs`
- **Supabase Dashboard**: `https://supabase.com/dashboard`
- **Render Dashboard**: `https://dashboard.render.com`
- **Vercel Dashboard**: `https://vercel.com/dashboard`
- **S3 Console**: `https://s3.console.aws.amazon.com/s3/buckets/pdfpixie-documents`

---

## 🎉 **Success Checklist**

- [ ] Supabase project created with database password saved
- [ ] Database connection string copied
- [ ] AWS S3 bucket created (optional)
- [ ] IAM user created with access keys (optional)
- [ ] Render account created and service deployed
- [ ] All environment variables set in Render
- [ ] Backend health check returns OK
- [ ] Vercel account created and frontend deployed
- [ ] VITE_API_URL set in Vercel
- [ ] FRONTEND_URL updated in Render
- [ ] Test PDF upload works
- [ ] Test chat functionality works
- [ ] Verify chat history persists after refresh
- [ ] Check Supabase dashboard shows data

---

## 🆘 **Need Help?**

### **Render Support**
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### **Supabase Support**
- Documentation: https://supabase.com/docs
- Community: https://github.com/supabase/supabase/discussions
- Discord: https://discord.supabase.com

### **Vercel Support**
- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions
- Status: https://www.vercel-status.com

---

## 🎯 **Next Steps**

1. **Custom Domain**: Add your own domain in Vercel/Render
2. **Error Tracking**: Set up Sentry for error monitoring
3. **Analytics**: Add usage analytics (Vercel Analytics)
4. **Backups**: Enable Supabase automatic backups
5. **CI/CD**: Add GitHub Actions for automated testing
6. **Caching**: Add Redis for faster responses (optional)

**Congratulations! Your PDFPixie is live on Render + Supabase + Vercel! 🚀**

---

## 📝 **Quick Reference Card**

```bash
# Render Quick Commands
# View logs: Dashboard → Logs
# Manual deploy: Dashboard → Manual Deploy
# Update env: Dashboard → Environment

# Vercel Quick Commands
vercel --prod                            # Deploy to production
vercel logs                              # View logs
vercel env add                           # Add environment variable

# Supabase Quick Commands
# Access via dashboard: https://supabase.com/dashboard
# SQL Editor: Dashboard → SQL Editor
# Table Editor: Dashboard → Table Editor

# Verify Deployment
curl https://pdfpixie-backend.onrender.com/health
open https://your-project.vercel.app
```

---

## 💡 **Pro Tips**

1. **Use S3 for production** - Render's ephemeral storage is only good for testing
2. **Set up cron job** - Keep your Render service awake
3. **Monitor Supabase usage** - 500MB is enough for ~50,000 chat messages
4. **Use Vercel Analytics** - Free insights into user behavior
5. **Enable Supabase backups** - Protect your data
6. **Test locally first** - Use `.env` files for local development
7. **Check logs regularly** - Catch issues before users do

---

**Total Setup Time: ~30 minutes**  
**Total Cost: $0/month (or $2-3/month with S3)**  
**Perfect for: Learning, portfolio projects, MVPs, small teams**
