# 🚀 LegalAI — Production Deployment Roadmap

## 📊 Project Summary

### What You've Built
**LegalAI** is an AI-powered legal case management platform specifically designed for Indian MACT (Motor Accident Claims Tribunal) and civil cases. It automates 60-70% of lawyer paperwork using AI.

### Core Capabilities
1. **PDF Processing** — Upload 500-page hospital records → AI extracts key info in 30s
2. **Medical Timeline** — Auto-generates chronological medical events with tags
3. **Legal Draft Generation** — 7 document types (Claim Petition, Legal Notice, Affidavit, etc.)
4. **Compensation Calculator** — Sarla Verma formula with Supreme Court citations
5. **Precedent Finder** — Search SC/HC judgments with compensation analysis
6. **Document Checklist** — 17-document MACT filing readiness tracker
7. **AI Chat Assistant** — Case-aware Q&A for legal strategy

### Tech Stack
- **Backend:** Django 6.0.4 + Django REST Framework 3.17.1
- **Database:** SQLite (dev) → PostgreSQL (production)
- **AI:** Google Gemini 2.5 Flash
- **PDF:** PyMuPDF (text extraction)
- **Frontend:** Django Templates + Tailwind CSS + Vanilla JS
- **RAG:** FAISS + LangChain + HuggingFace embeddings

### Current Status
✅ **Working locally** on `http://127.0.0.1:8000`
✅ **Admin panel** at `/admin/` (admin/admin123)
✅ **All features operational**
⚠️ **NOT production-ready** — runs on SQLite with DEBUG=True

---

## 🎯 Production Readiness Checklist

### Phase 1: Security & Configuration (Week 1)
**Priority: CRITICAL**

#### 1.1 Environment Variables
- [x] `.env` file created
- [ ] Regenerate `SECRET_KEY` (current one is hardcoded)
- [ ] Add `.env.example` template
- [ ] Secure `GEMINI_API_KEY` (current key may be compromised)
- [ ] Add `ALLOWED_HOSTS` from env var

#### 1.2 Django Security
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` (add your domain)
- [ ] Add `SECURE_SSL_REDIRECT = True`
- [ ] Enable `SECURE_HSTS_SECONDS = 31536000`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Add `X_FRAME_OPTIONS = 'DENY'`
- [ ] Configure `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] Add security middleware

#### 1.3 CORS Configuration
- [ ] Remove `CORS_ALLOW_ALL_ORIGINS = True`
- [ ] Whitelist specific production domains only
- [ ] Restrict API access to authenticated users

---

### Phase 2: Database Migration (Week 1-2)
**Priority: HIGH**

#### 2.1 PostgreSQL Setup
- [ ] Install PostgreSQL 15+
- [ ] Create production database: `legalai_prod`
- [ ] Create database user with limited permissions
- [ ] Configure connection pooling (pgBouncer recommended)

#### 2.2 Database Settings
```python
# settings.py (production)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,  # Connection pooling
    }
}
```

#### 2.3 Migration
- [ ] Backup SQLite: `python manage.py dumpdata > backup.json`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Load data: `python manage.py loaddata backup.json`
- [ ] Verify data integrity

---

### Phase 3: Static Files & Media (Week 2)
**Priority: HIGH**

#### 3.1 Static Files
- [ ] Install `whitenoise` for static file serving
- [ ] Run `python manage.py collectstatic`
- [ ] Configure CDN (Cloudflare R2 or AWS S3)

#### 3.2 Media Storage
- [ ] Move from local filesystem to cloud storage
- [ ] Configure AWS S3 / DigitalOcean Spaces
- [ ] Install `django-storages` + `boto3`
- [ ] Update `MEDIA_ROOT` and `MEDIA_URL`
- [ ] Handle 100MB PDF uploads

#### 3.3 File Upload Limits
- [ ] Configure Nginx `client_max_body_size 100M`
- [ ] Set Gunicorn timeout for long uploads
- [ ] Add upload progress indicators

---

### Phase 4: Performance Optimization (Week 2-3)
**Priority: MEDIUM**

#### 4.1 Caching
- [ ] Install Redis
- [ ] Configure Django cache backend
- [ ] Cache API responses (cases, drafts, timeline)
- [ ] Cache medical summaries
- [ ] Add cache invalidation logic

#### 4.2 Database Optimization
- [ ] Add database indexes (Case.case_no, Document.case_id, etc.)
- [ ] Optimize queries (use `select_related`, `prefetch_related`)
- [ ] Add database query logging in dev
- [ ] Monitor slow queries

