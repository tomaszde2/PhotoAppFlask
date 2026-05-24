import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth = Blueprint('auth', __name__)


# --- NOWA FUNKCJA: Walidacja siły hasła ---
def validate_password(password):
    # Sprawdzenie długości (minimum 10 znaków)
    if len(password) < 10:
        return False, "Hasło musi mieć co najmniej 10 znaków."

    # Sprawdzenie wielkiej litery (A-Z)
    if not re.search(r"[A-Z]", password):
        return False, "Hasło musi zawierać co najmniej jedną wielką literę."

    # Sprawdzenie małej litery (a-z)
    if not re.search(r"[a-z]", password):
        return False, "Hasło musi zawierać co najmniej jedną małą literę."

    # Sprawdzenie cyfry (0-9)
    if not re.search(r"\d", password):
        return False, "Hasło musi zawierać co najmniej jedną cyfrę."

    return True, ""


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            # 1. Sprawdzenie aktywnej blokady konta (Brute Force)
            if user.locked_until and user.locked_until > datetime.utcnow():
                remaining_mins = (user.locked_until - datetime.utcnow()).seconds // 60 + 1
                flash(f'Konto zablokowane z powodu zbyt wielu błędnych prób. Spróbuj za {remaining_mins} min.',
                      'danger')
                return redirect(url_for('auth.login'))

            # 2. Reset blokady, jeśli czas minął
            if user.locked_until and user.locked_until <= datetime.utcnow():
                user.failed_attempts = 0
                user.locked_until = None
                db.session.commit()

            # 3. Weryfikacja hasła
            if check_password_hash(user.password_hash, password):
                user.failed_attempts = 0
                user.locked_until = None
                db.session.commit()

                login_user(user)
                flash(f'Zalogowano pomyślnie. Witaj, {user.username}!', 'success')
                return redirect(url_for('main.index'))
            else:
                # Błędne hasło - zwiększenie licznika
                user.failed_attempts += 1

                if user.failed_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    db.session.commit()
                    flash('Konto zablokowane na 15 minut z powodu 5 nieudanych prób logowania.', 'danger')
                else:
                    db.session.commit()
                    attempts_left = 5 - user.failed_attempts
                    flash(f'Błędne hasło. Pozostało prób: {attempts_left}', 'danger')
        else:
            flash('Błędny e-mail lub hasło.', 'danger')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano pomyślnie.', 'success')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Sprawdzenie, czy użytkownik już istnieje
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Użytkownik o tym adresie e-mail już istnieje.', 'danger')
            return redirect(url_for('auth.register'))

        # --- WALIDACJA HASŁA PRZED ZAPISEM ---
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'danger')  # Zwracamy konkretny błąd użytkownikowi
            return redirect(url_for('auth.register'))

        # Haszowanie bezpiecznego hasła
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Konto zostało utworzone! Możesz się teraz zalogować.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')