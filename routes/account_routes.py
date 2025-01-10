from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.user_service import UserService

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route('/settings')  # Changed from '/' to '/settings'
def settings():
    user_id = session.get('user_id')
    user = UserService.get_user(user_id)
    return render_template('account.html', user=user)

@account_bp.route('/update-profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    display_name = request.form.get('display_name')
    
    try:
        UserService.update_profile(user_id, display_name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@account_bp.route('/update-settings', methods=['POST'])
def update_settings():
    user_id = session.get('user_id')
    data = request.get_json()
    
    try:
        UserService.update_settings(
            user_id=user_id,
            setting_name=data['setting'],
            setting_value=data['value']
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@account_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # パスワード変更のロジックを実装
        pass
    return render_template('change_password.html')

@account_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    if request.method == 'POST':
        # 二段階認証の設定ロジックを実装
        pass
    return render_template('two_factor.html')