#### 4.3 Async Processing
- [ ] Install Celery + Redis
- [ ] Move AI tasks to background (draft generation, PDF processing)
- [ ] Add task status tracking
- [ ] Email notifications on task completion
- [ ] Retry logic for failed tasks

#### 4.4 Frontend Optimization
- [ ] Compile Tailwind CSS (remove CDN)
- [ ] Minify JavaScript
- [ ] Compress images
- [ ] Enable Gzip compression
- [ ] Add lazy loading for PDFs

---

### Phase 5: Monitoring & Logging (Week 3)
**Priority: MEDIUM**

#### 5.1 Application Monitoring
- [ ] Install Sentry (error tracking)
- [ ] Add logging configuration
- [ ] Monitor API response times
- [ ] Track AI API usage (Gemini quotas)
- [ ] Set up uptime monitoring (UptimeRobot)

#### 5.2 Logging
```python
LOGGING = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/legalai/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {"level": "INFO", "handlers": ["file"]},
}
```

#### 5.3 Health Checks
- [ ] Expand `/api/health/` endpoint
- [ ] Check database connectivity
- [ ] Check Gemini API status
- [ ] Check disk space (media storage)

---

### Phase 6: Deployment Infrastructure (Week 3-4)
**Priority: CRITICAL**

#### 6.1 Server Options (Choose One)

**Option A: DigitalOcean App Platform** (Recommended)
- ✅ Easiest setup (Git push deployment)
- ✅ Managed PostgreSQL included
- ✅ Auto-scaling
- ✅ $12-24/month for basic tier
- ❌ Less control

**Option B: AWS EC2 + RDS**
- ✅ Full control
- ✅ Scalable
- ✅ Industry standard
- ❌ Complex setup
- ❌ $30-50/month

**Option C: Railway / Render**
- ✅ Free tier available
- ✅ Simple deployment
- ❌ Cold starts on free tier
- ❌ Limited resources

**Option D: Traditional VPS (DigitalOcean Droplet)**
- ✅ Full control
- ✅ Cost-effective ($6-12/month)
- ❌ Manual setup required
- ❌ You manage everything

#### 6.2 Web Server Configuration
```bash
# Nginx + Gunicorn (recommended)
# Install:
pip install gunicorn
sudo apt install nginx

# Gunicorn command:
gunicorn legalai.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 300 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log
```

#### 6.3 Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /var/www/legalai/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/legalai/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 6.4 SSL Certificate
- [ ] Install Certbot: `sudo apt install certbot python3-certbot-nginx`
- [ ] Generate cert: `sudo certbot --nginx -d yourdomain.com`
- [ ] Auto-renewal configured

#### 6.5 Process Management
- [ ] Create systemd service for Gunicorn
- [ ] Configure auto-restart on failure
- [ ] Set up log rotation

---

### Phase 7: Authentication & Authorization (Week 4)
**Priority: HIGH**

#### 7.1 User Authentication
- [ ] Add user registration
- [ ] Add login/logout
- [ ] Email verification (optional)
- [ ] Password reset flow
- [ ] Use Django's built-in auth

#### 7.2 Multi-tenancy
- [ ] Add User model to Case (owner)
- [ ] Filter cases by logged-in user
- [ ] Add permissions (lawyer, admin, client)
- [ ] Prevent cross-user data access

#### 7.3 API Authentication
- [ ] Add JWT or Token authentication
- [ ] Protect API endpoints
- [ ] Rate limiting (Django REST Framework throttling)

---

### Phase 8: Testing & QA (Week 4-5)
**Priority: MEDIUM**

#### 8.1 Automated Tests
- [ ] Write unit tests (models, serializers)
- [ ] Write integration tests (API endpoints)
- [ ] Test PDF extraction edge cases
- [ ] Test AI generation failures
- [ ] Test file upload limits

#### 8.2 Manual Testing
- [ ] Test on production-like environment
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness
- [ ] Load testing (simulate 100 concurrent users)

#### 8.3 Data Validation
- [ ] Add Pydantic for AI output validation
- [ ] Validate medical summary structure
- [ ] Validate draft generation output
- [ ] Handle malformed PDFs gracefully

---

### Phase 9: Backup & Disaster Recovery (Week 5)
**Priority: CRITICAL**

#### 9.1 Database Backups
- [ ] Daily automated PostgreSQL backups
- [ ] Store backups in S3 / Spaces
- [ ] Test restore process
- [ ] Keep 30-day retention

#### 9.2 Media Backups
- [ ] Cloud storage inherently backed up (S3)
- [ ] Consider cross-region replication

