# Contributing to AI Translator (الترجمان الآلي)

Welcome to the AI Translator project! We appreciate community contributions and your efforts to develop this system.

## 🔐 Getting Access

For testing and development, use these default credentials:
- **Username**: `admin`
- **Password**: `your_strong_password`
- **Important**: Change these credentials in production environments

## 🎯 Welcome Contribution Types

### 🐛 Bug Reports
- Translation errors or Arabic text quality issues
- Performance problems or resource consumption issues
- UI bugs or design problems
- Media server integration issues

### ✨ Feature Requests
- Support for additional translation languages
- AI model improvements
- Integration with new platforms
- Security and protection enhancements

### 🔧 Code Improvements
- Performance and speed optimizations
- Code quality improvements and comments
- Adding new tests
- Documentation improvements

## 🚀 Getting Started

### 1. Development Environment Setup
```bash
# Clone the project
git clone https://github.com/AbdelmonemAwad/ai-translator.git
cd ai-translator

# Create new feature branch
git checkout -b feature/your-feature-name

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup development database
python database_setup.py
```

### 2. Run System for Development
```bash
# Run server in development mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python -m flask run --host=0.0.0.0 --port=5000
```

### 3. Run Tests
```bash
# Install testing tools
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/

# Check code coverage
pytest --cov=. tests/

# Check code quality
flake8 .
black . --check
```

## 📋 Contribution Standards

### Python Code
- Follow **PEP 8** standards for code formatting
- Use **Black** for automatic code formatting
- Add clear comments in Arabic or English
- Use descriptive and clear variable names

```python
# Good example
def translate_arabic_text(english_text: str, model_name: str = "llama3") -> str:
    """
    Translate text from English to Arabic using Ollama model
    
    Args:
        english_text: English text to translate
        model_name: Model name used for translation
        
    Returns:
        Text translated to Arabic
    """
    # Translation implementation here
    pass
```

### JavaScript
- Use ES6+ syntax
- Add comments for complex functions
- Ensure compatibility with modern browsers

```javascript
// Good example
/**
 * Update progress status in user interface
 * @param {number} progress - Progress percentage (0-100)
 * @param {string} currentFile - Current file being processed
 */
function updateProgressBar(progress, currentFile) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${progress}%`;
    progressBar.textContent = `${Math.round(progress)}% - ${currentFile}`;
}
```

### CSS
- Use BEM methodology for naming
- Support RTL for Arabic text
- Responsive design for different devices

```css
/* Good example */
.translation-card {
    direction: rtl; /* Arabic text support */
}

.translation-card__title {
    font-family: 'Tajawal', sans-serif;
    font-weight: 600;
}

.translation-card__progress {
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    border-radius: 4px;
}
```

## 🔄 Review Process

### Submitting Pull Request
1. **Ensure Cleanliness**: All tests run successfully
2. **Clear Description**: Write detailed description of changes
3. **Examples**: Add screenshots for visual changes
4. **Link Issues**: Connect PR to related Issues

### Good Pull Request Example
```markdown
## 🎯 Goal
Add French language translation support alongside English

## 🔧 Changes
- Added French language detection in process_video.py
- Updated Ollama prompts for French support
- Added French translation tests
- Updated UI to include French language option

## 🧪 Testing
- [x] Test French video translation
- [x] Run all existing tests
- [x] Check UI on different devices

## 📸 Screenshots
![French translation interface](screenshots/french_ui.png)

## 🔗 Related Issues
Closes #42 - Add French language support
```

## 🌍 Multilingual Handling

### Arabic Text
- Always use UTF-8 encoding
- Ensure RTL support in CSS
- Test text on different devices

### Translation Files
```python
# translations.py
TRANSLATIONS = {
    'ar': {
        'dashboard_title': 'لوحة التحكم',
        'file_management': 'إدارة الملفات',
        'translation_progress': 'تقدم الترجمة'
    },
    'en': {
        'dashboard_title': 'Dashboard',
        'file_management': 'File Management', 
        'translation_progress': 'Translation Progress'
    }
}
```

## 🧪 Writing Tests

### Unit Tests
```python
import pytest
from app import create_app, db
from models import MediaFile

