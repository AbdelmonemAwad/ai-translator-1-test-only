#!/bin/bash

# AI Translator Ubuntu Installation with Virtual Environment
# تثبيت المترجم الآلي على Ubuntu مع البيئة الافتراضية

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "        AI Translator Ubuntu Installation (Virtual Environment)"
    echo "        تثبيت المترجم الآلي على Ubuntu مع البيئة الافتراضية"
    echo "=================================================================="
    echo -e "${NC}"
}

# Check if running as root
check_root() {
    [[ $EUID -eq 0 ]] || error "يجب تشغيل هذا السكريبت بصلاحية المدير: sudo $0"
}

# Install system dependencies
install_system_deps() {
    log "تثبيت متطلبات النظام..."
    
    apt update
    apt install -y \
        python3 python3-venv python3-full python3-dev python3-pip \
        postgresql postgresql-contrib \
        nginx systemctl \
        build-essential pkg-config \
        libpq-dev libffi-dev libssl-dev \
        ffmpeg mediainfo \
        curl wget git unzip htop
    
    log "تم تثبيت متطلبات النظام ✓"
}

# Setup PostgreSQL
setup_database() {
    log "إعداد قاعدة البيانات PostgreSQL..."
    
    systemctl start postgresql
    systemctl enable postgresql
    
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
    python3 -m venv "$VENV_DIR"
    
    # Install packages in virtual environment
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/pip" install \
        flask==3.0.0 \
        flask-sqlalchemy==3.1.1 \
        gunicorn==21.2.0 \
        psutil==5.9.6 \
        psycopg2-binary==2.9.9 \
        requests==2.31.0 \
        werkzeug==3.0.1 \
        email-validator==2.1.0
    
    log "تم إنشاء البيئة الافتراضية ✓"
}

# Setup application
setup_application() {
    log "إعداد التطبيق..."
    
    # Create application directory
    mkdir -p /opt/ai-translator
    
    # Copy application files (assuming we're in the source directory)
    if [[ -f "app.py" ]]; then
        cp -r . /opt/ai-translator/
        log "تم نسخ ملفات التطبيق من المجلد الحالي"
    else
        error "ملف app.py غير موجود. تأكد من تشغيل السكريبت من داخل مجلد ai-translator"
    fi
    
    # Create service user
    useradd -r -s /bin/false ai-translator 2>/dev/null || warn "المستخدم موجود مسبقاً"
    
    # Set permissions
    chown -R ai-translator:ai-translator /opt/ai-translator
    chown -R ai-translator:ai-translator /opt/ai-translator-venv
    
    log "تم إعداد التطبيق ✓"
}

# Create systemd service
create_service() {
    log "إنشاء خدمة النظام..."
    
    cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator Service (المترجم الآلي)
After=network.target postgresql.service

[Service]
Type=exec
User=ai-translator
Group=ai-translator
WorkingDirectory=/opt/ai-translator
ExecStart=/opt/ai-translator-venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
Restart=always
RestartSec=5
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ai-translator
    
    log "تم إنشاء خدمة النظام ✓"
}

# Configure Nginx
configure_nginx() {
    log "إعداد Nginx..."
    
    cat > /etc/nginx/sites-available/ai-translator << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart nginx
    nginx -t && systemctl restart nginx
    
    log "تم إعداد Nginx ✓"
}

# Start services
start_services() {
    log "بدء تشغيل الخدمات..."
    
    systemctl start ai-translator
    systemctl start nginx
    
    # Wait and check status
    sleep 5
    
    if systemctl is-active --quiet ai-translator; then
        SERVICE_STATUS="✅ تعمل بشكل صحيح"
    else
        SERVICE_STATUS="❌ فشل في التشغيل"
    fi
    
    log "حالة الخدمة: $SERVICE_STATUS"
}

# Main installation function
main() {
    print_header
    
    check_root
    install_system_deps
    setup_database
    setup_virtual_env
    setup_application
    create_service
    configure_nginx
    start_services
    
    echo ""
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "                    تم التثبيت بنجاح!"
    echo "                Installation Completed Successfully!"
    echo "=================================================================="
    echo -e "${NC}"
    echo ""
    echo "🌐 رابط التطبيق: http://$(hostname -I | awk '{print $1}')"
    echo "🔐 بيانات الدخول: admin / your_strong_password"
    echo ""
    echo "📋 أوامر مفيدة:"
    echo "   sudo systemctl status ai-translator    # حالة الخدمة"
    echo "   sudo systemctl restart ai-translator   # إعادة تشغيل"
    echo "   sudo journalctl -u ai-translator -f    # عرض السجلات"
    echo ""
    echo "📁 المسارات:"
    echo "   التطبيق: /opt/ai-translator"
    echo "   البيئة الافتراضية: /opt/ai-translator-venv"
    echo "   قاعدة البيانات: postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator"
    echo ""
    
    # Final status check
    if systemctl is-active --quiet ai-translator && systemctl is-active --quiet nginx; then
        echo -e "${GREEN}🎉 جميع الخدمات تعمل بشكل صحيح!${NC}"
    else
        echo -e "${RED}⚠️ تحقق من حالة الخدمات باستخدام: sudo systemctl status ai-translator${NC}"
    fi
}

# Run main function
main "$@"