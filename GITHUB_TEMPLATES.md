# GitHub Repository Templates and Community Files

## Directory Structure

Create the following directory structure in your repository:

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml
│   ├── feature_request.yml
│   └── config.yml
├── workflows/
│   ├── ci.yml
│   └── release.yml
└── PULL_REQUEST_TEMPLATE.md
```

## Issue Templates

### 1. Bug Report Template (.github/ISSUE_TEMPLATE/bug_report.yml)

```yaml
name: Bug Report
description: File a bug report to help us improve
title: "[BUG] "
labels: ["bug", "triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!

  - type: input
    id: version
    attributes:
      label: AI Translator Version
      description: What version of AI Translator are you running?
      placeholder: "v2.2.1"
    validations:
      required: true

  - type: dropdown
    id: environment
    attributes:
      label: Environment
      description: What operating system are you using?
      options:
        - Ubuntu 22.04
        - Ubuntu 20.04
        - Debian 11
        - Debian 12
        - Other Linux Distribution
        - Docker
        - Other (please specify in description)
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of what the bug is.
      placeholder: Tell us what happened!
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: A clear and concise description of what you expected to happen.
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant Log Output
      description: Please copy and paste any relevant log output. This will be automatically formatted into code.
      render: shell

  - type: textarea
    id: system-info
    attributes:
      label: System Information
      description: |
        Please provide the following system information:
      placeholder: |
        - Python Version: 
        - PostgreSQL Version: 
        - GPU: 
        - RAM: 
        - Browser (if web interface issue): 
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Pre-submission Checklist
      description: Please check the following before submitting
      options:
        - label: I have searched existing issues to ensure this is not a duplicate
          required: true
        - label: I have provided all requested information
          required: true
        - label: I have tested this with the latest version
          required: true
```

### 2. Feature Request Template (.github/ISSUE_TEMPLATE/feature_request.yml)

```yaml
name: Feature Request
description: Suggest an idea for AI Translator
title: "[FEATURE] "
labels: ["enhancement", "triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a new feature! We appreciate your input.

  - type: textarea
    id: problem
    attributes:
      label: Problem Description
      description: Is your feature request related to a problem? Please describe.
      placeholder: A clear and concise description of what the problem is.
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: Describe the solution you'd like
      placeholder: A clear and concise description of what you want to happen.
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternative Solutions
      description: Describe any alternative solutions or features you've considered
      placeholder: A clear and concise description of any alternative solutions.

  - type: dropdown
    id: component
    attributes:
      label: Component
      description: Which part of the system would this feature affect?
      options:
        - Web Interface
        - Translation Engine
        - Media Server Integration
        - Database
        - API
        - Installation/Setup
        - Documentation
        - Other (please specify)

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: How important is this feature to you?
      options:
        - Nice to have
        - Important
        - Critical
        - Urgent

  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Add any other context, screenshots, or examples about the feature request here.

  - type: checkboxes
    id: checklist
    attributes:
      label: Pre-submission Checklist
      description: Please check the following before submitting
      options:
        - label: I have searched existing issues to ensure this is not a duplicate
          required: true
        - label: I have provided a clear description of the feature
          required: true
```

### 3. Issue Config (.github/ISSUE_TEMPLATE/config.yml)

```yaml
blank_issues_enabled: false
contact_links:
  - name: 💬 Discussions
    url: https://github.com/YOUR_USERNAME/ai-translator/discussions
    about: Ask questions and discuss ideas with the community
  - name: 📚 Documentation
    url: https://github.com/YOUR_USERNAME/ai-translator/wiki
    about: Read the comprehensive documentation
  - name: 🚀 Installation Guide
    url: https://github.com/YOUR_USERNAME/ai-translator/blob/main/INSTALL.md
    about: Get help with installation and setup
```

## Pull Request Template

### .github/PULL_REQUEST_TEMPLATE.md

```markdown
## Description

Brief description of the changes and their purpose.

Fixes #(issue_number)

## Type of Change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Test improvements

## Testing

Describe the tests that you ran to verify your changes:

- [ ] Manual testing completed
- [ ] Automated tests pass
- [ ] Cross-browser testing (if applicable)
- [ ] Mobile testing (if applicable)

## Screenshots (if applicable)

Please add screenshots to help explain your changes.

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

Add any additional notes, concerns, or areas that need special attention during review.
```

## GitHub Actions Workflows

### 1. Continuous Integration (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: ai_translator_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg postgresql-client

    - name: Create virtual environment
      run: |
        python -m venv venv
        source venv/bin/activate
        echo "VIRTUAL_ENV=$VIRTUAL_ENV" >> $GITHUB_ENV
        echo "$VIRTUAL_ENV/bin" >> $GITHUB_PATH

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flask flask-sqlalchemy gunicorn psutil psycopg2-binary requests werkzeug email-validator

    - name: Set up database
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/ai_translator_test
      run: |
        python -c "from database_setup import create_database; create_database()"

    - name: Run syntax check
      run: |
        python -m py_compile app.py main.py models.py background_tasks.py

    - name: Test import statements
      run: |
        python -c "import app; print('App imports successfully')"

    - name: Check required files
      run: |
        test -f app.py
        test -f main.py
        test -f models.py
        test -f templates/layout.html
        test -f static/css/style.css

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run security check
      uses: pypa/gh-action-pip-audit@v1.0.8
      with:
        inputs: requirements.txt
        
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8
    - name: Lint with flake8
      run: |
        # Stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### 2. Release Workflow (.github/workflows/release.yml)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: AI Translator ${{ github.ref }}
        draft: false
        prerelease: false
        body: |
          ## Changes in this Release
          
          Please see [CHANGELOG.md](https://github.com/${{ github.repository }}/blob/main/CHANGELOG.md) for detailed changes.
          
          ## Installation
          
          ```bash
          wget https://github.com/${{ github.repository }}/releases/latest/download/install_ubuntu_venv.sh
          sudo chmod +x install_ubuntu_venv.sh
          sudo ./install_ubuntu_venv.sh
          ```

    - name: Upload Installation Scripts
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./install_ubuntu_venv.sh
        asset_name: install_ubuntu_venv.sh
        asset_content_type: application/x-sh

    - name: Upload Fixed Installation Script
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./install_fixed.sh
        asset_name: install_fixed.sh
        asset_content_type: application/x-sh
```

## Community Files

### 1. SECURITY.md

```markdown
# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.2.x   | :white_check_mark: |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### Private Disclosure

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email us directly at: **Eg2@live.com**
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the vulnerability and provide an initial response within 5 business days
- **Updates**: We will keep you informed of our progress
- **Resolution**: We aim to resolve critical issues within 30 days

### Responsible Disclosure

We request that you:
- Give us reasonable time to investigate and fix the issue
- Do not publicly disclose the vulnerability until we have released a fix
- Do not exploit the vulnerability for malicious purposes

### Recognition

We appreciate security researchers who help keep our users safe. With your permission, we will:
- Credit you in our security advisories
- List you in our hall of fame (if you're interested)

## Security Best Practices

When deploying AI Translator:

1. **Use HTTPS**: Always deploy behind a reverse proxy with SSL/TLS
2. **Strong Passwords**: Change default passwords immediately
3. **Network Security**: Restrict access to trusted networks when possible
4. **Keep Updated**: Always use the latest version
5. **Monitor Logs**: Regularly check application and system logs
6. **Backup Security**: Secure your database backups
7. **File Permissions**: Ensure proper file system permissions

## Known Security Considerations

- AI Translator requires significant system privileges for media processing
- GPU access requires elevated permissions
- Database contains potentially sensitive media metadata
- API endpoints require proper authentication

For more information, see our [Security Configuration Guide](security_config.py).
```

### 2. CODE_OF_CONDUCT.md

```markdown
# Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior:

* The use of sexualized language or imagery and unwelcome sexual attention or advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information without explicit permission
* Other conduct which could reasonably be considered inappropriate in a professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of acceptable behavior and will take appropriate and fair corrective action in response to any behavior that they deem inappropriate, threatening, offensive, or harmful.

## Scope

This Code of Conduct applies within all community spaces, and also applies when an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the community leaders responsible for enforcement at **Eg2@live.com**.

All complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 2.0.

[homepage]: https://www.contributor-covenant.org
```

## Repository Labels

Create these labels for better issue organization:

```
Type Labels:
- bug (red) - Something isn't working
- enhancement (blue) - New feature or request
- documentation (green) - Improvements or additions to documentation
- question (purple) - Further information is requested
- help wanted (yellow) - Extra attention is needed
- good first issue (green) - Good for newcomers

Priority Labels:
- priority: low (gray)
- priority: medium (yellow)
- priority: high (orange)
- priority: critical (red)

Component Labels:
- component: web-ui (blue)
- component: translation (green)
- component: media-servers (purple)
- component: installation (orange)
- component: database (brown)
- component: api (cyan)

Status Labels:
- status: triage (yellow)
- status: in-progress (blue)
- status: blocked (red)
- status: needs-review (orange)
```

This comprehensive template structure will create a professional, well-organized GitHub repository that encourages community participation and maintains high-quality contributions.