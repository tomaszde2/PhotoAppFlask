from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    login_manager.init_app(app)

    # Wczytywanie użytkownika dla Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Rejestracja Blueprintów (muszą być z wcięciem, wewnątrz funkcji!)
    from app.main.routes import main
    from app.auth.routes import auth
    from app.admin.routes import admin_bp

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app