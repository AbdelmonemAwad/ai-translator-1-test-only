# Import the app from app.py which has all routes configured
from app import app

# The app variable is now available for gunicorn
# gunicorn will look for 'app' variable in this file
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)