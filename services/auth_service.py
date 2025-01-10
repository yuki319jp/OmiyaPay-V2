from flask import session
from models.models import db, User

class AuthService:
    @staticmethod
    def register_user(username, password):
        if User.query.filter_by(username=username).first():
            raise ValueError('このユーザー名は既に使用されています')
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return user
        return None

    @staticmethod
    def logout_user():
        session.pop('user_id', None)
