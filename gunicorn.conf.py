# Gunicorn Configuration for LegalAI
# Usage: gunicorn -c gunicorn.conf.py legalai.wsgi:application

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for long AI processing
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "legalai"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if not using Nginx)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Server hooks
def on_starting(server):
    print("🚀 Starting LegalAI Gunicorn server...")

def on_reload(server):
    print("♻️  Reloading LegalAI...")

def when_ready(server):
    print(f"✅ LegalAI ready on {bind}")

def on_exit(server):
    print("👋 LegalAI shutting down...")
