from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, Regexp
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    # User fields
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6, message='Şifre en az 6 karakter olmalıdır')])
    confirm_password = PasswordField('Şifre Tekrar', validators=[DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor')])
    
    # StudentProfile fields
    first_name = StringField('Ad', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Soyad', validators=[DataRequired(), Length(max=64)])
    birth_date = DateField('Doğum Tarihi', validators=[DataRequired(message='Doğum tarihi zorunludur')])
    gender = SelectField('Cinsiyet', choices=[
        ('', 'Seçiniz'),
        ('male', 'Erkek'),
        ('female', 'Kadın'),
        ('other', 'Diğer')
    ], validators=[DataRequired(message='Cinsiyet seçimi zorunludur')])
    phone = StringField('Telefon', validators=[
        DataRequired(message='Telefon numarası zorunludur'), 
        Length(min=10, max=10, message='Telefon numarası 10 haneli olmalıdır'),
        Regexp(r'^[0-9]{10}$', message='Telefon numarası sadece rakamlardan oluşmalıdır (örn: 5432063908)')
    ])
    address = TextAreaField('Adres', validators=[DataRequired(message='Adres zorunludur'), Length(max=500)])
    
    submit = SubmitField('Kayıt Ol')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email adresi zaten kayıtlı.') 