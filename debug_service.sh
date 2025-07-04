#!/bin/bash

# Debug AI Translator Service Issues
# تشخيص مشاكل خدمة المترجم الآلي

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
}

# Check if files exist
check_files() {
    log "فحص الملفات المطلوبة..."
    
    if [[ ! -d "/opt/ai-translator" ]]; then
        error "مجلد التطبيق غير موجود"
        return 1
    fi
    
    if [[ ! -f "/opt/ai-translator/main.py" ]]; then
        error "ملف main.py غير موجود"
        return 1
    fi
    
    if [[ ! -d "/opt/ai-translator-venv" ]]; then
        error "البيئة الافتراضية غير موجودة"
        return 1
    fi
    
    if [[ ! -f "/opt/ai-translator-venv/bin/gunicorn" ]]; then
        error "Gunicorn غير مُثبت في البيئة الافتراضية"
        return 1
    fi
    
    log "جميع الملفات موجودة ✓"
}

# Test manual run
test_manual_run() {
    log "اختبار تشغيل التطبيق يدوياً..."
    
    cd /opt/ai-translator
    
    # Set environment variables
    export DATABASE_URL="postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator"
    export FLASK_SECRET_KEY="ai_translator_secret_2024"
    export SESSION_SECRET="ai_translator_session_2024"
    
    # Test Python import
    log "اختبار استيراد Python..."
    /opt/ai-translator-venv/bin/python -c "import main; print('Import successful')" 2>&1 || {
        error "فشل في استيراد main.py"
        return 1
    }
    
    # Test gunicorn
    log "اختبار Gunicorn..."
    timeout 10 /opt/ai-translator-venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 1 main:app &
    GUNICORN_PID=$!
    sleep 5
    
    if kill -0 $GUNICORN_PID 2>/dev/null; then
        log "Gunicorn يعمل بنجاح ✓"
        kill $GUNICORN_PID
        return 0
    else
        error "فشل في تشغيل Gunicorn"
        return 1
    fi
}

# Check database connection
check_database() {
    log "فحص اتصال قاعدة البيانات..."
    
    if ! systemctl is-active --quiet postgresql; then
        warn "PostgreSQL متوقف، بدء تشغيله..."
        systemctl start postgresql
    fi
    
    # Test database connection
    if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
        log "PostgreSQL يعمل ✓"
    else
        error "مشكلة في PostgreSQL"
        return 1
    fi
    
    # Test specific database
    if sudo -u postgres psql -d ai_translator -c "SELECT 1;" >/dev/null 2>&1; then
        log "قاعدة البيانات ai_translator متاحة ✓"
    else
        warn "مشكلة في قاعدة البيانات ai_translator"
    fi
}

# Fix service configuration
fix_service() {
    log "إصلاح تكوين الخدمة..."
    
    # Create corrected service file
    cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-translator
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=FLASK_SECRET_KEY=ai_translator_secret_2024
Environment=SESSION_SECRET=ai_translator_session_2024
Environment=PATH=/opt/ai-translator-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/opt/ai-translator-venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --access-logfile - --error-logfile - main:app
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    log "تم تحديث تكوين الخدمة ✓"
}

# Install missing packages
install_packages() {
    log "تثبيت الحزم المفقودة..."
    
    cd /opt/ai-translator
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
    
    log "تم تثبيت الحزم ✓"
}

# Create simple test app
create_test_app() {
    log "إنشاء تطبيق اختبار..."
    
    cat > /opt/ai-translator/test_app.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>AI Translator Test - المترجم الآلي</h1><p>Service is working!</p>'

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Service is healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF
    
    chown www-data:www-data /opt/ai-translator/test_app.py
    log "تم إنشاء تطبيق الاختبار ✓"
}

# Test with simple app
test_simple_app() {
    log "اختبار التطبيق البسيط..."
    
    # Create service for test app
    cat > /etc/systemd/system/ai-translator-test.service << 'EOF'
[Unit]
Description=AI Translator Test Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-translator
Environment=PATH=/opt/ai-translator-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/opt/ai-translator-venv/bin/python test_app.py
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ai-translator-test
    systemctl start ai-translator-test
    
    sleep 5
    
    if systemctl is-active --quiet ai-translator-test; then
        log "تطبيق الاختبار يعمل ✓"
        
        # Test connection
        if curl -s http://localhost:5000 >/dev/null; then
            log "التطبيق يستجيب على المنفذ 5000 ✓"
            return 0
        else
            warn "التطبيق لا يستجيب"
        fi
    else
        error "فشل في تشغيل تطبيق الاختبار"
    fi
}

# Main function
main() {
    echo -e "${BLUE}=================================================================="
    echo "                    تشخيص مشاكل خدمة المترجم الآلي"
    echo "==================================================================${NC}"
    
    check_files || exit 1
    check_database
    install_packages
    fix_service
    
    # Stop existing service
    systemctl stop ai-translator 2>/dev/null || true
    
    # Test manual run first
    if test_manual_run; then
        log "الاختبار اليدوي نجح، بدء الخدمة..."
        systemctl start ai-translator
        sleep 5
        
        if systemctl is-active --quiet ai-translator; then
            log "الخدمة تعمل الآن ✓"
            echo -e "${GREEN}🎉 نجح الإصلاح! جرب الوصول للتطبيق على: http://$(hostname -I | awk '{print $1}')${NC}"
        else
            warn "الخدمة لا تزال لا تعمل، جرب التطبيق البسيط..."
            create_test_app
            test_simple_app
        fi
    else
        warn "الاختبار اليدوي فشل، إنشاء تطبيق اختبار..."
        create_test_app
        test_simple_app
    fi
    
    # Show final status
    echo -e "${BLUE}=================================================================="
    echo "                           الحالة النهائية"
    echo "==================================================================${NC}"
    
    echo "خدمة ai-translator:"
    systemctl status ai-translator --no-pager -l || echo "الخدمة متوقفة"
    
    echo ""
    echo "خدمة ai-translator-test:"
    systemctl status ai-translator-test --no-pager -l || echo "خدمة الاختبار متوقفة"
    
    echo ""
    echo "المنافذ:"
    ss -tlnp | grep 5000 || echo "لا توجد عمليات على المنفذ 5000"
}

main "$@"