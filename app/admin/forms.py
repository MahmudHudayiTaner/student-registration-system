from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, TimeField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from app.models.course import Course

class CourseForm(FlaskForm):
    name = StringField('Kurs Adı', validators=[DataRequired(), Length(min=2, max=100)])
    instructor_name = StringField('Eğitmen Adı', validators=[DataRequired(), Length(min=2, max=100)])
    price = DecimalField('Ücret (TL)', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Açıklama', validators=[Optional(), Length(max=500)])
    is_active = SelectField('Durum', choices=[('True', 'Aktif'), ('False', 'Pasif')], validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class AdminPasswordChangeForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[DataRequired()])
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[DataRequired()])
    submit = SubmitField('Şifreyi Değiştir')

class AdminProfileForm(FlaskForm):
    first_name = StringField('Ad', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Soyad', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Telefon', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Profil Güncelle') 