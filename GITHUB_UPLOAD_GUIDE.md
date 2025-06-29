# دليل رفع AI Translator على GitHub
# GitHub Upload Guide for AI Translator

## 📋 الملفات الجاهزة للرفع / Files Ready for Upload

### الملفات الأساسية / Core Files:
- `README_GITHUB.md` → rename to `README.md`
- `RELEASES.md`
- `CONTRIBUTING.md` 
- `DEPENDENCIES.md`
- `.gitignore`
- `LICENSE`
- `app.py`
- `main.py`
- `models.py`
- `database_setup.py`
- `background_tasks.py`
- `process_video.py`
- `gpu_manager.py`
- `security_config.py`
- `server_config.py`
- `translations.py`
- `install.sh`
- `pyproject.toml`
- `uv.lock`

### المجلدات / Directories:
- `templates/` (all HTML files)
- `static/` (CSS, JS, assets)
- `services/` (media services integration)

## 🚀 خطوات الرفع / Upload Steps

### 1. إنشاء Repository جديد
1. اذهب إلى https://github.com
2. اضغط "New Repository"
3. املأ البيانات:
   - **Repository name**: `ai-translator`
   - **Description**: `AI-Powered Video Translation System - Advanced subtitle translation from English to Arabic using Whisper and Ollama`
   - **Visibility**: Public ✅
   - **Initialize**: لا تضع علامة على أي خيار (سنرفع الملفات يدوياً)

### 2. تحضير الملفات محلياً
```bash
# إنشاء مجلد محلي جديد
mkdir ai-translator-github
cd ai-translator-github

# تهيئة Git repository
git init
git branch -M main
```

### 3. نسخ الملفات من Replit
قم بتحميل هذه الملفات من Replit ورفعها في المجلد المحلي:

#### الملفات الجذرية:
- `README_GITHUB.md` (غيّر الاسم إلى `README.md`)
- `RELEASES.md`
- `CONTRIBUTING.md`
- `DEPENDENCIES.md`
- `.gitignore`
- `LICENSE`
- `app.py`
- `main.py`
- `models.py`
- `database_setup.py`
- `background_tasks.py`
- `process_video.py`
- `gpu_manager.py`
- `security_config.py`
- `server_config.py`
- `translations.py`
- `install.sh`
- `pyproject.toml`

#### المجلدات:
- نسخ مجلد `templates/` كاملاً
- نسخ مجلد `static/` كاملاً  
- نسخ مجلد `services/` كاملاً

### 4. إضافة الملفات إلى Git
```bash
# إضافة جميع الملفات
git add .

# أول commit
git commit -m "Initial release v2.1.0: AI-Powered Video Translation System

- Complete Arabic subtitle translation system
- OpenAI Whisper + Ollama integration  
- Support for 6 media servers (Plex, Jellyfin, Emby, Kodi, Radarr, Sonarr)
- Advanced GPU management system
- Bilingual Arabic/English interface
- Comprehensive documentation and installation guides"

# ربط بـ GitHub repository
git remote add origin https://github.com/[your-username]/ai-translator.git

# رفع الملفات
git push -u origin main
```

### 5. إعداد Repository Settings

#### Topics (المواضيع):
أضف هذه Topics في إعدادات Repository:
```
ai, translation, arabic, flask, whisper, ollama, subtitles, media-server, plex, jellyfin, gpu, python, machine-learning, speech-to-text, video-processing, automation
```

#### About Section:
```
AI-Powered Video Translation System for automatic English-to-Arabic subtitle generation using Whisper and Ollama. Features comprehensive media server integration, GPU management, and bilingual interface.
```

#### GitHub Pages (اختياري):
- اذهب إلى Settings → Pages
- اختر Source: "Deploy from a branch"
- Branch: `main`
- Folder: `/ (root)`

### 6. إنشاء Releases

#### إنشاء Tag للإصدار:
```bash
# إنشاء tag للإصدار الحالي
git tag -a v2.1.0 -m "Version 2.1.0: Server Configuration & Complete Documentation

Major Features:
- Smart server configuration with automatic IP detection
- Complete English documentation for GitHub
- Bilingual login page with language switcher
- Professional installation guides
- Enhanced security and GPU management

Files: 15,000+ lines of code, 1,267 lines of documentation"

# رفع Tags
git push origin --tags
```

#### إنشاء Release في GitHub:
1. اذهب إلى Releases → "Create a new release"
2. اختر Tag: `v2.1.0`
3. Release title: `Version 2.1.0 - Server Configuration & Complete Documentation`
4. Description: انسخ من `RELEASES.md`

### 7. إعداد Protection Rules (اختياري)
في Settings → Branches:
- أضف rule للـ `main` branch
- فعّل "Require pull request reviews"
- فعّل "Require status checks"

## 🔧 التحديثات المستقبلية / Future Updates

لتحديث Repository:
```bash
# عمل changes محلياً
git add .
git commit -m "Description of changes"
git push origin main

# للإصدارات الجديدة
git tag -a v2.2.0 -m "Version 2.2.0 description"
git push origin --tags
```

## 📊 إحصائيات المشروع / Project Stats

بعد الرفع ستحصل على:
- **Repository size**: ~50MB
- **Languages**: Python (85%), HTML (8%), CSS (4%), JavaScript (3%)
- **Files**: 50+ files
- **Documentation**: 1,267 lines
- **Code**: 15,000+ lines

## 🔗 روابط مهمة / Important Links

بعد الرفع:
- **Repository**: `https://github.com/[username]/ai-translator`
- **Documentation**: `https://[username].github.io/ai-translator` (إذا فعّلت Pages)
- **Releases**: `https://github.com/[username]/ai-translator/releases`
- **Issues**: `https://github.com/[username]/ai-translator/issues`

## ✅ التحقق من نجاح الرفع / Verify Upload

تأكد من:
- [ ] README.md يظهر بشكل صحيح
- [ ] جميع الملفات موجودة
- [ ] Topics مضافة
- [ ] Release مُنشأ
- [ ] License معرّف تلقائياً
- [ ] Repository public ومرئي

---

**ملاحظة**: بعد الرفع، شارك رابط Repository مع المجتمع وأضف النجوم الأولى!