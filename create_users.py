from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Lista przykładowych użytkowników do wygenerowania
    dummy_users = [
        {'username': 'JanKowalski', 'email': 'jan@test.pl', 'role': 'user'},
        {'username': 'AnnaNowak', 'email': 'anna@test.pl', 'role': 'user'},
        {'username': 'MarekZwykly', 'email': 'marek@test.pl', 'role': 'user'},
        {'username': 'KasiaPremium', 'email': 'kasia@test.pl', 'role': 'premium'},
        {'username': 'TomekVIP', 'email': 'tomek@test.pl', 'role': 'premium'}
    ]

    # Wspólne, proste hasło dla wszystkich testowych kont
    default_password = 'HasloTestowe1'

    print("Rozpoczynam generowanie kont...")

    for user_data in dummy_users:
        # Sprawdzamy, czy użytkownik z takim mailem już nie istnieje
        existing_user = User.query.filter_by(email=user_data['email']).first()

        if not existing_user:
            hashed_pw = generate_password_hash(default_password, method='pbkdf2:sha256')
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=hashed_pw,
                role=user_data['role']
            )
            db.session.add(new_user)
            print(f"[-] Dodano: {user_data['username']} (Rola: {user_data['role']})")
        else:
            print(f"[x] Pominięto: {user_data['username']} (Konto już istnieje)")

    # Zatwierdzenie wszystkich zmian w bazie
    db.session.commit()
    print("Gotowe! Baza danych została zasilona.")