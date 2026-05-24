from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')

    # Ochrona przed Brute Force
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    photos = db.relationship('Photo', backref='author', lazy=True, cascade="all, delete-orphan")

    def is_premium(self):
        return self.role in ['premium', 'admin']

    def is_admin(self):
        return self.role == 'admin'


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    hashtags = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# NOWY MODEL DLA PROŚB O PREMIUM
class PremiumRequest(db.Model):
    __tablename__ = 'premium_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacja pozwalająca łatwo wyciągnąć dane użytkownika w panelu admina
    user = db.relationship('User', backref=db.backref('requests', lazy=True, cascade="all, delete-orphan"))