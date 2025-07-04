#!/usr/bin/env python3
"""
AI Translator - Main Entry Point for Replit
المترجم الذكي - نقطة البداية الرئيسية لـ Replit
"""

import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# إعداد المسار للاستيراد
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# إعداد قاعدة البيانات
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# إنشاء التطبيق
app = Flask(__name__)

# إعداد المتغيرات البيئية
app.secret_key = os.environ.get("SESSION_SECRET", "replit-ai-translator-secret-key")

# إعداد قاعدة البيانات
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # استخدام SQLite في بيئة التطوير
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ai_translator.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# تهيئة قاعدة البيانات
db.init_app(app)

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # فحص وتثبيت البرامج المساعدة المطلوبة
    logger.info("🔍 Checking required dependencies...")
    
    # قائمة البرامج المساعدة الأساسية
    CORE_DEPENDENCIES = {
        'ai_models': ['torch', 'faster_whisper'],  # استخدام faster_whisper بدلاً من openai-whisper
        'media_processing': ['PIL', 'cv2', 'numpy'],
        'storage': ['paramiko', 'boto3'],
        'monitoring': ['psutil', 'pynvml'],
        'web': ['flask', 'sqlalchemy', 'gunicorn']
    }
    
    missing_deps = []
    for category, deps in CORE_DEPENDENCIES.items():
        for dep in deps:
            try:
                __import__(dep)
                logger.info(f"✓ {dep} available")
            except ImportError:
                missing_deps.append(dep)
                logger.warning(f"⚠ {dep} not found")
    
    if missing_deps:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.info("Run: pip install -r requirements_complete.txt")
    
    # استيراد التطبيق الأساسي
    logger.info("✓ Attempting to import original AI Translator...")
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        logger.info("✓ Database tables created successfully")
        
    # استيراد الوحدات الأساسية
    from app import *
    
    logger.info("✓ Successfully imported original AI Translator v2.2.5")
    
    # فحص إضافي للبرامج المساعدة المتقدمة
    logger.info("🔧 Checking advanced components...")
    
    # فحص GPU
    try:
        import pynvml
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        logger.info(f"✓ NVIDIA GPUs detected: {gpu_count}")
    except:
        logger.info("ℹ No NVIDIA GPUs detected (normal in cloud environments)")
    
    # فحص Ollama
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            logger.info(f"✓ Ollama running with {len(models)} models")
        else:
            logger.info("ℹ Ollama not running (will start on demand)")
    except:
        logger.info("ℹ Ollama not accessible (install with: curl -fsSL https://ollama.ai/install.sh | sh)")
    
    # فحص FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            logger.info("✓ FFmpeg available")
        else:
            logger.warning("⚠ FFmpeg not working properly")
    except:
        logger.warning("⚠ FFmpeg not found")
    
    # فحص قاعدة البيانات
    db_url = os.environ.get("DATABASE_URL")
    if db_url and 'postgresql' in db_url:
        logger.info("✓ PostgreSQL database configured")
    elif db_url:
        logger.info(f"✓ Database configured: {db_url.split('://')[0]}")
    else:
        logger.info("ℹ Using SQLite database (fallback)")
    
except Exception as e:
    logger.error(f"❌ Error importing AI Translator: {str(e)}")
    # إنشاء تطبيق بسيط في حالة الخطأ
    @app.route('/')
    def index():
        return '''
        <h1>AI Translator - الترجمان الذكي</h1>
        <p>التطبيق قيد التحميل... يرجى المحاولة مرة أخرى</p>
        <p>Application is loading... Please try again</p>
        '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)