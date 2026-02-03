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
import midtransclient
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
    
    # Isi Pilihan Checkbox
    form.service_ids.choices = [(s.id, f"{s.name} (Rp {s.price:,.0f})") for s in Service.query.all()]
    form.barber_id.choices = [(b.id, b.name) for b in Barber.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # 1. Hitung Total Harga dari Service yang dipilih
        selected_services = Service.query.filter(Service.id.in_(form.service_ids.data)).all()
        total_price = sum(service.price for service in selected_services)
        
        # 2. Simpan Booking ke Database dulu (Status: Unpaid)
        booking = Booking(
            user_id=current_user.id,
            barber_id=form.barber_id.data,
            booking_time=datetime.combine(form.booking_date.data, form.booking_time.data),
            notes=form.notes.data,
            status='pending',
            payment_status='unpaid'
        )
        booking.services = selected_services
        db.session.add(booking)
        db.session.commit() # Commit agar dapat booking.id

        # 3. REQUEST TOKEN KE MIDTRANS (SNAP API)
        # Inisialisasi Snap
        snap = midtransclient.Snap(
            is_production=False,
            server_key=Config.MIDTRANS_SERVER_KEY,
            client_key=Config.MIDTRANS_CLIENT_KEY
        )

        # Buat Parameter Transaksi
        # Order ID harus unik, kita gabungkan ID Booking + Timestamp
        order_id = f"BAJI-{booking.id}-{int(time.time())}"
        
        param = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": int(total_price)
            },
            "customer_details": {
                "first_name": current_user.username,
                "email": current_user.email,
                "phone": current_user.phone,
            },
            "item_details": [
                {"id": s.id, "price": int(s.price), "quantity": 1, "name": s.name[:50]} 
                for s in selected_services
            ]
        }

        try:
            # Minta Token
            transaction = snap.create_transaction(param)
            transaction_token = transaction['token']
            
            # Simpan Token ke Database
            booking.payment_token = transaction_token
            db.session.commit()
            
            flash('Booking berhasil! Silakan selesaikan pembayaran.', 'success')
        except Exception as e:
            flash(f'Gagal memproses pembayaran: {str(e)}', 'danger')

        return redirect(url_for('main.dashboard'))
        
    return render_template('booking/create.html', title='Booking Baru', form=form)