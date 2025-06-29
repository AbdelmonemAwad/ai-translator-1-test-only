# AI Translator (الترجمان الآلي)
**Version 2.1.0 - AI-Powered Video Translation System**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg)](https://postgresql.org)
[![AI Models](https://img.shields.io/badge/AI-Whisper%20%2B%20Ollama-orange.svg)](https://github.com/openai/whisper)

Advanced AI-powered system for automatic video content translation from English to Arabic using cutting-edge artificial intelligence technologies. Features a comprehensive web interface with full Arabic language support and integration with popular media servers.

---

## 🚀 Quick Installation

### Automated Installation (Recommended)
```bash
# Ubuntu/Debian
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

**Default Login Credentials:**
- Username: `admin`
- Password: `your_strong_password`

### Replit (Quick Trial)
[![Run on Repl.it](https://repl.it/badge/github/AbdelmonemAwad/ai-translator)](https://replit.com/new/github/AbdelmonemAwad/ai-translator)

### Docker (Coming Soon)
```bash
# Coming in next release
docker run -p 5000:5000 abdelmonemawad/ai-translator:latest
```

---

## 🌟 Key Features

### 🤖 AI-Powered Translation
- **OpenAI Whisper**: High-accuracy speech-to-text conversion
- **Ollama + Llama 3**: Natural and fluent Arabic translation
- **Batch Processing**: Translate multiple files simultaneously
- **GPU Support**: Accelerated processing with graphics cards

### 📺 Media Server Integration
- **Plex Media Server**: Complete integration with token-based authentication
- **Jellyfin Media Server**: Full API integration with library synchronization
- **Emby Media Server**: Complete support with API key authentication
- **Kodi Media Center**: JSON-RPC integration for home media centers
- **Radarr**: Movie management with metadata and poster retrieval
- **Sonarr**: TV series management with automated episode tracking

### 🌐 Advanced Arabic Interface
- **RTL Design**: Optimized interface for Arabic language
- **Responsive**: Works seamlessly on all devices
- **Bilingual**: Easy switching between Arabic and English
- **Dark/Light Mode**: Support for different viewing preferences

### ⚙️ Advanced Management
- **Smart Server Configuration**: Automatic display of current server information
- **GPU Management**: Intelligent distribution of graphics card resources
- **System Monitoring**: Real-time resource status display
- **Comprehensive Logging**: Detailed tracking of all operations

### 🔧 Professional Features
- **Database Administration**: Built-in PostgreSQL management with backup and optimization
- **Translation Status Tracking**: Comprehensive file status monitoring and progress tracking
- **Blacklist Management**: Advanced file filtering and exclusion system
- **Notification System**: Real-time alerts and system status notifications
- **Remote Storage**: Support for network-attached storage systems (NFS, SMB, SFTP)
- **File Browser System**: Interactive folder navigation with security protection
- **Security Framework**: Comprehensive file system protection with directory traversal prevention

### 🆕 Version 2.1.0 New Features
- **Enhanced Media Services**: Complete integration with 6 major media platforms
- **Mobile-First Design**: Fully responsive interface with collapsible sidebar navigation
- **Component Architecture**: Modular template system for better maintainability
- **Advanced GPU Support**: Multi-GPU detection with intelligent service distribution
- **Server Configuration**: Dynamic IP detection and port management
- **GitHub Integration**: Complete documentation system with professional release management

---

## 🛠️ System Requirements

### Minimum Requirements
- Ubuntu 20.04+ or Replit environment
- Python 3.9+ (3.9, 3.10, 3.11 supported)
- 16GB RAM
- 100GB storage
- NVIDIA GPU (recommended for AI processing)
- Stable internet connection

### Recommended Specifications
- Ubuntu 22.04+
- Python 3.11+
- 32GB+ RAM
- NVIDIA RTX series GPU
- SSD storage for faster processing
- 500GB+ SSD
- NVIDIA GPU with 8GB+ VRAM
- 100Mbps+ connection

---

## 📦 Installation Guide

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic requirements
sudo apt install git python3.11 python3.11-pip postgresql-14 ffmpeg -y
```

### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_2025';"
sudo -u postgres psql -c "CREATE DATABASE ai_translator_db OWNER ai_translator;"
```

### 3. Clone Project
```bash
# Clone from GitHub
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Environment Variables
```bash
export DATABASE_URL="postgresql://ai_translator:ai_translator_2025@localhost:5432/ai_translator_db"
export SESSION_SECRET=$(openssl rand -base64 32)
```

### 5. Install Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download Llama 3 model
ollama pull llama3
```

### 6. Run System
```bash
# Setup database
python database_setup.py

# Start server
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

---

## 📸 Screenshots

### Installation Guide
![Installation Steps](https://github.com/AbdelmonemAwad/ai-translator/raw/main/docs/screenshots/installation.png)

### Dashboard - Main Control Panel
![Dashboard](https://github.com/AbdelmonemAwad/ai-translator/raw/main/docs/screenshots/dashboard.png)

### File Management System
![File Management](https://github.com/AbdelmonemAwad/ai-translator/raw/main/docs/screenshots/files.png)

### Settings & Configuration
![Settings](https://github.com/AbdelmonemAwad/ai-translator/raw/main/docs/screenshots/settings.png)

### System Monitoring
![System Monitor](https://github.com/AbdelmonemAwad/ai-translator/raw/main/docs/screenshots/system-monitor.png)

**Features Shown:**
- **Bilingual Interface**: Complete Arabic/English support
- **Professional UI**: Modern dark theme with responsive design
- **Real-time Monitoring**: Live system status and progress tracking
- **Mobile Support**: Fully responsive design for all devices

*View more screenshots: [SCREENSHOTS.md](SCREENSHOTS.md)*

---

## 🔧 Usage

### Access Interface
1. Open browser and navigate to `http://localhost:5000`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `your_strong_password`

**Note**: Change the default password immediately after first login for security.

### Setup Media Servers
1. Go to **Settings** ← **Media Servers**
2. Enter connection details for your media server
3. Test connection and save settings
4. Sync media library

### Start Translation
1. Navigate to **File Management**
2. Select files to translate
3. Click **Translate Selected** or **Batch Translate**
4. Monitor progress from **Dashboard**

---

## 📊 Performance & Specifications

### Translation Rates
- **With GPU**: 10-15 minutes per video hour
- **Without GPU**: 30-45 minutes per video hour
- **Translation Quality**: 90%+ accuracy for clear content

### Resource Usage
- **Memory**: 8-16GB during processing
- **CPU**: 80-100% usage during translation
- **GPU**: 6-8GB VRAM for medium models
- **Storage**: 2-5GB per video hour (temporary)

---

## 🔧 Advanced Server Configuration

### New Network Settings (Version 2.1.0)
The system automatically displays current server information:

1. Go to **Settings** ← **System Management** ← **Server Configuration**
2. View current server information in the blue info box
3. Modify IP and port settings as needed:
   - **Public Access**: Use displayed address
   - **Local Access**: Use `127.0.0.1`
   - **Suggested Ports**: 5000, 8000, 3000

### Performance Optimization
```bash
# Optimize PostgreSQL
sudo nano /etc/postgresql/14/main/postgresql.conf

# Memory optimization for heavy processing
shared_buffers = 2GB
work_mem = 512MB
maintenance_work_mem = 1GB
```

---

## 📚 Documentation & Support

### Detailed Documentation
- 📖 [Comprehensive User Guide](USER_GUIDE_v2.1.0.md)
- 📋 [Complete Release History](RELEASES.md)
- 🔧 [API Documentation](API_DOCUMENTATION.md)
- 🚀 [Detailed Installation Guide](INSTALL.md)

### Troubleshooting
Check the [User Guide](USER_GUIDE_v2.1.0.md#troubleshooting) for common solutions:
- Database connection issues
- Ollama/Whisper errors
- GPU and CUDA problems
- Video files not appearing

---

## 🤝 Contributing

We welcome community contributions!

### How to Contribute
1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

### Contribution Guidelines
- Follow PEP 8 standards for Python code
- Add tests for new features
- Update documentation when needed
- Ensure all tests pass

---

## 📄 License

This project is licensed under the GNU GPL v3 License - see the [LICENSE](LICENSE) file for details.

### What this License Means:
- ✅ **Usage**: Free for personal and commercial use
- ✅ **Modification**: Code can be modified as needed
- ✅ **Distribution**: Modified copies can be distributed
- ⚠️ **Condition**: Must maintain same license for derivative works

---

## 👨‍💻 Developer Information

**AbdelmonemAwad (عبدالمنعم عوض)**
- 📧 **Email**: [Eg2@live.com](mailto:Eg2@live.com)
- 🐙 **GitHub**: [AbdelmonemAwad](https://github.com/AbdelmonemAwad)
- 📘 **Facebook**: [abdelmonemawad](https://www.facebook.com/abdelmonemawad/)
- 📷 **Instagram**: [abdelmonemawad](https://www.instagram.com/abdelmonemawad/)

### Support the Project
If you like this project:
- ⭐ Give it a star on GitHub
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📢 Share with others

---

## 📈 Project Statistics

![GitHub stars](https://img.shields.io/github/stars/AbdelmonemAwad/ai-translator)
![GitHub forks](https://img.shields.io/github/forks/AbdelmonemAwad/ai-translator)
![GitHub issues](https://img.shields.io/github/issues/AbdelmonemAwad/ai-translator)
![GitHub license](https://img.shields.io/github/license/AbdelmonemAwad/ai-translator)

### Development Milestones
- 🎯 **8 Releases** in 8 days
- 📝 **15,000+ Lines** of code
- 🌍 **Complete Bilingual** support
- 🚀 **40+ Advanced** features

---

## 🔮 Roadmap

### Version 2.2.0 (July 2025)
- [ ] Support for Chinese and French translation
- [ ] Advanced security enhancements
- [ ] Cloud deployment support
- [ ] Enhanced developer API

### Version 3.0.0 (August 2025)
- [ ] Infrastructure restructuring
- [ ] Docker/Kubernetes support
- [ ] Plugin system for extensions
- [ ] Mobile application

---

## ⚡ Quick Start

```bash
# Quick clone and run
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator
chmod +x install.sh
sudo ./install.sh

# Access application
open http://localhost:5000
```

**📱 For Instant Trial**: [Run on Replit](https://replit.com/new/github/AbdelmonemAwad/ai-translator)

---

<div align="center">

**Made with ❤️ in Egypt**

[⬆ Back to Top](#ai-translator-الترجمان-الآلي)

</div>