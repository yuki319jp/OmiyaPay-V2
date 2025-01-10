from models.models import db, User
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def get_user(user_id):
        """ユーザー情報を取得する"""
        if not user_id:
            return None
        return db.session.get(User, user_id)

    @staticmethod
    def update_profile(user_id, display_name):
        """ユーザープロファイルを更新する"""
        user = UserService.get_user(user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")
        
        user.display_name = display_name
        db.session.commit()
        return user

    @staticmethod
    def update_settings(user_id, setting_name, setting_value):
        """ユーザー設定を更新する"""
        user = UserService.get_user(user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")
        
        # 設定の更新ロジックを実装
        if setting_name == "email_notifications":
            user.email_notifications = setting_value
        elif setting_name == "two_factor_auth":
            user.two_factor_auth = setting_value
        else:
            raise ValueError("無効な設定名です")
        
        db.session.commit()
        return user

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """パスワードを変更する"""
        user = UserService.get_user(user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")
        
        if not user.check_password(current_password):
            raise ValueError("現在のパスワードが正しくありません")
        
        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def delete_account(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
