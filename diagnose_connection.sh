#!/bin/bash

# AI Translator Connection Diagnosis Script
# سكريپت تشخيص مشاكل الاتصال للمترجم الآلي

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
}

header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check service status
check_service() {
    header "فحص حالة الخدمة"
    
    if systemctl is-active --quiet ai-translator; then
        log "✓ خدمة ai-translator تعمل"
        systemctl status ai-translator --no-pager -l
    else
        error "✗ خدمة ai-translator متوقفة"
        echo "محاولة تشغيل الخدمة..."
        systemctl start ai-translator
        sleep 3
        systemctl status ai-translator --no-pager -l
    fi
    echo ""
}

# Check ports
check_ports() {
    header "فحص المنافذ"
    
    log "فحص المنفذ 5000 (Flask):"
    if netstat -tlnp | grep :5000; then
        log "✓ المنفذ 5000 مفتوح"
    else
        error "✗ المنفذ 5000 مغلق"
    fi
    
    log "فحص المنفذ 80 (Nginx):"
    if netstat -tlnp | grep :80; then
        log "✓ المنفذ 80 مفتوح"
    else
        error "✗ المنفذ 80 مغلق"
    fi
    echo ""
}

# Check processes
check_processes() {
    header "فحص العمليات"
    
    log "عمليات Python/Gunicorn:"
    ps aux | grep -E "(python|gunicorn)" | grep -v grep || warn "لا توجد عمليات Python"
    
    log "عمليات Nginx:"
    ps aux | grep nginx | grep -v grep || warn "لا توجد عمليات Nginx"
    echo ""
}

# Check logs
check_logs() {
    header "فحص السجلات"
    
    log "آخر 10 أسطر من سجل ai-translator:"
    journalctl -u ai-translator -n 10 --no-pager || warn "فشل في قراءة السجل"
    
    log "آخر 5 أسطر من سجل Nginx:"
    tail -n 5 /var/log/nginx/error.log 2>/dev/null || warn "فشل في قراءة سجل Nginx"
    echo ""
}

# Check database
check_database() {
    header "فحص قاعدة البيانات"
    
    if systemctl is-active --quiet postgresql; then
        log "✓ PostgreSQL يعمل"
        sudo -u postgres psql -c "SELECT version();" 2>/dev/null || warn "مشكلة في الاتصال بقاعدة البيانات"
    else
        error "✗ PostgreSQL متوقف"
        systemctl start postgresql
    fi
    echo ""
}

# Check firewall
check_firewall() {
    header "فحص الجدار الناري"
    
    log "حالة UFW:"
    ufw status || warn "UFW غير مُثبت أو غير مُفعل"
    
    log "فحص iptables:"
    iptables -L INPUT -n | grep -E "(80|5000)" || log "لا توجد قواعد للمنافذ 80/5000"
    echo ""
}

# Test local connections
test_connections() {
    header "اختبار الاتصالات المحلية"
    
    log "اختبار المنفذ 5000:"
    if curl -s -m 5 http://localhost:5000 >/dev/null; then
        log "✓ Flask يستجيب على localhost:5000"
    else
        error "✗ Flask لا يستجيب على localhost:5000"
    fi
    
    log "اختبار المنفذ 80:"
    if curl -s -m 5 http://localhost >/dev/null; then
        log "✓ Nginx يستجيب على localhost:80"
    else
        error "✗ Nginx لا يستجيب على localhost:80"
    fi
    
    log "اختبار الـ IP الخارجي:"
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if curl -s -m 5 http://$LOCAL_IP >/dev/null; then
        log "✓ التطبيق يستجيب على $LOCAL_IP"
    else
        error "✗ التطبيق لا يستجيب على $LOCAL_IP"
    fi
    echo ""
}

# Provide recommendations
provide_recommendations() {
    header "التوصيات"
    
    echo "بناءً على التشخيص، جرب هذه الحلول:"
    echo ""
    echo "1. إعادة تشغيل الخدمات:"
    echo "   sudo systemctl restart ai-translator"
    echo "   sudo systemctl restart nginx"
    echo ""
    echo "2. فحص السجلات للأخطاء:"
    echo "   sudo journalctl -u ai-translator -f"
    echo ""
    echo "3. اختبار التطبيق محلياً:"
    echo "   curl http://localhost:5000"
    echo "   curl http://localhost"
    echo ""
    echo "4. إعادة تنصيب إذا لزم الأمر:"
    echo "   curl -sSL https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_fixed.sh | sudo bash"
    echo ""
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "                 تشخيص مشاكل اتصال المترجم الآلي"
    echo "=================================================================="
    echo -e "${NC}"
    
    check_service
    check_ports
    check_processes
    check_logs
    check_database
    check_firewall
    test_connections
    provide_recommendations
    
    echo -e "${BLUE}=================================================================="
    echo "                      انتهى التشخيص"
    echo "==================================================================${NC}"
}

# Run if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi