from models.models import db, User, Transaction, AuthCode
from datetime import datetime

class TransactionService:
    @staticmethod
    def create_transaction(sender_id, receiver_id, amount):
        sender = db.session.get(User, sender_id)
        receiver = db.session.get(User, receiver_id)

        if not sender or not receiver:
            raise ValueError('ユーザーが見つかりません')

        if sender.balance < amount:
            raise ValueError('残高が不足しています')

        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            description='QR/認証コード決済'
        )

        sender.balance -= amount
        receiver.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def get_user_transactions(user_id):
        return Transaction.query.filter(
            (Transaction.sender_id == user_id) | 
            (Transaction.receiver_id == user_id)
        ).order_by(Transaction.created_at.desc()).all()
