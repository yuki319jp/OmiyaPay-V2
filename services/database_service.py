from flask import current_app
from models.models import db
from sqlalchemy.exc import SQLAlchemyError
import logging

class DatabaseService:
    @staticmethod
    def init_db():
        try:
            db.create_all()
        except SQLAlchemyError as e:
            logging.error(f"データベース初期化エラー: {str(e)}")
            raise

    @staticmethod
    def safe_commit():
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"データベース更新エラー: {str(e)}")
            raise

    @staticmethod
    def close_db():
        try:
            db.session.remove()
        except Exception as e:
            logging.error(f"セッション終了エラー: {str(e)}")
