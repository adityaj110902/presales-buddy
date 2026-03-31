# Railway Deployment - Complete Guide

## 🚀 DEPLOY OLLAMA + BACKEND + FRONTEND ON RAILWAY

---

## 📋 STEP 1: PREPARE YOUR PROJECT

Your folder should have these files:

```
C:\Users\AdityaJain\presales-buddy\
├── backend_api.py           (your Flask backend)
├── frontend.html            (your React UI)
├── Dockerfile               (NEW - for Docker)
├── .dockerignore           (NEW - ignore files)
├── railway.json            (NEW - Railway config)
├── Procfile                (NEW - how to run)
├── requirements.txt        (NEW - Python packages)
├── data/
│   ├── Company_Profile.pdf
│   └── Retail_Banking_Brochure.pdf
└── venv/                   (not needed for Railway)
```

---

## ✅ STEP 2: CREATE THE FILES (FROM /outputs/)

Download these files from `/outputs/`:
1. ✅ `Dockerfile`
2. ✅ `.dockerignore`
3. ✅ `railway.json`
4. ✅ `requirements.txt`

Also create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT backend_api:app
```

Or use the Procfile_railway file provided.

---

## 📤 STEP 3: PUSH TO GITHUB

Open Command Prompt:

```bash
cd C:\Users\AdityaJain\presales-buddy

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Add Railway deployment files - Ollama + Flask + React"

# Push to GitHub
git push origin main
```

If you don't have GitHub repo yet:
```bash
# Create new repo on GitHub first
# Go to github.com/new
# Name: presales-buddy
# Then:

git remote add origin https://github.com/YOUR-USERNAME/presales-buddy.git
git branch -M main
git push -u origin main
```

---

## 🚂 STEP 4: CREATE RAILWAY PROJECT

1. **Go to:** https://railway.app
2. **Sign up** (use GitHub recommended)
3. **Click:** "New Project"
4. **Select:** "Deploy from GitHub repo"

---

## 🔗 STEP 5: CONNECT GITHUB

1. **Search for:** presales-buddy repo
2. **Click:** "Select repo"
3. **Authorize Railway** to access your GitHub

---

## ⚙️ STEP 6: CONFIGURE RAILWAY

Railway should auto-detect the Dockerfile!

Wait for it to show:
```
Building...
Deploying...
```

This takes 5-10 minutes the first time (downloading Ollama model).

---

## 🌐 STEP 7: GET YOUR RAILWAY URL

Once deployed, Railway shows your URL:
```
https://presales-buddy-xxxxx.up.railway.app
```

Copy this!

---

## 📝 STEP 8: UPDATE FRONTEND

Edit `frontend.html` in your repo:

Find line ~285:
```javascript
const API_URL = 'http://localhost:5000/api';
```

Replace with:
```javascript
const API_URL = 'https://presales-buddy-xxxxx.up.railway.app/api';
```

(Use YOUR actual Railway URL!)

---

## 📤 STEP 9: PUSH CHANGES

```bash
cd C:\Users\AdityaJain\presales-buddy

git add frontend.html
git commit -m "Update API URL for Railway"
git push

# Railway auto-redeploys! Wait 2-3 minutes
```

---

## 🎉 STEP 10: ACCESS YOUR APP

Open in browser:
```
https://presales-buddy-xxxxx.up.railway.app
```

**You should see:**
- ✅ Beautiful React UI
- ✅ Green dot "AI ASSISTANT"
- ✅ 2 documents loaded
- ✅ Ready to chat!

---

## 🧪 STEP 11: TEST IT

1. Click suggested questions OR type your own
2. Ask: "What is Retail Banking?"
3. Wait for response (first call takes 10 seconds)
4. See structured answer with 📌 🎯 💡 📊 ✅ 🔗

---

## ⏱️ WHAT TO EXPECT

**First deployment:** 5-10 minutes (downloading Ollama + Llama model)
**First API call:** 10-15 seconds (model warming up)
**Subsequent calls:** 2-5 seconds (fast!)

---

## 📊 WHAT'S RUNNING

```
Railway Server:
├── Docker Container
├── Ollama Server (port 11434) ⭐
├── Llama 3.1 Model (4.9GB)
├── Flask Backend (port 5000)
└── Frontend (HTML)

All running in the cloud!
```

---

## 💰 RAILWAY PRICING

- **Free tier:** $5/month credit
- **Your usage:** ~$3-5/month (after credit expires)
- **Forever free for 1 month** with credit!

---

## 🔧 TROUBLESHOOTING

### **Deployment stuck on "Building"**
- Railway is downloading Ollama (can take 10+ min)
- Don't cancel it!
- Check logs: Click "Logs" tab in Railway dashboard

### **App won't load**
- Check if backend is running
- Click "Logs" to see errors
- Wait for Ollama to fully start

### **API returns error**
- First request might fail (model warming)
- Try again after 10 seconds
- Check logs for details

### **To view logs:**
1. Go to Railway dashboard
2. Click your project
3. Click "Logs" tab
4. See what's happening

---

## 🚀 SHARE YOUR APP

Once live, share the URL:
```
https://presales-buddy-xxxxx.up.railway.app
```

Anyone can access it! No installation needed!

---

## 📋 QUICK CHECKLIST

```
☐ Download 4 files from /outputs/
☐ Copy to presales-buddy folder
☐ Create Procfile (if needed)
☐ Push to GitHub
☐ Go to railway.app
☐ Create new project
☐ Connect GitHub repo
☐ Wait for deployment (5-10 min)
☐ Get Railway URL
☐ Update frontend.html with URL
☐ Push changes
☐ Open URL in browser
☐ Test! 🎉
```

---

## ✨ YOU NOW HAVE

✅ Private Ollama running in cloud
✅ Your own Llama 3.1 model
✅ Flask backend with RAG
✅ Beautiful React frontend
✅ Everything deployed to Railway
✅ Accessible from anywhere
✅ Free for 1 month!

---

## 🎯 FINAL RESULT

```
Your URL (public):
https://presales-buddy-xxxxx.up.railway.app

What's inside:
├── Your documents (RAG)
├── Ollama (private LLM)
├── Llama 3.1 (your model)
├── Flask (API backend)
└── React (beautiful UI)

All in one cloud deployment! 🚀
```

---

## 📞 NEED HELP?

During deployment:
1. Check Railway dashboard "Logs" tab
2. Wait for "Server is running"
3. Then try accessing URL

If stuck:
1. Click "Redeploy" in Railway
2. Check documentation: https://docs.railway.app

---

**You're ready to deploy!** 👍

Follow steps 1-11 above and your app will be LIVE on Railway!

The hardest part is waiting for Ollama to download the first time (~10 min).
Everything else is automatic! ✨
