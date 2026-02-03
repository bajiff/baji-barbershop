from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# --- SETUP USER LOADER (Wajib untuk Login) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TABEL USER (Pelanggan) ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='customer') # customer / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke Booking
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# --- TABEL BARBER (Tukang Cukur) ---
class Barber(db.Model):
    __tablename__ = 'barbers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100)) 
    is_active = db.Column(db.Boolean, default=True)
    
    bookings = db.relationship('Booking', backref='barber', lazy='dynamic')

    def __repr__(self):
        return f'<Barber {self.name}>'

# --- TABEL LAYANAN (Service) ---
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    
    bookings = db.relationship('Booking', backref='service', lazy='dynamic')

    def __repr__(self):
        return f'<Service {self.name}>'

# --- TABEL BOOKING (Transaksi) ---
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Kunci Tamu (Foreign Keys)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    booking_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='pending') # pending/confirmed/completed/cancelled
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_token = db.Column(db.String(100)) # ID dari Midtrans
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'