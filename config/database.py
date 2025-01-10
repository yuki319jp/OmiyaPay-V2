import os

class DatabaseConfig:
    DB_USER = os.getenv('DB_USER', 'omiyapay')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'omiyapay_password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'omiyapay')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'charset': 'utf8mb4'
    }
    SQLALCHEMY_ECHO = False  # SQLログを出力する場合はTrueに設定
