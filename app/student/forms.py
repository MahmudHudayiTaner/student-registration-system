from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, EqualTo

class ProfileUpdateForm(FlaskForm):
    first_name = StringField('Ad', validators=[DataRequired(), Length(max=64, message='Ad en fazla 64 karakter olabilir')])
    last_name = StringField('Soyad', validators=[DataRequired(), Length(max=64, message='Soyad en fazla 64 karakter olabilir')])
    birth_date = DateField('Doğum Tarihi', validators=[Optional()])
    gender = SelectField('Cinsiyet', choices=[
        ('', 'Seçiniz'),
        ('male', 'Erkek'),
        ('female', 'Kadın'),
        ('other', 'Diğer')
    ], validators=[Optional()])
    phone = StringField('Telefon', validators=[Optional(), Length(max=20, message='Telefon en fazla 20 karakter olabilir')])
    address = TextAreaField('Adres', validators=[Optional(), Length(max=500, message='Adres en fazla 500 karakter olabilir')])
    submit = SubmitField('Profili Güncelle')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[DataRequired(message='Mevcut şifrenizi girin')])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre girin'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifreyi tekrar girin'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Şifreyi Değiştir') 