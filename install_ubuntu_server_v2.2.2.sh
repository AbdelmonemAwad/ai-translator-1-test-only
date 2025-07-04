#!/bin/bash

# AI Translator v2.2.2 - Ubuntu Server Installation Script
# Compatible with Ubuntu Server 22.04+ and 24.04

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log() { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}ℹ $1${NC}"; }

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "          AI Translator v2.2.2 - Ubuntu Server Installer"
    echo "          المترجم الآلي - أداة تثبيت خادم أوبونتو"
    echo "=================================================================="
    echo -e "${NC}"
    echo "This script will install AI Translator on Ubuntu Server 22.04+"
    echo "Installation path: /root/ai-translator"
    echo "Default credentials: admin / your_strong_password"
    echo ""
}

check_requirements() {
    log "Checking system requirements..."
    
    # Check if running as root
    [[ $EUID -eq 0 ]] || error "Please run as root: sudo $0"
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu" /etc/os-release; then
        error "This script is designed for Ubuntu Server"
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" ]]; then
        warn "Detected architecture: $ARCH (x86_64 recommended)"
    fi
    
    # Check available space (minimum 5GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [[ $AVAILABLE_SPACE -lt 5242880 ]]; then
        error "Insufficient disk space. Need at least 5GB free."
    fi
    
    log "System requirements check passed"
}

update_system() {
    log "Updating system packages..."
    apt update -y
    apt upgrade -y
    log "System updated successfully"
}

install_dependencies() {
    log "Installing system dependencies..."
    
    # Essential packages
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        pkg-config \
        curl \
        wget \
        unzip \
        git \
        nginx \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        software-properties-common
    
    # FFmpeg for video processing
    apt install -y ffmpeg
    
    log "Dependencies installed successfully"
}

setup_postgresql() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;"
    sudo -u postgres psql -c "DROP USER IF EXISTS ai_translator;"
    sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
    sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
    sudo -u postgres psql -c "ALTER USER ai_translator CREATEDB;"
    
    # Test connection
    if sudo -u postgres psql -d ai_translator -c "SELECT 1;" >/dev/null 2>&1; then
        log "PostgreSQL database setup completed"
    else
        error "Failed to setup PostgreSQL database"
    fi
}

