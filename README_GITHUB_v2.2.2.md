# AI Translator (الترجمان الآلي) v2.2.2

<div align="center">

![AI Translator Logo](https://img.shields.io/badge/AI-Translator-2563eb?style=for-the-badge&logo=robot&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.2.2-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPL%20v3-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20Server-orange?style=for-the-badge&logo=ubuntu)

**Production-ready AI-powered translation system for converting movies and TV shows to Arabic with complete Ubuntu Server compatibility.**

[Quick Install](#-quick-installation) • [Features](#-features) • [Documentation](#-documentation) • [Support](#-support)

</div>

---

## 🚀 Quick Installation

### Ubuntu Server 22.04+ / 24.04 (Minimal Recommended)

```bash
# One-command installation
curl -fsSL https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_ubuntu_server_v2.2.2.sh | sudo bash
```

### Manual Installation
```bash
# Download installation script
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_ubuntu_server_v2.2.2.sh
chmod +x install_ubuntu_server_v2.2.2.sh
sudo ./install_ubuntu_server_v2.2.2.sh
```

### Verify Installation
```bash
# Download and run test script
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/test_ubuntu_installation.sh
chmod +x test_ubuntu_installation.sh
sudo ./test_ubuntu_installation.sh
```

**Default Access**: `http://YOUR_SERVER_IP` • Username: `admin` • Password: `your_strong_password`

---

## 🎯 What's New in v2.2.2

### ✅ **Complete Ubuntu Server Compatibility**
- **Production-Ready**: Tested on Ubuntu Server 22.04+ and 24.04 LTS
- **Minimal Server Support**: Optimized for Ubuntu Server Minimal installations
- **Safe Database Initialization**: Advanced error handling prevents crashes during setup
- **Original Features Preserved**: All v2.2.1 functionality maintained

### ✅ **Enhanced Installation System**
- **Automated Setup**: Complete installation with dependency checking
- **Service Management**: Systemd service with proper dependencies
- **Error Recovery**: Robust handling of setup and runtime issues
- **Testing Suite**: Comprehensive verification tools included

### ✅ **Professional Web Interface**
- **Arabic RTL Support**: Complete right-to-left interface with Tajawal font
- **Dark Professional Theme**: Modern styling with excellent usability
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Monitoring**: Live system status and progress tracking

---

## ⭐ Features

### 🤖 AI-Powered Translation
- **OpenAI Whisper**: Advanced speech-to-text conversion
- **Ollama + Llama 3**: Local LLM for high-quality Arabic translation
- **Batch Processing**: Handle multiple files simultaneously
- **Quality Control**: Subtitle correction and verification tools

### 🌐 Web Management Interface
- **Professional Dashboard**: Real-time system monitoring
- **File Management**: Upload, organize, and track media files
- **Progress Tracking**: Live translation progress with detailed logs
- **User Authentication**: Secure login system with session management

### 📊 Media Server Integration
- **Sonarr Integration**: Automatic TV series management
- **Radarr Integration**: Movie library management and metadata
- **Plex Support**: Direct integration with Plex Media Server
- **Jellyfin & Emby**: Support for alternative media servers

### 🗄️ Database & Storage
- **PostgreSQL Backend**: Robust database with proper relationships
- **File Organization**: Intelligent media file management
- **Progress Logging**: Comprehensive translation history
- **Backup Support**: Easy backup and restore functionality

---

## 📋 System Requirements

### **Minimum Requirements**
- Ubuntu Server 22.04+ LTS or 24.04 LTS (Minimal/Full)
- 4GB RAM (8GB recommended for AI processing)
- 10GB disk space (for application and media processing)
- Internet connection for initial setup and AI model downloads

### **Automatically Installed**
- Python 3.9+ with virtual environment
- PostgreSQL database with user setup
- Nginx reverse proxy
- FFmpeg for video processing
- All required Python packages

### **Optional (For Enhanced Performance)**
- NVIDIA GPU for AI acceleration
- Additional storage for large media libraries
- Higher RAM for concurrent processing

---

## 🔧 Configuration

### **Default Setup**
- **Installation Path**: `/root/ai-translator`
- **Database**: PostgreSQL with `ai_translator` user
- **Web Server**: Nginx reverse proxy on port 80
- **Application**: Gunicorn WSGI server on port 5000

### **Service Management**
```bash
# Service control
sudo systemctl start ai-translator    # Start service
sudo systemctl stop ai-translator     # Stop service
sudo systemctl restart ai-translator  # Restart service
sudo systemctl status ai-translator   # Check status

# View logs
sudo journalctl -u ai-translator -f   # Follow logs
sudo journalctl -u ai-translator -n 50 # Last 50 entries
```

### **File Locations**
- **Application**: `/root/ai-translator`
- **Virtual Environment**: `/root/ai-translator/venv`
- **Service File**: `/etc/systemd/system/ai-translator.service`
- **Nginx Config**: `/etc/nginx/sites-available/ai-translator`
- **Database**: PostgreSQL `ai_translator` database

---

## 🛠️ Usage

### **1. Access Web Interface**
Navigate to `http://YOUR_SERVER_IP` and login with:
- **Username**: `admin`
- **Password**: `your_strong_password`

### **2. Configure Media Services** (Optional)
- Add your Sonarr/Radarr API keys in Settings
- Configure path mappings for your media library
- Set up Plex/Jellyfin integration if needed

### **3. Upload Media Files**
- Use the File Management interface to upload videos
- Support for MP4, MKV, AVI, MOV, and other formats
- Automatic metadata extraction and organization

### **4. Start Translation**
- Select files for translation in the dashboard
- Monitor progress in real-time
- Review and download completed Arabic subtitles

---

## 🐛 Troubleshooting

### **Service Won't Start**
```bash
# Check detailed logs
sudo journalctl -u ai-translator --no-pager -l

# Verify Python environment
cd /root/ai-translator && source venv/bin/activate
python -c "import flask, psycopg2; print('Dependencies OK')"
```

### **Database Connection Issues**
```bash
# Test database connection
sudo -u postgres psql -d ai_translator -c "SELECT 1;"

# Reset database if needed
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_translator;"
sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_pass2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;"
```

### **Web Interface Issues**
```bash
# Test application directly
curl http://127.0.0.1:5000

# Check nginx configuration
sudo nginx -t

# Restart services
sudo systemctl restart ai-translator nginx
```

---

## 📖 Documentation

- **[Release Notes](RELEASE_NOTES_v2.2.2.md)**: Detailed changelog and improvements
- **[Installation Guide](UBUNTU_SERVER_TEST_GUIDE.md)**: Complete setup instructions
- **[API Documentation](API_DOCUMENTATION.md)**: Developer reference
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project

---

## 🤝 Support

### **Get Help**
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share experiences
- **Documentation**: Comprehensive guides and troubleshooting

### **Community**
- **Developer**: عبدالمنعم عوض (AbdelmonemAwad)
- **Email**: Eg2@live.com
- **GitHub**: https://github.com/AbdelmonemAwad/ai-translator

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### **License Summary**
- ✅ **Free to use** for personal and commercial purposes
- ✅ **Open source** with full access to source code
- ✅ **Modify and distribute** under the same license
- ❌ **No warranty** - use at your own risk

---

## 🌟 Star This Project

If you find AI Translator useful, please consider giving it a star ⭐ on GitHub. It helps others discover the project and motivates continued development!

---

<div align="center">

**Made with ❤️ for the Arabic-speaking community**

[![GitHub stars](https://img.shields.io/github/stars/AbdelmonemAwad/ai-translator?style=social)](https://github.com/AbdelmonemAwad/ai-translator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AbdelmonemAwad/ai-translator?style=social)](https://github.com/AbdelmonemAwad/ai-translator/network)
[![GitHub issues](https://img.shields.io/github/issues/AbdelmonemAwad/ai-translator)](https://github.com/AbdelmonemAwad/ai-translator/issues)

</div>