#!/bin/bash

# Environment Variables Setup for AI Translator
# إعداد متغيرات البيئة للمترجم الآلي

# Database Configuration
export DATABASE_URL="postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator"
export PGHOST="localhost"
export PGPORT="5432" 
export PGUSER="ai_translator"
export PGPASSWORD="ai_translator_pass2024"
export PGDATABASE="ai_translator"

# Flask Configuration
export FLASK_ENV="production"
export SESSION_SECRET="your-super-secret-session-key-2024"

# Application Configuration
export PYTHONPATH="/opt/ai-translator:$PYTHONPATH"

echo "✅ Environment variables configured successfully"
echo "Database URL: $DATABASE_URL"
echo "Python Path: $PYTHONPATH"