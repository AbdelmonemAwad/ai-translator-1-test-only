# AI Translator v2.2.1 - Ubuntu Server Test Guide

## 🚀 Quick Test Installation

### Step 1: Prepare Ubuntu Server
```bash
# On fresh Ubuntu Server 22.04+ or 24.04
sudo apt update && sudo apt upgrade -y
```

### Step 2: Download and Install
```bash
# Download the installation script
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_ubuntu_server_v2.2.1.sh

# Make executable and run
chmod +x install_ubuntu_server_v2.2.1.sh
sudo ./install_ubuntu_server_v2.2.1.sh
```

### Step 3: Verify Installation
```bash
# Download and run the test script
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/test_ubuntu_installation.sh
chmod +x test_ubuntu_installation.sh
sudo ./test_ubuntu_installation.sh
```

## 🔍 Manual Testing Steps

### 1. Check Service Status
```bash
sudo systemctl status ai-translator
sudo journalctl -u ai-translator -f
```

### 2. Test Web Access
```bash
# Get server IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# Test local access
curl -I http://localhost

# Test login page
curl -s http://localhost/login | grep "تسجيل الدخول"
```

### 3. Test Database Connection
```bash
sudo -u postgres psql -d ai_translator -c "SELECT current_database(), current_user;"
```

### 4. Test API Endpoints
```bash
curl -s http://localhost/api/status | jq .
```

## 📋 Expected Results

### ✅ Successful Installation Should Show:
- **Service Status**: `active (running)`
- **Web Response**: HTTP 200 or 302 redirect to login
- **Login Page**: Arabic interface with "تسجيل الدخول" title
- **Database**: Connection successful, user `ai_translator` exists
- **API Status**: Returns JSON with `"status": "operational"`

### 🔐 Default Login Credentials:
- **Username**: `admin`
- **Password**: `your_strong_password`

## 🐛 Common Issues and Solutions

### Issue 1: Service Won't Start
```bash
# Check logs
sudo journalctl -u ai-translator --no-pager -l

# Check Python environment
cd /root/ai-translator
source venv/bin/activate
python -c "import flask, psycopg2; print('Dependencies OK')"
```

### Issue 2: Database Connection Failed
```bash
# Reset database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;"
sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
```

### Issue 3: Nginx 502 Bad Gateway
```bash
# Check if app is running
curl http://127.0.0.1:5000

# Restart services
sudo systemctl restart ai-translator
sudo systemctl restart nginx
```

### Issue 4: Permission Issues
```bash
# Fix ownership
sudo chown -R root:root /root/ai-translator
sudo chmod -R 755 /root/ai-translator
```

## 🌐 Browser Testing Checklist

1. **Access the application** at `http://SERVER_IP`
2. **Login page loads** with Arabic interface
3. **Login works** with admin/your_strong_password
4. **Dashboard displays** system information
5. **Navigation works** between pages
6. **Logout functions** correctly

## 📊 Performance Testing

### Basic Load Test
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test 100 requests with 10 concurrent
ab -n 100 -c 10 http://localhost/login
```

### Memory and CPU Usage
```bash
# Monitor while testing
htop
# or
top -p $(pgrep -f ai-translator)
```

## 🔧 Advanced Configuration

### Environment Variables
Edit `/etc/systemd/system/ai-translator.service`:
```ini
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator
Environment=SESSION_SECRET=ai_translator_secret_2024
Environment=FLASK_ENV=production
```

### Nginx Tuning
Edit `/etc/nginx/sites-available/ai-translator`:
```nginx
client_max_body_size 500M;  # For large video files
proxy_read_timeout 900;     # For long processing tasks
```

## 📝 Test Report Template

```
AI Translator v2.2.1 - Ubuntu Server Test Report
=====================================================

Server Information:
- OS Version: Ubuntu 22.04/24.04
- Server IP: ___________
- Installation Date: ___________

Test Results:
□ Installation completed without errors
□ Service starts and stays running  
□ Web interface accessible
□ Login functionality works
□ Database connection successful
□ API endpoints respond correctly
□ Arabic interface displays properly

Performance:
- Response Time: _____ ms
- Memory Usage: _____ MB
- CPU Usage: _____%

Issues Found:
- None / List any issues

Overall Status: ✅ PASS / ❌ FAIL

Notes:
_________________________________
```

## 🚨 Emergency Recovery

### Complete Reinstall
```bash
# Stop services
sudo systemctl stop ai-translator nginx

# Remove installation
sudo rm -rf /root/ai-translator
sudo rm -f /etc/systemd/system/ai-translator.service
sudo rm -f /etc/nginx/sites-available/ai-translator
sudo rm -f /etc/nginx/sites-enabled/ai-translator

# Drop database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;"
sudo -u postgres psql -c "DROP USER IF EXISTS ai_translator;"

# Reinstall
sudo ./install_ubuntu_server_v2.2.1.sh
```

## 📞 Support Information

- **GitHub Repository**: https://github.com/AbdelmonemAwad/ai-translator
- **Documentation**: Check README.md for full documentation  
- **Issues**: Report problems via GitHub Issues
- **Version**: v2.2.1 Ubuntu Server Compatible