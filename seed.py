from app import create_app, db
# seed.py (UPDATE)
from app import create_app, db
from app.models import User, Service, Barber
import os

app = create_app()

with app.app_context():
    # HAPUS DB LAMA & BUAT BARU (Karena Struktur Berubah)
    print("⚠️  Mereset Database karena struktur berubah...")
    db.drop_all()
    db.create_all()
    print("✅ Database bersih berhasil dibuat.")

    # 1. SERVICES (Daftar Baru 14 Item)
    services_data = [
        ('Gentlemen Cut', 50000, 45),
        ('Beard Trim', 25000, 20),
        ('Hair Spa & Massage', 75000, 60),
        ('Kids Cut', 40000, 30),
        ('Classic Taper Fade', 50000, 45),
        ('Modern Pompadour', 65000, 60),
        ('Textured Crop / French Crop', 55000, 45),
        ('Side Part Slick Back', 50000, 45),
        ('Buzz Cut / Crew Cut', 35000, 30),
        ('Mullet Modern', 60000, 60),
        ('Two Block Haircut', 65000, 60),
        ('Gentleman Cut (Hot Towel)', 55000, 45), # Nama saya bedakan dikit biar unik
        ('Undercut Disconnected', 55000, 45),
        ('Beard Trim & Shaping', 30000, 20)
    ]

    for name, price, duration in services_data:
        s = Service(name=name, price=price, duration_minutes=duration)
        db.session.add(s)
    
    # 2. BARBERS
    barbers = [
        Barber(name='Baji Keisuke', specialty='Top Stylist', is_active=True),
        Barber(name='Chifuyu Matsuno', specialty='Senior Barber', is_active=True),
        Barber(name='Draken', specialty='Hair Tattoo Expert', is_active=True)
    ]
    db.session.add_all(barbers)

    # 3. ADMIN USER
    admin = User(username='admin', email='admin@baji.com', phone='081234567890', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    db.session.commit()
    print("🎉 Database Seed Selesai dengan Layanan Baru!")