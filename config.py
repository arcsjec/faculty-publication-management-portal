import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'sjec_publications.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PUBLICATIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'publications')
    PROFILES_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
    SIGNATURES_FOLDER = os.path.join(UPLOAD_FOLDER, 'signatures')
    FEEDBACK_SCREENSHOTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'feedback_screenshots')
    CIRCULARS_FOLDER = os.path.join(UPLOAD_FOLDER, 'circulars')
    
    MAX_CONTENT_LENGTH = 26214400  # 25 MB in bytes
    ALLOWED_EXTENSIONS = {'pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    ALLOWED_CIRCULAR_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    
    # Email domain restriction
    ALLOWED_EMAIL_DOMAIN = 'sjec.ac.in'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@sjec.ac.in'
    
    # Pagination
    ITEMS_PER_PAGE = 20
