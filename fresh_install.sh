#!/bin/bash

# Fresh AI Translator Installation - تثبيت نظيف من جديد
# After complete system reset

echo "🚀 Fresh AI Translator Installation"
echo "=================================="

# Check if running as root
[[ $EUID -eq 0 ]] || { echo "❌ Run as root: sudo $0"; exit 1; }

log() { echo "✓ $1"; }
error() { echo "❌ $1"; exit 1; }

# 1. Update system
log "Updating system packages..."
apt update && apt upgrade -y

# 2. Install essential tools
log "Installing essential tools..."
apt install -y curl wget git unzip

# 3. Install Python
log "Installing Python..."
apt install -y python3 python3-pip python3-venv python3-dev

# 4. Install PostgreSQL
log "Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

# 5. Install system dependencies
log "Installing system dependencies..."
apt install -y \
    build-essential \
    ffmpeg \
    nginx \
    supervisor \
    libpq-dev \
    libffi-dev \
    libssl-dev

# 6. Download AI Translator
log "Downloading AI Translator v2.2.0..."
cd /tmp
wget -q https://github.com/AbdelmonemAwad/ai-translator/releases/download/v2.2.0/ai-translator-v2.2.0.zip
unzip -q ai-translator-v2.2.0.zip
cd ai-translator*

# 7. Install Python packages
log "Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install \
    flask flask-sqlalchemy gunicorn \
    psutil psycopg2-binary requests \
    werkzeug email-validator

# 8. Setup application
log "Setting up application..."
mkdir -p /opt/ai-translator
cp -r . /opt/ai-translator/

# 9. Setup database
log "Setting up database..."
systemctl start postgresql
systemctl enable postgresql
sudo -u postgres createdb ai_translator
sudo -u postgres createuser ai_translator
sudo -u postgres psql -c "ALTER USER ai_translator WITH PASSWORD 'ai_pass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"

# 10. Create service user
log "Creating service user..."
useradd -r -s /bin/false ai-translator
chown -R ai-translator:ai-translator /opt/ai-translator

# 11. Create systemd service
log "Creating service..."
cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator
After=network.target postgresql.service

[Service]
Type=exec
User=ai-translator
Group=ai-translator
WorkingDirectory=/opt/ai-translator
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5000 app:app
Restart=always
Environment=DATABASE_URL=postgresql://ai_translator:ai_pass123@localhost/ai_translator

[Install]
WantedBy=multi-user.target
EOF

# 12. Configure Nginx
log "Configuring Nginx..."
cat > /etc/nginx/sites-available/ai-translator << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 13. Start services
log "Starting services..."
systemctl daemon-reload
systemctl enable ai-translator
systemctl start ai-translator
systemctl restart nginx

# 14. Check status
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
    echo "❌ Installation failed. Check logs:"
    echo "journalctl -u ai-translator -f"
fi