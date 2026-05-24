import os
import requests
import urllib.parse
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.models import Photo, PremiumRequest
from app import db
from werkzeug.utils import secure_filename

# Biała lista dozwolonych rozszerzeń (Ochrona przed złośliwymi plikami np. SVG, PHP, EXE)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Pobranie zdjęć od najnowszego
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template('index.html', photos=photos)


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        # Sprawdzenie limitu dla darmowego konta
        if current_user.role == 'user' and len(current_user.photos) >= 5:
            flash('Osiągnąłeś limit 5 zdjęć. Kup konto Premium, aby dodawać bez limitu!', 'danger')
            return redirect(url_for('main.upload_photo'))

        file = request.files.get('file')
        title = request.form.get('title')

        if file and title:
            # Walidacja rozszerzenia pliku
            if not allowed_file(file.filename):
                flash('Niedozwolony format pliku! Akceptujemy tylko: JPG, PNG, GIF.', 'danger')
                return redirect(url_for('main.upload_photo'))

            # Ochrona przed Path Traversal + unikalność nazw za pomocą UUID
            original_filename = secure_filename(file.filename)
            unique_id = uuid.uuid4().hex
            final_filename = f"{unique_id}_{original_filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], final_filename)

            # 1. Fizyczny zapis pliku na serwerze
            file.save(file_path)

            # 2. Komunikacja z zewnętrznym Datamuse API (inteligentne hashtagi)
            generated_hashtags = ""
            try:
                safe_title = urllib.parse.quote_plus(title)
                response = requests.get(f'https://api.datamuse.com/words?ml={safe_title}&max=3', timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        hashtag_list = [f"#{item['word'].replace(' ', '')}" for item in data]
                        generated_hashtags = " ".join(hashtag_list)
                    else:
                        generated_hashtags = "#nowe #zdjecie #galeria"
                else:
                    generated_hashtags = "#foto #galeria #projekt"
            except Exception as e:
                print(f"Błąd komunikacji z Datamuse API: {e}")
                generated_hashtags = "#awaryjne #tagi"

            # 3. Zapis rekordu do bazy danych
            new_photo = Photo(
                title=title,
                filename=final_filename,
                hashtags=generated_hashtags,
                author=current_user
            )
            db.session.add(new_photo)
            db.session.commit()

            flash('Zdjęcie zostało dodane! API wygenerowało kontekstowe hashtagi.', 'success')
            return redirect(url_for('main.index'))

    return render_template('upload.html')


@main.route('/download/<filename>')
@login_required
def download_photo(filename):
    # Ochrona przed nieuprawnionym pobieraniem plików
    if not current_user.is_premium():
        flash('Pobieranie zdjęć jest dostępne tylko dla użytkowników Premium.', 'warning')
        return redirect(url_for('main.index'))

    # Bezpieczne pobieranie z wbudowaną we Flask ochroną przed Path Traversal
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@main.route('/request_premium', methods=['POST'])
@login_required
def request_premium():
    if current_user.role != 'user':
        flash('Masz już status premium lub jesteś administratorem.', 'info')
        return redirect(url_for('main.index'))

    # Sprawdzamy, czy użytkownik nie wysłał już wcześniej prośby, która czeka na rozpatrzenie
    existing_request = PremiumRequest.query.filter_by(user_id=current_user.id, status='pending').first()
    if existing_request:
        flash('Twoja prośba o status Premium została już wysłana i oczekuje na decyzję administratora.', 'warning')
        return redirect(url_for('main.index'))

    # Tworzymy nowe zgłoszenie
    new_request = PremiumRequest(user_id=current_user.id)
    db.session.add(new_request)
    db.session.commit()

    flash('Prośba o nadanie statusu Premium została pomyślnie wysłana do administratora.', 'success')
    return redirect(url_for('main.index'))