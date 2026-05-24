from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Sprawdzamy, czy admin przypadkiem już nie istnieje
    admin_exists = User.query.filter_by(email='admin@admin.com').first()

    if not admin_exists:
        hashed_password = generate_password_hash('HasloAdmina123', method='pbkdf2:sha256')
        new_admin = User(
            username='GlownyAdmin',
            email='admin@admin.com',
            password_hash=hashed_password,
            role='admin'  # Nadajemy najwyższe uprawnienia
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Sukces! Utworzono konto administratora.")
    else:
        print("Konto administratora już znajduje się w bazie.")