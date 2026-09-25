# 🔐 Security Considerations for LegalAI

## Critical Security Issues

### 🔴 HIGH PRIORITY (Fix Before Deployment)

#### 1. SECRET_KEY Exposure
**Issue:** Hardcoded in `settings.py`
**Risk:** Session hijacking, CSRF bypass
**Fix:**
```bash
python generate_secret_key.py
# Add to .env (never commit!)
```

#### 2. DEBUG = True
**Issue:** Debug mode enabled
**Risk:** Exposes sensitive stack traces, SQL queries
**Fix:** Set `DEBUG = False` in production settings

#### 3. CORS_ALLOW_ALL_ORIGINS
**Issue:** Accepts requests from any origin
**Risk:** CSRF attacks
**Fix:** Whitelist specific domains only

#### 4. Gemini API Key in Git History
**Issue:** API key may be committed
**Risk:** Unauthorized API usage, billing fraud
**Fix:**
- Revoke old key
- Generate new key
- Add to .env
- Check git history: `git log -p | grep GEMINI_API_KEY`

#### 5. No Authentication
**Issue:** Anyone can access any case
**Risk:** Data leakage, unauthorized access
**Fix:** Implement user authentication (see roadmap)

---

## Security Best Practices

### File Upload Security

```python
# Add to settings_prod.py
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.png']

def validate_file_upload(uploaded_file):
    # Check extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(f"File type {ext} not allowed")
    
    # Check MIME type
    import magic
    mime = magic.from_buffer(uploaded_file.read(1024), mime=True)
    uploaded_file.seek(0)
    
    allowed_mimes = ['application/pdf', 'application/msword', 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if mime not in allowed_mimes:
        raise ValidationError("Invalid file type")
    
    # Check file size (100MB max)
    if uploaded_file.size > 100 * 1024 * 1024:
        raise ValidationError("File too large (max 100MB)")
```

### SQL Injection Prevention
- ✅ Use Django ORM (already protected)
- ✅ Never use raw SQL with user input
- ✅ Use parameterized queries if raw SQL needed

### XSS Prevention
- ✅ Django templates auto-escape by default
- ✅ Use `|safe` filter carefully
- ✅ Sanitize user input

### CSRF Protection
- ✅ Django CSRF middleware enabled
- ✅ Use `{% csrf_token %}` in all forms
- ✅ AJAX requests include CSRF header

### Password Security
```python
# Use Django's built-in validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### API Rate Limiting
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}
```

---

## Environment Variables Security

### Never Commit These Files
```
.env
.env.*
*.env
backend/db.sqlite3
vault/  # Contains legal PDFs (potentially sensitive)
media/  # User uploaded files
```

### Secure Environment Variables
```bash
# Use strong passwords
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Restrict API keys
GEMINI_API_KEY=<regenerate-from-google>

# Add to .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

---

## Server Hardening

### SSH Security
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no
sudo systemctl restart sshd

# Use SSH keys only
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Fail2Ban (Brute Force Protection)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Data Protection

### Database Encryption
```python
# Use encrypted PostgreSQL
# Enable SSL connection
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}
```

### Media File Encryption
```bash
# Encrypt media folder
sudo apt install ecryptfs-utils
sudo mount -t ecryptfs /var/www/legalai/media /var/www/legalai/media
```

### Backup Encryption
```bash
# Encrypt backups with GPG
pg_dump legalai_db | gzip | gpg --encrypt --recipient your@email.com > backup.sql.gz.gpg
```

---

## Compliance

### GDPR Compliance
- [ ] User consent for data processing
- [ ] Right to data deletion
- [ ] Data portability (export feature)
- [ ] Privacy policy
- [ ] Cookie consent

### Medical Data (HIPAA-like)
- [ ] Encrypt at rest (database + files)
- [ ] Encrypt in transit (HTTPS)
- [ ] Access logs
- [ ] User authentication
- [ ] Audit trail

### Legal Compliance
- [ ] Disclaimer: "AI assists, does not replace lawyers"
- [ ] Terms of Service
- [ ] Professional liability insurance
- [ ] Data retention policy

---

## Security Checklist

### Pre-Deployment
- [ ] `DEBUG = False`
- [ ] New `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enabled
- [ ] CORS restricted
- [ ] File upload validation
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Database credentials secured
- [ ] `.env` not in git
- [ ] Gemini API key regenerated

### Post-Deployment
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] SSH hardened
- [ ] Backups automated
- [ ] Monitoring enabled (Sentry)
- [ ] Log rotation configured
- [ ] Security updates automated
- [ ] Penetration testing done

---

## Incident Response

### If Breach Detected
1. **Isolate:** Take server offline immediately
2. **Preserve:** Don't delete logs
3. **Investigate:** Check access logs
4. **Notify:** Inform affected users
5. **Patch:** Fix vulnerability
6. **Restore:** From clean backup
7. **Monitor:** Enhanced logging

### Emergency Contacts
- Server provider support
- Legal counsel
- Security consultant
- Insurance provider

---

## Security Tools

### Static Analysis
```bash
# Bandit (Python security linter)
pip install bandit
bandit -r backend/

# Safety (dependency vulnerability check)
pip install safety
safety check
```

### Penetration Testing
- OWASP ZAP (free)
- Burp Suite (free tier)
- SQLMap (SQL injection testing)

### Monitoring
- Sentry (error tracking)
- UptimeRobot (uptime monitoring)
- Cloudflare (DDoS protection)

---

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/5.1/topics/security/
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks

---

**⚠️ Security is an ongoing process, not a one-time task!**

Regular security audits recommended every 6 months.