class TestTranslation:
    @pytest.fixture
    def app(self):
        app = create_app({'TESTING': True})
        return app
    
    def test_arabic_translation_quality(self, app):
        """Test Arabic translation quality"""
        with app.test_client() as client:
            english_text = "Hello world"
            response = client.post('/api/translate', 
                                 json={'text': english_text, 'target': 'ar'})
            
            assert response.status_code == 200
            arabic_text = response.json['translated_text']
            assert len(arabic_text) > 0
            assert 'أهلا' in arabic_text or 'مرحبا' in arabic_text
```

### Integration Tests
```python
def test_full_translation_pipeline(app):
    """Test complete translation pipeline"""
    with app.test_client() as client:
        # Upload test video file
        response = client.post('/upload', 
                             data={'file': test_video_file})
        
        # Start translation process
        response = client.post('/api/translate-file', 
                             json={'file_id': 1})
        
        # Check result
        assert response.status_code == 200
        assert 'translation_started' in response.json
```

## 🛡️ Security and Protection

### Security Review
- Don't put passwords or API keys in code
- Use environment variables for sensitive settings
- Validate all user inputs
- Use HTTPS in production environment

```python
# Secure example
import os
from werkzeug.security import generate_password_hash

# Good - using environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Bad - exposed passwords
# DATABASE_URL = "postgresql://user:password123@localhost/db"
```

## 📚 Documentation

### Writing Documentation
- Write documentation in Arabic for regular users
- Write documentation in English for developers
- Add practical and clear examples
- Update documentation with every significant change

### Documentation Structure
```
docs/
├── user_guide_ar.md      # Arabic user guide
├── user_guide_en.md      # English user guide
├── api_documentation.md  # API reference
├── deployment_guide.md   # Deployment guide
└── troubleshooting.md    # Troubleshooting
```

## 🎨 Design Standards

### User Interface
- Simple and clean design
- Consistent colors with visual identity
- Complete Arabic language support (RTL)
- Responsive to all screen sizes

### Color System
```css
:root {
    --primary-color: #2196F3;      /* Primary blue */
    --secondary-color: #FFC107;    /* Secondary yellow */
    --success-color: #4CAF50;      /* Success green */
    --danger-color: #F44336;       /* Danger red */
    --dark-bg: #1a1a1a;           /* Dark background */
    --light-text: #ffffff;        /* Light text */
}
```

## 🏷️ Version Control

### Semantic Versioning
- **MAJOR** (X.0.0): Major changes that break compatibility
- **MINOR** (1.X.0): New features compatible with previous
- **PATCH** (1.1.X): Bug fixes

### Version Update Example
```bash
# Small bug fix
git tag v2.1.1

# New feature
git tag v2.2.0

# Major change
git tag v3.0.0
```

## 🤝 Community Ethics

### Be Respectful
- Respect others' opinions and experiences
- Provide constructive and helpful criticism
- Help beginners and answer their questions

### Effective Communication
- Use clear and polite language
- Break long messages into points
- Attach examples when needed

## 📞 Getting Help

### Support Channels
1. **GitHub Issues**: For bugs and new features
2. **Email**: Eg2@live.com for direct inquiries
3. **GitHub Community**: For general development discussions

### Help Request Template
```markdown
## 🎯 Problem
Clear description of the problem you're facing

## 🔄 Steps Taken
1. First step
2. Second step
3. Expected vs actual result

## 🖥️ Environment
- Operating System: Ubuntu 22.04
- Python Version: 3.11.5
- Application Version: 2.1.0

## 📋 Error Logs
```
Copy error log here
```

## 🎉 Contributor Acknowledgment

We thank all contributors to this project:

- AbdelmonemAwad (Lead Developer)
- [Add your name here when contributing]

## 📜 License

By contributing to this project, you agree to license your contribution under the same GNU GPL v3 license that governs the project.

---

**Thank you for your interest in contributing to AI Translator!** 🙏

For any inquiries, contact us at [Eg2@live.com](mailto:Eg2@live.com)