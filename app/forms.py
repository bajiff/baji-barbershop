from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, TimeField, TextAreaField, RadioField
# PERHATIKAN BARIS DI BAWAH INI: Tambahkan Optional
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('No. WhatsApp', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar Sekarang')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email ini sudah terdaftar. Silakan login.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username ini sudah dipakai.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Login Masuk')
    
# --- FORM BOOKING (YANG DIPERBAIKI) ---
class BookingForm(FlaskForm):
    # 1. HAIRCUT: Radio Button (Pilih 1 Style atau Tidak sama sekali)
    haircut_id = RadioField('Gaya Rambut', coerce=int, validators=[Optional()])
    
    # 2. JENGGOT: Checkbox (Ya/Tidak)
    beard_trim = BooleanField('Potong Jenggot?')
    
    # 3. KUMIS: Checkbox (Ya/Tidak)
    mustache_trim = BooleanField('Potong Kumis?')
    
    # 4. WARNA: Radio Button (Pilih 1 Warna atau Tidak sama sekali)
    color_id = RadioField('Warna Rambut', coerce=int, validators=[Optional()])

    # Input Standar
    barber_id = SelectField('Pilih Barber', coerce=int, validators=[DataRequired()])
    booking_date = DateField('Tanggal Booking', validators=[DataRequired()])
    booking_time = TimeField('Jam Kedatangan', validators=[DataRequired()])
    notes = TextAreaField('Catatan Tambahan')
    submit = SubmitField('Konfirmasi Booking')

    # VALIDASI CUSTOM: "Yakali cuma mau nongki"
    # Memastikan user memilih minimal salah satu dari 4 layanan di atas
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
            
        # Cek apakah keempat-empatnya kosong?
        has_haircut = self.haircut_id.data is not None
        has_beard = self.beard_trim.data
        has_mustache = self.mustache_trim.data
        has_color = self.color_id.data is not None
        
        if not (has_haircut or has_beard or has_mustache or has_color):
            # Tampilkan error di bagian paling atas (haircut)
            self.haircut_id.errors.append('Anda belum memilih layanan apapun! Silakan pilih minimal satu (Potong/Jenggot/Kumis/Warna).')
            return False
        
        return True