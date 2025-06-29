# دليل التنصيب الشامل - AI Translator (الترجمان الآلي)
# Complete Installation Guide - AI Translator

## متطلبات النظام / System Requirements

### الأجهزة المطلوبة / Required Hardware
- **معالج / CPU**: Intel Core i5 أو AMD Ryzen 5 أو أفضل
- **ذاكرة الوصول العشوائي / RAM**: 16 GB أو أكثر (32 GB مفضل)
- **كرت الشاشة / GPU**: NVIDIA GTX 1060 6GB أو أفضل (8GB+ VRAM مطلوب)
- **التخزين / Storage**: 100 GB مساحة فارغة (SSD مفضل)
- **الشبكة / Network**: اتصال إنترنت سريع

### أنظمة التشغيل المدعومة / Supported Operating Systems
- Ubuntu Server 22.04 LTS
- Ubuntu Server 24.04 LTS
- Casa OS (أي إصدار)
- Debian 12+

## التنصيب السريع / Quick Installation

### 1. تحضير النظام / System Preparation
```bash
# تحديث النظام / Update system
sudo apt update && sudo apt upgrade -y

# تحميل ملف التنصيب / Download installer
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install.sh
chmod +x install.sh
```

### 2. تشغيل التنصيب / Run Installation
```bash
# تنصيب كامل مع GPU / Full installation with GPU support
sudo ./install.sh

# أو تنصيب بدون GPU (للاختبار فقط) / Or CPU-only install (testing only)
sudo ./install.sh --cpu-only
```

## الميزات المثبتة تلقائياً / Auto-Installed Features

### 🤖 مكونات الذكاء الاصطناعي / AI Components
- **OpenAI Whisper**: تحويل الصوت إلى نص (أحدث إصدار)
- **Ollama + Llama 3**: نموذج الترجمة المحلي
- **PyTorch**: مكتبة التعلم العميق مع دعم CUDA
- **Transformers**: مكتبات Hugging Face للذكاء الاصطناعي

### 🗄️ قاعدة البيانات / Database
- **PostgreSQL 15+**: قاعدة بيانات متقدمة مع دعم JSON
- **pgAdmin**: واجهة إدارة قاعدة البيانات
- **Automatic Backup**: نسخ احتياطي تلقائي يومي

### 🌐 خادم الويب / Web Server
- **Nginx**: خادم ويب عالي الأداء
- **Gunicorn**: خادم Python WSGI
- **SSL/TLS**: شهادات أمان تلقائية
- **Reverse Proxy**: توزيع الحمولة

### 🎥 معالجة الوسائط / Media Processing
- **FFmpeg**: معالجة الفيديو والصوت (16+ تشفير)
- **MediaInfo**: تحليل ملفات الوسائط
- **16+ Video Formats**: دعم جميع أشكال الفيديو الشائعة

### 🔧 إدارة الخدمات / Service Management
- **Systemd Services**: إدارة تلقائية للخدمات
- **Auto-restart**: إعادة تشغيل تلقائي عند الأخطاء
- **Log Rotation**: إدارة سجلات النظام
- **Health Monitoring**: مراقبة صحة النظام

## التحقق من التنصيب / Installation Verification

### 1. فحص الخدمات / Check Services
```bash
# فحص خدمة المترجم / Check translator service
sudo systemctl status ai-translator

# فحص قاعدة البيانات / Check database
sudo systemctl status postgresql

# فحص Ollama
sudo systemctl status ollama

# فحص Nginx
sudo systemctl status nginx
```

### 2. فحص GPU / GPU Check
```bash
# فحص كروت NVIDIA / Check NVIDIA cards
nvidia-smi

# فحص تخصيص GPU / Check GPU allocation
nvidia-smi -L
```

### 3. اختبار الوصول / Access Test
```bash
# اختبار المنفذ المحلي / Test local port
curl http://localhost:5000

# اختبار Nginx
curl http://localhost:80
```

## الوصول للتطبيق / Application Access

### عنوان الويب / Web Address
```
http://YOUR_SERVER_IP
أو / or
http://localhost (إذا كان محلي / if local)
```

### بيانات الدخول الافتراضية / Default Login
```
اسم المستخدم / Username: admin
كلمة المرور / Password: admin123
```

## التكوين المتقدم / Advanced Configuration

### 1. إعدادات الخادم / Server Configuration
- **تغيير المنفذ**: إمكانية تخصيص منفذ الخادم من الإعدادات (افتراضي: 5000)
- **عنوان IP**: تحديد عنوان الربط (افتراضي: 0.0.0.0 للوصول من جميع الأجهزة)
- **يتطلب إعادة تشغيل الخدمة** بعد تغيير إعدادات الشبكة

