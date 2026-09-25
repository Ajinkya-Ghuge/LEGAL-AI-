# Dockerfile for LegalAI
# Multi-stage build for optimized production image

# ── Stage 1: Base ──────────────────────────────────────────────────────────────
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 legalai && \
    mkdir -p /app /app/staticfiles /app/media /app/logs && \
    chown -R legalai:legalai /app

WORKDIR /app

# ── Stage 2: Dependencies ──────────────────────────────────────────────────────
FROM base as dependencies

# Copy requirements
COPY requirements-prod.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements-prod.txt

# ── Stage 3: Application ───────────────────────────────────────────────────────
FROM dependencies as application

# Copy application code
COPY --chown=legalai:legalai ./backend /app/backend
COPY --chown=legalai:legalai ./templates /app/templates
COPY --chown=legalai:legalai ./vault /app/vault
COPY --chown=legalai:legalai gunicorn.conf.py /app/

# Switch to app user
USER legalai

# Collect static files
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')" || exit 1

# Start Gunicorn
CMD ["gunicorn", "legalai.wsgi:application", \
     "--config", "/app/gunicorn.conf.py", \
     "--bind", "0.0.0.0:8000"]
