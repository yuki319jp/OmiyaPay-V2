from models.models import db, User, Transaction, AuthCode
import qrcode
import json
import random
import string
from datetime import datetime, timedelta

class PaymentService:
    @staticmethod
    def generate_auth_code(user_id, amount):
        # ランダムな6桁の認証コードを生成
        code = ''.join(random.choices(string.digits, k=6))
        expiry = datetime.now() + timedelta(minutes=10)
        
        auth_code = AuthCode(
            code=code,
            user_id=user_id,
            amount=amount,
            expiry=expiry
        )
        db.session.add(auth_code)
        db.session.commit()
        return code

    @staticmethod
    def process_auth_code_payment(code, payer_id):
        auth_code = AuthCode.query.filter_by(code=code).first()
        if not auth_code or auth_code.expiry < datetime.now():
            raise ValueError('無効な認証コードです')
        
        # 支払い処理を実行
        TransactionService.create_transaction(
            sender_id=payer_id,
            receiver_id=auth_code.user_id,
            amount=auth_code.amount
        )
        
        # 使用済みの認証コードを削除
        db.session.delete(auth_code)
        db.session.commit()
        return True

    @staticmethod
    def generate_qr_code(user_id):
        payment_data = {
            'type': 'payment',
            'receiver_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(payment_data))
        qr.make(fit=True)
        
        return qr.make_image()
