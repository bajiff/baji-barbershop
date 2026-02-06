from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.models import User
# IMPORT PENTING YANG TADI KURANG:
from app.forms import RegistrationForm, LoginForm 
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User, Barber, Service, Booking # Tambah Booking
from app.forms import RegistrationForm, LoginForm, BookingForm # Tambah BookingForm
from datetime import datetime
import time # Untuk membuat Order ID unik
from config import Config

main = Blueprint('main', __name__)

# --- HOME PAGE ---
@main.route("/")
def index():
    return render_template('index.html')

# --- REGISTER ---
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash password otomatis dibuat di model (set_password)
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('auth/register.html', title='Register', form=form)

# --- LOGIN ---
@main.route("/login", methods=['GET', 'POST'])
def login():
    # 1. Jika user sudah login, lempar langsung ke Dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = LoginForm()
    
    # 2. Logika saat tombol Submit ditekan (POST)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Cek user ada DAN password cocok
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            
            # --- PERBAIKAN DISINI ---
            # Kita ambil 'next' page dari URL (jika ada)
            next_page = request.args.get('next')
            
            # Jika ada next_page, ke sana. Jika tidak, ke Dashboard.
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.dashboard'))
                
        else:
            flash('Login gagal. Cek email dan password.', 'danger')
            
    # 3. Logika saat baru buka halaman (GET) atau Gagal Login
    # Return ini HARUS di paling bawah, di luar if validate_on_submit
    return render_template('auth/login.html', title='Login', form=form)

# --- LOGOUT ---
@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- DASHBOARD (Riwayat Booking) ---
@main.route("/dashboard")
@login_required # Wajib login
def dashboard():
    # Ambil booking milik user yang sedang login, urutkan dari yang terbaru
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('booking/dashboard.html', title='Dashboard Saya', bookings=bookings)

# --- BUAT BOOKING BARU ---
@main.route("/booking/new", methods=['GET', 'POST'])
@login_required
def new_booking():
    form = BookingForm()
    
    # 1. POPULATE OPSI DARI DATABASE
    form.haircut_id.choices = [(s.id, f"{s.name} - Rp {s.price:,.0f}") 
                               for s in Service.query.filter_by(category='haircut').all()]
    
    form.color_id.choices = [(s.id, f"{s.name} - Rp {s.price:,.0f}") 
                             for s in Service.query.filter_by(category='color').all()]
    
    form.barber_id.choices = [(b.id, b.name) for b in Barber.query.filter_by(is_active=True).all()]
    
    # 2. PROSES SIMPAN
    if form.validate_on_submit():
        selected_services = []
        
        # Logika Penggabungan Service (Tetap Sama)
        if form.haircut_id.data:
            selected_services.append(Service.query.get(form.haircut_id.data))
        if form.beard_trim.data:
            s = Service.query.filter_by(category='beard').first() 
            if s: selected_services.append(s)
        if form.mustache_trim.data:
            s = Service.query.filter_by(category='mustache').first()
            if s: selected_services.append(s)
        if form.color_id.data:
            selected_services.append(Service.query.get(form.color_id.data))
            
        # Simpan Booking
        booking = Booking(
            user_id=current_user.id,
            barber_id=form.barber_id.data,
            booking_time=datetime.combine(form.booking_date.data, form.booking_time.data),
            notes=form.notes.data,
            status='pending',        # Status awal: Pending (Menunggu Konfirmasi)
            payment_status='unpaid'  # Bayar nanti di lokasi
        )
        booking.services = selected_services
        
        db.session.add(booking)
        db.session.commit()
        
        # HAPUS SEMUA KODE MIDTRANS DISINI
        # Langsung redirect saja
        
        flash('Booking berhasil dikirim! Mohon tunggu konfirmasi admin / datang ke lokasi.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('booking/create.html', title='Booking Baru', form=form)