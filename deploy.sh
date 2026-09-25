#!/bin/bash
# LegalAI Deployment Script for DigitalOcean/VPS
# Usage: bash deploy.sh

set -e  # Exit on error

echo "🚀 Starting LegalAI deployment..."

# Variables
APP_DIR="/var/www/legalai"
VENV_DIR="$APP_DIR/venv"
BACKEND_DIR="$APP_DIR/backend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Pull latest code
echo -e "${YELLOW}📦 Pulling latest code from Git...${NC}"
cd $APP_DIR
git pull origin main

# Step 2: Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Step 3: Install/update dependencies
echo -e "${YELLOW}📚 Installing dependencies...${NC}"
pip install -r requirements-prod.txt --upgrade

# Step 4: Run migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
cd $BACKEND_DIR
python manage.py migrate --noinput

# Step 5: Collect static files
echo -e "${YELLOW}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Step 6: Clear cache (if Redis is configured)
echo -e "${YELLOW}🧹 Clearing cache...${NC}"
python manage.py shell <<EOF
from django.core.cache import cache
cache.clear()
print("Cache cleared!")
EOF

# Step 7: Restart services
echo -e "${YELLOW}♻️  Restarting services...${NC}"
sudo systemctl restart legalai
sudo systemctl restart celery
sudo systemctl reload nginx

# Step 8: Check status
echo -e "${YELLOW}✅ Checking service status...${NC}"
sudo systemctl status legalai --no-pager
sudo systemctl status celery --no-pager

# Step 9: Health check
echo -e "${YELLOW}🏥 Running health check...${NC}"
sleep 3
curl -f http://localhost:8000/api/health/ || echo -e "${RED}❌ Health check failed!${NC}"

echo -e "${GREEN}✨ Deployment complete!${NC}"
echo -e "${GREEN}Visit: https://yourdomain.com${NC}"
