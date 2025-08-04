from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, SubmitField, DecimalField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, EqualTo, ValidationError
from werkzeug.security import check_password_hash

class CourseForm(FlaskForm):
    name = StringField('Kurs Adı', validators=[
        DataRequired(message='Kurs adı zorunludur'),
        Length(min=2, max=100, message='Kurs adı 2-100 karakter arasında olmalıdır')
    ])
    instructor_name = StringField('Eğitmen Adı', validators=[
        DataRequired(message='Eğitmen adı zorunludur'),
        Length(min=2, max=50, message='Eğitmen adı 2-50 karakter arasında olmalıdır')
    ])
    price = DecimalField('Kurs Ücreti (TL)', validators=[
        DataRequired(message='Kurs ücreti zorunludur'),
        NumberRange(min=0, message='Kurs ücreti 0 veya daha büyük olmalıdır')
    ])
    description = TextAreaField('Açıklama', validators=[
        Optional(),
        Length(max=500, message='Açıklama 500 karakterden uzun olamaz')
    ])
    is_active = BooleanField('Aktif')
    submit = SubmitField('Kaydet')

class AdminPasswordChangeForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[
        DataRequired(message='Mevcut şifre zorunludur')
    ])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre zorunludur'),
        Length(min=8, message='Şifre en az 8 karakter olmalıdır')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı zorunludur'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Şifreyi Değiştir')

    def validate_current_password(self, field):
        from flask_login import current_user
        if not check_password_hash(current_user.password_hash, field.data):
            raise ValidationError('Mevcut şifre yanlış') 