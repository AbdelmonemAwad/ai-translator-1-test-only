#!/bin/bash

# Quick Cleanup Script for AI Translator
# سكريبت التنظيف السريع للمترجم الآلي

echo "🧹 Quick AI Translator Cleanup"
echo "=============================="

# Stop services
echo "🛑 Stopping services..."
sudo systemctl stop ai-translator 2>/dev/null
sudo systemctl stop nginx 2>/dev/null
sudo systemctl disable ai-translator 2>/dev/null

# Kill processes
echo "🔪 Stopping processes..."
sudo pkill -f "python.*ai-translator" 2>/dev/null
sudo pkill -f "gunicorn.*ai-translator" 2>/dev/null

# Remove directories
echo "📁 Removing directories..."
sudo rm -rf /opt/ai-translator
sudo rm -rf ~/ai-translator*
sudo rm -rf ./ai-translator*

# Remove service files
echo "⚙️ Removing service files..."
sudo rm -f /etc/systemd/system/ai-translator*
sudo rm -f /etc/nginx/sites-available/ai-translator
sudo rm -f /etc/nginx/sites-enabled/ai-translator
sudo systemctl daemon-reload

# Remove database
echo "🗄️ Removing database..."
sudo systemctl stop postgresql 2>/dev/null
sudo -u postgres dropdb ai_translator 2>/dev/null
sudo -u postgres dropuser ai_translator 2>/dev/null

# Remove user
echo "👤 Removing user..."
sudo deluser ai-translator 2>/dev/null

# Clean files
echo "🗑️ Cleaning files..."
rm -f ai-translator*.zip
rm -f ai-translator*.tar.gz
rm -f install*.sh
rm -f *.log
rm -f library.db

echo "✅ Quick cleanup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Download: wget https://github.com/AbdelmonemAwad/ai-translator/archive/refs/heads/main.zip"
echo "2. Extract: unzip main.zip && cd ai-translator-main"
echo "3. Install: sudo bash install_fixed.sh"