#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Translator (الترجمان الآلي) - Main Application Entry Point
Clean startup file without complex dependencies
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Initialize database
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_translator")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database with app
db.init_app(app)

# Import models after db initialization
with app.app_context():
    try:
        from models import Settings, MediaFile, Log, TranslationJob, Notification, UserSession
        db.create_all()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Import routes
try:
    from app import *
    print("✓ Routes loaded successfully")
except Exception as e:
    print(f"Routes loading error: {e}")
    # Create minimal route for testing
    @app.route('/')
    def index():
        return '''
        <h1>AI Translator (الترجمان الآلي)</h1>
        <p>System is starting up...</p>
        <p>النظام قيد التشغيل...</p>
        '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)