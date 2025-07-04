# AI Translator v2.2.5 - Quick Installation Guide
## دليل التثبيت السريع للمترجم الآلي v2.2.5

## 🚀 One-Line Installation (Ubuntu/Debian)

```bash
curl -fsSL https://raw.githubusercontent.com/AbdelmonemAwad/ai-translator/main/install.sh | bash
```

## 📋 What This Command Does

1. **Updates system packages** and installs dependencies
2. **Clones the repository** from GitHub
3. **Sets up Python virtual environment** with all required packages
4. **Configures PostgreSQL database** with secure credentials
5. **Creates systemd service** for automatic startup
6. **Installs Ollama** for AI translation capabilities
7. **Starts the application** and verifies it's running

## 🔧 Post-Installation Steps

1. **Access the web interface:**
   ```
   http://localhost:5000
   ```

2. **Login with default credentials:**
   ```
   Username: admin
   Password: your_strong_password
   ```

3. **Configure media servers** in Settings (optional)

4. **Install AI models:**
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```

## 📊 Service Management

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

## 🔍 Troubleshooting

### Service Not Starting
```bash
# Check detailed logs
sudo journalctl -u ai-translator -n 50

# Verify database connection
sudo -u postgres psql -c "\l" | grep ai_translator

# Check Python dependencies
cd ai-translator && source venv/bin/activate && pip list
```

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process if necessary
sudo kill -9 <PID>
```

### Database Issues
```bash
# Reset database
sudo -u postgres psql -c "DROP DATABASE ai_translator;"
sudo -u postgres psql -c "CREATE DATABASE ai_translator;"
cd ai-translator && python database_setup.py
```

## 📖 Next Steps

- Configure your media servers (Plex, Jellyfin, Radarr, Sonarr)
- Set up file paths for your media library
- Start translating your first video files
- Explore the AI settings for optimal performance

## 🆘 Support

- **GitHub Issues:** https://github.com/AbdelmonemAwad/ai-translator/issues
- **Documentation:** Access built-in docs at `/docs` in the web interface
- **System Monitor:** Real-time status available at `/system-monitor`

---

**Installation completed successfully? Start translating your media library now!**