from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.Enum('user', 'admin', name='user_role'), default='user')
    
    # PostgreSQLのインデックス追加
    __table_args__ = (
        db.Index('ix_user_username', 'username'),
        db.Index('ix_user_created_at', 'created_at'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))

class AuthCode(db.Model):
    __tablename__ = 'auth_code'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('auth_codes', lazy=True))

class ServiceStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='operational')
    
    @property
    def status_display(self):
        status_map = {
            'operational': '正常',
            'degraded': '一部制限',
            'down': '停止中'
        }
        return status_map.get(self.status, '不明')

    @staticmethod
    def init_services():
        services = [
            ('決済システム', 'operational'),
            ('認証システム', 'operational'),
            ('データベース', 'operational'),
            ('QRコード生成', 'operational'),
            ('Webソケット', 'operational')
        ]
        for name, status in services:
            if not ServiceStatus.query.filter_by(name=name).first():
                service = ServiceStatus(name=name, status=status)
                db.session.add(service)
        db.session.commit()
