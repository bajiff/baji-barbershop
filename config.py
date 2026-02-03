import os
from dotenv import load_dotenv

# Load file .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-default'
    
    # Ambil koneksi DB dari .env
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Matikan notifikasi track modification (biar hemat memori)
    SQLALCHEMY_TRACK_MODIFICATIONS = False