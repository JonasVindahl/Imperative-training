import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Anchor paths to the repo root so the app works from any CWD
BASE_DIR = Path(__file__).resolve().parent

DEFAULT_DEV_SECRET = 'dev-secret-key'


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or unsafe in production."""


class Config:
    """Application configuration"""

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', DEFAULT_DEV_SECRET)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "instance" / "practice.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Code execution settings
    MAX_CODE_EXECUTION_TIME = int(os.getenv('MAX_CODE_EXECUTION_TIME', '3'))
    MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', '50'))

    # Resolve to repo-relative paths so the app is independent of CWD
    TEMP_CODE_DIR = str(BASE_DIR / 'temp')
    QUESTIONS_DIR = str(BASE_DIR / 'questions')
    EXAMS_FILE = str(BASE_DIR / 'exams.json')

    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Cookie / session hardening — relax in DEBUG so local HTTP still works
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = not DEBUG
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = not DEBUG

    # Whether to enforce HTTPS / HSTS via Talisman; on by default outside DEBUG
    FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'true' if not DEBUG else 'false').lower() == 'true'

    @classmethod
    def validate(cls) -> None:
        """Fail fast if production-critical settings are unsafe."""
        if not cls.DEBUG and cls.SECRET_KEY == DEFAULT_DEV_SECRET:
            raise ConfigError(
                "Refusing to start: FLASK_SECRET_KEY is the default dev value "
                "while DEBUG=False. Set FLASK_SECRET_KEY in the environment."
            )
