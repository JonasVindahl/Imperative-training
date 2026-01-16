from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and tracking"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attempts = db.relationship('Attempt', backref='user', lazy=True)
    progress = db.relationship('Progress', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'


class Attempt(db.Model):
    """Track each question attempt by a user"""
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    time_spent = db.Column(db.Integer, default=0)  # in seconds
    submitted_answer = db.Column(db.Text)
    hints_used = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attempt {self.question_id} by User {self.user_id}>'


class Progress(db.Model):
    """Track overall progress per category per user"""
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    total_attempted = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', name='unique_user_category'),
    )

    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.total_attempted == 0:
            return 0
        return int((self.total_correct / self.total_attempted) * 100)

    def __repr__(self):
        return f'<Progress User {self.user_id} - {self.category}: {self.accuracy}%>'
