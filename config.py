import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Replace the URI with your MySQL configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Satish509073@localhost/store_monitoring'
    
    # Disable track modifications for performance reasons
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Your secret key for session management and CSRF protection
    SECRET_KEY = 'your_secret_key_here'
