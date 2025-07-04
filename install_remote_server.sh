#!/bin/bash
"""
Universal Installation Script for AI Translator v2.2.5
سكريبت التثبيت العام للترجمان الآلي v2.2.5

Compatible with any Ubuntu Server 20.04+ with root access
متوافق مع أي خادم Ubuntu 20.04+ مع صلاحيات root
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

echo -e "${BLUE}=== AI Translator Remote Server Installation ===${NC}"
echo -e "${BLUE}=== تثبيت الخادم البعيد للترجمان الآلي ===${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   print_error "يجب تشغيل هذا السكريپت كـ root"
   print_info "Run: sudo $0"
   exit 1
fi

print_info "Starting remote server installation..."

# 1. Stop existing service if running
print_info "Stopping existing services..."
systemctl stop ai-translator 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 2. Update system packages
print_info "Updating system packages..."
apt update -y
apt upgrade -y

# 3. Install system dependencies
print_info "Installing system dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    build-essential \
    curl \
    wget \
    git \
    nano \
    htop \
    postgresql \
    postgresql-contrib \
    nginx \
    ffmpeg \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    bc

print_status "System dependencies installed"

# 4. Fix Python pip and install packages
print_info "Setting up Python environment..."
python3 -m pip install --upgrade pip
python3 -m pip install setuptools wheel

# Install Python packages with specific focus on flask-sqlalchemy
print_info "Installing Python packages (fixing flask_sqlalchemy issue)..."
python3 -m pip install --force-reinstall \
    flask==3.0.0 \
    flask-sqlalchemy==3.1.1 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    gunicorn==21.2.0 \
    werkzeug==3.0.1 \
    jinja2==3.1.2 \
    requests==2.31.0 \
    psutil==5.9.6 \
    python-dotenv==1.0.0 \
    pillow==10.1.0 \
    opencv-python==4.8.1.78 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    paramiko==3.4.0 \
    boto3==1.34.0 \
    torch==2.1.2 \
    faster-whisper==1.0.1 \
    pynvml==11.5.0

# Test flask_sqlalchemy import
print_info "Testing flask_sqlalchemy import..."
python3 -c "from flask_sqlalchemy import SQLAlchemy; print('✅ flask_sqlalchemy working')" || {
    print_error "flask_sqlalchemy import failed. Trying alternative installation..."
    apt install -y python3-flask python3-flask-sqlalchemy
    python3 -c "from flask_sqlalchemy import SQLAlchemy; print('✅ flask_sqlalchemy working')"
}

print_status "Python packages installed successfully"

# 5. Setup PostgreSQL
print_info "Configuring PostgreSQL..."

# Start and enable PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Configure PostgreSQL database
sudo -u postgres psql << 'EOF'
DROP DATABASE IF EXISTS ai_translator;
DROP USER IF EXISTS ai_translator;
CREATE DATABASE ai_translator;
CREATE USER ai_translator WITH ENCRYPTED PASSWORD 'ai_translator_pass2024';
GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;
ALTER USER ai_translator CREATEDB;
\q
EOF

# Update pg_hba.conf for md5 authentication
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP 'PostgreSQL \K[0-9]+')
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

if [ -f "$PG_HBA" ]; then
    cp "$PG_HBA" "$PG_HBA.backup"
    sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "$PG_HBA"
    sed -i 's/local   all             all                                     ident/local   all             all                                     md5/' "$PG_HBA"
    systemctl reload postgresql
fi

# Test database connection
print_info "Testing database connection..."
PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status "Database connection successful"
else
    print_error "Database connection failed"
    exit 1
fi

# 6. Setup application directory
print_info "Setting up application directory..."

# Determine installation directory based on current user
if [ "$USER" = "root" ]; then
    APP_DIR="/root/ai-translator"
else
    APP_DIR="/home/$USER/ai-translator"
fi

print_info "Installing to: $APP_DIR"

# Backup existing installation
if [ -d "$APP_DIR" ]; then
    print_warning "Backing up existing installation..."
    mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create parent directory if needed
mkdir -p "$(dirname "$APP_DIR")"

# Download from GitHub (latest)
print_info "Downloading AI Translator from GitHub..."
cd "$(dirname "$APP_DIR")"
git clone https://github.com/AbdelmonemAwad/ai-translator.git || {
    print_warning "Git clone failed, downloading zip..."
    wget -O ai-translator.zip https://github.com/AbdelmonemAwad/ai-translator/archive/main.zip
    apt install -y unzip
    unzip ai-translator.zip
    mv ai-translator-main ai-translator
    rm ai-translator.zip
}

cd "$APP_DIR"

# Install additional requirements if present
if [ -f "requirements_github.txt" ]; then
    print_info "Installing additional requirements..."
    python3 -m pip install -r requirements_github.txt
fi

print_status "Application files downloaded"

# 7. Create systemd service
print_info "Creating systemd service..."

# Determine service user and group
if [ "$USER" = "root" ]; then
    SERVICE_USER="root"
    SERVICE_GROUP="root"
    USER_HOME="/root"
else
    SERVICE_USER="$USER"
    SERVICE_GROUP="$USER"
    USER_HOME="/home/$USER"
fi

cat > /etc/systemd/system/ai-translator.service << EOF
[Unit]
Description=AI Translator v2.2.5 Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
Environment=PATH=/usr/bin:/usr/local/bin:$USER_HOME/.local/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=ubuntu-ai-translator-secret-key-2024
Environment=FLASK_ENV=production
Environment=PYTHONPATH=$APP_DIR
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 --access-logfile - --error-logfile - main:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
KillMode=mixed
KillSignal=SIGINT
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ai-translator

print_status "Systemd service created"

# 8. Configure Nginx
print_info "Configuring Nginx..."

cat > /etc/nginx/sites-available/ai-translator << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 500M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
    systemctl enable nginx
    print_status "Nginx configured and started"
else
    print_error "Nginx configuration test failed"
fi

# 9. Set proper permissions
print_info "Setting file permissions..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
chmod +x "$APP_DIR/main.py" 2>/dev/null || true
chmod 755 "$APP_DIR"

# 10. Start services
print_info "Starting services..."

# Start AI Translator
systemctl start ai-translator
sleep 3

# Check service status
if systemctl is-active --quiet ai-translator; then
    print_status "AI Translator service started successfully"
else
    print_error "AI Translator service failed to start"
    print_info "Checking logs..."
    journalctl -u ai-translator --no-pager -n 20
fi

# Check nginx status
if systemctl is-active --quiet nginx; then
    print_status "Nginx service is running"
else
    print_warning "Nginx service not running"
fi

# 11. Final verification
print_info "Running final verification..."

# Test Python imports
python3 -c "
try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    import psycopg2
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test HTTP response
sleep 5
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ || echo "000")
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 302 ]; then
    print_status "HTTP service responding correctly (Status: $HTTP_STATUS)"
else
    print_warning "HTTP service not responding correctly (Status: $HTTP_STATUS)"
fi

# 12. Display final status
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo -e "${GREEN}=== اكتمل التثبيت ===${NC}"
echo ""
echo -e "${BLUE}Service Status:${NC}"
systemctl status ai-translator --no-pager -l
echo ""
echo -e "${BLUE}Access Information:${NC}"
echo -e "${GREEN}Application URL: http://$(curl -s ifconfig.me)${NC}"
echo -e "${GREEN}Default Login: admin / your_strong_password${NC}"
echo ""
echo -e "${BLUE}Management Commands:${NC}"
echo "View logs: journalctl -u ai-translator -f"
echo "Restart service: systemctl restart ai-translator"
echo "Check status: systemctl status ai-translator"
echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${GREEN}تم اكتمال التثبيت بنجاح!${NC}"