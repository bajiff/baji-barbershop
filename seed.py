from app import create_app, db
from app.models import User, Service, Barber

app = create_app()

with app.app_context():
    print("🚀 Memulai proses seeding database...")

    # --- 1. SERVICES ---
    if not Service.query.first():
        s1 = Service(name='Gentlemen Cut', price=50000, duration_minutes=45)
        s2 = Service(name='Beard Trim', price=25000, duration_minutes=20)
        s3 = Service(name='Hair Spa & Massage', price=75000, duration_minutes=60)
        s4 = Service(name='Kids Cut', price=40000, duration_minutes=30)
        db.session.add_all([s1, s2, s3, s4])
        print("✅ Layanan berhasil dibuat.")
    else:
        print("ℹ️ Layanan sudah ada data. Skip.")

    # --- 2. BARBERS ---
    if not Barber.query.first():
        b1 = Barber(name='Baji Keisuke', specialty='Long Hair & Fade', is_active=True)
        b2 = Barber(name='Chifuyu Matsuno', specialty='Undercut Style', is_active=True)
        b3 = Barber(name='Draken', specialty='Tato & Buzz Cut', is_active=True)
        db.session.add_all([b1, b2, b3])
        print("✅ Barber berhasil dibuat.")
    else:
        print("ℹ️ Barber sudah ada data. Skip.")

    # --- 3. ADMIN USER ---
    # Cek apakah admin sudah ada
    admin = User.query.filter_by(email='admin@baji.com').first()
    if not admin:
        admin = User(
            username='admin_baji', 
            email='admin@baji.com', 
            phone='081234567890',
            role='admin'
        )
        admin.set_password('admin123') 
        db.session.add(admin)
        print("✅ User Admin berhasil dibuat (Pass: admin123).")
    else:
        print("ℹ️ User Admin sudah ada. Skip.")

    db.session.commit()
    print("🎉 Selesai! Database siap digunakan.")