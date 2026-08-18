"""
Flask application configuration.

Separates configuration logic from app initialization.
Different configs for dev/production can be added here.
"""

import os
from pathlib import Path


class Config:
    """Base configuration."""
    
    # Database URI.
    # Reads DATABASE_URL from the environment if set; otherwise defaults to
    # SQLite stored at instance/app.db (no server required).
    # SQLite is used per the README pragmatic note: "Use SQLite unless you
    # specifically want to install and run a MySQL server — SQLite requires no
    # separate server, ships with Python, and is fully acceptable per Phase-I
    # spec as 'local storage'."
    # To switch to MySQL: DATABASE_URL=mysql+pymysql://user:pass@host/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout
    
    # Secret key for session signing and CSRF protection
    # In production, load from environment variable: SECRET_KEY = os.environ.get('SECRET_KEY')
    # For development, we use a fixed key (NOT for production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # File upload settings
    UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Simulated real-time sensor feed (Live Monitoring feature).
    # No physical IoT hardware is available for this academic project, so a
    # background job generates plausible readings instead — see
    # app/utils/sensor_simulator.py for the full rationale.
    ENABLE_SENSOR_SIMULATOR = True
    SENSOR_SIM_INTERVAL_SECONDS = int(os.environ.get('SENSOR_SIM_INTERVAL_SECONDS', 10))
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory DB for tests
    ENABLE_SENSOR_SIMULATOR = False  # Keep tests free of background threads


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # In production, ensure SECRET_KEY and DATABASE_URI come from environment
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prod-key-must-be-set')


# Config selection by environment
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
