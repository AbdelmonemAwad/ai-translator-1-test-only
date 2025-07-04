#!/bin/bash
"""
Ubuntu Server Fix Script for AI Translator
سكريبت إصلاح الخادم Ubuntu للترجمان الآلي
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Translator Ubuntu Server Fix Script ===${NC}"
echo -e "${BLUE}=== سكريبت إصلاح خادم Ubuntu للترجمان الآلي ===${NC}"

# Function to print status
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_info "Starting system diagnosis and fix..."

# 1. Update system packages
print_info "Updating system packages..."
apt update -y
apt upgrade -y

# 2. Install essential dependencies
print_info "Installing essential system dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
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
    lsb-release

print_status "System packages updated and installed"

# 3. Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_info "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) ]]; then
    print_status "Python version is compatible"
else
    print_error "Python version must be 3.9 or higher"
    exit 1
fi

# 4. Install Python packages globally (fix for flask_sqlalchemy issue)
print_info "Installing Python packages globally..."
pip3 install --upgrade pip
pip3 install \
    flask \
    flask-sqlalchemy \
    sqlalchemy \
    psycopg2-binary \
    gunicorn \
    werkzeug \
    jinja2 \
    requests \
    psutil \
    python-dotenv \
    pillow \
    opencv-python \
    numpy \
    pandas \
    paramiko \
    boto3 \
    torch \
    faster-whisper \
    pynvml \
    setuptools \
    wheel

print_status "Python packages installed"

# 5. Setup PostgreSQL database
print_info "Configuring PostgreSQL database..."

# Start PostgreSQL service
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;"
sudo -u postgres psql -c "DROP USER IF EXISTS ai_translator;"
sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
sudo -u postgres psql -c "CREATE USER ai_translator WITH ENCRYPTED PASSWORD 'ai_translator_pass2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
sudo -u postgres psql -c "ALTER USER ai_translator CREATEDB;"

print_status "PostgreSQL database configured"

# 6. Configure PostgreSQL authentication
print_info "Configuring PostgreSQL authentication..."

PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP 'PostgreSQL \K[0-9]+')
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

if [ -f "$PG_HBA" ]; then
    # Backup original file
    cp "$PG_HBA" "$PG_HBA.backup"
    
    # Update authentication method for local connections
    sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "$PG_HBA"
    sed -i 's/local   all             all                                     ident/local   all             all                                     md5/' "$PG_HBA"
    
    # Reload PostgreSQL configuration
    systemctl reload postgresql
    
    print_status "PostgreSQL authentication configured"
else
    print_warning "PostgreSQL configuration file not found at expected location"
fi

# 7. Test database connection
print_info "Testing database connection..."
PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status "Database connection test successful"
else
    print_error "Database connection test failed"
fi

# 8. Create AI Translator directory and download files
print_info "Setting up AI Translator application..."

APP_DIR="/root/ai-translator"
if [ -d "$APP_DIR" ]; then
    print_warning "Application directory exists, backing up..."
    mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Create requirements.txt for Ubuntu
cat > requirements.txt << 'EOF'
flask==3.0.0
flask-sqlalchemy==3.1.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
gunicorn==21.2.0
werkzeug==3.0.1
jinja2==3.1.2
requests==2.31.0
psutil==5.9.6
python-dotenv==1.0.0
pillow==10.1.0
opencv-python==4.8.1.78
numpy==1.26.4
pandas==2.1.4
paramiko==3.4.0
boto3==1.34.0
torch==2.1.2
faster-whisper==1.0.1
pynvml==11.5.0
setuptools==69.0.3
wheel==0.42.0
EOF

print_status "Requirements file created"

# 9. Create systemd service file
print_info "Creating systemd service..."

cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator v2.2.5 Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/root/ai-translator
Environment=PATH=/usr/bin:/usr/local/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=ubuntu-ai-translator-secret-key-2024
Environment=FLASK_ENV=production
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 main:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
print_status "Systemd service created"

# 10. Configure Nginx
print_info "Configuring Nginx reverse proxy..."

cat > /etc/nginx/sites-available/ai-translator << 'EOF'
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
        alias /root/ai-translator/static;
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

# 11. Create a simple test to verify the fix
print_info "Creating test script..."

cat > test_installation.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify AI Translator installation
سكريبت فحص للتأكد من تثبيت الترجمان الآلي
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'sqlalchemy',
        'psycopg2',
        'gunicorn',
        'werkzeug',
        'jinja2',
        'requests',
        'psutil',
        'PIL',
        'cv2',
        'numpy',
        'pandas',
        'paramiko',
        'boto3'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_database():
    """Test database connection"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="ai_translator",
            user="ai_translator",
            password="ai_translator_pass2024"
        )
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    print("=== AI Translator Installation Test ===")
    print("=== فحص تثبيت الترجمان الآلي ===")
    
    print("\n1. Testing Python imports...")
    failed = test_imports()
    
    print("\n2. Testing database connection...")
    db_ok = test_database()
    
    print("\n=== Test Results ===")
    if not failed and db_ok:
        print("✓ All tests passed! Installation is ready.")
        print("✓ جميع الاختبارات نجحت! التثبيت جاهز.")
        return True
    else:
        print("✗ Some tests failed. Check the output above.")
        print("✗ بعض الاختبارات فشلت. راجع النتائج أعلاه.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

chmod +x test_installation.py

print_status "Test script created"

# 12. Run the test
print_info "Running installation test..."
python3 test_installation.py

if [ $? -eq 0 ]; then
    print_status "Installation test passed!"
else
    print_error "Installation test failed!"
fi

# 13. Final instructions
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo -e "${GREEN}=== اكتمل التثبيت ===${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "${BLUE}الخطوات التالية:${NC}"
echo ""
echo "1. Copy your AI Translator files to: $APP_DIR"
echo "   انسخ ملفات الترجمان الآلي إلى: $APP_DIR"
echo ""
echo "2. Start the service:"
echo "   تشغيل الخدمة:"
echo "   systemctl start ai-translator"
echo "   systemctl enable ai-translator"
echo ""
echo "3. Check service status:"
echo "   فحص حالة الخدمة:"
echo "   systemctl status ai-translator"
echo ""
echo "4. View logs:"
echo "   عرض السجلات:"
echo "   journalctl -u ai-translator -f"
echo ""
echo "5. Access the application:"
echo "   الوصول للتطبيق:"
echo "   http://your-server-ip"
echo ""
echo -e "${GREEN}Database credentials:${NC}"
echo -e "${GREEN}بيانات قاعدة البيانات:${NC}"
echo "Host: localhost"
echo "Database: ai_translator"
echo "Username: ai_translator"  
echo "Password: ai_translator_pass2024"
echo ""
echo -e "${GREEN}Default login:${NC}"
echo -e "${GREEN}بيانات الدخول الافتراضية:${NC}"
echo "Username: admin"
echo "Password: your_strong_password"

print_status "Ubuntu Server fix script completed successfully!"