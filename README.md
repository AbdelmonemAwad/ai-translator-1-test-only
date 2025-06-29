# AI Translator (الترجمان الآلي)

<div align="center">

![AI Translator Logo](https://img.shields.io/badge/AI-Translator-2563eb?style=for-the-badge&logo=robot&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.2.2-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPL%20v3-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20Server-orange?style=for-the-badge&logo=ubuntu)

**Advanced AI-powered translation system for converting movies and TV shows to Arabic with exceptional accuracy and efficiency.**

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [Support](#support)

</div>

## 🎯 Overview

AI Translator is a comprehensive media translation system designed to automatically translate movies and TV shows from English to Arabic using cutting-edge AI technologies. The system provides a complete web interface for managing and monitoring all aspects of the translation process.

### Key Highlights
- 🤖 **AI-Powered**: Uses OpenAI Whisper for speech-to-text and Ollama (Llama 3) for translation
- 🌐 **Web Interface**: Professional Arabic RTL-supported web dashboard
- 📊 **Real-time Monitoring**: System resource monitoring and progress tracking
- 🔄 **Automated Processing**: Batch translation with background task management
- 📁 **Media Management**: Integration with Sonarr and Radarr for media library management
- 🗄️ **Database-driven**: PostgreSQL backend with comprehensive logging

## ✨ Features

### Core Translation Features
- **Speech-to-Text**: OpenAI Whisper with configurable models (tiny to large)
- **AI Translation**: Local Ollama LLM execution for secure Arabic translation
- **Subtitle Generation**: Automated SRT file creation with proper Arabic encoding
- **Batch Processing**: Queue-based translation with progress tracking
- **Quality Control**: Error handling and correction tools

### Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Arabic RTL Support**: Full right-to-left language support
- **Dark/Light Themes**: User-configurable appearance
- **Real-time Updates**: Live progress monitoring and notifications
- **File Management**: Advanced file listing with search and filtering

### System Management
- **Resource Monitoring**: CPU, RAM, GPU, and disk usage tracking
- **Logging System**: Comprehensive application and translation logs
- **User Authentication**: Secure session-based authentication
- **Settings Management**: Web-based configuration interface
- **Database Administration**: Built-in database management tools

### Integration Support
- **Sonarr Integration**: TV series management and metadata
- **Radarr Integration**: Movie management and metadata
- **Casa OS Support**: Native integration with Casa OS platform
- **API Endpoints**: RESTful APIs for external integration

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.11 + Flask | Web application framework |
| **Database** | PostgreSQL | Data storage and management |
| **AI/ML** | OpenAI Whisper + Ollama | Speech recognition and translation |
| **Media Processing** | FFmpeg | Audio/video processing |
| **Frontend** | HTML5 + CSS3 + JavaScript | User interface |
| **Web Server** | Nginx + Gunicorn | Production deployment |
| **Styling** | Custom CSS with Tajawal font | Arabic typography |

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu Server 22.04 LTS or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB free space (50GB+ recommended for models)
- **CPU**: 2 cores (4+ cores recommended)
- **GPU**: NVIDIA Graphics Card (required for AI processing)
- **Network**: Internet connection for initial setup

### Recommended Requirements
- **RAM**: 16GB for optimal performance
- **Storage**: SSD with 100GB+ free space
- **CPU**: 8+ cores for faster processing
- **GPU**: NVIDIA RTX series or better with 8GB+ VRAM

## 🚀 Quick Installation

### One-Command Installation

```bash
# Download and run the automated installer
wget https://raw.githubusercontent.com/username/ai-translator/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

### Manual Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/AbdelmonemAwad/ai-translator.git
   cd ai-translator
   ```

2. **Run Installation Script**
   ```bash
   sudo ./install.sh
   ```

3. **Access Application**
   ```
   URL: http://your-server-ip
   Default Login: admin / admin123
   ```

### What the Installer Does
- ✅ Installs Python 3.11 and dependencies
- ✅ Sets up PostgreSQL database
- ✅ Installs and configures Ollama with Llama 3
- ✅ Downloads OpenAI Whisper models
- ✅ Configures Nginx reverse proxy
- ✅ Sets up systemd services
- ✅ Configures firewall rules
- ✅ Creates default admin user

## 📖 Documentation

For comprehensive documentation, visit the built-in documentation page:
- **Web Documentation**: `http://your-server-ip/docs`
- **API Documentation**: Available in the web interface
- **Configuration Guide**: Settings page in the application

### Quick Start Guide

1. **Login**: Use default credentials `admin / admin123`
2. **Configure Settings**: Set up Sonarr/Radarr API endpoints
3. **Sync Library**: Import your media files
4. **Start Translation**: Select files and begin batch processing
5. **Monitor Progress**: Track translation status in real-time

## 🔧 Configuration

### Main Configuration Options
- **AI Models**: Whisper (speech-to-text) and Ollama/Llama 3 (translation)
- **Media Services**: Plex, Jellyfin, Emby, Kodi, Radarr, Sonarr integration
- **GPU Management**: Automatic NVIDIA GPU detection and allocation
- **Video Formats**: Support for 16+ video formats (MP4, MKV, AVI, etc.)
- **Remote Storage**: SFTP, FTP, SMB/CIFS, NFS mount support
- **Mobile Interface**: Responsive design with collapsible sidebar

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_translator_db
SESSION_SECRET=your-secret-key
FLASK_ENV=production
```

## 🐳 Casa OS Integration

AI Translator includes native Casa OS support:

```json
{
    "name": "AI Translator",
    "icon": "🤖",
    "description": "Advanced AI-powered translation system",
    "url": "http://localhost:80",
    "category": "Media",
    "tags": ["ai", "translation", "media", "subtitles"]
}
```

## 📊 Service Management

### SystemD Commands
```bash
# Check status
sudo systemctl status ai-translator

# Start/Stop/Restart
sudo systemctl start ai-translator
sudo systemctl stop ai-translator
sudo systemctl restart ai-translator

# View logs
sudo journalctl -u ai-translator -f
```

### Application Commands
```bash
# View application logs
tail -f /opt/ai-translator/app.log

# Check database status
sudo -u postgres psql -d ai_translator_db -c "\dt"

# Test Ollama connection
curl http://localhost:11434/api/tags
```

## 🔍 Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check logs for errors
sudo journalctl -u ai-translator -n 50

# Verify database connection
sudo systemctl status postgresql
```

**Web Interface Not Accessible**
```bash
# Check Nginx status
sudo systemctl status nginx

# Verify firewall settings
sudo ufw status
```

**Translation Errors**
- Ensure Ollama is running: `sudo systemctl status ollama`
- Check Whisper model availability
- Verify FFmpeg installation: `ffmpeg -version`

### Getting Help
- Check the built-in logs page for detailed error information
- Review system monitor for resource usage
- Consult the documentation page at `/docs`

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Setup
```bash
# Clone repository
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### Open Source Commitment
This software is **copyleft** protected, ensuring that:
- ✅ Source code remains forever open and free
- ✅ All modifications must be shared with the community  
- ✅ Commercial use is allowed but derivatives stay open source
- ✅ Cannot be incorporated into proprietary software

### Third-Party Licenses (GPL Compatible)
- OpenAI Whisper: Apache License 2.0
- Ollama: MIT License
- FFmpeg: LGPL/GPL
- PostgreSQL: PostgreSQL License

## 🆔 Version History & Changelog

### v2.2.0 (June 29, 2025) - Development Tools Centralization & Interface Optimization
**🎯 Major Features:**
- **Centralized Development Tools Interface**: Created comprehensive "Development Tools" category in Settings with unified sample data management
- **Enhanced Sample Data Management**: Complete development workflow with warning systems, bulk operations, and status feedback
- **Template Error Resolution**: Fixed critical "too many values to unpack" error in settings page option parsing
- **Database Integration**: Added development settings (debug_mode, log_level, testing_features) with multilingual support
- **UI/UX Improvements**: Streamlined interface by consolidating testing functionality from scattered pages into single location
- **Performance Optimization**: Enhanced JavaScript error handling and improved page loading speed

### v2.1.0 (June 29, 2025) - Complete Media Services Integration
**🎯 Major Features:**
- **Universal Media Services**: Full integration with Plex, Jellyfin, Emby, Kodi, Radarr, and Sonarr
- **Advanced GPU Management**: Automatic NVIDIA GPU detection with intelligent allocation
- **Comprehensive Video Format Support**: 16+ video formats including MP4, MKV, AVI, MOV, WMV, WebM
- **Perfect Mobile Interface**: Fully functional hamburger menu with responsive sidebar
- **Enhanced Remote Storage**: Multiple mount point support with SFTP, FTP, SMB/CIFS, NFS
- **Modular Architecture**: Component-based UI system for better maintainability

**🔧 Technical Improvements:**
- PostgreSQL database with enhanced schema for media services
- Services package with base classes and specialized implementations
- Improved error handling and connection management
- Advanced GPU performance scoring and service recommendations
- Complete translation status management system

**🌐 User Experience:**
- Professional dark theme with Arabic RTL support
- Interactive file browser with folder navigation
- Real-time system monitoring and translation progress
- Advanced notification system with multilingual support
- Grid layout controls for file management

### v2.0.0 (June 28, 2025) - Translation System Unification
**🎯 Major Features:**
- Complete translation status detection and management
- Enhanced UI with professional scan functionality
- Advanced API architecture with proper authentication
- Comprehensive file management with intelligent filtering

**🔧 Technical Improvements:**
- Background task system for bulk operations
- Real-time database updates during translation
- Flash message integration with session management
- Enhanced error handling and logging

### v1.0.0 (June 2025) - Initial Release
**🎯 Core Features:**
- OpenAI Whisper integration for speech-to-text
- Ollama/Llama 3 integration for Arabic translation
- Basic Radarr and Sonarr integration
- Web-based management interface
- SQLite database with basic schema
- Background processing system

## 👨‍💻 Author

**عبدالمنعم عوض (AbdelmonemAwad)**
- Email: Eg2@live.com
- GitHub: [@AbdelmonemAwad](https://github.com/AbdelmonemAwad)
- Facebook: [عبدالمنعم عوض](https://www.facebook.com/abdelmonemawad/)
- Instagram: [@abdelmonemawad](https://www.instagram.com/abdelmonemawad/)
- Specialized in AI-powered media processing systems
- Expert in Arabic language processing and NLP

## 🙏 Acknowledgments

- OpenAI for Whisper speech recognition
- Ollama team for local LLM execution
- FFmpeg project for media processing
- Casa OS community for platform integration

---

<div align="center">

**Built with ❤️ for the Arabic-speaking community**

[Website](http://your-server-ip) • [Documentation](/docs) • [Issues](https://github.com/AbdelmonemAwad/ai-translator/issues)

</div>