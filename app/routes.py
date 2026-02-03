from flask import Blueprint, render_template

# Membuat Blueprint bernama 'main'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "<h1>Sistem Baji Barbershop Berjalan! 💈</h1><p>Koneksi Database & Flask sukses.</p>"

# Placeholder untuk login (supaya tidak error di init)
@main.route('/login')
def login():
    return "Halaman Login (Belum dibuat)"