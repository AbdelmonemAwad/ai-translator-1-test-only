#!/bin/bash

# AI Translator Ubuntu Installation with Virtual Environment (Fixed)
# تثبيت المترجم الآلي على Ubuntu مع البيئة الافتراضية (محدث)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Check if running as root
check_root() {
    [[ $EUID -eq 0 ]] || error "يجب تشغيل هذا السكريبت بصلاحية المدير: sudo $0"
}

# System update
update_system() {
    log "تحديث النظام..."
    apt update && apt upgrade -y
    log "تم تحديث النظام ✓"
}

# Install system dependencies (Fixed version)
install_system_deps() {
    log "تثبيت متطلبات النظام..."
    
    apt update
    
    # Install packages one by one to avoid dependency conflicts
    log "تثبيت Python..."
    apt install -y python3 python3-venv python3-full python3-dev python3-pip
    
    log "تثبيت PostgreSQL..."
    apt install -y postgresql postgresql-contrib
    
    log "تثبيت Nginx..."
    apt install -y nginx
    
    log "تثبيت أدوات البناء..."
    apt install -y build-essential pkg-config
    
    log "تثبيت مكتبات التطوير..."
    apt install -y libpq-dev libffi-dev libssl-dev
    
    log "تثبيت أدوات الوسائط..."
    apt install -y ffmpeg mediainfo
    
    log "تثبيت الأدوات الأساسية..."
    apt install -y curl wget git unzip htop nano vim
    
    # Ensure systemd is working
    systemctl --version >/dev/null 2>&1 || warn "systemctl غير متوفر - قد تحتاج لإعادة تشغيل النظام"
    
    log "تم تثبيت متطلبات النظام ✓"
}

# Setup PostgreSQL
setup_database() {
    log "إعداد قاعدة البيانات PostgreSQL..."
    
    # Start PostgreSQL
    if systemctl is-active --quiet postgresql; then
        log "PostgreSQL يعمل بالفعل"
    else
        systemctl start postgresql
        systemctl enable postgresql
        log "تم تشغيل PostgreSQL"
    fi
    
    # Create database and user
    sudo -u postgres createdb ai_translator 2>/dev/null || warn "قاعدة البيانات موجودة مسبقاً"
    sudo -u postgres createuser ai_translator 2>/dev/null || warn "المستخدم موجود مسبقاً"
    sudo -u postgres psql -c "ALTER USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
    
    log "تم إعداد قاعدة البيانات ✓"
}

# Create virtual environment and install packages
setup_virtual_env() {
    log "إنشاء البيئة الافتراضية وتثبيت الحزم..."
    
    # Create virtual environment
    VENV_DIR="/opt/ai-translator-venv"
    rm -rf "$VENV_DIR" 2>/dev/null || true
    python3 -m venv "$VENV_DIR"
    
    # Install packages in virtual environment
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/pip" install \
        flask==3.0.0 \
        flask-sqlalchemy==3.1.1 \
        gunicorn==21.2.0 \
        psutil==5.9.6 \
        psycopg2-binary==2.9.7 \
        requests==2.31.0 \
        werkzeug==3.0.1 \
        email-validator==2.1.0 \
        pynvml==11.5.0
    
    log "تم إنشاء البيئة الافتراضية ✓"
}

# Download application
download_app() {
    log "تحميل التطبيق..."
    
    APP_DIR="/opt/ai-translator"
    rm -rf "$APP_DIR" 2>/dev/null || true
    mkdir -p "$APP_DIR"
    
    # Download from GitHub
    cd /tmp
    curl -L -o ai-translator.zip "https://github.com/AbdelmonemAwad/ai-translator/archive/main.zip"
    unzip -q ai-translator.zip
    cp -r ai-translator-main/* "$APP_DIR/"
    rm -rf ai-translator.zip ai-translator-main
    
    # Set permissions
    chown -R www-data:www-data "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    
    log "تم تحميل التطبيق ✓"
}

# Setup systemd service
setup_service() {
    log "إعداد خدمة النظام..."
    
    cat > /etc/systemd/system/ai-translator.service << EOF
[Unit]
Description=AI Translator Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-translator
Environment=PATH=/opt/ai-translator-venv/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=FLASK_SECRET_KEY=your_secret_key_here_$(openssl rand -hex 16)
ExecStart=/opt/ai-translator-venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ai-translator
    
    log "تم إعداد خدمة النظام ✓"
}

# Setup Nginx
setup_nginx() {
    log "إعداد Nginx..."
    
    cat > /etc/nginx/sites-available/ai-translator << EOF
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
    
    # Enable site
    ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
    
    log "تم إعداد Nginx ✓"
}

# Initialize database
init_database() {
    log "تهيئة قاعدة البيانات..."
    
    cd /opt/ai-translator
    /opt/ai-translator-venv/bin/python -c "
from database_setup import create_database
create_database()
print('Database initialized successfully')
" || warn "فشل في تهيئة قاعدة البيانات - سيتم تهيئتها عند أول تشغيل"
    
    log "تم تهيئة قاعدة البيانات ✓"
}

# Start services
start_services() {
    log "تشغيل الخدمات..."
    
    systemctl start ai-translator
    systemctl status ai-translator --no-pager -l
    
    log "تم تشغيل الخدمات ✓"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "        AI Translator Ubuntu Installation (Virtual Environment)"
    echo "        تثبيت المترجم الآلي على Ubuntu مع البيئة الافتراضية"
    echo "=================================================================="
    echo -e "${NC}"
    
    check_root
    update_system
    install_system_deps
    setup_database
    setup_virtual_env
    download_app
    setup_service
    setup_nginx
    init_database
    start_services
    
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "                 تم التثبيت بنجاح!"
    echo "=================================================================="
    echo -e "${NC}"
    echo "🌐 الوصول للتطبيق: http://$(hostname -I | awk '{print $1}')"
    echo "👤 اسم المستخدم: admin"
    echo "🔑 كلمة المرور: your_strong_password"
    echo ""
    echo "📋 أوامر مفيدة:"
    echo "• حالة الخدمة: sudo systemctl status ai-translator"
    echo "• إعادة تشغيل: sudo systemctl restart ai-translator"
    echo "• عرض السجلات: sudo journalctl -u ai-translator -f"
    echo ""
    echo "📖 للمساعدة: https://github.com/AbdelmonemAwad/ai-translator"
}

# Run main function
main "$@"