### 2. نظام الأمان المتقدم / Advanced Security System
- **حماية أدلة الملفات**: منع الوصول غير المصرح للمجلدات الحساسة
- **قائمة المسارات المحظورة**: /etc, /sys, /proc, /dev, /boot, /root
- **المسارات المسموحة فقط**: /mnt, /media, /opt/media, /srv/media
- **حماية من Directory Traversal**: منع استخدام ../ في المسارات
- **تسجيل الأحداث الأمنية**: مراقبة محاولات الوصول غير المصرح
- **حد أقصى لحجم الملفات**: 50GB لكل ملف
- **تنظيف المدخلات**: حماية من XSS والحقن الضار

### 3. تكوين GPU / GPU Configuration
- يتم اكتشاف كروت NVIDIA تلقائياً
- توزيع ذكي: Ollama للترجمة، Whisper للصوت
- إمكانية التخصيص اليدوي من واجهة الإعدادات

### 2. خدمات الوسائط / Media Services
يدعم التطبيق الاتصال مع:
- **Plex Media Server**
- **Jellyfin Media Server**
- **Emby Media Server**
- **Kodi Media Center**
- **Radarr** (إدارة الأفلام)
- **Sonarr** (إدارة المسلسلات)

### 3. التخزين البعيد / Remote Storage
- دعم SMB/CIFS
- دعم NFS
- دعم FTP/SFTP
- تصفح الملفات التفاعلي

## استكشاف الأخطاء / Troubleshooting

### مشاكل شائعة / Common Issues

#### 1. خطأ في GPU / GPU Error
```bash
# فحص تعريفات NVIDIA / Check NVIDIA drivers
nvidia-smi

# إعادة تثبيت التعريفات / Reinstall drivers
sudo apt install nvidia-driver-535
sudo reboot
```

#### 2. خطأ في قاعدة البيانات / Database Error
```bash
# إعادة تشغيل PostgreSQL / Restart PostgreSQL
sudo systemctl restart postgresql

# فحص حالة قاعدة البيانات / Check database status
sudo -u postgres psql -c "\l"
```

#### 3. خطأ في المنفذ / Port Error
```bash
# فحص المنافذ المستخدمة / Check used ports
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :80

# قتل العمليات المتداخلة / Kill conflicting processes
sudo fuser -k 5000/tcp
sudo fuser -k 80/tcp
```

### سجلات النظام / System Logs
```bash
# سجلات التطبيق / Application logs
sudo journalctl -u ai-translator -f

# سجلات قاعدة البيانات / Database logs
sudo journalctl -u postgresql -f

# سجلات Nginx / Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## إلغاء التنصيب / Uninstallation

### إزالة كاملة / Complete Removal
```bash
# إيقاف الخدمات / Stop services
sudo systemctl stop ai-translator nginx postgresql ollama

# إزالة الخدمات / Remove services
sudo systemctl disable ai-translator nginx postgresql ollama

# إزالة الملفات / Remove files
sudo rm -rf /opt/ai-translator
sudo rm -f /etc/systemd/system/ai-translator.service
sudo rm -f /etc/nginx/sites-enabled/ai-translator

# إزالة قاعدة البيانات / Remove database
sudo -u postgres dropdb ai_translator_db
sudo -u postgres dropuser ai_translator

# إزالة المستخدم / Remove user
sudo userdel -r ai-translator
```

## الدعم الفني / Technical Support

### معلومات المطور / Developer Information
- **الاسم / Name**: عبدالمنعم عوض (AbdelmonemAwad)
- **البريد الإلكتروني / Email**: Eg2@live.com
- **GitHub**: https://github.com/AbdelmonemAwad
- **الرخصة / License**: GNU GPL v3

### الحصول على المساعدة / Getting Help
1. قراءة هذا الدليل كاملاً
2. فحص سجلات النظام
3. البحث في مشاكل مشابهة على GitHub
4. إنشاء تقرير خطأ مفصل

---

## ملاحظات هامة / Important Notes

⚠️ **تحذير / Warning**: يتطلب النظام كرت شاشة NVIDIA مع 8GB+ VRAM للعمل الأمثل

✅ **التوافق / Compatibility**: تم اختبار النظام على Ubuntu Server 22.04 و Casa OS

🔒 **الأمان / Security**: تأكد من تغيير كلمة المرور الافتراضية بعد التنصيب

🚀 **الأداء / Performance**: للحصول على أفضل أداء، استخدم SSD وذاكرة 32GB+