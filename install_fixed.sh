#!/bin/bash
# AI Translator v2.2.5 - Fixed Installation Script
# المترجم الآلي v2.2.5 - سكريبت التثبيت المحسن

set -e

echo "🚀 AI Translator v2.2.5 - Fixed Installation Starting..."
echo "   المترجم الآلي v2.2.5 - بدء التثبيت المحسن..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Consider creating a dedicated user for the application."
fi

# Update system packages
print_info "Updating system packages..."
sudo apt update

# Install system dependencies
print_info "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    ffmpeg \
    git \
    curl \
    build-essential \
    pkg-config \
    libpq-dev \
    nginx

# Clone repository
print_info "Cloning AI Translator repository..."
if [ -d "ai-translator" ]; then
    print_warning "Directory ai-translator already exists. Removing..."
    rm -rf ai-translator
fi

git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies - FIX: Install Flask-SQLAlchemy explicitly
print_info "Installing Python dependencies..."
pip install --upgrade pip

# Install core dependencies first
pip install \
    Flask>=3.0.0 \
    Flask-SQLAlchemy>=3.1.1 \
    Gunicorn>=21.2.0 \
    Werkzeug>=3.0.1 \
    SQLAlchemy>=2.0.23 \
    psycopg2-binary>=2.9.9 \
    psutil>=5.9.6 \
    pynvml>=11.5.0 \
    requests>=2.31.0 \
    python-dotenv>=1.0.0

# Install additional dependencies
pip install \
    opencv-python>=4.8.1.78 \
    Pillow>=10.1.0 \
    "numpy>=1.26.4,<2.0.0" \
    torch>=2.0.1 \
    faster-whisper>=1.0.1 \
    torchaudio>=2.0.2 \
    torchvision>=0.15.2 \
    paramiko>=3.3.1 \
    boto3>=1.34.4 \
    setuptools>=69.0.2

# Try to install from requirements if it exists
if [ -f "requirements_github.txt" ]; then
    print_info "Installing additional requirements from requirements_github.txt..."
    pip install -r requirements_github.txt || print_warning "Some optional dependencies may not have installed"
fi

# Setup PostgreSQL database
print_info "Setting up PostgreSQL database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS ai_translator;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"

# Set environment variables
print_info "Setting up environment variables..."
cat > .env << EOF
DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
EOF

# Initialize database
print_info "Initializing database schema..."
export DATABASE_URL="postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator"
export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Test imports before database setup
print_info "Testing Python imports..."
python3 -c "
import sys
try:
    from flask_sqlalchemy import SQLAlchemy
    print('✓ Flask-SQLAlchemy imported successfully')
    import flask
    print('✓ Flask imported successfully')
    import sqlalchemy
    print('✓ SQLAlchemy imported successfully')
    import psycopg2
    print('✓ psycopg2 imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

# Initialize database if imports successful
if [ -f "database_setup.py" ]; then
    python database_setup.py
else
    print_warning "database_setup.py not found. Database initialization skipped."
fi

# Create systemd service
print_info "Creating systemd service..."
sudo tee /etc/systemd/system/ai-translator.service > /dev/null << EOF
[Unit]
Description=AI Translator v2.2.5 Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/ai-translator
ExecStart=/root/ai-translator/venv/bin/python -m gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 main:app
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
Environment=FLASK_ENV=production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
print_info "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/ai-translator > /dev/null << EOF
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Enable and start services
print_info "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ai-translator
sudo systemctl enable nginx
sudo systemctl restart nginx

# Start AI Translator service
print_info "Starting AI Translator service..."
sudo systemctl start ai-translator

# Check service status
sleep 5
if sudo systemctl is-active --quiet ai-translator; then
    print_status "AI Translator service is running successfully!"
else
    print_error "AI Translator service failed to start. Checking logs..."
    sudo journalctl -u ai-translator --no-pager -n 20
fi

# Display installation summary
print_status "Installation completed!"
print_info "Service status: $(sudo systemctl is-active ai-translator)"
print_info "Access your application at: http://$(hostname -I | awk '{print $1}')"
print_info "Default credentials: admin / your_strong_password"
print_info "Database: ai_translator"
print_info "Service logs: sudo journalctl -u ai-translator -f"

echo ""
echo "🎉 AI Translator v2.2.5 Installation Complete!"
echo "   المترجم الآلي v2.2.5 - اكتمل التثبيت!"