# 🚀 Koyeb Deployment Guide

## Step-by-Step Deployment to Koyeb (100% FREE)

### ✅ Prerequisites
- GitHub account
- Koyeb account (free)
- Git installed locally

---

## 📋 Step 1: Prepare Your Code

Your project is already configured with:
- ✅ `Procfile` - Deployment config
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `.gitignore` - Excludes unnecessary files

---

## 🔧 Step 2: Push to GitHub

### Initialize Git (if not already done):
```bash
cd amazon_deals_scraper
git init
```

### Add all files:
```bash
git add .
```

### Commit:
```bash
git commit -m "Initial commit: Amazon Deals Scraper for Koyeb"
```

### Create GitHub repo and push:
1. Go to [GitHub.com](https://github.com)
2. Click "+" → "New repository"
3. Name: `amazon-deals-scraper`
4. Make it **Public** (required for Koyeb free tier)
5. **Don't** initialize with README (we have one)
6. Click "Create repository"

### Push to GitHub:
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/amazon-deals-scraper.git
git push -u origin main
```

---

## 🌐 Step 3: Deploy on Koyeb

### 1. Sign Up for Koyeb
- Go to [app.koyeb.com/auth/signup](https://app.koyeb.com/auth/signup)
- Sign up with GitHub (easiest)
- **FREE** tier - No credit card required!

### 2. Create New App
- Click **"Create App"** button
- Select **"Deploy from GitHub"**

### 3. Connect GitHub
- Click **"Authorize Koyeb"**
- Grant access to your repositories
- Select your `amazon-deals-scraper` repository

### 4. Configure Deployment Settings

**Builder:** 
- Select **"Buildpack"** (auto-detected)

**Run Command:**
```bash
gunicorn app:app
```

**Port:**
```
8000
```

**Instance Type:**
- Select **"Nano"** (FREE tier)

**Regions:**
- Select **"Frankfurt (fra)"** or closest to you

**App Name:**
```
amazon-deals-scraper
```

**Environment Variables** (Optional but recommended):
```
FLASK_ENV=production
```

### 5. Deploy!
- Click **"Deploy"**
- Wait 2-3 minutes ⏱️
- Watch the build logs

---

## ✅ Step 4: Access Your Live App

Your app will be available at:
```
https://amazon-deals-scraper-YOUR-USERNAME.koyeb.app/
```

Or check your custom URL in Koyeb dashboard.

---

## 🎯 Post-Deployment Checklist

- [ ] App builds successfully
- [ ] No errors in logs
- [ ] Homepage loads correctly
- [ ] Can enter Amazon URL
- [ ] Scraping starts and shows progress
- [ ] Deals display correctly

---

## 🔍 Monitoring & Logs

### View Logs:
1. Go to Koyeb Dashboard
2. Click on your app
3. Go to **"Logs"** tab
4. See real-time logs

### Check Status:
- Green = Running ✅
- Yellow = Building 🔨
- Red = Error ❌

---

## 🐛 Troubleshooting

### Build Fails
**Error:** "Could not find requirements.txt"
- **Fix:** Make sure `requirements.txt` is in root directory
- Check it's pushed to GitHub: `git ls-files | grep requirements`

### App Crashes
**Error:** Port binding issues
- **Fix:** Already handled in `app.py` with `os.environ.get('PORT')`
- Koyeb automatically sets PORT to 8000

### Scraping Doesn't Work
**Issue:** Amazon blocks cloud IPs
- **Solution 1:** Try different regions in Koyeb
- **Solution 2:** Use fewer concurrent requests
- **Solution 3:** Add User-Agent rotation (already implemented)

---

## 🔄 Update Your Deployed App

### Make changes locally:
```bash
# Edit your files
git add .
git commit -m "Update: description of changes"
git push origin main
```

Koyeb will **automatically redeploy** when you push to GitHub! 🎉

---

## 💰 Koyeb Free Tier Limits

- ✅ 1 Free App
- ✅ 512 MB RAM
- ✅ 1 vCPU (shared)
- ✅ Unlimited bandwidth
- ✅ Auto-sleep after inactivity (wakes up on request)

Perfect for this scraper! 🎯

---

## 🔐 Security Notes

1. **Never commit:**
   - API keys
   - Passwords
   - `.env` files
   
2. **Use Environment Variables** for sensitive data in Koyeb dashboard

3. **Rate Limiting** is already implemented to avoid IP bans

---

## 📞 Support

**Koyeb Issues:**
- [Koyeb Support](https://www.koyeb.com/support)
- [Koyeb Community](https://community.koyeb.com/)

**App Issues:**
- Check logs first
- Review README.md
- Check GitHub issues

---

## 🎉 You're Live!

Your Amazon Deals Scraper is now live on the internet! 

Share your URL:
```
https://your-app-name.koyeb.app
```

Happy Scraping! 🛒✨
