# 🚀 LegalAI Deployment Guide

## Quick Start: Deploy to DigitalOcean App Platform (Easiest)

### Step 1: Prepare Your Code

```bash
# Generate new secret key
python generate_secret_key.py

# Copy to .env (don't commit!)
echo "SECRET_KEY=<generated-key>" >> .env
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Ready for production deployment"
git branch -M main
git remote add origin https://github.com/yourusername/legalai.git
git push -u origin main
```

### Step 3: Create DigitalOcean App

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub → Select `legalai` repo
4. Configure:
   - **Build Command:**
     ```bash
     pip install -r requirements-prod.txt && python backend/manage.py collectstatic --noinput && python backend/manage.py migrate --noinput
     ```
   - **Run Command:**
     ```bash
     gunicorn legalai.wsgi:application --chdir backend --bind 0.0.0.0:8080 --workers 4 --timeout 300
     ```
   - **HTTP Port:** 8080

5. Add PostgreSQL Database (Managed)
6. Add Environment Variables:

```env
DJANGO_SETTINGS_MODULE=legalai.settings_prod
SECRET_KEY=<your-generated-secret>
GEMINI_API_KEY=<your-gemini-key>
ALLOWED_HOSTS=your-app.ondigitalocean.app
DEBUG=False

# Database (auto-filled by DigitalOcean)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${db.DATABASE}
DB_USER=${db.USERNAME}
DB_PASSWORD=${db.PASSWORD}
DB_HOST=${db.HOSTNAME}
DB_PORT=${db.PORT}
```

7. Click "Deploy"

### Step 4: Post-Deployment Setup

```bash
# SSH into your app (via DigitalOcean console)
python backend/manage.py createsuperuser

# Or run from local:
doctl apps create-deployment <app-id> --command "python backend/manage.py createsuperuser"
```

### Step 5: Test

Visit: `https://your-app.ondigitalocean.app/dashboard/`

---

## Alternative: Deploy to VPS (Advanced)

### Prerequisites

- Ubuntu 22.04 server
- Root or sudo access
- Domain name (optional)

### Step-by-Step

#### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql nginx redis-server git

# Create user
sudo useradd -m -s /bin/bash legalai
sudo usermod -aG sudo legalai
```

#### 2. PostgreSQL Setup

```bash
sudo -u postgres psql

CREATE DATABASE legalai_db;
CREATE USER legalai_user WITH PASSWORD 'secure-password-here';
ALTER ROLE legalai_user SET client_encoding TO 'utf8';
ALTER ROLE legalai_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE legalai_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE legalai_db TO legalai_user;
\q
```

#### 3. Clone & Setup Application

```bash
# Switch to app user
sudo su - legalai

# Clone repo
cd /var/www
git clone https://github.com/yourusername/legalai.git
cd legalai

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Create .env file
nano .env
# (Paste your environment variables)
```

#### 4. Django Setup

```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Create logs directory
mkdir -p logs
```

#### 5. Gunicorn Setup

```bash
# Copy systemd service
sudo cp /var/www/legalai/systemd.service.example /etc/systemd/system/legalai.service

# Edit paths in service file
sudo nano /etc/systemd/system/legalai.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable legalai
sudo systemctl start legalai
sudo systemctl status legalai
```

#### 6. Nginx Setup

```bash
# Copy nginx config
sudo cp /var/www/legalai/nginx.conf.example /etc/nginx/sites-available/legalai

# Edit domain name
sudo nano /etc/nginx/sites-available/legalai

# Enable site
sudo ln -s /etc/nginx/sites-available/legalai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. SSL Certificate

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 8. Celery Setup (Optional - Background Tasks)

```bash
sudo cp /var/www/legalai/celery.service.example /etc/systemd/system/celery.service
sudo systemctl enable celery
sudo systemctl start celery
```

#### 9. Firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## Post-Deployment Checklist

### Security
- [ ] `DEBUG = False` in production
- [ ] New `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enabled (SSL certificate)
- [ ] CORS restricted to specific origins
- [ ] Firewall configured
- [ ] Database password is strong

### Functionality
- [ ] Can access `/dashboard/`
- [ ] Can upload PDF
- [ ] Can generate drafts
- [ ] Can create cases
- [ ] Admin panel works (`/admin/`)
- [ ] API health check passes (`/api/health/`)

### Performance
- [ ] Static files loading fast
- [ ] Media uploads working
- [ ] Database queries optimized
- [ ] Caching configured (if using Redis)

### Monitoring
- [ ] Sentry configured (error tracking)
- [ ] Server logs accessible
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Disk space monitoring

---

## Maintenance

### Update Application

```bash
cd /var/www/legalai
bash deploy.sh
```

### Backup Database

```bash
# Create backup
pg_dump -U legalai_user legalai_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U legalai_user legalai_db < backup_20260101.sql
```

### View Logs

```bash
# Application logs
sudo journalctl -u legalai -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Gunicorn logs
sudo tail -f /var/log/gunicorn/access.log
```

### Restart Services

```bash
sudo systemctl restart legalai
sudo systemctl restart celery
sudo systemctl reload nginx
```

---

## Troubleshooting

### Issue: 502 Bad Gateway
**Cause:** Gunicorn not running
**Fix:**
```bash
sudo systemctl status legalai
sudo systemctl restart legalai
sudo journalctl -u legalai -n 50
```

### Issue: Static files not loading
**Cause:** Collectstatic not run
**Fix:**
```bash
cd /var/www/legalai/backend
python manage.py collectstatic --noinput
```

### Issue: Database connection error
**Cause:** Wrong credentials or PostgreSQL not running
**Fix:**
```bash
sudo systemctl status postgresql
# Check .env file for correct DB credentials
```

### Issue: Gemini API errors
**Cause:** Invalid API key or rate limit
**Fix:**
- Get new key: https://aistudio.google.com/app/apikey
- Update `.env` with `GEMINI_API_KEY`
- Restart: `sudo systemctl restart legalai`

---

## Cost Optimization Tips

1. **Use DigitalOcean App Platform Basic tier** ($12/mo) for MVP
2. **Compress images** before upload (reduce storage)
3. **Enable Redis caching** to reduce database queries
4. **Use CDN** for static files (Cloudflare free tier)
5. **Schedule Celery tasks** during off-peak hours
6. **Monitor Gemini API usage** (15 req/min free tier)

---

## Scaling Strategy

### 100 Users → 1,000 Users
- Upgrade to App Platform Pro ($24/mo)
- Add Redis cache
- Enable Celery for background tasks
- PostgreSQL 4GB plan

### 1,000+ Users
- Add load balancer
- Multi-instance deployment
- S3 for media storage
- Separate Celery workers
- Database read replicas

---

## Support

- **Documentation:** See `PRODUCTION_ROADMAP.md`
- **Logs:** Check `/var/log/gunicorn/` and `journalctl`
- **Health Check:** `https://yourdomain.com/api/health/`

---

**🎉 Congratulations! Your LegalAI is now in production!**
