#!/usr/bin/env python3
"""
AI Translator (الترجمان الآلي) - Setup Configuration
GitHub: https://github.com/AbdelmonemAwad/ai-translator
"""

from setuptools import setup, find_packages

# Read requirements from pyproject.toml or provide fallback
try:
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        pyproject = tomllib.load(f)
        dependencies = pyproject.get('project', {}).get('dependencies', [])
except:
    # Fallback dependencies
    dependencies = [
        'flask>=2.3.0',
        'flask-sqlalchemy>=3.0.0',
        'psycopg2-binary>=2.9.0',
        'requests>=2.31.0',
        'psutil>=5.9.0',
        'gunicorn>=21.0.0',
        'pynvml>=11.5.0',
        'email-validator>=2.0.0',
        'sendgrid>=6.10.0',
        'werkzeug>=2.3.0'
    ]

setup(
    name="ai-translator",
    version="2.2.0",
    description="AI-powered Arabic subtitle translation system for movies and TV shows",
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="عبدالمنعم عوض (AbdelmonemAwad)",
    author_email="Eg2@live.com",
    url="https://github.com/AbdelmonemAwad/ai-translator",
    project_urls={
        "Bug Reports": "https://github.com/AbdelmonemAwad/ai-translator/issues",
        "Source": "https://github.com/AbdelmonemAwad/ai-translator",
        "Documentation": "https://github.com/AbdelmonemAwad/ai-translator/wiki"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=dependencies,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0'
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Arabic",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic"
    ],
    keywords="ai translation arabic subtitles movies tv-shows whisper ollama flask",
    entry_points={
        'console_scripts': [
            'ai-translator=main:app',
        ],
    },
    package_data={
        'ai-translator': [
            'templates/*.html',
            'templates/components/*.html',
            'static/css/*.css',
            'static/js/*.js',
            'static/fonts/*',
            '*.md',
            'LICENSE'
        ]
    },
    zip_safe=False,
    platforms=['Linux'],
    license="GPL-3.0"
)