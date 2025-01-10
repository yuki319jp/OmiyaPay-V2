from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AuthService.login_user(
            request.form['username'],
            request.form['password']
        )
        if user:
            session.permanent = True  # セッションを永続化
            session['user_id'] = user.id
            session['admin'] = user.is_admin if hasattr(user, 'is_admin') else False
            return redirect(url_for('dashboard'))
        flash('ユーザー名またはパスワードが間違っています', 'danger')
    return render_template('login.html')

# ...existing code...
