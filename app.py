from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from models.models import db, User, ServiceStatus
from services.auth_service import AuthService
from services.transaction_service import TransactionService
from services.database_service import DatabaseService
from config.database import DatabaseConfig
from routes.payment_routes import payment_bp
from routes.account_routes import account_bp  # Add this line
import qrcode
from io import BytesIO
import base64
import os
import logging
from datetime import timedelta

app = Flask(__name__,
           static_folder='static',  # 追加
           static_url_path='/static')  # 追加
app.secret_key = os.urandom(24)

# セッション設定を追加
app.config.update(
    SESSION_COOKIE_SECURE=False,  # HTTPS使用時はTrueに
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # セッション有効期限を7日に設定
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# データベース設定
app.config.from_object(DatabaseConfig)
db.init_app(app)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

@app.before_request
def before_request():
    if not db.engine.pool.checkedout():
        try:
            db.engine.connect()
        except Exception as e:
            logging.error(f"データベース接続エラー: {str(e)}")
            return "データベースに接続できません", 500

@app.teardown_appcontext
def shutdown_session(exception=None):
    DatabaseService.close_db()

def init_db():
    try:
        with app.app_context():
            # PostgreSQLのenumタイプのサポート
            db.engine.execute("CREATE TYPE user_role AS ENUM ('user', 'admin')")
            db.create_all()  # すべてのテーブルを作成
            ServiceStatus.init_services()
            
            # 管理者ユーザーの作成
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin')
                admin.set_password('admin123')
                admin.balance = 10000
                db.session.add(admin)
                db.session.commit()
    except Exception as e:
        logging.error(f"初期化エラー: {str(e)}")
        raise

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    transactions = TransactionService.get_user_transactions(user.id)
    return render_template('dashboard.html', user=user, transactions=transactions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            user = AuthService.register_user(
                request.form['username'],
                request.form['password']
            )
            session['user_id'] = user.id
            flash('アカウントが作成されました', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AuthService.login_user(
            request.form['username'],
            request.form['password']
        )
        if user:
            return redirect(url_for('dashboard'))
        flash('ユーザー名またはパスワードが間違っています', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    AuthService.logout_user()
    return redirect(url_for('login'))

@app.route('/pay', methods=['POST'])
def pay():
    try:
        transaction = TransactionService.create_transaction(
            session.get('user_id'),
            request.form.get('receiver_id'),
            int(request.form.get('amount'))
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/generate_qr/<amount>')
def generate_qr(amount):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    data = f"omiyapay://payment/{amount}"
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

@app.route('/status')
def status():
    services = ServiceStatus.query.all()
    user = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
    return render_template('status.html', user=user, services=services)

@app.route('/balance')
def balance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    return render_template('balance.html', user=user)

@app.route('/pay-menu')
def pay_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pay_menu.html')

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.balance.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

@app.route('/checkin')
def checkin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    return render_template('checkin.html', user=user)

@app.route('/admin-console')
def admin_console():
    if not session.get('admin'):
        flash('管理者権限が必要です', 'danger')
        return redirect(url_for('home'))
    
    services = ServiceStatus.query.all()
    stats = {
        'user_count': User.query.count(),
        'transaction_count': Transaction.query.count(),
        'total_amount': db.session.query(func.sum(Transaction.amount)).scalar() or 0
    }
    return render_template('admin_console.html', services=services, stats=stats)

@app.route('/update-service-status', methods=['POST'])
def update_service_status():
    if not session.get('admin'):
        return jsonify({'error': '権限がありません'}), 403
    
    service_id = request.form.get('service_id')
    new_status = request.form.get('status')
    
    service = ServiceStatus.query.get_or_404(service_id)
    service.status = new_status
    db.session.commit()
    
    return redirect(url_for('admin_console'))

# Blueprintを登録
app.register_blueprint(payment_bp)
app.register_blueprint(account_bp)  # Add this line

# 開発サーバー用の実行
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    # プロダクション環境用の設定
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
