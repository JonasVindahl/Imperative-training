import logging
import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user
from flask_talisman import Talisman

from config import Config
from models import User, db
from services.exam_service import ExamService

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Fail fast on unsafe production config (default secret key, etc.)
Config.validate()

# Configure logging once for the whole app
logging.basicConfig(
    level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO'), logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize exam service
exam_service = ExamService(app.config['EXAMS_FILE'])
app.config['EXAM_SERVICE'] = exam_service

# Security headers via Talisman.
# CSP is permissive because templates currently use inline scripts/styles
# and the layout pulls jQuery / jQuery-UI / highlight.js from CDNs. Tightening
# this is tracked in IMPROVEMENT_TASKS.md (frontend JS quality / CSP).
_csp = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        'https://code.jquery.com',
        'https://cdnjs.cloudflare.com',
        'https://cdn.jsdelivr.net',
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        'https://code.jquery.com',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
    ],
    'img-src': ["'self'", 'data:'],
    'font-src': [
        "'self'",
        'data:',
        'https://cdnjs.cloudflare.com',
        'https://fonts.gstatic.com',
    ],
    'connect-src': "'self'",
    'frame-ancestors': "'none'",
    'base-uri': "'self'",
    'form-action': "'self'",
}

Talisman(
    app,
    content_security_policy=_csp,
    force_https=app.config['FORCE_HTTPS'],
    strict_transport_security=app.config['FORCE_HTTPS'],
    strict_transport_security_max_age=31536000,
    strict_transport_security_include_subdomains=True,
    referrer_policy='strict-origin-when-cross-origin',
    frame_options='DENY',
    session_cookie_secure=app.config['SESSION_COOKIE_SECURE'],
    session_cookie_http_only=True,
    permissions_policy={
        'geolocation': '()',
        'camera': '()',
        'microphone': '()',
    },
)


@login_manager.unauthorized_handler
def unauthorized():
    wants_json = request.accept_mimetypes.accept_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if wants_json:
        return jsonify({'error': 'Authentication required'}), 401
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_exam_context():
    """Make exam info available in all templates"""
    if current_user.is_authenticated:
        active_exam = exam_service.get_active_exam()
        all_exams = exam_service.get_all_exams()
        return {
            'active_exam': active_exam,
            'all_exams': all_exams,
            'exam_service': exam_service
        }
    return {}


# Create temp directory for code compilation
if not os.path.exists(app.config['TEMP_CODE_DIR']):
    os.makedirs(app.config['TEMP_CODE_DIR'])

# Import and register blueprints
from routes.auth import auth_bp
from routes.exam import exam_bp
from routes.practice import practice_bp
from routes.progress import progress_bp

app.register_blueprint(auth_bp)
app.register_blueprint(practice_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(exam_bp)


@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('progress.dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/healthz')
def healthz():
    """Liveness probe."""
    return jsonify({'status': 'ok'}), 200


@app.route('/readyz')
def readyz():
    """Readiness probe — verifies DB connectivity."""
    from sqlalchemy import text
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'status': 'ready'}), 200
    except Exception as exc:
        logger.warning('readyz failed: %s', exc)
        return jsonify({'status': 'unavailable', 'error': str(exc)}), 503


@app.errorhandler(404)
def not_found_error(error):
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# Create database tables and run migrations
with app.app_context():
    db.create_all()

    # Auto-migrate: add exam_id column to existing tables if missing
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)

    for table_name in ['attempts', 'progress']:
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        if 'exam_id' not in columns:
            logger.info('Migrating %s: adding exam_id column...', table_name)
            db.session.execute(text(
                f"ALTER TABLE {table_name} ADD COLUMN exam_id VARCHAR(50) NOT NULL DEFAULT 'c_programming'"
            ))
            db.session.commit()
            logger.info('  -> %s.exam_id added (existing rows default to c_programming)', table_name)

    # Update unique constraint on progress table if needed
    # SQLite doesn't support ALTER CONSTRAINT, but the new constraint will apply to new rows
    # Existing rows already have unique (user_id, category) which is a subset of (user_id, category, exam_id)

    logger.info('Database initialized.')


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