install_application() {
    log "Installing AI Translator application..."
    
    # Remove any existing installation
    rm -rf /root/ai-translator
    
    # Create application directory
    mkdir -p /root/ai-translator
    cd /tmp
    
    # Download source code (use current working directory files if available)
    if [[ -f "app.py" && -f "main.py" ]]; then
        log "Using local source files..."
        cp -r * /root/ai-translator/
    else
        log "Downloading from GitHub..."
        wget -O ai-translator.zip https://github.com/AbdelmonemAwad/ai-translator/archive/refs/heads/main.zip
        unzip -o ai-translator.zip
        cp -r ai-translator-main/* /root/ai-translator/
        rm -f ai-translator.zip
        rm -rf ai-translator-main
    fi
    
    # Set correct permissions
    chown -R root:root /root/ai-translator
    chmod -R 755 /root/ai-translator
    
    log "Application files installed"
}

setup_python_environment() {
    log "Setting up Python virtual environment..."
    
    cd /root/ai-translator
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate and install packages
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install required packages
    pip install \
        flask==3.0.0 \
        flask-sqlalchemy==3.1.1 \
        gunicorn==21.2.0 \
        psutil==5.9.6 \
        psycopg2-binary==2.9.7 \
        requests==2.31.0 \
        werkzeug==3.0.1 \
        email-validator==2.1.0 \
        pynvml==11.5.0
    
    deactivate
    log "Python environment setup completed"
}

create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator v2.2.2 Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/root/ai-translator
Environment=PATH=/root/ai-translator/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=ai_translator_secret_2024
Environment=PYTHONPATH=/root/ai-translator
ExecStart=/root/ai-translator/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 --preload main:app
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=5
StartLimitBurst=3
StartLimitIntervalSec=60

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable ai-translator
    
    log "Systemd service created"
}

configure_nginx() {
    log "Configuring Nginx reverse proxy with static files support..."
    
    # Set proper permissions for Nginx to access /root directory
    chmod 755 /root
    chmod -R 755 /root/ai-translator
    
    cat > /etc/nginx/sites-available/ai-translator << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    client_max_body_size 100M;
    client_body_timeout 300;
    client_header_timeout 300;
    
    # Static files - serve directly from filesystem with proper MIME types
    location /static/ {
        alias /root/ai-translator/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
        
        # CSS files
        location ~* \.css$ {
            add_header Content-Type text/css;
        }
        
        # JavaScript files  
        location ~* \.js$ {
            add_header Content-Type application/javascript;
        }
        
        # Image files
        location ~* \.(jpg|jpeg|png|gif|ico|svg)$ {
            expires 1y;
        }
        
        # Font files
        location ~* \.(woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Access-Control-Allow-Origin "*";
        }
    }
    
    # Main application proxy
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
    
    # Compression settings
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/css
        text/javascript
        application/javascript
        application/json
        text/plain;
    
    # Error page for service startup
    error_page 502 503 504 /50x.html;
    location = /50x.html {
        return 200 '<html><body style="text-align:center;padding:50px;font-family:Arial;"><h1>🤖 AI Translator</h1><p>Service is starting up...</p><p>Please wait a moment and refresh.</p></body></html>';
        add_header Content-Type text/html;
    }
}
EOF
    
    # Enable site and disable default
    ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    nginx -t
    systemctl reload nginx
    
    log "Nginx configuration completed"
}

start_services() {
    log "Starting services..."
    
    # Start AI Translator
    systemctl start ai-translator
    
    # Wait for service to start
    sleep 10
    
    # Check service status
    if systemctl is-active --quiet ai-translator; then
        log "AI Translator service is running"
    else
        warn "AI Translator service may have issues"
        systemctl status ai-translator --no-pager -l | head -20
    fi
    
    # Start Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log "Services started"
}

test_installation() {
    log "Testing installation..."
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}' | tr -d '\n')
    
    # Test HTTP response
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|302"; then
        log "Web server is responding correctly"
    else
        warn "Web server may have issues"
    fi
    
    # Test database connection
    if sudo -u postgres psql -d ai_translator -c "SELECT 1;" >/dev/null 2>&1; then
        log "Database connection successful"
    else
        warn "Database connection may have issues"
    fi
}

print_completion() {
    SERVER_IP=$(hostname -I | awk '{print $1}' | tr -d '\n')
    
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "          AI Translator v2.2.2 Installation Complete!"
    echo "=================================================================="
    echo -e "${NC}"
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "📋 Access Information:"
    echo "   URL: http://$SERVER_IP"
    echo "   Username: admin"
    echo "   Password: your_strong_password"
    echo ""
    echo "📂 File Locations:"
    echo "   Application: /root/ai-translator"
    echo "   Service: /etc/systemd/system/ai-translator.service"
    echo "   Nginx Config: /etc/nginx/sites-available/ai-translator"
    echo ""
    echo "🔧 Service Commands:"
    echo "   Start: sudo systemctl start ai-translator"
    echo "   Stop: sudo systemctl stop ai-translator"
    echo "   Status: sudo systemctl status ai-translator"
    echo "   Logs: sudo journalctl -u ai-translator -f"
    echo ""
    echo "🌐 Test your installation at: http://$SERVER_IP"
    echo ""
}

# Main installation flow
main() {
    print_header
    check_requirements
    update_system
    install_dependencies
    setup_postgresql
    install_application
    setup_python_environment
    create_systemd_service
    configure_nginx
    start_services
    test_installation
    print_completion
}

# Run main function
main "$@"