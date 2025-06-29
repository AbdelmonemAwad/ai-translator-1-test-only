#!/bin/bash

# AI Translator v2.2.1 - Ubuntu Server Installation Test Script
# Use this script to verify the installation works correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
log() { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}ℹ $1${NC}"; }

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "          AI Translator v2.2.1 - Installation Test"
    echo "=================================================================="
    echo -e "${NC}"
}

test_system_requirements() {
    info "Testing system requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log "Running as root"
    else
        warn "Not running as root (may affect some tests)"
    fi
    
    # Check Ubuntu version
    if grep -q "Ubuntu" /etc/os-release; then
        UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2)
        log "Ubuntu $UBUNTU_VERSION detected"
    else
        error "Not running on Ubuntu"
    fi
    
    # Check Python version
    if command -v python3 >/dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log "$PYTHON_VERSION found"
    else
        error "Python3 not found"
    fi
    
    # Check available space
    AVAILABLE_SPACE=$(df -h / | awk 'NR==2 {print $4}')
    log "Available disk space: $AVAILABLE_SPACE"
}

test_dependencies() {
    info "Testing system dependencies..."
    
    # Essential packages
    REQUIRED_PACKAGES=("python3" "python3-pip" "postgresql" "nginx" "curl" "wget")
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if command -v "$package" >/dev/null || dpkg -l | grep -q "$package"; then
            log "$package is installed"
        else
            warn "$package is missing"
        fi
    done
}

test_postgresql() {
    info "Testing PostgreSQL setup..."
    
    # Check if PostgreSQL is running
    if systemctl is-active --quiet postgresql; then
        log "PostgreSQL service is running"
    else
        warn "PostgreSQL service is not running"
        return 1
    fi
    
    # Test database connection
    if sudo -u postgres psql -d ai_translator -c "SELECT 1;" >/dev/null 2>&1; then
        log "Database 'ai_translator' is accessible"
    else
        warn "Cannot connect to database 'ai_translator'"
        return 1
    fi
    
    # Test user permissions
    if sudo -u postgres psql -d ai_translator -c "SELECT current_user;" | grep -q "ai_translator" 2>/dev/null; then
        log "Database user 'ai_translator' exists"
    else
        warn "Database user 'ai_translator' may not exist"
    fi
}

test_application_files() {
    info "Testing application files..."
    
    # Check application directory
    if [[ -d "/root/ai-translator" ]]; then
        log "Application directory exists"
    else
        error "Application directory /root/ai-translator not found"
    fi
    
    # Check essential files
    ESSENTIAL_FILES=("app.py" "main.py" "models.py")
    cd /root/ai-translator
    
    for file in "${ESSENTIAL_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            log "$file exists"
        else
            warn "$file is missing"
        fi
    done
    
    # Check virtual environment
    if [[ -d "venv" ]]; then
        log "Virtual environment exists"
        
        # Test Python packages
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            
            # Check key packages
            if python -c "import flask" 2>/dev/null; then
                log "Flask is installed"
            else
                warn "Flask is not installed"
            fi
            
            if python -c "import psycopg2" 2>/dev/null; then
                log "PostgreSQL driver is installed"
            else
                warn "PostgreSQL driver is not installed"
            fi
            
            deactivate
        fi
    else
        warn "Virtual environment not found"
    fi
}

test_systemd_service() {
    info "Testing systemd service..."
    
    # Check if service file exists
    if [[ -f "/etc/systemd/system/ai-translator.service" ]]; then
        log "Service file exists"
    else
        error "Service file not found"
    fi
    
    # Check if service is enabled
    if systemctl is-enabled --quiet ai-translator; then
        log "Service is enabled"
    else
        warn "Service is not enabled"
    fi
    
    # Check if service is running
    if systemctl is-active --quiet ai-translator; then
        log "Service is running"
    else
        warn "Service is not running"
        systemctl status ai-translator --no-pager -l | head -10
    fi
}

test_nginx_configuration() {
    info "Testing Nginx configuration..."
    
    # Check if nginx config exists
    if [[ -f "/etc/nginx/sites-available/ai-translator" ]]; then
        log "Nginx configuration exists"
    else
        warn "Nginx configuration not found"
    fi
    
    # Check if site is enabled
    if [[ -L "/etc/nginx/sites-enabled/ai-translator" ]]; then
        log "Site is enabled"
    else
        warn "Site is not enabled"
    fi
    
    # Test nginx configuration
    if nginx -t >/dev/null 2>&1; then
        log "Nginx configuration is valid"
    else
        warn "Nginx configuration has errors"
    fi
    
    # Check if nginx is running
    if systemctl is-active --quiet nginx; then
        log "Nginx service is running"
    else
        warn "Nginx service is not running"
    fi
}

test_web_application() {
    info "Testing web application..."
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}' | tr -d '\n')
    
    # Test local connection
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|302"; then
        log "Local web server is responding"
    else
        warn "Local web server is not responding"
    fi
    
    # Test external connection
    if curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP" | grep -q "200\|302"; then
        log "External web server is responding"
    else
        warn "External web server is not responding"
    fi
    
    # Test login page
    if curl -s "http://localhost/login" | grep -q "تسجيل الدخول"; then
        log "Login page is accessible with Arabic content"
    else
        warn "Login page may have issues"
    fi
    
    # Test API endpoint
    if curl -s "http://localhost/api/status" | grep -q "operational"; then
        log "API endpoint is working"
    else
        warn "API endpoint may have issues"
    fi
}

run_comprehensive_test() {
    info "Running comprehensive test..."
    
    # Test actual login
    COOKIE_JAR=$(mktemp)
    
    # Get login page and extract any CSRF tokens if needed
    curl -s -c "$COOKIE_JAR" "http://localhost/login" > /dev/null
    
    # Attempt login
    LOGIN_RESPONSE=$(curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
        -d "username=admin&password=your_strong_password" \
        -X POST \
        "http://localhost/login" \
        -w "%{http_code}")
    
    if echo "$LOGIN_RESPONSE" | grep -q "302\|dashboard"; then
        log "Login functionality is working"
    else
        warn "Login functionality may have issues"
    fi
    
    # Clean up
    rm -f "$COOKIE_JAR"
}

generate_report() {
    SERVER_IP=$(hostname -I | awk '{print $1}' | tr -d '\n')
    
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "                    Installation Test Report"
    echo "=================================================================="
    echo -e "${NC}"
    echo "🖥️  Server IP: $SERVER_IP"
    echo "🌐 Access URL: http://$SERVER_IP"
    echo "👤 Username: admin"
    echo "🔑 Password: your_strong_password"
    echo ""
    echo "📋 Service Commands:"
    echo "   Status: sudo systemctl status ai-translator"
    echo "   Logs: sudo journalctl -u ai-translator -f"
    echo "   Restart: sudo systemctl restart ai-translator"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   Database: sudo -u postgres psql -d ai_translator"
    echo "   Application logs: tail -f /var/log/syslog | grep ai-translator"
    echo "   Nginx logs: tail -f /var/log/nginx/error.log"
    echo ""
}

# Main test flow
main() {
    print_header
    test_system_requirements
    test_dependencies
    test_postgresql
    test_application_files
    test_systemd_service
    test_nginx_configuration
    test_web_application
    run_comprehensive_test
    generate_report
}

# Run main function
main "$@"