#!/bin/bash

# AI Translator Service Setup Script
# سكريپت إعداد خدمة المترجم الآلي

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running as root
check_root() {
    [[ $EUID -eq 0 ]] || error "يجب تشغيل هذا السكريبت بصلاحية المدير: sudo $0"
}

# Check if app exists
check_app() {
    log "فحص وجود التطبيق..."
    
    if [[ ! -d "/opt/ai-translator" ]]; then
        error "مجلد التطبيق غير موجود في /opt/ai-translator"
    fi
    
    if [[ ! -f "/opt/ai-translator/main.py" ]]; then
        error "ملف main.py غير موجود"
    fi
    
    log "✓ التطبيق موجود"
}

# Check virtual environment
check_venv() {
    log "فحص البيئة الافتراضية..."
    
    if [[ ! -d "/opt/ai-translator-venv" ]]; then
        warn "البيئة الافتراضية غير موجودة، سيتم إنشاؤها..."
        python3 -m venv /opt/ai-translator-venv
        /opt/ai-translator-venv/bin/pip install --upgrade pip
        /opt/ai-translator-venv/bin/pip install \
            flask==3.0.0 \
            flask-sqlalchemy==3.1.1 \
            gunicorn==21.2.0 \
            psutil==5.9.6 \
            psycopg2-binary==2.9.7 \
            requests==2.31.0 \
            werkzeug==3.0.1 \
            email-validator==2.1.0 \
            pynvml==11.5.0
    fi
    
    log "✓ البيئة الافتراضية جاهزة"
}

# Setup database
setup_database() {
    log "إعداد قاعدة البيانات..."
    
    # Start PostgreSQL if not running
    if ! systemctl is-active --quiet postgresql; then
        systemctl start postgresql
        systemctl enable postgresql
    fi
    
    # Create database and user
    sudo -u postgres createdb ai_translator 2>/dev/null || warn "قاعدة البيانات موجودة مسبقاً"
    sudo -u postgres createuser ai_translator 2>/dev/null || warn "المستخدم موجود مسبقاً"
    sudo -u postgres psql -c "ALTER USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
    
    log "✓ قاعدة البيانات جاهزة"
}

# Create systemd service
create_service() {
    log "إنشاء خدمة النظام..."
    
    cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator Service (المترجم الآلي)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-translator
Environment=PATH=/opt/ai-translator-venv/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=FLASK_SECRET_KEY=ai_translator_secret_key_2024
Environment=SESSION_SECRET=ai_translator_session_secret_2024
ExecStart=/opt/ai-translator-venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 --preload main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Set permissions
    chown -R www-data:www-data /opt/ai-translator
    chmod -R 755 /opt/ai-translator
    
    # Reload systemd
    systemctl daemon-reload
    systemctl enable ai-translator
    
    log "✓ تم إنشاء خدمة النظام"
}

# Setup Nginx configuration
setup_nginx() {
    log "إعداد Nginx..."
    
    cat > /etc/nginx/sites-available/ai-translator << 'EOF'
server {
    listen 80 default_server;
    server_name _;
    
    client_max_body_size 100M;
    client_body_timeout 300;
    client_header_timeout 300;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        proxy_buffering off;
    }
    
    location /static/ {
        alias /opt/ai-translator/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site and remove default
    ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    if nginx -t; then
        systemctl reload nginx
        log "✓ تم إعداد Nginx"
    else
        error "خطأ في تكوين Nginx"
    fi
}

# Initialize database
init_database() {
    log "تهيئة قاعدة البيانات..."
    
    cd /opt/ai-translator
    
    # Set environment variables
    export DATABASE_URL="postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator"
    export FLASK_SECRET_KEY="ai_translator_secret_key_2024"
    export SESSION_SECRET="ai_translator_session_secret_2024"
    
    # Initialize database
    if [[ -f "database_setup.py" ]]; then
        /opt/ai-translator-venv/bin/python database_setup.py || warn "فشل في تهيئة قاعدة البيانات"
    else
        warn "ملف database_setup.py غير موجود"
    fi
    
    log "✓ تم تهيئة قاعدة البيانات"
}

# Start services
start_services() {
    log "تشغيل الخدمات..."
    
    # Start AI Translator service
    systemctl start ai-translator
    sleep 3
    
    # Check status
    if systemctl is-active --quiet ai-translator; then
        log "✓ خدمة ai-translator تعمل"
    else
        error "فشل في تشغيل خدمة ai-translator"
    fi
    
    # Start Nginx
    if ! systemctl is-active --quiet nginx; then
        systemctl start nginx
    fi
    
    log "✓ جميع الخدمات تعمل"
}

# Test connection
test_connection() {
    log "اختبار الاتصال..."
    
    sleep 5
    
    # Test Flask directly
    if curl -s -m 10 http://localhost:5000 >/dev/null; then
        log "✓ Flask يستجيب على المنفذ 5000"
    else
        warn "Flask لا يستجيب على المنفذ 5000"
    fi
    
    # Test Nginx
    if curl -s -m 10 http://localhost >/dev/null; then
        log "✓ Nginx يستجيب على المنفذ 80"
    else
        warn "Nginx لا يستجيب على المنفذ 80"
    fi
    
    # Get IP and test
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if curl -s -m 10 http://$LOCAL_IP >/dev/null; then
        log "✓ التطبيق يستجيب على $LOCAL_IP"
    else
        warn "التطبيق لا يستجيب على $LOCAL_IP"
    fi
}

# Show status
show_status() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "                      حالة الخدمات"
    echo "=================================================================="
    echo -e "${NC}"
    
    echo "🔧 حالة ai-translator:"
    systemctl status ai-translator --no-pager -l || true
    echo ""
    
    echo "🌐 المنافذ المفتوحة:"
    ss -tlnp | grep -E "(80|5000)" || echo "لا توجد منافذ مفتوحة"
    echo ""
    
    echo "📊 العمليات:"
    ps aux | grep -E "(gunicorn|nginx)" | grep -v grep || echo "لا توجد عمليات"
    echo ""
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "                   إعداد خدمة المترجم الآلي"
    echo "=================================================================="
    echo -e "${NC}"
    
    check_root
    check_app
    check_venv
    setup_database
    create_service
    setup_nginx
    init_database
    start_services
    test_connection
    show_status
    
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "                        تم الإعداد بنجاح!"
    echo "=================================================================="
    echo "🌐 الوصول للتطبيق: http://$(hostname -I | awk '{print $1}')"
    echo "👤 اسم المستخدم: admin"
    echo "🔑 كلمة المرور: your_strong_password"
    echo ""
    echo "📋 أوامر مفيدة:"
    echo "• حالة الخدمة: sudo systemctl status ai-translator"
    echo "• إعادة تشغيل: sudo systemctl restart ai-translator"
    echo "• عرض السجلات: sudo journalctl -u ai-translator -f"
    echo "=================================================================="
    echo -e "${NC}"
}

# Run main function
main "$@"