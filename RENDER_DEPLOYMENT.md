# 🚀 Render + Supabase Deployment Guide

## Prerequisites
- GitHub account with your code pushed
- Render account (render.com)
- Supabase account (supabase.com)
- Gemini API key

---

## STEP 1: Setup Supabase Database

### 1.1 Create New Supabase Project
1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - Name: `legalai-db`
   - Database Password: (save this!)
   - Region: Choose closest to you
4. Wait for project to be ready (~2 minutes)

### 1.2 Get Database Connection String
1. In Supabase project, go to **Settings** → **Database**
2. Scroll to **Connection string**
3. Select **URI** tab
4. Copy the connection string, it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password
6. **SAVE THIS** - you'll need it for Render

---

## STEP 2: Push Code to GitHub

### 2.1 Initialize Git (if not already)
```bash
cd "c:\Users\hp\OneDrive\Documents\legal ai"
git init
git add .
git commit -m "Initial commit - LegalAI Django app"
```

### 2.2 Create GitHub Repository
1. Go to https://github.com/new
2. Name: `legalai-app`
3. Make it **Private**
4. Click "Create repository"

### 2.3 Push Code
```bash
git remote add origin https://github.com/YOUR-USERNAME/legalai-app.git
git branch -M main
git push -u origin main
```

---

## STEP 3: Deploy on Render

### 3.1 Create New Web Service
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select `legalai-app` repository

### 3.2 Configure Service
Fill in these settings:

**Basic Info:**
- Name: `legalai`
- Region: `Singapore` (closest to India)
- Branch: `main`
- Runtime: `Python 3`

**Build Settings:**
- Build Command: `./build.sh`
- Start Command: `cd backend && gunicorn legalai.wsgi:application`

**Plan:**
- Select **Starter** ($7/month)

### 3.3 Add Environment Variables
Click "Advanced" → "Add Environment Variable"

Add these one by one:

1. **DATABASE_URL**
   - Value: Your Supabase connection string from Step 1.2
   
2. **SECRET_KEY**
   - Value: Generate using https://djecrety.ir/ or run:
     ```python
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

3. **GEMINI_API_KEY**
   - Value: Your Gemini API key

4. **ALLOWED_HOSTS**
   - Value: `legalai.onrender.com,.onrender.com`

5. **DJANGO_SETTINGS_MODULE**
   - Value: `legalai.settings_prod`

### 3.4 Deploy
1. Click "Create Web Service"
2. Wait for deployment (~5-10 minutes)
3. Watch the logs for any errors

---

## STEP 4: Verify Deployment

### 4.1 Check Service
1. Once deployed, Render will give you a URL: `https://legalai.onrender.com`
2. Open the URL in your browser
3. You should see your LegalAI dashboard!

### 4.2 Create Admin User
1. Go to Render dashboard → your service
2. Click "Shell" tab
3. Run:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```
4. Enter username, email, password

### 4.3 Access Admin Panel
- Go to: `https://legalai.onrender.com/admin/`
- Login with your superuser credentials
- You can now add cases and test!

---

## STEP 5: Upload Vault Files

### 5.1 Using Admin Panel
1. Go to `/admin/`
2. Upload your legal vault PDFs through Django admin
3. Or use the document upload feature in your app

### 5.2 Using Render Shell (for bulk upload)
1. Click "Shell" in Render dashboard
2. Navigate to vault directory
3. Upload files using `wget` or manual upload

---

## 🎉 DEPLOYMENT COMPLETE!

Your app is now live at: `https://legalai.onrender.com`

**Costs:**
- Render: $7/month
- Supabase: FREE
- **Total: $7/month**

---

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies in `requirements.txt`
- Verify Python version compatibility

### Database Connection Error
- Double-check DATABASE_URL format
- Ensure Supabase project is active
- Test connection string locally first

### Static Files Not Loading
- Run `python manage.py collectstatic` in Shell
- Check STATIC_ROOT setting
- Verify WhiteNoise is installed

### Import Errors
- Make sure all packages in requirements.txt
- Check for missing dependencies
- Look at specific error in logs

---

## Next Steps

1. ✅ Test all features (cases, drafts, AI chat, timeline)
2. ✅ Add sample case data
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring/alerts
5. ✅ Share with early users!

---

## Support

If you face issues:
1. Check Render logs
2. Check Supabase dashboard for DB issues
3. Test locally with same DATABASE_URL
4. Contact Render support (they're helpful!)
