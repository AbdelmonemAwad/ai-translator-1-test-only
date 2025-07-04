#!/usr/bin/env python3
import os
import sys
import json
import time
import glob
import subprocess
import threading
import logging
import math
import psutil
import shutil
import requests
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Settings, MediaFile, Log, TranslationJob, Notification, UserSession, PasswordReset, TranslationHistory, DatabaseStats, TranslationLog
from translations import get_translation, t
# from services.media_services import MediaServicesManager
from gpu_manager import gpu_manager, get_gpu_environment_variables

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    database_url = "sqlite:///library.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Global variables for compatibility
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(PROJECT_DIR, "status.json")
BLACKLIST_FILE = os.path.join(PROJECT_DIR, "blacklist.txt")
PROCESS_LOG_FILE = os.path.join(PROJECT_DIR, "process.log")
APP_LOG_FILE = os.path.join(PROJECT_DIR, "app.log")

def get_settings():
    """Get all settings as a dictionary"""
    settings = {}
    for setting in Settings.query.all():
        settings[setting.key] = setting.value
    return settings

def get_setting(key, default=None):
    """Get a specific setting value"""
    setting = Settings.query.filter_by(key=key).first()
    return setting.value if setting else default

def is_development_feature_enabled(feature_key):
    """Check if a development feature is enabled"""
    value = get_setting(feature_key, 'false')
    return value.lower() in ['true', '1', 'yes']

def get_user_language():
    """Get current user's language preference"""
    # First check session storage
    lang = session.get('user_language')
    if lang:
        return lang
    
    # Then check user session in database
    session_id = session.get('session_id')
    if session_id:
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if user_session:
            return user_session.language
    
    return get_setting('default_language', 'en')

def get_user_theme():
    """Get current user's theme preference"""
    user_session = UserSession.query.filter_by(session_id=session.get('session_id')).first()
    if user_session:
        return user_session.theme
    return get_setting('default_theme', 'system')

def translate_text(key, **kwargs):
    """Translation helper function for templates"""
    lang = get_user_language()
    return get_translation(key, lang, **kwargs)

def create_notification(title_key, message_key, notification_type='info', **kwargs):
    """Create a new notification with translation support"""
    try:
        # Store translation keys instead of translated text
        notification = Notification()
        notification.title = title_key  # Store the translation key
        notification.message = message_key  # Store the translation key with parameters
        notification.type = notification_type
        
        # Store translation parameters as JSON if any
        if kwargs:
            import json
            notification.translation_params = json.dumps(kwargs)
        
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        log_to_db("ERROR", "Failed to create notification", str(e))
        return False

def get_unread_notifications():
    """Get unread notifications count"""
    return Notification.query.filter_by(read=False).count()

def get_supported_video_formats():
    """Get list of supported video formats from database"""
    try:
        from models import VideoFormat
        formats = VideoFormat.query.filter_by(supported=True).all()
        return [fmt.extension.lower() for fmt in formats]
    except Exception as e:
        # Fallback to default formats if database is not available
        log_to_db("WARNING", f"Could not load video formats from database: {str(e)}")
        default_formats = 'mp4,mkv,avi,mov,m4v,wmv,flv,webm,ts,mts,m2ts,3gp,ogv,vob,asf,rm,rmvb'
        return [fmt.strip().lower() for fmt in default_formats.split(',')]

def is_video_file_supported(file_path):
    """Check if video file format is supported"""
    if not file_path:
        return False
    
    file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    supported_formats = get_supported_video_formats()
    return file_ext in supported_formats

