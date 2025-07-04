#!/bin/bash
# Quick Ubuntu Fix for AI Translator Remote Server
# إصلاح سريع لخادم Ubuntu البعيد للترجمان الآلي

echo "=== AI Translator Ubuntu Quick Fix ==="
echo "=== إصلاح سريع للترجمان الآلي على Ubuntu ==="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root"
   echo "❌ يجب تشغيل هذا السكريپت كـ root"
   exit 1
fi

echo "🔧 Starting quick fix for flask_sqlalchemy issue..."
echo "🔧 بدء الإصلاح السريع لمشكلة flask_sqlalchemy..."

# 1. Install missing Python packages
echo "📦 Installing missing Python packages..."
pip3 install --upgrade pip
pip3 install flask flask-sqlalchemy sqlalchemy psycopg2-binary gunicorn werkzeug

# 2. Fix the specific flask_sqlalchemy issue
echo "🔧 Fixing flask_sqlalchemy import issue..."
python3 -c "import flask_sqlalchemy; print('✅ flask_sqlalchemy working')" || {
    echo "❌ flask_sqlalchemy still not working, trying alternative installation..."
    apt update
    apt install -y python3-flask python3-flask-sqlalchemy
}

# 3. Test the fix
echo "🧪 Testing the fix..."
cd /root/ai-translator 2>/dev/null || {
    echo "⚠️ AI Translator directory not found at /root/ai-translator"
    echo "⚠️ مجلد الترجمان الآلي غير موجود في /root/ai-translator"
    echo "📁 Please ensure your files are in the correct location"
    exit 1
}

# Test import
python3 -c "
try:
    from flask_sqlalchemy import SQLAlchemy
    print('✅ flask_sqlalchemy import successful')
except ImportError as e:
    print(f'❌ flask_sqlalchemy import failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ flask_sqlalchemy is now working!"
    echo "✅ flask_sqlalchemy يعمل الآن!"
    
    # 4. Restart the service
    echo "🔄 Restarting AI Translator service..."
    systemctl stop ai-translator
    systemctl start ai-translator
    
    # Check service status
    if systemctl is-active --quiet ai-translator; then
        echo "✅ Service started successfully!"
        echo "✅ تم تشغيل الخدمة بنجاح!"
        echo "🌐 You can now access the application at: http://your-server-ip"
        echo "🌐 يمكنك الآن الوصول للتطبيق عبر: http://your-server-ip"
    else
        echo "❌ Service failed to start. Checking logs..."
        echo "❌ فشل في تشغيل الخدمة. فحص السجلات..."
        journalctl -u ai-translator --no-pager -n 20
    fi
else
    echo "❌ flask_sqlalchemy is still not working"
    echo "❌ flask_sqlalchemy لا يزال لا يعمل"
    echo "🔍 Please check the error messages above"
fi

echo ""
echo "=== Quick Fix Completed ==="
echo "=== اكتمل الإصلاح السريع ==="