from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, PremiumRequest
from app import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/panel')
@login_required
def panel():
    if current_user.role != 'admin':
        flash('Brak dostępu. Ta strona jest przeznaczona tylko dla administratorów.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    # Pobieramy tylko te prośby, które mają status 'pending' (oczekujące)
    pending_requests = PremiumRequest.query.filter_by(status='pending').order_by(
        PremiumRequest.request_date.desc()).all()

    return render_template('admin.html', users=users, requests=pending_requests)


@admin_bp.route('/handle_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    if current_user.role != 'admin':
        flash('Brak uprawnień do wykonania tej akcji.', 'danger')
        return redirect(url_for('main.index'))

    premium_req = PremiumRequest.query.get_or_404(request_id)
    user = User.query.get(premium_req.user_id)

    if action == 'approve':
        premium_req.status = 'approved'
        if user:
            user.role = 'premium'  # Zmieniamy rolę użytkownika na premium
        flash(f'Zaakceptowano prośbę. Użytkownik {user.username} otrzymał status Premium!', 'success')

    elif action == 'reject':
        premium_req.status = 'rejected'
        flash(f'Odrzucono prośbę użytkownika {user.username}.', 'warning')

    db.session.commit()
    return redirect(url_for('admin.panel'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Brak uprawnień do wykonania tej akcji.', 'danger')
        return redirect(url_for('main.index'))

    user_to_delete = User.query.get_or_404(user_id)

    if user_to_delete.id == current_user.id:
        flash('Nie możesz usunąć własnego konta administratora!', 'warning')
        return redirect(url_for('admin.panel'))

    db.session.delete(user_to_delete)
    db.session.commit()

    flash(f'Konto użytkownika {user_to_delete.username} zostało trwale usunięte.', 'success')
    return redirect(url_for('admin.panel'))