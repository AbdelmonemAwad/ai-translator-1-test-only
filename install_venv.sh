#!/bin/bash

# AI Translator Virtual Environment Installation
# تثبيت المترجم الآلي في بيئة افتراضية

echo "🐍 Installing AI Translator with Virtual Environment"
echo "=================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Running as root - creating system-wide installation"
    INSTALL_DIR="/opt/ai-translator"
    VENV_DIR="/opt/ai-translator-venv"
    SERVICE_USER="ai-translator"
else
    echo "👤 Running as user - creating user installation"
    INSTALL_DIR="$HOME/ai-translator"
    VENV_DIR="$HOME/ai-translator-venv"
    SERVICE_USER="$USER"
fi

log() { echo "✓ $1"; }
error() { echo "❌ $1"; exit 1; }

# 1. Install system dependencies
log "Installing system dependencies..."
if [[ $EUID -eq 0 ]]; then
    apt update
    apt install -y python3 python3-venv python3-full python3-dev
    apt install -y postgresql postgresql-contrib nginx
    apt install -y build-essential libpq-dev libffi-dev libssl-dev
    apt install -y ffmpeg mediainfo curl wget git unzip
else
    echo "❌ Please install system dependencies as root first:"
    echo "sudo apt update"
    echo "sudo apt install -y python3 python3-venv python3-full python3-dev postgresql postgresql-contrib"
    echo "Then run this script again as regular user"
    exit 1
fi

# 2. Create virtual environment
log "Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 3. Upgrade pip in virtual environment
log "Upgrading pip..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip

# 4. Install Python packages in virtual environment
log "Installing Python packages..."
"$VENV_DIR/bin/pip" install \
    flask flask-sqlalchemy gunicorn \
    psutil psycopg2-binary requests \
    werkzeug email-validator \
    openai-whisper torch torchaudio

# 5. Setup PostgreSQL
log "Setting up PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Create database
sudo -u postgres createdb ai_translator 2>/dev/null || log "Database already exists"
sudo -u postgres createuser ai_translator 2>/dev/null || log "User already exists"
sudo -u postgres psql -c "ALTER USER ai_translator WITH PASSWORD 'ai_translator_pass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"

# 6. Copy application files
log "Installing application files..."
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"

# 7. Create service user (if root)
if [[ $EUID -eq 0 ]]; then
    useradd -r -s /bin/false ai-translator 2>/dev/null || log "User already exists"
    chown -R ai-translator:ai-translator "$INSTALL_DIR"
    chown -R ai-translator:ai-translator "$VENV_DIR"
fi

# 8. Create systemd service
log "Creating systemd service..."
if [[ $EUID -eq 0 ]]; then
    cat > /etc/systemd/system/ai-translator.service << EOF
[Unit]
Description=AI Translator Service
After=network.target postgresql.service

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
Restart=always
RestartSec=3
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass@localhost/ai_translator

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ai-translator
fi

# 9. Configure Nginx (if root)
if [[ $EUID -eq 0 ]]; then
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
fi

# 10. Start services
log "Starting services..."
if [[ $EUID -eq 0 ]]; then
    systemctl start ai-translator
    systemctl start nginx
    
    # Check service status
    sleep 3
    if systemctl is-active --quiet ai-translator; then
        echo ""
        echo "🎉 Installation successful!"
        echo "=========================="
        echo "Access: http://$(hostname -I | awk '{print $1}')"
        echo "Login: admin / your_strong_password"
        echo ""
        echo "Service status:"
        systemctl status ai-translator --no-pager -l
    else
        echo "❌ Service failed to start. Manual start:"
        echo "cd $INSTALL_DIR"
        echo "source $VENV_DIR/bin/activate"
        echo "python app.py"
    fi
else
    echo ""
    echo "🎉 User installation complete!"
    echo "=============================="
    echo "To start the application:"
    echo "cd $INSTALL_DIR"
    echo "source $VENV_DIR/bin/activate"
    echo "python app.py"
    echo ""
    echo "Then access: http://localhost:5000"
fi

echo ""
echo "📝 Installation paths:"
echo "Application: $INSTALL_DIR"
echo "Virtual Env: $VENV_DIR"
echo "Database: postgresql://ai_translator:ai_translator_pass@localhost/ai_translator"