# Ubuntu Server Deployment Guide for AI Translator
# دليل نشر خادم Ubuntu للترجمان الآلي

## Overview
This guide provides comprehensive instructions for deploying AI Translator on Ubuntu Server, specifically addressing the flask_sqlalchemy import error encountered on remote servers.

## Quick Fix for Remote Server (94.203.60.118)

### Problem Identified
```bash
ModuleNotFoundError: No module named 'flask_sqlalchemy'
```

### Immediate Solution

1. **Connect to your server:**
```bash
ssh root@94.203.60.118
# Password: 1q1
```

2. **Run the quick fix:**
```bash
# Download and run the quick fix script
wget https://raw.githubusercontent.com/your-repo/main/quick_ubuntu_fix.sh
chmod +x quick_ubuntu_fix.sh
sudo ./quick_ubuntu_fix.sh
```

Or manually execute these commands:

```bash
# Install missing packages
pip3 install --upgrade pip
pip3 install flask flask-sqlalchemy sqlalchemy psycopg2-binary gunicorn werkzeug

# Test the fix
python3 -c "from flask_sqlalchemy import SQLAlchemy; print('✅ flask_sqlalchemy working')"

# Restart the service
systemctl stop ai-translator
systemctl start ai-translator
systemctl status ai-translator
```

## Complete Installation Guide

### Prerequisites
- Ubuntu Server 20.04+ or 22.04+
- Root access
- Internet connection

### Step 1: System Preparation
```bash
# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y python3 python3-pip python3-venv python3-dev \
               build-essential curl wget git nano htop \
               postgresql postgresql-contrib nginx ffmpeg \
               software-properties-common apt-transport-https \
               ca-certificates gnupg lsb-release
```

### Step 2: Python Dependencies
```bash
# Install Python packages globally
pip3 install --upgrade pip
pip3 install -r requirements_ubuntu.txt
```

**requirements_ubuntu.txt:**
```
flask==3.0.0
flask-sqlalchemy==3.1.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
gunicorn==21.2.0
werkzeug==3.0.1
jinja2==3.1.2
requests==2.31.0
psutil==5.9.6
python-dotenv==1.0.0
pillow==10.1.0
opencv-python==4.8.1.78
numpy==1.26.4
pandas==2.1.4
paramiko==3.4.0
boto3==1.34.0
torch==2.1.2
faster-whisper==1.0.1
pynvml==11.5.0
setuptools==69.0.3
wheel==0.42.0
```

### Step 3: PostgreSQL Configuration

1. **Create database and user:**
```bash
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ai_translator;
DROP USER IF EXISTS ai_translator;
CREATE DATABASE ai_translator;
CREATE USER ai_translator WITH ENCRYPTED PASSWORD 'ai_translator_pass2024';
GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;
ALTER USER ai_translator CREATEDB;
\q
EOF
```

2. **Configure authentication:**
```bash
# Find PostgreSQL version
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP 'PostgreSQL \K[0-9]+')

# Update pg_hba.conf
sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/$PG_VERSION/main/pg_hba.conf

# Restart PostgreSQL
systemctl restart postgresql
```

3. **Test database connection:**
```bash
PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator -c "SELECT 1;"
```

### Step 4: Application Setup

1. **Create application directory:**
```bash
mkdir -p /root/ai-translator
cd /root/ai-translator
```

2. **Copy your application files to this directory**

3. **Create systemd service:**
```bash
cat > /etc/systemd/system/ai-translator.service << 'EOF'
[Unit]
Description=AI Translator v2.2.5 Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/root/ai-translator
Environment=PATH=/usr/bin:/usr/local/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=ubuntu-ai-translator-secret-key-2024
Environment=FLASK_ENV=production
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 main:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ai-translator
```

### Step 5: Nginx Configuration

```bash
cat > /etc/nginx/sites-available/ai-translator << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 500M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
    
    location /static {
        alias /root/ai-translator/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/ai-translator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and start nginx
nginx -t && systemctl restart nginx && systemctl enable nginx
```

### Step 6: Start Services

```bash
# Start AI Translator service
systemctl start ai-translator

# Check status
systemctl status ai-translator

# View logs if needed
journalctl -u ai-translator -f
```

## Troubleshooting

### Common Issues

1. **flask_sqlalchemy not found:**
```bash
pip3 install flask-sqlalchemy
python3 -c "import flask_sqlalchemy; print('OK')"
```

2. **Database connection failed:**
```bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection manually
PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator
```

3. **Service won't start:**
```bash
# Check detailed logs
journalctl -u ai-translator --no-pager -n 50

# Check file permissions
chown -R root:root /root/ai-translator
chmod +x /root/ai-translator/main.py
```

4. **Import errors:**
```bash
# Reinstall all Python packages
pip3 install --force-reinstall -r requirements_ubuntu.txt
```

### Verification Commands

```bash
# Check service status
systemctl status ai-translator nginx postgresql

# Test web access
curl -I http://localhost

# Test database
sudo -u postgres psql -c "\l" | grep ai_translator

# Test Python imports
python3 -c "
import flask, flask_sqlalchemy, sqlalchemy, psycopg2
print('All imports successful')
"
```

## Default Credentials

- **Application Login:**
  - Username: admin
  - Password: your_strong_password

- **Database:**
  - Host: localhost
  - Database: ai_translator
  - Username: ai_translator
  - Password: ai_translator_pass2024

## Security Notes

1. Change default passwords before production use
2. Configure firewall rules as needed
3. Consider using SSL/TLS certificates for HTTPS
4. Regularly update system packages

## Support

If you encounter issues:
1. Check service logs: `journalctl -u ai-translator -f`
2. Verify database connectivity
3. Ensure all Python packages are installed
4. Check nginx configuration with `nginx -t`

For the specific server (94.203.60.118), the main issue was missing flask_sqlalchemy package, which is resolved by the quick fix script provided above.