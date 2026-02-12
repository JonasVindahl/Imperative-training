from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
from services.exam_service import ExamService
import os

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize exam service
exam_service = ExamService(os.path.join(os.getcwd(), 'exams.json'))
app.config['EXAM_SERVICE'] = exam_service


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
from routes.practice import practice_bp
from routes.progress import progress_bp
from routes.exam import exam_bp

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
            print(f"Migrating {table_name}: adding exam_id column...")
            db.session.execute(text(
                f"ALTER TABLE {table_name} ADD COLUMN exam_id VARCHAR(50) NOT NULL DEFAULT 'c_programming'"
            ))
            db.session.commit()
            print(f"  -> {table_name}.exam_id added (existing rows default to 'c_programming')")

    # Update unique constraint on progress table if needed
    # SQLite doesn't support ALTER CONSTRAINT, but the new constraint will apply to new rows
    # Existing rows already have unique (user_id, category) which is a subset of (user_id, category, exam_id)

    print("Database initialized!")


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
