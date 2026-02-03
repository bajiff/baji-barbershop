from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# --- SETUP USER LOADER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TABEL PIVOT (Relasi Many-to-Many Booking <-> Service) ---
booking_services = db.Table('booking_services',
    db.Column('booking_id', db.Integer, db.ForeignKey('bookings.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('services.id'), primary_key=True)
)

# --- TABEL USER ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- TABEL BARBER ---
class Barber(db.Model):
    __tablename__ = 'barbers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100)) 
    is_active = db.Column(db.Boolean, default=True)
    
    bookings = db.relationship('Booking', backref='barber', lazy='dynamic')

# --- TABEL SERVICE ---
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    
    def __repr__(self):
        return f'<Service {self.name}>'

# --- TABEL BOOKING ---
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    
    # Perhatikan: Tidak ada service_id lagi disini
    # Hubungan ke services lewat tabel pivot
    services = db.relationship('Service', secondary=booking_services, backref=db.backref('bookings', lazy='dynamic'))
    
    booking_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)