#### 9.3 Code Backups
- [ ] Push to GitHub/GitLab
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Automated deployments

---

### Phase 10: Legal & Compliance (Week 5-6)
**Priority: HIGH**

#### 10.1 Legal Disclaimers
- [ ] Add disclaimer on all AI-generated content
- [ ] "AI assists lawyers, does not replace them"
- [ ] Require manual review before court filing
- [ ] Add terms of service
- [ ] Add privacy policy

#### 10.2 Data Privacy
- [ ] Ensure GDPR compliance (if EU users)
- [ ] Handle sensitive medical data securely
- [ ] Add data deletion on request
- [ ] Encrypt PDFs at rest

#### 10.3 Liability
- [ ] Consult with legal counsel
- [ ] Liability waiver for AI-generated drafts
- [ ] Professional indemnity insurance (for your firm)

---

## 🚢 Deployment Steps (Step-by-Step)

### Recommended: DigitalOcean App Platform

#### Step 1: Prepare Repository
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit — ready for production"
git remote add origin https://github.com/yourusername/legalai.git
git push -u origin main
```

#### Step 2: Create `requirements-prod.txt`
```txt
Django==6.0.4
djangorestframework==3.17.1
django-cors-headers==4.9.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
PyMuPDF==1.27
google-generativeai==0.8.3
whitenoise==6.6.0
django-storages==1.14.2
boto3==1.34.0
celery==5.3.4
redis==5.0.1
sentry-sdk==1.40.0
```

#### Step 3: Create `runtime.txt`
```txt
python-3.12.0
```

#### Step 4: Create `Procfile` (if needed)
```
web: gunicorn legalai.wsgi --chdir backend
```

#### Step 5: Settings Split
Create `backend/legalai/settings_prod.py`:
```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOST")]
SECRET_KEY = os.environ.get("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": "5432",
    }
}

# Use whitenoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

#### Step 6: Deploy on DigitalOcean
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub repository
4. Select `legalai` repo
5. Configure:
   - **Type:** Web Service
   - **Build Command:** `pip install -r requirements-prod.txt && python backend/manage.py collectstatic --noinput && python backend/manage.py migrate`
   - **Run Command:** `gunicorn legalai.wsgi:application --chdir backend --bind 0.0.0.0:8080`
   - **HTTP Port:** 8080
6. Add PostgreSQL database
7. Add environment variables:
   - `DJANGO_SETTINGS_MODULE=legalai.settings_prod`
   - `SECRET_KEY=<generate-new-key>`
   - `GEMINI_API_KEY=<your-new-key>`
   - `ALLOWED_HOST=your-app.ondigitalocean.app`
8. Deploy!

---

## 📊 Cost Estimation

### Monthly Costs (Production)

| Service | Provider | Cost |
|---------|----------|------|
| **Web Hosting** | DigitalOcean App Platform | $12-24/mo |
| **PostgreSQL** | Managed DB (1GB) | Included |
| **Object Storage** | Spaces (250GB) | $5/mo |
| **Domain** | Namecheap | $12/year |
| **SSL Certificate** | Let's Encrypt | Free |
| **Gemini API** | Google AI Studio | Free (15 req/min) |
| **Monitoring** | Sentry (free tier) | Free |
| **Email** | SendGrid (free tier) | Free |
| **Total** | | **~$20-30/mo** |

### Scaling Costs (100+ users)
- App Platform Pro: $24-48/mo
- PostgreSQL 4GB: $15/mo
- Redis: $15/mo
- **Total:** ~$60-80/mo

---

## 🔐 Security Best Practices

