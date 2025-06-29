#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Translator Security Configuration
تكوين الأمان للمترجم الآلي
"""

import os
import logging
from functools import wraps
from flask import request, jsonify, session

# إعداد السجلات الأمنية
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
handler = logging.FileHandler('security.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
security_logger.addHandler(handler)

class SecurityConfig:
    """إعدادات الأمان للتطبيق"""
    
    # مسارات النظام المحظورة
    FORBIDDEN_PATHS = [
        '/etc', '/sys', '/proc', '/dev', '/boot', '/root',
        '/var/log', '/var/lib', '/usr/bin', '/usr/sbin', 
        '/bin', '/sbin', '/home/.ssh', '/home/.config',
        '/home/.local', '/home/.cache', '/tmp/systemd-private',
        '/run', '/lib', '/lib64'
    ]
    
    # المسارات المسموحة للتصفح
    ALLOWED_BROWSE_PATHS = [
        '/mnt', '/media', '/opt/media', '/srv/media',
        '/var/media', '/var/lib/media', '/home/media',
        '/storage', '/data'
    ]
    
    # امتدادات الملفات المسموحة
    ALLOWED_FILE_EXTENSIONS = [
        'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
        'm4v', '3gp', 'ogv', 'ts', 'm2ts', 'vob', 'asf',
        'rm', 'rmvb', 'mpg', 'mpeg', 'divx', 'xvid'
    ]
    
    # حد أقصى لحجم الملف (بالبايت) - 50GB
    MAX_FILE_SIZE = 50 * 1024 * 1024 * 1024
    
    # حد أقصى لعدد الملفات في المجلد الواحد
    MAX_FILES_PER_DIRECTORY = 1000
    
    # معدل الطلبات المسموح (طلبات في الدقيقة)
    RATE_LIMIT = 60

def log_security_event(event_type, details, ip_address=None):
    """تسجيل الأحداث الأمنية"""
    ip = ip_address or request.remote_addr if request else 'unknown'
    security_logger.warning(f"Security Event: {event_type} - IP: {ip} - Details: {details}")

def validate_file_path(file_path):
    """التحقق من صحة وأمان مسار الملف"""
    if not file_path:
        log_security_event("INVALID_PATH", "Empty file path")
        return False
    
    # تنظيف المسار
    clean_path = os.path.normpath(file_path)
    
    # منع Directory Traversal attacks
    if '..' in clean_path or clean_path.startswith('/'):
        log_security_event("DIRECTORY_TRAVERSAL", f"Attempted path: {file_path}")
        return False
    
    # فحص المسارات المحظورة
    for forbidden in SecurityConfig.FORBIDDEN_PATHS:
        if clean_path.startswith(forbidden.lstrip('/')):
            log_security_event("FORBIDDEN_PATH_ACCESS", f"Attempted path: {file_path}")
            return False
    
    return True

def validate_browse_path(path):
    """التحقق من أمان مسار التصفح"""
    if not path:
        return False
    
    # تنظيف المسار
    clean_path = os.path.normpath(path)
    
    # فحص المسارات المحظورة
    for forbidden in SecurityConfig.FORBIDDEN_PATHS:
        if clean_path.startswith(forbidden):
            log_security_event("FORBIDDEN_BROWSE", f"Attempted browse: {path}")
            return False
    
    # فحص المسارات المسموحة
    if clean_path == '/':
        return True
    
    for allowed in SecurityConfig.ALLOWED_BROWSE_PATHS:
        if clean_path.startswith(allowed):
            return True
    
    log_security_event("UNAUTHORIZED_BROWSE", f"Attempted browse: {path}")
    return False

def validate_file_extension(filename):
    """التحقق من امتداد الملف"""
    if not filename or '.' not in filename:
        return False
    
    ext = filename.lower().split('.')[-1]
    return ext in SecurityConfig.ALLOWED_FILE_EXTENSIONS

def check_file_size(file_path):
    """فحص حجم الملف"""
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > SecurityConfig.MAX_FILE_SIZE:
                log_security_event("OVERSIZED_FILE", f"File: {file_path}, Size: {size}")
                return False
        return True
    except Exception:
        return False

def safe_list_directory(path, max_files=None):
    """قائمة آمنة لمحتويات المجلد"""
    if not validate_browse_path(path):
        return None
    
    try:
        if not os.path.exists(path):
            return None
        
        items = []
        count = 0
        max_items = max_files or SecurityConfig.MAX_FILES_PER_DIRECTORY
        
        for item in os.listdir(path):
            if count >= max_items:
                break
                
            # تخطي الملفات المخفية
            if item.startswith('.'):
                continue
            
            item_path = os.path.join(path, item)
            
            try:
                if os.path.isdir(item_path):
                    if validate_browse_path(item_path):
                        items.append({
                            'name': item,
                            'path': item_path,
                            'type': 'folder',
                            'size': None
                        })
                        count += 1
                elif os.path.isfile(item_path):
                    if validate_file_extension(item):
                        file_size = os.path.getsize(item_path)
                        if file_size <= SecurityConfig.MAX_FILE_SIZE:
                            items.append({
                                'name': item,
                                'path': item_path,
                                'type': 'file',
                                'size': file_size
                            })
                            count += 1
            except (OSError, PermissionError):
                # تخطي الملفات التي لا يمكن الوصول إليها
                continue
        
        return sorted(items, key=lambda x: (x['type'] == 'file', x['name'].lower()))
        
    except PermissionError:
        log_security_event("PERMISSION_DENIED", f"Directory: {path}")
        return None
    except Exception as e:
        log_security_event("DIRECTORY_ERROR", f"Directory: {path}, Error: {str(e)}")
        return None

def require_authentication(f):
    """مطلوب تسجيل الدخول للوصول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            log_security_event("UNAUTHORIZED_ACCESS", f"Function: {f.__name__}")
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_check(f):
    """فحص معدل الطلبات"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # تنفيذ بسيط لمعدل الطلبات
        # يمكن تحسينه باستخدام Redis أو ذاكرة التخزين المؤقت
        ip = request.remote_addr
        # TODO: تنفيذ آلية Rate Limiting متقدمة
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(input_string, max_length=255):
    """تنظيف المدخلات من المحارف الضارة"""
    if not input_string:
        return ""
    
    # إزالة المحارف الضارة
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r']
    cleaned = input_string
    
    for char in dangerous_chars:
        cleaned = cleaned.replace(char, '')
    
    # حد أقصى للطول
    return cleaned[:max_length]

def get_secure_config():
    """الحصول على إعدادات الأمان الحالية"""
    return {
        'max_file_size': SecurityConfig.MAX_FILE_SIZE,
        'max_files_per_dir': SecurityConfig.MAX_FILES_PER_DIRECTORY,
        'allowed_extensions': SecurityConfig.ALLOWED_FILE_EXTENSIONS,
        'rate_limit': SecurityConfig.RATE_LIMIT
    }

# تصدير الوظائف الرئيسية
__all__ = [
    'validate_file_path',
    'validate_browse_path', 
    'validate_file_extension',
    'safe_list_directory',
    'require_authentication',
    'rate_limit_check',
    'sanitize_input',
    'log_security_event',
    'get_secure_config'
]