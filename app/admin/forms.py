from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

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