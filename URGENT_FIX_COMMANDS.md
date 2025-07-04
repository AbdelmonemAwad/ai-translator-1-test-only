# إصلاح عاجل لمشكلة flask_sqlalchemy
# Urgent Fix for flask_sqlalchemy Issue

## المشكلة / Problem
```
ModuleNotFoundError: No module named 'flask_sqlalchemy'
```

## الحل السريع / Quick Fix

### 1. إيقاف الخدمة / Stop Service
```bash
sudo systemctl stop ai-translator
```

### 2. تثبيت المكتبة المفقودة / Install Missing Library
```bash
cd /root/ai-translator
source venv/bin/activate
pip install Flask-SQLAlchemy>=3.1.1
```

### 3. تثبيت جميع المكتبات الأساسية / Install All Core Libraries
```bash
pip install \
    Flask>=3.0.0 \
    Flask-SQLAlchemy>=3.1.1 \
    Gunicorn>=21.2.0 \
    Werkzeug>=3.0.1 \
    SQLAlchemy>=2.0.23 \
    psycopg2-binary>=2.9.9 \
    psutil>=5.9.6 \
    pynvml>=11.5.0 \
    requests>=2.31.0 \
    python-dotenv>=1.0.0
```

### 4. فحص التثبيت / Test Installation
```bash
python3 -c "
import sys
try:
    from flask_sqlalchemy import SQLAlchemy
    print('✓ Flask-SQLAlchemy imported successfully')
    import flask
    print('✓ Flask imported successfully')
    import sqlalchemy
    print('✓ SQLAlchemy imported successfully')
    import psycopg2
    print('✓ psycopg2 imported successfully')
    print('✓ All imports successful!')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
```

### 5. إعادة تشغيل الخدمة / Restart Service
```bash
sudo systemctl start ai-translator
sudo systemctl status ai-translator
```

### 6. فحص الخدمة / Check Service
```bash
sudo journalctl -u ai-translator --no-pager -n 10
```

## إصلاح كامل باستخدام السكريبت المحسن / Complete Fix Using Enhanced Script

### تحميل السكريبت المحسن / Download Enhanced Script
```bash
curl -fsSL https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_fixed.sh -o install_fixed.sh
chmod +x install_fixed.sh
```

### تشغيل التثبيت المحسن / Run Enhanced Installation
```bash
./install_fixed.sh
```

## فحص الحالة النهائية / Final Status Check
```bash
sudo systemctl status ai-translator
sudo systemctl status nginx
sudo systemctl status postgresql
```

## الوصول للتطبيق / Access Application
```bash
curl -I http://localhost
```

Expected output:
```
HTTP/1.1 200 OK
```

## معلومات الاتصال / Connection Info
- **URL**: http://YOUR_SERVER_IP
- **Username**: admin
- **Password**: your_strong_password
- **Database**: ai_translator
- **Database User**: ai_translator
- **Database Password**: ai_translator_pass2024

## تسجيل المشاكل / Troubleshooting Logs
```bash
# خدمة AI Translator
sudo journalctl -u ai-translator -f

# قاعدة البيانات
sudo journalctl -u postgresql -f

# Nginx
sudo journalctl -u nginx -f

# فحص المنافذ
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :80
```