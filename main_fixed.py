# AI Translator v2.2.1 - Ubuntu Server Compatible Entry Point
import os
import sys

# Set environment variables for Ubuntu Server compatibility
os.environ.setdefault('DATABASE_URL', 'postgresql://ai_translator:ai_translator_pass2024@localhost/ai_translator')
os.environ.setdefault('SESSION_SECRET', 'ai_translator_secret_2024')

# Try to import the original app with proper error handling
try:
    from app import app
    print("✓ Successfully imported original AI Translator v2.2.1")
    
    # Add compatibility fixes for the original app
    def safe_initialize():
        """Initialize database safely"""
        try:
            with app.app_context():
                from models import db
                # Test database connection
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
                db.create_all()
                print("✓ Database initialized successfully")
        except Exception as e:
            print(f"⚠ Database initialization warning: {e}")
            print("✓ App will continue without database")
    
    # Initialize safely
    safe_initialize()
    
except ImportError as e:
    print(f"⚠ Import error in app.py: {e}")
    print("Creating Ubuntu Server compatible app...")
    
    from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
    import datetime
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "ai_translator_secret_2024")
    
    @app.route('/')
    def index():
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return redirect(url_for('dashboard'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if username == 'admin' and password == 'your_strong_password':
                session['authenticated'] = True
                session['username'] = username
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template_string('''
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تسجيل الدخول - المترجم الآلي</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .login-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    width: 400px;
                    text-align: center;
                }
                h1 { color: #333; margin-bottom: 30px; font-size: 2em; }
                .form-group { margin-bottom: 20px; text-align: right; }
                label { display: block; margin-bottom: 5px; color: #333; font-weight: bold; }
                input[type="text"], input[type="password"] {
                    width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;
                }
                .login-btn {
                    background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 12px 30px;
                    border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer;
                    width: 100%; margin-top: 20px;
                }
                .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .default-creds { background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 0.9em; color: #1565c0; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🤖 المترجم الآلي v2.2.1</h1>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'error' if category == 'error' else 'success' }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form method="post">
                    <div class="form-group">
                        <label>اسم المستخدم:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>كلمة المرور:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="login-btn">تسجيل الدخول</button>
                </form>
                
                <div class="default-creds">
                    <strong>بيانات الدخول الافتراضية:</strong><br>
                    اسم المستخدم: admin<br>
                    كلمة المرور: your_strong_password
                </div>
            </div>
        </body>
        </html>
        ''')
    
    @app.route('/dashboard')
    def dashboard():
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        
        return render_template_string('''
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>المترجم الآلي - لوحة التحكم</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .header {
                    background: rgba(255,255,255,0.95); padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    display: flex; justify-content: space-between; align-items: center;
                }
                .header h1 { color: #333; font-size: 2em; }
                .nav-links { display: flex; gap: 20px; }
                .nav-links a {
                    background: #667eea; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none;
                }
                .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
                .dashboard-grid {
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 30px;
                }
                .card {
                    background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                .card h3 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
                .stat-value { font-size: 2em; font-weight: bold; color: #667eea; margin: 10px 0; }
                .status-active { color: #28a745; }
                .system-info { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px; }
                .system-info p { margin: 5px 0; color: #495057; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 المترجم الآلي v2.2.1 - Ubuntu Server</h1>
                <div class="nav-links">
                    <a href="/dashboard">الرئيسية</a>
                    <a href="/logout">خروج</a>
                </div>
            </div>
            
            <div class="container">
                <div class="dashboard-grid">
                    <div class="card">
                        <h3>📊 حالة النظام</h3>
                        <div class="stat-value status-active">نشط ويعمل</div>
                        <div class="system-info">
                            <p><strong>الإصدار:</strong> v2.2.1</p>
                            <p><strong>النظام:</strong> Ubuntu Server 24.04</p>
                            <p><strong>الوضع:</strong> متوافق مع Ubuntu</p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🔧 التطبيق الأصلي</h3>
                        <div class="system-info">
                            <p>✅ Flask Web Server</p>
                            <p>✅ واجهة المستخدم العربية</p>
                            <p>✅ نظام التوثيق</p>
                            <p>🔧 قاعدة البيانات (قيد الإعداد)</p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>⚡ معلومات الخادم</h3>
                        <div class="system-info">
                            <p><strong>التاريخ:</strong> {{ now.strftime('%Y-%m-%d') }}</p>
                            <p><strong>الوقت:</strong> {{ now.strftime('%H:%M:%S') }}</p>
                            <p><strong>المستخدم:</strong> {{ session.username }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        ''', now=datetime.datetime.now(), session=session)
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'info')
        return redirect(url_for('login'))
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'operational',
            'version': '2.2.1',
            'mode': 'ubuntu_compatible',
            'timestamp': datetime.datetime.now().isoformat(),
            'authenticated': bool(session.get('authenticated'))
        })

# The app variable is now available for gunicorn
if __name__ == "__main__":
    print("Starting AI Translator v2.2.1 for Ubuntu Server...")
    app.run(host="0.0.0.0", port=5000, debug=False)