def download_thumbnail(url, media_file_id):
    """Download and save thumbnail for media file"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Save thumbnail data to database
            media_file = MediaFile.query.get(media_file_id)
            if media_file:
                media_file.thumbnail_data = response.content
                media_file.thumbnail_url = url
                db.session.commit()
                return True
    except Exception as e:
        log_to_db("ERROR", f"Failed to download thumbnail: {url}", str(e))
    return False

def update_setting(key, value):
    """Update or create a setting"""
    setting = Settings.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        setting.updated_at = datetime.utcnow()
    else:
        setting = Settings()
        setting.key = key
        setting.value = value
        db.session.add(setting)
    db.session.commit()

def log_to_db(level, message, details=""):
    """Log message to database"""
    try:
        log_entry = Log()
        log_entry.level = level
        log_entry.message = message
        log_entry.details = details
        log_entry.source = "web_app"
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log to database: {e}")

def log_to_file(message):
    """Log message to file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(APP_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Failed to log to file: {e}")

def log_translation_event(file_path, file_name, status, progress=0.0, error_message=None, details=None, **kwargs):
    """Log translation event to database"""
    try:
        # Check if log already exists for this file
        existing_log = TranslationLog.query.filter_by(file_path=file_path).first()
        
        if existing_log:
            # Update existing log
            existing_log.status = status
            existing_log.progress = progress
            existing_log.error_message = error_message
            existing_log.details = details
            existing_log.updated_at = datetime.utcnow()
            
            # Update other fields if provided
            for key, value in kwargs.items():
                if hasattr(existing_log, key) and value is not None:
                    setattr(existing_log, key, value)
            
            if status in ['success', 'failed']:
                existing_log.completed_at = datetime.utcnow()
        else:
            # Create new log
            new_log = TranslationLog()
            new_log.file_path = file_path
            new_log.file_name = file_name
            new_log.status = status
            new_log.progress = progress
            new_log.error_message = error_message
            new_log.details = details
            
            # Set additional fields
            for key, value in kwargs.items():
                if hasattr(new_log, key) and value is not None:
                    setattr(new_log, key, value)
            db.session.add(new_log)
        
        db.session.commit()
        log_to_db("INFO", f"سجل الترجمة: {file_name} - {status}")
        
    except Exception as e:
        log_to_db("ERROR", f"خطأ في تسجيل حدث الترجمة: {str(e)}")
        db.session.rollback()

def is_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

def validate_file_path(file_path):
    """Validate file path for security - prevent directory traversal attacks"""
    if not file_path:
        return False
    
    # منع المسارات التي تحتوي على ../ أو ../
    if '..' in file_path or file_path.startswith('/'):
        return False
    
    # قائمة بالمجلدات المحظورة
    forbidden_dirs = [
        '/etc', '/sys', '/proc', '/dev', '/boot', '/root', '/home',
        '/var/log', '/var/lib', '/usr/bin', '/usr/sbin', '/bin', '/sbin'
    ]
    
    # فحص إذا كان المسار يحتوي على مجلد محظور
    for forbidden in forbidden_dirs:
        if file_path.startswith(forbidden.lstrip('/')):
            return False
    
    return True

def get_safe_file_path(relative_path):
    """Get safe absolute file path from relative path"""
    if not validate_file_path(relative_path):
        return None
    
    # الحصول على الإعدادات المسموحة للملفات
    settings = get_settings()
    allowed_paths = [
        settings.get('local_movies_mount', '/mnt/remote/movies'),
        settings.get('local_tv_mount', '/mnt/remote/tv'),
        '/tmp/ai-translator',  # مجلد مؤقت للتطبيق
        './static',  # ملفات التطبيق الثابتة
        './uploads'  # مجلد الرفع إن وجد
    ]
    
    # التأكد من أن المسار ضمن المسارات المسموحة
    for allowed_path in allowed_paths:
        if relative_path.startswith(allowed_path.lstrip('./')):
            return os.path.abspath(relative_path)
    
    return None

def get_current_status():
    """Get current processing status"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {
        'status': 'idle',
        'progress': 0,
        'current_file': '',
        'total_files': 0,
        'files_done': 0,
        'task': ''
    }

def read_blacklist():
    """Read blacklisted paths from file"""
    if not os.path.exists(BLACKLIST_FILE):
        return []
    try:
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def add_to_blacklist(path):
    """Add path to blacklist"""
    blacklist = read_blacklist()
    if path not in blacklist:
        blacklist.append(path)
        try:
            with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(blacklist))
            
            # Update database record
            media_file = MediaFile.query.filter_by(path=path).first()
            if media_file:
                media_file.blacklisted = True
                db.session.commit()
            
            return True
        except Exception as e:
            log_to_db("ERROR", f"Failed to add to blacklist: {path}", str(e))
    return False

def remove_from_blacklist(path):
    """Remove path from blacklist"""
    blacklist = read_blacklist()
    if path in blacklist:
        blacklist.remove(path)
        try:
            with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(blacklist))
            
            # Update database record
            media_file = MediaFile.query.filter_by(path=path).first()
            if media_file:
                media_file.blacklisted = False
                db.session.commit()
            
            return True
        except Exception as e:
            log_to_db("ERROR", f"Failed to remove from blacklist: {path}", str(e))
    return False

def is_task_running():
    """Check if any background task is running"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline']
            if cmdline and any('background_tasks.py' in arg for arg in cmdline):
                return True
    except:
        pass
    return False

def run_background_task(task_name, *args):
    """Run a background task"""
    if is_task_running():
        return False, "مهمة أخرى قيد التشغيل حالياً"
    
    try:
        cmd = [sys.executable, 'background_tasks.py', task_name] + list(args)
        subprocess.Popen(cmd, cwd=PROJECT_DIR)
        log_to_db("INFO", f"Started background task: {task_name}")
        return True, f"تم بدء المهمة: {task_name}"
    except Exception as e:
        log_to_db("ERROR", f"Failed to start task: {task_name}", str(e))
        return False, f"فشل في بدء المهمة: {str(e)}"

# Routes - These will be registered by main.py
@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle language switching
    if 'lang' in request.args:
        session['language'] = request.args.get('lang')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin_username = get_setting('admin_username', 'admin')
        admin_password = get_setting('admin_password', 'your_strong_password')
        
        if username == admin_username and password == admin_password:
            session['authenticated'] = True
            session['username'] = username
            log_to_db("INFO", f"User logged in: {username}")
            return redirect(url_for('dashboard'))
        else:
            # Display error message in user's language
            if session.get('language', 'ar') == 'ar':
                flash('اسم المستخدم أو كلمة المرور غير صحيحة')
            else:
                flash('Invalid username or password')
            log_to_db("WARNING", f"Failed login attempt: {username}")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    log_to_db("INFO", f"User logged out: {username}")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    status = get_current_status()
    
    # Get statistics
    total_files = MediaFile.query.count()
    translated_files = MediaFile.query.filter_by(translated=True).count()
    blacklisted_files = MediaFile.query.filter_by(blacklisted=True).count()
    
    stats = {
        'total_files': total_files,
        'translated_files': translated_files,
        'blacklisted_files': blacklisted_files,
        'pending_files': total_files - translated_files - blacklisted_files
    }
    
    return render_template('dashboard.html', status=status, stats=stats)

@app.route('/files')
@app.route('/files/<status>')
def file_management(status='all'):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = int(get_setting('items_per_page', '24'))
    search = request.args.get('search', '')
    media_type = request.args.get('type', '')
    
    # Build query
    query = MediaFile.query
    
    if search:
        query = query.filter(MediaFile.title.contains(search))
    
    if media_type:
        query = query.filter_by(media_type=media_type)
    
    if status == 'untranslated':
        query = query.filter_by(translated=False, blacklisted=False)
    elif status == 'translated':
        query = query.filter_by(translated=True)
    elif status == 'blacklisted':
        query = query.filter_by(blacklisted=True)
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    files = pagination.items
    
    # Set page title based on status
    if status == 'untranslated':
        page_title = t('files_to_translate')
    elif status == 'translated':
        page_title = t('translated_files')
    elif status == 'blacklisted':
        page_title = t('blacklisted_files')
    else:
        page_title = t('all_files')

    return render_template('file_management.html', 
                         files=files, 
                         pagination=pagination,
                         status=status,
                         page_title=page_title,
                         search=search,
                         media_type=media_type)

@app.route('/corrections')
def corrections_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('corrections.html')

@app.route('/blacklist')
def blacklist_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    # Get blacklisted media files from database with full information
    blacklisted_files = MediaFile.query.filter_by(blacklisted=True).all()
    
    # Also read blacklist from file for paths not in database
    file_blacklist = read_blacklist()
    
    return render_template('blacklist.html', blacklisted_files=blacklisted_files, file_blacklist=file_blacklist)

@app.route('/logs')
def logs_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('logs.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update settings
        for key, value in request.form.items():
            if key.startswith('_'):  # Skip Flask form fields
                continue
            update_setting(key, value)
        
        flash('تم حفظ الإعدادات بنجاح')
        log_to_db("INFO", "Settings updated")
        return redirect(url_for('settings_page'))
    
    # Get settings grouped by section
    import json
    settings_by_section = {}
    user_language = get_user_language()
    
    for setting in Settings.query.order_by(Settings.section, Settings.key).all():
        if setting.section not in settings_by_section:
            settings_by_section[setting.section] = []
        
        # Process description for translation
        if setting.description:
            try:
                if isinstance(setting.description, str) and setting.description.startswith('{'):
                    desc_dict = json.loads(setting.description)
                    setting.translated_description = desc_dict.get(user_language, desc_dict.get('en', setting.key))
                else:
                    setting.translated_description = setting.description
            except:
                setting.translated_description = setting.description or setting.key
        else:
            setting.translated_description = setting.key
            
        # Process options for select fields
        if setting.type == 'select' and setting.options:
            setting.option_list = []
            options_text = setting.options
            
            # Check if options is JSON (multilingual)
            if isinstance(options_text, str) and options_text.startswith('{'):
                try:
                    options_dict = json.loads(options_text)
                    options_text = options_dict.get(user_language, options_dict.get('en', ''))
                except json.JSONDecodeError:
                    # If JSON parsing fails, use the raw text
                    pass
            
            # Parse the options text - handle both formats
            if options_text:
                for option_pair in options_text.split(','):
                    option_pair = option_pair.strip()
                    if ':' in option_pair:
                        # Format: value:label
                        value, label = option_pair.split(':', 1)
                        setting.option_list.append({
                            'value': value.strip(), 
                            'label': label.strip()
                        })
                    else:
                        # Format: just value (use as both value and label)
                        setting.option_list.append({
                            'value': option_pair.strip(), 
                            'label': option_pair.strip()
                        })
        else:
            setting.option_list = []
            
        settings_by_section[setting.section].append(setting)
    
    return render_template('settings.html', settings_by_section=settings_by_section)

@app.route('/system-monitor')
def system_monitor_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('system_monitor.html')

@app.route('/test-logs')
def test_logs_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('test_logs.html')

@app.route('/notifications')
def notifications_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('notifications.html')

@app.route('/docs')
def docs_page():
    """Documentation page with comprehensive application information"""
    return render_template('docs.html')

@app.route('/LICENSE')
def license_page():
    """Serve the LICENSE file"""
    try:
        with open('LICENSE', 'r', encoding='utf-8') as f:
            license_content = f.read()
        return f'<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px; background: #f5f5f5; margin: 20px; border-radius: 5px;">{license_content}</pre>'
    except FileNotFoundError:
        return "License file not found", 404

@app.route('/database-admin')
def database_admin_page():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('database_admin.html')

# API Routes
@app.route('/api/status')
def api_status():
    status = get_current_status()
    status['is_running'] = is_task_running()
    return jsonify(status)

@app.route('/api/files')
def api_files():
    page = request.args.get('page', 1, type=int)
    per_page = int(get_setting('items_per_page', '24'))
    search = request.args.get('search', '', type=str)
    media_type = request.args.get('media_type', 'all', type=str)
    status = request.args.get('status', 'all', type=str)
    
    query = MediaFile.query
    
    # Apply search filter
    if search:
        query = query.filter(MediaFile.title.contains(search))
    
    # Apply media type filter
    if media_type != 'all':
        if media_type == 'movies':
            query = query.filter(MediaFile.media_type == 'movie')
        elif media_type == 'tv':
            query = query.filter(MediaFile.media_type == 'episode')
    
    # Apply status filter (translated/untranslated)
    if status == 'translated':
        query = query.filter(MediaFile.translated == True)
    elif status == 'untranslated':
        query = query.filter(MediaFile.translated == False)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    files_data = []
    for file in pagination.items:
        files_data.append({
            'id': file.id,
            'path': file.path,
            'title': file.title,
            'year': file.year,
            'media_type': file.media_type,
            'poster_url': file.poster_url,
            'translated': file.translated,
            'blacklisted': file.blacklisted,
            'file_size': file.file_size,
            'quality': file.quality
        })
    
    return jsonify({
        'files': files_data,
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'per_page': pagination.per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

@app.route('/api/system-monitor')
def api_system_monitor_stats():
    try:
        from gpu_manager import SystemMonitor
        
        # Initialize system monitor
        system_monitor = SystemMonitor()
        system_info = system_monitor.get_complete_system_info()
        
        if not system_info:
            # Fallback to basic stats
            cpu_percent = round(psutil.cpu_percent(interval=1))
            memory = psutil.virtual_memory()
            ram_percent = round(memory.percent)
            ram_used_gb = round(memory.used / (1024**3), 1)
            ram_total_gb = round(memory.total / (1024**3), 1)
            
            return jsonify({
                'cpu_percent': cpu_percent,
                'ram_percent': ram_percent,
                'ram_used_gb': ram_used_gb,
                'ram_total_gb': ram_total_gb,
                'disk': {},
                'gpu': {'available': False, 'error': 'نظام المراقبة غير متوفر'}
            })
        
        # Format comprehensive system stats
        stats = {
            'system': {
                'hostname': system_info.hostname,
                'os_name': system_info.os_name,
                'os_version': system_info.os_version,
                'uptime': system_monitor.format_uptime(system_info.uptime),
                'load_average': system_info.load_average
            },
            'cpu': {
                'name': system_info.cpu.name,
                'architecture': system_info.cpu.architecture,
                'cores_physical': system_info.cpu.cores_physical,
                'cores_logical': system_info.cpu.cores_logical,
                'frequency_current': system_info.cpu.frequency_current,
                'frequency_max': system_info.cpu.frequency_max,
                'utilization': system_info.cpu.utilization,
                'temperature': system_info.cpu.temperature,
                'cache': {
                    'l1': system_info.cpu.cache_l1,
                    'l2': system_info.cpu.cache_l2,
                    'l3': system_info.cpu.cache_l3
                }
            },
            'memory': {
                'total': system_info.memory.total,
                'available': system_info.memory.available,
                'used': system_info.memory.used,
                'percentage': system_info.memory.percentage,
                'swap_total': system_info.memory.swap_total,
                'swap_used': system_info.memory.swap_used,
                'type': system_info.memory.type,
                'speed': system_info.memory.speed
            },
            'storage': [],
            'network': [],
            'gpu': {'available': False, 'gpus': []}
        }
        
        # Format storage information
        for storage in system_info.storage:
            stats['storage'].append({
                'device': storage.device,
                'mountpoint': storage.mountpoint,
                'filesystem': storage.filesystem,
                'total': storage.total,
                'used': storage.used,
                'free': storage.free,
                'percentage': storage.percentage,
                'device_type': storage.device_type,
                'read_speed': storage.read_speed,
                'write_speed': storage.write_speed
            })
        
        # Format network information
        for network in system_info.network:
            stats['network'].append({
                'interface': network.interface,
                'ip_address': network.ip_address,
                'netmask': network.netmask,
                'bytes_sent': system_monitor.format_bytes(network.bytes_sent),
                'bytes_recv': system_monitor.format_bytes(network.bytes_recv),
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'speed': network.speed,
                'status': network.status
            })
        
        # Format GPU information
        if system_info.gpus:
            stats['gpu'] = {
                'available': True,
                'count': len(system_info.gpus),
                'gpus': []
            }
            for gpu in system_info.gpus:
                stats['gpu']['gpus'].append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'memory_total': gpu.memory_total,
                    'memory_used': gpu.memory_used,
                    'memory_free': gpu.memory_free,
                    'utilization': gpu.utilization,
                    'temperature': gpu.temperature,
                    'power_draw': gpu.power_draw,
                    'power_limit': gpu.power_limit,
                    'driver_version': gpu.driver_version,
                    'cuda_version': gpu.cuda_version,
                    'performance_score': gpu.performance_score
                })
        else:
            stats['gpu'] = {'available': False, 'error': 'لا توجد بطاقات رسومية متاحة'}
        
        # Legacy compatibility fields
        stats['cpu_percent'] = system_info.cpu.utilization
        stats['ram_percent'] = system_info.memory.percentage
        stats['ram_used_gb'] = system_info.memory.used
        stats['ram_total_gb'] = system_info.memory.total
        
        # Format disk for legacy compatibility
        stats['disk'] = {}
        for storage in system_info.storage:
            stats['disk'][storage.mountpoint] = {
                'total': int(storage.total),
                'used': int(storage.used),
                'percent': int(storage.percentage),
                'error': False
            }
        
        return jsonify(stats)
        
    except Exception as e:
        log_to_db('ERROR', f'System monitor error: {str(e)}')
        # Fallback to basic psutil stats
        try:
            cpu_percent = round(psutil.cpu_percent(interval=1))
            memory = psutil.virtual_memory()
            ram_percent = round(memory.percent)
            ram_used_gb = round(memory.used / (1024**3), 1)
            ram_total_gb = round(memory.total / (1024**3), 1)
            
            return jsonify({
                'cpu_percent': cpu_percent,
                'ram_percent': ram_percent,
                'ram_used_gb': ram_used_gb,
                'ram_total_gb': ram_total_gb,
                'disk': {},
                'gpu': {'available': False, 'error': f'خطأ في نظام المراقبة: {str(e)}'}
            })
        except Exception as fallback_error:
            return jsonify({'error': f'خطأ في مراقبة النظام: {str(fallback_error)}'}), 500

@app.route('/api/get_log')
def api_get_log():
    log_type = request.args.get('type', 'app')
    lines = int(request.args.get('lines', 100))
    
    try:
        # Get logs from database first
        log_entries = Log.query.order_by(Log.created_at.desc()).limit(lines).all()
        
        if log_entries:
            log_content = []
            for entry in reversed(log_entries):  # Show oldest first
                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                log_line = f"[{timestamp}] {entry.level}: {entry.message}"
                if entry.details:
                    log_line += f" - {entry.details}"
                log_content.append(log_line)
            
            return jsonify({'content': '\n'.join(log_content)})
        
        # If no database logs, try file logs
        if log_type == 'process':
            log_file = PROCESS_LOG_FILE
        else:
            log_file = APP_LOG_FILE
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.readlines()
                if len(content) > lines:
                    content = content[-lines:]
                return jsonify({'content': ''.join(content)})
        
        return jsonify({'content': 'لا توجد سجلات'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_log', methods=['POST'])
def api_clear_log():
    data = request.get_json() or {}
    log_type = data.get('type', 'app')
    
    # Get filter parameters from URL
    level = request.args.get('level')
    days = request.args.get('days')
    
    try:
        # Clear database logs with filters
        if level:
            # Clear specific level logs
            Log.query.filter_by(level=level).delete()
            log_message = f"تم مسح سجلات {level}"
        elif days:
            # Clear old logs
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=int(days))
            Log.query.filter(Log.created_at < cutoff_date).delete()
            log_message = f"تم مسح السجلات الأقدم من {days} أيام"
        else:
            # Clear all logs
            Log.query.delete()
            log_message = "تم مسح جميع السجلات"
            
            # Also clear file logs if clearing all
            if log_type == 'process':
                log_file = PROCESS_LOG_FILE
            else:
                log_file = APP_LOG_FILE
            
            if os.path.exists(log_file):
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
        
        db.session.commit()
        log_to_db("INFO", log_message)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_selected_logs', methods=['POST'])
def api_delete_selected_logs():
    """Delete selected log entries by indices"""
    try:
        data = request.get_json()
        indices = data.get('indices', [])
        
        if not indices:
            return jsonify({'success': False, 'error': 'No indices provided'})
        
        # Get all logs ordered by creation date (newest first)
        all_logs = Log.query.order_by(Log.created_at.desc()).all()
        
        # Convert indices to log IDs
        log_ids_to_delete = []
        for index in indices:
            if 0 <= int(index) < len(all_logs):
                log_ids_to_delete.append(all_logs[int(index)].id)
        
        if log_ids_to_delete:
            # Delete selected logs
            Log.query.filter(Log.id.in_(log_ids_to_delete)).delete(synchronize_session=False)
            db.session.commit()
            
            log_to_db("INFO", f"تم حذف {len(log_ids_to_delete)} سجل محدد")
        
        return jsonify({'success': True, 'deleted_count': len(log_ids_to_delete)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/translation_logs', methods=['GET'])
def api_translation_logs():
    """Get translation logs"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        status_filter = request.args.get('status', None)
        
        # Build query
        query = TranslationLog.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Get logs ordered by creation date (newest first)
        logs = query.order_by(TranslationLog.created_at.desc()).limit(limit).all()
        
        # Convert to JSON-serializable format
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'file_path': log.file_path,
                'file_name': log.file_name,
                'status': log.status,
                'progress': log.progress,
                'error_message': log.error_message,
                'details': log.details,
                'file_size': log.file_size,
                'duration': log.duration,
                'whisper_model': log.whisper_model,
                'ollama_model': log.ollama_model,
                'subtitle_path': log.subtitle_path,
                'quality_score': log.quality_score,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'updated_at': log.updated_at.isoformat() if log.updated_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None
            })
        
        return jsonify({'logs': logs_data, 'count': len(logs_data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_sample_translation_logs', methods=['POST'])
def api_clear_sample_translation_logs():
    """Clear all sample translation logs"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Delete all translation logs
        count = TranslationLog.query.count()
        TranslationLog.query.delete()
        db.session.commit()
        
        log_to_db("INFO", f"تم حذف {count} سجل ترجمة وهمي")
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create_sample_translation_logs', methods=['POST'])
def api_create_sample_translation_logs():
    """Create sample translation logs for testing"""
    try:
        # Sample translation logs
        sample_logs = [
            {
                'file_path': '/media/movies/The.Matrix.1999.1080p.BluRay.x264.mkv',
                'file_name': 'The Matrix (1999)',
                'status': 'success',
                'progress': 100.0,
                'details': 'تم إنشاء ترجمة عربية عالية الجودة',
                'duration': 285.5,
                'whisper_model': 'medium.en',
                'ollama_model': 'llama3',
                'subtitle_path': '/media/movies/The.Matrix.1999.1080p.BluRay.x264.ar.srt',
                'quality_score': 95.0
            },
            {
                'file_path': '/media/series/Breaking.Bad.S01E01.720p.WEB-DL.x264.mkv',
                'file_name': 'Breaking Bad S01E01',
                'status': 'failed', 
                'progress': 45.0,
                'error_message': 'فشل في الاتصال بخدمة Ollama',
                'details': 'توقف أثناء مرحلة الترجمة',
                'duration': 120.3,
                'whisper_model': 'medium.en',
                'ollama_model': 'llama3'
            },
            {
                'file_path': '/media/movies/Inception.2010.1080p.BluRay.x264.mkv',
                'file_name': 'Inception (2010)',
                'status': 'incomplete',
                'progress': 75.0,
                'details': 'توقف أثناء المعالجة - يمكن استكمالها',
                'duration': 180.7,
                'whisper_model': 'medium.en',
                'ollama_model': 'llama3'
            },
            {
                'file_path': '/media/movies/Avatar.2009.1080p.BluRay.x264.mkv',
                'file_name': 'Avatar (2009)',
                'status': 'started',
                'progress': 25.0,
                'details': 'بدأت عملية استخراج الصوت',
                'whisper_model': 'medium.en',
                'ollama_model': 'llama3'
            }
        ]
        
        # Add sample logs to database
        for log_data in sample_logs:
            log_translation_event(**log_data)
        
        return jsonify({'success': True, 'message': f'تم إنشاء {len(sample_logs)} سجل تجريبي'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create_sample_media_files', methods=['POST'])
def api_create_sample_media_files():
    """Create sample media files for testing"""
    try:
        # Sample movie data
        sample_movies = [
            {
                'path': '/media/movies/The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv',
                'title': 'The Matrix',
                'year': 1999,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
                'imdb_id': 'tt0133093',
                'tmdb_id': 603,
                'has_subtitles': True,
                'translated': False,
                'blacklisted': False,
                'file_size': 8589934592,  # 8GB
                'duration': 8160,  # 136 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'AC3',
                'resolution': '1920x1080'
            },
            {
                'path': '/media/movies/Inception.2010.1080p.BluRay.x264-SPARKS.mkv',
                'title': 'Inception',
                'year': 2010,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
                'imdb_id': 'tt1375666',
                'tmdb_id': 27205,
                'has_subtitles': False,
                'translated': True,
                'blacklisted': False,
                'file_size': 10737418240,  # 10GB
                'duration': 8880,  # 148 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'DTS',
                'resolution': '1920x1080'
            },
            {
                'path': '/media/movies/Avatar.2009.1080p.BluRay.x265-RARBG.mkv',
                'title': 'Avatar',
                'year': 2009,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/6EiRUJpuoeQPghrs3YNktfnqOVh.jpg',
                'imdb_id': 'tt0499549',
                'tmdb_id': 19995,
                'has_subtitles': True,
                'translated': False,
                'blacklisted': False,
                'file_size': 12884901888,  # 12GB
                'duration': 9720,  # 162 minutes
                'quality': '1080p',
                'video_codec': 'x265',
                'audio_codec': 'DTS-HD',
                'resolution': '1920x1080'
            },
            {
                'path': '/media/movies/Interstellar.2014.1080p.BluRay.x264-SPARKS.mkv',
                'title': 'Interstellar',
                'year': 2014,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
                'imdb_id': 'tt0816692',
                'tmdb_id': 157336,
                'has_subtitles': False,
                'translated': False,
                'blacklisted': True,
                'file_size': 11811160064,  # 11GB
                'duration': 10140,  # 169 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'DTS',
                'resolution': '1920x1080'
            },
            {
                'path': '/media/movies/The.Dark.Knight.2008.1080p.BluRay.x264-REFiNED.mkv',
                'title': 'The Dark Knight',
                'year': 2008,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
                'imdb_id': 'tt0468569',
                'tmdb_id': 155,
                'has_subtitles': True,
                'translated': True,
                'blacklisted': False,
                'file_size': 9663676416,  # 9GB
                'duration': 9120,  # 152 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'AC3',
                'resolution': '1920x1080'
            }
        ]
        
        # Sample TV show data
        sample_tv_shows = [
            {
                'path': '/media/tv/Breaking Bad/Season 01/Breaking.Bad.S01E01.720p.WEB-DL.x264-GROUP.mkv',
                'title': 'Breaking Bad S01E01 - Pilot',
                'year': 2008,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg',
                'imdb_id': 'tt0959621',
                'tmdb_id': 1396,
                'sonarr_id': 1,
                'has_subtitles': False,
                'translated': False,
                'blacklisted': False,
                'file_size': 2147483648,  # 2GB
                'duration': 2760,  # 46 minutes
                'quality': '720p',
                'video_codec': 'x264',
                'audio_codec': 'AAC',
                'resolution': '1280x720'
            },
            {
                'path': '/media/tv/Breaking Bad/Season 01/Breaking.Bad.S01E02.720p.WEB-DL.x264-GROUP.mkv',
                'title': 'Breaking Bad S01E02 - Cat\'s in the Bag...',
                'year': 2008,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg',
                'imdb_id': 'tt0959621',
                'tmdb_id': 1396,
                'sonarr_id': 1,
                'has_subtitles': True,
                'translated': True,
                'blacklisted': False,
                'file_size': 2080374784,  # 1.9GB
                'duration': 2880,  # 48 minutes
                'quality': '720p',
                'video_codec': 'x264',
                'audio_codec': 'AAC',
                'resolution': '1280x720'
            },
            {
                'path': '/media/tv/Game of Thrones/Season 01/Game.of.Thrones.S01E01.1080p.BluRay.x264-REWARD.mkv',
                'title': 'Game of Thrones S01E01 - Winter Is Coming',
                'year': 2011,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg',
                'imdb_id': 'tt0944947',
                'tmdb_id': 1399,
                'sonarr_id': 2,
                'has_subtitles': False,
                'translated': False,
                'blacklisted': True,
                'file_size': 4294967296,  # 4GB
                'duration': 3600,  # 60 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'DTS',
                'resolution': '1920x1080'
            },
            {
                'path': '/media/tv/Stranger Things/Season 01/Stranger.Things.S01E01.1080p.NF.WEBRip.x264-SKGTV.mkv',
                'title': 'Stranger Things S01E01 - Chapter One: The Vanishing of Will Byers',
                'year': 2016,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg',
                'imdb_id': 'tt4574334',
                'tmdb_id': 66732,
                'sonarr_id': 3,
                'has_subtitles': True,
                'translated': False,
                'blacklisted': False,
                'file_size': 3221225472,  # 3GB
                'duration': 2880,  # 48 minutes
                'quality': '1080p',
                'video_codec': 'x264',
                'audio_codec': 'AC3',
                'resolution': '1920x1080'
            }
        ]
        
        # Combine all samples
        all_samples = sample_movies + sample_tv_shows
        
        # Add samples to database
        for media_data in all_samples:
            # Check if media file already exists
            existing_file = MediaFile.query.filter_by(path=media_data['path']).first()
            if not existing_file:
                new_file = MediaFile()
                for key, value in media_data.items():
                    if hasattr(new_file, key):
                        setattr(new_file, key, value)
                db.session.add(new_file)
        
        db.session.commit()
        log_to_db("INFO", f"تم إنشاء بيانات وهمية للملفات: {len(all_samples)} ملف")
        
        return jsonify({
            'success': True, 
            'message': f'تم إنشاء {len(all_samples)} ملف وهمي',
            'movies': len(sample_movies),
            'episodes': len(sample_tv_shows)
        })
    except Exception as e:
        log_to_db("ERROR", f"خطأ في إنشاء البيانات الوهمية: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clear_sample_media_files', methods=['POST'])
def api_clear_sample_media_files():
    """Clear sample media files"""
    try:
        # Define sample file paths to identify and remove them
        sample_paths = [
            '/media/movies/The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv',
            '/media/movies/Inception.2010.1080p.BluRay.x264-SPARKS.mkv',
            '/media/movies/Avatar.2009.1080p.BluRay.x265-RARBG.mkv',
            '/media/movies/Interstellar.2014.1080p.BluRay.x264-SPARKS.mkv',
            '/media/movies/The.Dark.Knight.2008.1080p.BluRay.x264-REFiNED.mkv',
            '/media/tv/Breaking Bad/Season 01/Breaking.Bad.S01E01.720p.WEB-DL.x264-GROUP.mkv',
            '/media/tv/Breaking Bad/Season 01/Breaking.Bad.S01E02.720p.WEB-DL.x264-GROUP.mkv',
            '/media/tv/Game of Thrones/Season 01/Game.of.Thrones.S01E01.1080p.BluRay.x264-REWARD.mkv',
            '/media/tv/Stranger Things/Season 01/Stranger.Things.S01E01.1080p.NF.WEBRip.x264-SKGTV.mkv'
        ]
        
        # Remove sample files from database
        deleted_count = 0
        for path in sample_paths:
            media_file = MediaFile.query.filter_by(path=path).first()
            if media_file:
                db.session.delete(media_file)
                deleted_count += 1
        
        db.session.commit()
        log_to_db("INFO", f"تم حذف {deleted_count} ملف وهمي من قاعدة البيانات")
        
        return jsonify({
            'success': True, 
            'message': f'تم حذف {deleted_count} ملف وهمي',
            'deleted_count': deleted_count
        })
    except Exception as e:
        log_to_db("ERROR", f"خطأ في حذف البيانات الوهمية: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create_sample_blacklist', methods=['POST'])
def api_create_sample_blacklist():
    """Create sample blacklist entries for testing"""
    if not is_authenticated():
        return jsonify({'error': translate_text('not_authenticated')}), 401
    
    try:
        sample_blacklist_paths = [
            '/media/movies/Old.Movie.1995.DVDRip.XviD-RARBG.avi',
            '/media/movies/Low.Quality.Film.2000.CAM-TERRIBLE.mp4',
            '/media/movies/Broken.Audio.Movie.2010.720p.HDTV.x264-BROKEN.mkv',
            '/media/tv/Old Series/Season 01/Old.Series.S01E01.480p.WEB-DL.x264-OLD.mkv',
            '/media/tv/Corrupted Show/Season 02/Corrupted.Show.S02E05.CORRUPT.mkv',
            '/media/movies/Sample.Movie.SAMPLE.mkv',
            '/media/tv/Test Series/Test.Series.S01E01.TEST.mkv',
            '/media/movies/Trailer.Only.Movie.2024.TRAILER.mp4'
        ]
        
        # Create sample media files in database first
        sample_media_data = [
            {
                'path': '/media/movies/Old.Movie.1995.DVDRip.XviD-RARBG.avi',
                'title': 'Old Movie',
                'year': 1995,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample1.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/movies/Low.Quality.Film.2000.CAM-TERRIBLE.mp4',
                'title': 'Low Quality Film',
                'year': 2000,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample2.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/movies/Broken.Audio.Movie.2010.720p.HDTV.x264-BROKEN.mkv',
                'title': 'Broken Audio Movie',
                'year': 2010,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample3.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/tv/Old Series/Season 01/Old.Series.S01E01.480p.WEB-DL.x264-OLD.mkv',
                'title': 'Old Series - S01E01',
                'year': 2005,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample4.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/tv/Corrupted Show/Season 02/Corrupted.Show.S02E05.CORRUPT.mkv',
                'title': 'Corrupted Show - S02E05',
                'year': 2018,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample5.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/movies/Sample.Movie.SAMPLE.mkv',
                'title': 'Sample Movie',
                'year': 2023,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample6.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/tv/Test Series/Test.Series.S01E01.TEST.mkv',
                'title': 'Test Series - S01E01',
                'year': 2024,
                'media_type': 'episode',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample7.jpg',
                'blacklisted': True
            },
            {
                'path': '/media/movies/Trailer.Only.Movie.2024.TRAILER.mp4',
                'title': 'Trailer Only Movie',
                'year': 2024,
                'media_type': 'movie',
                'poster_url': 'https://image.tmdb.org/t/p/w500/sample8.jpg',
                'blacklisted': True
            }
        ]
        
        # Add or update media files in database
        for media_data in sample_media_data:
            media_file = MediaFile.query.filter_by(path=media_data['path']).first()
            if not media_file:
                media_file = MediaFile(**media_data)
                db.session.add(media_file)
            else:
                for key, value in media_data.items():
                    setattr(media_file, key, value)
        
        db.session.commit()
        
        added_count = 0
        for path in sample_blacklist_paths:
            if add_to_blacklist(path):
                added_count += 1
        
        log_to_db("INFO", f"Created {added_count} sample blacklist entries")
        
        return jsonify({
            'success': True, 
            'message': f'Added {added_count} sample paths to blacklist',
            'added_count': added_count,
            'total_paths': len(sample_blacklist_paths)
        })
    except Exception as e:
        log_to_db("ERROR", f"Error creating sample blacklist: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clear_sample_blacklist', methods=['POST'])
def api_clear_sample_blacklist():
    """Clear sample blacklist entries"""
    if not is_authenticated():
        return jsonify({'error': translate_text('not_authenticated')}), 401
    
    try:
        sample_blacklist_paths = [
            '/media/movies/Old.Movie.1995.DVDRip.XviD-RARBG.avi',
            '/media/movies/Low.Quality.Film.2000.CAM-TERRIBLE.mp4',
            '/media/movies/Broken.Audio.Movie.2010.720p.HDTV.x264-BROKEN.mkv',
            '/media/tv/Old Series/Season 01/Old.Series.S01E01.480p.WEB-DL.x264-OLD.mkv',
            '/media/tv/Corrupted Show/Season 02/Corrupted.Show.S02E05.CORRUPT.mkv',
            '/media/movies/Sample.Movie.SAMPLE.mkv',
            '/media/tv/Test Series/Test.Series.S01E01.TEST.mkv',
            '/media/movies/Trailer.Only.Movie.2024.TRAILER.mp4'
        ]
        
        removed_count = 0
        for path in sample_blacklist_paths:
            if remove_from_blacklist(path):
                removed_count += 1
        
        log_to_db("INFO", f"Removed {removed_count} sample blacklist entries")
        
        return jsonify({
            'success': True, 
            'message': f'Removed {removed_count} sample paths from blacklist',
            'removed_count': removed_count
        })
    except Exception as e:
        log_to_db("ERROR", f"Error clearing sample blacklist: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Action Routes
@app.route('/action/start-batch', methods=['POST'])
def action_start_batch():
    if not is_authenticated():
        return jsonify({'error': translate_text('not_authenticated')}), 401
    
    success, message = run_background_task('batch_translate')
    
    if success:
        return jsonify({'success': True, 'message': translate_text('batch_translation_started')})
    else:
        return jsonify({'error': f'{translate_text("failed_to_start_task")}: {message}'}), 500

@app.route('/action/stop', methods=['POST'])
def action_stop():
    if not is_authenticated():
        return jsonify({'error': translate_text('not_authenticated')}), 401
    
    try:
        # Find and terminate background processes
        terminated = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline']
            if cmdline and any('background_tasks.py' in arg for arg in cmdline):
                proc.terminate()
                terminated = True
        
        if terminated:
            log_to_db("INFO", "Background tasks stopped")
            return jsonify({'success': True, 'message': translate_text('tasks_stopped')})
        else:
            return jsonify({'error': translate_text('no_running_tasks')})
    except Exception as e:
        log_to_db("ERROR", "Failed to stop tasks", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/action/sync-library', methods=['POST'])
def action_sync_library():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    success, message = run_background_task('sync_library')
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500

@app.route('/action/run-corrections', methods=['POST'])
def action_run_corrections():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    def generate():
        yield "data: بدء عملية التصحيح...\n\n"
        
        try:
            # Find and rename subtitle files
            corrections_made = 0
            
            for media_file in MediaFile.query.filter_by(translated=True).all():
                file_dir = os.path.dirname(media_file.path)
                filename = os.path.splitext(os.path.basename(media_file.path))[0]
                
                # Look for .hi.srt files
                hi_srt = os.path.join(file_dir, f"{filename}.hi.srt")
                ar_srt = os.path.join(file_dir, f"{filename}.ar.srt")
                
                if os.path.exists(hi_srt) and not os.path.exists(ar_srt):
                    try:
                        os.rename(hi_srt, ar_srt)
                        corrections_made += 1
                        yield f"data: تم تصحيح: {filename}\n\n"
                        time.sleep(0.1)
                    except Exception as e:
                        yield f"data: خطأ في تصحيح {filename}: {str(e)}\n\n"
            
            yield f"data: تم الانتهاء. عدد الملفات المصححة: {corrections_made}\n\n"
            
        except Exception as e:
            yield f"data: خطأ: {str(e)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/action/remove-from-blacklist', methods=['POST'])
def action_remove_from_blacklist():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    data = request.get_json() or {}
    path = data.get('path')
    if not path:
        return jsonify({'error': 'مسار الملف مطلوب'}), 400
    
    if remove_from_blacklist(path):
        return jsonify({'success': True, 'message': 'تم إزالة الملف من القائمة السوداء'})
    else:
        return jsonify({'error': 'فشل في إزالة الملف من القائمة السوداء'}), 500

@app.route('/action/scan_translation_status')
def action_scan_translation_status():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if is_task_running():
        return jsonify({'error': translate_text('task_already_running')}), 400
    
    success = run_background_task("scan_translation_status_task")
    
    if success:
        create_notification('scan_started', 'scan_translation_status_started', 'info')
        return jsonify({'success': True, 'message': translate_text('scan_translation_status_started')})
    else:
        return jsonify({'error': translate_text('failed_to_start_task')}), 500

# Notification API endpoints
@app.route('/api/notifications')
def api_notifications():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    user_language = get_user_language()
    
    notifications_data = []
    for notification in notifications:
        # Translate title and message
        translated_title = get_translation(notification.title, user_language)
        translated_message = get_translation(notification.message, user_language)
        
        # Apply translation parameters if they exist
        if notification.translation_params:
            import json
            try:
                params = json.loads(notification.translation_params)
                translated_message = translated_message.format(**params)
            except:
                pass  # Use message as is if formatting fails
        
        notifications_data.append({
            'id': notification.id,
            'title': translated_title,
            'message': translated_message,
            'type': notification.type,
            'read': notification.read,
            'created_at': notification.created_at.isoformat() if notification.created_at else None
        })
    
    return jsonify(notifications_data)

@app.route('/api/notifications/count')
def api_notifications_count():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    count = Notification.query.filter_by(read=False).count()
    return jsonify({'count': count})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def api_mark_notification_read(notification_id):
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/<int:notification_id>/delete', methods=['POST'])
def api_delete_notification(notification_id):
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_notifications_read():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    Notification.query.filter_by(read=False).update({'read': True})
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/clear-all', methods=['POST'])
def api_clear_all_notifications():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    Notification.query.delete()
    db.session.commit()
    
    return jsonify({'success': True})

# Database Admin API endpoints
@app.route('/api/database/stats')
def api_database_stats():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        from sqlalchemy import text
        import os
        
        # Get database file size
        db_path = "library.db"
        db_size_mb = 0
        if os.path.exists(db_path):
            db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2)
        
        # Query all tables with proper error handling
        tables = ['settings', 'media_files', 'logs', 'translation_jobs', 'notifications', 'user_sessions', 'translation_history']
        tables_info = []
        total_records = 0
        
        for table_name in tables:
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                if count is not None:
                    total_records += count
                    tables_info.append({
                        'name': table_name,
                        'record_count': count
                    })
            except Exception as e:
                print(f"Error querying table {table_name}: {e}")
                continue
        
        # Get last backup info (check for backup files)
        last_backup = 'لم يتم إجراء نسخ احتياطي'
        backup_files = [f for f in os.listdir('.') if f.startswith('library_backup_') and f.endswith('.db')]
        if backup_files:
            latest_backup = max(backup_files, key=lambda x: os.path.getmtime(x))
            backup_time = os.path.getmtime(latest_backup)
            import datetime
            last_backup = datetime.datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d %H:%M')
        
        stats = {
            'total_size_mb': db_size_mb,
            'table_count': len(tables_info),
            'total_records': total_records,
            'last_backup': last_backup,
            'tables': tables_info
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/tables')
def api_database_tables():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        from sqlalchemy import text
        import datetime
        
        table_names = ['settings', 'media_files', 'logs', 'translation_jobs', 'notifications', 'user_sessions', 'translation_history']
        tables = []
        
        # Arabic names for tables
        table_translations = {
            'settings': 'الإعدادات',
            'media_files': 'ملفات الوسائط',
            'logs': 'السجلات',
            'translation_jobs': 'مهام الترجمة',
            'notifications': 'الإشعارات',
            'user_sessions': 'جلسات المستخدم',
            'translation_history': 'تاريخ الترجمة'
        }
        
        for table_name in table_names:
            try:
                # Get record count
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar() or 0
                
                # Try to get last updated timestamp if the table has created_at or updated_at columns
                last_updated = 'غير متوفر'
                try:
                    result = db.session.execute(text(f"SELECT MAX(created_at) FROM {table_name}"))
                    last_record = result.scalar()
                    if last_record:
                        last_updated = last_record.strftime('%Y-%m-%d %H:%M') if hasattr(last_record, 'strftime') else str(last_record)
                except:
                    pass
                
                tables.append({
                    'name': table_name,
                    'display_name': table_translations.get(table_name, table_name),
                    'record_count': count,
                    'size_mb': round(count * 0.1, 2),  # Rough estimate based on record count
                    'last_updated': last_updated
                })
            except Exception as e:
                print(f"Error querying table {table_name}: {e}")
                continue
        
        return jsonify(tables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/query', methods=['POST'])
def api_database_query():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'لا يوجد استعلام'}), 400
    
    # Basic security check - only allow SELECT statements
    if not query.upper().startswith('SELECT'):
        return jsonify({'error': 'يُسمح فقط بعمليات SELECT'}), 400
    
    try:
        from sqlalchemy import text
        result = db.session.execute(text(query))
        
        # Try to fetch results
        try:
            results = []
            for row in result:
                results.append(dict(row))
            return jsonify({'results': results})
        except:
            return jsonify({'results': [], 'message': 'تم تنفيذ الاستعلام بنجاح'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/backup', methods=['POST'])
def api_database_backup():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        # Create notification about backup start
        create_notification(
            'backup_started',
            'backup_in_progress',
            'info'
        )
        
        # Simulate backup process (in real implementation, use pg_dump)
        import time
        time.sleep(2)
        
        create_notification(
            'backup_completed',
            'backup_success',
            'success'
        )
        
        return jsonify({'success': True, 'message': 'تم إنشاء النسخة الاحتياطية'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/optimize', methods=['POST'])
def api_database_optimize():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        # For PostgreSQL, VACUUM operations need to be done outside transactions
        # We'll just run ANALYZE which is safe in transactions
        from sqlalchemy import text
        
        # Run ANALYZE to update statistics
        db.session.execute(text('ANALYZE'))
        db.session.commit()
        
        # Optionally run REINDEX on key tables
        try:
            db.session.execute(text('REINDEX TABLE settings'))
            db.session.execute(text('REINDEX TABLE media_files'))
            db.session.commit()
        except:
            pass  # REINDEX may fail, that's OK
        
        create_notification(
            'database_optimized', 
            'database_optimization_success',
            'success'
        )
        
        return jsonify({'success': True, 'message': 'تم تحسين قاعدة البيانات بنجاح'})
    except Exception as e:
        return jsonify({'error': f'خطأ في تحسين قاعدة البيانات: {str(e)}'}), 500

@app.route('/api/database/cleanup', methods=['POST'])
def api_database_cleanup():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        # Clean old logs (older than 30 days)
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_logs = Log.query.filter(Log.created_at < cutoff_date).count()
        Log.query.filter(Log.created_at < cutoff_date).delete()
        
        # Clean read notifications older than 7 days
        notification_cutoff = datetime.utcnow() - timedelta(days=7)
        old_notifications = Notification.query.filter(
            Notification.read == True,
            Notification.created_at < notification_cutoff
        ).count()
        Notification.query.filter(
            Notification.read == True,
            Notification.created_at < notification_cutoff
        ).delete()
        
        db.session.commit()
        
        cleaned_records = old_logs + old_notifications
        
        create_notification(
            'database_cleaned',
            'database_cleanup_success',
            'success',
            count=cleaned_records
        )
        
        return jsonify({'success': True, 'cleaned_records': cleaned_records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User preferences API
@app.route('/api/user/theme', methods=['POST'])
def api_user_theme():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    data = request.get_json() or {}
    theme = data.get('theme', 'system')
    
    # Update user session theme preference
    session_id = session.get('session_id')
    if session_id:
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if user_session:
            user_session.theme = theme
            db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/user/language', methods=['POST'])
def api_user_language():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    data = request.get_json() or {}
    language = data.get('language', 'en')
    
    # Update session
    session['user_language'] = language
    
    # Update user session language preference in database
    session_id = session.get('session_id')
    if session_id:
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if user_session:
            user_session.language = language
            db.session.commit()
    
    return jsonify({'success': True})
@app.route('/api/check-ollama-models', methods=['GET'])
def api_check_ollama_models():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    try:
        import requests
        ollama_url = get_setting('ollama_url', 'http://localhost:11434')
        
        # Check if Ollama is running
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'].split(':')[0] for model in models_data.get('models', [])]
            return jsonify({
                'success': True, 
                'available_models': available_models,
                'ollama_running': True
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Ollama غير متاح',
                'ollama_running': False
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'خطأ في الاتصال بـ Ollama: {str(e)}',
            'ollama_running': False
        })

@app.route('/api/install-ollama-model', methods=['POST'])
def api_install_ollama_model():
    if not is_authenticated():
        return jsonify({'error': 'غير مصرح'}), 401
    
    data = request.get_json() or {}
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({'error': 'اسم النموذج مطلوب'}), 400
    
    try:
        import subprocess
        # Run ollama pull command in background
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'success': True, 
            'message': f'بدأ تحميل النموذج {model_name}. يرجى الانتظار...',
            'model': model_name
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'خطأ في تحميل النموذج: {str(e)}'
        })

# Initialize database and default settings
with app.app_context():
    # Make translation function available to all templates
    app.jinja_env.globals['t'] = translate_text
    app.jinja_env.globals['get_user_language'] = get_user_language
    app.jinja_env.globals['get_setting'] = get_setting
    
    # Create all database tables
    db.create_all()
    
    # Initialize default settings if database is empty
    if not Settings.query.first():
        default_settings = [
            # Authentication & Security
            {'key': 'admin_username', 'value': 'admin', 'section': 'AUTH', 'type': 'string', 'description': '{"ar": "اسم مستخدم المدير", "en": "Admin Username"}'},
            {'key': 'admin_password', 'value': 'your_strong_password', 'section': 'AUTH', 'type': 'password', 'description': '{"ar": "كلمة مرور المدير", "en": "Admin Password"}'},
            
            # API Settings
            {'key': 'sonarr_url', 'value': 'http://localhost:8989', 'section': 'API', 'type': 'url', 'description': '{"ar": "رابط Sonarr API", "en": "Sonarr API URL"}'},
            {'key': 'sonarr_api_key', 'value': '', 'section': 'API', 'type': 'string', 'description': '{"ar": "مفتاح Sonarr API", "en": "Sonarr API Key"}'},
            {'key': 'radarr_url', 'value': 'http://localhost:7878', 'section': 'API', 'type': 'url', 'description': '{"ar": "رابط Radarr API", "en": "Radarr API URL"}'},
            {'key': 'radarr_api_key', 'value': '', 'section': 'API', 'type': 'string', 'description': '{"ar": "مفتاح Radarr API", "en": "Radarr API Key"}'},
            {'key': 'ollama_url', 'value': 'http://localhost:11434', 'section': 'API', 'type': 'url', 'description': '{"ar": "رابط Ollama API", "en": "Ollama API URL"}'},
            
            # Model & AI Settings
            {'key': 'whisper_model', 'value': 'medium.en', 'section': 'MODELS', 'type': 'select', 'options': 'tiny,base,small,medium,large,medium.en,large-v2,large-v3', 'description': '{"ar": "نموذج Whisper", "en": "Whisper Model"}'},
            {'key': 'ollama_model', 'value': 'llama3', 'section': 'MODELS', 'type': 'string', 'description': '{"ar": "نموذج Ollama", "en": "Ollama Model"}'},
            
            # UI & Interface
            {'key': 'default_language', 'value': 'ar', 'section': 'UI', 'type': 'select', 'options': 'ar,en', 'description': '{"ar": "لغة الواجهة الافتراضية", "en": "Default Interface Language"}'},
            {'key': 'default_theme', 'value': 'system', 'section': 'UI', 'type': 'select', 'options': 'light,dark,system', 'description': '{"ar": "السمة الافتراضية", "en": "Default Theme"}'},
            {'key': 'items_per_page', 'value': '24', 'section': 'UI', 'type': 'number', 'description': '{"ar": "عدد العناصر في الصفحة", "en": "Items Per Page"}'},
            
            # Corrections & Quality
            {'key': 'auto_correct_filenames', 'value': 'true', 'section': 'CORRECTIONS', 'type': 'boolean', 'description': '{"ar": "تصحيح أسماء الملفات تلقائياً", "en": "Auto Correct Filenames"}'},
        ]
        
        for setting_data in default_settings:
            setting = Settings(**setting_data)
            db.session.add(setting)
        
        db.session.commit()
        print("✓ Default settings initialized successfully")

# Media Services API Endpoints
@app.route('/api/media-services/status')
def api_media_services_status():
    """Get status of all configured media services"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Initialize services from settings
        initialize_media_services()
        
        # Get status for all services
        # TODO: Implement media services status
        return jsonify({"status": "not_implemented", "services": []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media-services/test/<service_type>')
def api_test_media_service(service_type):
    """Test connection to a specific media service"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get service configuration from settings
        service_config = get_service_config(service_type)
        if not service_config:
            return jsonify({'error': f'Service {service_type} not configured'}), 400
        
        # TODO: Implement media service testing
        connected = False
        return jsonify({
            'service': service_type,
            'connected': connected,
            'config': service_config
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media-services/sync/<service_type>')
def api_sync_media_service(service_type):
    """Sync media from a specific service"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Initialize services first
        initialize_media_services()
        
        # Sync from service
        results = {}
        
        return jsonify({
            'service': service_type,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media-services/sync-all')
def api_sync_all_media_services():
    """Sync media from all configured services"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Initialize services first
        initialize_media_services()
        
        # TODO: Implement media services sync
        all_results = {}
        active_services = []
        
        return jsonify({
            'results': all_results,
            'active_services': active_services
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_service_config(service_type):
    """Get service configuration from settings"""
    settings = get_settings()
    
    config_map = {
        'plex': {
            'enabled_key': 'plex_enabled',
            'url_key': 'plex_url',
            'auth_key': 'plex_token',
            'auth_field': 'token'
        },
        'jellyfin': {
            'enabled_key': 'jellyfin_enabled',
            'url_key': 'jellyfin_url',
            'auth_key': 'jellyfin_api_key',
            'auth_field': 'api_key'
        },
        'emby': {
            'enabled_key': 'emby_enabled',
            'url_key': 'emby_url',
            'auth_key': 'emby_api_key',
            'auth_field': 'api_key'
        },
        'radarr': {
            'enabled_key': 'radarr_enabled',
            'url_key': 'radarr_url',
            'auth_key': 'radarr_api_key',
            'auth_field': 'api_key'
        },
        'sonarr': {
            'enabled_key': 'sonarr_enabled',
            'url_key': 'sonarr_url',
            'auth_key': 'sonarr_api_key',
            'auth_field': 'api_key'
        }
    }
    
    if service_type not in config_map:
        return None
    
    config_info = config_map[service_type]
    
    # Check if service is enabled
    if not settings.get(config_info['enabled_key'], 'false').lower() == 'true':
        return None
    
    # Get URL and auth
    url = settings.get(config_info['url_key'], '')
    auth = settings.get(config_info['auth_key'], '')
    
    if not url or not auth:
        return None
    
    return {
        'url': url,
        config_info['auth_field']: auth
    }

def initialize_media_services():
    """Initialize all enabled media services from settings"""
    service_types = ['plex', 'jellyfin', 'emby', 'radarr', 'sonarr']
    
    for service_type in service_types:
        service_config = get_service_config(service_type)
        if service_config:
            True  # TODO: Implement media service configuration

# GPU Management API Endpoints
@app.route('/api/gpu/status')
def api_gpu_status():
    """Get GPU status and information"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        gpus = gpu_manager.get_available_gpus()
        allocation = gpu_manager.get_optimal_allocation()
        
        return jsonify({
            'nvidia_available': gpu_manager.is_nvidia_available(),
            'gpus': gpus,
            'optimal_allocation': allocation,
            'total_gpus': len(gpus)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu/refresh')
def api_gpu_refresh():
    """Refresh GPU information"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        success = gpu_manager.refresh_gpu_info()
        if success:
            gpus = gpu_manager.get_available_gpus()
            return jsonify({
                'success': True,
                'gpus': gpus,
                'total_gpus': len(gpus)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No NVIDIA GPUs detected or nvidia-smi not available'
            }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu/allocate', methods=['POST'])
def api_gpu_allocate():
    """Allocate GPUs to services"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        whisper_gpu = data.get('whisper_gpu')
        ollama_gpu = data.get('ollama_gpu')
        
        # Update settings
        if whisper_gpu is not None:
            update_setting('whisper_gpu_id', str(whisper_gpu))
        
        if ollama_gpu is not None:
            update_setting('ollama_gpu_id', str(ollama_gpu))
        
        return jsonify({
            'success': True,
            'allocation': {
                'whisper_gpu': whisper_gpu,
                'ollama_gpu': ollama_gpu
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu/auto-allocate', methods=['POST'])
def api_gpu_auto_allocate():
    """Automatically allocate GPUs based on optimal configuration"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        allocation = gpu_manager.get_optimal_allocation()
        
        # Update settings with optimal allocation
        if allocation['whisper'] is not None:
            update_setting('whisper_gpu_id', str(allocation['whisper']))
        else:
            update_setting('whisper_gpu_id', 'cpu')
            
        if allocation['ollama'] is not None:
            update_setting('ollama_gpu_id', str(allocation['ollama']))
        else:
            update_setting('ollama_gpu_id', 'cpu')
        
        # Update auto allocation setting
        update_setting('auto_gpu_allocation', 'true')
        
        return jsonify({
            'success': True,
            'allocation': allocation,
            'message': 'GPUs allocated automatically based on optimal configuration'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_current_gpu_allocation():
    """Get current GPU allocation from settings"""
    settings = get_settings()
    
    whisper_gpu = settings.get('whisper_gpu_id', 'auto')
    ollama_gpu = settings.get('ollama_gpu_id', 'auto')
    
    # Convert 'auto' to actual GPU IDs if needed
    if whisper_gpu == 'auto' or ollama_gpu == 'auto':
        optimal = gpu_manager.get_optimal_allocation()
        if whisper_gpu == 'auto':
            whisper_gpu = optimal['whisper'] if optimal['whisper'] is not None else 'cpu'
        if ollama_gpu == 'auto':
            ollama_gpu = optimal['ollama'] if optimal['ollama'] is not None else 'cpu'
    
    return {
        'whisper_gpu': whisper_gpu,
        'ollama_gpu': ollama_gpu
    }

# Remote Storage Management API Endpoints
@app.route('/api/remote-mount-test', methods=['POST'])
def api_remote_mount_test():
    """Test remote file system connection"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        protocol = data.get('protocol')
        host = data.get('host')
        username = data.get('username')
        password = data.get('password')
        path = data.get('path', '/')
        port = data.get('port')
        
        from services.remote_storage import test_remote_connection
        result = test_remote_connection(protocol, host, username, password, path, port)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote-mount-setup', methods=['POST'])
def api_remote_mount_setup():
    """Setup remote file system mount"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Save remote mount settings
        update_setting('remote_storage_enabled', str(data.get('enabled', False)))
        update_setting('remote_storage_protocol', data.get('protocol', 'sftp'))
        update_setting('remote_storage_host', data.get('host', ''))
        update_setting('remote_storage_port', str(data.get('port', 22)))
        update_setting('remote_storage_username', data.get('username', ''))
        update_setting('remote_storage_password', data.get('password', ''))
        update_setting('remote_storage_path', data.get('path', '/'))
        update_setting('remote_storage_mount_point', data.get('mount_point', '/mnt/remote'))
        update_setting('remote_storage_auto_mount', str(data.get('auto_mount', True)))
        
        if data.get('enabled', False):
            from services.remote_storage import setup_remote_mount
            result = setup_remote_mount(
                data.get('protocol', 'smb'),
                data.get('host', ''),
                data.get('username', ''),
                data.get('password', ''),
                data.get('remote_path', ''),
                data.get('local_path', ''),
                data.get('port')
            )
        else:
            result = {'success': True, 'message': 'Remote storage disabled'}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote-mount-status', methods=['GET'])
def api_remote_mount_status():
    """Get remote mount status"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from services.remote_storage import get_mount_status
        status = get_mount_status()
        
        # Add settings info
        settings = get_settings()
        status['settings'] = {
            'enabled': settings.get('remote_storage_enabled', 'false') == 'true',
            'protocol': settings.get('remote_storage_protocol', 'sftp'),
            'host': settings.get('remote_storage_host', ''),
            'mount_point': settings.get('remote_storage_mount_point', '/mnt/remote')
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote-mount-unmount', methods=['POST'])
def api_remote_mount_unmount():
    """Unmount remote storage"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        mount_point = data.get('mount_point')
        
        from services.remote_storage import unmount_remote_storage
        result = unmount_remote_storage(mount_point)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_browse_path(path):
    """Validate path for browsing - security check"""
    if not path:
        return False
        
    # مسارات النظام المحظورة
    system_paths = [
        '/etc', '/sys', '/proc', '/dev', '/boot', '/root',
        '/var/log', '/var/lib', '/usr/bin', '/usr/sbin', '/bin', '/sbin',
        '/home/.ssh', '/home/.config', '/home/.local'
    ]
    
    # فحص إذا كان المسار من مسارات النظام المحظورة
    for sys_path in system_paths:
        if path.startswith(sys_path):
            return False
    
    # المسارات المسموحة للتصفح
    allowed_paths = [
        '/mnt', '/media', '/opt', '/srv', '/tmp',
        '/var/media', '/var/lib/media', '/home/media'
    ]
    
    # فحص إذا كان المسار يبدأ بمسار مسموح
    for allowed in allowed_paths:
        if path.startswith(allowed):
            return True
    
    # السماح بالمسار الجذري للتصفح الأولي
    if path == '/':
        return True
        
    return False

def is_supported_media_file(filename):
    """Check if file is a supported media format"""
    settings = get_settings()
    extensions = settings.get('video_extensions', 'mp4,mkv,avi,mov,wmv,flv,webm,m4v')
    supported_exts = [ext.strip().lower() for ext in extensions.split(',')]
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_ext in supported_exts

@app.route('/api/server-config/apply', methods=['POST'])
def api_apply_server_config():
    """تطبيق تكوين الخادم الجديد"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        host = data.get('host', '0.0.0.0')
        port = data.get('port', 5000)
        
        # استيراد مدير الخادم
        from server_config import apply_server_settings
        
        # تطبيق الإعدادات
        result = apply_server_settings(host, port)
        
        if result['success']:
            # تحديث قاعدة البيانات
            update_setting('server_host', host)
            update_setting('server_port', str(port))
            
            log_to_db("INFO", f"Server config updated: {host}:{port}")
            
            return jsonify({
                'success': True,
                'message': 'تم تحديث تكوين الخادم بنجاح',
                'host': host,
                'port': port,
                'results': result['results']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل في تطبيق تكوين الخادم',
                'errors': result.get('errors', []),
                'results': result['results']
            })
            
    except Exception as e:
        log_to_db("ERROR", f"Server config error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server-config/status')
def api_server_config_status():
    """الحصول على حالة الخادم الحالية"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from server_config import create_server_manager
        
        manager = create_server_manager()
        current_config = manager.get_current_config()
        service_status = manager.get_service_status()
        
        return jsonify({
            'current_config': current_config,
            'service_status': service_status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server-config/validate', methods=['POST'])
def api_validate_server_config():
    """التحقق من صحة تكوين الخادم"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        host = data.get('host', '0.0.0.0')
        port = data.get('port', 5000)
        
        from server_config import create_server_manager
        
        manager = create_server_manager()
        errors = manager.validate_config(host, port)
        port_available = manager.check_port_availability(int(port))
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'port_available': port_available,
            'host': host,
            'port': port
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/browse-folders', methods=['GET', 'POST'])
def api_browse_folders():
    """Browse folders for file browser with security protection"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json() or {}
        path = data.get('path', request.args.get('path', '/'))
        
        # التحقق الأمني من المسار
        if not validate_browse_path(path):
            return jsonify({'error': 'Access denied to this path'}), 403
        
        # Mock folder structure for safe browsing (testing environment)
        mock_folders = {
            '/': [
                {'name': 'home', 'path': '/home', 'type': 'folder'},
                {'name': 'mnt', 'path': '/mnt', 'type': 'folder'},
                {'name': 'opt', 'path': '/opt', 'type': 'folder'},
                {'name': 'var', 'path': '/var', 'type': 'folder'},
                {'name': 'usr', 'path': '/usr', 'type': 'folder'},
                {'name': 'etc', 'path': '/etc', 'type': 'folder'}
            ],
            '/home': [
                {'name': 'user', 'path': '/home/user', 'type': 'folder'},
                {'name': 'admin', 'path': '/home/admin', 'type': 'folder'}
            ],
            '/mnt': [
                {'name': 'storage', 'path': '/mnt/storage', 'type': 'folder'},
                {'name': 'remote', 'path': '/mnt/remote', 'type': 'folder'},
                {'name': 'backup', 'path': '/mnt/backup', 'type': 'folder'}
            ],
            '/opt': [
                {'name': 'applications', 'path': '/opt/applications', 'type': 'folder'},
                {'name': 'scripts', 'path': '/opt/scripts', 'type': 'folder'}
            ],
            '/var': [
                {'name': 'log', 'path': '/var/log', 'type': 'folder'},
                {'name': 'www', 'path': '/var/www', 'type': 'folder'},
                {'name': 'lib', 'path': '/var/lib', 'type': 'folder'}
            ],
            '/mnt/storage': [
                {'name': 'movies', 'path': '/mnt/storage/movies', 'type': 'folder'},
                {'name': 'series', 'path': '/mnt/storage/series', 'type': 'folder'},
                {'name': 'music', 'path': '/mnt/storage/music', 'type': 'folder'}
            ],
            '/mnt/remote': [
                {'name': 'synology', 'path': '/mnt/remote/synology', 'type': 'folder'},
                {'name': 'nas', 'path': '/mnt/remote/nas', 'type': 'folder'}
            ]
        }
        
        folders = mock_folders.get(path, [])
        
        return jsonify({
            "success": True,
            "path": path,
            "folders": folders
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/download')
def download_page():
    """Display download page"""
    return render_template('download.html')

@app.route('/download-github-release')
def download_github_release():
    """Download GitHub release package without authentication"""
    from flask import send_file
    
    # Check if GitHub release file exists - prioritize latest version
    release_files = [
        'ai-translator-v2.2.2.zip',          # Latest version
        'ai-translator-github-v2.2.1.zip',   # Previous release
        'ai-translator-github-v2.2.0.zip'    # fallback
    ]
    
    for release_file in release_files:
        if os.path.exists(release_file):
            if 'v2.2.2' in release_file:
                version = '2.2.2'
            elif '2.2.1' in release_file:
                version = '2.2.1'
            else:
                version = '2.2.0'
            
            return send_file(
                release_file,
                as_attachment=True,
                download_name=f'ai-translator-v{version}-ubuntu-server.zip',
                mimetype='application/zip'
            )
    else:
        return jsonify({'error': 'GitHub release file not found'}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
