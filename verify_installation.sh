#!/bin/bash

# AI Translator Installation Verification Script
# فحص صحة تثبيت الترجمان الآلي

echo "🔍 AI Translator Installation Verification"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

# 1. Check Python Virtual Environment
echo "🐍 Checking Python Virtual Environment..."
if [ -d "/opt/ai-translator-venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists at /opt/ai-translator-venv${NC}"
    
    # Check if gunicorn exists in venv
    if [ -f "/opt/ai-translator-venv/bin/gunicorn" ]; then
        echo -e "${GREEN}✅ Gunicorn installed in virtual environment${NC}"
    else
        echo -e "${RED}❌ Gunicorn missing in virtual environment${NC}"
    fi
    
    # Check Python packages
    /opt/ai-translator-venv/bin/pip list | grep -E "(flask|sqlalchemy|gunicorn)" >/dev/null
    check_success "Required Python packages installed"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
fi

# 2. Check Application Directory
echo "📁 Checking Application Files..."
if [ -d "/opt/ai-translator" ]; then
    echo -e "${GREEN}✅ Application directory exists${NC}"
    
    # Check main files
    for file in app.py main.py models.py; do
        if [ -f "/opt/ai-translator/$file" ]; then
            echo -e "${GREEN}✅ $file exists${NC}"
        else
            echo -e "${RED}❌ $file missing${NC}"
        fi
    done
else
    echo -e "${RED}❌ Application directory not found${NC}"
fi

# 3. Check PostgreSQL Database
echo "🗄️ Checking PostgreSQL Database..."
systemctl is-active --quiet postgresql
check_success "PostgreSQL service running"

sudo -u postgres psql -d ai_translator -c "SELECT 1;" >/dev/null 2>&1
check_success "Database connection working"

# 4. Check Systemd Service
echo "⚙️ Checking System Service..."
if [ -f "/etc/systemd/system/ai-translator.service" ]; then
    echo -e "${GREEN}✅ Service file exists${NC}"
    
    systemctl is-enabled --quiet ai-translator
    check_success "Service enabled"
    
    systemctl is-active --quiet ai-translator
    check_success "Service running"
else
    echo -e "${RED}❌ Service file not found${NC}"
fi

# 5. Check Nginx Configuration
echo "🌐 Checking Nginx Configuration..."
if [ -f "/etc/nginx/sites-available/ai-translator" ]; then
    echo -e "${GREEN}✅ Nginx configuration exists${NC}"
    
    nginx -t >/dev/null 2>&1
    check_success "Nginx configuration valid"
    
    systemctl is-active --quiet nginx
    check_success "Nginx service running"
else
    echo -e "${RED}❌ Nginx configuration not found${NC}"
fi

# 6. Check Network Connectivity
echo "🌍 Checking Network Access..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302"
check_success "Application responding on port 5000"

# 7. Show Service Status
echo ""
echo "📊 Service Status Summary:"
echo "========================="
systemctl status ai-translator --no-pager -l | head -10

echo ""
echo "🔗 Access Information:"
echo "====================="
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 Local Access: http://$LOCAL_IP"
echo "🔐 Default Login: admin / your_strong_password"

echo ""
echo "✅ Verification completed!"