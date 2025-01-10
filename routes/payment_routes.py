from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.payment_service import PaymentService
from services.transaction_service import TransactionService
import io
import base64

payment_bp = Blueprint('payment', __name__, url_prefix='/pay')

@payment_bp.route('/qr-scan')
def qr_scan():
    return render_template('qr_scan.html')

@payment_bp.route('/qr-show')
def qr_show():
    user_id = session.get('user_id')
    return render_template('qr_show.html', user_id=user_id)

@payment_bp.route('/generate-qr')
def generate_qr():
    user_id = session.get('user_id')
    qr_image = PaymentService.generate_qr_code(user_id)
    img_io = io.BytesIO()
    qr_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode()
    
    return img_data

@payment_bp.route('/generate-code', methods=['POST'])
def generate_auth_code():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    try:
        user_id = session.get('user_id')
        amount = int(request.form.get('amount', 0))
        if amount <= 0:
            raise ValueError('金額は0より大きい値を指定してください')
            
        code = PaymentService.generate_auth_code(user_id, amount)
        return render_template('auth_code_display.html', code=code, amount=amount)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('pay_menu'))

@payment_bp.route('/auth-code', methods=['GET', 'POST'])
def auth_code_payment():
    if request.method == 'POST':
        code = request.form.get('code')
        amount = request.form.get('amount', type=float)
        payer_id = session.get('user_id')
        
        try:
            PaymentService.process_auth_code_payment(code, payer_id)
            return jsonify({'success': True})
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)})
            
    return render_template('auth_code_payment.html')

@payment_bp.route('/request', methods=['POST'])
def request_payment():
    data = request.get_json()
    user_id = session.get('user_id')
    
    try:
        request_id = PaymentService.create_payment_request(
            payer_id=user_id,
            receiver_id=data['receiver_id'],
            amount=data['amount']
        )
        return jsonify({'success': True, 'request_id': request_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@payment_bp.route('/respond', methods=['POST'])
def respond_to_payment():
    data = request.get_json()
    user_id = session.get('user_id')
    
    try:
        PaymentService.process_payment_response(
            request_id=data['request_id'],
            approved=data['approved'],
            receiver_id=user_id
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
