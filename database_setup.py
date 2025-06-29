import sqlite3
import os
import secrets

# --- الإعدادات الأولية ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(PROJECT_DIR, "library.db")

def create_database():
    """
    Creates or updates the database schema and populates default settings.
    This function is idempotent and safe to run multiple times.
    """
    print(f"INFO: Connecting to database at: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("INFO: Creating 'settings' table if it doesn't exist...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, 
            value TEXT, 
            section TEXT, 
            type TEXT, 
            description TEXT,
            options TEXT
        )
    ''')
    
    print("INFO: Creating 'logs' table if it doesn't exist...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL, /* INFO, WARNING, ERROR, FIX */
            message TEXT NOT NULL,
            details TEXT
        )
    ''')
    
    print("INFO: Creating 'media_files' table if it doesn't exist...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_files (
            id INTEGER PRIMARY KEY,
            local_path TEXT NOT NULL UNIQUE,
            media_type TEXT NOT NULL, -- 'movie' or 'tv'
            has_arabic_subtitle BOOLEAN NOT NULL DEFAULT 0,
            status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
            poster_url TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    print("INFO: Populating default settings...")
    # قاموس الإعدادات الافتراضية
    default_settings = {
        'DEFAULT': {
            'web_username': ('admin', 'text', 'اسم مستخدم لوحة التحكم'),
            'web_password': ('your_strong_password', 'password', 'كلمة مرور لوحة التحكم'),
            'secret_key': (secrets.token_hex(16), 'password', 'مفتاح سري للتطبيق (لا تقم بتغييره)'),
            'items_per_page': ('24', 'number', 'عدد العناصر في صفحات إدارة الملفات'),
            'default_language': ('ar', 'select', 'اللغة الافتراضية للواجهة'),
            'server_port': ('5000', 'number', 'منفذ خادم التطبيق (يتطلب إعادة تشغيل الخدمة)'),
            'server_host': ('0.0.0.0', 'text', 'عنوان IP للخادم (0.0.0.0 للوصول من جميع الأجهزة)')
        },
        'API': {
            'radarr_url': ('http://192.168.0.250:8310', 'text', 'عنوان URL الخاص بـ Radarr'),
            'radarr_api_key': ('bf791a422f26468cbc0508efc4ee3348', 'password', 'مفتاح API الخاص بـ Radarr'),
            'sonarr_url': ('http://192.168.0.250:8989', 'text', 'عنوان URL الخاص بـ Sonarr'),
            'sonarr_api_key': ('644b50d65b27484ca449093e1064eb4d', 'password', 'مفتاح API الخاص بـ Sonarr')
        },
        'REMOTE_STORAGE': {
            # Connection and Protocol Settings
            'remote_storage_enabled': ('false', 'select', 'تفعيل تحميل التخزين البعيد'),
            'remote_storage_protocol': ('sftp', 'select', 'بروتوكول التخزين'),
            'remote_storage_host': ('', 'text', 'عنوان الخادم'),
            'remote_storage_port': ('22', 'number', 'منفذ الخادم'),
            'remote_storage_timeout': ('30', 'number', 'مهلة الاتصال (ثانية)'),
            
            # Authentication Settings
            'remote_storage_username': ('', 'text', 'اسم المستخدم'),
            'remote_storage_password': ('', 'password', 'كلمة المرور'),
            
            # Remote Base Path
            'remote_storage_path': ('/', 'text', 'مسار المجلد الجذري على التخزين البعيد'),
            
            # Mount Points for Remote Storage
            'remote_storage_movies_mount': ('/mnt/remote/movies', 'text', 'نقطة تحميل الأفلام'),
            'remote_storage_series_mount': ('/mnt/remote/series', 'text', 'نقطة تحميل المسلسلات'),
            
            # Auto Mount Settings
            'remote_storage_auto_mount': ('false', 'select', 'التحميل التلقائي عند البدء')
        },
        'PATHS': {
            # Remote Paths on Storage Server
            'remote_movies_root': ('/volume1/Download/complete', 'text', 'مسار الأفلام الجذري على التخزين البعيد'),
            'remote_tv_root': ('/volume1/tv show download', 'text', 'مسار المسلسلات الجذري على التخزين البعيد'),
            
            # Local Mount Points
            'local_movies_mount': ('/mnt/remote/movies/complete', 'text', 'نقطة تركيب الأفلام على هذا الخادم'),
            'local_tv_mount': ('/mnt/remote/tv', 'text', 'نقطة تركيب المسلسلات على هذا الخادم')
        },
        'MODELS': {
            'ollama_api_url': ('http://localhost:11434/api/generate', 'text', 'عنوان URL لواجهة Ollama API (اتركه كما هو)'),
            'ollama_model': ('llama3', 'text', 'نموذج اللغة المستخدم في Ollama'),
            'whisper_model': ('medium.en', 'text', 'نموذج Whisper (مثل: base.en, small.en, medium.en)')
        },
        'CORRECTIONS': {
            'rename_hi_srt': ('yes', 'boolean', 'إعادة تسمية ملفات .hi.srt إلى .ar.srt'),
            'rename_generic_srt': ('yes', 'boolean', 'إعادة تسمية ملفات .srt العامة (فقط إذا لم توجد ترجمات أخرى)')
        }
    }
    
    # إضافة عمود options إذا لم يكن موجود (للتوافق مع قواعد البيانات الحالية)
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN options TEXT")
        print("INFO: Added 'options' column to settings table")
    except sqlite3.OperationalError:
        pass  # العمود موجود بالفعل
    
    # حلقة لإدراج الإعدادات فقط إذا لم تكن موجودة
    for section, keys in default_settings.items():
        for key, (value, key_type, desc) in keys.items():
            # إضافة خيارات للإعدادات من نوع select
            options = None
            if key == 'default_language':
                options = 'ar:العربية,en:English'
            elif key == 'remote_storage_enabled':
                options = 'false:معطل,true:مفعل'
            elif key == 'remote_storage_protocol':
                options = 'sftp:SFTP (SSH),ftp:FTP,smb:SMB/CIFS,nfs:NFS'
            elif key == 'remote_storage_auto_mount':
                options = 'false:معطل,true:مفعل'
            
            cursor.execute(
                "INSERT OR IGNORE INTO settings (section, key, value, type, description, options) VALUES (?, ?, ?, ?, ?, ?)",
                (section, key, value, key_type, desc, options)
            )
    
    # إنشاء جدول خدمات الوسائط
    print("INFO: Creating 'media_services' table if it doesn't exist...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT NOT NULL,
            service_name TEXT NOT NULL,
            base_url TEXT NOT NULL,
            api_key TEXT,
            username TEXT,
            password TEXT,
            enabled BOOLEAN DEFAULT 1,
            last_sync DATETIME,
            sync_status TEXT DEFAULT 'pending',
            error_message TEXT,
            media_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إنشاء جدول أشكال الفيديو المدعومة  
    print("INFO: Creating 'video_formats' table if it doesn't exist...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_formats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            extension TEXT UNIQUE NOT NULL,
            format_name TEXT NOT NULL,
            supported BOOLEAN DEFAULT 1,
            ffmpeg_codec TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إضافة أشكال الفيديو المدعومة
    video_formats = [
        ('mp4', 'MPEG-4 Part 14', True, 'h264', 'أكثر أشكال الفيديو شيوعاً'),
        ('mkv', 'Matroska Video', True, 'h264', 'شكل مفتوح المصدر يدعم ترجمات متعددة'),
        ('avi', 'Audio Video Interleave', True, 'xvid', 'شكل قديم ولكن مدعوم على نطاق واسع'),
        ('mov', 'QuickTime Movie', True, 'h264', 'شكل Apple QuickTime'),
        ('wmv', 'Windows Media Video', True, 'wmv', 'شكل Microsoft Windows Media'),
        ('flv', 'Flash Video', True, 'flv', 'شكل Adobe Flash (قديم)'),
        ('webm', 'WebM', True, 'vp8', 'شكل مفتوح المصدر للويب'),
        ('m4v', 'iTunes Video', True, 'h264', 'شكل iTunes/QuickTime'),
        ('3gp', '3GPP', True, 'h263', 'شكل للهواتف المحمولة'),
        ('ogv', 'Ogg Video', True, 'theora', 'شكل مفتوح المصدر من Xiph'),
        ('ts', 'Transport Stream', True, 'h264', 'شكل البث التلفزيوني'),
        ('m2ts', 'Blu-ray Transport Stream', True, 'h264', 'شكل Blu-ray'),
        ('vob', 'DVD Video Object', True, 'mpeg2video', 'شكل DVD'),
        ('asf', 'Advanced Systems Format', True, 'wmv', 'شكل Microsoft متقدم'),
        ('rm', 'RealMedia', True, 'rv40', 'شكل RealNetworks'),
        ('rmvb', 'RealMedia Variable Bitrate', True, 'rv40', 'RealMedia بمعدل بت متغير')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO video_formats (extension, format_name, supported, ffmpeg_codec, description) VALUES (?, ?, ?, ?, ?)",
        video_formats
    )
    
    conn.commit()
    conn.close()
    print("\nSUCCESS: Database setup is complete!")
    print("- Added support for media services integration")
    print("- Added comprehensive video format support")  
    print("You can now proceed to set up the web application files.")

if __name__ == "__main__":
    create_database()
