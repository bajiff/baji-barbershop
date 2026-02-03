from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# 1. Inisialisasi Extension secara Global (Belum terikat ke app manapun)
db = SQLAlchemy()
login_manager = LoginManager()

# Konfigurasi Login
login_manager.login_view = 'main.login' # Nanti kita arahkan ke halaman login
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    # 2. Inisialisasi Flask App
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 3. Bind Extension ke App ini
    db.init_app(app)
    login_manager.init_app(app)

    # 4. Registrasi Blueprints (Routes)
    # Kita import di dalam fungsi untuk menghindari Circular Import
    from app.routes import main
    app.register_blueprint(main)

    # 5. Create Database Tables (Development Mode)
    # Ini akan otomatis membuat tabel berdasarkan models.py
    with app.app_context():
        from app import models  # Import models agar terbaca SQLAlchemy
        db.create_all()

    return app