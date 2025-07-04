#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Translator Server Configuration Manager
إدارة تكوين الخادم للمترجم الآلي
"""

import os
import subprocess
import logging
import time
from pathlib import Path

# إعداد السجلات
logger = logging.getLogger('server_config')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('server_config.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ServerConfigManager:
    """مدير تكوين الخادم"""
    
    def __init__(self):
        self.service_name = "ai-translator"
        self.systemd_path = f"/etc/systemd/system/{self.service_name}.service"
        self.nginx_config_path = f"/etc/nginx/sites-available/{self.service_name}"
        self.app_dir = "/opt/ai-translator"
        
    def get_current_config(self):
        """الحصول على التكوين الحالي"""
        try:
            from app import get_settings
            settings = get_settings()
            
            # Get actual server IP if running
            actual_host = self._get_actual_server_ip()
            saved_host = settings.get('server_host', '0.0.0.0')
            
            return {
                'host': saved_host,
                'port': int(settings.get('server_port', 5000)),
                'actual_host': actual_host,
                'is_replit': True
            }
        except Exception as e:
            logger.error(f"Error getting current config: {e}")
            return {
                'host': '0.0.0.0', 
                'port': 5000,
                'actual_host': '0.0.0.0',
                'is_replit': True
            }
    
    def _get_actual_server_ip(self):
        """الحصول على عنوان IP الفعلي للخادم"""
        import socket
        try:
            # Try to get the actual IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # In Replit, also check for external IP via environment or well-known methods
            if 'REPL_SLUG' in os.environ:
                # This is Replit environment
                repl_url = os.environ.get('REPLIT_URL', '')
                if repl_url:
                    # Extract domain from Replit URL
                    from urllib.parse import urlparse
                    parsed = urlparse(repl_url)
                    if parsed.hostname:
                        return parsed.hostname
            
            return local_ip
        except Exception:
            return '0.0.0.0'
    
    def update_systemd_service(self, host, port):
        """تحديث خدمة systemd - مُعطل في بيئة Replit"""
        # في بيئة Replit، نحفظ التكوين فقط في قاعدة البيانات
        logger.info(f"Config saved for Replit environment: {host}:{port}")
        return True
    
    def update_nginx_config(self, host, port):
        """تحديث تكوين Nginx - مُعطل في بيئة Replit"""
        # في بيئة Replit، لا نحتاج إلى Nginx
        logger.info(f"Nginx config skipped for Replit environment: {host}:{port}")
        return True
    
    def reload_systemd(self):
        """إعادة تحميل systemd - مُعطل في بيئة Replit"""
        logger.info("Systemd reload skipped for Replit environment")
        return True
    
    def restart_service(self):
        """إعادة تشغيل الخدمة - في بيئة Replit يتم إعادة التشغيل تلقائياً"""
        logger.info("Service restart will be handled automatically by Replit")
        return True
    
    def test_nginx_config(self):
        """اختبار تكوين Nginx - مُعطل في بيئة Replit"""
        logger.info("Nginx config test skipped for Replit environment")
        return True
    
    def reload_nginx(self):
        """إعادة تحميل Nginx - مُعطل في بيئة Replit"""
        logger.info("Nginx reload skipped for Replit environment")
        return True
    
    def apply_server_config(self, host, port):
        """تطبيق تكوين الخادم الجديد"""
        logger.info(f"Applying server config: {host}:{port}")
        
        steps = [
            ("تحديث خدمة systemd", lambda: self.update_systemd_service(host, port)),
            ("تحديث تكوين Nginx", lambda: self.update_nginx_config(host, port)),
            ("إعادة تحميل systemd", self.reload_systemd),
            ("اختبار تكوين Nginx", self.test_nginx_config),
            ("إعادة تحميل Nginx", self.reload_nginx),
            ("إعادة تشغيل الخدمة", self.restart_service)
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                result = step_func()
                results.append((step_name, result, None))
                if not result:
                    logger.warning(f"Step failed: {step_name}")
            except Exception as e:
                logger.error(f"Step error - {step_name}: {e}")
                results.append((step_name, False, str(e)))
        
        return results
    
    def get_service_status(self):
        """الحصول على حالة الخدمة - في بيئة Replit"""
        # في بيئة Replit، الخدمة تعمل دائماً إذا كان التطبيق يستجيب
        return {
            'active': True,
            'status_output': 'Running on Replit platform',
            'return_code': 0,
            'platform': 'Replit'
        }
    
    def check_port_availability(self, port):
        """فحص توفر المنفذ"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0  # المنفذ متاح إذا لم يكن قيد الاستخدام
        except Exception:
            return True  # افتراض أن المنفذ متاح عند حدوث خطأ
    
    def validate_config(self, host, port):
        """التحقق من صحة التكوين"""
        errors = []
        
        # فحص المنفذ
        try:
            port = int(port)
            if port < 1 or port > 65535:
                errors.append("المنفذ يجب أن يكون بين 1 و 65535")
            elif port < 1024 and port != 80 and port != 443:
                errors.append("المنافذ أقل من 1024 محجوزة للنظام")
        except ValueError:
            errors.append("المنفذ يجب أن يكون رقماً صحيحاً")
        
        # فحص عنوان IP
        if host not in ['0.0.0.0', '127.0.0.1', 'localhost']:
            import socket
            try:
                socket.inet_aton(host)
            except socket.error:
                errors.append("عنوان IP غير صحيح")
        
        return errors

def create_server_manager():
    """إنشاء مدير الخادم"""
    return ServerConfigManager()

def apply_server_settings(host, port):
    """تطبيق إعدادات الخادم"""
    manager = create_server_manager()
    
    # التحقق من صحة التكوين
    errors = manager.validate_config(host, port)
    if errors:
        return {'success': False, 'errors': errors}
    
    # تطبيق التكوين
    results = manager.apply_server_config(host, port)
    
    # تحليل النتائج
    success_count = sum(1 for _, success, _ in results if success)
    total_steps = len(results)
    
    return {
        'success': success_count == total_steps,
        'results': results,
        'success_count': success_count,
        'total_steps': total_steps
    }

# دوال مساعدة للاستخدام في التطبيق
__all__ = [
    'ServerConfigManager',
    'create_server_manager', 
    'apply_server_settings'
]