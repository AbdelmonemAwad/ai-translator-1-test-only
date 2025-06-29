# Changelog - AI Translator (الترجمان الآلي)
# سجل التغييرات - المترجم الآلي

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-06-29

### Added - المضاف
- **Centralized Development Tools Interface**: Created comprehensive "Development Tools" category in Settings
- **Enhanced Sample Data Management**: Complete development workflow with warning systems and bulk operations
- **Development Settings Database**: Added debug_mode, log_level, and enable_testing_features with multilingual options
- **Clear Sample Translation Logs**: New API endpoint and interface for translation log cleanup
- **Clear All Sample Data**: Comprehensive cleanup function for all development data

### Fixed - المُصلح
- **Template Error Resolution**: Fixed critical "too many values to unpack" error in settings page option parsing
- **Option Processing**: Enhanced template parsing with proper error handling and split limitations
- **JavaScript Performance**: Optimized error handling and removed null reference errors

### Improved - المُحسن
- **UI/UX Streamlining**: Consolidated testing functionality from scattered pages into single location
- **Navigation Enhancement**: Improved category dropdown integration with development tools
- **Interface Cleanup**: Removed duplicate buttons from File Management and Blacklist pages
- **Status Feedback**: Added visual indicators and development status display

## [2.1.0] - 2025-06-29

### Added - المضاف
- **Universal Media Services Integration**: Full support for Plex, Jellyfin, Emby, Kodi, Radarr, and Sonarr
- **Advanced GPU Management**: Automatic NVIDIA GPU detection with intelligent allocation
- **Comprehensive Video Format Support**: 16+ video formats with database-driven management
- **Enhanced Database Schema**: PostgreSQL with media services and video formats tables
- **Modular Services Architecture**: Professional services package with base classes
- **Perfect Mobile Interface**: Fully functional hamburger menu with responsive sidebar
- **Enhanced Remote Storage**: Multiple mount point support (SFTP, FTP, SMB/CIFS, NFS)
- **Interactive File Browser**: Modal-based folder navigation system

### Changed - المُحدَّث  
- **Database Migration**: From SQLite to PostgreSQL with enhanced schema
- **Video Format Management**: From static configuration to database-driven approach
- **Mobile Navigation**: Improved sidebar with proper z-index and overlay system
- **API Architecture**: Enhanced endpoints for media services management
- **Documentation**: Comprehensive version history and installation guides

### Fixed - المُصحح
- **Mobile Sidebar**: Fixed hamburger menu functionality and content visibility
- **JavaScript Errors**: Resolved null reference errors in dashboard components
- **Database Compatibility**: Added proper column migrations for existing installations
- **LSP Issues**: Fixed type annotations in services module

### Technical Details - التفاصيل التقنية
- Added `MediaService` model for service configuration storage
- Added `VideoFormat` model with 16 supported formats
- Created `/services/` package with specialized service implementations
- Enhanced `MediaFile` model with service-specific ID columns
- Improved error handling and connection management
- Added comprehensive fallback mechanisms

## [2.0.0] - 2025-06-28

### Added - المضاف
- **Translation Status Management**: Automatic detection and tracking system
- **Professional UI Components**: Enhanced scan functionality with real-time feedback
- **Advanced API Architecture**: Proper authentication and route management
- **Comprehensive File Management**: Intelligent filtering and status tracking
- **Notification System**: Multilingual notification support with session awareness

### Changed - المُحدَّث
- **Background Task System**: Improved processing with detailed progress tracking
- **Database Updates**: Real-time status updates during translation processes
- **User Experience**: Streamlined workflow operations with automatic redirects
- **Error Handling**: Enhanced logging and user-friendly error messages

### Fixed - المُصحح
- **API Endpoints**: Resolved 404 errors for notifications and database admin
- **Authentication**: Proper session checks and route protection
- **Translation Detection**: Accurate subtitle file scanning and status updates

## [1.0.0] - 2025-06-25

### Added - المضاف
- **Core AI Integration**: OpenAI Whisper for speech-to-text conversion
- **Translation Engine**: Ollama/Llama 3 for Arabic translation
- **Web Management Interface**: Complete Flask-based administration panel
- **Media Server Integration**: Basic Radarr and Sonarr API support
- **Background Processing**: Automated translation workflow system
- **Database Foundation**: SQLite with comprehensive schema
- **Authentication System**: Session-based user management
- **Real-time Monitoring**: System resource and translation progress tracking
- **Casa OS Support**: Integration with Casa OS platform
- **Automated Installation**: Complete Ubuntu Server installer script

### Technical Foundation - الأساس التقني
- Flask web framework with SQLAlchemy ORM
- PostgreSQL database with migration support
- NVIDIA GPU acceleration for AI processing
- FFmpeg integration for media file processing
- Nginx reverse proxy configuration
- Systemd service management
- Comprehensive logging and error handling

---

## Version Numbering - ترقيم الإصدارات

This project follows Semantic Versioning (SemVer):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions  
- **PATCH** version for backwards-compatible bug fixes

## Support - الدعم

For questions, bug reports, or feature requests:
- **GitHub Issues**: https://github.com/AbdelmonemAwad/ai-translator/issues
- **Email**: Eg2@live.com
- **Documentation**: `/docs` page in the application

## License - الترخيص

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.