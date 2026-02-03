from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from wtforms import SelectField, DateField, TimeField, TextAreaField # Tambahkan import ini
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
    
class BookingForm(FlaskForm):
    # Coerce=int artinya data yang dikirim akan dipaksa jadi Integer (ID database)
    service_id = SelectField('Pilih Layanan', coerce=int, validators=[DataRequired()])
    barber_id = SelectField('Pilih Barber', coerce=int, validators=[DataRequired()])
    booking_date = DateField('Tanggal Booking', validators=[DataRequired()])
    booking_time = TimeField('Jam Kedatangan', validators=[DataRequired()])
    notes = TextAreaField('Catatan Tambahan (Opsional)')
    submit = SubmitField('Konfirmasi Booking')