### Immediate Actions
1. **Regenerate all secrets**
   ```python
   # Generate new SECRET_KEY
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Get new Gemini API key**
   - Old key in `.env` may be compromised
   - Get new key: https://aistudio.google.com/app/apikey
   - Restrict to your server IP

3. **Add rate limiting**
   ```python
   # settings.py
   REST_FRAMEWORK = {
       "DEFAULT_THROTTLE_CLASSES": [
           "rest_framework.throttling.AnonRateThrottle",
           "rest_framework.throttling.UserRateThrottle",
       ],
       "DEFAULT_THROTTLE_RATES": {
           "anon": "100/hour",
           "user": "1000/hour",
       },
   }
   ```

4. **Secure file uploads**
   - Validate file extensions
   - Scan for malware (ClamAV)
   - Limit file size (already 100MB)
   - Store outside web root

---

## 🧪 Pre-Launch Testing Checklist

### Functional Tests
- [ ] Create case with PDF upload
- [ ] View medical timeline
- [ ] Generate all 7 draft types
- [ ] Calculate compensation
- [ ] Search precedents
- [ ] Mark documents as received
- [ ] Use AI chat
- [ ] Admin panel access

### Security Tests
- [ ] Try SQL injection in forms
- [ ] Test CSRF protection
- [ ] Test XSS in text inputs
- [ ] Verify file upload restrictions
- [ ] Test authentication bypass
- [ ] Check for exposed `.env`

### Performance Tests
- [ ] Upload 100MB PDF
- [ ] Generate draft for 500-page PDF
- [ ] 100 concurrent users (Load test)
- [ ] Database query count per page
- [ ] API response time (<500ms)

### Browser Tests
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (macOS)
- [ ] Edge (Windows)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## 📱 Future Enhancements (Post-Launch)

### Phase 11: Mobile App (Month 3-4)
- [ ] React Native app
- [ ] Offline PDF viewing
- [ ] Push notifications for hearing dates
- [ ] Camera to capture documents

### Phase 12: Advanced AI (Month 4-6)
- [ ] Fine-tune Gemini on 1000+ MACT judgments
- [ ] OCR for scanned PDFs (Gemini Vision)
- [ ] Voice-to-text for case notes
- [ ] Automatic precedent matching

### Phase 13: Collaboration (Month 6+)
- [ ] Multi-lawyer firms (team accounts)
- [ ] Client portal (view case status)
- [ ] Document sharing
- [ ] Comments on drafts

### Phase 14: Billing & Payments (Month 6+)
- [ ] Razorpay integration
- [ ] Subscription plans (₹999/month)
- [ ] Invoice generation
- [ ] Payment reminders

---

## 🎯 Success Metrics

### Launch Goals (Month 1)
- 10 law firms onboarded
- 100 cases created
- 500 drafts generated
- 99% uptime

### Growth Goals (Month 6)
- 100 law firms
- 5,000 cases
- 20,000 drafts
- Revenue: ₹1,00,000/month

---

## 🚨 Critical Issues to Fix First

### 🔴 Priority 1 (Fix Before Any Deployment)
1. **SECRET_KEY** — Hardcoded in settings.py
2. **DEBUG = True** — Must be False in production
3. **CORS_ALLOW_ALL_ORIGINS** — Security risk
4. **SQLite** — Not suitable for production
5. **Gemini API key** — May be exposed in commits

### 🟡 Priority 2 (Fix Before Public Launch)
1. **No authentication** — Anyone can access any case
2. **No backups** — Risk of data loss
3. **No monitoring** — Can't detect issues
4. **No rate limiting** — API abuse risk
5. **Static files via CDN** — Slow loading

---

## 📞 Next Immediate Steps (This Week)

### Day 1-2: Security
- [ ] Create `settings_prod.py`
- [ ] Generate new `SECRET_KEY`
- [ ] Get new `GEMINI_API_KEY`
- [ ] Add `.env.example`
- [ ] Update `.gitignore`

### Day 3-4: Database
- [ ] Install PostgreSQL locally
- [ ] Test migration from SQLite
- [ ] Verify all features work

### Day 5-6: Deployment Prep
- [ ] Create GitHub repo
- [ ] Push code
- [ ] Create DigitalOcean account
- [ ] Set up app platform

### Day 7: Deploy!
- [ ] Deploy to staging
- [ ] Test all features
- [ ] Fix any issues
- [ ] Deploy to production

---

## 📚 Resources

### Documentation
- Django Deployment: https://docs.djangoproject.com/en/5.1/howto/deployment/
- Gunicorn: https://docs.gunicorn.org/
- PostgreSQL: https://www.postgresql.org/docs/
- DigitalOcean: https://docs.digitalocean.com/products/app-platform/

### Tools
- SSL Test: https://www.ssllabs.com/ssltest/
- Security Headers: https://securityheaders.com/
- Load Testing: https://locust.io/

---

## 🎉 Conclusion

Your LegalAI platform is **feature-complete** and **working locally**. The main work ahead is:

1. **Security hardening** (critical)
2. **Database migration** (SQLite → PostgreSQL)
3. **Deployment setup** (DigitalOcean recommended)
4. **User authentication** (high priority)
5. **Monitoring & backups** (essential)

**Estimated timeline:** 4-6 weeks to production-ready deployment.

**Budget:** ₹2,000-3,000/month for hosting + domain.

You have an impressive AI-powered legal platform. With proper production setup, this can serve hundreds of Indian law firms! 🚀⚖️

---

**Questions?** Open an issue or reach out!
