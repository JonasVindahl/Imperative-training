import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///practice.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Code execution settings
    MAX_CODE_EXECUTION_TIME = int(os.getenv('MAX_CODE_EXECUTION_TIME', 3))
    MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', 50))

    # Temp directory for code compilation
    TEMP_CODE_DIR = os.path.join(os.getcwd(), 'temp')

    # Questions directory
    QUESTIONS_DIR = os.path.join(os.getcwd(), 'questions')

    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
