# AI Translator v2.2.5 Universal GitHub Package

## Package Information

- **Version**: 2.2.5 Final
- **Size**: 324KB (328,837 bytes)
- **Files**: 80 complete files
- **Target**: Ubuntu Server 20.04+ (Universal)
- **Installation**: One-line command

## Universal Installation Support

This package supports installation on any Ubuntu server with any username that has root privileges. The installation script automatically detects the user and sets up appropriate directories and permissions.

### Supported Environments
- **Ubuntu Server 20.04+**
- **Ubuntu Server 22.04** (Recommended)
- **Ubuntu Server 24.04** (Latest)
- **Any user with sudo/root access**
- **Both root and regular user installations**

## Installation Methods

### Method 1: Direct GitHub Installation (Recommended)
```bash
# Download and run installation script directly from GitHub
wget https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install_remote_server.sh
chmod +x install_remote_server.sh
sudo ./install_remote_server.sh
```

### Method 2: Clone Repository
```bash
# Clone the repository and install
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator
sudo ./install_remote_server.sh
```

### Method 3: Fix Existing Installation
If you have flask_sqlalchemy import errors:
```bash
sudo ./quick_ubuntu_fix.sh
```

## Installation Locations

The script automatically determines the installation directory based on the user:

- **Root user**: `/root/ai-translator`
- **Regular user**: `/home/username/ai-translator`
- **Service user**: Configured automatically based on installation user
- **Permissions**: Set appropriately for the installing user

## Features Fixed in v2.2.5

### Core Fixes
✅ **Flask-SQLAlchemy Import Resolution**: Completely fixed ModuleNotFoundError issues on Ubuntu servers
✅ **Database Schema Consistency**: Standardized all path/file_path column references
✅ **GPU Management APIs**: Fixed authentication issues in all GPU management functions
✅ **PostgreSQL Permissions**: Enhanced database user management and permissions
✅ **Universal User Support**: Installation works with any user having root privileges

### Enhanced Features
✅ **Advanced System Monitoring**: Real-time hardware monitoring with detailed system stats
✅ **Remote Storage Integration**: Complete SFTP, FTP, SMB, NFS support
✅ **Media Server Integrations**: Full support for Plex, Jellyfin, Emby, Kodi, Radarr, Sonarr
✅ **Mobile-First Design**: Responsive interface with Arabic RTL support
✅ **AI Translation Pipeline**: Whisper + Ollama integration with automatic subtitle generation

## Default Configuration

### Application Access
- **URL**: `http://YOUR_SERVER_IP`
- **Username**: `admin`
- **Password**: `your_strong_password`

### Database Configuration
- **Type**: PostgreSQL
- **Database**: `ai_translator`
- **Username**: `ai_translator`
- **Password**: `ai_translator_pass2024`
- **Host**: `localhost`

### Services
- **Application Service**: `ai-translator.service`
- **Web Server**: Nginx (reverse proxy)
- **Application Port**: 5000
- **Public Port**: 80

## Post-Installation Management

### Service Commands
```bash
# Check service status
sudo systemctl status ai-translator

# View real-time logs
sudo journalctl -u ai-translator -f

# Restart service
sudo systemctl restart ai-translator

# Stop service
sudo systemctl stop ai-translator

# Start service
sudo systemctl start ai-translator
```

### Nginx Commands
```bash
# Check nginx status
sudo systemctl status nginx

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Database Commands
```bash
# Connect to database
PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator

# Check database status
sudo systemctl status postgresql
```

## Troubleshooting

### Common Issues

1. **flask_sqlalchemy Import Error**
   ```bash
   sudo pip3 install --force-reinstall flask-sqlalchemy
   sudo systemctl restart ai-translator
   ```

2. **Database Connection Failed**
   ```bash
   sudo systemctl restart postgresql
   sudo ./database_permissions_fix.sql
   ```

3. **Service Won't Start**
   ```bash
   sudo journalctl -u ai-translator --no-pager -n 50
   sudo systemctl restart ai-translator
   ```

4. **Port Already in Use**
   ```bash
   sudo netstat -tlnp | grep :5000
   sudo pkill -f gunicorn
   sudo systemctl restart ai-translator
   ```

### Log Locations
- **Application Logs**: `journalctl -u ai-translator`
- **Nginx Logs**: `/var/log/nginx/`
- **PostgreSQL Logs**: `/var/log/postgresql/`

## Package Contents

### Core Application Files (11)
- `app.py` - Main Flask application
- `main.py` - Application entry point
- `models.py` - Database models
- `database_setup.py` - Database initialization
- `background_tasks.py` - Background processing
- `process_video.py` - Video processing pipeline
- `auth_manager.py` - Authentication system
- `translations.py` - Multilingual support
- `gpu_manager.py` - GPU management
- `system_monitor.py` - System monitoring
- `ai_integration_workaround.py` - AI integration

### Installation Scripts (5)
- `install_remote_server.sh` - Main installation script
- `ubuntu_server_fix.sh` - Ubuntu compatibility fixes
- `quick_ubuntu_fix.sh` - Quick flask_sqlalchemy fix
- `database_permissions_fix.sql` - Database permissions
- `requirements_github.txt` - Python dependencies

### Documentation (6)
- `README.md` - Project overview
- `UBUNTU_SERVER_DEPLOYMENT_GUIDE.md` - Deployment guide
- `INSTALL.md` - Installation instructions
- `LICENSE` - GPL v3 license
- `CONTRIBUTING.md` - Contribution guidelines
- `DEPENDENCIES.md` - Dependencies list

### Frontend (58 files)
- `templates/` - Jinja2 templates (48 files)
- `static/` - CSS, JavaScript, images (10 files)
- `services/` - Service integrations

## Security Considerations

1. **Change Default Credentials**: Update admin password after installation
2. **Database Security**: Consider changing database passwords in production
3. **Firewall Configuration**: Configure appropriate firewall rules
4. **SSL/TLS**: Consider adding HTTPS certificates for production use
5. **User Permissions**: Ensure proper file and directory permissions

## Performance Optimization

1. **System Requirements**:
   - Minimum: 2GB RAM, 2 CPU cores
   - Recommended: 4GB RAM, 4 CPU cores
   - Storage: 10GB free space

2. **Optional Enhancements**:
   - NVIDIA GPU for AI acceleration
   - SSD storage for better performance
   - Additional RAM for large media libraries

## Support and Updates

- **GitHub Repository**: https://github.com/AbdelmonemAwad/ai-translator
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Complete guides in repository
- **Updates**: Check repository for latest versions

## License

This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

---

**This package has been created to support universal installation on all Ubuntu servers with any user having root privileges.**