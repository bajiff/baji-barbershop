from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.models import User, Barber, Service
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

# --- HOME PAGE ---
@main.route("/")
def index():
    return render_template('index.html')

# --- REGISTER (Disini Hashing Terjadi) ---
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # 1. Ambil data dari form
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        
        # 2. HASHING PASSWORD (Penting!)
        # Fungsi ini akan mengubah 'rahasia123' menjadi 'pbkdf2:sha256:...'
        user.set_password(form.password.data)
        
        # 3. Simpan ke MySQL
        db.session.add(user)
        db.session.commit()
        
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('auth/register.html', title='Register', form=form)

# --- LOGIN ---
@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Cek Password Hash vs Input User
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login gagal. Cek email dan password.', 'danger')
            
    return render_template('auth/login.html', title='Login', form=form)

# --- LOGOUT ---
@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))