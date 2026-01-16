from flask import Flask, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create temp directory for code compilation
if not os.path.exists(app.config['TEMP_CODE_DIR']):
    os.makedirs(app.config['TEMP_CODE_DIR'])

# Import and register blueprints
from routes.auth import auth_bp
from routes.practice import practice_bp
from routes.progress import progress_bp

app.register_blueprint(auth_bp)
app.register_blueprint(practice_bp)
app.register_blueprint(progress_bp)


@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('progress.dashboard'))
    return redirect(url_for('auth.login'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Create database tables
with app.app_context():
    db.create_all()
    print("Database initialized!")


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
