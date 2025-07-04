# AI Translator v2.2.5 Installation Guide

## Quick Installation for Ubuntu Server

### Method 1: Automatic Installation (Recommended)
```bash
# Download and run installation script
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_remote_server.sh
chmod +x install_remote_server.sh
sudo ./install_remote_server.sh
```

### Method 2: Manual Installation
1. Download the repository:
```bash
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator
```

2. Run the installation script:
```bash
sudo ./install_remote_server.sh
```

### Method 3: Fix flask_sqlalchemy Issue Only
If you already have the application but facing flask_sqlalchemy errors:
```bash
sudo ./quick_ubuntu_fix.sh
```

## Access Information
- **Application URL**: http://YOUR_SERVER_IP
- **Default Login**: admin / your_strong_password
- **Database**: PostgreSQL (ai_translator / ai_translator_pass2024)

## Server Management
- **View Logs**: `journalctl -u ai-translator -f`
- **Restart Service**: `systemctl restart ai-translator`
- **Check Status**: `systemctl status ai-translator`

## Features
- Complete Arabic subtitle translation system
- Media server integrations (Plex, Jellyfin, Emby, Kodi, Radarr, Sonarr)
- Advanced system monitoring and GPU management
- Remote storage support (SFTP, FTP, SMB, NFS)
- Responsive mobile-first design

## Support
For issues or questions, check the logs or refer to UBUNTU_SERVER_DEPLOYMENT_GUIDE.md
