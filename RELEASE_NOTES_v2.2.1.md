# AI Translator (الترجمان الآلي) - Release Notes v2.2.1

**Release Date**: June 29, 2025
**Python Support**: 3.9+ with Virtual Environment
**Ubuntu Support**: 22.04+ LTS

---

## 🎯 **Key Highlights**

This release specifically addresses Python 3.12+ compatibility issues by implementing comprehensive virtual environment support, resolving the "externally-managed-environment" error that prevents pip installations on modern Ubuntu systems.

---

## ✨ **Major Features**

### 🐍 **Python 3.12 Virtual Environment Support**
- **Virtual Environment Integration**: All installations now use Python virtual environments (`/opt/ai-translator-venv`)
- **Fixed PEP 668 Compliance**: Resolved "externally-managed-environment" error on Ubuntu 22.04+ with Python 3.12
- **Enhanced Package Management**: Isolated package installation preventing system Python conflicts
- **Backward Compatibility**: Maintains support for Python 3.9, 3.10, 3.11, and 3.12

### 🔧 **Enhanced Installation Scripts**
- **install_ubuntu_venv.sh**: New comprehensive installation script with virtual environment support
- **install_fixed.sh**: Updated existing script with virtual environment integration
- **install_venv.sh**: Generic virtual environment installer for all systems
- **Automatic Python Detection**: Scripts automatically detect available Python versions

### 🧹 **Complete System Cleanup Tools**
- **complete_system_reset.sh**: Comprehensive removal of all AI Translator components
- **quick_cleanup.sh**: Fast cleanup for quick reinstalls
- **fresh_install.sh**: Automated fresh installation after cleanup
- **CLEANUP_COMMANDS.md**: Complete guide with step-by-step instructions

### ⚙️ **Production-Ready Systemd Service**
- **Virtual Environment Integration**: Systemd service uses `/opt/ai-translator-venv/bin/gunicorn`
- **Enhanced Timeout Configuration**: Increased timeouts for AI processing operations
- **Improved Security**: Proper user/group permissions with service isolation
- **Restart Policies**: Enhanced restart mechanisms for reliability

---

## 🔨 **Technical Improvements**

### **Database Integration**
- **PostgreSQL Optimization**: Enhanced connection pooling and error handling
- **Stronger Password Security**: Updated default passwords with improved complexity
- **Connection Management**: Better database connection lifecycle management

### **Nginx Configuration**
- **File Upload Limits**: Increased `client_max_body_size` to 500MB for large media files
- **Timeout Optimization**: Extended proxy timeouts for AI processing operations
- **Security Headers**: Enhanced security configuration for production deployment

### **Package Management**
- **Dependency Isolation**: All Python packages installed in virtual environment
- **Version Pinning**: Specific package versions for stability and reproducibility
- **Clean Dependencies**: Removed unnecessary packages, optimized installation size

---

## 📦 **Package Information**

- **File**: `ai-translator-github-v2.2.1.zip`
- **Size**: 241 KB
- **Files**: 33 essential files and directories
- **Architecture**: Clean, production-ready codebase

### **Installation Methods**

#### **Method 1: Recommended (Virtual Environment)**
```bash
cd /tmp
wget https://github.com/AbdelmonemAwad/ai-translator/archive/refs/heads/main.zip
unzip main.zip
cd ai-translator-main
chmod +x install_ubuntu_venv.sh
sudo ./install_ubuntu_venv.sh
```

#### **Method 2: Quick Install**
```bash
cd /tmp && wget -q https://github.com/AbdelmonemAwad/ai-translator/archive/refs/heads/main.zip && unzip -q main.zip && cd ai-translator-main && sudo apt update && sudo apt install -y python3 python3-venv postgresql && chmod +x install_ubuntu_venv.sh && sudo ./install_ubuntu_venv.sh
```

---

## 🔧 **System Requirements**

### **Operating System**
- Ubuntu Server 22.04+ LTS
- Debian 11+ (Bullseye)
- Other Debian-based distributions with Python 3.9+

### **Hardware Requirements**
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space minimum
- **CPU**: 2 cores minimum, 4 cores recommended
- **GPU**: NVIDIA GPU recommended for AI processing (optional)

### **Software Dependencies**
- Python 3.9+ with venv support
- PostgreSQL 12+
- Nginx (installed automatically)
- FFmpeg (installed automatically)

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **"externally-managed-environment" Error**
✅ **Solved**: This release uses virtual environments to avoid this error completely.

#### **Permission Denied**
```bash
sudo chmod +x install_ubuntu_venv.sh
sudo ./install_ubuntu_venv.sh
```

#### **Service Won't Start**
```bash
sudo systemctl status ai-translator
sudo journalctl -u ai-translator -f
```

#### **Database Connection Issues**
```bash
sudo systemctl restart postgresql
sudo -u postgres psql -l
```

---

## 🔐 **Default Credentials**

- **Username**: `admin`
- **Password**: `your_strong_password`
- **Database**: `postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator`

---

## 📁 **File Structure**

```
/opt/ai-translator/           # Application files
/opt/ai-translator-venv/      # Virtual environment
/etc/systemd/system/ai-translator.service  # System service
/etc/nginx/sites-available/ai-translator   # Nginx configuration
```

---

## 🔄 **Upgrade from v2.2.0**

### **Clean Upgrade (Recommended)**
```bash
# 1. Backup database (optional)
sudo -u postgres pg_dump ai_translator > backup.sql

# 2. Remove old installation
sudo systemctl stop ai-translator
sudo rm -rf /opt/ai-translator /opt/ai-translator-venv

# 3. Install v2.2.1
cd /tmp && wget -q https://github.com/AbdelmonemAwad/ai-translator/archive/refs/heads/main.zip && unzip -q main.zip && cd ai-translator-main && sudo ./install_ubuntu_venv.sh
```

---

## 📞 **Support**

- **GitHub Issues**: https://github.com/AbdelmonemAwad/ai-translator/issues
- **Documentation**: `/docs` page in the application
- **Email**: Eg2@live.com

---

## 📄 **License**

GNU General Public License v3.0 - Open Source with Copyleft Protection

---

*This release ensures compatibility with modern Ubuntu systems while maintaining all the powerful features of the AI Translator system.*