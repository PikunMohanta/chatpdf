# PDFPixie - Fly.io + Vercel Deployment Guide

## 🚀 **100% Free Deployment Architecture**

```
Frontend (Vercel)        Backend (Fly.io)
   ↓                         ↓
React App              FastAPI + Socket.IO
Global CDN             PostgreSQL Database
Instant Loading        Persistent Volumes
```

### **Why Fly.io + Vercel?**

- ✅ **100% Free** - No credit card required for either platform
- ✅ **Persistent Storage** - Fly.io includes free volumes
- ✅ **PostgreSQL** - Free Fly.io Postgres database
- ✅ **WebSockets** - Full Socket.IO support
- ✅ **Global CDN** - Vercel's edge network
- ✅ **No Cold Starts** - Fly.io keeps apps warm

---

## 📋 **Prerequisites**

- GitHub account
- Vercel account ([vercel.com](https://vercel.com))
- Fly.io account ([fly.io](https://fly.io))
- Code pushed to GitHub `render` branch

---

## 🛫 **Part 1: Deploy Backend to Fly.io**

### **Step 1: Install Fly CLI**

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### **Step 2: Login to Fly.io**

```bash
fly auth login
```

This will open your browser for authentication.

### **Step 3: Navigate to Your Project**

```bash
cd e:\Project\New\chatpdf
```

### **Step 4: Launch Your App**

```bash
fly launch --name pdfpixie-backend --region sin --dockerfile Dockerfile.fly
```

**Options to select:**
- **Would you like to copy its configuration to the new app?** → No
- **Would you like to set up a Postgresql database now?** → Yes
  - Choose: **Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk**
  - This is FREE
- **Would you like to set up an Upstash Redis database now?** → No
- **Would you like to deploy now?** → No (we'll set up environment variables first)

### **Step 5: Create Persistent Volume**

```bash
fly volumes create pdfpixie_data --region sin --size 1
```

This creates a 1GB persistent volume (FREE).

### **Step 6: Set Environment Variables**

```bash
# Set your OpenRouter API key
fly secrets set OPENROUTER_API_KEY=your_openrouter_api_key_here

# Set environment
fly secrets set ENVIRONMENT=production

# Note: DATABASE_URL is automatically set when you created Postgres
```

### **Step 7: Deploy**

```bash
fly deploy --dockerfile Dockerfile.fly
```

Wait for deployment to complete (2-4 minutes).

### **Step 8: Get Your Fly.io Backend URL**

```bash
fly status
```

Your URL will look like: `https://pdfpixie-backend.fly.dev`

**Copy this URL** - you'll need it for Vercel!

### **Step 9: Verify Backend is Running**

```bash
# Check status
fly status

# View logs
fly logs

# Open in browser
fly open
```

Visit `https://pdfpixie-backend.fly.dev/docs` to see API documentation.

---

## 🎨 **Part 2: Deploy Frontend to Vercel**

### **Step 1: Go to Vercel**

1. Visit [vercel.com](https://vercel.com)
2. Click "Sign Up" or "Login"
3. Choose "Continue with GitHub"
4. Authorize Vercel

### **Step 2: Import Your Repository**

1. Click **"Add New..." → "Project"**
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
VITE_API_URL=https://pdfpixie-backend.fly.dev
```

**Replace with your actual Fly.io backend URL from Part 1, Step 8**

### **Step 5: Deploy**

1. Click **"Deploy"**
2. Wait for build and deployment (1-2 minutes)
3. Your frontend will be live at: `https://your-project.vercel.app`

---

## 🔧 **Part 3: Connect Frontend to Backend**

### **Step 1: Update Fly.io with Vercel URL**

After your Vercel deployment completes, get your Vercel URL (e.g., `https://pdfpixie.vercel.app`)

Set it as an environment variable in Fly.io:

```bash
fly secrets set FRONTEND_URL=https://your-project.vercel.app
```

This updates the CORS configuration to allow requests from your frontend.

### **Step 2: Redeploy Fly.io Backend**

```bash
fly deploy --dockerfile Dockerfile.fly
```

This picks up the new `FRONTEND_URL` environment variable.

---

## ✅ **Testing Your Deployment**

### **1. Test Backend (Fly.io)**

Visit: `https://pdfpixie-backend.fly.dev/health`

You should see:
```json
{"status": "healthy", "service": "pdfpixie-api"}
```

### **2. Test API Documentation**

Visit: `https://pdfpixie-backend.fly.dev/docs`

You should see the FastAPI Swagger UI.

### **3. Test Frontend (Vercel)**

Visit: `https://your-project.vercel.app`

You should see the PDFPixie upload screen.

### **4. Test Full Integration**

1. **Upload a PDF document**
2. **Ask a question about the PDF**
3. **Verify the response appears**
4. **Refresh the page** - should stay on the same page
5. **Check chat history persists**

---

## 🎯 **Environment Variables Reference**

### **Fly.io (Backend)**

```bash
# Automatically set by Fly.io
DATABASE_URL=postgres://...  # When you create Postgres
PORT=8080  # Fly.io default

# You need to set these
fly secrets set ENVIRONMENT=production
fly secrets set OPENROUTER_API_KEY=your_key_here
fly secrets set FRONTEND_URL=https://your-vercel-url.vercel.app
```

### **Vercel (Frontend)**

```env
VITE_API_URL=https://pdfpixie-backend.fly.dev
```

---

## 🔄 **Continuous Deployment**

### **Automatic Deployments**

**Fly.io:**
- Set up GitHub Actions for auto-deploy (optional)
- Or use `fly deploy` manually when needed

**Vercel:**
- Automatically redeploys on push to `render` branch
- Creates preview deployments for PRs
- Zero configuration needed

### **Manual Deployments**

**Deploy Backend (Fly.io):**
```bash
cd e:\Project\New\chatpdf
fly deploy --dockerfile Dockerfile.fly
```

**Deploy Frontend (Vercel):**
```bash
# Automatic on git push, or use Vercel CLI
cd frontend
vercel --prod
```

---

## 🛠️ **Useful Fly.io Commands**

```bash
# Check app status
fly status

# View real-time logs
fly logs

# SSH into your app
fly ssh console

# Check PostgreSQL status
fly postgres list

# Connect to PostgreSQL
fly postgres connect -a pdfpixie-backend-db

# Scale app
fly scale count 1  # Number of instances

# View volumes
fly volumes list

# Check app info
fly info

# Open app in browser
fly open

# View secrets
fly secrets list

# Remove a secret
fly secrets unset SECRET_NAME
```

---

## 💰 **Cost Breakdown (100% Free)**

### **Fly.io Free Tier**
- ✅ **3 shared-cpu-1x VMs** (256MB RAM each)
- ✅ **PostgreSQL database** (256MB RAM, 1GB storage)
- ✅ **3GB persistent volumes**
- ✅ **160GB outbound bandwidth**
- ✅ **Free SSL certificates**

**Usage for PDFPixie:**
- 1 VM for backend (FREE)
- 1 Postgres database (FREE)
- 1GB volume (FREE)

### **Vercel Free Tier**
- ✅ **100GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **Global CDN**
- ✅ **Serverless functions**
- ✅ **Preview deployments**

**Total Monthly Cost: $0** 🎉

---

## 🚀 **Performance Optimization**

### **Fly.io Backend**
```bash
# Add more regions (for global performance)
fly regions add ams lhr  # Amsterdam, London

# Scale up if needed (still within free tier)
fly scale vm shared-cpu-1x

# Monitor performance
fly dashboard
```

### **Vercel Frontend**
- ✅ Automatically optimized
- ✅ Global CDN caching
- ✅ Compressed assets
- ✅ HTTP/2 and Brotli

---

## 🐛 **Troubleshooting**

### **Issue: Frontend Can't Connect to Backend**

**Check:**
1. Verify `VITE_API_URL` in Vercel matches your Fly.io URL
2. Ensure `FRONTEND_URL` is set in Fly.io secrets
3. Check CORS in `backend/main.py`

**Fix:**
```bash
# Update frontend URL in Fly.io
fly secrets set FRONTEND_URL=https://your-actual-vercel-url.vercel.app

# Redeploy
fly deploy --dockerfile Dockerfile.fly
```

### **Issue: Database Connection Error**

**Check:**
```bash
# List PostgreSQL apps
fly postgres list

# Check database status
fly postgres connect -a pdfpixie-backend-db

# View connection string
fly secrets list
```

**Fix:**
```bash
# Recreate database if needed
fly postgres create --name pdfpixie-db --region sin
fly postgres attach pdfpixie-db
```

### **Issue: Volume Not Mounted**

**Check:**
```bash
# List volumes
fly volumes list

# Check app status
fly status
```

**Fix:**
```bash
# Create volume if missing
fly volumes create pdfpixie_data --region sin --size 1

# Ensure fly.toml has [mounts] section
# Then redeploy
fly deploy --dockerfile Dockerfile.fly
```

### **Issue: Build Fails**

**Check logs:**
```bash
fly logs
```

**Common fixes:**
```bash
# Clear build cache
fly deploy --dockerfile Dockerfile.fly --no-cache

# Check Dockerfile.fly exists
ls Dockerfile.fly

# Verify requirements.txt is correct
cat backend/requirements.txt
```

### **Issue: App Not Starting**

**Check:**
```bash
# View logs
fly logs

# SSH into container
fly ssh console

# Check health
curl https://pdfpixie-backend.fly.dev/health
```

---

## 🔐 **Security Best Practices**

1. ✅ **Secrets Management**: Use `fly secrets` for sensitive data
2. ✅ **CORS**: Only allow your Vercel domain
3. ✅ **HTTPS**: Both platforms provide free SSL
4. ✅ **Database**: Fly Postgres has built-in security
5. ✅ **Environment Variables**: Never commit secrets to Git

---

## 📊 **Monitoring**

### **Fly.io Dashboard**
```bash
# Open dashboard
fly dashboard

# View metrics
fly dashboard metrics

# Check logs
fly logs --follow
```

### **Vercel Dashboard**
- Visit [vercel.com/dashboard](https://vercel.com/dashboard)
- View deployment logs
- Check analytics and performance
- Monitor bandwidth usage

---

## 🔗 **Important URLs**

After deployment, you'll have:

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://pdfpixie-backend.fly.dev`
- **API Docs**: `https://pdfpixie-backend.fly.dev/docs`
- **Fly.io Dashboard**: `https://fly.io/dashboard`
- **Vercel Dashboard**: `https://vercel.com/dashboard`

---

## 🎉 **Success Checklist**

- [ ] Fly CLI installed and logged in
- [ ] Backend deployed to Fly.io with PostgreSQL
- [ ] Persistent volume created and mounted
- [ ] Environment variables set (OPENROUTER_API_KEY, FRONTEND_URL)
- [ ] Frontend deployed to Vercel
- [ ] VITE_API_URL set in Vercel
- [ ] CORS configured correctly
- [ ] Test PDF upload works
- [ ] Test chat functionality
- [ ] Verify chat history persists after refresh
- [ ] Check API docs are accessible

---

## 🆘 **Need Help?**

### **Fly.io Support**
- Documentation: https://fly.io/docs
- Community: https://community.fly.io
- Status: https://status.fly.io

### **Vercel Support**
- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions
- Status: https://www.vercel-status.com

### **Check Logs**
```bash
# Fly.io
fly logs --follow

# Vercel (in dashboard)
# Go to Deployments → Click deployment → View logs
```

---

## 🎯 **Next Steps**

1. **Custom Domain**: Add your own domain in Vercel/Fly.io
2. **Monitoring**: Set up error tracking (Sentry)
3. **Analytics**: Add usage analytics
4. **Backups**: Set up database backups on Fly.io
5. **CI/CD**: Add GitHub Actions for automated testing

**Congratulations! Your PDFPixie is live on Fly.io + Vercel! 🚀**

---

## 📝 **Quick Reference Card**

```bash
# Fly.io Quick Commands
fly deploy --dockerfile Dockerfile.fly  # Deploy
fly logs                                 # View logs
fly status                               # Check status
fly secrets set KEY=value               # Set secret
fly volumes list                         # List volumes
fly postgres list                        # List databases

# Vercel Quick Commands
vercel --prod                            # Deploy to production
vercel logs                              # View logs
vercel env add                           # Add environment variable

# Verify Deployment
curl https://pdfpixie-backend.fly.dev/health
open https://your-project.vercel.app
```