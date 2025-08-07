import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    # Database settings
    TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL')
    TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')

    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        print("Warning: TURSO_DATABASE_URL or TURSO_AUTH_TOKEN not set.  Using SQLite fallback.")

    # Admin settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Cache settings
    CACHE_FOLDER = 'static/cache'
    
    @property
    def DATABASE_URL(self):
        """Return appropriate database URL based on environment"""
        if self.TURSO_DATABASE_URL and self.TURSO_AUTH_TOKEN:
            return self.TURSO_DATABASE_URL
        return 'site.db'  # SQLite fallback for local development
    
    @property
    def IS_PRODUCTION(self):
        """Check if running in production"""
        return self.TURSO_DATABASE_URL is not None and self.TURSO_AUTH_TOKEN is not None
