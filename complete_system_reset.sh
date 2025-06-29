#!/bin/bash

# Complete System Reset for AI Translator
# حذف شامل لجميع التثبيتات والبدء من جديد

echo "🗑️ Complete System Reset - AI Translator"
echo "========================================"
echo "⚠️  WARNING: This will remove EVERYTHING related to:"
echo "   - Python packages and virtual environments"
echo "   - AI Translator installations"
echo "   - PostgreSQL databases"
echo "   - System services"
echo "   - Configuration files"
echo ""
read -p "Continue with complete reset? (y/N): " -n 1 -r
echo ""
[[ ! $REPLY =~ ^[Yy]$ ]] && { echo "❌ Reset cancelled"; exit 1; }

echo "🔥 Starting complete system reset..."

# 1. Stop all services
echo "🛑 Stopping services..."
sudo systemctl stop ai-translator 2>/dev/null
sudo systemctl stop nginx 2>/dev/null
sudo systemctl stop postgresql 2>/dev/null
sudo systemctl disable ai-translator 2>/dev/null

# 2. Kill all Python processes
echo "🔪 Killing Python processes..."
sudo pkill -f python 2>/dev/null
sudo pkill -f gunicorn 2>/dev/null
sudo pkill -f ai-translator 2>/dev/null

# 3. Remove all AI Translator directories
echo "📁 Removing application directories..."
sudo rm -rf /opt/ai-translator
sudo rm -rf /usr/local/ai-translator
sudo rm -rf ~/ai-translator*
sudo rm -rf ./ai-translator*
sudo rm -rf /var/www/ai-translator
sudo rm -rf /srv/ai-translator

# 4. Remove Python virtual environments
echo "🐍 Removing Python virtual environments..."
rm -rf ~/venv*
rm -rf ~/.virtualenvs
rm -rf ~/ai-translator-venv
rm -rf .venv
rm -rf venv
rm -rf env

# 5. Remove all Python packages (pip)
echo "📦 Removing Python packages..."
pip3 freeze | grep -v "^-e" | cut -d "@" -f1 | xargs -n1 pip3 uninstall -y 2>/dev/null
python3 -m pip uninstall -y pip setuptools wheel 2>/dev/null

# 6. Remove Python package cache
echo "🧹 Cleaning Python cache..."
rm -rf ~/.cache/pip
rm -rf ~/.local/lib/python*
rm -rf /root/.cache/pip
sudo rm -rf /tmp/pip*

# 7. Remove PostgreSQL completely
echo "🗄️ Removing PostgreSQL..."
sudo systemctl stop postgresql 2>/dev/null
sudo apt remove --purge -y postgresql postgresql-* 2>/dev/null
sudo rm -rf /var/lib/postgresql
sudo rm -rf /etc/postgresql
sudo deluser postgres 2>/dev/null

# 8. Remove service files
echo "⚙️ Removing service files..."
sudo rm -f /etc/systemd/system/ai-translator*
sudo rm -f /etc/nginx/sites-available/ai-translator
sudo rm -f /etc/nginx/sites-enabled/ai-translator
sudo systemctl daemon-reload

# 9. Remove configuration files
echo "🔧 Removing configuration files..."
sudo rm -f /etc/ai-translator*
rm -f ~/.ai-translator*
sudo rm -rf /var/log/ai-translator*

# 10. Remove downloaded files
echo "📥 Removing downloaded files..."
rm -f ai-translator*.zip
rm -f ai-translator*.tar.gz
rm -f install*.sh
rm -f *.log *.db

# 11. Remove users
echo "👤 Removing system users..."
sudo deluser ai-translator 2>/dev/null
sudo delgroup ai-translator 2>/dev/null

# 12. Clean package manager
echo "🧽 Cleaning package manager..."
sudo apt autoremove -y
sudo apt autoclean
sudo apt clean

# 13. Remove Python completely (optional)
echo ""
read -p "🐍 Remove Python completely? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing Python..."
    sudo apt remove --purge -y python3* 2>/dev/null
    sudo apt autoremove -y
fi

# 14. Remove development tools (optional)
echo ""
read -p "🔨 Remove development tools (build-essential, git, etc.)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing development tools..."
    sudo apt remove --purge -y build-essential git curl wget 2>/dev/null
    sudo apt autoremove -y
fi

echo ""
echo "✅ Complete system reset finished!"
echo ""
echo "🚀 Fresh installation commands:"
echo "================================"
echo ""
echo "1. Install Python:"
echo "   sudo apt update"
echo "   sudo apt install -y python3 python3-pip python3-venv"
echo ""
echo "2. Download AI Translator:"
echo "   wget https://github.com/AbdelmonemAwad/ai-translator/releases/download/v2.2.0/ai-translator-v2.2.0.zip"
echo "   unzip ai-translator-v2.2.0.zip"
echo "   cd ai-translator*"
echo ""
echo "3. Install:"
echo "   sudo bash install_fixed.sh"
echo ""
echo "Or one-line fresh install:"
echo "curl -s https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/complete_fresh_install.sh | sudo bash"