#!/bin/bash
# AI Translator Fixed Installation Script - إصلاح مشكلة Python
# Support: Ubuntu Server 22.04+ with Python auto-detection

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
    echo "          AI Translator Fixed Installation"
    echo "          تثبيت المترجم الآلي مع إصلاح Python"
    echo "=================================================================="
    echo -e "${NC}"
}

detect_python() {
    log "Detecting available Python version..."
    
    if command -v python3.11 >/dev/null 2>&1; then
        PYTHON_VERSION="3.11"
    elif command -v python3.10 >/dev/null 2>&1; then
        PYTHON_VERSION="3.10"
    elif command -v python3.9 >/dev/null 2>&1; then
        PYTHON_VERSION="3.9"
    else
        PYTHON_VERSION="3"  # Generic python3
    fi
    
    log "Using Python $PYTHON_VERSION"
    export PYTHON_VERSION
}

install_python_packages() {
    log "Installing Python and dependencies..."
    
    # Update package list
    apt update
    
    # Install basic Python (available on all Ubuntu versions)
    apt install -y python3 python3-dev python3-venv python3-pip
    
    # Try to install specific version if available
    if [[ "$PYTHON_VERSION" != "3" ]]; then
        apt install -y python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv 2>/dev/null || {
            warn "Specific Python $PYTHON_VERSION packages not available, using default python3"
        }
    fi
    
    log "Python packages installed ✓"
}

install_system_dependencies() {
    log "Installing system dependencies..."
    
    apt install -y \
        curl wget git build-essential \
        software-properties-common \
        apt-transport-https ca-certificates \
        postgresql postgresql-contrib \
        nginx ufw htop unzip \
        ffmpeg mediainfo \
        libpq-dev libffi-dev libssl-dev \
        pkg-config sqlite3 libsqlite3-dev \
        python3-numpy python3-requests \
        python3-flask python3-sqlalchemy
    
    log "System dependencies installed ✓"
}

install_python_ai_packages() {
    log "Installing AI packages with virtual environment..."
    
    # Create virtual environment
    VENV_DIR="/opt/ai-translator-venv"
    python3 -m venv "$VENV_DIR"
    
    # Upgrade pip in virtual environment
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    
    # Install AI Translator requirements in virtual environment
    "$VENV_DIR/bin/pip" install \
        flask flask-sqlalchemy gunicorn \
        psutil psycopg2-binary requests \
        werkzeug email-validator \
        openai-whisper torch torchaudio
    
    # Set permissions
    chown -R ai-translator:ai-translator "$VENV_DIR"
    
    log "AI packages installed in virtual environment ✓"
}

setup_database() {
    log "Setting up PostgreSQL database..."
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres createdb ai_translator 2>/dev/null || warn "Database already exists"
    sudo -u postgres createuser ai_translator 2>/dev/null || warn "User already exists"
    sudo -u postgres psql -c "ALTER USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
    
    log "Database setup completed ✓"
}

create_service() {
    log "Creating systemd service..."
    
    # Create service user
    useradd -r -s /bin/false ai-translator 2>/dev/null || warn "User already exists"
    
    # Set permissions
    chown -R ai-translator:ai-translator /opt/ai-translator
    chmod +x /opt/ai-translator/app.py
    
    # Create systemd service with virtual environment
    cat > /etc/systemd/system/ai-translator.service << EOF
[Unit]
Description=AI Translator Service
After=network.target postgresql.service

[Service]
Type=exec
User=ai-translator
Group=ai-translator
WorkingDirectory=/opt/ai-translator
ExecStart=/opt/ai-translator-venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
Restart=always
RestartSec=3
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ai-translator
    
    log "Service created ✓"
}

configure_nginx() {
    log "Configuring Nginx..."
    
    cat > /etc/nginx/sites-available/ai-translator << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t && systemctl restart nginx
    
    log "Nginx configured ✓"
}

main() {
    print_header
    
    # Check if running as root
    [[ $EUID -eq 0 ]] || error "Run as root: sudo $0"
    
    detect_python
    install_python_packages
    install_system_dependencies
    
    # Copy files to /opt/ai-translator (assumes we're in the ai-translator directory)
    log "Installing application files..."
    mkdir -p /opt/ai-translator
    cp -r . /opt/ai-translator/
    
    install_python_ai_packages
    setup_database
    create_service
    configure_nginx
    
    # Start services
    log "Starting services..."
    systemctl start ai-translator
    systemctl start nginx
    
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "          AI Translator Installation Complete!"
    echo "=================================================================="
    echo "Access your application at: http://$(hostname -I | awk '{print $1}')"
    echo "Default credentials: admin / your_strong_password"
    echo "=================================================================="
    echo -e "${NC}"
}

main "$@"